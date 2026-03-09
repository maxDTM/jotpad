"""Live markdown syntax highlighter for Jotpad."""

import re

from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont


class MarkdownHighlighter(QSyntaxHighlighter):
    """Highlights markdown syntax inline while keeping source visible."""

    def __init__(self, parent, theme, enabled=True):
        super().__init__(parent)
        self.theme = theme
        self.enabled = enabled
        self._build_formats()

    def _build_formats(self):
        t = self.theme

        self.fmt_h1 = QTextCharFormat()
        self.fmt_h1.setFontPointSize(28)
        self.fmt_h1.setFontWeight(QFont.Bold)
        self.fmt_h1.setForeground(QColor(t["heading1"]))

        self.fmt_h2 = QTextCharFormat()
        self.fmt_h2.setFontPointSize(22)
        self.fmt_h2.setFontWeight(QFont.Bold)
        self.fmt_h2.setForeground(QColor(t["heading2"]))

        self.fmt_h3 = QTextCharFormat()
        self.fmt_h3.setFontPointSize(18)
        self.fmt_h3.setFontWeight(QFont.Bold)
        self.fmt_h3.setForeground(QColor(t["heading3"]))

        self.fmt_h4 = QTextCharFormat()
        self.fmt_h4.setFontPointSize(16)
        self.fmt_h4.setFontWeight(QFont.DemiBold)
        self.fmt_h4.setForeground(QColor(t["heading3"]))

        self.fmt_bold = QTextCharFormat()
        self.fmt_bold.setFontWeight(QFont.Bold)
        self.fmt_bold.setForeground(QColor(t["bold"]))

        self.fmt_italic = QTextCharFormat()
        self.fmt_italic.setFontItalic(True)
        self.fmt_italic.setForeground(QColor(t["italic"]))

        self.fmt_bold_italic = QTextCharFormat()
        self.fmt_bold_italic.setFontWeight(QFont.Bold)
        self.fmt_bold_italic.setFontItalic(True)
        self.fmt_bold_italic.setForeground(QColor(t["bold"]))

        self.fmt_code = QTextCharFormat()
        self.fmt_code.setFontFamily("monospace")
        self.fmt_code.setForeground(QColor(t["code"]))
        self.fmt_code.setBackground(QColor(t["code_bg"]))

        self.fmt_link = QTextCharFormat()
        self.fmt_link.setForeground(QColor(t["hyperlink"]))
        self.fmt_link.setFontUnderline(True)

        self.fmt_syntax = QTextCharFormat()
        self.fmt_syntax.setForeground(QColor(t["md_syntax"]))

        self.fmt_url = QTextCharFormat()
        self.fmt_url.setForeground(QColor(t["hyperlink"]))
        self.fmt_url.setFontUnderline(True)

    def set_theme(self, theme):
        self.theme = theme
        self._build_formats()
        self.rehighlight()

    def set_enabled(self, enabled):
        self.enabled = enabled
        self.rehighlight()

    def highlightBlock(self, text):
        # Always highlight URLs regardless of markdown toggle
        self._highlight_urls(text)

        if not self.enabled:
            return

        # Headings: # through ####
        heading_match = re.match(r"^(#{1,4})\s", text)
        if heading_match:
            level = len(heading_match.group(1))
            fmt_map = {1: self.fmt_h1, 2: self.fmt_h2, 3: self.fmt_h3, 4: self.fmt_h4}
            hfmt = fmt_map.get(level, self.fmt_h4)
            self.setFormat(0, len(heading_match.group(1)), self.fmt_syntax)
            self.setFormat(
                len(heading_match.group(0)),
                len(text) - len(heading_match.group(0)),
                hfmt,
            )
            return

        # Bold+italic ***text***
        for m in re.finditer(r"(\*{3})(.+?)\1", text):
            self.setFormat(m.start(), 3, self.fmt_syntax)
            self.setFormat(m.start() + 3, len(m.group(2)), self.fmt_bold_italic)
            self.setFormat(m.end() - 3, 3, self.fmt_syntax)

        # Bold **text**
        for m in re.finditer(r"(\*{2})(.+?)\1", text):
            self.setFormat(m.start(), 2, self.fmt_syntax)
            self.setFormat(m.start() + 2, len(m.group(2)), self.fmt_bold)
            self.setFormat(m.end() - 2, 2, self.fmt_syntax)

        # Italic *text*
        for m in re.finditer(r"(?<!\*)(\*)(?!\*)(.+?)(?<!\*)\1(?!\*)", text):
            self.setFormat(m.start(), 1, self.fmt_syntax)
            self.setFormat(m.start() + 1, len(m.group(2)), self.fmt_italic)
            self.setFormat(m.end() - 1, 1, self.fmt_syntax)

        # Inline code `text`
        for m in re.finditer(r"(`+)(.+?)\1", text):
            self.setFormat(m.start(), len(m.group(1)), self.fmt_syntax)
            self.setFormat(m.start() + len(m.group(1)), len(m.group(2)), self.fmt_code)
            self.setFormat(m.end() - len(m.group(1)), len(m.group(1)), self.fmt_syntax)

        # Markdown links [text](url)
        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
            self.setFormat(m.start(), 1, self.fmt_syntax)
            self.setFormat(m.start() + 1, len(m.group(1)), self.fmt_link)
            self.setFormat(m.start() + 1 + len(m.group(1)), 2, self.fmt_syntax)
            self.setFormat(
                m.start() + 1 + len(m.group(1)) + 2, len(m.group(2)), self.fmt_url
            )
            self.setFormat(m.end() - 1, 1, self.fmt_syntax)

    def _highlight_urls(self, text):
        for m in re.finditer(r"https?://[^\s\)\]>]+", text):
            self.setFormat(m.start(), m.end() - m.start(), self.fmt_url)
