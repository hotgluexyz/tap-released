"""Released tap class."""

from __future__ import annotations

from hotglue_singer_sdk import Stream, Tap
from hotglue_singer_sdk import typing as th  # JSON schema typing helpers
from typing_extensions import override

from tap_released.streams import (
    CompaniesStream,
    ContactsStream,
    CreditNotesStream,
    InvoicesStream,
    PaymentsStream,
)

STREAM_TYPES = [
    CompaniesStream,
    ContactsStream,
    CreditNotesStream,
    InvoicesStream,
    PaymentsStream,
]


class TapReleased(Tap):
    """Singer tap for Released."""

    name = "tap-released"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
            default="2000-01-01T00:00:00Z",
        ),
        th.Property(
            "access_token",
            th.StringType,
            required=True,
            description="Long-lived Bearer access token for the Released API",
        ),
        th.Property(
            "company_id",
            th.StringType,
            required=True,
            description="Company ID to sync; only records for this company are emitted",
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapReleased.cli()
