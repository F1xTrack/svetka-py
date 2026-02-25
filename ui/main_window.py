import sys
from PyQt6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QLabel,
    QHBoxLayout,
    QSystemTrayIcon,
    QMenu,
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon, QGuiApplication, QAction

from core.config import ConfigManager
from core.guide_manager import GuideManager
from core.api_bridge import APIBridge
from core.memory.context import ContextManager
from ui.guide_widget import GuideWidget, GuideModal
from modules.audio.processor import AudioProcessor
from modules.vision.processor import VisionProcessor

from ui.tabs.vision_tab import VisionTab
from ui.tabs.audio_tab import AudioTab
from ui.tabs.api_tab import APISettingsTab
from ui.tabs.personality_tab import PersonalityTab
from ui.tabs.memory_tab import MemoryTab
from ui.tabs.appearance_tab import AppearanceTab
from ui.tabs.privacy_tab import PrivacyTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Svetka AI Assistant")
        self.resize(1000, 800)

        self.config_manager = ConfigManager("config.yaml")
        self.guide_manager = GuideManager("config.yaml")
        self.api_bridge = APIBridge(self.config_manager)
        self.context_manager = ContextManager(self.config_manager, self.api_bridge)
        self.audio_processor = AudioProcessor(self.config_manager)
        self.vision_processor = VisionProcessor(self.config_manager)

        # Настройки системного трея
        self.tray_icon: QSystemTrayIcon | None = None
        self.close_to_tray = False
        self.minimize_to_tray = False

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tab_widgets = {}

        # Инициализация вкладок
        self.tab_widgets["vision"] = VisionTab(self.config_manager, self.guide_manager, self.vision_processor)
        self.tab_widgets["audio"] = AudioTab(self.config_manager, self.guide_manager, self.audio_processor)
        self.tab_widgets["api"] = APISettingsTab(self.config_manager, self.guide_manager)
        self.tab_widgets["personality"] = PersonalityTab(self.config_manager, self.guide_manager)
        self.tab_widgets["memory"] = MemoryTab(self.config_manager, self.guide_manager, self.context_manager)
        self.tab_widgets["appearance"] = AppearanceTab(self.config_manager, self.guide_manager)
        self.tab_widgets["privacy"] = PrivacyTab(self.config_manager, self.guide_manager, self.context_manager)

        self.tabs.addTab(self.tab_widgets["vision"], "Vision")
        self.tabs.addTab(self.tab_widgets["audio"], "Audio")
        self.tabs.addTab(self.tab_widgets["api"], "AI & API")
        self.tabs.addTab(self.tab_widgets["personality"], "Personality")
        self.tabs.addTab(self.tab_widgets["memory"], "Memory")
        self.tabs.addTab(self.tab_widgets["appearance"], "Appearance")
        self.tabs.addTab(self.tab_widgets["privacy"], "Privacy")

        # Инициализация системного трея
        self.init_system_tray()

        # Загрузка настроек трея из конфига
        self.load_tray_settings()

        self.guide_manager.guides_loaded.connect(self._on_guides_loaded)
        
        # Запуск фоновых задач
        import asyncio
        asyncio.create_task(self._start_background_tasks())

    async def _start_background_tasks(self):
        """Запуск асинхронных процессоров"""
        try:
            await self.vision_processor.start()
            await self.audio_processor.start()
            print("Background processors started successfully.")
        except Exception as e:
            print(f"Error starting background tasks: {e}")

    def init_system_tray(self):
        """Инициализация иконки в системном трее"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("System tray not available")
            return

        # Создание иконки (используем стандартную иконку)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.HelpBrowser,
                                                QIcon.fromTheme("dialog-information")))

        # Создание контекстного меню
        tray_menu = QMenu()

        # Действие "Показать"
        show_action = QAction("Show Svetka", self)
        show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(show_action)

        # Действие "Скрыть"
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.minimize_to_tray_action)
        tray_menu.addAction(hide_action)

        tray_menu.addSeparator()

        # Действие "Выход"
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)

        # Обработка двойного клика
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Отображение иконки
        self.tray_icon.show()
        self.tray_icon.setToolTip("Svetka AI Assistant")

    def load_tray_settings(self):
        """Загрузка настроек системного трея из конфига"""
        config = self.config_manager.config
        appearance = config.get("appearance", {})
        tray_settings = appearance.get("tray", {})

        self.tray_enabled = tray_settings.get("enabled", {}).get("value", True)
        self.minimize_to_tray = tray_settings.get("minimize_to_tray", {}).get("value", False)
        self.close_to_tray = tray_settings.get("close_to_tray", {}).get("value", False)

        # Если трей отключён, скрываем иконку
        if not self.tray_enabled and self.tray_icon:
            self.tray_icon.hide()

    def on_tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """Обработка активации иконки трея"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_from_tray()

    def show_from_tray(self):
        """Показать окно приложения из трея"""
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def minimize_to_tray_action(self):
        """Скрыть приложение в трей"""
        self.hide()

    def quit_application(self):
        """Выход из приложения"""
        import asyncio
        asyncio.create_task(self._shutdown())

    async def _shutdown(self):
        """Асинхронное завершение работы процессоров"""
        print("Shutting down processors...")
        await self.vision_processor.stop()
        await self.audio_processor.stop()
        self.close()
        QGuiApplication.quit()

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.close_to_tray and self.tray_icon and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Svetka",
                "Приложение свёрнуто в трей. Для выхода используйте меню иконки.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            event.accept()

    def changeEvent(self, event):
        """Обработка изменения состояния окна"""
        if event.type() == event.Type.WindowStateChange:
            if self.windowState() & Qt.WindowState.WindowMinimized:
                if self.minimize_to_tray and self.tray_icon and self.tray_icon.isVisible():
                    self.hide()
        super().changeEvent(event)

    def _get_guide_key(self, tab_name: str) -> str:
        mapping = {
            "Vision Settings": "vision",
            "Audio Settings": "audio",
            "AI & API Settings": "api",
            "Personality Settings": "personality",
            "Memory Settings": "memory",
            "Appearance & Errors": "appearance",
            "Privacy Settings": "privacy",
        }
        return mapping.get(tab_name, "")

    def _on_guides_loaded(self):
        print("Guides loaded successfully")

    def show_guide_modal(self, guide_key: str):
        guide = self.guide_manager.get_guide(guide_key)
        if guide:
            modal = GuideModal(guide_key, guide.title, guide.rich_text, self)
            modal.exec()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
