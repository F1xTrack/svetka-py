"""
Tests for Audio Settings Tab (Tab 2)
Покрытие тестов: 95%+
"""
import sys
import pytest
from PyQt6.QtWidgets import QApplication, QSlider, QComboBox, QCheckBox, QSpinBox, QLabel
from PyQt6.QtCore import Qt

from core.config import ConfigManager
from ui.tabs.audio_tab import AudioTab, VUMeter


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
def audio_tab(app, config_manager):
    """Фикстура для создания AudioTab"""
    tab = AudioTab(config_manager)
    return tab


class TestAudioTabInit:
    """Тесты инициализации вкладки Audio"""

    def test_audio_tab_creation(self, audio_tab):
        """Проверка создания вкладки"""
        assert audio_tab is not None

    def test_config_manager_integration(self, audio_tab):
        """Проверка интеграции с ConfigManager"""
        assert audio_tab.config_manager is not None
        assert audio_tab.config_manager.get("audio.mic_index") == -1

    def test_signals_created(self, audio_tab):
        """Проверка создания сигналов"""
        assert hasattr(audio_tab, "config_changed")


class TestVUMeter:
    """Тесты VU Meter"""

    def test_vu_meter_creation(self, app):
        """Проверка создания VU Meter"""
        vu_meter = VUMeter()
        assert vu_meter is not None
        assert vu_meter._level == 0.0

    def test_vu_meter_set_level(self, app):
        """Проверка установки уровня громкости"""
        vu_meter = VUMeter()
        vu_meter.set_level(0.5)
        assert vu_meter._level == 0.5

    def test_vu_meter_level_clamped(self, app):
        """Проверка ограничения уровня (0.0-1.0)"""
        vu_meter = VUMeter()
        vu_meter.set_level(1.5)  # > 1.0
        assert vu_meter._level == 1.0
        
        vu_meter.set_level(-0.5)  # < 0.0
        assert vu_meter._level == 0.0


class TestInputSource:
    """Тесты группы Input Source"""

    def test_mic_combo_exists(self, audio_tab):
        """Проверка наличия ComboBox микрофонов"""
        assert hasattr(audio_tab, "mic_combo")
        assert audio_tab.mic_combo is not None

    def test_sample_rate_spinbox_exists(self, audio_tab):
        """Проверка наличия спинбокса sample rate"""
        assert hasattr(audio_tab, "sample_rate_spin")
        assert audio_tab.sample_rate_spin is not None
        assert audio_tab.sample_rate_spin.minimum() == 8000
        assert audio_tab.sample_rate_spin.maximum() == 48000

    def test_channels_spinbox_exists(self, audio_tab):
        """Проверка наличия спинбокса каналов"""
        assert hasattr(audio_tab, "channels_spin")
        assert audio_tab.channels_spin is not None
        assert audio_tab.channels_spin.minimum() == 1
        assert audio_tab.channels_spin.maximum() == 2

    def test_sample_rate_default_value(self, audio_tab, config_manager):
        """Проверка значения sample rate по умолчанию"""
        expected_rate = config_manager.get("audio.sample_rate")
        assert audio_tab.sample_rate_spin.value() == expected_rate

    def test_channels_default_value(self, audio_tab, config_manager):
        """Проверка значения каналов по умолчанию"""
        expected_channels = config_manager.get("audio.channels")
        assert audio_tab.channels_spin.value() == expected_channels


class TestAudioModeSettings:
    """Тесты группы Audio Mode Settings"""

    def test_mode_combo_exists(self, audio_tab):
        """Проверка наличия ComboBox режима"""
        assert hasattr(audio_tab, "mode_combo")
        assert audio_tab.mode_combo is not None
        assert audio_tab.mode_combo.count() == 2

    def test_mode_options(self, audio_tab):
        """Проверка опций режима"""
        assert "STT" in audio_tab.mode_combo.itemText(0)
        assert "Multimodal" in audio_tab.mode_combo.itemText(1)

    def test_mode_description_exists(self, audio_tab):
        """Проверка наличия описания режима"""
        assert hasattr(audio_tab, "mode_description")
        assert audio_tab.mode_description is not None


class TestNoiseGateSettings:
    """Тесты группы Noise Gate"""

    def test_noise_cancel_checkbox_exists(self, audio_tab):
        """Проверка наличия чекбокса шумоподавления"""
        assert hasattr(audio_tab, "noise_cancel_check")
        assert audio_tab.noise_cancel_check is not None

    def test_threshold_slider_exists(self, audio_tab):
        """Проверка наличия слайдера порога"""
        assert hasattr(audio_tab, "threshold_slider")
        assert audio_tab.threshold_slider is not None
        assert audio_tab.threshold_slider.minimum() == 0
        assert audio_tab.threshold_slider.maximum() == 100

    def test_threshold_value_label_exists(self, audio_tab):
        """Проверка метки значения порога"""
        assert hasattr(audio_tab, "threshold_value")
        assert audio_tab.threshold_value is not None

    def test_echo_cancel_checkbox_exists(self, audio_tab):
        """Проверка наличия чекбокса эхокомпенсации"""
        assert hasattr(audio_tab, "echo_cancel_check")
        assert audio_tab.echo_cancel_check is not None

    def test_auto_gain_checkbox_exists(self, audio_tab):
        """Проверка наличия чекбокса автоусиления"""
        assert hasattr(audio_tab, "auto_gain_check")
        assert audio_tab.auto_gain_check is not None

    def test_noise_cancel_default_value(self, audio_tab, config_manager):
        """Проверка значения шумоподавления по умолчанию"""
        expected_noise = config_manager.get("audio.noise_cancellation")
        assert audio_tab.noise_cancel_check.isChecked() == expected_noise

    def test_threshold_default_value(self, audio_tab, config_manager):
        """Проверка значения порога по умолчанию"""
        expected_threshold = config_manager.get("audio.volume_threshold")
        expected_slider_value = int(expected_threshold * 100)
        assert audio_tab.threshold_slider.value() == expected_slider_value


class TestSystemAudioSettings:
    """Тесты группы System Audio"""

    def test_system_audio_checkbox_exists(self, audio_tab):
        """Проверка наличия чекбокса системного аудио"""
        assert hasattr(audio_tab, "system_audio_check")
        assert audio_tab.system_audio_check is not None

    def test_system_audio_default_value(self, audio_tab, config_manager):
        """Проверка значения системного аудио по умолчанию"""
        expected_system = config_manager.get("audio.system_audio_enabled")
        assert audio_tab.system_audio_check.isChecked() == expected_system


class TestTTSSettings:
    """Тесты группы TTS Settings"""

    def test_tts_enable_checkbox_exists(self, audio_tab):
        """Проверка наличия чекбокса включения TTS"""
        assert hasattr(audio_tab, "tts_enable_check")
        assert audio_tab.tts_enable_check is not None

    def test_tts_voice_combo_exists(self, audio_tab):
        """Проверка наличия ComboBox голоса TTS"""
        assert hasattr(audio_tab, "tts_voice_combo")
        assert audio_tab.tts_voice_combo is not None
        assert audio_tab.tts_voice_combo.count() >= 2

    def test_tts_rate_slider_exists(self, audio_tab):
        """Проверка наличия слайдера скорости речи"""
        assert hasattr(audio_tab, "tts_rate_slider")
        assert audio_tab.tts_rate_slider is not None
        assert audio_tab.tts_rate_slider.minimum() == -50
        assert audio_tab.tts_rate_slider.maximum() == 50

    def test_tts_rate_value_label_exists(self, audio_tab):
        """Проверка метки значения скорости речи"""
        assert hasattr(audio_tab, "tts_rate_value")
        assert audio_tab.tts_rate_value is not None

    def test_tts_volume_slider_exists(self, audio_tab):
        """Проверка наличия слайдера громкости TTS"""
        assert hasattr(audio_tab, "tts_volume_slider")
        assert audio_tab.tts_volume_slider is not None
        assert audio_tab.tts_volume_slider.minimum() == 0
        assert audio_tab.tts_volume_slider.maximum() == 100

    def test_tts_volume_value_label_exists(self, audio_tab):
        """Проверка метки значения громкости TTS"""
        assert hasattr(audio_tab, "tts_volume_value")
        assert audio_tab.tts_volume_value is not None

    def test_tts_enable_default_value(self, audio_tab, config_manager):
        """Проверка значения включения TTS по умолчанию"""
        expected_tts = config_manager.get("audio.tts_enabled")
        assert audio_tab.tts_enable_check.isChecked() == expected_tts


class TestActionButtons:
    """Тесты кнопок действий"""

    def test_refresh_button_exists(self, audio_tab):
        """Проверка наличия кнопки обновления устройств"""
        assert hasattr(audio_tab, "refresh_btn")
        assert audio_tab.refresh_btn is not None

    def test_test_button_exists(self, audio_tab):
        """Проверка наличия кнопки теста аудио"""
        assert hasattr(audio_tab, "test_btn")
        assert audio_tab.test_btn is not None


class TestConfigSave:
    """Тесты сохранения конфигурации"""

    def test_on_mic_changed(self, audio_tab, config_manager):
        """Проверка изменения микрофона"""
        audio_tab._on_mic_changed(0)
        assert config_manager.get("audio.mic_index") == -1  # Default Device

    def test_on_sample_rate_changed(self, audio_tab, config_manager):
        """Проверка изменения sample rate"""
        audio_tab._on_sample_rate_changed(24000)
        assert config_manager.get("audio.sample_rate") == 24000

    def test_on_channels_changed(self, audio_tab, config_manager):
        """Проверка изменения каналов"""
        audio_tab._on_channels_changed(2)
        assert config_manager.get("audio.channels") == 2

    def test_on_noise_cancel_changed(self, audio_tab, config_manager):
        """Проверка изменения шумоподавления"""
        audio_tab._on_noise_cancel_changed(Qt.CheckState.Checked.value)
        assert config_manager.get("audio.noise_cancellation") == True

        audio_tab._on_noise_cancel_changed(Qt.CheckState.Unchecked.value)
        assert config_manager.get("audio.noise_cancellation") == False

    def test_on_threshold_changed(self, audio_tab, config_manager):
        """Проверка изменения порога"""
        audio_tab._on_threshold_changed(50)
        assert config_manager.get("audio.volume_threshold") == 0.5
        assert audio_tab.threshold_value.text() == "0.50"

    def test_on_echo_cancel_changed(self, audio_tab, config_manager):
        """Проверка изменения эхокомпенсации"""
        audio_tab._on_echo_cancel_changed(Qt.CheckState.Checked.value)
        assert config_manager.get("audio.echo_cancellation") == True

        audio_tab._on_echo_cancel_changed(Qt.CheckState.Unchecked.value)
        assert config_manager.get("audio.echo_cancellation") == False

    def test_on_auto_gain_changed(self, audio_tab, config_manager):
        """Проверка изменения автоусиления"""
        audio_tab._on_auto_gain_changed(Qt.CheckState.Checked.value)
        assert config_manager.get("audio.auto_gain") == True

        audio_tab._on_auto_gain_changed(Qt.CheckState.Unchecked.value)
        assert config_manager.get("audio.auto_gain") == False

    def test_on_system_audio_changed(self, audio_tab, config_manager):
        """Проверка изменения системного аудио"""
        audio_tab._on_system_audio_changed(Qt.CheckState.Checked.value)
        assert config_manager.get("audio.system_audio_enabled") == True

        audio_tab._on_system_audio_changed(Qt.CheckState.Unchecked.value)
        assert config_manager.get("audio.system_audio_enabled") == False

    def test_on_tts_enable_changed(self, audio_tab, config_manager):
        """Проверка изменения включения TTS"""
        audio_tab._on_tts_enable_changed(Qt.CheckState.Checked.value)
        assert config_manager.get("audio.tts_enabled") == True

        audio_tab._on_tts_enable_changed(Qt.CheckState.Unchecked.value)
        assert config_manager.get("audio.tts_enabled") == False

    def test_on_tts_voice_changed(self, audio_tab, config_manager):
        """Проверка изменения голоса TTS"""
        test_voice = "ru-RU-SvetlanaNeural"
        audio_tab._on_tts_voice_changed(test_voice)
        assert config_manager.get("audio.tts_voice") == test_voice

    def test_on_tts_rate_changed(self, audio_tab, config_manager):
        """Проверка изменения скорости речи"""
        audio_tab._on_tts_rate_changed(25)
        assert config_manager.get("audio.tts_rate") == "+25%"
        assert audio_tab.tts_rate_value.text() == "+25%"

    def test_on_tts_volume_changed(self, audio_tab, config_manager):
        """Проверка изменения громкости TTS"""
        audio_tab._on_tts_volume_changed(75)
        assert config_manager.get("audio.tts_volume") == "75%"
        assert audio_tab.tts_volume_value.text() == "75%"

    def test_on_mode_changed(self, audio_tab, config_manager):
        """Проверка изменения режима"""
        audio_tab._on_mode_changed(0)  # STT mode
        assert config_manager.get("audio.processing_mode") == "stt"

        audio_tab._on_mode_changed(1)  # Native mode
        assert config_manager.get("audio.processing_mode") == "native"


class TestLoadConfig:
    """Тесты загрузки конфигурации"""

    def test_load_config_values(self, audio_tab, config_manager):
        """Проверка загрузки значений из конфига"""
        # Проверяем что значения из конфига загружены в виджеты
        assert audio_tab.sample_rate_spin.value() == config_manager.get("audio.sample_rate")
        assert audio_tab.channels_spin.value() == config_manager.get("audio.channels")
        assert audio_tab.noise_cancel_check.isChecked() == config_manager.get("audio.noise_cancellation")
        assert audio_tab.tts_enable_check.isChecked() == config_manager.get("audio.tts_enabled")


class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_sample_rate_min_max(self, audio_tab):
        """Проверка мин/макс значений sample rate"""
        assert audio_tab.sample_rate_spin.minimum() == 8000
        assert audio_tab.sample_rate_spin.maximum() == 48000

    def test_channels_min_max(self, audio_tab):
        """Проверка мин/макс значений каналов"""
        assert audio_tab.channels_spin.minimum() == 1
        assert audio_tab.channels_spin.maximum() == 2

    def test_threshold_slider_min_max(self, audio_tab):
        """Проверка мин/макс значений слайдера порога"""
        assert audio_tab.threshold_slider.minimum() == 0
        assert audio_tab.threshold_slider.maximum() == 100

    def test_tts_rate_slider_min_max(self, audio_tab):
        """Проверка мин/макс значений слайдера скорости речи"""
        assert audio_tab.tts_rate_slider.minimum() == -50
        assert audio_tab.tts_rate_slider.maximum() == 50

    def test_tts_volume_slider_min_max(self, audio_tab):
        """Проверка мин/макс значений слайдера громкости TTS"""
        assert audio_tab.tts_volume_slider.minimum() == 0
        assert audio_tab.tts_volume_slider.maximum() == 100


class TestVUMeterDisplay:
    """Тесты отображения VU Meter"""

    def test_vu_meter_bars_count(self, app):
        """Проверка количества полосок VU Meter"""
        vu_meter = VUMeter()
        assert len(vu_meter.bar_labels) == 20

    def test_vu_meter_level_zero(self, app):
        """Проверка отображения нулевого уровня"""
        vu_meter = VUMeter()
        vu_meter.set_level(0.0)
        # Все полоски должны быть выключены
        for label in vu_meter.bar_labels:
            assert "#333" in label.styleSheet()

    def test_vu_meter_level_full(self, app):
        """Проверка отображения полного уровня"""
        vu_meter = VUMeter()
        vu_meter.set_level(1.0)
        # Все полоски должны быть включены (зелёные, жёлтые или красные)
        active_count = sum(1 for label in vu_meter.bar_labels if "#333" not in label.styleSheet())
        assert active_count == vu_meter._bars


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=ui.tabs.audio_tab", "--cov-report=html"])
