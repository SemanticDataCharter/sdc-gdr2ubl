"""The business documents library's Receipt Advice model as an OASIS UBL 2.3 ReceiptAdvice.

Where each value goes was worked out first in HalvorsenDemo's hand-written UBL writer (ubl/receipt_advice.py): the
date and time the goods actually arrived are the shipment's delivery's; each received handling unit carries its
receiving condition as UBL's Status, and each check made on receipt as a Status of its own, described by the check's
component.
"""
from common import (DOCUMENT_REFERENCES, HEADER, ITEM_AND_PRICE, LINE_REFERENCES, PACK_SPECIFICATION_DOCUMENT,
                    PARTIES, QUANTITY, TAX_CATEGORY, SHIPMENT, C, DELIVERY, V, record, unit_document)

TITLE = "Receipt Advice (business documents library) to OASIS UBL 2.3 ReceiptAdvice"
ID = "receipt-advice-ubl-2.3"
VERSION = 1
AUTHOR = "Axius SDC, Inc."
DATE = "2026-10-25"
DESCRIPTION = ("The Receipt Advice model's values in a UBL 2.3 ReceiptAdvice. Declared: the library links its "
               "components to UBL's aggregates, not to each basic component.")
DOCUMENT = "ReceiptAdvice"
PACK_IN_FORCE_DOCUMENT = "Pack specification in force"

RULES = [
    *record("Receipt Advice Governed Record", "Receipt Advice", "ReceiptAdvice"),
    C("Receipt Advice Document", "."),
    *HEADER,
    V("Receipt Advice ID", "cbc:ID"),
    V("Document Status", "cbc:DocumentStatusCode", listURI=True),
    V("Receipt Advice Type", "cbc:ReceiptAdviceTypeCode", listURI=True),

    C("Order Reference", "cac:OrderReference"),
    V("Order ID", "cbc:ID"),
    V("Sales Order ID", "cbc:SalesOrderID"),
    V("Order Type", "cbc:OrderTypeCode", listURI=True),
    C("Despatch Document Reference", "cac:DespatchDocumentReference"),
    *DOCUMENT_REFERENCES,

    C("Despatch Supplier Party", "cac:DespatchSupplierParty"),
    C("Delivery Customer Party", "cac:DeliveryCustomerParty"),
    *PARTIES,

    C("Receipt Shipment", "cac:Shipment"),
    *SHIPMENT,
    *DELIVERY,
    V("Actual Delivery Date", "=cac:Delivery/cbc:ActualDeliveryDate"),
    V("Actual Delivery Time", "=cac:Delivery/cbc:ActualDeliveryTime"),
    C("Received Handling Units", "."),
    *[C(f"Received Handling Unit {n}", ".", order=n) for n in range(1, 7)],
    C("Received Handling Unit", "cac:TransportHandlingUnit"),
    V("Pack Specification Version", "+cac:ShipmentDocumentReference/cbc:ID", **unit_document(PACK_SPECIFICATION_DOCUMENT)),
    V("Pack Specification in Force", "+cac:ShipmentDocumentReference/cbc:ID", **unit_document(PACK_IN_FORCE_DOCUMENT)),
    V("Receiving Condition", "cac:Status/cbc:ConditionCode", listURI=True),
    V("Received Date", "cac:Status/cbc:ReferenceDate", within=["Received Handling Unit"]),
    V("Received Time", "cac:Status/cbc:ReferenceTime"),
    V("Exception Description", "cac:Status/cbc:Description"),
    # each check made on receipt: a Status of its own, described by the check's component
    V("Pallet ID Valid on Receipt", "+cac:Status/cbc:IndicationIndicator", iri_to="+cac:Status/cbc:Description"),
    V("Pack Specification Compliant", "+cac:Status/cbc:IndicationIndicator", iri_to="+cac:Status/cbc:Description"),

    C("Receipt Lines", "."),
    *[C(f"Receipt Line {n}", ".", order=n) for n in range(1, 11)],
    C("Receipt Line", "cac:ReceiptLine"),
    *ITEM_AND_PRICE,
    *TAX_CATEGORY,
    V("Received Quantity", "cbc:ReceivedQuantity", **QUANTITY),
    V("Short Quantity", "cbc:ShortQuantity", **QUANTITY),
    V("Shortage Action", "cbc:ShortageActionCode", listURI=True),
    V("Rejected Quantity", "cbc:RejectedQuantity", **QUANTITY),
    V("Reject Reason", "cbc:RejectReasonCode", listURI=True),
    V("Reject Reason Description", "cbc:RejectReason"),
    V("Reject Action", "cbc:RejectActionCode", listURI=True),
    V("Quantity Discrepancy", "cbc:QuantityDiscrepancyCode", listURI=True),
    V("Oversupply Quantity", "cbc:OversupplyQuantity", **QUANTITY),
    V("Received Date", "cbc:ReceivedDate"),
    V("Timing Complaint", "cbc:TimingComplaintCode", listURI=True),
    V("Timing Complaint Description", "cbc:TimingComplaint"),
    *LINE_REFERENCES,
]
