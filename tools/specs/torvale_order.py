"""The business documents library's Torvale Order profile as an OASIS UBL 2.3 Order.

The profile is the Order with Torvale's delivery terms and requirements; where each value goes was worked out first in
HalvorsenDemo's hand-written UBL writer (ubl/order.py, the TORVALE profile): the pack specification version Torvale
requires is a second additional document reference, of the type "Pack specification"; the delivery window in days is
the requested delivery period's DurationMeasure.
"""
import order
from common import C, PACK_SPECIFICATION_DOCUMENT, V, payment_means, record

TITLE = "Torvale Order (business documents library profile) to OASIS UBL 2.3 Order"
ID = "torvale-order-ubl-2.3"
VERSION = 1
AUTHOR = "Axius SDC, Inc."
DATE = "2026-10-25"
DESCRIPTION = ("The Torvale Order profile's values in a UBL 2.3 Order: the Order's mapping with the profile's delivery "
               "terms and requirements. Declared: the library links its components to UBL's aggregates, not to each "
               "basic component.")
DOCUMENT = "Order"

RULES = [
    *record("Torvale Order Governed Record", "Torvale Order", "Order"),
    *[r for r in order.RULES if r.get("cluster") not in ("Order Governed Record", "Order")],
    *payment_means("Payment Means Instruction"),
    C("Torvale Delivery Terms", "cac:DeliveryTerms"),
    V("Torvale Delivery Terms Code", "cbc:ID", attributes={"schemeName": "Incoterms 2020"}),
    C("Torvale Order Requirements", "."),
    V("Torvale Pack Specification Version", "+cac:AdditionalDocumentReference/cbc:ID",
      also=[{"to": "+cac:AdditionalDocumentReference/cbc:DocumentType", "transform": "constant",
             "value": PACK_SPECIFICATION_DOCUMENT}]),
    V("Torvale Delivery Window Days", "=cac:Delivery/=cac:RequestedDeliveryPeriod/cbc:DurationMeasure",
      attributes={"unitCode": "DAY"}),
]
