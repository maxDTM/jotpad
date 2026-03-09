# Jotpad

A minimal single-note editor for Linux with live markdown formatting.

## Features

- Single persistent note — opens the same file every time
- Auto-saves when you stop typing (800ms debounce)
- Remembers window size and position (position only on X11)
- Live markdown formatting (headings, bold, italic, code, links)
- Ctrl+click to open hyperlinks
- Configurable font, font size, and note storage location

## Install

### From source

### Arch Linux (AUR)

```sh
paru -S jotpad
```

## Run

```sh
jotpad
```

Or without installing:

cd into cloned directory

```sh
python -m jotpad
```

## Configuration

Stored at `~/.config/jotpad/config` in plain `key = value` format.
Respects `$XDG_CONFIG_HOME`.

See `man jotpad` for all configuration options.

## License

GPL-3.0-or-later

---
