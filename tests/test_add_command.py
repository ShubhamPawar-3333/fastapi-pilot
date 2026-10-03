"""Tests for the `pilot add` command."""

import os
from pathlib import Path

from typer.testing import CliRunner

from fastapi_pilot.cli import app

runner = CliRunner()


def _create_pilot_project(tmp_path: Path) -> Path:
    """Create a minimal pilot project for testing `pilot add`.

    Generates a real project using `pilot new` so the directory
    structure and sentinel markers are all in place.
    """
    os.chdir(tmp_path)
    result = runner.invoke(app, ["new", "test-project", "--no-interactive"])
    assert result.exit_code == 0, f"Project creation failed: {result.output}"
    return tmp_path / "test-project"


class TestAddRoute:
    """Test adding a route (generates full stack)."""

    def test_adds_all_files(self, tmp_path: Path) -> None:
        """pilot add route users creates route, schema, service, and repository."""
        project_dir = _create_pilot_project(tmp_path)
        os.chdir(project_dir)

        result = runner.invoke(app, ["add", "route", "users"])
        assert result.exit_code == 0

        app_dir = project_dir / "app"
        assert (app_dir / "routes" / "users.py").exists()
        assert (app_dir / "schemas" / "users.py").exists()
        assert (app_dir / "services" / "users.py").exists()
        assert (app_dir / "repositories" / "users.py").exists()

    def test_route_content_has_endpoints(self, tmp_path: Path) -> None:
        """Generated route file contains all CRUD endpoints."""
        project_dir = _create_pilot_project(tmp_path)
        os.chdir(project_dir)

        runner.invoke(app, ["add", "route", "products"])
        content = (project_dir / "app" / "routes" / "products.py").read_text()

        assert "list_products" in content
        assert "get_product" in content
        assert "create_product" in content
        assert "update_product" in content
        assert "delete_product" in content

    def test_route_registered_in_router(self, tmp_path: Path) -> None:
        """Route is auto-registered in app/routes/router.py."""
        project_dir = _create_pilot_project(tmp_path)
        os.chdir(project_dir)

        runner.invoke(app, ["add", "route", "users"])
        router_content = (project_dir / "app" / "routes" / "router.py").read_text()

        assert "from app.routes.users import router as users_router" in router_content
        assert "users_router" in router_content

    def test_schema_has_pydantic_models(self, tmp_path: Path) -> None:
        """Generated schema has Create, Update, and Read models."""
        project_dir = _create_pilot_project(tmp_path)
        os.chdir(project_dir)

        runner.invoke(app, ["add", "route", "orders"])
        content = (project_dir / "app" / "schemas" / "orders.py").read_text()

        assert "OrderCreate" in content
        assert "OrderUpdate" in content
        assert "OrderRead" in content

    def test_skips_existing_files(self, tmp_path: Path) -> None:
        """Re-running pilot add for the same name skips existing files."""
        project_dir = _create_pilot_project(tmp_path)
        os.chdir(project_dir)

        # First run creates files
        runner.invoke(app, ["add", "route", "users"])
        # Second run should skip without error
        result = runner.invoke(app, ["add", "route", "users"])
        assert result.exit_code == 0
        assert "Skipped" in result.output or "already" in result.output.lower()


class TestAddModel:
    """Test adding just a model."""

    def test_adds_only_model(self, tmp_path: Path) -> None:
        """pilot add model creates only the model file."""
        project_dir = _create_pilot_project(tmp_path)
        os.chdir(project_dir)

        result = runner.invoke(app, ["add", "model", "products"])
        assert result.exit_code == 0

        assert (project_dir / "app" / "models" / "products.py").exists()
        # Should NOT create route, schema, etc.
        assert not (project_dir / "app" / "routes" / "products.py").exists()
        assert not (project_dir / "app" / "schemas" / "products.py").exists()

    def test_model_has_sqlalchemy_setup(self, tmp_path: Path) -> None:
        """Generated model uses SQLAlchemy Base and mapped_column."""
        project_dir = _create_pilot_project(tmp_path)
        os.chdir(project_dir)

        runner.invoke(app, ["add", "model", "categories"])
        content = (project_dir / "app" / "models" / "categories.py").read_text()

        assert "Base" in content
        assert "mapped_column" in content
        assert "Category" in content  # Singular class name


class TestAddErrors:
    """Test error handling in `pilot add`."""

    def test_invalid_component_type(self, tmp_path: Path) -> None:
        """Unknown component type gives a clear error."""
        project_dir = _create_pilot_project(tmp_path)
        os.chdir(project_dir)

        result = runner.invoke(app, ["add", "widget", "users"])
        assert result.exit_code == 1
        assert "Unknown component type" in result.output

    def test_invalid_component_name(self, tmp_path: Path) -> None:
        """Names with special characters are rejected."""
        project_dir = _create_pilot_project(tmp_path)
        os.chdir(project_dir)

        result = runner.invoke(app, ["add", "route", "my-route!"])
        assert result.exit_code == 1

    def test_not_in_project(self, tmp_path: Path) -> None:
        """Running outside a pilot project gives a clear error."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["add", "route", "users"])
        assert result.exit_code == 1
        assert "Not inside" in result.output


class TestAddService:
    """Test adding just a service."""

    def test_adds_only_service(self, tmp_path: Path) -> None:
        """pilot add service creates only the service file."""
        project_dir = _create_pilot_project(tmp_path)
        os.chdir(project_dir)

        result = runner.invoke(app, ["add", "service", "payments"])
        assert result.exit_code == 0

        assert (project_dir / "app" / "services" / "payments.py").exists()
        assert not (project_dir / "app" / "routes" / "payments.py").exists()
