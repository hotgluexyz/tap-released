"""HTTP API client (REST or GraphQL), including ReleasedStream base class."""

from __future__ import annotations

from functools import cached_property
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests
from hotglue_singer_sdk.authenticators import BearerTokenAuthenticator
from hotglue_singer_sdk.helpers.jsonpath import extract_jsonpath
from hotglue_singer_sdk.streams import RESTStream
from typing_extensions import override


class ReleasedStream(RESTStream):
    """Released stream class."""

    # Most Released list endpoints nest records under ``Data``.
    records_jsonpath = "$.Data[*]"

    # Cursor pagination: ``MetaData.NextPageUrl`` (e.g. ``api/invoices?fromId=...``).
    next_page_token_jsonpath = "$.MetaData.NextPageUrl"

    # When set, keep only records whose value at this path equals config ``company_id``.
    company_id_jsonpath: str | None = None

    @override
    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via the ``api_url`` tap setting."""
        return "https://api.re-leased.com/api"

    @override
    @cached_property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a Bearer token authenticator using ``access_token`` from config."""
        return BearerTokenAuthenticator.create_for_stream(
            self,
            token=self.config["access_token"],
        )

    @override
    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        return {}

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Any | None,
    ) -> Any | None:
        """Return ``MetaData.NextPageUrl`` or None when there is no next page."""
        if self.next_page_token_jsonpath:
            all_matches = extract_jsonpath(
                self.next_page_token_jsonpath, response.json()
            )
            return next(iter(all_matches), None)

        return None

    @override
    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return URL query params, including ``fromId`` from ``NextPageUrl``."""
        params: dict[str, Any] = {}
        if next_page_token:
            from_id = parse_qs(urlparse(str(next_page_token)).query).get(
                "fromId", [None]
            )[0]
            if from_id:
                params["fromId"] = from_id
        if self.replication_key:
            starting = self.get_starting_timestamp(context)
            if starting:
                params["updatedAfterDate"] = starting.strftime("%Y-%m-%dT%H:%M:%S")
        return params

    @override
    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        """Drop records that do not belong to the configured ``company_id``."""
        if self.company_id_jsonpath:
            match = next(
                extract_jsonpath(self.company_id_jsonpath, row),
                None,
            )
            if match != self.config["company_id"]:
                return None
        return row
