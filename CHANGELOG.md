## [0.1.0] - 2026-04-21

### Added

- `pilot new` command — create a production-ready FastAPI project
- Standard template with layered architecture (routes → services → repositories)
- Async SQLAlchemy with PostgreSQL or SQLite support
- Pydantic v2 settings loaded from .env
- JWT + bcrypt security utilities
- Structured logging with per-request duration tracking
- Alembic async migration environment
- Async pytest + httpx test infrastructure
- Makefile with dev shortcuts (run, test, lint, format, migrate)
- Interactive CLI with questionary prompts
- --no-interactive mode for CI/scripted usage
- --force mode to overwrite existing directories
- Post-generation: automatic dependency install and git init
- GitHub Actions CI pipeline (lint, test matrix, template validation)

## [0.2.0] - 2026-10-03

### Added

- `pilot add` command — generate components in existing projects
  - `pilot add route <name>` — generates full CRUD stack (route + schema + service + repository)
  - `pilot add model <name>` — generates SQLAlchemy model
  - `pilot add schema <name>` — generates Pydantic schemas
  - `pilot add service <name>` — generates service layer
  - `pilot add repository <name>` — generates repository layer
  - Auto-registers new routes in `app/routes/router.py`
  - Auto-detects database configuration for correct code generation
  - Smart singularization/pluralization (users → User, categories → Category)
- `pilot db` command — database migration shortcuts wrapping Alembic
  - `pilot db migrate <message>` — generate and apply migration
  - `pilot db upgrade [revision]` — apply pending migrations
  - `pilot db downgrade [revision]` — roll back migrations
  - `pilot db reset` — downgrade to base and re-apply all migrations
  - `pilot db history` — show migration history
  - Auto-detects package manager (uv/poetry/pip) from lockfiles
- `--with docker` addon for `pilot new` — adds Dockerfile, docker-compose.yml, .dockerignore
  - Multi-stage Dockerfile with layer caching and non-root user
  - Docker Compose with PostgreSQL service and healthchecks (when DB is configured)
- Project name validation — catches invalid names before generation
- Cleanup on failure — removes partially-created directories if generation fails

## [Unreleased]