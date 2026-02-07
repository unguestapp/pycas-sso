# SPDX-License-Identifier: BSD-3-Clause

"""CAS-related error definitions and exceptions."""

AUTHENTICATION_ERRORS = {
    "INVALID_REQUEST": "Not all of the required request parameters were present.",
    
    "INVALID_TICKET_SPEC": "Failure to meet the requirements of validation specification.",
    
    "UNAUTHORIZED_SERVICE_PROXY": "The service is not authorized to perform proxy authentication.",
    
    "INVALID_PROXY_CALLBACK": "The proxy callback specified is invalid. The credentials \
specified for proxy authentication do not meet the security requirements.",

    "INVALID_TICKET": "The ticket provided was not valid, or the ticket did not come from an \
initial login and renew was set on validation.",

    "INVALID_SERVICE": "The ticket provided was valid, but the service specified did not match \
the service associated with the ticket.",

    "INTERNAL_ERROR": "An internal error occured during ticket validation."
}

class CASServiceAuthenticationFailure(Exception):
    """Exception raised when CAS service authentication fails."""

    def __init__(self, client, code:str, message:str = ""):
        self.client = client
        errmsg = AUTHENTICATION_ERRORS[code] if code in AUTHENTICATION_ERRORS else message
        super(CASServiceAuthenticationFailure, self).__init__(errmsg)



PROXY_ERRORS = {
    "INVALID_REQUEST": "Not all of the required request parameters were present.",

    "UNAUTHORIZED_SERVICE": "Service is unauthorized to perform the proxy request.",

    "INTERNAL_ERROR": "An internal error occured during ticket validation."
}

class CASProxyFailure(Exception):
    """Exception raised when CAS proxy request fails."""

    def __init__(self, client, code:str, message:str = ""):
        self.client = client
        errmsg = PROXY_ERRORS[code] if code in PROXY_ERRORS else message
        super(CASProxyFailure, self).__init__(errmsg)