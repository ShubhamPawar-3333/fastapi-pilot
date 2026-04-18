"""Configuration and path resolution for fastapi-pilot."""

from pathlib import Path

# Path resolution:
# This file lives at: src/fastapi_pilot/core/config.py
# __file__ resolves to the installed location (site-packages/fastapi_pilot/core/config.py)
# .parent = fastapi_pilot/core/
# .parent.parent = fastapi_pilot/
# So PACKAGE_DIR = the root of our installed package, regardless of where it's installed.
PACKAGE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PACKAGE_DIR / "templates"
STANDARD_TEMPLATE_DIR = TEMPLATES_DIR / "standard"

# What options we support (shown in prompts and validated against)
SUPPORTED_DATABASES = ["postgresql", "sqlite", "none"]
SUPPORTED_PACKAGE_MANAGERS = ["uv", "pip", "poetry"]
SUPPORTED_TEMPLATES = ["standard"]

# What we use when the user doesn't specify or picks --no-interactive
DEFAULT_DATABASE = "postgresql"
DEFAULT_PACKAGE_MANAGER = "uv"
DEFAULT_TEMPLATE = "standard"
DEFAULT_PYTHON_VERSION = "3.12"