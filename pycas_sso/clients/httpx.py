# SPDX-License-Identifier: BSD-3-Clause

import logging
import httpx

from datetime import datetime
from uuid import uuid4

from .core import CASClientBase
from ..errors import CASServiceAuthenticationFailure
from ..schemas import CASLoginData
from ..xml import XML_SAML_VALIDATE_TEMPLATE

logger = logging.getLogger(__name__)

class CASClient_Httpx(CASClientBase):
    """CASClient implementation using the httpx library."""

    def __init__(self, provider: str, service_url: str, callback_url: str, is_async:bool = False, **kwargs):
        super(CASClient_Httpx, self).__init__(provider, service_url, callback_url, is_async)
        self.http = httpx.AsyncClient(**kwargs) if self.is_async else httpx.Client(**kwargs)

    # -------------

    def __enter__(self) -> 'CASClient_Httpx':
        if self.is_async:
            raise Exception("You can't use `with` statement with async client. Use `async with` instead.") 
        return self
    
    def close(self):
        self.http.close()

    
    async def __aenter__(self) -> 'CASClient_Httpx':
        if self.is_async is False:
            raise Exception("You can't use `async with` statement with sync client. Use `with` instead.")
        return self
    
    async def aclose(self):
        await self.http.aclose()

    # -------------

    def _get_login_data(self, username:str, password:str, remember: bool = False,
        warn:bool = False, extra_data: dict|None = None) -> dict:

        data = {
            "service": self.service_url, "username": username, "password": password,
            "remember": remember, "warn": warn
        }

        if extra_data is not None:
            data = {**data, **extra_data}

        return data

    def login(self, username:str, password:str, remember: bool = False,
        warn:bool = False, extra_data: dict|None = None) -> CASLoginData:

        data = self._get_login_data(username, password, remember, warn, extra_data)
        rq = self.http.post(self.login_url(), data = data, params = { "service": self.service_url })

        logger.debug(f"[pycas-sso][login] {rq.status_code} - {rq.url}")

        return CASLoginData(
            self,
            rq.status_code in [200, 201, 302],
            rq.status_code,
            rq.headers['location'] if rq.is_redirect else ""
        )

    async def alogin(self, username:str, password:str, remember: bool = False,
        warn:bool = False, extra_data: dict|None = None) -> CASLoginData:

        data = self._get_login_data(username, password, remember, warn, extra_data)
        rq = await self.http.post(self.login_url(), data = data, params = { "service": self.service_url })

        logger.debug(f"[pycas-sso][login] {rq.status_code} - {rq.url}")

        return CASLoginData(
            self,
            rq.status_code in [200, 201, 302],
            rq.status_code,
            rq.headers['location'] if rq.is_redirect else ""
        )
    
    # -------------

    def logout(self) -> bool:
        rq = self.http.get(self.logout_url(), params = { "service": self.service_url })
        logger.debug(f"[pycas-sso][logout] {rq.status_code} - {rq.url}")
        return rq.status_code in [ 200, 201 ]
    
    async def alogout(self) -> bool:
        rq = await self.http.get(self.logout_url(), params = { "service": self.service_url })
        logger.debug(f"[pycas-sso][logout] {rq.status_code} - {rq.url}")
        return rq.status_code in [ 200, 201 ]
    
    # -------------

    def _validate_params(self, ticket:str, renew:bool = False) -> dict:
        params = { "service": self.service_url, "ticket": ticket }
        if renew:
            params["renew"] = "true"
        return params

    def fetch_validate(self, ticket:str, renew:bool = False) -> str:
        params = self._validate_params(ticket, renew)

        with self.http.stream("GET", self.validate_url(), params = params) as stream:
            logger.debug(f"[pycas-sso][validate] {stream.status_code} - {stream.url}")

            it = stream.iter_lines()
            if next(it) == "yes":
                try:
                    username = next(it).strip()
                except:
                    username = ""
                return username
            
        raise CASServiceAuthenticationFailure(self, "VALIDATE_FAILED", "Ticket validation failed.")
    
    async def afetch_validate(self, ticket:str, renew:bool = False) -> str:
        params = self._validate_params(ticket, renew)

        async with self.http.stream("GET", self.validate_url(), params = params) as stream:
            logger.debug(f"[pycas-sso][validate] {stream.status_code} - {stream.url}")

            it = stream.aiter_lines()
            if await anext(it) == "yes":
                try:
                    username = (await anext(it)).strip()
                except:
                    username = ""
                return username
            
        raise CASServiceAuthenticationFailure(self, "VALIDATE_FAILED", "Ticket validation failed.")

    # -------------

    def _service_validate_params(self, ticket:str, pgt_url:str|None = None, renew:bool = False) -> dict:
        params = { "service": self.service_url, "ticket": ticket }
        if pgt_url is not None:
            params["pgtUrl"] = pgt_url
        if renew:
            params["renew"] = "true"
        return params

    def fetch_service_validate(self, ticket:str, pgt_url:str|None = None, renew:bool = False, version:int = 2) -> bytes:
        params = self._service_validate_params(ticket, pgt_url, renew)
        rq = self.http.get(self.service_validate_url(version), params = params)
        logger.debug(f"[pycas-sso][serviceValidate] {rq.status_code} - {rq.url}")
        return rq.content

    async def afetch_service_validate(self, ticket:str, pgt_url:str|None = None, renew:bool = False, version:int = 2) -> bytes:
        params = self._service_validate_params(ticket, pgt_url, renew)
        rq = await self.http.get(self.service_validate_url(version), params = params)
        logger.debug(f"[pycas-sso][serviceValidate] {rq.status_code} - {rq.url}")
        return rq.content
    
    # -------------
    
    def fetch_proxy_validate(self, ticket:str, pgt_url:str|None = None, renew:bool = False, version:int = 2) -> bytes:
        params = self._service_validate_params(ticket, pgt_url, renew)
        rq = self.http.get(self.proxy_validate_url(version), params = params)
        logger.debug(f"[pycas-sso][proxyValidate] {rq.status_code} - {rq.url}")
        return rq.content

    async def afetch_proxy_validate(self, ticket:str, pgt_url:str|None = None, renew:bool = False, version:int = 2) -> bytes:
        params = self._service_validate_params(ticket, pgt_url, renew)
        rq = await self.http.get(self.proxy_validate_url(version), params = params)
        logger.debug(f"[pycas-sso][proxyValidate] {rq.status_code} - {rq.url}")
        return rq.content
    
    # -------------

    def _proxy_params(self, pgt:str, target_service:str) -> dict:
        return { "pgt": pgt, "targetService": target_service }

    def fetch_proxy(self, pgt:str, target_service:str) -> bytes:
        params = self._proxy_params(pgt, target_service)
        rq = self.http.get(self.proxy_url(), params = params)
        logger.debug(f"[pycas-sso][proxy] {rq.status_code} - {rq.url}")
        return rq.content
    
    async def afetch_proxy(self, pgt:str, target_service:str) -> bytes:
        params = self._proxy_params(pgt, target_service)
        rq = await self.http.get(self.proxy_url(), params = params)
        logger.debug(f"[pycas-sso][proxy] {rq.status_code} - {rq.url}")
        return rq.content
    
    # -------------

    _SAML_VALIDATE_HEADERS = {
        'soapaction': 'http://www.oasis-open.org/committees/security',
        'content-type': 'text/xml; charset=utf-8',
        'accept': 'text/xml',
    }

    def _saml_validate_content(self, ticket:str, request_id:str|None = None, issued_at:datetime|None = None) -> bytes:
        if request_id is None:
            request_id = uuid4()

        issued_at_str = issued_at.isoformat() \
            if issued_at is not None else datetime.now().isoformat()
        
        return XML_SAML_VALIDATE_TEMPLATE.format(
            request_id = request_id,
            issued_at = issued_at_str,
            ticket = ticket
        ).encode('utf-8')
    
    def _saml_validate_params(self):
        return { "TARGET": self.service_url }

    def fetch_saml_validate(self, ticket:str, request_id:str|None = None, 
        issued_at:datetime|None = None) -> bytes:
        params = self._saml_validate_params()
        content = self._saml_validate_content(ticket, request_id, issued_at)
        rq = self.http.post(
            self.saml_validate_url(),
            params = params,
            content = content,
            headers = CASClient_Httpx._SAML_VALIDATE_HEADERS
        )
        logger.debug(f"[pycas-sso][samlValidate] {rq.status_code} - {rq.url}")
        return rq.content
        
    async def afetch_saml_validate(self, ticket:str, request_id:str|None = None, 
        issued_at:datetime|None = None) -> bytes:
        params = self._saml_validate_params()
        content = self._saml_validate_content(ticket, request_id, issued_at)
        rq = await self.http.post(
            self.saml_validate_url(),
            params = params,
            content = content,
            headers = CASClient_Httpx._SAML_VALIDATE_HEADERS
        )
        logger.debug(f"[pycas-sso][samlValidate] {rq.status_code} - {rq.url}")
        return rq.content