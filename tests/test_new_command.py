"""Tests for the `pilot new` command."""

import os
from pathlib import Path

from typer.testing import CliRunner

from fastapi_pilot.cli import app

runner = CliRunner()


class TestNewCommand:
    """Test project generation via `pilot new`."""

    def test_creates_project_directory(self, tmp_path: Path) -> None:
        """pilot new creates a project with the correct top-level structure."""
        os.chdir(tmp_path)
        runner.invoke(app, ["new", "test-project", "--no-interactive"])
        project_dir = tmp_path / "test-project"
        assert project_dir.exists()
        assert (project_dir / "app").exists()
        assert (project_dir / "app" / "main.py").exists()
        assert (project_dir / "pyproject.toml").exists()

    def test_creates_core_directory(self, tmp_path: Path) -> None:
        """Generated project has all core infrastructure files."""
        os.chdir(tmp_path)
        runner.invoke(app, ["new", "test-project", "--no-interactive"])
        core_dir = tmp_path / "test-project" / "app" / "core"
        assert (core_dir / "config.py").exists()
        assert (core_dir / "database.py").exists()
        assert (core_dir / "security.py").exists()
        assert (core_dir / "exceptions.py").exists()

    def test_creates_all_layers(self, tmp_path: Path) -> None:
        """Generated project has all architectural layers as directories."""
        os.chdir(tmp_path)
        runner.invoke(app, ["new", "test-project", "--no-interactive"])
        app_dir = tmp_path / "test-project" / "app"
        for layer in ["models", "schemas", "routes", "services", "repositories"]:
            assert (app_dir / layer).is_dir(), f"Missing layer: {layer}"

    def test_creates_test_directory(self, tmp_path: Path) -> None:
        """Generated project has test infrastructure."""
        os.chdir(tmp_path)
        runner.invoke(app, ["new", "test-project", "--no-interactive"])
        tests_dir = tmp_path / "test-project" / "tests"
        assert tests_dir.is_dir()
        assert (tests_dir / "conftest.py").exists()


class TestNewCommandErrors:
    """Test error handling in `pilot new`."""

    def test_fails_if_directory_exists(self, tmp_path: Path) -> None:
        """pilot new refuses to overwrite an existing directory without --force."""
        os.chdir(tmp_path)
        (tmp_path / "existing-project").mkdir()
        result = runner.invoke(app, ["new", "existing-project", "--no-interactive"])
        assert result.exit_code == 1
        assert "already exists" in result.output

    def test_force_overwrites_existing(self, tmp_path: Path) -> None:
        """--force allows overwriting an existing directory."""
        os.chdir(tmp_path)
        (tmp_path / "my-project").mkdir()
        result = runner.invoke(
            app, ["new", "my-project", "--no-interactive", "--force"]
        )
        assert result.exit_code == 0
        assert (tmp_path / "my-project" / "app").exists()

    def test_invalid_database_option(self, tmp_path: Path) -> None:
        """--db with an unsupported value gives a clear error."""
        os.chdir(tmp_path)
        result = runner.invoke(
            app, ["new", "test-project", "--no-interactive", "--db", "mysql"]
        )
        assert result.exit_code == 1
        assert "Invalid database" in result.output


class TestNewCommandOptions:
    """Test CLI option handling for `pilot new`."""

    def test_db_option(self, tmp_path: Path) -> None:
        """--db postgresql creates migrations directory and alembic config."""
        os.chdir(tmp_path)
        result = runner.invoke(
            app, ["new", "db-project", "--no-interactive", "--db", "postgresql"]
        )
        assert result.exit_code == 0
        assert (tmp_path / "db-project" / "migrations").is_dir()
        assert (tmp_path / "db-project" / "alembic.ini").exists()

    def test_no_interactive_uses_defaults(self, tmp_path: Path) -> None:
        """--no-interactive uses default options (postgresql, uv) without prompting."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["new", "default-project", "--no-interactive"])
        assert result.exit_code == 0
        assert (tmp_path / "default-project" / "app" / "main.py").exists()
