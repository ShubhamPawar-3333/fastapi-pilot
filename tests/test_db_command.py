"""Tests for the `pilot db` subcommands."""

import os
from pathlib import Path

from typer.testing import CliRunner

from fastapi_pilot.cli import app

runner = CliRunner()


class TestDbHelp:
    """Test that db subcommands show help."""

    def test_db_help(self) -> None:
        """pilot db --help shows available subcommands."""
        result = runner.invoke(app, ["db", "--help"])
        assert result.exit_code == 0
        assert "migrate" in result.output
        assert "upgrade" in result.output
        assert "downgrade" in result.output
        assert "reset" in result.output
        assert "history" in result.output

    def test_db_no_args_shows_help(self) -> None:
        """Running just `pilot db` shows help."""
        result = runner.invoke(app, ["db"])
        assert "migrate" in result.output


class TestDbOutsideProject:
    """Test that db commands fail gracefully outside a project."""

    def test_migrate_outside_project(self, tmp_path: Path) -> None:
        """pilot db migrate fails with a clear message outside a project."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["db", "migrate", "test"])
        assert result.exit_code == 1
        assert "alembic.ini" in result.output.lower() or "No alembic" in result.output

    def test_upgrade_outside_project(self, tmp_path: Path) -> None:
        """pilot db upgrade fails gracefully outside a project."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["db", "upgrade"])
        assert result.exit_code == 1

    def test_downgrade_outside_project(self, tmp_path: Path) -> None:
        """pilot db downgrade fails gracefully outside a project."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["db", "downgrade"])
        assert result.exit_code == 1

    def test_reset_outside_project(self, tmp_path: Path) -> None:
        """pilot db reset fails gracefully outside a project."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["db", "reset"])
        assert result.exit_code == 1

    def test_history_outside_project(self, tmp_path: Path) -> None:
        """pilot db history fails gracefully outside a project."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["db", "history"])
        assert result.exit_code == 1
