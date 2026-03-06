# Jotpad

A minimal single-note editor for Linux with live markdown formatting.

## Features

- Single persistent note — opens the same file every time
- Auto-saves when you stop typing (800ms debounce)
- Live markdown formatting (headings, bold, italic, code, links)
- Ctrl+click to open hyperlinks
- Four themes: Dark, Light, Solarized Dark, Solarized Light
- Configurable font, font size, and note storage location
- Markdown formatting can be toggled on/off
- Remembers window size and position

## Install

### From source

```sh
pip install .
```

### Arch Linux (AUR)

```sh
paru -S jotpad
```

### Fedora (COPR)

```sh
sudo dnf copr enable maxDTM/jotpad
sudo dnf install jotpad
```

### Debian/Ubuntu

```sh
sudo dpkg -i jotpad_1.0.0-1_all.deb
```

## Run

```sh
jotpad
```

Or without installing:

```sh
python -m jotpad
```

## Configuration

Stored at `~/.config/jotpad/config` in plain `key = value` format.
Respects `$XDG_CONFIG_HOME`.

See `man jotpad` for all configuration options.

## License

GPL-3.0-or-later
