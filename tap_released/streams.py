"""Stream type classes for tap-released."""

from __future__ import annotations

from typing import Any, ClassVar

from hotglue_singer_sdk import typing as th  # JSON Schema typing helpers
from typing_extensions import override

from tap_released.client import ReleasedStream

_ADDRESS = th.ObjectType(
    th.Property("StreetAddress", th.StringType),
    th.Property("Suburb", th.StringType),
    th.Property("TownCity", th.StringType),
    th.Property("Region", th.StringType),
    th.Property("PostCode", th.StringType),
    th.Property("CountryCode", th.StringType),
    th.Property("CountryName", th.StringType),
)

_PERSON = th.ObjectType(
    th.Property("Id", th.StringType),
    th.Property("Name", th.StringType),
    th.Property("FirstName", th.StringType),
    th.Property("LastName", th.StringType),
    th.Property("EmailAddress", th.StringType),
)

_TENANCY = th.ObjectType(
    th.Property("Id", th.StringType),
    th.Property("Title", th.StringType),
    th.Property("PropertyId", th.StringType),
    th.Property("DatePaidTo", th.DateTimeType),
)

_LINE_ITEM = th.ObjectType(
    th.Property("Id", th.StringType),
    th.Property("Description", th.StringType),
    th.Property("Quantity", th.NumberType),
    th.Property("UnitAmount", th.NumberType),
    th.Property("TaxAmount", th.NumberType),
    th.Property("TaxType", th.StringType),
    th.Property("AccountCode", th.StringType),
    th.Property("Tracking", th.ArrayType(th.ObjectType())),
)

_ATTACHMENT = th.ObjectType(
    th.Property("Id", th.StringType),
    th.Property("Name", th.StringType),
    th.Property("FileSize", th.IntegerType),
    th.Property("DownloadLink", th.StringType),
    th.Property("MimeType", th.StringType),
)

_PROPERTY = th.ObjectType(
    th.Property("Id", th.StringType),
    th.Property("Name", th.StringType),
    th.Property("Type", th.StringType),
    th.Property("Address", th.StringType),
    th.Property("Tenancy", _TENANCY),
    th.Property("PropertyManager", _PERSON),
    th.Property("PropertyOwner", _PERSON),
)


class InvoicesStream(ReleasedStream):
    """Stream for ``invoices``."""

    name = "invoices"
    path = "/invoices"
    primary_keys: ClassVar[list[str]] = ["Id"]
    replication_key = "UpdatedDate"
    company_id_jsonpath = "$.Company.Id"

    schema = th.PropertiesList(
        th.Property("Id", th.StringType, description="Invoice ID"),
        th.Property("DisplayId", th.StringType),
        th.Property("Reference", th.StringType),
        th.Property("Contact", _PERSON),
        th.Property(
            "Company",
            th.ObjectType(
                th.Property("Id", th.StringType),
                th.Property("Name", th.StringType),
            ),
        ),
        th.Property("Property", _PROPERTY),
        th.Property("Type", th.StringType),
        th.Property("IssueDate", th.DateTimeType),
        th.Property("DueDate", th.DateTimeType),
        th.Property("ServiceDate", th.DateTimeType),
        th.Property("RentPeriodFromDate", th.DateTimeType),
        th.Property("RentPeriodToDate", th.DateTimeType),
        th.Property("OutgoingsPeriodFromDate", th.DateTimeType),
        th.Property("OutgoingsPeriodToDate", th.DateTimeType),
        th.Property("LineAmountTypes", th.StringType),
        th.Property("Status", th.StringType),
        th.Property("CreatedDate", th.DateTimeType),
        th.Property(
            "UpdatedDate",
            th.DateTimeType,
            description="Last update timestamp (replication key)",
        ),
        th.Property("AmountDue", th.NumberType),
        th.Property("AmountPaid", th.NumberType),
        th.Property("SubTotal", th.NumberType),
        th.Property("TotalTax", th.NumberType),
        th.Property("Total", th.NumberType),
        th.Property("LineItems", th.ArrayType(_LINE_ITEM)),
        th.Property("Payments", th.ArrayType(th.ObjectType())),
        th.Property("Attachments", th.ArrayType(_ATTACHMENT)),
    ).to_dict()


class CreditNotesStream(ReleasedStream):
    """Stream for ``credit_notes``."""

    name = "credit_notes"
    path = "/credit-notes"
    primary_keys: ClassVar[list[str]] = ["Id"]
    replication_key = "UpdatedDate"

    schema = th.PropertiesList(
        th.Property("Id", th.StringType, description="Credit note ID"),
        th.Property("DisplayId", th.StringType),
        th.Property("Reference", th.StringType),
        th.Property("Contact", _PERSON),
        th.Property("Property", _PROPERTY),
        th.Property("Type", th.StringType),
        th.Property("Date", th.DateTimeType),
        th.Property("IssueDate", th.DateTimeType),
        th.Property("LineAmountTypes", th.StringType),
        th.Property("Status", th.StringType),
        th.Property(
            "UpdatedDate",
            th.DateTimeType,
            description="Last update timestamp (replication key)",
        ),
        th.Property("RemainingCredit", th.NumberType),
        th.Property("SubTotal", th.NumberType),
        th.Property("TotalTax", th.NumberType),
        th.Property("Total", th.NumberType),
        th.Property("LineItems", th.ArrayType(_LINE_ITEM)),
        th.Property("Allocations", th.ArrayType(th.ObjectType())),
    ).to_dict()


class CompaniesStream(ReleasedStream):
    """Stream for ``companies`` (parent of contacts)."""

    name = "companies"
    path = "/companies"
    primary_keys: ClassVar[list[str]] = ["Id"]
    replication_key = None
    company_id_jsonpath = "$.Id"

    schema = th.PropertiesList(
        th.Property("Id", th.StringType, description="Company ID"),
        th.Property("Name", th.StringType, description="Company name"),
        th.Property("TimeZone", th.StringType, description="Company time zone"),
        th.Property("Culture", th.StringType, description="Company culture / locale"),
    ).to_dict()

    def get_child_context(self, record: dict, context: dict | None) -> dict[str, Any]:
        """Pass company id to child streams (e.g. contacts)."""
        return {
            "company_id": record["Id"],
        }


class ContactsStream(ReleasedStream):
    """Stream for ``contacts`` (child of companies)."""

    name = "contacts"
    path = "/contacts"
    primary_keys: ClassVar[list[str]] = ["Id"]
    replication_key = "UpdatedDateTime"
    parent_stream_type = CompaniesStream
    ignore_parent_replication_key = True

    schema = th.PropertiesList(
        th.Property(
            "company_id",
            th.StringType,
            description="Parent company ID from context",
        ),
        th.Property("Id", th.StringType, description="Contact ID"),
        th.Property(
            "CompanyMaps",
            th.ArrayType(th.ObjectType()),
            description="Company mappings for this contact",
        ),
        th.Property("Name", th.StringType),
        th.Property("CorrespondenceName", th.StringType),
        th.Property("FirstName", th.StringType),
        th.Property("LastName", th.StringType),
        th.Property("Email", th.StringType),
        th.Property(
            "UpdatedDateTime",
            th.DateTimeType,
            description="Last update timestamp (replication key)",
        ),
        th.Property("Category", th.StringType),
        th.Property("Status", th.StringType),
        th.Property("FaxPhone", th.ObjectType()),
        th.Property("MobilePhone", th.ObjectType()),
        th.Property("DirectDialPhone", th.ObjectType()),
        th.Property("TelephoneNumber", th.ObjectType()),
        th.Property("PhysicalAddress", _ADDRESS),
        th.Property("PostalAddress", _ADDRESS),
        th.Property("TaxBusinessNumber", th.StringType),
        th.Property("TaxNumber", th.StringType),
    ).to_dict()

    @override
    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Pass companyId plus shared updatedAfterDate from the base client."""
        params = super().get_url_params(context, next_page_token)
        params["companyId"] = self.config["company_id"]
        return params
