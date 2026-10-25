"""The UBL 2.3 mapper: a Governed Data Record as an OASIS UBL 2.3 document, by a mapping file.

UBL binds meaning at the level of its aggregates, and the business documents library links its components to UBL's
aggregates, not to each basic component, so where a value goes in UBL is declared in a mapping file, one per model.
Where the model does bind a value to UBL (a payment means bound to UBL's PaymentMeansCode list), the mapping's
`binding` transform takes the code from the model, and the value is a lookup.

UBL has no null flavors: an Exceptional Value has nothing to say it with, and is lost; when UBL requires the element
whose value is exceptional, the element (or the document) cannot be written, and the report says so.
"""
from __future__ import annotations

from lxml import etree

from sdc_mapper import (DECLARED, JOIN, LOOKUP, LOST, NOT_REPRESENTABLE, EVRule, IncompleteMapping, MapResult,
                        MappingError, ValueOutcome, place)
from sdcreader.record import EXCEPTIONAL_VALUES

from . import __version__
from .writer import UBL_VERSION, Builder

#: What a UBL document cannot hold for any record.
CANNOT_HOLD = [
    "Exceptional Values: UBL has no null flavors",
    "validity windows and the time a value was recorded (act, vtb, vte, tr)",
    "the definitions the model binds each component to, beyond a list's listURI",
    "the record's provenance and audit clusters",
]


class UBLMapper:
    name = "ubl"
    target = "OASIS UBL"
    target_version = UBL_VERSION
    package = "sdc-gdr2ubl"
    version = __version__
    ev_table = {code: EVRule(LOST) for code in EXCEPTIONAL_VALUES}

    def map(self, record, mapping) -> MapResult:
        if mapping is None:
            raise MappingError("UBL needs a mapping file: the model does not say where its values go in UBL")
        if mapping.carry_rejected:
            raise MappingError("UBL has no place to carry a rejected value; carry_rejected is not available")
        for code, override in mapping.exceptional_values.items():
            if override["class"] != LOST:
                raise MappingError(f"UBL cannot say {code}: it has no null flavors, so an Exceptional Value is lost")
        placements, clusters = place(record, mapping)
        document = self._document(placements)
        b = Builder(document, mapping.cluster_order)
        notes: dict[int, str] = {}
        later = []                      # writes through '=name' steps wait until every element they may join exists
        for p in placements:
            v = p.value
            if v.exceptional or p.omitted or p.rule is None or not p.steps:
                continue
            if p.text is None:
                notes[v.position] = p.note or "no value to write"
                continue
            writes = [(p.steps, p.attribute, p.text, v.position, p)]
            writes += [(e.steps, e.attribute, e.text, None, None) for e in p.extras if e.text is not None]
            for w in writes:
                if any(key == JOIN for _, key in w[0]):
                    later.append(w)
                else:
                    self._write(b, *w)
        for w in later:
            self._write(b, *w)
        for c in clusters:
            if c.attributes:
                node = b.find(c.steps)
                if node is not None:
                    node.attrs.update(c.attributes)
        root = b.finish()
        outcomes = []
        missing = []
        for p in placements:
            v = p.value
            if v.exceptional:
                outcomes.append(ValueOutcome(v.position, LOST, note="UBL has no null flavors"))
            elif p.omitted:
                outcomes.append(ValueOutcome(v.position, NOT_REPRESENTABLE, note=p.omitted_by.reason or ""))
            elif p.rule is None:
                missing.append(f"{' / '.join(v.path_labels + [v.label])} ({v.ct_id})")
            elif v.position in notes:
                outcomes.append(ValueOutcome(v.position, NOT_REPRESENTABLE, note=notes[v.position]))
            elif v.position in b.pruned:
                outcomes.append(ValueOutcome(v.position, NOT_REPRESENTABLE, note=b.pruned[v.position]))
            else:
                cls = LOOKUP if p.rule.transform == "binding" else DECLARED
                where = "/".join(n for n, _ in p.steps) + (f"/@{p.attribute}" if p.attribute else "")
                outcomes.append(ValueOutcome(v.position, cls, location=where))
        if missing:
            raise IncompleteMapping(f"mapping {mapping.id} has no rule for {len(missing)} value(s): " + "; ".join(missing[:5]))
        xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)
        return MapResult(files={f"{document}.xml": xml}, outcomes=outcomes, cannot_hold=list(CANNOT_HOLD))

    @staticmethod
    def _write(b, steps, attribute, text, position, p):
        node = b.put(steps, attribute, text, position)
        if p is not None:           # the value's own element: its constant attributes and its units
            node.attrs.update(p.attributes)
            if p.units_attribute and p.units_text is not None:
                node.attrs[p.units_attribute] = p.units_text

    @staticmethod
    def _document(placements) -> str:
        for p in placements:
            if p.steps:
                return p.steps[0][0]
        raise MappingError("nothing to write: no value of the record reached the document")

