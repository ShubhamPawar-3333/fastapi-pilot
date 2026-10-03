"""Tests for addon support (--with docker) in `pilot new`."""

import os
from pathlib import Path

from typer.testing import CliRunner

from fastapi_pilot.cli import app

runner = CliRunner()


class TestDockerAddon:
    """Test the --with docker addon."""

    def test_creates_dockerfile(self, tmp_path: Path) -> None:
        """--with docker creates a Dockerfile."""
        os.chdir(tmp_path)
        result = runner.invoke(
            app, ["new", "docker-project", "--no-interactive", "--with", "docker"]
        )
        assert result.exit_code == 0
        assert (tmp_path / "docker-project" / "Dockerfile").exists()

    def test_creates_docker_compose(self, tmp_path: Path) -> None:
        """--with docker creates a docker-compose.yml."""
        os.chdir(tmp_path)
        result = runner.invoke(
            app, ["new", "docker-project", "--no-interactive", "--with", "docker"]
        )
        assert result.exit_code == 0
        assert (tmp_path / "docker-project" / "docker-compose.yml").exists()

    def test_creates_dockerignore(self, tmp_path: Path) -> None:
        """--with docker creates a .dockerignore."""
        os.chdir(tmp_path)
        result = runner.invoke(
            app, ["new", "docker-project", "--no-interactive", "--with", "docker"]
        )
        assert result.exit_code == 0
        assert (tmp_path / "docker-project" / ".dockerignore").exists()

    def test_compose_has_postgres(self, tmp_path: Path) -> None:
        """docker-compose.yml includes PostgreSQL when --db postgresql."""
        os.chdir(tmp_path)
        runner.invoke(
            app,
            [
                "new",
                "pg-project",
                "--no-interactive",
                "--db",
                "postgresql",
                "--with",
                "docker",
            ],
        )
        compose = (tmp_path / "pg-project" / "docker-compose.yml").read_text()
        assert "postgres" in compose
        assert "pgdata" in compose

    def test_compose_no_postgres_for_sqlite(self, tmp_path: Path) -> None:
        """docker-compose.yml does not include PostgreSQL for SQLite projects."""
        os.chdir(tmp_path)
        runner.invoke(
            app,
            [
                "new",
                "sqlite-project",
                "--no-interactive",
                "--db",
                "sqlite",
                "--with",
                "docker",
            ],
        )
        compose = (tmp_path / "sqlite-project" / "docker-compose.yml").read_text()
        assert "postgres" not in compose

    def test_next_steps_mentions_docker(self, tmp_path: Path) -> None:
        """Success output mentions docker compose when addon is used."""
        os.chdir(tmp_path)
        result = runner.invoke(
            app, ["new", "docker-project", "--no-interactive", "--with", "docker"]
        )
        assert "docker compose" in result.output.lower()

    def test_invalid_addon_fails(self, tmp_path: Path) -> None:
        """Unknown addon gives a clear error."""
        os.chdir(tmp_path)
        result = runner.invoke(
            app, ["new", "bad-project", "--no-interactive", "--with", "kubernetes"]
        )
        assert result.exit_code == 1
        assert "Unknown addon" in result.output


class TestProjectNameValidation:
    """Test project name validation in the new command."""

    def test_rejects_name_starting_with_digit(self, tmp_path: Path) -> None:
        """Project names starting with a digit are rejected."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["new", "123project", "--no-interactive"])
        assert result.exit_code == 1
        assert "Must start with a letter" in result.output

    def test_rejects_python_keyword(self, tmp_path: Path) -> None:
        """Project names that are Python keywords are rejected."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["new", "class", "--no-interactive"])
        assert result.exit_code == 1
        assert "keyword" in result.output.lower()
