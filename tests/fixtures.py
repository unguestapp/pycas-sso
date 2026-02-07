import pytest

from pycas_sso.cas import CASClient
from pycas_sso.schemas import CASLoginData, CASServiceValidateData, CASProxyData

# ===========================
# Parametrized fixtures for
# testing all http libs.
# ===========================

CAS_CLIENTS = [ "httpx", "requests" ]

@pytest.fixture(params = CAS_CLIENTS)
def cas_client(request, provider, service, callback):
    client = CASClient.create(
        provider, service, callback, http_lib = request.param
    )
    yield client
    client.close()


ASYNC_CAS_CLIENTS = [ "httpx", "aiohttp" ]

@pytest.fixture(params = ASYNC_CAS_CLIENTS)
async def async_cas_client(request, provider, service, callback):
    client = CASClient.create(
        provider, service, callback, http_lib = request.param, is_async = True
    )
    yield client
    await client.aclose()

# ---

@pytest.fixture
def provider(httpserver):
    return httpserver.url_for("/cas")

@pytest.fixture
def service():
    return "https://service.example.com/"

@pytest.fixture
def callback():
    return "https://service.example.com/login"

@pytest.fixture
def ticket():
    return "ST-123456-789"

@pytest.fixture
def login_ticket():
    return "LT-123456-789"

@pytest.fixture
def username():
    return "johndoe"

@pytest.fixture
def pgt():
    return "PGTIOU-12345-789"

@pytest.fixture
def pgt_url():
    return "https://proxy.example.com"

@pytest.fixture
def proxy_ticket():
    return "PT-123456-789"

@pytest.fixture
def target_service():
    return "https://target.example.com"

# ---

@pytest.fixture
def assert_login_success(service):
    def _factory(client):
        return CASLoginData(
            client, True, 302, service
        )
    return _factory

@pytest.fixture
def assert_validate_success(username):
    def _factory(client):
        return CASServiceValidateData(client, username)
    return _factory

@pytest.fixture
def assert_service_validate_success(username, pgt):
    def _factory(client):
        return CASServiceValidateData(client, username, pgt, {
            "cn": username, "memberOf": [ "person", "user" ]
        }
    )
    return _factory

@pytest.fixture
def assert_proxy_validate_success(username, pgt):
    def _factory(client):
        return CASServiceValidateData(client, username,pgt,
            proxies = [
                "https://proxy1.example.com/",
                "https://proxy2.example.com/"
            ]
        )
    return _factory

@pytest.fixture
def assert_proxy_success(proxy_ticket):
    def _factory(client):
        return CASProxyData(client, proxy_ticket)
    return _factory

@pytest.fixture
def assert_saml_validate_success(username):
    def _factory(client):
        return CASServiceValidateData(
            client, username,
            attrs = { "cn": username, "memberOf": [ "person", "user" ] }
        )
    return _factory

# ---

@pytest.fixture
def logoutrequest_xml():
    return """<samlp:LogoutRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
        ID="123456789" Version="2.0" IssueInstant="2025-12-05T09:21:59Z">
    <saml:NameID xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"></saml:NameID>
    <samlp:SessionIndex>session_id</samlp:SessionIndex>
</samlp:LogoutRequest>"""

@pytest.fixture
def service_validate_response(username, pgt):
    return f"""<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
    <cas:authenticationSuccess>
        <cas:user>{username}</cas:user>
        <cas:attributes>
            <cas:cn>{username}</cas:cn>
            <cas:memberOf>person</cas:memberOf>
            <cas:memberOf>user</cas:memberOf>
        </cas:attributes>
        <cas:proxyGrantingTicket>{pgt}</cas:proxyGrantingTicket>
    </cas:authenticationSuccess>
</cas:serviceResponse>"""

@pytest.fixture
def service_validate_failed_response():
    return """<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
    <cas:authenticationFailure code="INVALID_TICKET">
        Ticket ... not recognized
    </cas:authenticationFailure>
</cas:serviceResponse>
"""

@pytest.fixture
def proxy_validate_response(username, pgt):
    return f"""<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
    <cas:authenticationSuccess>
        <cas:user>{username}</cas:user>
        <cas:proxyGrantingTicket>{pgt}</cas:proxyGrantingTicket>
        <cas:proxies>
            <cas:proxy>https://proxy1.example.com/</cas:proxy>
            <cas:proxy>https://proxy2.example.com/</cas:proxy>
        </cas:proxies>
    </cas:authenticationSuccess>
</cas:serviceResponse>"""

@pytest.fixture
def proxy_response(proxy_ticket):
    return f"""<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
    <cas:proxySuccess>
        <cas:proxyTicket>{proxy_ticket}</cas:proxyTicket>
    </cas:proxySuccess>
</cas:serviceResponse>"""

@pytest.fixture
def proxy_response_failed():
    return """<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
    <cas:proxyFailure code="INVALID_REQUEST">
        'pgt' and 'targetService' parameters are both required
    </cas:proxyFailure>
</cas:serviceResponse>"""

@pytest.fixture
def saml_validate_response(username):
    return f"""<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
    <SOAP-ENV:Header />
    <SOAP-ENV:Body>
        <Response xmlns="urn:oasis:names:tc:SAML:1.0:protocol" xmlns:saml="urn:oasis:names:tc:SAML:1.0:assertion"
            xmlns:samlp="urn:oasis:names:tc:SAML:1.0:protocol" xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" IssueInstant="2025-12-10T14:12:14.817Z"
            MajorVersion="1" MinorVersion="1" Recipient="https://eiger.iad.vt.edu/dat/home.do"
            ResponseID="_5c94b5431c540365e5a70b2874b75996">
            <Status>
                <StatusCode Value="samlp:Success" />
            </Status>
            <Assertion
                xmlns="urn:oasis:names:tc:SAML:1.0:assertion" AssertionID="_e5c23ff7a3889e12fa01802a47331653"
                IssueInstant="2025-12-10T14:12:14.817Z" Issuer="localhost" MajorVersion="1" MinorVersion="1">
                <Conditions
                    NotBefore="2025-12-10T14:12:14.817Z"
                    NotOnOrAfter="2025-12-10T14:12:44.817Z">
                    <AudienceRestrictionCondition>
                        <Audience>
                            https://some-service.example.com/app/
                        </Audience>
                    </AudienceRestrictionCondition>
                </Conditions>
                <AttributeStatement>
                    <Subject>
                        <NameIdentifier>{username}</NameIdentifier>
                        <SubjectConfirmation>
                            <ConfirmationMethod>
                                urn:oasis:names:tc:SAML:1.0:cm:artifact
                            </ConfirmationMethod>
                        </SubjectConfirmation>
                    </Subject>
                    <Attribute AttributeName="cn"
                        AttributeNamespace="http://www.ja-sig.org/products/cas/">
                        <AttributeValue>{username}</AttributeValue>
                    </Attribute>
                    <Attribute AttributeName="memberOf"
                        AttributeNamespace="http://www.ja-sig.org/products/cas/">
                        <AttributeValue>person</AttributeValue>
                    </Attribute>
                    <Attribute AttributeName="memberOf"
                        AttributeNamespace="http://www.ja-sig.org/products/cas/">
                        <AttributeValue>user</AttributeValue>
                    </Attribute>
                </AttributeStatement>
                <AuthenticationStatement
                    AuthenticationInstant="2025-12-10T14:12:14.741Z"
                    AuthenticationMethod="urn:oasis:names:tc:SAML:1.0:am:password">
                    <Subject>
                        <NameIdentifier>{username}</NameIdentifier>
                        <SubjectConfirmation>
                            <ConfirmationMethod>
                                urn:oasis:names:tc:SAML:1.0:cm:artifact
                            </ConfirmationMethod>
                        </SubjectConfirmation>
                    </Subject>
                </AuthenticationStatement>
            </Assertion>
        </Response>
    </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"""