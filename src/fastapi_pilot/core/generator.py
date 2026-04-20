"""Project generation engine using Jinja2.

Walks the template directory, renders .jinja files with Jinja2,
copies everything else as-is. Replaces Copier to avoid its
mandatory git dependency.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from fastapi_pilot.core.config import STANDARD_TEMPLATE_DIR
from fastapi_pilot.core.console import console

# Files/dirs that need special handling during copy
RENAME_MAP = {"_gitignore": ".gitignore"}
SKIP_FILES = {"copier.yml"}


def generate_project(
    project_name: str,
    project_path: Path,
    database: str,
    package_manager: str,
) -> None:
    """Generate a new FastAPI project from the standard template.

    This function does three things:
    1. Renders the template into project_path
    2. Installs dependencies with the chosen package manager
    3. Initializes a git repo with an initial commit

    Steps 2 and 3 are non-fatal - if they fail, the project
    still exists, the user just needs to run them manually.
    """
    template_data = {
        "project_name": project_name,
        "project_slug": project_name.replace("-", "_").replace(" ", "_").lower(),
        "project_description": "A FastAPI project created with pilot",
        "author_name": "Developer",
        "author_email": "dev@example.com",
        "database": database,
        "package_manager": package_manager,
    }

    _render_template(STANDARD_TEMPLATE_DIR, project_path, template_data)

    # Post-generation hooks
    _install_dependencies(project_path, package_manager)
    _init_git(project_path)


def _render_template(
    template_dir: Path,
    output_dir: Path,
    data: dict[str, str],
) -> None:
    """Walk template_dir, render .jinja files, copy the rest.

    - .jinja files: rendered with Jinja2, written without .jinja extension
    - _gitignore: copied as .gitignore (git ignores dotfiles in templates)
    - copier.yml: skipped (legacy config, not needed)
    - everything else: copied as-is
    """
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        keep_trailing_newline=True,  # preserve trailing newlines in templates
    )

    for source_path in template_dir.rglob("*"):
        if source_path.is_dir():
            continue

        # Get the relative path from template root
        rel_path = source_path.relative_to(template_dir)
        filename = rel_path.name

        # Skip files we don't want in the output
        if filename in SKIP_FILES:
            continue

        # Determine the output path
        if filename in RENAME_MAP:
            # _gitignore -> .gitignore
            dest = output_dir / rel_path.parent / RENAME_MAP[filename]
        elif filename.endswith(".jinja"):
            # config.py.jinja -> config.py
            dest = output_dir / rel_path.parent / filename.removesuffix(".jinja")
        else:
            dest = output_dir / rel_path

        # Create parent directories
        dest.parent.mkdir(parents=True, exist_ok=True)

        if filename.endswith(".jinja"):
            # Render with Jinja2
            template = env.get_template(str(rel_path.as_posix()))
            rendered = template.render(**data)
            dest.write_text(rendered, encoding="utf-8")
        else:
            # Copy as-is (binary-safe)
            shutil.copy2(source_path, dest)


def _install_dependencies(project_path: Path, package_manager: str) -> None:
    """Run the package manager's install command.

    Non-fatal: prints a warning if the tool isn't installed or fails.
    The generated project is still usable - user just needs to install manually.
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
            f"[warning]{package_manager} not found on PATH. "
            "Install dependencies manually.[/warning]"
        )
    except subprocess.CalledProcessError as e:
        console.print(
            f"[warning]{package_manager} install failed "
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
        console.print("[warning]git not found on PATH. Skipping repo init.[/warning]")
    except subprocess.CalledProcessError:
        console.print("[warning]git init/commit failed. Initialize manually.[/warning]")
