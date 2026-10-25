"""The business documents library's Despatch Advice model as an OASIS UBL 2.3 DespatchAdvice.

Where each value goes was worked out first in HalvorsenDemo's hand-written UBL writer (ubl/dispatch_advice.py): the
transport handling unit's identifier is the GS1 Serial Shipping Container Code; the pallet as an asset is UBL's
TransportEquipment, its identifier's validity period the equipment's document reference; the pack specification the
unit was packed to is the unit's document reference; layers and cases are UBL's own package containment; the loaded
pallet's height and weight are the package's measurement dimensions.
"""
from common import (DOCUMENT_REFERENCES, HEADER, ITEM_AND_PRICE, LINE_REFERENCES, PACK_SPECIFICATION_DOCUMENT,
                    PARTIES, QUANTITY, TAX_CATEGORY, REC20, SHIPMENT, C, DELIVERY, V, record)

TITLE = "Despatch Advice (business documents library) to OASIS UBL 2.3 DespatchAdvice"
ID = "despatch-advice-ubl-2.3"
VERSION = 1
AUTHOR = "Axius SDC, Inc."
DATE = "2026-10-25"
DESCRIPTION = ("The Despatch Advice model's values in a UBL 2.3 DespatchAdvice. Declared: the library links its "
               "components to UBL's aggregates, not to each basic component.")
DOCUMENT = "DespatchAdvice"


def measure(element: str, attribute: str, plus: bool = True):
    step = f"+{element}" if plus else element
    return {"units": {"to": "@unitCode", "transform": "code", "table": REC20},
            "also": [{"to": f"{step}/cbc:AttributeID", "transform": "constant", "value": attribute}]}


HANDLING_UNIT = [
    V("Transport Handling Unit Type", "cbc:TransportHandlingUnitTypeCode", listURI=True),
    V("Shipping Marks", "cbc:ShippingMarks"),
    V("Total Package Quantity", "cbc:TotalPackageQuantity"),
    V("Minimum Temperature", "cac:MinimumTemperature/cbc:Measure", **measure("cac:MinimumTemperature", "Minimum", False)),
    V("Maximum Temperature", "cac:MaximumTemperature/cbc:Measure", **measure("cac:MaximumTemperature", "Maximum", False)),
    C("Package", "cac:Package"),
    V("Package ID", "cbc:ID"),
    V("Package Quantity", "cbc:Quantity"),
    V("Packaging Type", "cbc:PackagingTypeCode", listURI=True),
    C("Pack Specification", "."),
    # the receiver's pack specification is a document; the version the unit was packed to is the unit's reference
    V("Pack Specification Version", "../+cac:ShipmentDocumentReference/cbc:ID",
      also=[{"to": "../+cac:ShipmentDocumentReference/cbc:DocumentType", "transform": "constant",
             "value": PACK_SPECIFICATION_DOCUMENT}]),
    V("Layers per Pallet", "cac:ContainedPackage/cbc:Quantity",
      also=[{"to": "cac:ContainedPackage/cbc:PackageLevelCode", "transform": "constant", "value": "Layer"}]),
    V("Cases per Layer", "cac:ContainedPackage/cac:ContainedPackage/cbc:Quantity", also=[
        {"to": "cac:ContainedPackage/cbc:PackageLevelCode", "transform": "constant", "value": "Layer"},
        {"to": "cac:ContainedPackage/cac:ContainedPackage/cbc:PackageLevelCode", "transform": "constant", "value": "Case"}]),
    V("Pallet Height", "+cac:MeasurementDimension/cbc:Measure", **measure("cac:MeasurementDimension", "Height")),
    V("Weight", "+cac:MeasurementDimension/cbc:Measure", within=["Pack Specification"],
      **measure("cac:MeasurementDimension", "Weight")),
]

RULES = [
    *record("Despatch Advice Governed Record", "Despatch Advice", "DespatchAdvice"),
    C("Despatch Advice Document", "."),
    *HEADER,
    V("Despatch Advice ID", "cbc:ID"),
    V("Document Status", "cbc:DocumentStatusCode", listURI=True),
    V("Despatch Advice Type", "cbc:DespatchAdviceTypeCode", listURI=True),

    C("Order Reference", "cac:OrderReference"),
    V("Order ID", "cbc:ID"),
    V("Sales Order ID", "cbc:SalesOrderID"),
    V("Order Type", "cbc:OrderTypeCode", listURI=True),
    *DOCUMENT_REFERENCES,

    C("Despatch Supplier Party", "cac:DespatchSupplierParty"),
    C("Delivery Customer Party", "cac:DeliveryCustomerParty"),
    C("Originator Customer Party", "cac:OriginatorCustomerParty"),
    *PARTIES,

    *SHIPMENT,
    *DELIVERY,
    V("Total Goods Item Quantity", "cbc:TotalGoodsItemQuantity"),
    V("Total Transport Handling Unit Quantity", "cbc:TotalTransportHandlingUnitQuantity"),
    C("Transport Handling Units", "."),
    *[C(f"Transport Handling Unit {n}", ".", order=n) for n in range(1, 7)],
    C("Transport Handling Unit", "cac:TransportHandlingUnit"),
    *HANDLING_UNIT,

    C("Despatch Lines", "."),
    *[C(f"Despatch Line {n}", ".", order=n) for n in range(1, 11)],
    C("Despatch Line", "cac:DespatchLine"),
    *ITEM_AND_PRICE,
    *TAX_CATEGORY,
    V("Delivered Quantity", "cbc:DeliveredQuantity", **QUANTITY),
    V("Backorder Quantity", "cbc:BackorderQuantity", **QUANTITY),
    V("Backorder Reason", "cbc:BackorderReason"),
    V("Outstanding Quantity", "cbc:OutstandingQuantity", **QUANTITY),
    V("Outstanding Reason", "cbc:OutstandingReason"),
    *LINE_REFERENCES,
]
