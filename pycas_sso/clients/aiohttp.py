# SPDX-License-Identifier: BSD-3-Clause

import logging
import aiohttp

from datetime import datetime
from uuid import uuid4

from .core import CASClientBase
from ..errors import CASServiceAuthenticationFailure
from ..schemas import CASLoginData
from ..xml import XML_SAML_VALIDATE_TEMPLATE

logger = logging.getLogger(__name__)

class CASClient_AIOHttp(CASClientBase):
    """
    CASClient implementation using the aiohttp library.
    
    Note:
        Only asynchronous operations are supported by aiohttp library.
    """

    def __init__(self, provider: str, service_url: str, callback_url: str, is_async:bool = True, **kwargs):
        super(CASClient_AIOHttp, self).__init__(provider, service_url, callback_url, is_async = True)
        self.http = aiohttp.ClientSession(**kwargs)

    # -------------
    
    async def __aenter__(self) -> 'CASClient_AIOHttp':
        return self
    
    async def aclose(self):
        await self.http.close()

    # -------------

    async def alogin(self, username:str, password:str, remember: bool = False,
        warn:bool = False, extra_data: dict|None = None) -> CASLoginData:

        data = {
            "service": self.service_url, "username": username, "password": password,
            "remember": remember, "warn": warn
        }
        if extra_data is not None:
            data = {**data, **extra_data}

        async with self.http.post(self.login_url(), data = data, params = { "service": self.service_url }, allow_redirects = False) as rq:
            logger.debug(f"[pycas-sso][login] {rq.status} - {rq.url}")

            return CASLoginData(
                self,
                rq.status in [200, 201, 302],
                rq.status,
                rq.headers['location'] if 'location' in rq.headers else ""
            )
    
    # -------------
    
    async def alogout(self) -> bool:
        async with self.http.get(self.logout_url(), params = { "service": self.service_url }) as rq:
            logger.debug(f"[pycas-sso][logout] {rq.status} - {rq.url}")
            return rq.status in [ 200, 201 ]
    
    # -------------
    
    async def afetch_validate(self, ticket:str, renew:bool = False) -> str:
        params = { "service": self.service_url, "ticket": ticket }
        if renew:
            params["renew"] = "true"

        async with self.http.get(self.validate_url(), params = params) as rq:
            logger.debug(f"[pycas-sso][validate] {rq.status} - {rq.url}")

            status = (await rq.content.readline()).decode("utf-8").strip()
            if status == "yes":
                try:
                    username = ((await rq.content.readline()).decode("utf-8")).strip()
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

    async def afetch_service_validate(self, ticket:str, pgt_url:str|None = None, renew:bool = False, version:int = 2) -> bytes:
        params = self._service_validate_params(ticket, pgt_url, renew)
        async with self.http.get(self.service_validate_url(version), params = params) as rq:
            logger.debug(f"[pycas-sso][serviceValidate] {rq.status} - {rq.url}")
            return await rq.read()
    
    # -------------

    async def afetch_proxy_validate(self, ticket:str, pgt_url:str|None = None, renew:bool = False, version:int = 2) -> bytes:
        params = self._service_validate_params(ticket, pgt_url, renew)
        async with self.http.get(self.proxy_validate_url(version), params = params) as rq:
            logger.debug(f"[pycas-sso][proxyValidate] {rq.status} - {rq.url}")
            return await rq.read()
    
    # -------------
    
    async def afetch_proxy(self, pgt:str, target_service:str) -> bytes:
        params = { "pgt": pgt, "targetService": target_service }
        async with self.http.get(self.proxy_url(), params = params) as rq:
            logger.debug(f"[pycas-sso][proxy] {rq.status} - {rq.url}")
            return await rq.read()
    
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
        
    async def afetch_saml_validate(self, ticket:str, request_id:str|None = None, 
        issued_at:datetime|None = None) -> bytes:
        params = self._saml_validate_params()
        content = self._saml_validate_content(ticket, request_id, issued_at)
        async with self.http.post(
            self.saml_validate_url(),
            params = params,
            data = content,
            headers = CASClient_AIOHttp._SAML_VALIDATE_HEADERS
        ) as rq:
            logger.debug(f"[pycas-sso][samlValidate] {rq.status} - {rq.url}")
            return await rq.read()