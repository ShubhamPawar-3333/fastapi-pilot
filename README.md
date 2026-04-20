# fastapi-pilot

> The development companion for FastAPI. Not just a starter — a daily driver.

[![CI](https://github.com/ShubhamPawar-3333/fastapi-pilot/actions/workflows/ci.yml/badge.svg)](https://github.com/ShubhamPawar-3333/fastapi-pilot/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**fastapi-pilot** scaffolds production-ready FastAPI projects with a single command. No boilerplate. No copy-pasting from old projects. Just run `pilot new` and start writing business logic.

## Install

```bash
pip install fastapi-pilot
```

## Quick Start

```bash
pilot new my-api
cd my-api
make run
```

That's it. You get a running FastAPI app at `http://localhost:8000` with auto-docs at `/docs`.

## What You Get

Every generated project includes:

```
my-api/
├── app/
│   ├── main.py              # FastAPI entry point with lifespan
│   ├── core/
│   │   ├── config.py        # Pydantic v2 settings from .env
│   │   ├── database.py      # Async SQLAlchemy engine & sessions
│   │   ├── security.py      # bcrypt + JWT utilities
│   │   ├── exceptions.py    # Custom exception hierarchy
│   │   └── logging.py       # Structured logging
│   ├── models/              # SQLAlchemy table definitions
│   ├── schemas/             # Pydantic request/response models
│   ├── routes/              # API route handlers
│   ├── services/            # Business logic layer
│   ├── repositories/        # Database query layer
│   ├── dependencies/        # FastAPI Depends() functions
│   ├── middleware/           # Request logging middleware
│   └── utils/               # Utility functions
├── tests/                   # Async pytest + httpx setup
├── migrations/              # Alembic async migrations
├── Makefile                 # Dev shortcuts
├── pyproject.toml
└── .env
```

**Data flow:**

```
Request -> Routes -> Services -> Repositories -> Database
                       |
                    Schemas (validation)
```

## CLI Options

```bash
# Interactive mode (default) — prompts for database & package manager
pilot new my-api

# Non-interactive with defaults (postgresql + uv)
pilot new my-api --no-interactive

# Choose database backend
pilot new my-api --db postgresql   # async SQLAlchemy + asyncpg
pilot new my-api --db sqlite       # async SQLAlchemy + aiosqlite
pilot new my-api --db none         # no database layer

# Choose package manager
pilot new my-api --pm uv           # recommended
pilot new my-api --pm pip
pilot new my-api --pm poetry

# Overwrite existing directory
pilot new my-api --force

# Check version
pilot --version
```

## Development Commands

Every generated project comes with a `Makefile`:

```bash
make run          # Start dev server with hot reload
make test         # Run tests
make test-cov     # Run tests with coverage report
make lint         # Lint (ruff) + type check (mypy)
make format       # Auto-format code
make migrate      # Generate and apply database migrations
make db-reset     # Reset database (downgrade + upgrade)
make clean        # Remove caches and build artifacts
```

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip/poetry

## Contributing

Contributions are welcome. Please open an issue first to discuss what you'd like to change.

## License

[MIT](LICENSE)
