"""Every published mapping: conformant UBL for every sample record, and equivalent to HalvorsenDemo's hand-written
writer for the golden records."""
from __future__ import annotations

from pathlib import Path

import pytest
from lxml import etree

from sdc_mapper import DECLARED, LOOKUP, NOT_REPRESENTABLE, VALID, Engine, load_mapping
from sdc_gdr2ubl import UBLMapper, mapping_path
from sdc_gdr2ubl.writer import schema_for

ROOT = Path(__file__).resolve().parents[1]
SDC4 = "https://semanticdatacharter.com/ns/sdc4/"
#: (golden directory, sample directory, model, UBL document)
DOCUMENTS = [
    ("invoice", "halvorsen-invoice", "u19w614300a8ot4a7qnn2o1c", "Invoice"),
    ("order", "halvorsen-order", "h8bttbt9afwzf9zs4jhae566", "Order"),
    ("order-response", "halvorsen-order-response", "kuntv2wlkw54h7nxe0kqhvi2", "OrderResponse"),
    ("despatch-advice", "halvorsen-despatch-advice", "cacl4njrwanj15g3p3so8t6h", "DespatchAdvice"),
    ("receipt-advice", "halvorsen-receipt-advice", "tog0v0p1zit1xwpxysxwpf3d", "ReceiptAdvice"),
    ("credit-note", "halvorsen-credit-note", "jkuyr38hydqaiwlq5vhp2rjr", "CreditNote"),
    ("remittance-advice", "halvorsen-remittance-advice", "fgtbf38cj0bwxppxn69etcci", "RemittanceAdvice"),
    ("torvale-order", "halvorsen-torvale-order", "cq1fjrvyn0fxl1kyk9y3kr1w", "Order"),
]
GOLDEN = [(d, g) for d in DOCUMENTS for g in sorted((ROOT / "tests" / "golden" / d[0]).glob("*.xml"))]


@pytest.fixture(scope="module")
def engine(tmp_path_factory):
    return Engine(schema_dir=tmp_path_factory.mktemp("schemas"))


def run(engine, doc, xml: bytes):
    _, sample, ct, _ = doc
    return engine.map_record(xml, UBLMapper(), load_mapping(mapping_path(ct)), directory=str(ROOT / "samples" / sample))


#: Repeats UBL gives no order: HalvorsenDemo writes them in its own lists' order, this mapping in the record's.
UNORDERED = {"Dimension", "MeasurementDimension", "Status", "ShipmentDocumentReference", "AdditionalDocumentReference"}
#: Where the two name a component: HalvorsenDemo by the library's page, this mapping by the component's own IRI.
COMPONENT = ("https://axius-sdc.com/library/", f"{SDC4}mc-")


def _unordered_repeats_sorted(el):
    for name in UNORDERED:
        group = [c for c in el if etree.QName(c).localname == name]
        if len(group) > 1:
            at = list(el).index(group[0])
            for g in group:
                el.remove(g)
            for k, g in enumerate(sorted(group, key=lambda g: str(flat(g)))):
                el.insert(at + k, g)
    for c in el:
        _unordered_repeats_sorted(c)
    return el


def flat(el, path=""):
    """Every element in document order: its path, its text and its attributes, with a component named by either form
    as one (listURI, a check's description)."""
    p = f"{path}/{etree.QName(el).localname}"
    attrs = dict(el.attrib)
    has_list = attrs.pop("listURI", None) is not None
    text = (el.text or "").strip()
    out = [(p, "<component>" if text.startswith(COMPONENT) else text, tuple(sorted(attrs.items())), has_list)]
    for c in el:
        out += flat(c, p)
    return out


@pytest.mark.parametrize("doc,golden", GOLDEN, ids=lambda x: x.stem if isinstance(x, Path) else x[0])
def test_equivalent_to_the_hand_written_writer(engine, doc, golden):
    r = run(engine, doc, (ROOT / "samples" / doc[1] / "records" / golden.name).read_bytes())
    assert r.outcome == VALID, r.errors
    ours = _unordered_repeats_sorted(etree.fromstring(r.files[f"{doc[3]}.xml"]))
    assert flat(ours) == flat(_unordered_repeats_sorted(etree.fromstring(golden.read_bytes())))


@pytest.mark.parametrize("doc", DOCUMENTS, ids=lambda d: d[0])
def test_every_record_maps_to_a_conformant_document(engine, doc):
    schema = schema_for(doc[3])
    for f in sorted((ROOT / "samples" / doc[1] / "records").glob("*.xml")):
        r = run(engine, doc, f.read_bytes())
        assert r.outcome == VALID, (f.name, r.errors)
        assert schema.is_valid(etree.fromstring(r.files[f"{doc[3]}.xml"])), f.name


@pytest.mark.parametrize("doc", DOCUMENTS, ids=lambda d: d[0])
def test_the_report_accounts_for_every_value(engine, doc):
    f = sorted((ROOT / "samples" / doc[1] / "records").glob("*.xml"))[0]
    r = run(engine, doc, f.read_bytes())
    assert {v["class"] for v in r.report.values} <= {DECLARED, LOOKUP, NOT_REPRESENTABLE}
    payment = [v for v in r.report.values if v["label"] == "Payment Means"]
    assert all(v["class"] == LOOKUP for v in payment), "the model binds the payment means to UBL's list"
    audit = [v for v in r.report.values if v["path"][1:2] == ["Audit Event"]]
    assert audit and all(v["class"] == NOT_REPRESENTABLE for v in audit)
    lists = [el for el in etree.fromstring(r.files[f"{doc[3]}.xml"]).iter() if el.get("listURI")]
    assert lists and all(el.get("listURI").startswith(f"{SDC4}mc-") for el in lists)
