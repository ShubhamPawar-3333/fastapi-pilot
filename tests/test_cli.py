"""Tests for the pilot CLI entry point."""

from typer.testing import CliRunner

from fastapi_pilot import __version__
from fastapi_pilot.cli import app

runner = CliRunner()


class TestVersion:
    """Test the --version flag."""

    def test_version_flag(self) -> None:
        """pilot --version prints the version string."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "fastapi-pilot" in result.output
        assert __version__ in result.output

    def test_version_short_flag(self) -> None:
        """-v is a shortcut for --version."""
        result = runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        assert __version__ in result.output


class TestHelp:
    """Test the --help flag."""

    def test_help_flag(self) -> None:
        """pilot --help lists available commands."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "new" in result.output

    def test_no_args_shows_help(self) -> None:
        """Running just `pilot` (no args) shows help because of no_args_is_help=True."""
        result = runner.invoke(app, [])
        assert "pilot" in result.output.lower()
