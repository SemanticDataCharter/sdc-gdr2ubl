# sdc-gdr2ubl

Governed Data Records as conformant OASIS UBL 2.3 documents. A target mapper for
[sdc-mapper](https://github.com/SemanticDataCharter/sdc-mapper): the core validates the record, resolves every value
against its model and reports each one; this package says where each value goes in UBL and writes the document.
Outbound only. Apache 2.0.

**Status:** 4.0.0 in development. Every document of the business documents library has a mapping:

| Model | ct_id | UBL 2.3 document | Rules |
|---|---|---|---|
| Order | `h8bttbt9afwzf9zs4jhae566` | Order | 181 |
| Torvale Order (profile) | `cq1fjrvyn0fxl1kyk9y3kr1w` | Order | 190 |
| Order Response | `kuntv2wlkw54h7nxe0kqhvi2` | OrderResponse | 204 |
| Despatch Advice | `cacl4njrwanj15g3p3so8t6h` | DespatchAdvice | 179 |
| Receipt Advice | `tog0v0p1zit1xwpxysxwpf3d` | ReceiptAdvice | 175 |
| Invoice | `u19w614300a8ot4a7qnn2o1c` | Invoice | 212 |
| Credit Note | `jkuyr38hydqaiwlq5vhp2rjr` | CreditNote | 211 |
| Remittance Advice | `fgtbf38cj0bwxppxn69etcci` | RemittanceAdvice | 112 |

## Use

```
pip install sdc-gdr2ubl
sdc-map map ubl invoice.xml --package DIR --mapping "$(python -c 'from sdc_gdr2ubl import mapping_path; print(mapping_path("u19w614300a8ot4a7qnn2o1c"))')"
```

```python
from sdc_mapper import Engine, load_mapping
from sdc_gdr2ubl import UBLMapper, mapping_path

result = Engine().map_record(xml, UBLMapper(), load_mapping(mapping_path("u19w614300a8ot4a7qnn2o1c")))
result.outcome            # valid, valid_with_ev, refused or error
result.files["Invoice.xml"]
result.report             # every value: declared, lookup or not representable, and why
```

Through sdc-mapper's MCP server the mapper is the target `ubl`.

## The target

**OASIS Universal Business Language (UBL) Version 2.3**, OASIS Standard, 15 June 2021
(http://docs.oasis-open.org/ubl/os-UBL-2.3/). Its notices allow copies, and works that assist in implementing it,
provided the copyright notice and the notices section travel with them; the standard itself may not be modified. UBL
2.3 was produced under the "RF on Limited Terms" mode of the OASIS IPR Policy. This package carries the 2.3 schemas
unmodified, under that notice (see `NOTICE`), so documents are ordered and checked without fetching anything.

Every document this package writes conforms to the OASIS schema for its document type, or is not written.

## Where values go: declared, one mapping file per model

The business documents library links its components to UBL at the level of UBL's aggregates (54 `seeAlso` links to
the UBL 2.3 specification), not to each basic component, so where a value goes in UBL is stated in a mapping file:
`src/sdc_gdr2ubl/mappings/<document>-<ct_id>.yaml`, bound to the model's schema by its SHA-256 and immutable once
published. That is the same work an organization does today from its own database to UBL, written down once per model
and checked on every record.

Where the model does bind a value to UBL, the mapping says only where it goes, and the value is a **lookup**: the
payment means and allowance charge reason components bind each of their values to UBL's code lists
(`PaymentMeansCode-2.3.gc#2`), so the code written is the model's own.

The mapping files are written with `tools/build_mapping.py` from a spec in the model's labels (`tools/specs/`: one per
document, composed with the rules every library document shares in `common.py`), which also checks that every value
the model can hold reaches a rule: placed, or omitted with a reason.

The placements were worked out first in HalvorsenDemo's hand-written UBL writers. For all 293 sample records across
the eight models, this package and those writers produce the same document, element by element, with two kinds of
difference:

- Where a document names one of the library's components (a token's `listURI`, a receipt check's description), this
  package uses the component's own published identifier (`https://semanticdatacharter.com/ns/sdc4/mc-…`), where
  HalvorsenDemo names the library's page for it.
- Repeats UBL gives no order (an item's `Dimension`s, a handling unit's `Status`es and `ShipmentDocumentReference`s)
  follow the record's order here, where HalvorsenDemo uses lists of its own. Lines follow the order each mapping
  declares (`order:` on the line clusters), so line 10 comes after line 9.

## What UBL cannot say

- **Exceptional Values.** UBL has no null flavors: a value the record marks as asked and refused, unknown, masked or
  not applicable has nothing in UBL to say it with. It is **lost**, every ISO 21090 code alike, and the report says so.
  A mapping file cannot promise otherwise.
- **When UBL requires the exceptional value.** An aggregate UBL requires a member of (a `TaxSubtotal`'s
  `TaxAmount`) cannot be written without it: the aggregate is left out, and every other value in it is reported as
  not representable with the reason (`UBL requires cbc:TaxAmount in cac:TaxSubtotal, and the record has no value for
  it`). When the document itself requires it (an Invoice's `cbc:ID`, its `LegalMonetaryTotal`), there is no document:
  the call ends as an error that says which element UBL requires.
- **The record's provenance and audit.** The PROV and audit clusters of a Governed Data Record have no place in a UBL
  document.
- Validity windows and recording times (act, vtb, vte, tr), and the definitions each component is bound to, beyond a
  list's `listURI`.
- A contact point's method and use (UBL's Contact has neither); the document status of an Invoice, a Credit Note and
  a Remittance Advice (UBL's documents of those kinds have none); a catalogue reference's document type (UBL's
  CatalogueReference is the type); on an order response line, the line item's own status (UBL has one
  `LineStatusCode` there, and it carries the line's answer).

## How the writer works

The writer knows UBL's syntax, not any model. From sdc-mapper's placements it builds one element per step and cluster
instance, then, from the OASIS schemas: orders every aggregate's members as its type's sequence does; adds a required
aggregate whose members are all optional (a `TaxCategory`'s `TaxScheme`); removes an aggregate that lacks a required
basic component, with the reason; refuses a path, attribute or repetition UBL does not have; and validates the result.
`cbc:UBLVersionID` is written as `2.3`.

## Tests

```
pip install -e ".[dev]"
python -m pytest
```

The suite maps every sample record and checks each against the OASIS schema, compares up to five of each document
with HalvorsenDemo's writers (`tests/golden/`), and exercises Exceptional Values and refused mappings.
