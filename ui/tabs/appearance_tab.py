"""
Appearance & Errors UI Tab (Tab 6)
Реализация вкладки настроек внешнего вида с использованием QtWebEngine
"""
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QComboBox,
    QCheckBox,
    QGroupBox,
    QFrame,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings

from core.config import ConfigManager
from core.guide_manager import GuideManager
from ui.guide_widget import GuideWidget


class AppearanceWebPage(QWebEnginePage):
    """Кастомная страница для обработки сигналов от веб-контента"""
    
    theme_changed = pyqtSignal(str)
    setting_changed = pyqtSignal(str, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptEnabled, True
        )
        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )


class AppearanceTab(QWidget):
    """
    Вкладка настроек внешнего вида (Tab 6)
    
    Функционал:
    - Интеграция QtWebEngine для браузерного UI
    - Настройки тёмной темы
    - Конфигурация окна ошибок
    - Управление системным треем
    """
    
    def __init__(self, config_manager: ConfigManager, guide_manager: GuideManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.guide_manager = guide_manager
        
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса вкладки"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Заголовок вкладки
        header_layout = QHBoxLayout()
        title_label = QLabel("Appearance & Errors")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Guide widget
        guide_widget = GuideWidget("appearance", self.guide_manager)
        header_layout.addWidget(guide_widget)
        
        main_layout.addLayout(header_layout)
        
        # Браузерный движок для превью темы
        theme_group = QGroupBox("Theme Preview (QtWebEngine)")
        theme_layout = QVBoxLayout(theme_group)
        
        self.web_view = QWebEngineView()
        self.web_page = AppearanceWebPage(self)
        self.web_view.setPage(self.web_page)
        self.web_view.setMinimumHeight(300)
        
        # Подключение сигналов от JavaScript
        self.web_page.loadFinished.connect(self.on_web_load_finished)
        
        theme_layout.addWidget(self.web_view)
        
        # Кнопки управления темой
        theme_buttons = QHBoxLayout()
        
        self.light_theme_btn = QPushButton("☀️ Light Theme")
        self.light_theme_btn.clicked.connect(lambda: self.set_theme("light"))
        
        self.dark_theme_btn = QPushButton("🌙 Dark Theme")
        self.dark_theme_btn.clicked.connect(lambda: self.set_theme("dark"))
        
        self.system_theme_btn = QPushButton("💻 System Theme")
        self.system_theme_btn.clicked.connect(lambda: self.set_theme("system"))
        
        theme_buttons.addWidget(self.light_theme_btn)
        theme_buttons.addWidget(self.dark_theme_btn)
        theme_buttons.addWidget(self.system_theme_btn)
        theme_buttons.addStretch()
        
        theme_layout.addLayout(theme_buttons)
        main_layout.addWidget(theme_group)
        
        # Настройки окна ошибок
        error_window_group = QGroupBox("Error Window Settings")
        error_window_layout = QVBoxLayout(error_window_group)
        
        # Прозрачность
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("Opacity:")
        opacity_label.setFixedWidth(100)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(80)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        self.opacity_value_label = QLabel("80%")
        self.opacity_value_label.setFixedWidth(40)
        
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_value_label)
        error_window_layout.addLayout(opacity_layout)
        
        # Цвет акцента
        color_layout = QHBoxLayout()
        color_label = QLabel("Accent Color:")
        color_label.setFixedWidth(100)
        self.color_combo = QComboBox()
        self.color_combo.addItems([
            "🔴 Red (#FF5555)",
            "🔵 Blue (#5555FF)",
            "🟢 Green (#55FF55)",
            "🟡 Yellow (#FFFF55)",
            "🟣 Purple (#FF55FF)",
            "🟠 Orange (#FFAA55)",
        ])
        self.color_combo.currentIndexChanged.connect(self.on_color_changed)
        
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_combo)
        color_layout.addStretch()
        error_window_layout.addLayout(color_layout)
        
        # Таймер автозакрытия
        timer_layout = QHBoxLayout()
        timer_label = QLabel("Auto-close (sec):")
        timer_label.setFixedWidth(100)
        self.timer_slider = QSlider(Qt.Orientation.Horizontal)
        self.timer_slider.setMinimum(1)
        self.timer_slider.setMaximum(30)
        self.timer_slider.setValue(5)
        self.timer_slider.valueChanged.connect(self.on_timer_changed)
        self.timer_value_label = QLabel("5s")
        self.timer_value_label.setFixedWidth(40)
        
        timer_layout.addWidget(timer_label)
        timer_layout.addWidget(self.timer_slider)
        timer_layout.addWidget(self.timer_value_label)
        error_window_layout.addLayout(timer_layout)
        
        # Чекбокс сохранения позиции
        self.save_position_check = QCheckBox("Save window position")
        self.save_position_check.setChecked(True)
        self.save_position_check.stateChanged.connect(self.on_save_position_changed)
        error_window_layout.addWidget(self.save_position_check)
        
        # Кнопка сброса позиции
        reset_position_btn = QPushButton("🔄 Reset Window Position")
        reset_position_btn.clicked.connect(self.reset_window_position)
        error_window_layout.addWidget(reset_position_btn)
        
        main_layout.addWidget(error_window_group)
        
        # Настройки системного трея
        tray_group = QGroupBox("System Tray Settings")
        tray_layout = QVBoxLayout(tray_group)
        
        self.tray_enabled_check = QCheckBox("Enable System Tray Icon")
        self.tray_enabled_check.setChecked(True)
        self.tray_enabled_check.stateChanged.connect(self.on_tray_enabled_changed)
        tray_layout.addWidget(self.tray_enabled_check)
        
        self.minimize_to_tray_check = QCheckBox("Minimize to Tray")
        self.minimize_to_tray_check.setChecked(False)
        self.minimize_to_tray_check.stateChanged.connect(self.on_minimize_to_tray_changed)
        tray_layout.addWidget(self.minimize_to_tray_check)
        
        self.close_to_tray_check = QCheckBox("Close to Tray (don't exit)")
        self.close_to_tray_check.setChecked(False)
        self.close_to_tray_check.stateChanged.connect(self.on_close_to_tray_changed)
        tray_layout.addWidget(self.close_to_tray_check)
        
        main_layout.addWidget(tray_group)
        
        # Кнопка тестирования
        test_layout = QHBoxLayout()
        test_btn = QPushButton("🧪 Test Error Overlay")
        test_btn.clicked.connect(self.test_error_overlay)
        test_layout.addWidget(test_btn)
        test_layout.addStretch()
        main_layout.addLayout(test_layout)
        
        main_layout.addStretch()
        
    def load_config(self):
        """Загрузка настроек из ConfigManager"""
        config = self.config_manager.config
        
        # Appearance settings
        appearance = config.get("appearance", {})
        
        # Theme
        theme = appearance.get("theme", "system")
        self.set_theme(theme, update_config=False)
        
        # Error window
        error_window = appearance.get("error_window", {})
        self.opacity_slider.setValue(error_window.get("opacity", 80))
        self.timer_slider.setValue(error_window.get("auto_close_seconds", 5))
        self.color_combo.setCurrentIndex(error_window.get("color_index", 0))
        self.save_position_check.setChecked(error_window.get("save_position", True))
        
        # Tray settings
        tray = appearance.get("tray", {})
        self.tray_enabled_check.setChecked(tray.get("enabled", True))
        self.minimize_to_tray_check.setChecked(tray.get("minimize_to_tray", False))
        self.close_to_tray_check.setChecked(tray.get("close_to_tray", False))
        
    def save_config(self):
        """Сохранение настроек в ConfigManager"""
        config = self.config_manager.config
        
        if "appearance" not in config:
            config["appearance"] = {}
            
        appearance = config["appearance"]
        
        # Theme
        appearance["theme"] = self.current_theme
        
        # Error window
        if "error_window" not in appearance:
            appearance["error_window"] = {}
            
        appearance["error_window"]["opacity"] = self.opacity_slider.value()
        appearance["error_window"]["auto_close_seconds"] = self.timer_slider.value()
        appearance["error_window"]["color_index"] = self.color_combo.currentIndex()
        appearance["error_window"]["save_position"] = self.save_position_check.isChecked()
        
        # Tray settings
        if "tray" not in appearance:
            appearance["tray"] = {}
            
        appearance["tray"]["enabled"] = self.tray_enabled_check.isChecked()
        appearance["tray"]["minimize_to_tray"] = self.minimize_to_tray_check.isChecked()
        appearance["tray"]["close_to_tray"] = self.close_to_tray_check.isChecked()
        
        self.config_manager.save_config(config)
        
    def set_theme(self, theme: str, update_config: bool = True):
        """
        Установка темы оформления
        
        Args:
            theme: "light", "dark", или "system"
            update_config: Сохранять ли в конфиг
        """
        self.current_theme = theme
        
        # Генерация HTML для превью
        html = self.generate_theme_preview_html(theme)
        self.web_view.setHtml(QUrl.fromUserInput(html))
        
        # Обновление стиля кнопок
        self.light_theme_btn.setStyleSheet(
            "font-weight: bold;" if theme == "light" else ""
        )
        self.dark_theme_btn.setStyleSheet(
            "font-weight: bold;" if theme == "dark" else ""
        )
        self.system_theme_btn.setStyleSheet(
            "font-weight: bold;" if theme == "system" else ""
        )
        
        if update_config:
            self.save_config()
            
    def generate_theme_preview_html(self, theme: str) -> str:
        """
        Генерация HTML страницы для превью темы
        
        Args:
            theme: Тип темы
            
        Returns:
            HTML строка
        """
        if theme == "dark":
            bg_color = "#1a1a2e"
            card_bg = "#16213e"
            text_color = "#eaeaea"
            accent = "#e94560"
        elif theme == "light":
            bg_color = "#f0f2f5"
            card_bg = "#ffffff"
            text_color = "#333333"
            accent = "#007bff"
        else:  # system
            bg_color = "#f0f2f5"
            card_bg = "#ffffff"
            text_color = "#333333"
            accent = "#007bff"
            
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    background-color: {bg_color};
                    color: {text_color};
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    transition: all 0.3s ease;
                }}
                .card {{
                    background-color: {card_bg};
                    border-radius: 10px;
                    padding: 20px;
                    margin: 15px 0;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    border-left: 4px solid {accent};
                }}
                h1 {{
                    color: {accent};
                    margin-top: 0;
                }}
                .preview-item {{
                    display: inline-block;
                    padding: 10px 20px;
                    margin: 5px;
                    background-color: {accent};
                    color: white;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <h1>Theme Preview: {theme.title()}</h1>
            <div class="card">
                <h2>Sample Card</h2>
                <p>This is how the UI will look with the {theme} theme.</p>
                <div class="preview-item">Button</div>
                <div class="preview-item">Active</div>
            </div>
            <div class="card">
                <h3>Settings Panel</h3>
                <p>All settings will follow this color scheme.</p>
            </div>
        </body>
        </html>
        """
        return html
        
    def on_web_load_finished(self, success: bool):
        """Обработчик завершения загрузки веб-страницы"""
        if success:
            print("Theme preview loaded successfully")
            
    def on_opacity_changed(self, value: int):
        """Изменение прозрачности окна ошибок"""
        self.opacity_value_label.setText(f"{value}%")
        self.save_config()
        
    def on_color_changed(self, index: int):
        """Изменение цвета акцента"""
        self.save_config()
        
    def on_timer_changed(self, value: int):
        """Изменение таймера автозакрытия"""
        self.timer_value_label.setText(f"{value}s")
        self.save_config()
        
    def on_save_position_changed(self, state):
        """Изменение настройки сохранения позиции"""
        self.save_config()
        
    def reset_window_position(self):
        """Сброс позиции окна ошибок"""
        # Здесь будет логика сброса сохранённых координат
        print("Window position reset")
        self.save_config()
        
    def on_tray_enabled_changed(self, state):
        """Изменение настройки системного трея"""
        self.save_config()
        
    def on_minimize_to_tray_changed(self, state):
        """Изменение настройки сворачивания в трей"""
        self.save_config()
        
    def on_close_to_tray_changed(self, state):
        """Изменение настройки закрытия в трей"""
        self.save_config()
        
    def test_error_overlay(self):
        """Тестирование окна ошибок"""
        from ui.error_window import OverlayWindow
        error = OverlayWindow("🧪 Test Error: This is a sample error message")
        error.show()
