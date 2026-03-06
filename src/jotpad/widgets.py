"""Custom widgets for Jotpad."""

import math
import re
from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import (
    QColor,
    QDesktopServices,
    QFont,
    QFontDatabase,
    QPainter,
    QPen,
)

from jotpad.config import save_config
from jotpad.themes import THEME_DISPLAY_NAMES


class GearButton(QPushButton):
    """Settings gear icon button rendered via QPainter."""

    def __init__(self, color="#6c7086", parent=None):
        super().__init__(parent)
        self.setFixedSize(32, 32)
        self.setCursor(Qt.PointingHandCursor)
        self._color = color
        self.setStyleSheet("background: transparent; border: none;")

    def set_color(self, color):
        self._color = color
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(self._color), 1.6)
        p.setPen(pen)

        cx, cy = 16, 16
        r = 5.5
        teeth = 8
        outer_r = 11
        inner_r = 8.5

        for i in range(teeth):
            a1 = (i * 360 / teeth) * math.pi / 180
            a2 = ((i + 0.4) * 360 / teeth) * math.pi / 180
            a3 = ((i + 0.5) * 360 / teeth) * math.pi / 180
            a4 = ((i + 0.9) * 360 / teeth) * math.pi / 180
            p.drawLine(
                int(cx + inner_r * math.cos(a1)),
                int(cy + inner_r * math.sin(a1)),
                int(cx + outer_r * math.cos(a2)),
                int(cy + outer_r * math.sin(a2)),
            )
            p.drawLine(
                int(cx + outer_r * math.cos(a2)),
                int(cy + outer_r * math.sin(a2)),
                int(cx + outer_r * math.cos(a3)),
                int(cy + outer_r * math.sin(a3)),
            )
            p.drawLine(
                int(cx + outer_r * math.cos(a3)),
                int(cy + outer_r * math.sin(a3)),
                int(cx + inner_r * math.cos(a4)),
                int(cy + inner_r * math.sin(a4)),
            )

        p.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
        p.end()


class SettingsPanel(QFrame):
    """Slide-out settings panel."""

    settings_changed = Signal()

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setFixedWidth(280)
        self.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        title = QLabel("Settings")
        title.setObjectName("settings_title")
        title.setStyleSheet("font-size: 15px; font-weight: 600;")
        layout.addWidget(title)

        # Theme
        layout.addWidget(QLabel("Theme"))
        self.theme_combo = QComboBox()
        for key, name in THEME_DISPLAY_NAMES.items():
            self.theme_combo.addItem(name, key)
        idx = list(THEME_DISPLAY_NAMES.keys()).index(config.get("theme", "dark"))
        self.theme_combo.setCurrentIndex(idx)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_change)
        layout.addWidget(self.theme_combo)

        # Font family
        layout.addWidget(QLabel("Font"))
        self.font_combo = QComboBox()
        self.font_combo.setEditable(True)
        for fam in sorted(QFontDatabase.families()):
            self.font_combo.addItem(fam)
        current_font = config.get("font_family", "monospace")
        idx = self.font_combo.findText(current_font, Qt.MatchFixedString)
        if idx >= 0:
            self.font_combo.setCurrentIndex(idx)
        else:
            self.font_combo.setEditText(current_font)
        self.font_combo.currentTextChanged.connect(self._on_font_change)
        layout.addWidget(self.font_combo)

        # Font size
        layout.addWidget(QLabel("Font Size"))
        self.size_combo = QComboBox()
        sizes = [10, 11, 12, 13, 14, 16, 18, 20, 24, 28, 32]
        for s in sizes:
            self.size_combo.addItem(str(s), s)
        current_size = config.get("font_size", 14)
        idx = sizes.index(current_size) if current_size in sizes else 4
        self.size_combo.setCurrentIndex(idx)
        self.size_combo.currentIndexChanged.connect(self._on_size_change)
        layout.addWidget(self.size_combo)

        # Markdown toggle
        layout.addWidget(QLabel("Markdown Formatting"))
        self.md_combo = QComboBox()
        self.md_combo.addItem("Enabled", True)
        self.md_combo.addItem("Disabled", False)
        self.md_combo.setCurrentIndex(0 if config.get("markdown_enabled", True) else 1)
        self.md_combo.currentIndexChanged.connect(self._on_md_change)
        layout.addWidget(self.md_combo)

        # Storage location
        layout.addWidget(QLabel("Note Location"))
        self.storage_btn = QPushButton("Change...")
        self.storage_btn.setCursor(Qt.PointingHandCursor)
        self.storage_btn.clicked.connect(self._on_change_storage)
        layout.addWidget(self.storage_btn)

        self.storage_label = QLabel()
        self.storage_label.setWordWrap(True)
        self.storage_label.setStyleSheet("font-size: 11px;")
        self._update_storage_label()
        layout.addWidget(self.storage_label)

        layout.addStretch()

    def _update_storage_label(self):
        p = self.config.get("note_path", "")
        display = p if len(p) < 40 else "..." + p[-37:]
        self.storage_label.setText(display)

    def _on_theme_change(self, idx):
        self.config["theme"] = self.theme_combo.currentData()
        save_config(self.config)
        self.settings_changed.emit()

    def _on_font_change(self, text):
        self.config["font_family"] = text
        save_config(self.config)
        self.settings_changed.emit()

    def _on_size_change(self, idx):
        self.config["font_size"] = self.size_combo.currentData()
        save_config(self.config)
        self.settings_changed.emit()

    def _on_md_change(self, idx):
        self.config["markdown_enabled"] = self.md_combo.currentData()
        save_config(self.config)
        self.settings_changed.emit()

    def _on_change_storage(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Choose note file location",
            self.config.get("note_path", str(Path.home())),
            "Text files (*.txt *.md);;All files (*)",
        )
        if path:
            old_path = self.config.get("note_path", "")
            if old_path and Path(old_path).exists():
                try:
                    content = Path(old_path).read_text()
                    Path(path).write_text(content)
                except Exception:
                    pass
            self.config["note_path"] = path
            save_config(self.config)
            self._update_storage_label()
            self.settings_changed.emit()

    def apply_theme(self, theme):
        t = theme
        self.setStyleSheet(f"""
            SettingsPanel {{
                background: {t['surface']};
                border-left: 1px solid {t['border']};
                border-radius: 3px;
            }}
            QLabel {{
                color: {t['muted']};
                font-size: 12px;
                background: transparent;
            }}
            QComboBox {{
                background: {t['surface2']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 13px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox QAbstractItemView {{
                background: {t['surface']};
                color: {t['text']};
                border: 1px solid {t['border']};
                selection-background-color: {t['highlight']};
            }}
            QPushButton {{
                background: {t['surface2']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {t['highlight']};
            }}
        """)
        title = self.findChild(QLabel, "settings_title")
        if title:
            title.setStyleSheet(
                f"font-size: 15px; font-weight: 600; color: {t['text']}; background: transparent;"
            )


class NoteEditor(QTextEdit):
    """Plain-text editor with Ctrl+click link opening."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptRichText(False)
        self.setLineWrapMode(QTextEdit.WidgetWidth)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier:
            cursor = self.cursorForPosition(event.pos())
            text = cursor.block().text()
            pos = cursor.positionInBlock()

            # Markdown links [text](url)
            for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
                if m.start() <= pos <= m.end():
                    QDesktopServices.openUrl(QUrl(m.group(2)))
                    return

            # Bare URLs
            for m in re.finditer(r"https?://[^\s\)\]>]+", text):
                if m.start() <= pos <= m.end():
                    QDesktopServices.openUrl(QUrl(m.group(0)))
                    return

        super().mousePressEvent(event)
