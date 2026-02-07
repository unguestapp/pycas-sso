# PyCAS-SSO

[![PyPI](https://img.shields.io/badge/PyPI-pycas--sso-blue)](https://pypi.org/project/pycas-sso/)
[![Python Version](https://img.shields.io/badge/Python->=3.10-yellowgreen)](https://www.python.org/downloads/)
[![License: BSD-3-Clause](https://img.shields.io/badge/license-BSD--3--Clause-orange.svg)](https://opensource.org/license/bsd-3-clause)
![tests](https://img.shields.io/badge/Tests-pass-success)
![coverage](https://img.shields.io/badge/Coverage-94%25-lightgrey)


PyCAS-SSO is a Python client for the CAS protocol (Central Authentication Service), compatible with multiple HTTP clients with asynchronous support.

## 🎯 Features

- **Client for CAS Protocol** : Implementation of the CAS protocol (1.0, 2.0 and 3.0).
- **Ticket validation** : Support Ticket validation using CAS protocol.
- **User Attributes** : Extract user attribute from CAS response.
- **Multi-HTTP Clients** : Support for `requests`, `httpx`, and `aiohttp`.
- **Async/Await** : Optional support for asynchronous programming.

**Disclaimer: This library is in early version. Bugs may still exist, particularly in advanced CAS features and structure might be subject to change. Use it at your own risk.**

## 📦 Installation

### Requirements

- Python 3.10+

### Basic Installation

```bash
pip install pycas-sso[httpx]
```

### Installation with alternative HTTP library

```bash
# With requests library
pip install pycas-sso[requests]
```

```bash
# With aiohttp library
pip install pycas-sso[aiohttp]
```

## 🔧 Supported HTTP Clients

| Client | Synchronous | Asynchronous | Installation |
|--------|-----------|------------|--------------|
| `requests` | ✅ | ❌ | `pip install pycas-sso[requests]` |
| `httpx` | ✅ | ✅ | `pip install pycas-sso[httpx]` |
| `aiohttp` | ❌ | ✅ | `pip install pycas-sso[aiohttp]` |

The library will automatically detect the available client if you don't specify one.

## 🚀 Quick Start

### Basic Usage (Synchronous)

```python
from pycas_sso import CASClient

# Create a CAS client
with CASClient.create(
    'https://cas.example.com',
    'https://myapp.example.com',
    'https://myapp.example.com/login',
    http_lib='requests'
) as client:

    # Validate a CAS ticket
    try:
        user_info = client.service_validate('ST-123456-abcdef')
        print(f"Authenticated user: {user_info}")
    except Exception as e:
        print(f"Validation error: {e}")
```

### Asynchronous Usage

```python
import asyncio
from pycas_sso import CASClient

async def main():
    # Create an asynchronous CAS client
    async with CASClient.create(
        'https://cas.example.com',
        'https://myapp.example.com',
        'https://myapp.example.com/login',
        http_lib='httpx'  # or 'aiohttp'
    ) as client:
    
        # Validate a ticket asynchronously
        try:
            user_info = await client.aservice_validate('ST-123456-abcdef')
            print(f"Authenticated user: {user_info}")
        except Exception as e:
            print(f"Validation error: {e}")

# Run
asyncio.run(main())
```

## 📚 Documentation

Full documentation is available at [https://pycas-sso.readthedocs.io/](https://pycas-sso.readthedocs.io/en/latest/).

### Contributing

If you want to contribute to the documentation, clone the repo. Then install required packages from `docs/requirements.txt`.

```bash
pip install -r docs/requirements.txt
```

## 🧪 Testing & Development

First install packages required for testing:

```bash
pip install pycas-sso[dev]
```

Then run the test suite with coverage:

```bash
pytest -vv
```

## 📝 License

This project is licensed under BSD-3-Clause or later. See [LICENSE](LICENSE) for more details.

## 👤 Author

- **C. Nicolas** - [GitHub](https://github.com/eryux)

## 🤝 Contributing

Contributions are welcome! Please refer to [CONTRIBUTING.md](docs/source/contributing.md) for guidelines.

## 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md) for the history of changes.

## 📖 Resources

- [CAS Protocol Documentation](https://apereo.github.io/cas/7.3.x/protocol/Protocol-Overview.html)
- [Apereo CAS](https://www.apereo.org/projects/cas)

---

**Note** : This library implements the CAS protocol (Central Authentication Service) and is compatible with Apereo CAS servers and other compatible implementations.
