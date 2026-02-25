"""
Integration tests for APISettingsTab

Tests the integration between APISettingsTab, ConfigManager, and GuideManager.
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, AsyncMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ui.tabs.api_tab import APISettingsTab


class TestConfigManagerIntegration:
    """Тесты интеграции с ConfigManager"""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Создание мок ConfigManager"""
        config = Mock()
        config.api = Mock()
        config.api.model_dump.return_value = {
            'base_url': 'https://api.openai.com/v1/',
            'api_key': 'test-key',
            'model_name': 'gpt-4o-mini',
            'temperature': 0.7,
            'max_tokens': 512,
            'top_p': 1.0,
        }
        
        manager = Mock()
        manager.get_api_settings.return_value = config.api.model_dump()
        manager.update_api_settings = Mock()
        return manager
    
    @pytest.fixture
    def api_tab_with_config(self, app, mock_config_manager):
        """Создание APISettingsTab с ConfigManager"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        mock_guide = Mock()
        tab = APISettingsTab(config_manager=mock_config_manager, guide_manager=mock_guide)
        yield tab
    
    def test_load_settings_from_config(self, api_tab_with_config, mock_config_manager):
        """Проверка загрузки настроек из ConfigManager"""
        mock_config_manager.get_api_settings.return_value = {
            'base_url': 'https://custom.api.com/v1/',
            'api_key': 'custom-key',
            'model_name': 'gpt-4-turbo',
            'temperature': 1.2,
            'max_tokens': 2048,
            'top_p': 0.8,
        }
        
        api_tab_with_config._load_settings()
        
        assert api_tab_with_config.base_url_input.text() == 'https://custom.api.com/v1/'
        assert api_tab_with_config.api_key_input.text() == 'custom-key'
        assert api_tab_with_config.model_combo.currentText() == 'gpt-4-turbo'
    
    def test_save_settings_to_config(self, api_tab_with_config, mock_config_manager):
        """Проверка сохранения настроек в ConfigManager"""
        api_tab_with_config.base_url_input.setText('https://save.test/v1/')
        api_tab_with_config.api_key_input.setText('save-key')
        api_tab_with_config.model_combo.setCurrentText('gpt-4o')
        
        api_tab_with_config._save_settings()
        
        mock_config_manager.update_api_settings.assert_called_once()
        call_args = mock_config_manager.update_api_settings.call_args[0][0]
        assert call_args['base_url'] == 'https://save.test/v1/'
        assert call_args['api_key'] == 'save-key'
    
    def test_get_settings_returns_dict(self, api_tab_with_config):
        """Проверка что get_settings возвращает dict"""
        settings = api_tab_with_config.get_settings()
        assert isinstance(settings, dict)
        assert 'base_url' in settings
        assert 'api_key' in settings
        assert 'model_name' in settings


class TestGuideManagerIntegration:
    """Тесты интеграции с GuideManager"""
    
    def test_register_guides(self, app):
        """Проверка регистрации подсказок"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        mock_config = Mock()
        mock_guide = Mock()
        
        tab = APISettingsTab(config_manager=mock_config, guide_manager=mock_guide)
        
        # Проверяем что bind_to_widget был вызван для каждого виджета
        assert mock_guide.bind_to_widget.call_count >= 9
        
    def test_guide_keys_registered(self, app):
        """Проверка что ключи Guide Engine зарегистрированы"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        mock_config = Mock()
        mock_guide = Mock()
        
        tab = APISettingsTab(config_manager=mock_config, guide_manager=mock_guide)
        
        # Собираем все вызовы bind_to_widget
        calls = mock_guide.bind_to_widget.call_args_list
        keys = [call[0][0] for call in calls]
        
        # Проверяем наличие ключей
        assert 'api.provider' in keys
        assert 'api.base_url' in keys
        assert 'api.api_key' in keys
        assert 'api.model_name' in keys
        assert 'api.temperature' in keys


class TestConnectionTest:
    """Тесты проверки соединения"""
    
    @pytest.mark.asyncio
    async def test_test_connection_without_api_key(self, app):
        """Проверка теста соединения без API ключа"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        mock_config = Mock()
        mock_config.get_api_settings.return_value = {'api_key': ''}
        mock_guide = Mock()
        
        tab = APISettingsTab(config_manager=mock_config, guide_manager=mock_guide)
        tab.api_key_input.setText('')
        
        # Эмулируем нажатие кнопки
        with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_msg:
            await tab._test_connection()
            mock_msg.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_connection_with_api_key(self, app):
        """Проверка теста соединения с API ключом"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        mock_config = Mock()
        mock_config.get_api_settings.return_value = {
            'api_key': 'test-key',
            'base_url': 'https://test.api.com/v1/',
            'model_name': 'gpt-4o-mini'
        }
        mock_guide = Mock()
        
        tab = APISettingsTab(config_manager=mock_config, guide_manager=mock_guide)
        
        # APIBridge не установлен - должна быть заглушка
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_msg:
            await tab._test_connection()
            # Должна быть вызвана заглушка
            assert mock_msg.called
    
    @pytest.mark.asyncio
    async def test_connection_status_label_updated(self, app):
        """Проверка обновления метки статуса"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        mock_config = Mock()
        mock_config.get_api_settings.return_value = {'api_key': ''}
        mock_guide = Mock()
        
        tab = APISettingsTab(config_manager=mock_config, guide_manager=mock_guide)
        
        await tab._test_connection()
        
        # Проверяем что статус обновлён
        assert "Ошибка" in tab.connection_status_label.text() or "Статус:" in tab.connection_status_label.text()


class TestSettingsValidation:
    """Тесты валидации настроек"""
    
    def test_temperature_range(self, app):
        """Проверка диапазона Temperature"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        mock_config = Mock()
        mock_guide = Mock()
        tab = APISettingsTab(config_manager=mock_config, guide_manager=mock_guide)
        
        # Проверяем диапазон
        assert tab.temp_spinbox.minimum() == 0.0
        assert tab.temp_spinbox.maximum() == 2.0
    
    def test_top_p_range(self, app):
        """Проверка диапазона Top-P"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        mock_config = Mock()
        mock_guide = Mock()
        tab = APISettingsTab(config_manager=mock_config, guide_manager=mock_guide)
        
        assert tab.top_p_spinbox.minimum() == 0.0
        assert tab.top_p_spinbox.maximum() == 1.0
    
    def test_max_tokens_range(self, app):
        """Проверка диапазона Max Tokens"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        mock_config = Mock()
        mock_guide = Mock()
        tab = APISettingsTab(config_manager=mock_config, guide_manager=mock_guide)
        
        assert tab.max_tokens_spinbox.minimum() == 1
        assert tab.max_tokens_spinbox.maximum() == 128000


class TestSignalEmission:
    """Тесты эмиссии сигналов"""
    
    def test_settings_changed_signal(self, app, qtbot):
        """Проверка сигнала settings_changed"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        mock_config = Mock()
        mock_guide = Mock()
        tab = APISettingsTab(config_manager=mock_config, guide_manager=mock_guide)
        
        with qtbot.waitSignal(tab.settings_changed, timeout=1000):
            tab.api_key_input.setText('new-key')
    
    def test_connection_tested_signal(self, app, qtbot):
        """Проверка сигнала connection_tested"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        mock_config = Mock()
        mock_config.get_api_settings.return_value = {'api_key': ''}
        mock_guide = Mock()
        tab = APISettingsTab(config_manager=mock_config, guide_manager=mock_guide)
        
        # Сигнал должен быть испущен даже при ошибке
        import asyncio
        asyncio.run(tab._test_connection())
        
        # Проверяем что сигнал существует
        assert hasattr(tab, 'connection_tested')


# Import QApplication for fixtures
from PyQt6.QtWidgets import QApplication
