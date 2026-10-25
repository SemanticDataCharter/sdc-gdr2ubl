"""The business documents library's Order model as an OASIS UBL 2.3 Order.

Where each value goes was worked out first in HalvorsenDemo's hand-written UBL writer (ubl/order.py); this spec
states the same placements as data, composed with the rules every library document shares (common.py).
"""
from common import (ALLOWANCES_AND_TAX, AMOUNT, C, DELIVERY, DOCUMENT_REFERENCES, HEADER, ITEM_AND_PRICE, OMIT,
                    PARTIES, PAYMENT_TERMS, QUANTITY, V, monetary_total, payment_means, record)

TITLE = "Order (business documents library) to OASIS UBL 2.3 Order"
ID = "order-ubl-2.3"
VERSION = 1
AUTHOR = "Axius SDC, Inc."
DATE = "2026-10-25"
DESCRIPTION = ("The Order model's values in a UBL 2.3 Order. Declared: the library links its components to UBL's "
               "aggregates, not to each basic component. The payment means and allowance charge reason codes are the "
               "model's own bindings to UBL's code lists.")
DOCUMENT = "Order"

RULES = [
    *record("Order Governed Record", "Order", "Order"),
    C("Order Document", "."),
    *HEADER,
    V("Order ID", "cbc:ID"),
    V("Sales Order ID", "cbc:SalesOrderID"),
    V("Order Type", "cbc:OrderTypeCode", listURI=True),
    V("Customer Reference", "cbc:CustomerReference"),
    C("Validity Period", "cac:ValidityPeriod"),

    C("Quotation Document Reference", "cac:QuotationDocumentReference"),
    C("Catalogue Reference", "cac:CatalogueReference"),
    # UBL's CatalogueReference is its own aggregate: a description, and no document type (the element is the type)
    V("Document Description", "cbc:Description", within=["Catalogue Reference"]),
    OMIT("Document Type", "UBL's CatalogueReference fixes the type: the element is a catalogue reference",
         within=["Catalogue Reference"]),
    *DOCUMENT_REFERENCES,
    C("Contract", "cac:Contract"),                      # UBL's Order carries the contract itself
    V("Contract Type", "cbc:ContractType"),

    C("Originator Customer Party", "cac:OriginatorCustomerParty"),
    *PARTIES,

    *DELIVERY,
    *payment_means("Payment Means"),
    *PAYMENT_TERMS,
    *ALLOWANCES_AND_TAX,
    *monetary_total("Anticipated Monetary Total", "cac:AnticipatedMonetaryTotal"),

    C("Order Lines", "."),
    *[C(f"Order Line {n}", ".") for n in range(1, 11)],
    C("Order Line", "cac:OrderLine"),
    C("Line Item", "cac:LineItem"),
    *ITEM_AND_PRICE,
    V("Ordered Quantity", "cbc:Quantity", **QUANTITY),
    V("Total Tax Amount", "cbc:TotalTaxAmount", **AMOUNT),
    V("Partial Delivery Allowed", "cbc:PartialDeliveryIndicator"),
    V("Back Order Allowed", "cbc:BackOrderAllowedIndicator"),
]
