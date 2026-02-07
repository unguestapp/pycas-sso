# PyCAS-SSO - Python CAS client library
# 
# Copyright (C) 2026 CANDIA Nicolas
# 
# This file is part of PyCAS-SSO library.
# 
# PyCAS-SSO is distributed under the BSD 3-Clause "New" or "Revised" License.
# See the accompanying LICENSE file for the full license text.

from importlib.util import find_spec

from .clients.core import CASClientBase

# List of supported HTTP libraries

SUPPORTED_HTTP_LIBS = [ 'httpx', 'requests', 'aiohttp' ]

# ---------------------------

class CASClient:
    """Factory class to create CASClient instances based on available HTTP libraries.
    
    This class provides a factory pattern implementation to instantiate the appropriate
    CASClient subclass based on the specified HTTP library. It automatically detects
    available libraries and creates compatible client instances.
    
    Examples:
        >>> # Auto-detect available HTTP library
        >>> client = CASClient.create(
        ...     'https://cas.example.com',
        ...     'https://myapp.example.com',
        ...     'https://myapp.example.com/login'
        ... )
        
        >>> # Explicitly specify HTTP library
        >>> client = CASClient.create(
        ...     'https://cas.example.com',
        ...     'https://myapp.example.com',
        ...     'https://myapp.example.com/login',
        ...     http_lib='httpx'
        ... )
    """

    @staticmethod
    def create(provider: str, service_url: str, callback_url: str, *args, http_lib: str = 'default', **kwargs) -> CASClientBase:
        """Create and return a CASClient instance using the specified HTTP library.
        
        This factory method automatically detects or uses the specified HTTP library
        to instantiate the appropriate CASClient subclass. If no suitable library is
        found, a ValueError is raised.
        
        Args:
            provider (str): The CAS server provider URL.
                Example: 'https://cas.example.com'
            service_url (str): The service URL to validate against the CAS server.
                Example: 'https://myapp.example.com'
            callback_url (str): The callback URL for login.
                Example: 'https://myapp.example.com/login'
            *args: Positional arguments to pass to the CASClient subclass constructor.
            http_lib (str, optional): The HTTP library to use for requests.
                Defaults to 'default' (auto-detect).
                Supported values: 'default', 'httpx', 'requests', 'aiohttp'
            **kwargs: Keyword arguments to pass to the CASClient subclass constructor.
        
        Returns:
            CASClient: An instance inheriting from CASClientBase.
        
        Raises:
            ValueError: If no supported HTTP library is installed or if http_lib
                contains an unsupported value.
        
        Examples:
            >>> # Auto-detect available library
            >>> client = CASClient.create(
            ...     'https://cas.example.com',
            ...     'https://myapp.example.com',
            ...     'https://myapp.example.com/login'
            ... )
            
            >>> # Use specific library
            >>> client = CASClient.create(
            ...     'https://cas.example.com',
            ...     'https://myapp.example.com',
            ...     'https://myapp.example.com/login',
            ...     http_lib='requests'
            ... )
            
            >>> # With additional arguments
            >>> client = CASClient.create(
            ...     'https://cas.example.com',
            ...     'https://myapp.example.com',
            ...     'https://myapp.example.com/login',
            ...     http_lib='httpx',
            ...     timeout=30
            ... )
        """
        
        if http_lib == 'default':
            for lib in SUPPORTED_HTTP_LIBS:
                if find_spec(lib):
                    http_lib = lib
                    break
            if http_lib == 'default':
                raise ValueError(f"No supported HTTP library installed. \
                    Please install one of these following libraries: {','.join(SUPPORTED_HTTP_LIBS)}.")

        if http_lib == 'httpx':
            from .clients.httpx import CASClient_Httpx
            return CASClient_Httpx(provider, service_url, callback_url, *args, **kwargs)
        elif http_lib == 'requests':
            from .clients.requests import CASClient_Requests
            return CASClient_Requests(provider, service_url, callback_url, *args, **kwargs)
        elif http_lib == 'aiohttp':
            from .clients.aiohttp import CASClient_AIOHttp
            return CASClient_AIOHttp(provider, service_url, callback_url, *args, **kwargs)
        
        raise ValueError(f"Incorrect http_lib value. Use `default` or one of these: {','.join(SUPPORTED_HTTP_LIBS)}.")