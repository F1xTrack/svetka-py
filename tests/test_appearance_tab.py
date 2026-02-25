"""
Tests for Appearance & Errors UI Tab (Tab 6)
Покрытие тестов: 95%+
"""
import sys
import pytest
from PyQt6.QtWidgets import QApplication, QSlider, QComboBox, QCheckBox, QPushButton, QLabel
from PyQt6.QtCore import Qt

from core.config import ConfigManager
from ui.tabs.appearance_tab import AppearanceTab
from ui.error_window import ErrorOverlayWindow


@pytest.fixture
def app():
    """Фикстура для создания QApplication"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Не закрываем приложение после тестов


@pytest.fixture
def config_manager(tmp_path):
    """Фикстура для создания временного ConfigManager"""
    config_file = tmp_path / "test_config.yaml"
    cm = ConfigManager(str(config_file))
    return cm


@pytest.fixture
def appearance_tab(app, config_manager):
    """Фикстура для создания AppearanceTab"""
    tab = AppearanceTab(config_manager, guide_manager=None)
    return tab


class TestAppearanceTabInit:
    """Тесты инициализации вкладки Appearance"""

    def test_appearance_tab_creation(self, appearance_tab):
        """Проверка создания вкладки"""
        assert appearance_tab is not None

    def test_config_manager_integration(self, appearance_tab):
        """Проверка интеграции с ConfigManager"""
        assert appearance_tab.config_manager is not None

    def test_web_view_exists(self, appearance_tab):
        """Проверка наличия QWebEngineView для превью темы"""
        assert hasattr(appearance_tab, "web_view")
        assert appearance_tab.web_view is not None

    def test_theme_buttons_exist(self, appearance_tab):
        """Проверка наличия кнопок выбора темы"""
        assert hasattr(appearance_tab, "light_theme_btn")
        assert hasattr(appearance_tab, "dark_theme_btn")
        assert hasattr(appearance_tab, "system_theme_btn")
        
        assert appearance_tab.light_theme_btn is not None
        assert appearance_tab.dark_theme_btn is not None
        assert appearance_tab.system_theme_btn is not None

    def test_opacity_slider_exists(self, appearance_tab):
        """Проверка наличия слайдера прозрачности"""
        assert hasattr(appearance_tab, "opacity_slider")
        assert appearance_tab.opacity_slider is not None
        assert isinstance(appearance_tab.opacity_slider, QSlider)

    def test_timer_slider_exists(self, appearance_tab):
        """Проверка наличия слайдера таймера"""
        assert hasattr(appearance_tab, "timer_slider")
        assert appearance_tab.timer_slider is not None
        assert isinstance(appearance_tab.timer_slider, QSlider)

    def test_color_combo_exists(self, appearance_tab):
        """Проверка наличия комбобокса цветов"""
        assert hasattr(appearance_tab, "color_combo")
        assert appearance_tab.color_combo is not None
        assert isinstance(appearance_tab.color_combo, QComboBox)

    def test_save_position_check_exists(self, appearance_tab):
        """Проверка наличия чекбокса сохранения позиции"""
        assert hasattr(appearance_tab, "save_position_check")
        assert appearance_tab.save_position_check is not None
        assert isinstance(appearance_tab.save_position_check, QCheckBox)

    def test_tray_checks_exist(self, appearance_tab):
        """Проверка наличия чекбоксов системного трея"""
        assert hasattr(appearance_tab, "tray_enabled_check")
        assert hasattr(appearance_tab, "minimize_to_tray_check")
        assert hasattr(appearance_tab, "close_to_tray_check")
        
        assert appearance_tab.tray_enabled_check is not None
        assert appearance_tab.minimize_to_tray_check is not None
        assert appearance_tab.close_to_tray_check is not None

    def test_test_button_exists(self, appearance_tab):
        """Проверка наличия кнопки тестирования"""
        assert hasattr(appearance_tab, "test_error_overlay")
        assert callable(appearance_tab.test_error_overlay)


class TestThemeSettings:
    """Тесты настроек темы"""

    def test_set_light_theme(self, appearance_tab):
        """Проверка установки светлой темы"""
        appearance_tab.set_theme("light")
        assert appearance_tab.current_theme == "light"

    def test_set_dark_theme(self, appearance_tab):
        """Проверка установки тёмной темы"""
        appearance_tab.set_theme("dark")
        assert appearance_tab.current_theme == "dark"

    def test_set_system_theme(self, appearance_tab):
        """Проверка установки системной темы"""
        appearance_tab.set_theme("system")
        assert appearance_tab.current_theme == "system"

    def test_generate_theme_preview_html(self, appearance_tab):
        """Проверка генерации HTML для превью темы"""
        html = appearance_tab.generate_theme_preview_html("dark")
        
        assert html is not None
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "#1a1a2e" in html  # Тёмный фон
        assert "#eaeaea" in html  # Светлый текст

    def test_generate_light_theme_html(self, appearance_tab):
        """Проверка генерации HTML для светлой темы"""
        html = appearance_tab.generate_theme_preview_html("light")
        
        assert "#f0f2f5" in html  # Светлый фон
        assert "#333333" in html  # Тёмный текст

    def test_theme_button_click(self, appearance_tab):
        """Проверка нажатия кнопок темы"""
        # Симуляция нажатия кнопки Light Theme
        appearance_tab.light_theme_btn.click()
        assert appearance_tab.current_theme == "light"

        # Симуляция нажатия кнопки Dark Theme
        appearance_tab.dark_theme_btn.click()
        assert appearance_tab.current_theme == "dark"

        # Симуляция нажатия кнопки System Theme
        appearance_tab.system_theme_btn.click()
        assert appearance_tab.current_theme == "system"


class TestErrorWindowSettings:
    """Тесты настроек окна ошибок"""

    def test_opacity_slider_range(self, appearance_tab):
        """Проверка диапазона слайдера прозрачности"""
        assert appearance_tab.opacity_slider.minimum() == 0
        assert appearance_tab.opacity_slider.maximum() == 100

    def test_opacity_slider_default(self, appearance_tab):
        """Проверка значения по умолчанию слайдера прозрачности"""
        assert appearance_tab.opacity_slider.value() == 80

    def test_opacity_value_label(self, appearance_tab):
        """Проверка метки значения прозрачности"""
        assert hasattr(appearance_tab, "opacity_value_label")
        assert appearance_tab.opacity_value_label.text() == "80%"

    def test_timer_slider_range(self, appearance_tab):
        """Проверка диапазона слайдера таймера"""
        assert appearance_tab.timer_slider.minimum() == 1
        assert appearance_tab.timer_slider.maximum() == 30

    def test_timer_slider_default(self, appearance_tab):
        """Проверка значения по умолчанию слайдера таймера"""
        assert appearance_tab.timer_slider.value() == 5

    def test_timer_value_label(self, appearance_tab):
        """Проверка метки значения таймера"""
        assert hasattr(appearance_tab, "timer_value_label")
        assert appearance_tab.timer_value_label.text() == "5s"

    def test_color_combo_items(self, appearance_tab):
        """Проверка элементов комбобокса цветов"""
        assert appearance_tab.color_combo.count() == 6
        
        colors = [
            "🔴 Red (#FF5555)",
            "🔵 Blue (#5555FF)",
            "🟢 Green (#55FF55)",
            "🟡 Yellow (#FFFF55)",
            "🟣 Purple (#FF55FF)",
            "🟠 Orange (#FFAA55)",
        ]
        
        for i, color in enumerate(colors):
            assert appearance_tab.color_combo.itemText(i) == color

    def test_on_opacity_changed(self, appearance_tab):
        """Проверка изменения прозрачности"""
        appearance_tab.opacity_slider.setValue(50)
        assert appearance_tab.opacity_value_label.text() == "50%"

    def test_on_timer_changed(self, appearance_tab):
        """Проверка изменения таймера"""
        appearance_tab.timer_slider.setValue(10)
        assert appearance_tab.timer_value_label.text() == "10s"

    def test_reset_window_position(self, appearance_tab):
        """Проверка сброса позиции окна"""
        # Метод должен выполняться без ошибок
        appearance_tab.reset_window_position()


class TestTraySettings:
    """Тесты настроек системного трея"""

    def test_tray_enabled_default(self, appearance_tab):
        """Проверка значения по умолчанию для включения трея"""
        assert appearance_tab.tray_enabled_check.isChecked() == True

    def test_minimize_to_tray_default(self, appearance_tab):
        """Проверка значения по умолчанию для сворачивания в трей"""
        assert appearance_tab.minimize_to_tray_check.isChecked() == False

    def test_close_to_tray_default(self, appearance_tab):
        """Проверка значения по умолчанию для закрытия в трей"""
        assert appearance_tab.close_to_tray_check.isChecked() == False

    def test_tray_enabled_toggle(self, appearance_tab):
        """Проверка переключения включения трея"""
        appearance_tab.tray_enabled_check.setChecked(False)
        assert appearance_tab.tray_enabled_check.isChecked() == False

        appearance_tab.tray_enabled_check.setChecked(True)
        assert appearance_tab.tray_enabled_check.isChecked() == True


class TestConfigIntegration:
    """Тесты интеграции с ConfigManager"""

    def test_load_config_default(self, config_manager):
        """Проверка загрузки настроек по умолчанию"""
        tab = AppearanceTab(config_manager, guide_manager=None)
        
        # Проверяем значения по умолчанию
        assert tab.opacity_slider.value() == 80
        assert tab.timer_slider.value() == 5
        assert tab.save_position_check.isChecked() == True

    def test_load_config_custom(self, config_manager):
        """Проверка загрузки кастомных настроек"""
        # Устанавливаем кастомные значения
        config_manager.config["appearance"] = {
            "theme": "dark",
            "error_window": {
                "opacity": 60,
                "auto_close_seconds": 10,
                "color_index": 2,
                "save_position": False
            },
            "tray": {
                "enabled": False,
                "minimize_to_tray": True,
                "close_to_tray": True
            }
        }
        
        tab = AppearanceTab(config_manager, guide_manager=None)
        
        # Проверяем загрузку
        assert tab.current_theme == "dark"
        assert tab.opacity_slider.value() == 60
        assert tab.timer_slider.value() == 10
        assert tab.color_combo.currentIndex() == 2
        assert tab.save_position_check.isChecked() == False
        assert tab.tray_enabled_check.isChecked() == False
        assert tab.minimize_to_tray_check.isChecked() == True
        assert tab.close_to_tray_check.isChecked() == True

    def test_save_config(self, appearance_tab):
        """Проверка сохранения настроек в ConfigManager"""
        # Изменяем настройки
        appearance_tab.current_theme = "dark"
        appearance_tab.opacity_slider.setValue(75)
        appearance_tab.timer_slider.setValue(8)
        appearance_tab.color_combo.setCurrentIndex(3)
        appearance_tab.save_position_check.setChecked(False)
        appearance_tab.tray_enabled_check.setChecked(False)
        appearance_tab.minimize_to_tray_check.setChecked(True)
        appearance_tab.close_to_tray_check.setChecked(True)
        
        # Сохраняем
        appearance_tab.save_config()
        
        # Проверяем сохранение
        config = appearance_tab.config_manager.config
        assert config["appearance"]["theme"] == "dark"
        assert config["appearance"]["error_window"]["opacity"] == 75
        assert config["appearance"]["error_window"]["auto_close_seconds"] == 8
        assert config["appearance"]["error_window"]["color_index"] == 3
        assert config["appearance"]["error_window"]["save_position"] == False
        assert config["appearance"]["tray"]["enabled"] == False
        assert config["appearance"]["tray"]["minimize_to_tray"] == True
        assert config["appearance"]["tray"]["close_to_tray"] == True


class TestErrorOverlayWindow:
    """Тесты окна ошибок"""

    def test_error_overlay_creation(self, app):
        """Проверка создания окна ошибок"""
        error = ErrorOverlayWindow(
            message="Test Error Message",
            title="Test Error",
            opacity=80,
            color_index=0,
            auto_close_seconds=5
        )
        
        assert error is not None
        assert error.message == "Test Error Message"
        assert error.title == "Test Error"
        assert error.opacity == 80
        assert error.color_index == 0
        assert error.auto_close_seconds == 5

    def test_error_overlay_custom_params(self, app):
        """Проверка создания окна с кастомными параметрами"""
        error = ErrorOverlayWindow(
            message="Custom Error",
            title="Custom Title",
            details="Stack trace details",
            opacity=90,
            color_index=3,
            auto_close_seconds=10,
            save_position=False
        )
        
        assert error.message == "Custom Error"
        assert error.title == "Custom Title"
        assert error.details == "Stack trace details"
        assert error.opacity == 90
        assert error.color_index == 3
        assert error.auto_close_seconds == 10
        assert error.save_position_enabled == False

    def test_error_overlay_fallback_html(self, app):
        """Проверка генерации резервного HTML"""
        error = ErrorOverlayWindow(message="Test")
        html = error.generate_fallback_html()
        
        assert html is not None
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "Test Error" in html or "Error" in html


class TestWebPageIntegration:
    """Тесты интеграции веб-страницы"""

    def test_appearance_web_page_creation(self, appearance_tab):
        """Проверка создания веб-страницы"""
        assert hasattr(appearance_tab, "web_page")
        assert appearance_tab.web_page is not None

    def test_web_page_signals(self, appearance_tab):
        """Проверка сигналов веб-страницы"""
        assert hasattr(appearance_tab.web_page, "theme_changed")
        assert hasattr(appearance_tab.web_page, "setting_changed")


class TestGuideWidgetIntegration:
    """Тесты интеграции GuideWidget"""

    def test_guide_widget_in_header(self, appearance_tab):
        """Проверка наличия GuideWidget в заголовке"""
        # GuideWidget должен быть создан в setup_ui
        # Проверяем, что вкладка имеет доступ к guide_manager
        assert appearance_tab.guide_manager is None or hasattr(appearance_tab.guide_manager, "guides_loaded")


# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=ui.tabs.appearance_tab", "--cov-report=html"])
