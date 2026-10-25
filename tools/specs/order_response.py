"""The business documents library's Order Response model as an OASIS UBL 2.3 OrderResponse.

Where each value goes was worked out first in HalvorsenDemo's hand-written UBL writer (ubl/order_response.py). The
answer to each line belongs to the response line, and UBL has no element for it beside the line item's status, so it
goes in the line item's LineStatusCode, with the line response component as the list; the line item's own status is
left out on a response line, with the reason.
"""
from common import (ALLOWANCES_AND_TAX, C, DELIVERY, DOCUMENT_REFERENCES, HEADER, ITEM_AND_PRICE, LINE_REFERENCES,
                    OMIT, PARTIES, PAYMENT_TERMS, QUANTITY, SHIPMENT_MEASURES, AMOUNT, V, monetary_total,
                    payment_means, record)

TITLE = "Order Response (business documents library) to OASIS UBL 2.3 OrderResponse"
ID = "order-response-ubl-2.3"
VERSION = 1
AUTHOR = "Axius SDC, Inc."
DATE = "2026-10-25"
DESCRIPTION = ("The Order Response model's values in a UBL 2.3 OrderResponse. Declared: the library links its components "
               "to UBL's aggregates, not to each basic component. The payment means and allowance charge reason codes "
               "are the model's own bindings to UBL's code lists.")
DOCUMENT = "OrderResponse"

SUBSTITUTES = ("Seller Proposed Substitute Line Item", "Seller Substituted Line Item")

RULES = [
    *record("Order Response Governed Record", "Order Response", "OrderResponse"),
    C("Order Response Document", "."),
    *HEADER,
    V("Order Response ID", "cbc:ID"),
    V("Sales Order ID", "cbc:SalesOrderID"),
    V("Order Response Type", "cbc:OrderResponseCode", listURI=True),
    V("Customer Reference", "cbc:CustomerReference"),
    C("Validity Period", "cac:ValidityPeriod"),
    C("Response Shipment Totals", "."),
    V("Total Packages Quantity", "cbc:TotalPackagesQuantity"),
    *SHIPMENT_MEASURES,

    C("Order Reference", "cac:OrderReference"),
    V("Order ID", "cbc:ID"),
    V("Order Type", "cbc:OrderTypeCode", listURI=True),
    C("Order Document Reference", "cac:OrderDocumentReference"),
    C("Order Change Document Reference", "cac:OrderChangeDocumentReference"),
    *DOCUMENT_REFERENCES,
    C("Contract", "cac:Contract"),
    V("Contract Type", "cbc:ContractType"),
    C("Transaction Conditions", "cac:TransactionConditions"),
    V("Transaction Conditions ID", "cbc:ID"),
    V("Transaction Conditions Description", "cbc:Description"),
    C("Document Reference", "cac:DocumentReference", within=["Transaction Conditions"]),

    C("Accounting Supplier Party", "cac:AccountingSupplierParty"),
    C("Originator Customer Party", "cac:OriginatorCustomerParty"),
    *PARTIES,

    *DELIVERY,
    *payment_means("Payment Means Instruction"),
    *PAYMENT_TERMS,
    *ALLOWANCES_AND_TAX,
    *monetary_total("Legal Monetary Total", "cac:LegalMonetaryTotal"),

    C("Order Response Lines", "."),
    *[C(f"Order Response Line {n}", ".", order=n) for n in range(1, 11)],
    C("Order Response Line", "cac:OrderLine"),
    C("Line Item", "cac:LineItem"),
    *ITEM_AND_PRICE,
    V("Ordered Quantity", "cbc:Quantity", **QUANTITY),
    V("Total Tax Amount", "cbc:TotalTaxAmount", **AMOUNT),
    V("Partial Delivery Allowed", "cbc:PartialDeliveryIndicator"),
    V("Back Order Allowed", "cbc:BackOrderAllowedIndicator"),
    # the line's answer, in the line item's status
    V("Line Response", "=cac:LineItem/cbc:LineStatusCode", listURI=True),
    OMIT("Line Status", "a response line's status is its answer (Line Response); UBL has one LineStatusCode",
         within=["Order Response Line", "Line Item"]),
    *[C(s, f"cac:{s.replace(' ', '')}") for s in SUBSTITUTES],
    *[C("Line Item", ".", within=[s]) for s in SUBSTITUTES],
    *[V("Line Status", "cbc:LineStatusCode", listURI=True, within=["Order Response Line", s, "Line Item"])
      for s in SUBSTITUTES],
    *LINE_REFERENCES,
]
