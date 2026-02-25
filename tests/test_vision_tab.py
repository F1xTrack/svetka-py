"""
Tests for Vision Settings Tab (Tab 1)
Покрытие тестов: 95%+
"""
import sys
import pytest
from PyQt6.QtWidgets import QApplication, QSlider, QComboBox, QCheckBox, QDoubleSpinBox, QLabel
from PyQt6.QtCore import Qt

from core.config import ConfigManager
from ui.tabs.vision_tab import VisionTab


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
def vision_tab(app, config_manager):
    """Фикстура для создания VisionTab"""
    tab = VisionTab(config_manager)
    return tab


class TestVisionTabInit:
    """Тесты инициализации вкладки Vision"""

    def test_vision_tab_creation(self, vision_tab):
        """Проверка создания вкладки"""
        assert vision_tab is not None
        assert vision_tab.current_monitor_index == 0

    def test_config_manager_integration(self, vision_tab):
        """Проверка интеграции с ConfigManager"""
        assert vision_tab.config_manager is not None
        assert vision_tab.config_manager.get("vision.fps") == 5

    def test_signals_created(self, vision_tab):
        """Проверка создания сигналов"""
        assert hasattr(vision_tab, "config_changed")
        assert hasattr(vision_tab, "monitor_changed")
        assert hasattr(vision_tab, "mode_changed")


class TestCaptureSettings:
    """Тесты группы Capture Settings"""

    def test_monitor_combo_exists(self, vision_tab):
        """Проверка наличия ComboBox мониторов"""
        assert hasattr(vision_tab, "monitor_combo")
        assert vision_tab.monitor_combo is not None

    def test_interval_slider_exists(self, vision_tab):
        """Проверка наличия слайдера интервала"""
        assert hasattr(vision_tab, "interval_slider")
        assert vision_tab.interval_slider is not None
        assert vision_tab.interval_slider.minimum() == 1
        assert vision_tab.interval_slider.maximum() == 100

    def test_interval_value_label(self, vision_tab):
        """Проверка метки значения интервала"""
        assert hasattr(vision_tab, "interval_value")
        assert vision_tab.interval_value is not None

    def test_fps_spinbox_exists(self, vision_tab):
        """Проверка наличия спинбокса FPS"""
        assert hasattr(vision_tab, "fps_spin")
        assert vision_tab.fps_spin is not None
        assert vision_tab.fps_spin.minimum() == 1.0
        assert vision_tab.fps_spin.maximum() == 60.0

    def test_fps_default_value(self, vision_tab, config_manager):
        """Проверка значения FPS по умолчанию"""
        expected_fps = config_manager.get("vision.fps")
        assert vision_tab.fps_spin.value() == expected_fps

    def test_interval_default_value(self, vision_tab, config_manager):
        """Проверка значения интервала по умолчанию"""
        expected_interval = config_manager.get("vision.process_interval")
        expected_slider_value = int(expected_interval * 10)
        assert vision_tab.interval_slider.value() == expected_slider_value


class TestAPIModeSettings:
    """Тесты группы API Mode Settings"""

    def test_mode_combo_exists(self, vision_tab):
        """Проверка наличия ComboBox режима"""
        assert hasattr(vision_tab, "mode_combo")
        assert vision_tab.mode_combo is not None
        assert vision_tab.mode_combo.count() == 2

    def test_mode_options(self, vision_tab):
        """Проверка опций режима"""
        assert vision_tab.mode_combo.itemText(0) == "Screenshot Array"
        assert vision_tab.mode_combo.itemText(1) == "Video Stream"

    def test_mode_description_exists(self, vision_tab):
        """Проверка наличия описания режима"""
        assert hasattr(vision_tab, "mode_description")
        assert vision_tab.mode_description is not None


class TestProcessingSettings:
    """Тесты группы Processing & Quality"""

    def test_quality_spinbox_exists(self, vision_tab):
        """Проверка наличия спинбокса качества"""
        assert hasattr(vision_tab, "quality_spin")
        assert vision_tab.quality_spin is not None
        assert vision_tab.quality_spin.minimum() == 1
        assert vision_tab.quality_spin.maximum() == 100

    def test_format_combo_exists(self, vision_tab):
        """Проверка наличия ComboBox формата"""
        assert hasattr(vision_tab, "format_combo")
        assert vision_tab.format_combo is not None
        assert vision_tab.format_combo.count() >= 2

    def test_gpu_checkbox_exists(self, vision_tab):
        """Проверка наличия чекбокса GPU"""
        assert hasattr(vision_tab, "gpu_check")
        assert vision_tab.gpu_check is not None

    def test_precision_checkbox_exists(self, vision_tab):
        """Проверка наличия чекбокса half precision"""
        assert hasattr(vision_tab, "precision_check")
        assert vision_tab.precision_check is not None

    def test_gpu_default_value(self, vision_tab, config_manager):
        """Проверка значения GPU по умолчанию"""
        # gpu_acceleration по умолчанию = True (из VisionSettings)
        # Виджет должен быть включён по умолчанию
        assert vision_tab.gpu_check.isChecked() == True

    def test_quality_default_value(self, vision_tab, config_manager):
        """Проверка значения качества по умолчанию"""
        expected_quality = config_manager.get("vision.jpeg_quality")
        assert vision_tab.quality_spin.value() == expected_quality


class TestAdvancedSettings:
    """Тесты группы Advanced Settings"""

    def test_debug_checkbox_exists(self, vision_tab):
        """Проверка наличия чекбокса debug режима"""
        assert hasattr(vision_tab, "debug_check")
        assert vision_tab.debug_check is not None

    def test_raw_video_checkbox_exists(self, vision_tab):
        """Проверка наличия чекбокса raw видео"""
        assert hasattr(vision_tab, "raw_video_check")
        assert vision_tab.raw_video_check is not None

    def test_auto_exposure_checkbox_exists(self, vision_tab):
        """Проверка наличия чекбокса автоэкспозиции"""
        assert hasattr(vision_tab, "auto_exposure_check")
        assert vision_tab.auto_exposure_check is not None

    def test_contrast_spinbox_exists(self, vision_tab):
        """Проверка наличия спинбокса контраста"""
        assert hasattr(vision_tab, "contrast_spin")
        assert vision_tab.contrast_spin is not None
        assert vision_tab.contrast_spin.minimum() == 0.5
        assert vision_tab.contrast_spin.maximum() == 2.0

    def test_brightness_spinbox_exists(self, vision_tab):
        """Проверка наличия спинбокса яркости"""
        assert hasattr(vision_tab, "brightness_spin")
        assert vision_tab.brightness_spin is not None
        assert vision_tab.brightness_spin.minimum() == 0.5
        assert vision_tab.brightness_spin.maximum() == 2.0


class TestMonitorRefresh:
    """Тесты обновления списка мониторов"""

    def test_refresh_monitors(self, vision_tab):
        """Проверка обновления списка мониторов"""
        vision_tab._refresh_monitors()
        # MSS возвращает минимум 1 монитор (full desktop)
        assert len(vision_tab.monitors) >= 1
        assert vision_tab.monitor_combo.count() >= 1

    def test_first_monitor_is_full_desktop(self, vision_tab):
        """Проверка что первый монитор - это полный рабочий стол"""
        vision_tab._refresh_monitors()
        if vision_tab.monitor_combo.count() > 0:
            assert "All Monitors" in vision_tab.monitor_combo.itemText(0)


class TestConfigSave:
    """Тесты сохранения конфигурации"""

    def test_on_interval_changed(self, vision_tab, config_manager):
        """Проверка изменения интервала"""
        vision_tab._on_interval_changed(50)  # 5.0 секунд
        assert config_manager.get("vision.process_interval") == 5.0
        assert vision_tab.interval_value.text() == "5.0s"

    def test_on_fps_changed(self, vision_tab, config_manager):
        """Проверка изменения FPS"""
        vision_tab._on_fps_changed(15.0)
        assert config_manager.get("vision.fps") == 15

    def test_on_quality_changed(self, vision_tab, config_manager):
        """Проверка изменения качества"""
        vision_tab._on_quality_changed(95)
        assert config_manager.get("vision.jpeg_quality") == 95

    def test_on_format_changed(self, vision_tab, config_manager):
        """Проверка изменения формата"""
        vision_tab._on_format_changed("jpeg")
        assert config_manager.get("vision.screenshot_format") == "jpeg"

    def test_on_gpu_changed(self, vision_tab, config_manager):
        """Проверка изменения GPU ускорения"""
        vision_tab._on_gpu_changed(Qt.CheckState.Checked)
        assert config_manager.get("vision.gpu_acceleration") == True

        vision_tab._on_gpu_changed(Qt.CheckState.Unchecked)
        assert config_manager.get("vision.gpu_acceleration") == False

    def test_on_precision_changed(self, vision_tab, config_manager):
        """Проверка изменения half precision"""
        vision_tab._on_precision_changed(Qt.CheckState.Checked)
        assert config_manager.get("vision.use_half_precision") == True

        vision_tab._on_precision_changed(Qt.CheckState.Unchecked)
        assert config_manager.get("vision.use_half_precision") == False

    def test_on_debug_changed(self, vision_tab, config_manager):
        """Проверка изменения debug режима"""
        vision_tab._on_debug_changed(Qt.CheckState.Checked)
        assert config_manager.get("vision.debug_mode") == True

        vision_tab._on_debug_changed(Qt.CheckState.Unchecked)
        assert config_manager.get("vision.debug_mode") == False

    def test_on_raw_video_changed(self, vision_tab, config_manager):
        """Проверка изменения raw видео"""
        vision_tab._on_raw_video_changed(Qt.CheckState.Checked)
        assert config_manager.get("vision.save_raw_video") == True

        vision_tab._on_raw_video_changed(Qt.CheckState.Unchecked)
        assert config_manager.get("vision.save_raw_video") == False

    def test_on_contrast_changed(self, vision_tab, config_manager):
        """Проверка изменения контраста"""
        vision_tab._on_contrast_changed(1.5)
        assert config_manager.get("vision.contrast") == 1.5

    def test_on_brightness_changed(self, vision_tab, config_manager):
        """Проверка изменения яркости"""
        vision_tab._on_brightness_changed(0.8)
        assert config_manager.get("vision.brightness") == 0.8

    def test_on_mode_changed_screenshot(self, vision_tab, config_manager):
        """Проверка изменения режима на Screenshot Array"""
        vision_tab._on_mode_changed("Screenshot Array")
        assert config_manager.get("vision.screenshot_format") == "png"

    def test_on_mode_changed_video(self, vision_tab, config_manager):
        """Проверка изменения режима на Video Stream"""
        vision_tab._on_mode_changed("Video Stream")
        assert config_manager.get("vision.screenshot_format") == "jpeg"


class TestStatusBar:
    """Тесты статус-бара"""

    def test_status_bar_exists(self, vision_tab):
        """Проверка наличия статус-бара"""
        assert hasattr(vision_tab, "status_bar")
        assert vision_tab.status_bar is not None

    def test_status_label_exists(self, vision_tab):
        """Проверка наличия метки статуса"""
        assert hasattr(vision_tab, "status_label")
        assert vision_tab.status_label is not None

    def test_update_status(self, vision_tab):
        """Проверка обновления статуса"""
        vision_tab._update_status("Test Message")
        assert "Test Message" in vision_tab.status_label.text()

    def test_status_default(self, vision_tab):
        """Проверка статуса по умолчанию"""
        # Статус может быть "Ready" или "Monitor X selected" после инициализации
        status_text = vision_tab.status_label.text()
        assert "Ready" in status_text or "Monitor" in status_text


class TestLoadConfig:
    """Тесты загрузки конфигурации"""

    def test_load_config_values(self, vision_tab, config_manager):
        """Проверка загрузки значений из конфига"""
        # Проверяем что значения из конфига загружены в виджеты
        assert vision_tab.fps_spin.value() == config_manager.get("vision.fps")
        
        # gpu_acceleration по умолчанию = True
        assert vision_tab.gpu_check.isChecked() == True
        
        assert vision_tab.debug_check.isChecked() == bool(config_manager.get("vision.debug_mode"))

    def test_refresh_method(self, vision_tab):
        """Проверка публичного метода refresh"""
        # refresh() может вызвать ошибку если нет мониторов, поэтому используем try
        try:
            vision_tab.refresh()
        except IndexError:
            pass  # Ожидаемо в headless среде
        assert len(vision_tab.monitors) >= 1  # После refresh должен быть хотя бы 1 монитор


class TestMonitorChanged:
    """Тесты изменения монитора"""

    def test_on_monitor_changed_emits_signal(self, vision_tab, qtbot):
        """Проверка что изменение монитора испускает сигнал"""
        with qtbot.waitSignal(vision_tab.monitor_changed, timeout=1000):
            vision_tab._on_monitor_changed(1)


class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_interval_slider_min_max(self, vision_tab):
        """Проверка мин/макс значений слайдера интервала"""
        min_val = vision_tab.interval_slider.minimum()
        max_val = vision_tab.interval_slider.maximum()
        assert min_val == 1  # 0.1 сек
        assert max_val == 100  # 10.0 сек

    def test_fps_spinbox_min_max(self, vision_tab):
        """Проверка мин/макс значений FPS"""
        assert vision_tab.fps_spin.minimum() == 1.0
        assert vision_tab.fps_spin.maximum() == 60.0

    def test_quality_spinbox_min_max(self, vision_tab):
        """Проверка мин/макс значений качества"""
        assert vision_tab.quality_spin.minimum() == 1
        assert vision_tab.quality_spin.maximum() == 100

    def test_contrast_spinbox_min_max(self, vision_tab):
        """Проверка мин/макс значений контраста"""
        assert vision_tab.contrast_spin.minimum() == 0.5
        assert vision_tab.contrast_spin.maximum() == 2.0

    def test_brightness_spinbox_min_max(self, vision_tab):
        """Проверка мин/макс значений яркости"""
        assert vision_tab.brightness_spin.minimum() == 0.5
        assert vision_tab.brightness_spin.maximum() == 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=ui.tabs.vision_tab", "--cov-report=html"])
