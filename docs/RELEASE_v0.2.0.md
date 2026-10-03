# v0.2.0 — Release Notes

**Release date:** 2026-10-03

This release transforms fastapi-pilot from a one-time scaffolder into an ongoing development companion with three new commands and Docker support.

---

## New Features

### `pilot add` — Component Generator

Generate components inside an **existing** pilot project. The headline feature that makes `pilot` useful beyond project creation.

```bash
pilot add route users       # full CRUD stack (4 files + auto-registration)
pilot add model product     # just the SQLAlchemy model
pilot add schema order      # just the Pydantic schemas
pilot add service payments  # just the service layer
pilot add repository items  # just the repository layer
```

**`pilot add route <name>` generates a complete vertical slice:**

| Generated File | What's Inside |
|----------------|---------------|
| `app/routes/<name>.py` | 5 CRUD endpoints (list, get, create, update, delete) |
| `app/schemas/<name>.py` | Pydantic v2 schemas (Create, Update, Read) with `from_attributes` |
| `app/services/<name>.py` | Business logic layer with error handling via `NotFoundException` |
| `app/repositories/<name>.py` | Async SQLAlchemy CRUD ops (or in-memory stub if `--db none`) |
| `app/routes/router.py` | **Auto-updated** — import + `include_router()` added automatically |

**Smart naming:**
- `users` → class `User`, table `users`, route `/users/`
- `categories` → class `Category`, table `categories`, route `/categories/`
- `blog_posts` → class `BlogPost`, table `blog_posts`, route `/blog_posts/`

**Key implementation files:**
- `src/fastapi_pilot/commands/add.py` — command logic, project detection, route registration
- `src/fastapi_pilot/core/validation.py` — name validation, slug/class/plural conversion
- `src/fastapi_pilot/templates/components/*.py.jinja` — Jinja2 templates for each component type

---

### `pilot db` — Database Migration Shortcuts

Ergonomic wrappers around Alembic that auto-detect your package manager (uv/poetry/pip):

```bash
pilot db migrate "add users"   # autogenerate revision + upgrade head
pilot db upgrade               # alembic upgrade head
pilot db upgrade abc123        # upgrade to specific revision
pilot db downgrade             # roll back one step
pilot db downgrade base        # roll back everything
pilot db reset                 # downgrade base + upgrade head
pilot db history               # show migration history (verbose)
```

**Key implementation file:** `src/fastapi_pilot/commands/db.py`

---

### `--with docker` Addon for `pilot new`

```bash
pilot new my-api --with docker
pilot new my-api --with docker --db postgresql --no-interactive
```

**Generated files:**

| File | Details |
|------|---------|
| `Dockerfile` | Multi-stage build, Python 3.12-slim, uv for deps, non-root user, layer caching |
| `docker-compose.yml` | App service with hot-reload + PostgreSQL with healthchecks (when DB is configured) |
| `.dockerignore` | Excludes venvs, caches, .git, build artifacts |

The addon system is extensible — adding new addons (celery, redis, etc.) only requires dropping templates into `src/fastapi_pilot/templates/addons/<name>/` and adding the name to `SUPPORTED_ADDONS` in config.

**Key implementation files:**
- `src/fastapi_pilot/commands/new.py` — `--with` flag handling, `_generate_addons()` function
- `src/fastapi_pilot/templates/addons/docker/` — template files

---

### Project Name Validation

`pilot new` now validates project names before generation:
- Must start with a letter
- Only letters, digits, hyphens, and underscores allowed
- Max 100 characters
- Cannot produce Python keywords when slugified (e.g., `class`, `import`)

**Key implementation file:** `src/fastapi_pilot/core/validation.py`

---

### Cleanup on Failure

If template rendering fails partway through `pilot new`, the partially-created directory is automatically removed instead of leaving behind a broken project.

**Key implementation file:** `src/fastapi_pilot/core/generator.py` (try/except around `_render_template`)

---

## Files Changed

### New Source Files
| File | Lines | Purpose |
|------|-------|---------|
| `src/fastapi_pilot/commands/add.py` | ~250 | `pilot add` command |
| `src/fastapi_pilot/commands/db.py` | ~175 | `pilot db` command group |
| `src/fastapi_pilot/core/validation.py` | ~120 | Name validation + naming utilities |
| `src/fastapi_pilot/templates/components/route.py.jinja` | ~70 | Route template |
| `src/fastapi_pilot/templates/components/model.py.jinja` | ~30 | Model template |
| `src/fastapi_pilot/templates/components/schema.py.jinja` | ~35 | Schema template |
| `src/fastapi_pilot/templates/components/service.py.jinja` | ~50 | Service template |
| `src/fastapi_pilot/templates/components/repository.py.jinja` | ~110 | Repository template (DB + in-memory) |
| `src/fastapi_pilot/templates/addons/docker/Dockerfile` | ~35 | Multi-stage Dockerfile |
| `src/fastapi_pilot/templates/addons/docker/docker-compose.yml.jinja` | ~40 | Compose with optional PostgreSQL |
| `src/fastapi_pilot/templates/addons/docker/.dockerignore` | ~13 | Docker build exclusions |

### New Test Files
| File | Tests | Purpose |
|------|-------|---------|
| `tests/test_add_command.py` | 11 | Full-stack generation, auto-registration, errors, idempotency |
| `tests/test_db_command.py` | 7 | Help output, subcommand registration, outside-project errors |
| `tests/test_addons.py` | 10 | Docker file generation, DB-aware compose, invalid addon errors |
| `tests/test_validation.py` | 24 | Name validation, slugs, PascalCase, pluralization edge cases |

### Modified Source Files
| File | Change |
|------|--------|
| `src/fastapi_pilot/cli.py` | Register `add` command and `db` subgroup |
| `src/fastapi_pilot/commands/new.py` | Add `--with` flag, name validation, addon generation |
| `src/fastapi_pilot/core/config.py` | Add `COMPONENT_TEMPLATE_DIR`, `ADDONS_DIR`, `SUPPORTED_ADDONS` |
| `src/fastapi_pilot/core/generator.py` | Add cleanup-on-failure logic |
| `src/fastapi_pilot/__init__.py` | Version bump 0.1.0 → 0.2.0 |
| `pyproject.toml` | Version bump 0.1.0 → 0.2.0 |
| `README.md` | Full rewrite with new command documentation |
| `CHANGELOG.md` | v0.2.0 entry with all new features |

---

## Test Results

```
65 passed in 6.59s
All ruff checks passed
```

**Test breakdown:** 13 existing (all pass) + 52 new = 65 total
