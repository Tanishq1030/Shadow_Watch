# Shadow Watch — Repository Structure

```
Shadow_Watch/
│
├── shadowwatch/                 # Core Python package (pip install shadowwatch)
│   ├── __init__.py              # Public API surface
│   ├── main.py                  # ShadowWatch class
│   ├── exceptions.py            # Custom exceptions
│   ├── models/                  # SQLAlchemy ORM models
│   ├── core/                    # Core algorithms (fingerprinting, entropy, continuity)
│   ├── utils/                   # Input validators, cache helpers
│   └── integrations/            # Framework integrations
│       └── fastapi.py           # FastAPI middleware
│
├── examples/                    # Ready-to-run usage examples
│   ├── fastapi_example.py       # Full FastAPI integration
│   ├── ecommerce_example.py     # E-commerce use case
│   ├── gaming_example.py        # Gaming platform use case
│   ├── social_media_example.py  # Social media use case
│   ├── standalone_usage.py      # Direct Python usage
│   └── README.md                # Examples overview
│
├── tests/                       # Test suite
│   ├── test_simple.py           # PostgreSQL smoke test
│   ├── test_local_dev.py        # Local dev / no-Redis setup
│   ├── test_production.py       # Production PostgreSQL tests
│   ├── test_continuity.py       # ATO / continuity algorithm tests
│   ├── test_day1_refactoring.py # Feature availability tests
│   ├── test_day1_simple.py      # Basic feature tests
│   ├── test_client_integration.py  # End-to-end client flow
│   ├── verify_package.py        # Package import sanity check
│   └── README.md                # Test suite overview
│
├── docs/                        # Markdown documentation
│   ├── GETTING_STARTED.md       # 5-minute setup guide
│   ├── API_REFERENCE.md         # Complete API reference
│   ├── api-reference.md         # Quick API reference (single page)
│   └── INTEGRATION_GUIDES.md    # FastAPI, Django, Flask guides
│
├── dist/                        # Built package (gitignored)
├── .gitignore
├── setup.py                     # PyPI package configuration
├── pyproject.toml               # PEP 517 packaging
├── MANIFEST.in                  # Package data manifest
├── LICENSE                      # MIT License
├── README.md                    # Project overview & quick start
└── STRUCTURE.md                 # This file
```

---

## Directory Purposes

### `/shadowwatch` — Library Code

The installable Python package. All public API lives in `__init__.py`.

### `/examples` — Usage Demos

Runnable scripts showing real-world integrations. No server required.

### `/tests` — Test Suite

Full test coverage. Run with `pytest tests/`. No license needed.

### `/docs` — Documentation

Markdown docs readable on GitHub or any doc site.

---

## What's Excluded (`.gitignore`)

| Category        | Patterns                                  |
| --------------- | ----------------------------------------- |
| Databases       | `*.db`, `*.sqlite`, `*.sqlite3`           |
| Build artifacts | `dist/`, `build/`, `*.egg-info/`          |
| Python cache    | `__pycache__/`, `*.pyc`, `.pytest_cache/` |
| Dev artifacts   | `$null`, `*.tmp`, `dump.rdb`              |
| Coverage        | `.coverage`, `htmlcov/`                   |

---

## Open Source Checklist

- [x] MIT Licensed — no keys, no tiers, no limits
- [x] No license server dependencies
- [x] No event limits
- [x] All features freely available
- [x] Clean `.gitignore` (no test DBs in Git)
- [x] Tests run without any external API
- [x] Ready for PyPI (`pip install shadowwatch`)
- [x] Ready for public GitHub

---

**v2.0.0 — Free and open source forever.** 🌑
