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

## [Unreleased]