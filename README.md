# fastapi-pilot

> The development companion for FastAPI. Not just a starter — a daily driver.

[![CI](https://github.com/ShubhamPawar-3333/fastapi-pilot/actions/workflows/ci.yml/badge.svg)](https://github.com/ShubhamPawar-3333/fastapi-pilot/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**fastapi-pilot** scaffolds production-ready FastAPI projects and keeps helping you build them. Generate full CRUD endpoints, manage database migrations, and add Docker support — all from the CLI.

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

## CLI Commands

### `pilot new` — Create a Project

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

# Include Docker support
pilot new my-api --with docker     # adds Dockerfile + docker-compose.yml

# Overwrite existing directory
pilot new my-api --force

# Check version
pilot --version
```

### `pilot add` — Generate Components

Add new components to an **existing** project. Run from inside a pilot project:

```bash
# Full CRUD stack — creates route + schema + service + repository
pilot add route users

# Individual components
pilot add model product
pilot add schema order
pilot add service payments
pilot add repository invoices
```

**What `pilot add route users` generates:**

| File | Contents |
|------|----------|
| `app/routes/users.py` | GET, POST, PUT, DELETE endpoints |
| `app/schemas/users.py` | UserCreate, UserUpdate, UserRead (Pydantic v2) |
| `app/services/users.py` | Business logic with error handling |
| `app/repositories/users.py` | Async SQLAlchemy CRUD operations |
| `app/routes/router.py` | Auto-updated with route registration |

The generated code follows your project's database configuration — if you chose `--db none`, repositories use in-memory storage instead of SQLAlchemy.

### `pilot db` — Database Shortcuts

Ergonomic wrappers around Alembic. Auto-detects your package manager:

```bash
pilot db migrate "add users table"   # autogenerate + upgrade head
pilot db upgrade                     # apply pending migrations
pilot db downgrade                   # roll back one migration
pilot db reset                       # downgrade to base + upgrade head
pilot db history                     # show migration history
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

## Docker Support

Use `--with docker` when creating a project:

```bash
pilot new my-api --with docker --no-interactive
cd my-api
docker compose up
```

This generates:
- **Dockerfile** — multi-stage build with layer caching and non-root user
- **docker-compose.yml** — app + PostgreSQL (with healthchecks) for dev
- **.dockerignore** — keeps images lean

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip/poetry

## Contributing

Contributions are welcome. Please open an issue first to discuss what you'd like to change.

## License

[MIT](LICENSE)
