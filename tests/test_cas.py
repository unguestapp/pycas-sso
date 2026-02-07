import pytest

from urllib.parse import urlencode
from datetime import datetime

from .fixtures import *
from .mocks import *

from pycas_sso.errors import CASServiceAuthenticationFailure, CASProxyFailure
from pycas_sso.schemas import CASLoginData, CASLogoutData

# ===========================
# Testing CASClient factory
# ===========================

def test_cas_client(cas_client):
    with cas_client as client:
        pass

@pytest.mark.asyncio
async def test_async_cas_client(async_cas_client):
    async with async_cas_client as client:
        pass

# ===========================
# Testing *.login_form_url
# ===========================

def test_login_form_url_default(cas_client, provider, callback):
    params = urlencode({ "service": callback })
    assert cas_client.login_form_url() == f"{provider}/login?{params}"

def test_login_form_url_full(cas_client, provider, callback):
    params = urlencode({ 
        "service": callback, "gateway": "true",
        "renew": "true", "method": "POST"
    })
    assert cas_client.login_form_url(True, True, True) == f"{provider}/login?{params}"

# ===========================
# Testing *.login_url
# ===========================

def test_login_url(cas_client, provider, service):
    params = { "service": service }
    assert cas_client.login_url(**params) == f"{provider}/login?{urlencode(params)}"

# ===========================
# Testing *.logout_url
# ===========================

def test_logout_url(cas_client, provider, service):
    params = { "service": service }
    assert cas_client.logout_url(**params) == f"{provider}/logout?{urlencode(params)}"

# ===========================
# Testing *.ticket_from_url
# ===========================

def test_ticket_from_url(cas_client, ticket):
    url = f"http://example.com/?ticket={ticket}"
    assert cas_client.ticket_from_url(url) == ticket

# ===========================
# Testing *.validate_url
# ===========================

def test_validate_url(cas_client, provider, service, ticket):
    params = { "service": service, "ticket": ticket }
    assert cas_client.validate_url(**params) == f"{provider}/validate?{urlencode(params)}"

# ===========================
# Testing 
# *.service_validate_url
# ===========================

def test_service_validate_url(cas_client, provider, service, ticket, pgt_url):
    params = { "service": service, "ticket": ticket, "pgtUrl": pgt_url, "renew": "true" }
    assert cas_client.service_validate_url(**params) == \
f"{provider}/serviceValidate?{urlencode(params)}"

def test_service_validate_url_v3(cas_client, provider, service, ticket, pgt_url):
    params = { "service": service, "ticket": ticket, "pgtUrl": pgt_url, "renew": "true" }
    assert cas_client.service_validate_url(version = 3, **params) == \
f"{provider}/p3/serviceValidate?{urlencode(params)}"
    
# ===========================
# Testing 
# *.proxy_validate_url
# ===========================

def test_proxy_validate_url(cas_client, provider, service, ticket, pgt_url):
    params = { "service": service, "ticket": ticket, "pgtUrl": pgt_url, "renew": "true" }
    assert cas_client.proxy_validate_url(**params) == \
f"{provider}/proxyValidate?{urlencode(params)}"
    
def test_proxy_validate_url_v3(cas_client, provider, service, ticket, pgt_url):
    params = { "service": service, "ticket": ticket, "pgtUrl": pgt_url, "renew": "true" }
    assert cas_client.proxy_validate_url(version = 3, **params) == \
f"{provider}/p3/proxyValidate?{urlencode(params)}"
    
# ===========================
# Testing *.proxy_url
# ===========================

def test_proxy_url(cas_client, provider, pgt, target_service):
    params = { "pgt": pgt, "targetService": target_service }
    assert cas_client.proxy_url(**params) == f"{provider}/proxy?{urlencode(params)}"

# ===========================
# Testing 
# *.ssaml_validate_url
# ===========================

def test_saml_validate_url(cas_client, provider, service, ticket, pgt_url):
    params = { "TARGET": service }
    assert cas_client.saml_validate_url(**params) == f"{provider}/samlValidate?{urlencode(params)}"
    
# ===========================
# Testing 
# *.parse_logout_request
# ===========================

def test_parse_logout_request(cas_client, logoutrequest_xml):
    assert cas_client.parse_logout_request(
        logoutrequest_xml.encode("utf-8")
    ) == CASLogoutData(
        "123456789", 
        datetime.strptime("2025-12-05T09:21:59Z", "%Y-%m-%dT%H:%M:%SZ"),
        "session_id"
    )

# ===========================
# Testing *.login
# ===========================

def test_login(cas_client, mock_http_login_success, username, login_ticket, assert_login_success):
    mock_http_login_success()
    r = cas_client.login(username, '123456789', True, True, { 'lt': login_ticket })
    assert r == assert_login_success(cas_client)

@pytest.mark.asyncio
async def test_alogin(async_cas_client, mock_http_login_success, username, login_ticket, assert_login_success):
    mock_http_login_success()
    r = await async_cas_client.alogin(username, '123456789', True, True, { 'lt': login_ticket })
    assert r == assert_login_success(async_cas_client)

# ===========================
# Testing *.logout
# ===========================

def test_logout(cas_client, mock_http_logout):
    mock_http_logout()
    assert cas_client.logout() == True

@pytest.mark.asyncio
async def test_alogout(async_cas_client, mock_http_logout):
    mock_http_logout()
    assert await async_cas_client.alogout() == True

# ===========================
# Testing *.validate
# ===========================

def test_validate(cas_client, ticket, mock_http_validate, assert_validate_success):
    mock_http_validate()
    r = cas_client.validate(ticket)
    assert r == assert_validate_success(cas_client)

@pytest.mark.asyncio
async def test_avalidate(async_cas_client, ticket, mock_http_validate, assert_validate_success):
    mock_http_validate()
    r = await async_cas_client.avalidate(ticket)
    assert r == assert_validate_success(async_cas_client)

def test_validate_fail(cas_client, ticket, mock_http_validate_failed):
    mock_http_validate_failed()
    with pytest.raises(CASServiceAuthenticationFailure):
        cas_client.validate(ticket)

# ===========================
# Testing *.service_validate
# ===========================

def test_service_validate(cas_client, mock_http_service_validate, ticket, pgt, assert_service_validate_success):
    mock_http_service_validate()
    r = cas_client.service_validate(ticket, pgt, True)
    assert r == assert_service_validate_success(cas_client)

@pytest.mark.asyncio
async def test_aservice_validate(async_cas_client, mock_http_service_validate, ticket, pgt, assert_service_validate_success):
    mock_http_service_validate()
    r = await async_cas_client.aservice_validate(ticket, pgt, True)
    assert r == assert_service_validate_success(async_cas_client)

def test_service_validate_v3(cas_client, mock_http_service_validate_v3, ticket, pgt, assert_service_validate_success):
    mock_http_service_validate_v3()
    r = cas_client.service_validate(ticket, pgt, True, 3)
    assert r == assert_service_validate_success(cas_client)

def test_service_validate_fail(cas_client, mock_http_service_validate_failed, ticket, pgt):
    mock_http_service_validate_failed()
    with pytest.raises(CASServiceAuthenticationFailure):
        cas_client.service_validate(ticket, pgt, True)

# ===========================
# Testing *.proxy_validate
# ===========================

def test_proxy_validate(cas_client, mock_http_proxy_validate, ticket, pgt, assert_proxy_validate_success):
    mock_http_proxy_validate()
    r = cas_client.proxy_validate(ticket, pgt, True)
    assert r == assert_proxy_validate_success(cas_client)

@pytest.mark.asyncio
async def test_aproxy_validate(async_cas_client, mock_http_proxy_validate, ticket, pgt, assert_proxy_validate_success):
    mock_http_proxy_validate()
    r = await async_cas_client.aproxy_validate(ticket, pgt, True)
    assert r == assert_proxy_validate_success(async_cas_client)

def test_proxy_validate_v3(cas_client, mock_http_proxy_validate_v3, ticket, pgt, assert_proxy_validate_success):
    mock_http_proxy_validate_v3()
    r = cas_client.proxy_validate(ticket, pgt, True, 3)
    assert r == assert_proxy_validate_success(cas_client)

# ===========================
# Testing *.proxy
# ===========================

def test_proxy(cas_client, mock_http_proxy, pgt, target_service, assert_proxy_success):
    mock_http_proxy()
    r = cas_client.proxy(pgt, target_service)
    assert r == assert_proxy_success(cas_client)

@pytest.mark.asyncio
async def test_aproxy(async_cas_client, mock_http_proxy, pgt, target_service, assert_proxy_success):
    mock_http_proxy()
    r = await async_cas_client.aproxy(pgt, target_service)
    assert r == assert_proxy_success(async_cas_client)

def test_proxy_fail(cas_client, mock_http_proxy_failed, pgt, target_service):
    mock_http_proxy_failed()
    with pytest.raises(CASProxyFailure):
        cas_client.proxy(pgt, target_service)

# ===========================
# Testing *.saml_validate
# ===========================

def test_saml_validate(cas_client, mock_http_saml_validate, ticket, assert_saml_validate_success):
    mock_http_saml_validate()
    r = cas_client.saml_validate(ticket, '123456789')
    assert r == assert_saml_validate_success(cas_client)

@pytest.mark.asyncio
async def test_asaml_validate(async_cas_client, mock_http_saml_validate, ticket, assert_saml_validate_success):
    mock_http_saml_validate()
    r = await async_cas_client.asaml_validate(ticket, '123456789')
    assert r == assert_saml_validate_success(async_cas_client)