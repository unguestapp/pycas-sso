# Quickstart

This section covers basic installation and usage of the PyCAS-SSO library.

## Requirements

- Python 3.10 or newer.


## Installation

First step is to install the library.

```{note}
It's highly recommended to use [Python virtual env.](https://docs.python.org/3/library/venv.html).
```


### Using PyPi

Installing PyCAS-SSO from PyPi is the easiest way to install the library.

- In your Python venv :

```bash
pip install pycas-sso[httpx]
```

It will install PyCAS-SSO alongside the HTTPX library. The HTTPX library is the default choice for PyCAS-SSO because it supports both synchronous and asynchronous programming.

If you want to use another HTTP client with PyCAS-SSO refer to the list of supported library below.


### Supported HTTP Clients

| Client | Synchronous | Asynchronous | Installation |
|--------|-----------|------------|--------------|
| `requests` | ✅ | ❌ | `pip install pycas-sso[requests]` |
| `httpx` | ✅ | ✅ | `pip install pycas-sso[httpx]` |
| `aiohttp` | ❌ | ✅ | `pip install pycas-sso[aiohttp]` |


### From Git Repository

- To install the library manually in your project, download the latest release from [GitHub](https://github.com/unguestapp/pycas-sso/releases).

- Extract the archive and copy the `pycas_sso` folder into your project folder.

- Install the library dependencies from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

- Finally install `httpx` or another supported HTTP client using `pip`.

```bash
pip install httpx
```


## Basic Usage

The common uses of CAS are:
- Check if a user is authenticated on a service, and if not, redirect them to the CAS login page;
- After user sign-in, they will be redirected to the service with a ticket included in the callback URL;
- The service validates the ticket with the CAS service and then marks the user as authenticated if successful.


### Start a CAS Client

Let's get started. First we need to instantiate a CAS client using [](#pycas_sso.cas.CASClient.create).

```python
from pycas_sso.cas import CASClient

# URL of your CAS service
provider = "https://cas.example.com"

# URL of your service
# Note: don't forget to authorize this url on your CAS service
service = "https://service.example.com/"

# Callback URL of you service
# This is the URL where user will be redirect after sign-in
callback = "https://service.example.com/login"

if __name__ == "__main__":
    # Use Python ContextManager with CASClient.create
    with CASClient.create(provider, service, callback) as client:
        pass
```

[](#pycas_sso.cas.CASClient.create) will return a [](#pycas_sso.clients.core.CASClientBase) instance depending on your HTTP client. You can force the HTTP client by specifying the `http_lib` parameter (e.g., `http_lib = 'requests'`), otherwise it will search for a supported HTTP library that is installed and use it.

If you want to use asynchronous operations:

```python
import asyncio
from pycas_sso.cas import CASClient

...

async def main():
    async with CASClient.create(provider, service, callback, is_async = True) as client:
        pass

if __name__ == "__main__":
    asyncio.run(main())
```

Don't forget the `is_async = True` parameter.


### Get Login Page URL

To retrieve the login page URL, use [](#pycas_sso.clients.core.CASClientBase.login_form_url).

```python
with CASClient.create(provider, service, callback) as client:
    login_url = client.login_form_url()
```

### Extract Service Ticket from URL

To extract ticket from a URL you just need to pass the URL to [](#pycas_sso.clients.core.CASClientBase.ticket_from_url).

```python
url = "https://service.example.com/login?ticket=ST-123456-789"

with CASClient.create(provider, service) as client:
    ticket = client.ticket_from_url(url) # ticket = "ST-123456-789"
```

### Validate the Service Ticket

Validating the ticket allows verification of the ticket with the CAS service and retrieval of user information. To achieve this, we will use [](#pycas_sso.clients.core.CASClientBase.service_validate).

```python
from pycas_sso.errors import CASServiceAuthenticationFailure

ticket = "ST-123456-789"

with CASClient.create(provider, service, callback) as client:
    try:
        data = client.service_validate(ticket)
        print(f"Validation succeeded\nUsername: {data.username}")
    except CASServiceAuthenticationFailure as err:
        print(err)
```

Or with asynchronous:

```python
...

async with CASClient.create(provider, service, callback) as client:
    try:
        data = await client.aservice_validate(ticket)
        print(f"Validation succeeded\nUsername: {data.username}")
    except CASServiceAuthenticationFailure as err:
        print(err)
```

```{tip}
Use the `version='2|3'` parameter to specify which version of the CAS protocol to use when performing a service validation call.
```

You can also use:
- [](#pycas_sso.clients.core.CASClientBase.validate) for CAS 1.0 validation;
- [](#pycas_sso.clients.core.CASClientBase.saml_validate) for SAML validation.

## Go Further

- Go to the [](example/index) section for more examples.
- Check the [](api/index) to discover all possibilities and features offered by the library.
- Take a look at the [CAS Protocol Documentation](https://apereo.github.io/cas/7.3.x/protocol/Protocol-Overview.html) from Apereo.