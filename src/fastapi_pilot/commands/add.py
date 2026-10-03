"""The `pilot add` command — generate components in an existing FastAPI project."""

import re
from pathlib import Path

import typer
from jinja2 import Environment, FileSystemLoader
from rich.panel import Panel
from rich.table import Table

from fastapi_pilot.core.config import COMPONENT_TEMPLATE_DIR
from fastapi_pilot.core.console import console
from fastapi_pilot.core.validation import (
    to_class_name,
    to_plural,
    to_slug,
    validate_component_name,
)

# Component types that can be generated
COMPONENT_TYPES = ["route", "model", "schema", "service", "repository"]

# Sentinel marker pattern used in router.py to auto-register new routes
ROUTE_MARKER = re.compile(r"^# --- pilot:routes ---$", re.MULTILINE)


def _find_project_root() -> Path | None:
    """Walk up from cwd to find a pilot-generated project root.

    A project root is identified by having an app/ directory with
    a main.py and a routes/ subdirectory.
    """
    current = Path.cwd()
    for directory in [current, *current.parents]:
        app_dir = directory / "app"
        if (
            app_dir.is_dir()
            and (app_dir / "main.py").is_file()
            and (app_dir / "routes").is_dir()
        ):
            return directory
        # Don't search above home directory
        if directory == Path.home():
            break
    return None


def _detect_database(project_root: Path) -> bool:
    """Detect whether the project has a database configured.

    Checks if the database.py file contains actual SQLAlchemy setup
    (not the 'No database configured' placeholder).
    """
    db_file = project_root / "app" / "core" / "database.py"
    if not db_file.exists():
        return False
    content = db_file.read_text(encoding="utf-8")
    return "DeclarativeBase" in content or "Base" in content


def _render_component(
    component_type: str,
    data: dict[str, str | bool],
) -> str:
    """Render a component template and return the content as a string."""
    env = Environment(
        loader=FileSystemLoader(str(COMPONENT_TEMPLATE_DIR)),
        keep_trailing_newline=True,
    )
    template = env.get_template(f"{component_type}.py.jinja")
    return template.render(**data)


def _register_route(project_root: Path, name: str, name_plural: str) -> bool:
    """Add an import and include_router line to app/routes/router.py.

    Looks for the `# --- pilot:routes ---` sentinel marker and inserts
    the new route registration just above it. Returns True if successful.
    """
    router_file = project_root / "app" / "routes" / "router.py"
    if not router_file.exists():
        return False

    content = router_file.read_text(encoding="utf-8")

    # Check if this route is already registered
    if f"from app.routes.{name}" in content:
        console.print(
            f"[warning]Route '{name}' is already registered in router.py[/warning]"
        )
        return True

    # Build the import and registration lines
    import_line = f"from app.routes.{name} import router as {name}_router"
    register_line = (
        f"api_router.include_router("
        f'{name}_router, prefix="/{name_plural}", '
        f'tags=["{name_plural}"])'
    )

    # Insert import at the end of the import block (before the first blank line
    # after imports, or before the api_router line)
    lines = content.split("\n")
    import_insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("from app.routes.") or line.startswith("from app."):
            import_insert_idx = i + 1
        if line.startswith("api_router = APIRouter"):
            break

    lines.insert(import_insert_idx, import_line)

    # Now find the marker (accounting for the line we just inserted)
    marker_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "# --- pilot:routes ---":
            marker_idx = i
            break

    if marker_idx is not None:
        lines.insert(marker_idx, register_line)
    else:
        # No marker found — append to end of file
        lines.append(register_line)

    router_file.write_text("\n".join(lines), encoding="utf-8")
    return True


def add_command(
    component_type: str = typer.Argument(
        ...,
        help=f"Type of component to add. Choices: {', '.join(COMPONENT_TYPES)}",
    ),
    name: str = typer.Argument(
        ...,
        help="Name of the component (e.g., 'users', 'products', 'orders').",
    ),
) -> None:
    """Generate a new component (route, model, schema, service, or repository)
    in an existing FastAPI project.

    Examples:
        pilot add route users       — creates route + schema + service + repo
        pilot add model product     — creates just the model file
        pilot add service payments  — creates just the service file
    """
    # ── Validate inputs ──────────────────────────────────────────────
    if component_type not in COMPONENT_TYPES:
        console.print(
            f"[error]Unknown component type:[/error] '{component_type}'. "
            f"Choices: {', '.join(COMPONENT_TYPES)}"
        )
        raise typer.Exit(code=1)

    name_error = validate_component_name(name, component_type)
    if name_error:
        console.print(f"[error]Error:[/error] {name_error}")
        raise typer.Exit(code=1)

    # ── Find project root ────────────────────────────────────────────
    project_root = _find_project_root()
    if project_root is None:
        console.print(
            "[error]Error:[/error] Not inside a FastAPI pilot project.\n"
            "  Run this command from within a project created by"
            " [command]pilot new[/command]."
        )
        raise typer.Exit(code=1)

    # ── Prepare template data ────────────────────────────────────────
    slug = to_slug(name)
    class_name = to_class_name(name)
    name_plural = to_plural(slug)
    has_db = _detect_database(project_root)

    template_data: dict[str, str | bool] = {
        "name": slug,
        "name_plural": name_plural,
        "class_name": class_name,
        "has_db": has_db,
    }

    # ── Determine what to generate ───────────────────────────────────
    # Adding a 'route' generates the full stack (route + schema + service + repo)
    # Adding anything else generates just that single component
    if component_type == "route":
        components_to_generate = ["route", "schema", "service", "repository"]
    else:
        components_to_generate = [component_type]

    # ── Banner ────────────────────────────────────────────────────────
    console.print()
    console.print(
        Panel(
            f"[heading]pilot add {component_type}[/heading]\n\n"
            f"Generating [bold]{name}[/bold] "
            f"component{'s' if len(components_to_generate) > 1 else ''}",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    # ── Map component types to output directories ─────────────────────
    dir_map = {
        "route": "routes",
        "model": "models",
        "schema": "schemas",
        "service": "services",
        "repository": "repositories",
    }

    created_files: list[str] = []
    skipped_files: list[str] = []

    for comp in components_to_generate:
        target_dir = project_root / "app" / dir_map[comp]
        target_file = target_dir / f"{slug}.py"

        if target_file.exists():
            skipped_files.append(str(target_file.relative_to(project_root)))
            continue

        # Render and write
        content = _render_component(comp, template_data)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file.write_text(content, encoding="utf-8")
        created_files.append(str(target_file.relative_to(project_root)))

    # ── Auto-register route in router.py ─────────────────────────────
    if component_type == "route" and f"app/routes/{slug}.py" in created_files:
        _register_route(project_root, slug, name_plural)
        created_files.append("app/routes/router.py (updated)")

    # ── Summary ───────────────────────────────────────────────────────
    console.print()
    if created_files:
        table = Table(
            title="[bold green]Created[/bold green]",
            show_header=False,
            border_style="dim",
            padding=(0, 2),
        )
        table.add_column("File", style="cyan")
        for f in created_files:
            table.add_row(f)
        console.print(table)

    if skipped_files:
        console.print()
        table = Table(
            title="[bold yellow]Skipped (already exists)[/bold yellow]",
            show_header=False,
            border_style="dim",
            padding=(0, 2),
        )
        table.add_column("File", style="dim")
        for f in skipped_files:
            table.add_row(f)
        console.print(table)

    console.print()

    if component_type == "route":
        console.print(
            Panel(
                f"  Your new [bold]/{name_plural}[/bold] endpoints are ready!\n\n"
                f"  GET     /api/v1/{name_plural}/\n"
                f"  GET     /api/v1/{name_plural}/{{id}}\n"
                f"  POST    /api/v1/{name_plural}/\n"
                f"  PUT     /api/v1/{name_plural}/{{id}}\n"
                f"  DELETE  /api/v1/{name_plural}/{{id}}",
                title="[bold]Next Steps[/bold]",
                border_style="green",
                padding=(1, 2),
            )
        )
    else:
        console.print(f"[success]Done![/success] {len(created_files)} file(s) created.")
    console.print()
