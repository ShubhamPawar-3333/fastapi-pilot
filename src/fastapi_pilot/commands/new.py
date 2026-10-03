"""The `pilot new` command — create a new FastAPI project."""

from pathlib import Path

import questionary
import typer
from rich.panel import Panel
from rich.table import Table

from fastapi_pilot.core.config import (
    ADDONS_DIR,
    DEFAULT_DATABASE,
    DEFAULT_PACKAGE_MANAGER,
    SUPPORTED_ADDONS,
    SUPPORTED_DATABASES,
    SUPPORTED_PACKAGE_MANAGERS,
)
from fastapi_pilot.core.console import console
from fastapi_pilot.core.generator import generate_project
from fastapi_pilot.core.validation import validate_project_name

_ADDONS_HELP = "Optional addons to include. Choices: " + ", ".join(SUPPORTED_ADDONS)


def new_command(
    # Typer.Argument = positional (required). User types: pilot new MY-PROJECT
    project_name: str = typer.Argument(
        ...,
        help="Name of the new project directory.",
    ),
    # Typer.Option = flag. User types: pilot new my-api --db postgresql
    database: str | None = typer.Option(
        None,
        "--db",
        help=f"Database backend. Choices: {', '.join(SUPPORTED_DATABASES)}",
    ),
    package_manager: str | None = typer.Option(
        None,
        "--pm",
        help=f"Package manager. Choices: {', '.join(SUPPORTED_PACKAGE_MANAGERS)}",
    ),
    no_interactive: bool = typer.Option(
        False,
        "--no-interactive",
        "--ni",
        help="Skip interactive prompts, use defaults.",
    ),
    addons: list[str] | None = typer.Option(  # noqa: B008
        None,
        "--with",
        help=_ADDONS_HELP,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing directory.",
    ),
) -> None:
    """Create a new FastAPI project with production-ready structure."""
    # ── Validate project name ─────────────────────────────────────────
    name_error = validate_project_name(project_name)
    if name_error:
        console.print(f"[error]Error:[/error] {name_error}")
        raise typer.Exit(code=1)

    project_path = Path.cwd() / project_name

    # ── Pre-flight check ──────────────────────────────────────────────
    # Don't silently overwrite someone's existing project
    if project_path.exists() and not force:
        console.print(
            f"[error]Error:[/error] Directory "
            f"[path]{project_name}[/path] already exists.\n"
            "  Use [command] --force [/command] to overwrite.",
        )
        raise typer.Exit(code=1)

    # ── Banner ────────────────────────────────────────────────────────
    console.print()
    console.print(
        Panel(
            "[heading]pilot new[/heading]\n\nCreate a new FastAPI project",
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()

    # ── Gather options ────────────────────────────────────────────────
    # If --no-interactive, use defaults (or whatever was passed via --db/--pm)
    # Otherwise, show interactive prompts for any option not provided via flags
    if no_interactive:
        db_choice = database or DEFAULT_DATABASE
        pm_choice = package_manager or DEFAULT_PACKAGE_MANAGER
    else:
        # questionary.select shows an arrow-key menu in the terminal
        # .ask() blocks until the user picks one. Returns None if they Ctrl+C.
        db_choice = (
            database
            or questionary.select(
                "Database?",
                choices=SUPPORTED_DATABASES,
                default=DEFAULT_DATABASE,
            ).ask()
        )

        if db_choice is None:  # user pressed Ctrl+C
            raise typer.Abort()

        pm_choice = (
            package_manager
            or questionary.select(
                "Package manager?",
                choices=SUPPORTED_PACKAGE_MANAGERS,
                default=DEFAULT_PACKAGE_MANAGER,
            ).ask()
        )

        if pm_choice is None:
            raise typer.Abort()

    # ── Validate ──────────────────────────────────────────────────────
    # Someone might pass --db mysql (we don't support that)
    if db_choice not in SUPPORTED_DATABASES:
        console.print(
            f"[error]Invalid database:[/error] {db_choice}. "
            f"Choices: {', '.join(SUPPORTED_DATABASES)}"
        )
        raise typer.Exit(code=1)

    if pm_choice not in SUPPORTED_PACKAGE_MANAGERS:
        console.print(
            f"[error]Invalid package manager:[/error] {pm_choice}. "
            f"Choices: {', '.join(SUPPORTED_PACKAGE_MANAGERS)}"
        )
        raise typer.Exit(code=1)

    # ── Summary ───────────────────────────────────────────────────────
    # Show what we're about to create so the user can sanity-check
    console.print()
    table = Table(show_header=False, border_style="dim", padding=(0, 2))
    table.add_column("Setting", style="bold")
    table.add_column("Value", style="cyan")
    table.add_row("Project", project_name)
    table.add_row("Template", "standard")
    table.add_row("Database", db_choice)
    table.add_row("Package Manager", pm_choice)
    if addons:
        table.add_row("Addons", ", ".join(addons))
    console.print(table)
    console.print()

    # ── Validate addons ───────────────────────────────────────────────
    validated_addons: list[str] = []
    if addons:
        for addon in addons:
            if addon not in SUPPORTED_ADDONS:
                console.print(
                    f"[error]Unknown addon:[/error] '{addon}'. "
                    f"Choices: {', '.join(SUPPORTED_ADDONS)}"
                )
                raise typer.Exit(code=1)
            validated_addons.append(addon)

    # ── Generate ──────────────────────────────────────────────────────
    with console.status("[info]Creating project...[/info]", spinner="dots"):
        try:
            generate_project(
                project_name=project_name,
                project_path=project_path,
                database=db_choice,
                package_manager=pm_choice,
            )
        except Exception as e:
            console.print(f"[error]Generation failed:[/error] {e}")
            raise typer.Exit(code=1) from e

    # ── Generate addons ───────────────────────────────────────────────
    if validated_addons:
        _generate_addons(
            project_path=project_path,
            project_name=project_name,
            database=db_choice,
            addons=validated_addons,
        )

    # ── Success ───────────────────────────────────────────────────────
    console.print()
    console.print(
        f"[success]Project created at[/success] [path]./{project_name}[/path]"
    )
    console.print()

    next_steps = (
        f"  cd {project_name}\n"
        "  make run        - start dev server\n"
        "  make test       - run tests\n"
        "  make migrate    - run database migrations"
    )
    if "docker" in validated_addons:
        next_steps += "\n  docker compose up - start with Docker"

    console.print(
        Panel(
            next_steps,
            title="[bold]Next Steps[/bold]",
            border_style="green",
            padding=(1, 2),
        )
    )
    console.print()


def _generate_addons(
    project_path: Path,
    project_name: str,
    database: str,
    addons: list[str],
) -> None:
    """Generate addon files into the project directory."""
    import shutil

    from jinja2 import Environment, FileSystemLoader

    project_slug = project_name.replace("-", "_").replace(" ", "_").lower()

    for addon in addons:
        addon_dir = ADDONS_DIR / addon
        if not addon_dir.is_dir():
            continue

        env = Environment(
            loader=FileSystemLoader(str(addon_dir)),
            keep_trailing_newline=True,
        )

        for source_path in addon_dir.rglob("*"):
            if source_path.is_dir():
                continue

            rel_path = source_path.relative_to(addon_dir)
            filename = rel_path.name

            if filename.endswith(".jinja"):
                dest = project_path / rel_path.parent / filename.removesuffix(".jinja")
                template = env.get_template(str(rel_path.as_posix()))
                rendered = template.render(
                    project_name=project_name,
                    project_slug=project_slug,
                    database=database,
                )
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(rendered, encoding="utf-8")
            else:
                dest = project_path / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest)
