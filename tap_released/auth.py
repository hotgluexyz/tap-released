"""Released Authentication."""

from __future__ import annotations

from hotglue_singer_sdk.authenticators import BearerTokenAuthenticator

# Released uses a long-lived access_token (no refresh_token flow).
# Auth is applied via BearerTokenAuthenticator in client.py.
__all__ = ["BearerTokenAuthenticator"]
