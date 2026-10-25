"""The business documents library's Invoice model as an OASIS UBL 2.3 Invoice.

Where each value goes was worked out first in HalvorsenDemo's hand-written UBL writer (ubl/invoice.py and the Order
writer it builds on); this spec states the same placements as data. Labels are the model's; paths are UBL's, relative
to the element of the nearest enclosing cluster that has one ('..' goes up, '+' is an element of the value's own).
"""
TITLE = "Invoice (business documents library) to OASIS UBL 2.3 Invoice"
ID = "invoice-ubl-2.3"
VERSION = 1
AUTHOR = "Axius SDC, Inc."
DATE = "2026-10-25"
DESCRIPTION = ("The Invoice model's values in a UBL 2.3 Invoice. Declared: the library links its components to UBL's "
               "aggregates, not to each basic component. The payment means and allowance charge reason codes are the "
               "model's own bindings to UBL's code lists.")

UBL_CL = "http://docs.oasis-open.org/ubl/os-UBL-2.3/cl/gc/default/"
#: UN/ECE Recommendation 20 codes for the SI unit symbols the Default library's dimension components carry.
REC20 = {"mm": "MMT", "cm": "CMT", "m": "MTR", "km": "KMT", "mg": "MGM", "g": "GRM", "kg": "KGM", "mL": "MLT",
         "L": "LTR", "°C": "CEL", "K": "KEL"}
PARTY_SCHEME_ID = {"Global Location Number (GS1)": "GLN", "DUNS number": "DUNS"}
PARTY_SCHEME_AGENCY = {"Global Location Number (GS1)": "9", "DUNS number": "16"}   # UN/ECE 3055
ITEM_SCHEME_ID = {"Global Trade Item Number (GS1)": "GTIN"}
ITEM_SCHEME_AGENCY = {"Global Trade Item Number (GS1)": "9"}


def C(label, to, **kw):
    return {"cluster": label, "to": to, **kw}


def V(label, to, transform="copy", **kw):
    return {"component": label, "to": to, "transform": transform, **kw}


def OMIT_C(label, reason, **kw):
    return {"cluster": label, "to": "-", "transform": "omit", "reason": reason, **kw}


def OMIT(label, reason, **kw):
    return {"component": label, "to": "-", "transform": "omit", "reason": reason, **kw}


AMOUNT = {"units": {"to": "@currencyID", "transform": "copy"}}
QUANTITY = {"units": {"to": "@unitCode", "transform": "copy"}}   # trade units carry their UN/ECE code already


def scheme(ids, agencies):
    return {"also": [
        {"to": "cbc:ID/@schemeID", "transform": "code", "table": ids, "on_miss": "omit"},
        {"to": "cbc:ID/@schemeAgencyID", "transform": "code", "table": agencies, "on_miss": "omit"},
    ]}


RULES = [
    # ---------------------------------------------------------------- the record and the document
    C("Invoice Governed Record", "Invoice"),
    C("Invoice", "."),
    OMIT_C("Audit Event", "the record's audit event: UBL has no place for it"),
    OMIT_C("PROV Activity", "the record's provenance: UBL has no place for it"),
    OMIT_C("PROV Agent", "the record's provenance: UBL has no place for it"),
    OMIT_C("PROV Entity", "the record's provenance: UBL has no place for it"),
    C("Invoice Document", "."),
    V("Customization ID", "cbc:CustomizationID"),
    V("Profile ID", "cbc:ProfileID"),
    V("Profile Execution ID", "cbc:ProfileExecutionID"),
    V("Invoice ID", "cbc:ID"),
    V("Copy Indicator", "cbc:CopyIndicator"),
    V("Document UUID", "cbc:UUID"),
    V("Issue Date", "cbc:IssueDate"),
    V("Issue Time", "cbc:IssueTime"),
    V("Due Date", "cbc:DueDate"),
    V("Invoice Type", "cbc:InvoiceTypeCode", listURI=True),
    V("Note", "cbc:Note"),
    V("Tax Point Date", "cbc:TaxPointDate"),
    V("Document Currency", "cbc:DocumentCurrencyCode"),
    V("Tax Currency", "cbc:TaxCurrencyCode"),
    V("Pricing Currency", "cbc:PricingCurrencyCode"),
    V("Payment Currency", "cbc:PaymentCurrencyCode"),
    V("Accounting Cost", "cbc:AccountingCost"),
    V("Line Count", "cbc:LineCountNumeric"),
    V("Buyer Reference", "cbc:BuyerReference"),
    OMIT("Document Status", "UBL's Invoice carries no document status"),
    C("Invoice Period", "cac:InvoicePeriod"),
    C("Date Range", "."),
    V("Date Range Start", "cbc:StartDate"),
    V("Date Range End", "cbc:EndDate"),

    # ---------------------------------------------------------------- references
    C("Order Reference", "cac:OrderReference"),
    V("Order ID", "cbc:ID"),
    V("Sales Order ID", "cbc:SalesOrderID"),
    V("Order Type", "cbc:OrderTypeCode", listURI=True),
    C("Billing Reference", "cac:BillingReference"),
    C("Invoice Document Reference", "cac:InvoiceDocumentReference"),
    C("Document Reference", "."),
    C("Despatch Document Reference", "cac:DespatchDocumentReference"),
    C("Receipt Document Reference", "cac:ReceiptDocumentReference"),
    C("Originator Document Reference", "cac:OriginatorDocumentReference"),
    C("Additional Document Reference", "cac:AdditionalDocumentReference"),
    C("Line Document Reference", "cac:DocumentReference"),
    V("Document Reference ID", "cbc:ID"),
    V("Document Reference Issue Date", "cbc:IssueDate"),
    V("Document Type", "cbc:DocumentType"),           # a text in UBL; the value is the library's token
    V("Document Description", "cbc:DocumentDescription"),
    C("Contract", "cac:ContractDocumentReference"),
    V("Contract ID", "cbc:ID"),
    V("Contract Issue Date", "cbc:IssueDate"),
    V("Contract Type", "cbc:DocumentType"),

    # ---------------------------------------------------------------- parties
    C("Accounting Supplier Party", "cac:AccountingSupplierParty"),
    C("Seller Supplier Party", "cac:SellerSupplierParty"),
    C("Supplier Party", "."),
    C("Accounting Customer Party", "cac:AccountingCustomerParty"),
    C("Buyer Customer Party", "cac:BuyerCustomerParty"),
    C("Customer Party", "."),
    V("Customer Assigned Account ID", "cbc:CustomerAssignedAccountID"),
    V("Supplier Assigned Account ID", "cbc:SupplierAssignedAccountID"),
    C("Payee Party", "cac:PayeeParty"),
    C("Tax Representative Party", "cac:TaxRepresentativeParty"),
    C("Delivery Party", "cac:DeliveryParty"),
    C("Party", "cac:Party"),
    # UBL's PayeeParty, TaxRepresentativeParty and DeliveryParty are themselves of UBL's PartyType
    C("Party", ".", within=["Payee Party"]),
    C("Party", ".", within=["Tax Representative Party"]),
    C("Party", ".", within=["Delivery Party"]),
    V("Endpoint ID", "cbc:EndpointID"),
    C("Party Identification", "cac:PartyIdentification"),
    V("Party Identification Value", "cbc:ID"),
    V("Party Identification Scheme", "cbc:ID/@schemeName", **scheme(PARTY_SCHEME_ID, PARTY_SCHEME_AGENCY)),
    V("Organization Name", "cac:PartyName/cbc:Name"),
    C("US Address", "cac:PostalAddress"),
    C("International Address", "cac:PostalAddress"),
    C("US Address", "cac:Address", within=["Delivery Location"]),
    C("International Address", "cac:Address", within=["Delivery Location"]),
    V("Address Use", "cbc:AddressTypeCode", listURI=True),
    V("Address (Line 1)", "cbc:StreetName"),
    V("Address (Line 2)", "cbc:AdditionalStreetName"),
    V("City Name", "cbc:CityName"),
    V("US ZIP Code", "cbc:PostalZone"),
    V("Postal Code", "cbc:PostalZone"),
    V("US State Code", "cbc:CountrySubentityCode"),
    V("Region Name", "cbc:CountrySubentity"),
    V("Country Code ISO 3166", "cac:Country/cbc:IdentificationCode"),
    C("Party Legal Entity", "cac:PartyLegalEntity"),
    V("Registration Name", "cbc:RegistrationName"),
    V("Company ID", "cbc:CompanyID"),
    C("Party Contact", "cac:Contact"),
    C("Contact Point", "."),
    V("Contact Name", "cbc:Name"),
    V("Contact Job Title", "cbc:JobTitle"),
    V("Contact Department", "cbc:Department"),
    V("Phone Number", "cbc:Telephone"),
    V("Fax Number", "cbc:Telefax"),
    V("Email Address", "cbc:ElectronicMail"),
    V("Website URL", "../cbc:WebsiteURI"),             # UBL keeps the website on the party, not the contact
    OMIT("Contact Method", "UBL's Contact has no contact method"),
    OMIT("Contact Use", "UBL's Contact has no contact use"),

    # ---------------------------------------------------------------- delivery
    C("Delivery", "cac:Delivery"),
    V("Delivery ID", "cbc:ID"),
    V("Delivery Quantity", "cbc:Quantity", **QUANTITY),
    V("Latest Delivery Date", "cbc:LatestDeliveryDate"),
    C("Delivery Location", "cac:DeliveryLocation"),
    V("Delivery Location ID", "cbc:ID"),
    V("Delivery Location Name", "cbc:Name"),
    C("Requested Delivery Period", "cac:RequestedDeliveryPeriod"),
    C("Delivery Terms", "cac:DeliveryTerms"),
    V("Delivery Terms Code", "cbc:ID", attributes={"schemeName": "Incoterms 2020"}),
    V("Delivery Special Terms", "cbc:SpecialTerms"),

    # ---------------------------------------------------------------- payment
    C("Payment Means Instruction", "cac:PaymentMeans"),
    V("Payment Means", "cbc:PaymentMeansCode", "binding", prefix=UBL_CL + "PaymentMeansCode-2.3.gc",
      also=[{"to": "cbc:PaymentMeansCode/@name", "transform": "copy"}]),
    V("Payment Due Date", "cbc:PaymentDueDate"),
    V("Note", "cbc:InstructionNote", within=["Payment Means Instruction"]),
    C("Payment Terms", "cac:PaymentTerms"),
    V("Payment Terms ID", "cbc:ID"),
    V("Settlement Discount Percent", "cbc:SettlementDiscountPercent"),
    V("Penalty Surcharge Percent", "cbc:PenaltySurchargePercent"),
    C("Settlement Period", "cac:SettlementPeriod"),
    C("Prepaid Payment", "cac:PrepaidPayment"),
    V("Payment ID", "cbc:ID"),
    V("Paid Amount", "cbc:PaidAmount", **AMOUNT),
    V("Payment Received Date", "cbc:ReceivedDate"),
    V("Paid Date", "cbc:PaidDate"),
    V("Payment Instruction ID", "cbc:InstructionID"),

    # ---------------------------------------------------------------- allowances, charges, tax, totals
    C("Allowance Charge", "cac:AllowanceCharge"),
    V("Charge Indicator", "cbc:ChargeIndicator"),
    V("Allowance Charge Reason", "cbc:AllowanceChargeReasonCode", "binding",
      prefix=UBL_CL + "AllowanceChargeReasonCode-2.3.gc",
      also=[{"to": "cbc:AllowanceChargeReasonCode/@name", "transform": "copy"}]),
    V("Allowance Charge Reason Text", "cbc:AllowanceChargeReason"),
    V("Multiplier Factor", "cbc:MultiplierFactorNumeric"),
    V("Allowance Charge Amount", "cbc:Amount", **AMOUNT),
    V("Base Amount", "cbc:BaseAmount", **AMOUNT),
    C("Tax Total", "cac:TaxTotal"),
    C("Withholding Tax Total", "cac:WithholdingTaxTotal"),
    C("Tax Total", ".", within=["Withholding Tax Total"]),
    V("Tax Amount", "cbc:TaxAmount", **AMOUNT),
    C("Tax Subtotal", "cac:TaxSubtotal"),
    V("Taxable Amount", "cbc:TaxableAmount", **AMOUNT),
    C("Tax Category", "cac:TaxCategory"),
    C("Tax Category", "cac:ClassifiedTaxCategory", within=["Item"]),
    V("Tax Category ID", "cbc:ID"),
    V("Tax Category Name", "cbc:Name"),
    V("Tax Percent", "cbc:Percent"),
    C("Tax Scheme", "cac:TaxScheme"),
    V("Tax Scheme ID", "cbc:ID"),
    V("Tax Scheme Name", "cbc:Name"),
    C("Legal Monetary Total", "cac:LegalMonetaryTotal"),
    V("Line Extension Total Amount", "cbc:LineExtensionAmount", **AMOUNT),
    V("Tax Exclusive Amount", "cbc:TaxExclusiveAmount", **AMOUNT),
    V("Tax Inclusive Amount", "cbc:TaxInclusiveAmount", **AMOUNT),
    V("Allowance Total Amount", "cbc:AllowanceTotalAmount", **AMOUNT),
    V("Charge Total Amount", "cbc:ChargeTotalAmount", **AMOUNT),
    V("Prepaid Amount", "cbc:PrepaidAmount", **AMOUNT),
    V("Payable Rounding Amount", "cbc:PayableRoundingAmount", **AMOUNT),
    V("Payable Amount", "cbc:PayableAmount", **AMOUNT),

    # ---------------------------------------------------------------- lines
    C("Invoice Lines", "."),
    *[C(f"Invoice Line {n}", ".") for n in range(1, 11)],
    C("Invoice Line", "cac:InvoiceLine"),
    V("Line ID", "cbc:ID"),
    V("Invoiced Quantity", "cbc:InvoicedQuantity", **QUANTITY),
    V("Line Extension Amount", "cbc:LineExtensionAmount", **AMOUNT),
    V("Tax Inclusive Line Extension Amount", "cbc:TaxInclusiveLineExtensionAmount", **AMOUNT),
    V("Free of Charge", "cbc:FreeOfChargeIndicator"),
    C("Order Line Reference", "cac:OrderLineReference"),
    C("Despatch Line Reference", "cac:DespatchLineReference"),
    C("Receipt Line Reference", "cac:ReceiptLineReference"),
    *[V("Line ID", "cbc:LineID", within=[ref]) for ref in
      ("Order Line Reference", "Despatch Line Reference", "Receipt Line Reference")],
    V("Sales Order Line ID", "cbc:SalesOrderLineID"),
    V("Line Status", "cbc:LineStatusCode", listURI=True),
    C("Document Reference", "cac:DocumentReference", within=["Despatch Line Reference"]),
    C("Document Reference", "cac:DocumentReference", within=["Receipt Line Reference"]),
    C("Item", "cac:Item"),
    V("Item Description", "cbc:Description"),
    V("Pack Quantity", "cbc:PackQuantity"),
    V("Pack Size", "cbc:PackSizeNumeric"),
    V("Item Name", "cbc:Name"),
    V("Brand Name", "cbc:BrandName"),
    V("Model Name", "cbc:ModelName"),
    C("Buyer's Item Identification", "cac:BuyersItemIdentification"),
    C("Seller's Item Identification", "cac:SellersItemIdentification"),
    C("Manufacturer's Item Identification", "cac:ManufacturersItemIdentification"),
    C("Standard Item Identification", "cac:StandardItemIdentification"),
    C("Item Identification", "."),
    V("Item Identification Value", "cbc:ID"),
    V("Item Identification Scheme", "cbc:ID/@schemeName", **scheme(ITEM_SCHEME_ID, ITEM_SCHEME_AGENCY)),
    V("Item Extended ID", "cbc:ExtendedID"),
    C("Commodity Classification", "cac:CommodityClassification"),
    V("Commodity Code", "cbc:CommodityCode"),
    V("Item Classification Code", "cbc:ItemClassificationCode"),
    C("Item Dimensions", "."),
    *[V(label, "+cac:Dimension/cbc:Measure", units={"to": "@unitCode", "transform": "code", "table": REC20},
        also=[{"to": "+cac:Dimension/cbc:AttributeID", "transform": "constant", "value": attribute}])
      for label, attribute in (("Length/Distance", "Length"), ("Weight", "Weight"), ("Volume", "Volume"))],
    C("Price", "cac:Price"),
    V("Price Amount", "cbc:PriceAmount", **AMOUNT),
    V("Base Quantity", "cbc:BaseQuantity", **QUANTITY),
    V("Price Type", "cbc:PriceTypeCode", listURI=True),
    C("Price Validity Period", "cac:ValidityPeriod"),
]
