"""Rich console configuration for consistent terminal output."""

from rich.console import Console
from rich.theme import Theme

pilot_theme = Theme(
    {
        "info": "cyan",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "heading": "bold magenta",
        "path": "dim cyan",
        "command": "bold white on dark_green",
    }
)

# These are singletons — import them wherever you need terminal output.
# Use `console` for normal output, `error_console` for errors (goes to stderr).
console = Console(theme=pilot_theme)
error_console = Console(stderr=True, theme=pilot_theme)
