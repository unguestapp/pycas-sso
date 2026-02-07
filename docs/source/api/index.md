# API Reference

```{eval-rst}  
.. automodule:: pycas_sso
   :members:
   :show-inheritance:
```

## Main module

```{eval-rst}
.. automodule:: pycas_sso.cas
   :members:
   :show-inheritance:
```

## Client interface

**Never use client interface directly, use factory method [](#pycas_sso.cas.CASClient.create) instead.**

```{eval-rst}
.. automodule:: pycas_sso.clients
   :members:
   :show-inheritance:

.. automodule:: pycas_sso.clients.core
   :members:
   :show-inheritance:
```

## Specific client interface

**Never use client interface directly, use factory method [](#pycas_sso.cas.CASClient.create) instead.**

```{eval-rst}
.. autoclass:: pycas_sso.clients.httpx.CASClient_Httpx

.. autoclass:: pycas_sso.clients.requests.CASClient_Requests

.. autoclass:: pycas_sso.clients.aiohttp.CASClient_AIOHttp
```

## Exceptions

```{eval-rst}
.. automodule:: pycas_sso.errors
   :members:
   :show-inheritance:
```

## Miscellaneous

```{eval-rst}
.. automodule:: pycas_sso.schemas
   :members:
   :show-inheritance:
```