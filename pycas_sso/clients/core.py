# SPDX-License-Identifier: BSD-3-Clause

import logging

from lxml import etree
from urllib.parse import urlencode, urlparse, parse_qs
from datetime import datetime

from ..schemas import CASLoginData, CASServiceValidateData, CASProxyData, CASLogoutData
from ..errors import CASServiceAuthenticationFailure, CASProxyFailure
from ..xml import XML_CAS_NS, XML_SAML_NS, XML_SAML_2_NS

logger = logging.getLogger(__name__)

class CASClientBase:
    """
    Base class for CAS client implementations.
    
    This abstract base class defines the interface for interacting with a CAS server.
    It provides methods for authentication, service validation, proxy handling, and SAML validation.
    Subclasses should implement the HTTP transport layer for specific HTTP libraries (requests, httpx, aiohttp).
    
    The class supports both synchronous and asynchronous operations through corresponding method pairs
    (e.g., `login()` and `alogin()`).
    
    Attributes:
        provider (str): The base URL of the CAS server (e.g., 'https://cas.example.com/cas').
        service_url (str): The service URL registered with the CAS server.
        callback_url (str): The callback URL for login.
        is_async (bool): Flag indicating whether this client is used for async operations.
    
    Example:
        Subclasses should implement HTTP fetching methods and context managers:
        
        >>> class MyCustomClient(CASClientBase):
        ...     def fetch_service_validate(self, ticket, pgt_url=None, renew=False, version=2):
        ...         # Implement HTTP request to serviceValidate provider
        ...         pass

    Usage:
        >>> with CASClient.create(provider, service, callback) as client:
        ...     client.service_validate(ticket)

        >>> # Or in async context:
        ... async with CASClient.create(provider, service, callback, is_async=True) as client:
        ...     await client.aservice_validate(ticket)
    """

    def __init__(self, provider: str, service_url: str, callback_url: str, is_async:bool = False):
        self.provider = provider
        self.service_url = service_url
        self.callback_url = callback_url
        self.is_async = is_async
    
    # -------------

    def __enter__(self) -> 'CASClientBase':
        raise NotImplementedError() # pragma: no cover
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def close(self):
        """
        Close any underlying HTTP connections or sessions.
        Called automatically when used as a context manager.
        """
        raise NotImplementedError() # pragma: no cover


    async def __aenter__(self) -> 'CASClientBase':
        raise NotImplementedError() # pragma: no cover
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.aclose()
    
    async def aclose(self):
        """
        Close any underlying HTTP connections or sessions asynchronously.
        Called automatically when used as an async context manager.
        """
        raise NotImplementedError() # pragma: no cover
    
    # -------------

    def login_form_url(self, gateway: bool = False, renew: bool = False, use_post: bool = False) -> str:
        """
        Construct the URL for the CAS login form.

        Args:
            gateway (bool): If True, adds the 'gateway' parameter to the URL.
            renew (bool): If True, adds the 'renew' parameter to the URL.
            use_post (bool): If True, adds the 'method=POST' parameter to the
                URL.

        Returns:
            str: The constructed login form URL.

        Example:
            >>> with CASClient.create(provider, service) as client:
            ...     login_url = client.login_form_url()
        """
        params = { "service": self.callback_url }
        
        if gateway:
            params["gateway"] = "true"
        if renew:
            params["renew"] = "true"
        if use_post:
            params["method"] = "POST"

        return f"{self.provider}/login?{urlencode(params)}"
    
    def login_url(self, **kwargs):
        """
        Construct the URL for the CAS login provider with optional parameters.

        Args:
            **kwargs: Additional query parameters to include in the URL. Must
                include 'service' parameter.
            
        Returns:
            str: The constructed login URL.
        """
        url = f"{self.provider}/login"
        if len(kwargs) > 0:
            url += f"?{urlencode(kwargs)}"
        return url
    
    def ticket_from_url(self, url:str) -> str:
        """
        Extract the CAS ticket from a given URL.

        Args:
            url (str): The URL containing the CAS ticket as a query parameter.

        Returns:
            str: The extracted CAS ticket, or an empty string if not found.
        """

        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)
        return params['ticket'][0] if 'ticket' in params else ''

    def login(self, username:str, password:str, remember: bool = False,
        warn:bool = False, extra_data: dict|None = None) -> CASLoginData:
        """
        Login to the CAS server with the provided credentials.

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.
            remember (bool): If True, sets the 'remember me' option.
            warn (bool): If True, sets the 'warn' option.
            extra_data (dict|None): Additional form data to include in the login
                request.

        Returns:
            CASLoginData: The result of the login attempt.
        """
        raise NotImplementedError() # pragma: no cover

    async def alogin(self, username:str, password:str, remember: bool = False,
        warn:bool = False, extra_data: dict|None = None) -> CASLoginData:
        """Same as `login()` but for asynchronous operation."""
        raise NotImplementedError() # pragma: no cover
    
    # -------------

    def logout_url(self, **kwargs) -> str:
        """
        Construct the URL for the CAS logout provider with optional parameters.

        Args:
            **kwargs: Additional query parameters to include in the URL. Must
                include 'service' parameter.

        Returns:
            str: The constructed logout URL.
        """
        url = f"{self.provider}/logout"
        if len(kwargs) > 0:
            url += f"?{urlencode(kwargs)}"
        return url

    def logout(self) -> bool:
        """
        Logout from the CAS server.

        Returns:
            bool: True if logout was successful, False otherwise.
        """
        raise NotImplementedError() # pragma: no cover
    
    async def alogout(self) -> bool:
        """Same as `logout()` but for asynchronous operation."""
        raise NotImplementedError() # pragma: no cover
    
    # -------------

    def validate_url(self, **kwargs):
        """
        Construct the URL for the CAS validate provider with optional parameters.

        Args:
            **kwargs: Additional query parameters to include in the URL. Must
                include 'service' and 'ticket' parameters.

        Returns:
            str: The constructed validate URL.
        """
        url = f"{self.provider}/validate"
        if len(kwargs) > 0:
            url += f"?{urlencode(kwargs)}"
        return url

    def fetch_validate(self, ticket:str, renew:bool = False) -> str:
        """
        Fetch validation result for the given ticket. This method is
            only responsible for making the HTTP request. If you want to
            perform full validation, use the `validate()` method.

        Args:
            ticket (str): The CAS ticket to validate.
            renew (bool): If True, adds the 'renew' parameter to the validation request.

        Returns:
            str: The username associated with the validated ticket.

        Raises:
            CASServiceAuthenticationFailure: If ticket validation fails.
        """
        raise NotImplementedError() # pragma: no cover
    
    async def afetch_validate(self, ticket:str, renew:bool = False) -> str:
        """Same as `fetch_validate()` but for asynchronous operation."""
        raise NotImplementedError() # pragma: no cover

    def validate(self, ticket:str, renew:bool = False) -> CASServiceValidateData:
        """
        Validate the given ticket against CAS server and return the validation data.

        Args:
            ticket (str): The CAS ticket to validate.
            renew (bool): If True, adds the 'renew' parameter to the validation request.

        Returns:
            CASServiceValidateData: The result of the ticket validation.

        Raises:
            CASServiceAuthenticationFailure: If ticket validation fails.
        """
        username = self.fetch_validate(ticket, renew)
        return CASServiceValidateData(self, username)
    
    async def avalidate(self, ticket:str, renew:bool = False) -> CASServiceValidateData:
        """Same as `validate()` but for asynchronous operation."""
        username = await self.afetch_validate(ticket, renew)
        return CASServiceValidateData(self, username)
    
    # -------------

    def service_validate_url(self, version = 2, **kwargs):
        """
        Construct the URL for the CAS serviceValidate provider with optional parameters.

        Args:
            version (int): The CAS protocol version (2 or 3).
            **kwargs: Additional query parameters to include in the URL. Must
                include 'service' and 'ticket' parameters.

        Returns:
            str: The constructed serviceValidate URL.
        """
        if version == 3:
            url = f"{self.provider}/p3/serviceValidate"
        else:
            url = f"{self.provider}/serviceValidate"
        if len(kwargs) > 0:
            url += f"?{urlencode(kwargs)}"
        return url

    def fetch_service_validate(self, ticket:str, pgt_url:str|None = None, renew:bool = False,
        version:int = 2) -> bytes:
        """
        Fetch service validation result for the given ticket. This method is
            only responsible for making the HTTP request. If you want to
            perform full service validation, use the `service_validate()` method.

        Args:
            ticket (str): The CAS ticket to validate.
            pgt_url (str|None): Proxy Granting Ticket URL, if applicable.
            renew (bool): If True, adds the 'renew' parameter to the validation request.
            version (int): The CAS protocol version (2 or 3).

        Returns:
            bytes: The raw XML content returned by the CAS server.

        Raises:
            CASServiceAuthenticationFailure: If ticket validation fails.
        """
        raise NotImplementedError() # pragma: no cover
    
    async def afetch_service_validate(self, ticket:str, pgt_url:str|None = None, renew:bool = False,
        version:int = 2) -> bytes:
        """Same as `fetch_service_validate()` but for asynchronous operation."""
        raise NotImplementedError() # pragma: no cover

    def _parse_service_validate_content(self, content:bytes, proxy_validate:bool = False) -> CASServiceValidateData:
        root = etree.fromstring(content)

        # success
        success_el = root.find("cas:authenticationSuccess", namespaces = XML_CAS_NS)
        if success_el is not None:
            # retrieve username
            user_el = success_el.find("cas:user", namespaces = XML_CAS_NS)
            username = user_el.text if user_el is not None else ""

            # retrieve extra attributes
            attrs = None
            attrs_el = success_el.find("cas:attributes", namespaces = XML_CAS_NS)
            if attrs_el is not None:
                attrs = dict()
                for child in attrs_el:
                    name = etree.QName(child).localname
                    if name not in attrs:
                        attrs[name] = list()
                    attrs[name].append(child.text)

                attrs = {
                    k: v[0] if len(v) == 1 else v for k, v in attrs.items()
                }

            # retrieve proxy granting ticket
            pgt_elem = success_el.find("cas:proxyGrantingTicket", namespaces = XML_CAS_NS)
            pgt = pgt_elem.text if pgt_elem is not None else None

            # retrieve proxy
            proxies = None
            if proxy_validate:
                proxies_el = success_el.find("cas:proxies", namespaces = XML_CAS_NS)
                if proxies_el is not None:
                    proxies = list()
                    for child in proxies_el:
                        proxies.append(child.text)

            return CASServiceValidateData(
                self,
                username,
                pgt,
                attrs,
                proxies
            )
        
        # failed
        failure_el = root.find("cas:authenticationFailure", namespaces = XML_CAS_NS)
        if failure_el is not None:
            code = failure_el.get("code")
            message = failure_el.text

            logger.error(f"[pycas-sso][serviceValidate] {code}: {message}")
            raise CASServiceAuthenticationFailure(self, code, message)
        
        raise ValueError("Incorrect XML content for serviceValidate")

    def service_validate(self, ticket:str, pgt_url:str|None = None, 
        renew:bool = False, version:int = 2) -> CASServiceValidateData:
        """
        Validate the given ticket against CAS server and return the validation data.
        
        Args:
            ticket (str): The CAS ticket to validate.
            pgt_url (str|None): Proxy Granting Ticket URL, if applicable.
            renew (bool): If True, adds the 'renew' parameter to the validation request.
            version (int): The CAS protocol version (2 or 3).

        Returns:
            CASServiceValidateData: The result of the ticket validation.

        Raises:
            CASServiceAuthenticationFailure: If ticket validation fails.
        """
        content = self.fetch_service_validate(ticket, pgt_url, renew, version)
        return self._parse_service_validate_content(content)
    
    async def aservice_validate(self, ticket:str, pgt_url:str|None = None, 
        renew:bool = False, version:int = 2) -> CASServiceValidateData:
        """Same as `service_validate()` but for asynchronous operation."""
        content = await self.afetch_service_validate(ticket, pgt_url, renew, version)
        return self._parse_service_validate_content(content)
    
    # -------------

    def proxy_validate_url(self, version = 2, **kwargs):
        """
        Construct the URL for the CAS proxyValidate provider with optional parameters.

        Args:
            version (int): The CAS protocol version (2 or 3).
            **kwargs: Additional query parameters to include in the URL. Must
                include 'service' and 'ticket' parameters.

        Returns:
            str: The constructed proxyValidate URL.
        """
        if version == 3:
            url = f"{self.provider}/p3/proxyValidate"
        else:
            url = f"{self.provider}/proxyValidate"
        if len(kwargs) > 0:
            url += f"?{urlencode(kwargs)}"
        return url

    def fetch_proxy_validate(self, ticket:str, pgt_url:str|None = None, renew:bool = False,
        version:int = 2) -> bytes:
        """
        Fetch proxy validation result for the given ticket. This method is
            only responsible for making the HTTP request. If you want to
            perform full proxy validation, use the `proxy_validate()` method.

        Args:
            ticket (str): The CAS ticket to validate.
            pgt_url (str|None): Proxy Granting Ticket URL, if applicable.
            renew (bool): If True, adds the 'renew' parameter to the validation request.
            version (int): The CAS protocol version (2 or 3).
            Returns:
            bytes: The raw XML content returned by the CAS server.

        Raises:
            CASServiceAuthenticationFailure: If ticket validation fails.
        """
        raise NotImplementedError() # pragma: no cover
    
    async def afetch_proxy_validate(self, ticket:str, pgt_url:str|None = None, renew:bool = False, 
        version:int = 2) -> bytes:
        """Same as `fetch_proxy_validate()` but for asynchronous operation."""
        raise NotImplementedError() # pragma: no cover
    
    def proxy_validate(self, ticket:str, pgt_url:str|None = None, 
        renew:bool = False, version:int = 2) -> CASServiceValidateData:
        """Same as `service_validate()` but it can additionnaly validate proxy tickets."""
        content = self.fetch_proxy_validate(ticket, pgt_url, renew, version)
        return self._parse_service_validate_content(content, proxy_validate = True)
    
    async def aproxy_validate(self, ticket:str, pgt_url:str|None = None, 
        renew:bool = False, version:int = 2) -> CASServiceValidateData:
        """Same as `proxy_validate()` but for asynchronous operation."""
        content = await self.afetch_proxy_validate(ticket, pgt_url, renew, version)
        return self._parse_service_validate_content(content, proxy_validate = True)
    
    # -------------

    def proxy_url(self, **kwargs):
        """
        Construct the URL for the CAS proxy provider with optional parameters.

        Args:
            **kwargs: Additional query parameters to include in the URL. Must
                include 'pgt' and 'targetService' parameters.

        Returns:
            str: The constructed proxy URL.
        """
        url = f"{self.provider}/proxy"
        if len(kwargs) > 0:
            url += f"?{urlencode(kwargs)}"
        return url

    def _parse_proxy_content(self, content:bytes) -> CASProxyData:
        root = etree.fromstring(content)

        # success
        success_el = root.find("cas:proxySuccess", namespaces = XML_CAS_NS)
        if success_el is not None:
            proxy_el = success_el.find("cas:proxyTicket", namespaces = XML_CAS_NS)
            if proxy_el is not None:
                return CASProxyData(
                    self,
                    proxy_el.text
                )
            
        # failure
        failure_el = root.find("cas:proxyFailure", namespaces = XML_CAS_NS)
        if failure_el is not None:
            code = failure_el.get("code")
            message = failure_el.text

            logger.error(f"[pycas-sso][proxy] {code}: {message}")
            raise CASProxyFailure(self, code, message)
            
        raise ValueError("Incorrect XML content for proxy")
    
    def fetch_proxy(self, pgt:str, target_service:str) -> bytes:
        """
        Fetch a proxy ticket using the provided Proxy Granting Ticket (PGT) and target service. 
            This method is only responsible for making the HTTP request. If you want to
            perform full proxy ticket retrieval, use the `proxy()` method.
        """
        raise NotImplementedError() # pragma: no cover
    
    async def afetch_proxy(self, pgt:str, target_service:str) -> bytes:
        """Same as `fetch_proxy()` but for asynchronous operation."""
        raise NotImplementedError() # pragma: no cover
    
    def proxy(self, pgt:str, target_service:str) -> CASProxyData:
        """
        Retrieve a proxy ticket against CAS server for the specified target service 
            using the provided PGT.

        Args:
            pgt (str): The Proxy Granting Ticket.
            target_service (str): The target service for which to obtain the proxy ticket.

        Returns:
            CASProxyData: The result containing the proxy ticket.

        Raises:
            CASProxyFailure: If proxy ticket retrieval fails.
        """
        content = self.fetch_proxy(pgt, target_service)
        return self._parse_proxy_content(content)
    
    async def aproxy(self, pgt:str, target_service:str) -> CASProxyData:
        """Same as `proxy()` but for asynchronous operation."""
        content = await self.afetch_proxy(pgt, target_service)
        return self._parse_proxy_content(content)
    
    # -------------

    @staticmethod
    def parse_logout_request(content:bytes) -> CASLogoutData:
        """
        Parse a SAML logout request XML content and return a CASLogoutData object.

        Args:
            content (bytes): The SAML logout request XML content.

        Returns:
            CASLogoutData: The parsed logout data.
        """
        root = etree.fromstring(content)

        request_id = root.get("ID")
        session_id = root.find(".//samlp:SessionIndex", namespaces = XML_SAML_2_NS).text

        try:
            issued_at = datetime.strptime(
                root.get("IssueInstant"),
                "%Y-%m-%dT%H:%M:%SZ"
            )
        except ValueError:
            issued_at = root.get("IssueInstant")

        return CASLogoutData(request_id, issued_at, session_id)
    
    # -------------

    def saml_validate_url(self, **kwargs):
        """
        Construct the URL for the CAS samlValidate provider with optional parameters.

        Args:
            **kwargs: Additional query parameters to include in the URL. Must
                include 'TARGET' parameter.

        Returns:
            str: The constructed samlValidate URL.
        """
        url = f"{self.provider}/samlValidate"
        if len(kwargs) > 0:
            url += f"?{urlencode(kwargs)}"
        return url

    def _parse_saml_validate_content(self, content:bytes) -> CASServiceValidateData:
        root = etree.fromstring(content)

        status_el = root.find(".//samlp:StatusCode", namespaces = XML_SAML_NS)
        if status_el is not None:
            status_code = status_el.get("Value")[6:]
            if status_code == "Success":
                # retrieve username
                user_el = root.find(".//saml:NameIdentifier", namespaces = XML_SAML_NS)
                username = user_el.text if user_el is not None else ""

                # retrieve attributes
                attrs = dict()
                attrs_all = root.findall(".//saml:Attribute", namespaces = XML_SAML_NS)
                for attr_el in attrs_all:
                    name = attr_el.get("AttributeName")
                    for child in attr_el:
                        if etree.QName(child).localname == "AttributeValue":
                            if name not in attrs:
                                attrs[name] = list()
                            attrs[name].append(child.text)

                attrs = {
                    k: v[0] if len(v) == 1 else v for k, v in attrs.items()
                }

                return CASServiceValidateData(
                    self,
                    username,
                    attrs = attrs
                )
            else:
                message_el = status_el.find("samlp:StatusMessage", namespaces = XML_SAML_NS)
                message = message_el.text if message_el is not None else ""
                raise CASServiceAuthenticationFailure(self, status_code, message)

        raise ValueError("Incorrect XML content for samlValidate")
    
    def fetch_saml_validate(self, ticket:str, request_id:str|None = None, 
        issued_at:datetime|None = None) -> bytes:
        """
        Fetch SAML validation result for the given ticket. This method is
            only responsible for making the HTTP request. If you want to
            perform full SAML validation, use the `saml_validate()` method.
            
        Args:
            ticket (str): The CAS ticket to validate.
            request_id (str|None): Optional request ID for the SAML request.
            issued_at (datetime|None): Optional issue timestamp for the SAML request.

        Returns:
            bytes: The raw XML content returned by the CAS server.
        """
        raise NotImplementedError() # pragma: no cover

    async def afetch_saml_validate(self, ticket:str, request_id:str|None = None, 
        issued_at:datetime|None = None) -> bytes:
        """Same as `fetch_saml_validate()` but for asynchronous operation."""
        raise NotImplementedError() # pragma: no cover
    
    def saml_validate(self, ticket:str, request_id:str|None = None, 
        issued_at:datetime|None = None) -> CASServiceValidateData:
        """
        Validate the given ticket against CAS server using SAML and return the validation data.

        Args:
            ticket (str): The CAS ticket to validate.
            request_id (str|None): Optional request ID for the SAML request.
            issued_at (datetime|None): Optional issue timestamp for the SAML request.
                If not provided, the current time will be used.

        Returns:
            CASServiceValidateData: The result of the ticket validation.

        Raises:
            CASServiceAuthenticationFailure: If ticket validation fails.
        """
        content = self.fetch_saml_validate(ticket, request_id, issued_at)
        return self._parse_saml_validate_content(content)
    
    async def asaml_validate(self, ticket:str, request_id:str|None = None, 
        issued_at:datetime|None = None) -> CASServiceValidateData:
        """Same as `saml_validate()` but for asynchronous operation."""
        content = await self.afetch_saml_validate(ticket, request_id, issued_at)
        return self._parse_saml_validate_content(content)