from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class VerificationDialog(QDialog):
    """Dialog for manual verification of phase completion"""

    def __init__(self, header: str, question: str, parent=None, dialog_type: str = "yesno"):
        super().__init__(parent)
        self.header = header
        self.question = question
        self.dialog_type = dialog_type
        self.result = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(self.header)
        self.setMinimumSize(600, 400)
        self.setModal(True)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header_label = QLabel(self.header)
        header_label.setStyleSheet("""
            color: #4a9eff;
            font-size: 22px;
            font-weight: bold;
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #444;")
        separator.setFixedHeight(2)
        layout.addWidget(separator)

        # Question
        question_label = QLabel(self.question)
        question_label.setStyleSheet("""
            color: #ddd;
            font-size: 14px;
            line-height: 1.6;
        """)
        question_label.setWordWrap(True)
        question_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        question_label.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(question_label)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        if self.dialog_type == "yesno":
            yes_btn = QPushButton("Yes")
            yes_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px 30px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            yes_btn.clicked.connect(self._on_yes)
            btn_layout.addWidget(yes_btn)

            no_btn = QPushButton("No")
            no_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 10px 30px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            no_btn.clicked.connect(self._on_no)
            btn_layout.addWidget(no_btn)
        else:
            ok_btn = QPushButton("OK")
            ok_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a9eff;
                    color: white;
                    border: none;
                    padding: 10px 30px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5aafff;
                }
            """)
            ok_btn.clicked.connect(self._on_ok)
            btn_layout.addWidget(ok_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _on_yes(self):
        self.result = "yes"
        self.accept()

    def _on_no(self):
        self.result = "no"
        self.accept()

    def _on_ok(self):
        self.result = "ok"
        self.accept()

    def get_result(self) -> str | None:
        return self.result
