"""Project generation engine using Copier."""

import subprocess
import sys
from pathlib import Path

from copier import run_copy

from fastapi_pilot.core.config import STANDARD_TEMPLATE_DIR
from fastapi_pilot.core.console import console


def generate_project(
    project_name: str,
    project_path: Path,
    database: str,
    package_manager: str,
) -> None:
    """Generate a new FastAPI project from the standard template.

    This function does three things:
    1. Renders the Copier template into project_path
    2. Installs dependencies with the chosen package manager
    3. Initializes a git repo with an initial commit

    Steps 2 and 3 are non-fatal — if they fail, the project
    still exists, the user just needs to run them manually.
    """
    # These variables get injected into .jinja template files.
    # For example, {{ project_name }} in main.py.jinja becomes "my-api".
    template_data = {
        "project_name": project_name,
        "project_slug": project_name.replace("-", "_").replace(" ", "_").lower(),
        "project_description": "A FastAPI project created with pilot",
        "author_name": "Developer",
        "author_email": "dev@example.com",
        "database": database,
        "package_manager": package_manager,
    }

    # Copier reads copier.yml, finds all .jinja files, renders them,
    # and writes the output (without .jinja extension) to project_path.
    # Non-.jinja files are copied as-is.
    run_copy(
        src_path=str(STANDARD_TEMPLATE_DIR),
        dst_path=str(project_path),
        data=template_data,
        defaults=True,    # don't prompt for template questions (we already answered them)
        overwrite=True,    # overwrite files if they exist
        unsafe=True,       # allow local template paths (not just git URLs)
    )

    # Post-generation hooks
    _install_dependencies(project_path, package_manager)
    _init_git(project_path)


def _install_dependencies(project_path: Path, package_manager: str) -> None:
    """Run the package manager's install command.

    Non-fatal: prints a warning if the tool isn't installed or fails.
    The generated project is still usable — user just needs to install manually.
    """
    cmds: dict[str, list[str]] = {
        "uv": ["uv", "sync"],
        "pip": [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
        "poetry": ["poetry", "install"],
    }
    cmd = cmds.get(package_manager)
    if not cmd:
        return

    try:
        subprocess.run(cmd, cwd=project_path, check=True, capture_output=True)
    except FileNotFoundError:
        console.print(
            f"[warning]⚠️  {package_manager} not found on PATH. "
            "Install dependencies manually.[/warning]"
        )
    except subprocess.CalledProcessError as e:
        console.print(
            f"[warning]⚠️  {package_manager} install failed "
            f"(exit code {e.returncode}). Run it manually.[/warning]"
        )


def _init_git(project_path: Path) -> None:
    """Initialize a git repo in the generated project.

    Creates an initial commit so the user starts with a clean working tree.
    Non-fatal: if git isn't installed, skip silently with a warning.
    """
    try:
        subprocess.run(
            ["git", "init"], cwd=project_path, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "add", "."], cwd=project_path, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit from fastapi-pilot"],
            cwd=project_path,
            check=True,
            capture_output=True,
        )
    except FileNotFoundError:
        console.print(
            "[warning]⚠️  git not found on PATH. Skipping repo init.[/warning]"
        )
    except subprocess.CalledProcessError:
        console.print(
            "[warning]⚠️  git init/commit failed. Initialize manually.[/warning]"
        )