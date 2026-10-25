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
]
GOLDEN = [(d, g) for d in DOCUMENTS for g in sorted((ROOT / "tests" / "golden" / d[0]).glob("*.xml"))]


@pytest.fixture(scope="module")
def engine(tmp_path_factory):
    return Engine(schema_dir=tmp_path_factory.mktemp("schemas"))


def run(engine, doc, xml: bytes):
    _, sample, ct, _ = doc
    return engine.map_record(xml, UBLMapper(), load_mapping(mapping_path(ct)), directory=str(ROOT / "samples" / sample))


def _dimensions_by_attribute(el):
    """UBL gives repeated Dimensions no order; HalvorsenDemo writes them in its own list's order, this mapping in the
    record's. Compared as a set, by AttributeID."""
    dims = [c for c in el if etree.QName(c).localname == "Dimension"]
    if len(dims) > 1:
        at = list(el).index(dims[0])
        for d in dims:
            el.remove(d)
        for k, d in enumerate(sorted(dims, key=lambda d: d.findtext("{*}AttributeID") or "")):
            el.insert(at + k, d)
    for c in el:
        _dimensions_by_attribute(c)
    return el


def flat(el, path=""):
    """Every element in document order: its path, text and attributes (listURI's value aside: HalvorsenDemo names the
    library's page for the list, this mapping the list component's own IRI)."""
    p = f"{path}/{etree.QName(el).localname}"
    attrs = dict(el.attrib)
    has_list = attrs.pop("listURI", None) is not None
    out = [(p, (el.text or "").strip(), tuple(sorted(attrs.items())), has_list)]
    for c in el:
        out += flat(c, p)
    return out


@pytest.mark.parametrize("doc,golden", GOLDEN, ids=lambda x: x.stem if isinstance(x, Path) else x[0])
def test_equivalent_to_the_hand_written_writer(engine, doc, golden):
    r = run(engine, doc, (ROOT / "samples" / doc[1] / "records" / golden.name).read_bytes())
    assert r.outcome == VALID, r.errors
    ours = _dimensions_by_attribute(etree.fromstring(r.files[f"{doc[3]}.xml"]))
    assert flat(ours) == flat(_dimensions_by_attribute(etree.fromstring(golden.read_bytes())))


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
    assert payment and all(v["class"] == LOOKUP for v in payment), "the model binds the payment means to UBL's list"
    audit = [v for v in r.report.values if v["path"][1:2] == ["Audit Event"]]
    assert audit and all(v["class"] == NOT_REPRESENTABLE for v in audit)
    lists = [el for el in etree.fromstring(r.files[f"{doc[3]}.xml"]).iter() if el.get("listURI")]
    assert lists and all(el.get("listURI").startswith(f"{SDC4}mc-") for el in lists)
