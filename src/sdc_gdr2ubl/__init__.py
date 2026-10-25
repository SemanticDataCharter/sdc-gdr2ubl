"""sdc-gdr2ubl: Governed Data Records as OASIS UBL 2.3 documents, through sdc-mapper.

    from sdc_mapper import Engine, load_mapping
    from sdc_gdr2ubl import UBLMapper, mapping_path
    result = Engine(models).map_record(xml, UBLMapper(), load_mapping(mapping_path("u19w614300a8ot4a7qnn2o1c")))

One mapping file per model, in `mappings/`. Registered with sdc-mapper as the target `ubl`.
"""
from pathlib import Path

__version__ = "4.0.1"

MAPPINGS = Path(__file__).with_name("mappings")


def mapping_path(ct_id: str) -> Path:
    """The mapping file this package publishes for a model, by the model's identifier."""
    found = sorted(MAPPINGS.glob(f"*-{ct_id}.yaml"))
    if not found:
        raise FileNotFoundError(f"sdc-gdr2ubl has no mapping for model {ct_id}")
    return found[-1]


from .mapper import UBLMapper  # noqa: E402

__all__ = ["UBLMapper", "mapping_path", "MAPPINGS", "__version__"]
