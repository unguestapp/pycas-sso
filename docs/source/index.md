# PyCAS-SSO : Python CAS client

[![GitHub](https://img.shields.io/badge/github-pycas--sso-blue?logo=github)](https://github.com/unguestapp/pycas-sso)
[![PyPI](https://img.shields.io/badge/PyPI-pycas--sso-blue)](https://pypi.org/project/pycas-sso/)
[![Python Version](https://img.shields.io/badge/Python->=3.10-yellowgreen)](https://www.python.org/downloads/)
[![License: BSD-3-Clause](https://img.shields.io/badge/license-BSD--3--Clause-orange.svg)](https://opensource.org/license/bsd-3-clause)

PyCAS-SSO is a Python client for the CAS protocol (Central Authentication Service), compatible with multiple HTTP clients and including asynchronous support.

---

## Features

- **Client for CAS Protocol** : Implementation of the CAS protocol (1.0, 2.0 and 3.0).
- **Ticket Validation** : Support Ticket validation using CAS protocol.
- **User Attributes** : Extract user attribute from CAS response.
- **Multi-HTTP Clients** : Support for `requests`, `httpx`, and `aiohttp`.
- **Async/Await** : Optional support for asynchronous programming.

To get started read the [](quickstart) documentation.

```{caution}
This library is in early version. Bugs may still exist, particularly in advanced CAS features and structure might be subject to change. Use it at your own risk.
```

---

## Table of content

```{toctree}
:maxdepth: 1

quickstart
example/index
api/index
changelog
contributing

GitHub <https://github.com/unguestapp/pycas-sso>
PyPI <https://pypi.org>
```
---

## License

This project is licensed under BSD-3-Clause.

---

## Resources

- [Official GitHub](https://github.com/unguestapp/pycas-sso)
- [CAS Protocol Documentation](https://apereo.github.io/cas/7.3.x/protocol/Protocol-Overview.html)
- [Apereo CAS](https://www.apereo.org/projects/cas)