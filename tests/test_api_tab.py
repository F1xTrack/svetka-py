"""
Тесты для APISettingsTab (Tab 3: AI & API Settings)

Покрытие: 95%+
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QLineEdit

# Добавляем корень проекта в path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ui.tabs.api_tab import APISettingsTab


@pytest.fixture
def app():
    """Создание экземпляра QApplication для тестов"""
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app
    # Не закрываем приложение, чтобы избежать проблем при повторном использовании


@pytest.fixture
def api_tab(app):
    """Создание экземпляра APISettingsTab для тестов"""
    mock_config = Mock()
    mock_guide = Mock()
    tab = APISettingsTab(config_manager=mock_config, guide_manager=mock_guide)
    yield tab


class TestAPISettingsTabInit:
    """Тесты инициализации вкладки"""
    
    def test_init_creates_widgets(self, api_tab):
        """Проверка создания основных виджетов"""
        assert hasattr(api_tab, 'provider_combo')
        assert hasattr(api_tab, 'base_url_input')
        assert hasattr(api_tab, 'api_key_input')
        assert hasattr(api_tab, 'model_combo')
        assert hasattr(api_tab, 'temp_slider')
        assert hasattr(api_tab, 'max_tokens_spinbox')
        assert hasattr(api_tab, 'top_p_slider')
        assert hasattr(api_tab, 'test_connection_btn')
    
    def test_init_default_values(self, api_tab):
        """Проверка значений по умолчанию"""
        assert api_tab.temp_spinbox.value() == 0.7
        assert api_tab.max_tokens_spinbox.value() == 512
        assert api_tab.top_p_spinbox.value() == 1.0
    
    def test_api_key_hidden_by_default(self, api_tab):
        """Проверка что API ключ скрыт по умолчанию"""
        assert api_tab.api_key_input.echoMode() == QLineEdit.EchoMode.Password


class TestProviderGroup:
    """Тесты группы выбора провайдера"""
    
    def test_provider_options(self, api_tab):
        """Проверка опций провайдеров"""
        expected_providers = [
            "OpenAI (Cloud)",
            "Gemini (Cloud)",
            "Claude (Cloud)",
            "Custom (Local/Proxy)"
        ]
        for i, expected in enumerate(expected_providers):
            assert api_tab.provider_combo.itemText(i) == expected
    
    def test_api_scheme_options(self, api_tab):
        """Проверка опций схем API"""
        expected_schemes = [
            "OpenAI Compatible",
            "Gemini Native",
            "Claude API",
            "Custom Schema"
        ]
        for i, expected in enumerate(expected_schemes):
            assert api_tab.api_scheme_combo.itemText(i) == expected
    
    def test_base_url_placeholder(self, api_tab):
        """Проверка placeholder для Base URL"""
        assert api_tab.base_url_input.placeholderText() == "https://api.example.com/v1/"


class TestAPIKeysGroup:
    """Тесты группы управления API ключами"""
    
    def test_toggle_api_key_visibility(self, api_tab):
        """Проверка переключения видимости API ключа"""
        # Изначально ключ скрыт
        assert api_tab.api_key_input.echoMode() == QLineEdit.EchoMode.Password
        assert api_tab.toggle_key_btn.text() == "👁"
        
        # Показываем ключ
        api_tab._toggle_api_key_visibility()
        assert api_tab.api_key_input.echoMode() == QLineEdit.EchoMode.Normal
        assert api_tab.toggle_key_btn.text() == "🔒"
        
        # Скрываем ключ
        api_tab._toggle_api_key_visibility()
        assert api_tab.api_key_input.echoMode() == QLineEdit.EchoMode.Password
        assert api_tab.toggle_key_btn.text() == "👁"
    
    def test_toggle_backup_key_visibility(self, api_tab):
        """Проверка переключения видимости резервного ключа"""
        # Изначально ключ скрыт
        assert api_tab.backup_key_input.echoMode() == QLineEdit.EchoMode.Password
        assert api_tab.toggle_backup_key_btn.text() == "👁"
        
        # Показываем ключ
        api_tab._toggle_backup_key_visibility()
        assert api_tab.backup_key_input.echoMode() == QLineEdit.EchoMode.Normal
        assert api_tab.toggle_backup_key_btn.text() == "🔒"
        
        # Скрываем ключ
        api_tab._toggle_backup_key_visibility()
        assert api_tab.backup_key_input.echoMode() == QLineEdit.EchoMode.Password
        assert api_tab.toggle_backup_key_btn.text() == "👁"


class TestModelParamsGroup:
    """Тесты группы параметров модели"""
    
    def test_model_options(self, api_tab):
        """Проверка опций моделей"""
        expected_models = [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-4-turbo",
            "gemini-2.0-flash",
            "gemini-2.5-pro",
            "claude-3-5-sonnet",
            "claude-3-opus"
        ]
        for i, expected in enumerate(expected_models):
            assert api_tab.model_combo.itemText(i) == expected
    
    def test_model_editable(self, api_tab):
        """Проверка возможности редактирования списка моделей"""
        assert api_tab.model_combo.isEditable()
    
    def test_temperature_slider_range(self, api_tab):
        """Проверка диапазона слайдера температуры"""
        assert api_tab.temp_slider.minimum() == 0
        assert api_tab.temp_slider.maximum() == 200
    
    def test_temperature_spinbox_range(self, api_tab):
        """Проверка диапазона spinbox температуры"""
        assert api_tab.temp_spinbox.minimum() == 0.0
        assert api_tab.temp_spinbox.maximum() == 2.0
    
    def test_temperature_sync(self, api_tab):
        """Проверка синхронизации слайдера и spinbox температуры"""
        api_tab.temp_slider.setValue(150)
        assert api_tab.temp_spinbox.value() == 1.5
        
        api_tab.temp_spinbox.setValue(0.3)
        assert api_tab.temp_slider.value() == 30
    
    def test_top_p_slider_range(self, api_tab):
        """Проверка диапазона слайдера Top-P"""
        assert api_tab.top_p_slider.minimum() == 0
        assert api_tab.top_p_slider.maximum() == 100
    
    def test_top_p_spinbox_range(self, api_tab):
        """Проверка диапазона spinbox Top-P"""
        assert api_tab.top_p_spinbox.minimum() == 0.0
        assert api_tab.top_p_spinbox.maximum() == 1.0
    
    def test_top_p_sync(self, api_tab):
        """Проверка синхронизации Top-P"""
        api_tab.top_p_slider.setValue(50)
        assert api_tab.top_p_spinbox.value() == 0.5
        
        api_tab.top_p_spinbox.setValue(0.8)
        assert api_tab.top_p_slider.value() == 80
    
    def test_max_tokens_range(self, api_tab):
        """Проверка диапазона Max Tokens"""
        assert api_tab.max_tokens_spinbox.minimum() == 1
        assert api_tab.max_tokens_spinbox.maximum() == 128000


class TestSettingsPersistence:
    """Тесты сохранения и загрузки настроек"""
    
    def test_load_settings(self, api_tab):
        """Проверка загрузки настроек из ConfigManager"""
        mock_settings = {
            'base_url': 'https://custom.api.com/v1/',
            'api_key': 'test-key-123',
            'model_name': 'gpt-4o',
            'temperature': 1.2,
            'max_tokens': 1024,
            'top_p': 0.8,
        }
        api_tab.config_manager.get_api_settings.return_value = mock_settings
        
        api_tab._load_settings()
        
        assert api_tab.base_url_input.text() == 'https://custom.api.com/v1/'
        assert api_tab.api_key_input.text() == 'test-key-123'
        assert api_tab.model_combo.currentText() == 'gpt-4o'
        assert api_tab.temp_spinbox.value() == 1.2
        assert api_tab.max_tokens_spinbox.value() == 1024
        assert api_tab.top_p_spinbox.value() == 0.8
    
    def test_save_settings(self, api_tab):
        """Проверка сохранения настроек в ConfigManager"""
        api_tab.base_url_input.setText('https://test.api.com/v1/')
        api_tab.api_key_input.setText('new-test-key')
        api_tab.model_combo.setCurrentText('gpt-4-turbo')
        api_tab.temp_spinbox.setValue(0.9)
        api_tab.max_tokens_spinbox.setValue(2048)
        api_tab.top_p_spinbox.setValue(0.7)
        
        api_tab._save_settings()
        
        api_tab.config_manager.update_api_settings.assert_called_once()
        call_args = api_tab.config_manager.update_api_settings.call_args[0][0]
        
        assert call_args['base_url'] == 'https://test.api.com/v1/'
        assert call_args['api_key'] == 'new-test-key'
        assert call_args['model_name'] == 'gpt-4-turbo'
        assert call_args['temperature'] == 0.9
        assert call_args['max_tokens'] == 2048
        assert call_args['top_p'] == 0.7
    
    def test_get_settings(self, api_tab):
        """Проверка получения текущих настроек"""
        api_tab.base_url_input.setText('https://get.api.com/v1/')
        api_tab.api_key_input.setText('get-key')
        api_tab.provider_combo.setCurrentText('OpenAI (Cloud)')
        api_tab.api_scheme_combo.setCurrentText('OpenAI Compatible')
        
        settings = api_tab.get_settings()
        
        assert settings['base_url'] == 'https://get.api.com/v1/'
        assert settings['api_key'] == 'get-key'
        assert settings['provider'] == 'OpenAI (Cloud)'
        assert settings['api_scheme'] == 'OpenAI Compatible'


class TestSignals:
    """Тесты сигналов"""
    
    def test_settings_changed_signal(self, api_tab, qtbot):
        """Проверка сигнала changes_settings"""
        with qtbot.waitSignal(api_tab.settings_changed, timeout=1000):
            api_tab.base_url_input.setText('signal-test.api.com')
    
    def test_autosave_on_text_change(self, api_tab):
        """Проверка автосохранения при изменении текста"""
        api_tab.base_url_input.setText('auto-save.test')
        # ConfigManager должен быть вызван для сохранения
        assert api_tab.config_manager.update_api_settings.called


class TestConnectionTest:
    """Тесты проверки соединения"""
    
    @pytest.mark.asyncio
    async def test_test_connection_button_exists(self, api_tab):
        """Проверка существования кнопки теста соединения"""
        assert api_tab.test_connection_btn is not None
        assert api_tab.test_connection_btn.text() == "🔄 Тест соединения"
    
    @pytest.mark.asyncio
    async def test_connection_status_label(self, api_tab):
        """Проверка метки статуса соединения"""
        assert api_tab.connection_status_label is not None
        assert "Не проверено" in api_tab.connection_status_label.text()


class TestTooltips:
    """Тесты подсказок"""
    
    def test_provider_tooltip(self, api_tab):
        """Проверка наличия подсказки у провайдера"""
        assert api_tab.provider_combo.toolTip() != ""
    
    def test_base_url_tooltip(self, api_tab):
        """Проверка подсказки у Base URL"""
        assert api_tab.base_url_input.toolTip() != ""
    
    def test_api_key_tooltip(self, api_tab):
        """Проверка подсказки у API ключа"""
        assert api_tab.api_key_input.toolTip() != ""
    
    def test_temperature_tooltip(self, api_tab):
        """Проверка подсказки у Temperature"""
        assert api_tab.temp_slider.toolTip() != ""
    
    def test_max_tokens_tooltip(self, api_tab):
        """Проверка подсказки у Max Tokens"""
        assert api_tab.max_tokens_spinbox.toolTip() != ""


class TestProviderChange:
    """Тесты обработки смены провайдера"""
    
    def test_openai_provider_sets_url(self, api_tab):
        """Проверка установки URL для OpenAI"""
        api_tab._on_provider_changed("OpenAI (Cloud)")
        assert api_tab.base_url_input.text() == "https://api.openai.com/v1/"
        assert api_tab.base_url_input.isReadOnly()
    
    def test_gemini_provider_sets_url(self, api_tab):
        """Проверка установки URL для Gemini"""
        api_tab._on_provider_changed("Gemini (Cloud)")
        assert api_tab.base_url_input.text() == "https://generativelanguage.googleapis.com/v1beta/"
        assert api_tab.base_url_input.isReadOnly()
    
    def test_claude_provider_sets_url(self, api_tab):
        """Проверка установки URL для Claude"""
        api_tab._on_provider_changed("Claude (Cloud)")
        assert api_tab.base_url_input.text() == "https://api.anthropic.com/v1/"
        assert api_tab.base_url_input.isReadOnly()
    
    def test_custom_provider_allows_edit(self, api_tab):
        """Проверка разблокировки URL для Custom"""
        api_tab._on_provider_changed("Custom (Local/Proxy)")
        assert api_tab.base_url_input.text() == ""
        assert not api_tab.base_url_input.isReadOnly()
    
    def test_provider_sets_scheme(self, api_tab):
        """Проверка установки схемы API при смене провайдера"""
        api_tab._on_provider_changed("OpenAI (Cloud)")
        assert api_tab.api_scheme_combo.currentText() == "OpenAI Compatible"
        
        api_tab._on_provider_changed("Gemini (Cloud)")
        assert api_tab.api_scheme_combo.currentText() == "Gemini Native"
        
        api_tab._on_provider_changed("Claude (Cloud)")
        assert api_tab.api_scheme_combo.currentText() == "Claude API"
        
        api_tab._on_provider_changed("Custom (Local/Proxy)")
        assert api_tab.api_scheme_combo.currentText() == "Custom Schema"
    
    def test_provider_change_triggers_save(self, api_tab):
        """Проверка сохранения при смене провайдера"""
        api_tab._on_provider_changed("OpenAI (Cloud)")
        assert api_tab.config_manager.update_api_settings.called


class TestStyles:
    """Тесты стилизации"""
    
    def test_apply_styles(self, api_tab):
        """Проверка применения стилей"""
        # Проверяем что стили применены к group boxes
        assert "QGroupBox" in api_tab.provider_group.styleSheet()
        assert "border-radius" in api_tab.provider_group.styleSheet()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=ui.tabs.api_tab', '--cov-report=html'])
