"""Project name and component name validation utilities."""

import keyword
import re

# Valid project name: starts with a letter, allows letters/digits/hyphens/_
PROJECT_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")

# Valid component name: simple identifier (letters, digits, underscores), no hyphens
COMPONENT_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")


def validate_project_name(name: str) -> str | None:
    """Validate a project name.

    Returns None if valid, or an error message string if invalid.
    """
    if not name:
        return "Project name cannot be empty."

    if len(name) > 100:
        return "Project name is too long (max 100 characters)."

    if not PROJECT_NAME_PATTERN.match(name):
        return (
            f"Invalid project name '{name}'. "
            "Must start with a letter and contain only letters, digits, "
            "hyphens, and underscores."
        )

    # Check if the slug would be a Python keyword
    slug = name.replace("-", "_").replace(" ", "_").lower()
    if keyword.iskeyword(slug):
        return f"Project name '{name}' conflicts with Python keyword '{slug}'."

    return None


def validate_component_name(name: str, component_type: str = "component") -> str | None:
    """Validate a component name (route, model, service, etc.).

    Returns None if valid, or an error message string if invalid.
    """
    if not name:
        return f"{component_type.capitalize()} name cannot be empty."

    if not COMPONENT_NAME_PATTERN.match(name):
        return (
            f"Invalid {component_type} name '{name}'. "
            "Must start with a letter and contain only letters, digits, "
            "and underscores."
        )

    if keyword.iskeyword(name):
        return f"{component_type.capitalize()} name '{name}' is a Python keyword."

    return None


def to_slug(name: str) -> str:
    """Convert a name to a Python-safe slug (lowercase with underscores)."""
    return name.replace("-", "_").replace(" ", "_").lower()


def to_class_name(name: str) -> str:
    """Convert a name to PascalCase for class names.

    Examples:
        'users' -> 'User'
        'blog_posts' -> 'BlogPost'
        'order_items' -> 'OrderItem'
        'categories' -> 'Category'
    """
    # Split on underscores or hyphens, capitalize each part
    parts = re.split(r"[-_]", name)

    # Singularize the last part (heuristic)
    last = parts[-1]
    if last.endswith("ies") and len(last) > 3:
        # categories -> category
        parts[-1] = last[:-3] + "y"
    elif last.endswith(("shes", "ches")):
        # dishes -> dish, watches -> watch
        parts[-1] = last[:-2]
    elif last.endswith(("ses", "xes", "zes")):
        # buses -> bus, boxes -> box
        parts[-1] = last[:-2]
    elif last.endswith("s") and len(last) > 1 and not last.endswith("ss"):
        # users -> user (but don't strip 'ss' from 'class')
        parts[-1] = last[:-1]

    return "".join(part.capitalize() for part in parts)


def to_plural(name: str) -> str:
    """Simple pluralization for route paths.

    Examples:
        'user' -> 'users'
        'category' -> 'categories'
        'users' -> 'users'  (already plural)
    """
    # Already looks plural — don't double-pluralize
    # (only for longer words where the plural suffix is more reliable)
    if name.endswith("ies") and len(name) > 4:
        return name
    if name.endswith(("ses", "xes", "zes", "ches", "shes")) and len(name) > 4:
        return name
    if name.endswith("s") and len(name) > 4 and not name.endswith("ss"):
        return name

    if name.endswith("y") and not name.endswith(("ay", "ey", "iy", "oy", "uy")):
        return name[:-1] + "ies"
    if name.endswith(("s", "x", "z", "ch", "sh")):
        return name + "es"
    return name + "s"
