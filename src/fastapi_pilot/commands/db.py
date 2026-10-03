"""The `pilot db` command — database migration shortcuts."""

import subprocess
from pathlib import Path

import typer
from rich.panel import Panel

from fastapi_pilot.core.console import console

# Subcommand group for database operations
db_app = typer.Typer(
    name="db",
    help="Database migration shortcuts (wraps Alembic).",
    no_args_is_help=True,
)


def _find_project_root() -> Path | None:
    """Walk up from cwd to find a pilot-generated project root."""
    current = Path.cwd()
    for directory in [current, *current.parents]:
        alembic_ini = (directory / "alembic.ini").is_file()
        migrations = (directory / "migrations").is_dir()
        if alembic_ini and migrations:
            return directory
        if directory == Path.home():
            break
    return None


def _detect_runner(project_root: Path) -> list[str]:
    """Detect the package manager runner prefix.

    Checks for uv.lock, poetry.lock, or falls back to direct execution.
    """
    if (project_root / "uv.lock").is_file():
        return ["uv", "run"]
    if (project_root / "poetry.lock").is_file():
        return ["poetry", "run"]
    return []


def _run_alembic(
    project_root: Path,
    args: list[str],
    description: str,
) -> None:
    """Run an alembic command with the detected package manager."""
    runner = _detect_runner(project_root)
    cmd = [*runner, "alembic", *args]

    console.print(f"[info]Running:[/info] {' '.join(cmd)}")
    console.print()

    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            check=True,
        )
        if result.returncode == 0:
            console.print(f"\n[success]{description} complete.[/success]")
    except FileNotFoundError:
        tool = runner[0] if runner else "alembic"
        console.print(
            f"[error]Error:[/error] '{tool}' not found on PATH.\n"
            f"  Install it or run alembic manually."
        )
        raise typer.Exit(code=1) from None
    except subprocess.CalledProcessError as e:
        console.print(
            f"[error]{description} failed[/error] (exit code {e.returncode})."
        )
        raise typer.Exit(code=1) from e


@db_app.command(name="migrate")
def db_migrate(
    message: str = typer.Argument(
        "auto",
        help="Migration message (used in the revision filename).",
    ),
) -> None:
    """Generate a new migration from model changes and apply it.

    Equivalent to:
        alembic revision --autogenerate -m "message"
        alembic upgrade head
    """
    project_root = _find_project_root()
    if project_root is None:
        console.print(
            "[error]Error:[/error] No alembic.ini found. "
            "Are you inside a pilot project with a database configured?"
        )
        raise typer.Exit(code=1)

    console.print()
    console.print(
        Panel(
            f'[heading]pilot db migrate[/heading]\n\nGenerating migration: "{message}"',
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()

    _run_alembic(
        project_root,
        ["revision", "--autogenerate", "-m", message],
        "Migration generation",
    )
    console.print()
    _run_alembic(project_root, ["upgrade", "head"], "Migration apply")


@db_app.command(name="upgrade")
def db_upgrade(
    revision: str = typer.Argument(
        "head",
        help="Target revision (default: head).",
    ),
) -> None:
    """Apply pending migrations.

    Equivalent to: alembic upgrade head
    """
    project_root = _find_project_root()
    if project_root is None:
        console.print("[error]Error:[/error] No alembic.ini found.")
        raise typer.Exit(code=1)

    _run_alembic(project_root, ["upgrade", revision], "Upgrade")


@db_app.command(name="downgrade")
def db_downgrade(
    revision: str = typer.Argument(
        "-1",
        help="Target revision (default: -1, i.e., one step back).",
    ),
) -> None:
    """Roll back the last migration.

    Equivalent to: alembic downgrade -1
    """
    project_root = _find_project_root()
    if project_root is None:
        console.print("[error]Error:[/error] No alembic.ini found.")
        raise typer.Exit(code=1)

    _run_alembic(project_root, ["downgrade", revision], "Downgrade")


@db_app.command(name="reset")
def db_reset() -> None:
    """Reset the database — downgrade to base, then upgrade to head.

    Equivalent to:
        alembic downgrade base
        alembic upgrade head
    """
    project_root = _find_project_root()
    if project_root is None:
        console.print("[error]Error:[/error] No alembic.ini found.")
        raise typer.Exit(code=1)

    console.print()
    console.print(
        Panel(
            "[heading]pilot db reset[/heading]\n\n"
            "Downgrading to base and re-applying all migrations",
            border_style="yellow",
            padding=(1, 2),
        )
    )
    console.print()

    _run_alembic(project_root, ["downgrade", "base"], "Downgrade to base")
    console.print()
    _run_alembic(project_root, ["upgrade", "head"], "Upgrade to head")


@db_app.command(name="history")
def db_history() -> None:
    """Show migration history.

    Equivalent to: alembic history --verbose
    """
    project_root = _find_project_root()
    if project_root is None:
        console.print("[error]Error:[/error] No alembic.ini found.")
        raise typer.Exit(code=1)

    _run_alembic(project_root, ["history", "--verbose"], "History")
