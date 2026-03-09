"""Configuration management for Jotpad.

Config is stored at $XDG_CONFIG_HOME/jotpad/config (default ~/.config/jotpad/config)
in plain key = value format following Unix conventions.
"""

import os
from pathlib import Path


CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "jotpad"
CONFIG_FILE = CONFIG_DIR / "config"


def default_config():
    """Return default configuration dictionary."""
    return {
        "theme": "dark",
        "font_family": "monospace",
        "font_size": 14,
        "note_path": "",
        "window_width": 720,
        "window_height": 600,
        "window_x": -9999,
        "window_y": -9999,
        "markdown_enabled": True,
        "settings_shortcut": "Ctrl+`",
        "quit_shortcut": "Ctrl+Q",
    }


def load_config():
    """Load configuration from disk. Returns defaults for missing keys."""
    cfg = default_config()
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip()
                        if key in cfg:
                            if isinstance(cfg[key], bool):
                                cfg[key] = val.lower() in ("true", "1", "yes")
                            elif isinstance(cfg[key], int):
                                try:
                                    cfg[key] = int(val)
                                except ValueError:
                                    pass
                            else:
                                cfg[key] = val
        except Exception:
            pass
    return cfg


def save_config(cfg):
    """Write configuration to disk in key = value format."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        f.write("# Jotpad configuration\n")
        f.write("# See jotpad(1) for details\n\n")
        for key, val in cfg.items():
            if isinstance(val, bool):
                f.write(f"{key} = {'true' if val else 'false'}\n")
            else:
                f.write(f"{key} = {val}\n")
