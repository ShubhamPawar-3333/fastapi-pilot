"""The `pilot new` command — create a new FastAPI project."""

from pathlib import Path
from typing import Optional

import questionary
import typer
from rich.panel import Panel
from rich.table import Table

from fastapi_pilot.core.config import (
    DEFAULT_DATABASE,
    DEFAULT_PACKAGE_MANAGER,
    SUPPORTED_DATABASES,
    SUPPORTED_PACKAGE_MANAGERS,
)
from fastapi_pilot.core.console import console
from fastapi_pilot.core.generator import generate_project


def new_command(
    # Typer.Argument = positional (required). User types: pilot new MY-PROJECT
    project_name: str = typer.Argument(
        ...,
        help="Name of the new project directory.",
    ),
    # Typer.Option = flag. User types: pilot new my-api --db postgresql
    database: Optional[str] = typer.Option(
        None,
        "--db",
        help=f"Database backend. Choices: {', '.join(SUPPORTED_DATABASES)}",
    ),
    package_manager: Optional[str] = typer.Option(
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
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing directory.",
    ),
) -> None:
    """Create a new FastAPI project with production-ready structure."""
    project_path = Path.cwd() / project_name

    # ── Pre-flight check ──────────────────────────────────────────────
    # Don't silently overwrite someone's existing project
    if project_path.exists() and not force:
        console.print(
            f"[error]Error:[/error] Directory [path]{project_name}[/path] already exists.\n"
            "  Use [command] --force [/command] to overwrite.",
        )
        raise typer.Exit(code=1)

    # ── Banner ────────────────────────────────────────────────────────
    console.print()
    console.print(
        Panel(
            "[heading]✈  pilot new[/heading]\n\nCreate a new FastAPI project",
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
        db_choice = database or questionary.select(
            "Database?",
            choices=SUPPORTED_DATABASES,
            default=DEFAULT_DATABASE,
        ).ask()

        if db_choice is None:  # user pressed Ctrl+C
            raise typer.Abort()

        pm_choice = package_manager or questionary.select(
            "Package manager?",
            choices=SUPPORTED_PACKAGE_MANAGERS,
            default=DEFAULT_PACKAGE_MANAGER,
        ).ask()

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
    console.print(table)
    console.print()

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

    # ── Success ───────────────────────────────────────────────────────
    console.print()
    console.print(
        f"[success]✅ Project created at[/success] [path]./{project_name}[/path]"
    )
    console.print()
    console.print(
        Panel(
            f"  cd {project_name}\n"
            "  make run        → start dev server\n"
            "  make test       → run tests\n"
            "  make migrate    → run database migrations",
            title="[bold]Next Steps[/bold]",
            border_style="green",
            padding=(1, 2),
        )
    )
    console.print()