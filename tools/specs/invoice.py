"""The business documents library's Invoice model as an OASIS UBL 2.3 Invoice.

Where each value goes was worked out first in HalvorsenDemo's hand-written UBL writer (ubl/invoice.py and the Order
writer it builds on); this spec states the same placements as data, composed with the rules every library document
shares (common.py).
"""
from common import (ALLOWANCES_AND_TAX, AMOUNT, C, DELIVERY, DOCUMENT_REFERENCES, HEADER, ITEM_AND_PRICE,
                    LINE_REFERENCES, OMIT, PARTIES, PAYMENT_TERMS, QUANTITY, V, monetary_total, payment_means, record)

TITLE = "Invoice (business documents library) to OASIS UBL 2.3 Invoice"
ID = "invoice-ubl-2.3"
VERSION = 1
AUTHOR = "Axius SDC, Inc."
DATE = "2026-10-25"
DESCRIPTION = ("The Invoice model's values in a UBL 2.3 Invoice. Declared: the library links its components to UBL's "
               "aggregates, not to each basic component. The payment means and allowance charge reason codes are the "
               "model's own bindings to UBL's code lists.")
DOCUMENT = "Invoice"

RULES = [
    *record("Invoice Governed Record", "Invoice", "Invoice"),
    C("Invoice Document", "."),
    *HEADER,
    V("Invoice ID", "cbc:ID"),
    V("Due Date", "cbc:DueDate"),
    V("Invoice Type", "cbc:InvoiceTypeCode", listURI=True),
    V("Tax Point Date", "cbc:TaxPointDate"),
    V("Tax Currency", "cbc:TaxCurrencyCode"),
    V("Payment Currency", "cbc:PaymentCurrencyCode"),
    V("Buyer Reference", "cbc:BuyerReference"),
    OMIT("Document Status", "UBL's Invoice carries no document status"),
    C("Invoice Period", "cac:InvoicePeriod"),

    C("Order Reference", "cac:OrderReference"),
    V("Order ID", "cbc:ID"),
    V("Sales Order ID", "cbc:SalesOrderID"),
    V("Order Type", "cbc:OrderTypeCode", listURI=True),
    C("Billing Reference", "cac:BillingReference"),
    C("Invoice Document Reference", "cac:InvoiceDocumentReference"),
    C("Despatch Document Reference", "cac:DespatchDocumentReference"),
    C("Receipt Document Reference", "cac:ReceiptDocumentReference"),
    *DOCUMENT_REFERENCES,
    C("Contract", "cac:ContractDocumentReference"),    # UBL's Invoice refers to the contract as a document
    V("Contract Type", "cbc:DocumentType"),

    C("Accounting Supplier Party", "cac:AccountingSupplierParty"),
    C("Payee Party", "cac:PayeeParty"),
    C("Tax Representative Party", "cac:TaxRepresentativeParty"),
    # UBL's PayeeParty and TaxRepresentativeParty are themselves of UBL's PartyType
    C("Party", ".", within=["Payee Party"]),
    C("Party", ".", within=["Tax Representative Party"]),
    *PARTIES,

    *DELIVERY,
    *payment_means("Payment Means Instruction"),
    *PAYMENT_TERMS,
    C("Prepaid Payment", "cac:PrepaidPayment"),
    V("Payment ID", "cbc:ID"),
    V("Paid Amount", "cbc:PaidAmount", **AMOUNT),
    V("Payment Received Date", "cbc:ReceivedDate"),
    V("Paid Date", "cbc:PaidDate"),
    V("Payment Instruction ID", "cbc:InstructionID"),

    *ALLOWANCES_AND_TAX,
    C("Withholding Tax Total", "cac:WithholdingTaxTotal"),
    C("Tax Total", ".", within=["Withholding Tax Total"]),
    *monetary_total("Legal Monetary Total", "cac:LegalMonetaryTotal"),

    C("Invoice Lines", "."),
    *[C(f"Invoice Line {n}", ".", order=n) for n in range(1, 11)],
    C("Invoice Line", "cac:InvoiceLine"),
    *ITEM_AND_PRICE,
    V("Invoiced Quantity", "cbc:InvoicedQuantity", **QUANTITY),
    V("Tax Inclusive Line Extension Amount", "cbc:TaxInclusiveLineExtensionAmount", **AMOUNT),
    V("Free of Charge", "cbc:FreeOfChargeIndicator"),
    *LINE_REFERENCES,
]
