"""Theme loading for Jotpad.

System themes: /usr/share/jotpad/themes/
User themes:   ~/.config/jotpad/themes/
User themes override system themes with the same filename.
"""

import os
from pathlib import Path

SYSTEM_THEMES_DIR = Path("/usr/share/jotpad/themes")
USER_THEMES_DIR = Path(
    os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
) / "jotpad" / "themes"

# Fallback theme used if no theme files are found
FALLBACK_THEME = {
    "name": "Dark",
    "bg": "#1e1e2e",
    "text": "#cdd6f4",
    "highlight": "#45475a",
    "hyperlink": "#89b4fa",
    "md_syntax": "#585b70",
    "surface": "#181825",
    "surface2": "#313244",
    "border": "#45475a",
    "accent": "#89b4fa",
    "muted": "#6c7086",
    "heading1": "#cdd6f4",
    "heading2": "#bac2de",
    "heading3": "#a6adc8",
    "bold": "#f5e0dc",
    "italic": "#f2cdcd",
    "code": "#a6e3a1",
    "code_bg": "#1e1e2e",
    "scrollbar": "#45475a",
    "scrollbar_hover": "#585b70",
}


def _parse_theme_file(path):
    """Parse a theme .conf file into a dict."""
    theme = {}
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    theme[key.strip()] = val.strip()
    except Exception:
        return None
    return theme


def load_themes():
    """Load all themes. Returns dict of {slug: theme_dict}.

    User themes override system themes with the same filename.
    """
    themes = {}

    # Load system themes first
    if SYSTEM_THEMES_DIR.is_dir():
        for f in sorted(SYSTEM_THEMES_DIR.glob("*.conf")):
            slug = f.stem
            theme = _parse_theme_file(f)
            if theme:
                themes[slug] = theme

    # User themes override
    if USER_THEMES_DIR.is_dir():
        for f in sorted(USER_THEMES_DIR.glob("*.conf")):
            slug = f.stem
            theme = _parse_theme_file(f)
            if theme:
                themes[slug] = theme

    # Fallback if nothing loaded
    if not themes:
        themes["dark"] = FALLBACK_THEME.copy()

    return themes


def get_theme(themes, name):
    """Get a theme by slug, falling back to first available."""
    if name in themes:
        return themes[name]
    return next(iter(themes.values()))


def get_display_names(themes):
    """Return dict of {slug: display_name} for all loaded themes."""
    return {slug: t.get("name", slug) for slug, t in themes.items()}