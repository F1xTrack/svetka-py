import sys
import pytest
from PyQt6.QtWidgets import QApplication, QTabWidget, QLabel
from ui.main_window import MainWindow
from ui.error_window import OverlayWindow

# Check for pytest-qt, but we'll use a basic test here.
# Since we might not have pytest-qt, we'll use a standard QApplication instance.

@pytest.fixture
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

def test_main_window_tabs(app):
    window = MainWindow()
    assert window.windowTitle() == "Svetka AI Assistant"
    
    tabs = window.findChild(QTabWidget)
    assert tabs is not None
    assert tabs.count() == 7
    
    # Check tab labels
    expected_tabs = [
        "Vision Settings", "Audio Settings", "AI & API Settings",
        "Personality Settings", "Memory Settings", "Appearance & Errors",
        "Privacy Settings"
    ]
    for i in range(7):
        assert tabs.tabText(i) == expected_tabs[i]

def test_error_overlay_init(app):
    msg = "Test Error"
    error = OverlayWindow(msg)
    assert error.label.text() == msg
    assert error.windowFlags() & (1 << 11) # FramelessWindowHint
