"""Main application window for Jotpad."""

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QHBoxLayout, QVBoxLayout,
    QWidget, QFrame, QFileDialog,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon

from jotpad.config import CONFIG_DIR, load_config, save_config
from jotpad.themes import THEMES
from jotpad.highlighter import MarkdownHighlighter
from jotpad.widgets import GearButton, NoteEditor, SettingsPanel


class JotpadWindow(QMainWindow):
    """Single-window note editor with settings panel overlay."""

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.setWindowTitle("Jotpad")
        self.setMinimumSize(400, 300)

        # Restore window geometry
        w = self.config.get("window_width", 720)
        h = self.config.get("window_height", 600)
        self.resize(w, h)
        x = self.config.get("window_x", -1)
        y = self.config.get("window_y", -1)
        if x >= 0 and y >= 0:
            self.move(x, y)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Editor container
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)

        self.editor = NoteEditor()
        self.editor.setFrameShape(QFrame.NoFrame)
        editor_layout.addWidget(self.editor)
        main_layout.addWidget(editor_container, 1)

        # Settings panel
        self.settings_panel = SettingsPanel(self.config)
        self.settings_panel.settings_changed.connect(self._on_settings_changed)
        main_layout.addWidget(self.settings_panel)

        # Gear button overlay
        self.gear_btn = GearButton(parent=self.editor)
        self.gear_btn.clicked.connect(self._toggle_settings)

        # Markdown highlighter
        theme = THEMES[self.config.get("theme", "dark")]
        self.highlighter = MarkdownHighlighter(
            self.editor.document(),
            theme,
            enabled=self.config.get("markdown_enabled", True),
        )

        # Auto-save with 800ms debounce
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(800)
        self.save_timer.timeout.connect(self._save_note)
        self.editor.textChanged.connect(self._on_text_changed)

        self._apply_theme()

        # First run: ask for file location
        if not self.config.get("note_path"):
            QTimer.singleShot(200, self._first_run_dialog)
        else:
            self._load_note()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.gear_btn.move(self.editor.width() - 44, 10)

    def closeEvent(self, event):
        self.config["window_width"] = self.width()
        self.config["window_height"] = self.height()
        self.config["window_x"] = self.x()
        self.config["window_y"] = self.y()
        save_config(self.config)
        self._save_note()
        super().closeEvent(event)

    def _first_run_dialog(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Choose where to save your note",
            str(Path.home() / "note.md"),
            "Markdown (*.md);;Text files (*.txt);;All files (*)",
        )
        if path:
            self.config["note_path"] = path
            save_config(self.config)
            if Path(path).exists():
                self._load_note()
        else:
            default_path = CONFIG_DIR / "note.md"
            self.config["note_path"] = str(default_path)
            save_config(self.config)
            if default_path.exists():
                self._load_note()

    def _load_note(self):
        path = self.config.get("note_path", "")
        if path and Path(path).exists():
            try:
                content = Path(path).read_text(encoding="utf-8")
                self.editor.blockSignals(True)
                self.editor.setPlainText(content)
                self.editor.blockSignals(False)
            except Exception:
                pass

    def _save_note(self):
        path = self.config.get("note_path", "")
        if path:
            try:
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                Path(path).write_text(
                    self.editor.toPlainText(), encoding="utf-8"
                )
            except Exception:
                pass

    def _on_text_changed(self):
        self.save_timer.start()

    def _toggle_settings(self):
        self.settings_panel.setVisible(not self.settings_panel.isVisible())

    def _on_settings_changed(self):
        self._apply_theme()
        self._load_note()

    def _apply_theme(self):
        theme_name = self.config.get("theme", "dark")
        t = THEMES.get(theme_name, THEMES["dark"])
        font_family = self.config.get("font_family", "monospace")
        font_size = self.config.get("font_size", 14)

        self.setStyleSheet(f"QMainWindow {{ background: {t['bg']}; }}")

        self.editor.setStyleSheet(f"""
            QTextEdit {{
                background: {t['bg']};
                color: {t['text']};
                selection-background-color: {t['highlight']};
                border: none;
                padding: 24px 32px;
                font-family: '{font_family}';
                font-size: {font_size}px;
            }}
            QScrollBar:vertical {{
                background: {t['bg']};
                width: 8px;
                border-radius: 4px;
                margin: 4px 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {t['scrollbar']};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {t['scrollbar_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

        font = QFont(font_family, font_size)
        self.editor.setFont(font)
        self.editor.document().setDefaultFont(font)

        self.gear_btn.set_color(t["muted"])
        self.settings_panel.apply_theme(t)
        self.highlighter.set_theme(t)
        self.highlighter.set_enabled(self.config.get("markdown_enabled", True))


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Jotpad")
    app.setApplicationDisplayName("Jotpad")
    app.setDesktopFileName("com.jotpad.Jotpad")

    window = JotpadWindow()
    window.show()
    sys.exit(app.exec())
