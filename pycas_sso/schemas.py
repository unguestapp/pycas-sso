from __future__ import annotations

# SPDX-License-Identifier: BSD-3-Clause

""""Data schemas returned after CAS client operations."""

from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .clients.core import CASClientBase


@dataclass
class CASLoginData:
    """Data returned after a login attempt."""

    client: CASClientBase

    success: bool

    http_status: int

    redirect_url: str = ""

    @property
    def ticket(self) -> str:
        return self.client.ticket_from_url(self.redirect_url)
    

@dataclass
class CASServiceValidateData:
    """
    Data returned after a service validation, proxy validation or 
        saml validation attempt.
    """

    client: CASClientBase

    username: str

    proxy_granting_ticket: str|None = None

    attrs: dict|None = None

    proxies: list|None = None
    

@dataclass
class CASProxyData:
    """Data returned after a proxy ticket request."""

    client: CASClientBase

    proxy_ticket:str
    

@dataclass
class CASLogoutData:
    """Data returned after parsing a logout callback content from CAS server."""

    request_id: str

    issued_at: datetime|str

    session_id: str