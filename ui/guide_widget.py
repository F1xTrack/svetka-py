from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QDialog,
    QScrollArea,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtProperty
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont


class GuideIcon(QPushButton):
    clicked_for_help = pyqtSignal(str)

    def __init__(self, guide_key: str, parent=None):
        super().__init__(parent)
        self.guide_key = guide_key
        self.setFixedSize(20, 20)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click for help")
        self.clicked.connect(self._on_click)

    def _on_click(self):
        self.clicked_for_help.emit(self.guide_key)


class InlineGuideLabel(QLabel):
    def __init__(self, text: str = "", parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setStyleSheet("color: #888; font-size: 11px;")
        self.setWordWrap(True)


class GuideTooltip(QLabel):
    def __init__(self, title: str = "", content: str = "", parent=None):
        super().__init__(parent)
        self._title = title
        self._content = content
        self._setup_style()

    def _setup_style(self):
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setTextFormat(Qt.TextFormat.RichText)
        self._update_content()

    def _update_content(self):
        html = f"""
        <div style="
            background-color: #2b2b2b;
            border: 1px solid #555;
            border-radius: 6px;
            padding: 12px;
            max-width: 350px;
        ">
            <b style="color: #4a9eff; font-size: 14px;">{self._title}</b>
            <hr style="border: 0; border-top: 1px solid #444; margin: 8px 0;">
            <p style="color: #ddd; font-size: 12px; margin: 0;">{self._content}</p>
        </div>
        """
        self.setText(html)

    def set_content(self, title: str, content: str):
        self._title = title
        self._content = content
        self._update_content()

    def show_at(self, pos):
        self.adjustSize()
        self.move(pos.x() + 15, pos.y() + 15)
        self.show()


class GuideModal(QDialog):
    def __init__(self, guide_key: str, title: str, content: str, parent=None):
        super().__init__(parent)
        self.guide_key = guide_key
        self.setWindowTitle(title or "Help")
        self.setMinimumSize(550, 450)
        self._setup_ui(title, content)

    def _setup_ui(self, title: str, content: str):
        layout = QVBoxLayout(self)

        header = QFrame()
        header.setStyleSheet("background-color: #3a3a3a;")
        header_layout = QHBoxLayout(header)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #4a9eff; font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: #2b2b2b; }
            QScrollBar:vertical { background: #333; width: 12px; }
            QScrollBar::handle:vertical { background: #555; border-radius: 6px; }
        """)

        content_browser = QTextBrowser()
        content_browser.setOpenExternalLinks(True)
        content_browser.setStyleSheet("""
            QTextBrowser { 
                background-color: #2b2b2b; 
                color: #ddd;
                border: none;
                padding: 15px;
                font-size: 13px;
            }
        """)

        html_content = f"""
        <html>
        <body style="color: #ddd; font-family: Segoe UI, sans-serif; font-size: 13px;">
            {content}
        </body>
        </html>
        """
        content_browser.setHtml(html_content)

        scroll.setWidget(content_browser)
        layout.addWidget(scroll)

        footer = QFrame()
        footer.setStyleSheet("background-color: #3a3a3a;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                padding: 8px 24px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #5aafff; }
        """)
        close_btn.clicked.connect(self.accept)
        footer_layout.addWidget(close_btn)

        layout.addWidget(footer)


class GuideWidget(QWidget):
    help_requested = pyqtSignal(str)

    def __init__(self, guide_key: str, guide_manager, parent=None):
        super().__init__(parent)
        self.guide_key = guide_key
        self.guide_manager = guide_manager
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        guide = self.guide_manager.get_guide(self.guide_key)

        if guide and guide.inline:
            inline_label = InlineGuideLabel(guide.inline)
            layout.addWidget(inline_label)

        help_icon = GuideIcon(self.guide_key)
        help_icon.clicked_for_help.connect(self._on_help_clicked)
        layout.addWidget(help_icon)

    def _on_help_clicked(self):
        self.help_requested.emit(self.guide_key)

    def refresh(self):
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, InlineGuideLabel):
                guide = self.guide_manager.get_guide(self.guide_key)
                if guide:
                    widget.setText(guide.inline)


class GuideTourOverlay(QFrame):
    tour_complete = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.5);")
        self._steps = []
        self._current_step = 0
        self._highlight_widget = None

    def add_step(self, widget: QWidget, message: str, position: str = "bottom"):
        self._steps.append({"widget": widget, "message": message, "position": position})

    def start_tour(self):
        if not self._steps:
            return
        self._current_step = 0
        self._show_current_step()

    def _show_current_step(self):
        if self._current_step >= len(self._steps):
            self.tour_complete.emit()
            return

        step = self._steps[self._current_step]
        widget = step["widget"]

        if not widget or not widget.isVisible():
            self._current_step += 1
            self._show_current_step()
            return

        rect = widget.rect()
        global_pos = widget.mapToGlobal(rect.center())

        self._show_message_popup(step["message"], global_pos, step["position"])

    def _show_message_popup(self, message: str, pos, position: str):
        self._highlight_widget = QFrame(self.parentWidget())
        self._highlight_widget.setStyleSheet("""
            QFrame {
                border: 3px solid #4a9eff;
                background-color: transparent;
                border-radius: 4px;
            }
        """)
        self._highlight_widget.show()

        popup = QFrame(self)
        popup.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #4a9eff;
                border-radius: 8px;
            }
        """)

        popup_layout = QVBoxLayout(popup)

        msg_label = QLabel(message)
        msg_label.setStyleSheet("color: #ddd; font-size: 13px;")
        msg_label.setWordWrap(True)
        msg_label.setMaximumWidth(300)
        popup_layout.addWidget(msg_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        if self._current_step > 0:
            prev_btn = QPushButton("Previous")
            prev_btn.clicked.connect(self._prev_step)
            btn_layout.addWidget(prev_btn)

        next_btn = QPushButton(
            "Next" if self._current_step < len(self._steps) - 1 else "Finish"
        )
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
            }
        """)
        next_btn.clicked.connect(self._next_step)
        btn_layout.addWidget(next_btn)

        skip_btn = QPushButton("Skip")
        skip_btn.setStyleSheet("color: #888; border: none;")
        skip_btn.clicked.connect(self._skip_tour)
        btn_layout.addWidget(skip_btn)

        popup_layout.addLayout(btn_layout)
        popup.show()

        if position == "bottom":
            popup.move(pos.x() - popup.width() // 2, pos.y() + 50)
        elif position == "right":
            popup.move(pos.x() + 50, pos.y() - popup.height() // 2)

        self._current_popup = popup

    def _next_step(self):
        if hasattr(self, "_current_popup"):
            self._current_popup.close()
        self._current_step += 1
        self._show_current_step()

    def _prev_step(self):
        if hasattr(self, "_current_popup"):
            self._current_popup.close()
        self._current_step -= 1
        self._show_current_step()

    def _skip_tour(self):
        if hasattr(self, "_current_popup"):
            self._current_popup.close()
        self.tour_complete.emit()
