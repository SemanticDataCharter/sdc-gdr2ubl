"""The business documents library's Remittance Advice model as an OASIS UBL 2.3 RemittanceAdvice.

Where each value goes was worked out first in HalvorsenDemo's hand-written UBL writer (ubl/remittance_advice.py): the
totals debited, credited and paid and the payer's references are UBL's own header elements; the invoice paid and the
credit note taken into account are a billing reference's invoice and credit note document references.
"""
from common import (AMOUNT, C, DOCUMENT_REFERENCES, HEADER, ALLOWANCES_AND_TAX, OMIT, PARTIES, V, payment_means,
                    record)

TITLE = "Remittance Advice (business documents library) to OASIS UBL 2.3 RemittanceAdvice"
ID = "remittance-advice-ubl-2.3"
VERSION = 1
AUTHOR = "Axius SDC, Inc."
DATE = "2026-10-25"
DESCRIPTION = ("The Remittance Advice model's values in a UBL 2.3 RemittanceAdvice. Declared: the library links its "
               "components to UBL's aggregates, not to each basic component. The payment means code is the model's "
               "own binding to UBL's code list.")
DOCUMENT = "RemittanceAdvice"

RULES = [
    *record("Remittance Advice Governed Record", "Remittance Advice", "RemittanceAdvice"),
    C("Remittance Advice Document", "."),
    *HEADER,
    V("Remittance Advice ID", "cbc:ID"),
    V("Total Debit Amount", "cbc:TotalDebitAmount", **AMOUNT),
    V("Total Credit Amount", "cbc:TotalCreditAmount", **AMOUNT),
    V("Total Payment Amount", "cbc:TotalPaymentAmount", **AMOUNT),
    V("Payment Order Reference", "cbc:PaymentOrderReference"),
    V("Payer Reference", "cbc:PayerReference"),
    V("Invoicing Party Reference", "cbc:InvoicingPartyReference"),
    OMIT("Document Status", "UBL's RemittanceAdvice carries no document status"),
    C("Invoice Period", "cac:InvoicePeriod"),

    C("Billing Reference", "cac:BillingReference"),
    C("Invoice Document Reference", "cac:InvoiceDocumentReference"),
    C("Credit Note Document Reference", "cac:CreditNoteDocumentReference"),
    *DOCUMENT_REFERENCES,

    C("Accounting Supplier Party", "cac:AccountingSupplierParty"),
    C("Payee Party", "cac:PayeeParty"),
    C("Party", ".", within=["Payee Party"]),
    *PARTIES,

    *payment_means("Payment Means Instruction"),
    *ALLOWANCES_AND_TAX,

    C("Remittance Advice Lines", "."),
    *[C(f"Remittance Advice Line {n}", ".", order=n) for n in range(1, 11)],
    C("Remittance Advice Line", "cac:RemittanceAdviceLine"),
    V("Line ID", "cbc:ID"),
    V("Debit Line Amount", "cbc:DebitLineAmount", **AMOUNT),
    V("Credit Line Amount", "cbc:CreditLineAmount", **AMOUNT),
    V("Balance Amount", "cbc:BalanceAmount", **AMOUNT),
    V("Payment Purpose", "cbc:PaymentPurposeCode"),
]
