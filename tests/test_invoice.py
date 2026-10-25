"""The Invoice mapping: conformant UBL, equivalent to HalvorsenDemo's hand-written writer, and honest about what UBL
cannot say."""
from __future__ import annotations

import io
from pathlib import Path

import pytest
from lxml import etree

from sdc_mapper import DECLARED, ERROR, LOOKUP, LOST, NOT_REPRESENTABLE, VALID, Engine, MappingError, load_mapping
from sdc_gdr2ubl import UBLMapper, mapping_path
from sdc_gdr2ubl.writer import schema_for

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "samples" / "halvorsen-invoice"
CT = "u19w614300a8ot4a7qnn2o1c"
RECORDS = sorted((SAMPLE / "records").glob("*.xml"))
GOLDEN = sorted((ROOT / "tests" / "golden").glob("*.xml"))
SDC4 = "https://semanticdatacharter.com/ns/sdc4/"
NS = {"sdc4": SDC4}


@pytest.fixture(scope="module")
def engine(tmp_path_factory):
    return Engine(schema_dir=tmp_path_factory.mktemp("schemas"))


@pytest.fixture(scope="module")
def mapping():
    return load_mapping(mapping_path(CT))


def run(engine, mapping, xml: bytes):
    return engine.map_record(xml, UBLMapper(), mapping, directory=str(SAMPLE))


def flat(el, path=""):
    """Every element, in document order: its path, its text, its attributes (listURI's value aside: HalvorsenDemo
    names the library's page for the list, this mapping the list component's own IRI)."""
    p = f"{path}/{etree.QName(el).localname}"
    attrs = dict(el.attrib)
    has_list = attrs.pop("listURI", None) is not None
    out = [(p, (el.text or "").strip(), tuple(sorted(attrs.items())), has_list)]
    for c in el:
        out += flat(c, p)
    return out


@pytest.mark.parametrize("golden", GOLDEN, ids=lambda p: p.stem)
def test_equivalent_to_the_hand_written_writer(engine, mapping, golden):
    r = run(engine, mapping, (SAMPLE / "records" / golden.name).read_bytes())
    assert r.outcome == VALID, r.errors
    ours = etree.fromstring(r.files["Invoice.xml"])
    assert flat(ours) == flat(etree.fromstring(golden.read_bytes()))


def test_every_record_maps_to_a_conformant_invoice(engine, mapping):
    schema = schema_for("Invoice")
    for f in RECORDS:
        r = run(engine, mapping, f.read_bytes())
        assert r.outcome == VALID, (f.name, r.errors)
        assert schema.is_valid(etree.fromstring(r.files["Invoice.xml"])), f.name


def test_the_report_accounts_for_every_value(engine, mapping):
    r = run(engine, mapping, RECORDS[0].read_bytes())
    classes = {v["class"] for v in r.report.values}
    assert classes <= {DECLARED, LOOKUP, NOT_REPRESENTABLE}
    payment = [v for v in r.report.values if v["label"] == "Payment Means"]
    assert payment and all(v["class"] == LOOKUP for v in payment), "the model binds the payment means to UBL's list"
    status = next(v for v in r.report.values if v["label"] == "Document Status")
    assert status["class"] == NOT_REPRESENTABLE and "document status" in status["note"]
    audit = [v for v in r.report.values if v["path"][1:2] == ["Audit Event"]]
    assert audit and all(v["class"] == NOT_REPRESENTABLE for v in audit)


def test_a_list_travels_with_its_component(engine, mapping):
    r = run(engine, mapping, RECORDS[0].read_bytes())
    root = etree.fromstring(r.files["Invoice.xml"])
    code = root.find("{*}InvoiceTypeCode")
    assert code.get("listURI").startswith(f"{SDC4}mc-")


# ---------------------------------------------------------------- Exceptional Values: UBL has no null flavors
def with_ev(xml: bytes, label_path: list[str], code="ASKR", name="Asked and Refused") -> bytes:
    """The record with a source Exceptional Value on the first value at a label path (clusters, then the value)."""
    from sdcreader import load_package, read_model
    model = read_model(load_package(SAMPLE, CT))
    by_label = {}
    for c in model.components.values():
        by_label.setdefault(c.label, set()).add(c.ct_id)
    tree = etree.parse(io.BytesIO(xml))
    candidates = tree.getroot().iter()
    for label in label_path:
        ids = by_label[label]
        found = next(el for el in candidates if isinstance(el.tag, str) and el.tag.startswith(f"{{{SDC4}}}ms-")
                     and el.tag.split("ms-", 1)[1] in ids)
        candidates = found.iter()
    after = found.find("sdc4:act", NS)
    if after is None:
        after = found.find("label")
    ev = etree.SubElement(found, f"{{{SDC4}}}{code}")
    etree.SubElement(ev, "ev-name").text = name
    found.remove(ev)
    after.addnext(ev)
    return etree.tostring(tree)


def test_an_exceptional_optional_value_is_lost_and_the_document_still_written(engine, mapping):
    xml = with_ev(RECORDS[0].read_bytes(), ["Invoice Document", "Buyer Reference"])
    r = run(engine, mapping, xml)
    assert r.outcome == VALID, r.errors        # a source Exceptional Value: the record is valid as it stands
    ev = r.report.exceptional
    assert [(e["label"], e["code"], e["class"]) for e in ev] == [("Buyer Reference", "ASKR", LOST)]
    assert etree.fromstring(r.files["Invoice.xml"]).find("{*}BuyerReference") is None


def test_an_exceptional_required_value_takes_its_aggregate_with_it_and_says_why(engine, mapping):
    """A TaxSubtotal is optional, its TaxAmount required: with the first line's subtotal amount exceptional, that
    subtotal cannot be written, every other value in it is reported with the reason, and the document conforms."""
    xml = with_ev(RECORDS[0].read_bytes(), ["Invoice Line", "Tax Total", "Tax Subtotal", "Tax Amount"])
    r = run(engine, mapping, xml)
    assert r.outcome == VALID, r.errors
    assert [e["class"] for e in r.report.exceptional] == [LOST]
    gone = [v for v in r.report.values if v["class"] == NOT_REPRESENTABLE
            and v.get("note", "").startswith("UBL requires cbc:TaxAmount in cac:TaxSubtotal")]
    assert {v["label"] for v in gone} == {"Taxable Amount", "Tax Category ID", "Tax Category Name", "Tax Percent",
                                          "Tax Scheme ID", "Tax Scheme Name"}
    assert schema_for("Invoice").is_valid(etree.fromstring(r.files["Invoice.xml"]))


def test_an_exceptional_value_in_a_required_aggregate_refuses_the_document(engine, mapping):
    xml = with_ev(RECORDS[0].read_bytes(), ["Legal Monetary Total", "Payable Amount"])
    r = run(engine, mapping, xml)
    assert r.outcome == ERROR
    assert "UBL requires cac:LegalMonetaryTotal in Invoice" in r.errors[0]["reason"]


def test_an_exceptional_value_the_document_requires_refuses_the_document(engine, mapping):
    xml = with_ev(RECORDS[0].read_bytes(), ["Invoice Document", "Invoice ID"])
    r = run(engine, mapping, xml)
    assert r.outcome == ERROR
    assert "UBL requires cbc:ID in Invoice" in r.errors[0]["reason"]


# ---------------------------------------------------------------- the mapping file decides; the writer refuses guesses
def test_no_mapping_no_document(engine):
    r = engine.map_record(RECORDS[0].read_bytes(), UBLMapper(), None, directory=str(SAMPLE))
    assert r.outcome == ERROR and "needs a mapping file" in r.errors[0]["reason"]


def test_a_mapping_that_promises_ubl_can_say_an_exceptional_value_is_refused(engine, mapping, tmp_path):
    import yaml
    doc = yaml.safe_load(mapping_path(CT).read_text())
    doc["exceptional_values"] = {"ASKR": {"class": "carried", "target_code": "ASKR"}}
    p = tmp_path / "m.yaml"
    p.write_text(yaml.safe_dump(doc, sort_keys=False))
    r = run(engine, load_mapping(p), RECORDS[0].read_bytes())
    assert r.outcome == ERROR and "no null flavors" in r.errors[0]["reason"]


def test_a_path_ubl_does_not_have_is_an_error_not_a_guess(engine, mapping, tmp_path):
    import yaml
    doc = yaml.safe_load(mapping_path(CT).read_text())
    for rule in doc["rules"]:
        if rule.get("to") == "cbc:BuyerReference":
            rule["to"] = "cbc:BuyersReference"
    p = tmp_path / "m.yaml"
    p.write_text(yaml.safe_dump(doc, sort_keys=False))
    r = run(engine, load_mapping(p), RECORDS[0].read_bytes())
    assert r.outcome == ERROR and "cbc:BuyersReference is not a member of Invoice" in r.errors[0]["reason"]


def test_a_component_with_no_rule_is_an_incomplete_mapping(engine, mapping, tmp_path):
    import yaml
    doc = yaml.safe_load(mapping_path(CT).read_text())
    doc["rules"] = [r for r in doc["rules"] if r.get("to") != "cbc:BuyerReference"]
    p = tmp_path / "m.yaml"
    p.write_text(yaml.safe_dump(doc, sort_keys=False))
    r = run(engine, load_mapping(p), RECORDS[0].read_bytes())
    assert r.outcome == ERROR and "Buyer Reference" in r.errors[0]["reason"]


def test_a_mapping_for_another_model_is_refused(engine):
    with pytest.raises(MappingError):
        load_mapping(mapping_path(CT)).check("x" * 24, "0" * 64, "OASIS UBL", "2.3")
