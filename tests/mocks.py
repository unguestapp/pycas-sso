import pytest

from .fixtures import *

@pytest.fixture
def mock_http_login_success(httpserver, service):
    def _mock():
        httpserver.expect_request("/cas/login", method = "POST").respond_with_data(
            headers = { 'location': service }, status = 302
        )
    return _mock

@pytest.fixture
def mock_http_logout(httpserver):
    def _mock():
        httpserver.expect_request("/cas/logout").respond_with_data()
    return _mock


@pytest.fixture
def mock_http_validate(httpserver, username, service, ticket):
    def _mock():
        httpserver.expect_request("/cas/validate", 
            query_string = { "service": service, "ticket": ticket }
        ).respond_with_data(
            f"yes\n{username}".encode("utf-8")
        )
    return _mock

@pytest.fixture
def mock_http_validate_failed(httpserver):
    def _mock():
        httpserver.expect_request("/cas/validate").respond_with_data(
            f"no".encode("utf-8"), status=401
        )
    return _mock


@pytest.fixture
def mock_http_service_validate(httpserver, service, ticket, pgt, service_validate_response):
    def _mock():
         httpserver.expect_request("/cas/serviceValidate", 
            query_string = {
                "service": service, "ticket": ticket,
                "pgtUrl": pgt, "renew": "true"
            }
        ).respond_with_data(
            service_validate_response, content_type="text/xml"
        )
    return _mock

@pytest.fixture
def mock_http_service_validate_v3(httpserver, service_validate_response):
    def _mock():
         httpserver.expect_request("/cas/p3/serviceValidate").respond_with_data(
            service_validate_response, content_type="text/xml"
        )
    return _mock

@pytest.fixture
def mock_http_service_validate_failed(httpserver, service_validate_failed_response):
    def _mock():
         httpserver.expect_request("/cas/serviceValidate").respond_with_data(
            service_validate_failed_response, content_type="text/xml"
        )
    return _mock


@pytest.fixture
def mock_http_proxy_validate(httpserver, service, ticket, pgt, proxy_validate_response):
    def _mock():
         httpserver.expect_request("/cas/proxyValidate", 
            query_string = {
                "service": service, "ticket": ticket,
                "pgtUrl": pgt, "renew": "true"
            }
        ).respond_with_data(
            proxy_validate_response, content_type="text/xml"
        )
    return _mock

@pytest.fixture
def mock_http_proxy_validate_v3(httpserver, proxy_validate_response):
    def _mock():
         httpserver.expect_request("/cas/p3/proxyValidate").respond_with_data(
            proxy_validate_response, content_type="text/xml"
        )
    return _mock


@pytest.fixture
def mock_http_proxy(httpserver, pgt, target_service, proxy_response):
    def _mock():
         httpserver.expect_request("/cas/proxy", 
            query_string =  { "pgt": pgt, "targetService": target_service }
        ).respond_with_data(
            proxy_response, content_type="text/xml"
        )
    return _mock

@pytest.fixture
def mock_http_proxy_failed(httpserver, proxy_response_failed):
    def _mock():
         httpserver.expect_request("/cas/proxy").respond_with_data(
            proxy_response_failed, content_type="text/xml"
        )
    return _mock


@pytest.fixture
def mock_http_saml_validate(httpserver, saml_validate_response):
    def _mock():
        httpserver.expect_request("/cas/samlValidate", method = "POST").respond_with_data(
            saml_validate_response, content_type="text/xml"
        )
    return _mock