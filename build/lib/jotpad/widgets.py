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
    QLineEdit,
)
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import (
    QColor,
    QDesktopServices,
    QFont,
    QFontDatabase,
    QPainter,
    QPen,
    QKeySequence,
)

from jotpad.config import save_config
from jotpad.themes import load_themes, get_display_names

class GearButton(QPushButton):
    """Settings gear icon button rendered via QPainter."""

    def __init__(self, color="#6c7086", parent=None):
        super().__init__(parent)
        self.setFixedSize(32, 32)
        self.setCursor(Qt.PointingHandCursor)
        self._color = color
        self.setStyleSheet("background: transparent; border: none;")

    def set_color(self, color, opacity=1.0):
        self._color = color
        self._opacity = opacity
        self.update()

    def enterEvent(self, event):
        self._opacity = 1.0
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self._opacity = 0.3
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        color = QColor(self._color)
        color.setAlphaF(self._opacity)
        pen = QPen(color, 1.6)
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


class ShortcutEdit(QLineEdit):
    """Click and press keys to record a shortcut."""

    def __init__(self, shortcut_str="", parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setAlignment(Qt.AlignCenter)
        self._shortcut = shortcut_str
        self.setText(shortcut_str)
        self._recording = False

    def mousePressEvent(self, event):
        self._recording = True
        self.setText("Press keys...")
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if not self._recording:
            return
        key = event.key()
        if key in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
            return
        modifiers = event.modifiers()
        seq = QKeySequence(modifiers.value | key)
        self._shortcut = seq.toString()
        self.setText(self._shortcut)
        self._recording = False
        self.editingFinished.emit()
        self.clearFocus()

    def focusOutEvent(self, event):
        if self._recording:
            self._recording = False
            self.setText(self._shortcut)
        super().focusOutEvent(event)

    def shortcut(self):
        return self._shortcut


class SettingsPanel(QFrame):
    """Slide-out settings panel."""

    settings_changed = Signal()

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
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
        self._populate_themes(load_themes())
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
        layout.addWidget(QLabel("Auto-Detect Markdown"))
        self.md_toggle = QPushButton()
        self.md_toggle.setCursor(Qt.PointingHandCursor)
        self._update_md_toggle()
        self.md_toggle.clicked.connect(self._on_md_toggle)
        layout.addWidget(self.md_toggle)

        # Visual Separation Between Formatting and Functionality Settings
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        # Storage location
        layout.addWidget(QLabel("Note Location"))
        self.storage_btn = QPushButton()
        self.storage_btn.setCursor(Qt.PointingHandCursor)
        self.storage_btn.setStyleSheet("text-align: right; padding: 6px 10px;")
        self.storage_btn.clicked.connect(self._on_change_storage)
        self._update_storage_label()
        layout.addWidget(self.storage_btn)

        # Settings Shortcut
        layout.addWidget(QLabel("Settings Shortcut"))
        self.shortcut_edit = ShortcutEdit(config.get("settings_shortcut", "Ctrl+`"))
        self.shortcut_edit.editingFinished.connect(self._on_shortcut_change)
        layout.addWidget(self.shortcut_edit)

        # Quit Program Shortcut
        layout.addWidget(QLabel("Quit Shortcut"))
        self.quit_shortcut_edit = ShortcutEdit(config.get("quit_shortcut", "Ctrl+Q"))
        self.quit_shortcut_edit.editingFinished.connect(self._on_quit_shortcut_change)
        layout.addWidget(self.quit_shortcut_edit)

        layout.addStretch()

    def _update_storage_label(self):
        p = self.config.get("note_path", "")
        metrics = self.storage_btn.fontMetrics()
        available = self.storage_btn.width() - 24
        if available < 50:
            available = 220
        elided = metrics.elidedText(p, Qt.ElideLeft, available)
        self.storage_btn.setText(elided)
        self.storage_btn.setToolTip(p)

    def _populate_themes(self, themes):
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        display = get_display_names(themes)
        for slug, name in display.items():
            self.theme_combo.addItem(name, slug)
        current = self.config.get("theme", "dark")
        idx = self.theme_combo.findData(current)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        self.theme_combo.blockSignals(False)

    def refresh_themes(self, themes):
        self._populate_themes(themes)

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

    def _on_md_toggle(self):
        self.config["markdown_enabled"] = not self.config.get("markdown_enabled", True)
        save_config(self.config)
        self._update_md_toggle()
        self.settings_changed.emit()
    
    def _update_md_toggle(self):
        if self.config.get("markdown_enabled", True):
            self.md_toggle.setText("Disable")
        else:
            self.md_toggle.setText("Enable")

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
                    Path(old_path).unlink()
                except Exception:
                    pass
            self.config["note_path"] = path
            save_config(self.config)
            self._update_storage_label()
            self.settings_changed.emit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_storage_label()

    def _on_shortcut_change(self):
        self.config["settings_shortcut"] = self.shortcut_edit.shortcut()
        save_config(self.config)
        self.settings_changed.emit()

    def _on_quit_shortcut_change(self):
        self.config["quit_shortcut"] = self.quit_shortcut_edit.shortcut()
        save_config(self.config)
        self.settings_changed.emit()

    def apply_theme(self, theme):
        t = theme
        self.setStyleSheet(f"""
            SettingsPanel {{
                background: {t['surface']};
                border-left: 1px solid {t['border']};
                border-radius: 3px;
            }}
            QFrame[frameShape="4"] {{
                background: {t['border']};
                border: none;
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
            ShortcutEdit {{
                background: {t['surface2']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 13px;
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
