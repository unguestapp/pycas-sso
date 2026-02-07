# SPDX-License-Identifier: BSD-3-Clause

"""XML namespaces and templates used for CAS SAML requests and responses."""

XML_CAS_NS = { "cas": "http://www.yale.edu/tp/cas" }

XML_SAML_NS = {
    "soap":  "http://schemas.xmlsoap.org/soap/envelope/",
    "samlp": "urn:oasis:names:tc:SAML:1.0:protocol",
    "saml":  "urn:oasis:names:tc:SAML:1.0:assertion",
}

XML_SAML_2_NS = {
    "soap":  "http://schemas.xmlsoap.org/soap/envelope/",
    "samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
    "saml":  "urn:oasis:names:tc:SAML:2.0:assertion",
}

XML_SAML_VALIDATE_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
    <SOAP-ENV:Header/>
    <SOAP-ENV:Body>
        <samlp:Request xmlns:samlp="urn:oasis:names:tc:SAML:1.0:protocol"
        MajorVersion="1" MinorVersion="1" RequestID="{request_id}" IssueInstant="{issued_at}">
            <samlp:AssertionArtifact>{ticket}</samlp:AssertionArtifact></samlp:Request>
    </SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""