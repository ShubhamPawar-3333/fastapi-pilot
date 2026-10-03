# 🚀 fastapi-pilot — Improvement Roadmap

Right now the project has **one command** — `pilot new` — which scaffolds a FastAPI project. That's a solid foundation, but it's essentially a "use once and forget" tool. Here's how to turn it into an **ongoing development companion** (which the tagline already promises).

---

## 🔥 High Impact — New CLI Commands

These transform `pilot` from a one-time scaffolder into a tool developers **keep using** throughout the project lifecycle.

### 1. `pilot add <component>` — Code Generator ✅ DONE (v0.2.0)
Scaffold new components into an **existing** project:
```bash
pilot add route users          # creates app/routes/users.py + schema + service + repo
pilot add model Product        # creates app/models/product.py with SQLAlchemy boilerplate
pilot add middleware cors      # adds CORS middleware with sensible defaults
pilot add service payments     # creates app/services/payments.py with interface
```
> **Why:** This is the #1 feature that separates a "starter" from a "daily driver." Django has `startapp`, Rails has `generate` — FastAPI has nothing.

### 2. `pilot run` — Dev Server Wrapper
```bash
pilot run                      # uvicorn with reload, auto-detects app entry
pilot run --port 3000          # custom port
pilot run --workers 4          # production-like mode
```
> **Why:** Saves developers from remembering uvicorn flags. Works from project root without a Makefile.

### 3. `pilot check` — Project Health Check
```bash
pilot check                    # validates project structure, missing files, config issues
```
> **Why:** Useful after manual edits — catches broken imports, missing `__init__.py`, env var mismatches, etc.

### 4. `pilot db` — Database Shortcuts ✅ DONE (v0.2.0)
```bash
pilot db migrate "add users"   # alembic revision --autogenerate -m "add users"
pilot db upgrade               # alembic upgrade head
pilot db downgrade             # alembic downgrade -1
pilot db reset                 # downgrade to base + upgrade to head
```
> **Why:** Alembic commands are verbose and error-prone. This is a huge DX win.

---

## 🎯 Medium Impact — Template & Scaffolding Enhancements

### 5. Template Variants / Addons ✅ PARTIALLY DONE (v0.2.0 — Docker)
Add opt-in features during `pilot new`:
```bash
pilot new my-api --with docker       # ✅ adds Dockerfile + docker-compose.yml
pilot new my-api --with celery       # adds Celery worker setup
pilot new my-api --with redis        # adds Redis caching layer
pilot new my-api --with websockets   # adds WebSocket support
pilot new my-api --with auth         # adds full auth flow (register/login/refresh)
```

### 6. `pilot add route` — Full CRUD Generator ✅ DONE (v0.2.0)
```bash
pilot add route users
```
Generates: model, schema (Create/Update/Read), repository (with all CRUD ops), service, route (GET/POST/PUT/DELETE) — all wired together and auto-registered.

### 7. Configurable Author/Project Metadata
Currently hardcoded to `"Developer"` / `"dev@example.com"`. Support a `~/.pilotrc` or `~/.config/pilot/config.toml` for defaults:
```toml
[defaults]
author_name = "Phoenix"
author_email = "phoenix@example.com"
database = "postgresql"
package_manager = "uv"
```

---

## 🛡️ Code Quality & Robustness

### 8. Expand Test Coverage ✅ PARTIALLY DONE (v0.2.0)
Current tests cover CLI flags and basic generation. v0.2.0 added:
- ✅ Edge cases: special characters in project name, very long names, reserved words
- ✅ Smart singularization/pluralization test coverage
- Generated project structure completeness (still to do)
- Rendered template correctness verification (still to do)
- Generated project actually starts (`uvicorn` import check) (still to do)

### 9. Add Integration Tests
Actually run `pilot new test-project` in CI and verify:
- `make lint` passes on the generated code
- `make test` passes
- The app starts and `/docs` returns 200

### 10. Error Handling Improvements ✅ DONE (v0.2.0)
- ✅ Cleanup on failure — removes partially-created directories
- ✅ Validate `project_name` (no spaces, no special chars, valid Python identifier)

---

## 📦 Distribution & Polish

### 11. Publish to PyPI
The project has proper `pyproject.toml` metadata but isn't on PyPI yet. Add:
- GitHub Actions workflow for automated publishing on tag push
- `MANIFEST.in` or proper package data config for templates

### 12. `pilot upgrade` — Upgrade Existing Projects
When templates improve, let users pull in updates:
```bash
pilot upgrade                  # diff current project against latest template
```

### 13. Plugin System
Let the community contribute templates and generators:
```bash
pilot plugin install fastapi-pilot-graphql
pilot new my-api --template graphql
```

---

## Summary — Priority Table

| Priority | Feature | Effort | Impact | Status |
|----------|---------|--------|--------|--------|
| **P0** | `pilot add route/model/service` | Medium | 🔥🔥🔥 | ✅ Done |
| **P0** | `--with docker` addon | Low | 🔥🔥 | ✅ Done |
| **P1** | `pilot db` commands | Low | 🔥🔥 | ✅ Done |
| **P1** | Project name validation + cleanup | Low | 🛡️🛡️ | ✅ Done |
| **P1** | `~/.pilotrc` config file | Low | 🔥 | ⬜ Todo |
| **P2** | `pilot check` health check | Medium | 🔥 | ⬜ Todo |
| **P2** | Integration tests for generated projects | Medium | 🛡️🛡️ | ⬜ Todo |
| **P2** | Additional addons (celery, redis, auth) | Medium | 🔥🔥 | ⬜ Todo |
| **P3** | `pilot run` dev server wrapper | Low | 🔥 | ⬜ Todo |
| **P3** | PyPI publishing workflow | Low | 📦 | ⬜ Todo |
| **P3** | `pilot upgrade` | High | 🔥 | ⬜ Todo |
| **P3** | Plugin system | High | 🔥 | ⬜ Todo |
