# Changelog

## 4.0.0 (unreleased)

The first target mapper of the sdc-mapper line: Governed Data Records as conformant OASIS UBL 2.3 documents.

- **The writer**, driven by the OASIS UBL 2.3 schemas (carried unmodified): member order, required aggregates added
  empty, aggregates missing a required basic component left out with the reason, conformance checked on every
  document.
- **The Invoice mapping** for the business documents library's Invoice model (`u19w614300a8ot4a7qnn2o1c`), 212
  rules, written by `tools/build_mapping.py` from a spec in the model's labels. Equivalent, element by element, to
  HalvorsenDemo's hand-written UBL writer for all 52 sample records, apart from `listURI`, which names the list
  component's published identifier.
- **Exceptional Values are lost**: UBL has no null flavors. Where UBL requires the value, the aggregate or the document
  cannot be written, and the report or the error says which element UBL requires.
