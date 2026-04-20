"""Main CLI entry point for fastapi-pilot."""

import typer

from fastapi_pilot import __version__

app = typer.Typer(
    name="pilot",
    help="The development companion for FastAPI.",
    no_args_is_help=True,  # running just `pilot` shows help instead of doing nothing
    rich_markup_mode="rich",  # allows [bold], [red], etc. in help text
    add_completion=False,  # don't add shell completion commands (keeps help clean)
)


def version_callback(value: bool) -> None:
    """Print version and exit.

    This is a Typer "callback" — it runs when the user passes --version.
    `is_eager=True` below means it runs BEFORE any other processing,
    so `pilot --version new my-app` still just prints the version.
    """
    if value:
        from fastapi_pilot.core.console import console

        console.print(f"[bold]fastapi-pilot[/bold] v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show the version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """The development companion for FastAPI."""


def _register_commands() -> None:
    """Register all CLI commands.

    We do this in a function (not at module level) to avoid circular imports.
    When cli.py loads, it imports __version__ from __init__.py.
    If new.py also imported from cli.py, we'd have a circle.
    By deferring registration to a function call, new.py is only imported
    when this function runs, after cli.py is fully loaded.
    """
    from fastapi_pilot.commands.new import new_command

    app.command(name="new", help="Create a new FastAPI project.")(new_command)


_register_commands()
