"""The business documents library's Credit Note model as an OASIS UBL 2.3 CreditNote.

Where each value goes was worked out first in HalvorsenDemo's hand-written UBL writer (ubl/credit_note.py), the
Invoice's with the credit note's own parts: the discrepancy the credit resolves is UBL's DiscrepancyResponse, on the
document and on each line.
"""
from common import (ALLOWANCES_AND_TAX, AMOUNT, C, DELIVERY, DOCUMENT_REFERENCES, HEADER, ITEM_AND_PRICE,
                    LINE_REFERENCES, OMIT, PARTIES, PAYMENT_TERMS, QUANTITY, V, monetary_total, payment_means, record)

TITLE = "Credit Note (business documents library) to OASIS UBL 2.3 CreditNote"
ID = "credit-note-ubl-2.3"
VERSION = 1
AUTHOR = "Axius SDC, Inc."
DATE = "2026-10-25"
DESCRIPTION = ("The Credit Note model's values in a UBL 2.3 CreditNote. Declared: the library links its components to "
               "UBL's aggregates, not to each basic component. The payment means and allowance charge reason codes are "
               "the model's own bindings to UBL's code lists.")
DOCUMENT = "CreditNote"

RULES = [
    *record("Credit Note Governed Record", "Credit Note", "CreditNote"),
    C("Credit Note Document", "."),
    *HEADER,
    V("Credit Note ID", "cbc:ID"),
    V("Due Date", "cbc:DueDate"),
    V("Credit Note Type", "cbc:CreditNoteTypeCode", listURI=True),
    V("Tax Point Date", "cbc:TaxPointDate"),
    V("Tax Currency", "cbc:TaxCurrencyCode"),
    V("Payment Currency", "cbc:PaymentCurrencyCode"),
    V("Buyer Reference", "cbc:BuyerReference"),
    OMIT("Document Status", "UBL's CreditNote carries no document status"),
    C("Invoice Period", "cac:InvoicePeriod"),
    C("Discrepancy Response", "cac:DiscrepancyResponse"),
    V("Discrepancy Reference ID", "cbc:ReferenceID"),
    V("Discrepancy Response Code", "cbc:ResponseCode"),
    V("Discrepancy Description", "cbc:Description"),
    V("Discrepancy Effective Date", "cbc:EffectiveDate"),

    C("Order Reference", "cac:OrderReference"),
    V("Order ID", "cbc:ID"),
    V("Sales Order ID", "cbc:SalesOrderID"),
    V("Order Type", "cbc:OrderTypeCode", listURI=True),
    C("Billing Reference", "cac:BillingReference"),
    C("Invoice Document Reference", "cac:InvoiceDocumentReference"),
    C("Despatch Document Reference", "cac:DespatchDocumentReference"),
    C("Receipt Document Reference", "cac:ReceiptDocumentReference"),
    *DOCUMENT_REFERENCES,
    C("Contract", "cac:ContractDocumentReference"),
    V("Contract Type", "cbc:DocumentType"),

    C("Accounting Supplier Party", "cac:AccountingSupplierParty"),
    C("Payee Party", "cac:PayeeParty"),
    C("Tax Representative Party", "cac:TaxRepresentativeParty"),
    C("Party", ".", within=["Payee Party"]),
    C("Party", ".", within=["Tax Representative Party"]),
    *PARTIES,

    *DELIVERY,
    *payment_means("Payment Means Instruction"),
    *PAYMENT_TERMS,
    *ALLOWANCES_AND_TAX,
    C("Withholding Tax Total", "cac:WithholdingTaxTotal"),
    C("Tax Total", ".", within=["Withholding Tax Total"]),
    *monetary_total("Legal Monetary Total", "cac:LegalMonetaryTotal"),

    C("Credit Note Lines", "."),
    *[C(f"Credit Note Line {n}", ".", order=n) for n in range(1, 11)],
    C("Credit Note Line", "cac:CreditNoteLine"),
    *ITEM_AND_PRICE,
    V("Credited Quantity", "cbc:CreditedQuantity", **QUANTITY),
    V("Tax Inclusive Line Extension Amount", "cbc:TaxInclusiveLineExtensionAmount", **AMOUNT),
    V("Free of Charge", "cbc:FreeOfChargeIndicator"),
    *LINE_REFERENCES,
]
