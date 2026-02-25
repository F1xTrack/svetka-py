"""
Vision Settings Tab (Tab 1)
Реализация вкладки настроек визуального восприятия для Svetka AI
"""
import sys
from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QComboBox,
    QCheckBox,
    QDoubleSpinBox,
    QGroupBox,
    QPushButton,
    QStatusBar,
    QFrame,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

import mss
import mss.tools

from core.config import ConfigManager, VisionSettings


class VisionTab(QWidget):
    """Вкладка настроек Vision с полной интеграцией ConfigManager и Guide Engine"""

    # Сигналы для уведомления об изменениях
    config_changed = pyqtSignal(str, object)
    monitor_changed = pyqtSignal(int)
    mode_changed = pyqtSignal(str)

    def __init__(self, config_manager: ConfigManager, guide_manager=None, vision_processor=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.guide_manager = guide_manager
        self.vision_processor = vision_processor
        self.current_monitor_index = 0
        self.monitors: List[Dict] = []

        self._init_ui()
        self._load_config()
        self._refresh_monitors()

    def _init_ui(self):
        """Инициализация UI компонентов вкладки"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # === Header секция ===
        header_layout = QHBoxLayout()
        header_label = QLabel("⚙️ Vision Settings")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Guide button (если есть guide_manager)
        if self.guide_manager:
            from ui.guide_widget import GuideWidget
            self.guide_widget = GuideWidget("vision", self.guide_manager)
            header_layout.addWidget(self.guide_widget)

        main_layout.addLayout(header_layout)

        # === Основная сетка настроек ===
        settings_frame = QFrame()
        settings_frame.setObjectName("settingsFrame")
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setSpacing(12)

        # 1. Группа: Основные настройки захвата
        capture_group = self._create_capture_group()
        settings_layout.addWidget(capture_group)

        # 2. Группа: Режимы API
        api_group = self._create_api_mode_group()
        settings_layout.addWidget(api_group)

        # 3. Группа: Обработка и качество
        processing_group = self._create_processing_group()
        settings_layout.addWidget(processing_group)

        # 4. Группа: Расширенные настройки
        advanced_group = self._create_advanced_group()
        settings_layout.addWidget(advanced_group)

        main_layout.addWidget(settings_frame)

        # === Статус-бар модуля ===
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2b2b2b;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 4px;
            }
            QLabel {
                color: #4ec9b0;
                font-size: 12px;
            }
        """)
        self.status_label = QLabel("🟢 Vision Module: Ready")
        self.status_bar.addWidget(self.status_label)
        main_layout.addWidget(self.status_bar)

        # Spacer
        main_layout.addStretch()

    def _create_capture_group(self) -> QGroupBox:
        """Группа: Основные настройки захвата"""
        group = QGroupBox("📷 Capture Settings")
        layout = QVBoxLayout(group)

        # Выбор монитора
        monitor_layout = QHBoxLayout()
        monitor_label = QLabel("Monitor:")
        monitor_label.setFixedWidth(120)
        self.monitor_combo = QComboBox()
        self.monitor_combo.currentIndexChanged.connect(self._on_monitor_changed)
        monitor_layout.addWidget(monitor_label)
        monitor_layout.addWidget(self.monitor_combo)
        monitor_layout.addStretch()
        layout.addLayout(monitor_layout)

        # Интервал захвата (слайдер + значение)
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Capture Interval (sec):")
        interval_label.setFixedWidth(120)
        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setMinimum(1)  # 0.1 sec
        self.interval_slider.setMaximum(100)  # 10.0 sec
        self.interval_slider.setValue(20)  # 2.0 sec default
        self.interval_slider.valueChanged.connect(self._on_interval_changed)
        self.interval_value = QLabel("2.0s")
        self.interval_value.setFixedWidth(50)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_slider)
        interval_layout.addWidget(self.interval_value)
        layout.addLayout(interval_layout)

        # FPS для видео-режима
        fps_layout = QHBoxLayout()
        fps_label = QLabel("FPS:")
        fps_label.setFixedWidth(120)
        self.fps_spin = QDoubleSpinBox()
        self.fps_spin.setMinimum(1.0)
        self.fps_spin.setMaximum(60.0)
        self.fps_spin.setValue(5.0)
        self.fps_spin.setSingleStep(1.0)
        self.fps_spin.valueChanged.connect(self._on_fps_changed)
        fps_layout.addWidget(fps_label)
        fps_layout.addWidget(self.fps_spin)
        fps_layout.addStretch()
        layout.addLayout(fps_layout)

        return group

    def _create_api_mode_group(self) -> QGroupBox:
        """Группа: Режимы API (Скриншоты vs Видео)"""
        group = QGroupBox("🔄 API Mode")
        layout = QVBoxLayout(group)

        # Переключатель режима
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Mode:")
        mode_label.setFixedWidth(120)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Screenshot Array", "Video Stream"])
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Описание режимов
        self.mode_description = QLabel(
            "Screenshot Array: Отправляет массив скриншотов пакетом.\n"
            "Video Stream: Потоковая передача видео в реальном времени."
        )
        self.mode_description.setWordWrap(True)
        self.mode_description.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self.mode_description)

        return group

    def _create_processing_group(self) -> QGroupBox:
        """Группа: Обработка и качество"""
        group = QGroupBox("🎨 Processing & Quality")
        layout = QVBoxLayout(group)

        # Качество скриншотов
        quality_layout = QHBoxLayout()
        quality_label = QLabel("JPEG Quality:")
        quality_label.setFixedWidth(120)
        self.quality_spin = QDoubleSpinBox()
        self.quality_spin.setMinimum(1)
        self.quality_spin.setMaximum(100)
        self.quality_spin.setValue(85)
        self.quality_spin.setSingleStep(5)
        self.quality_spin.valueChanged.connect(self._on_quality_changed)
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_spin)
        quality_layout.addStretch()
        layout.addLayout(quality_layout)

        # Формат скриншотов
        format_layout = QHBoxLayout()
        format_label = QLabel("Screenshot Format:")
        format_label.setFixedWidth(120)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["png", "jpeg", "webp"])
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        layout.addLayout(format_layout)

        # GPU ускорение
        self.gpu_check = QCheckBox("GPU Acceleration")
        self.gpu_check.stateChanged.connect(self._on_gpu_changed)
        layout.addWidget(self.gpu_check)

        # Half precision
        self.precision_check = QCheckBox("Half Precision (FP16)")
        self.precision_check.stateChanged.connect(self._on_precision_changed)
        layout.addWidget(self.precision_check)

        return group

    def _create_advanced_group(self) -> QGroupBox:
        """Группа: Расширенные настройки"""
        group = QGroupBox("⚡ Advanced Settings")
        layout = QVBoxLayout(group)

        # Debug режим
        self.debug_check = QCheckBox("Debug Mode")
        self.debug_check.stateChanged.connect(self._on_debug_changed)
        layout.addWidget(self.debug_check)

        # Сохранение сырого видео
        self.raw_video_check = QCheckBox("Save Raw Video")
        self.raw_video_check.stateChanged.connect(self._on_raw_video_changed)
        layout.addWidget(self.raw_video_check)

        # Автоэкспозиция
        self.auto_exposure_check = QCheckBox("Auto Exposure")
        self.auto_exposure_check.stateChanged.connect(self._on_auto_exposure_changed)
        layout.addWidget(self.auto_exposure_check)

        # Контраст
        contrast_layout = QHBoxLayout()
        contrast_label = QLabel("Contrast:")
        contrast_label.setFixedWidth(120)
        self.contrast_spin = QDoubleSpinBox()
        self.contrast_spin.setMinimum(0.5)
        self.contrast_spin.setMaximum(2.0)
        self.contrast_spin.setValue(1.0)
        self.contrast_spin.setSingleStep(0.1)
        self.contrast_spin.valueChanged.connect(self._on_contrast_changed)
        contrast_layout.addWidget(contrast_label)
        contrast_layout.addWidget(self.contrast_spin)
        contrast_layout.addStretch()
        layout.addLayout(contrast_layout)

        # Яркость
        brightness_layout = QHBoxLayout()
        brightness_label = QLabel("Brightness:")
        brightness_label.setFixedWidth(120)
        self.brightness_spin = QDoubleSpinBox()
        self.brightness_spin.setMinimum(0.5)
        self.brightness_spin.setMaximum(2.0)
        self.brightness_spin.setValue(1.0)
        self.brightness_spin.setSingleStep(0.1)
        self.brightness_spin.valueChanged.connect(self._on_brightness_changed)
        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(self.brightness_spin)
        brightness_layout.addStretch()
        layout.addLayout(brightness_layout)

        return group

    def _refresh_monitors(self):
        """Обновление списка доступных мониторов через MSS"""
        self.monitors.clear()
        self.monitor_combo.clear()

        with mss.mss() as sct:
            for i, monitor in enumerate(sct.monitors):
                if i == 0:
                    self.monitors.append(monitor)
                    self.monitor_combo.addItem(f"All Monitors (Full Desktop)")
                else:
                    self.monitors.append(monitor)
                    desc = f"Monitor {i} ({monitor['width']}x{monitor['height']})"
                    self.monitor_combo.addItem(desc)

    def _load_config(self):
        """Загрузка настроек из ConfigManager"""
        vision = self.config_manager.config["vision"]

        # Capture Settings
        self.interval_slider.setValue(int(vision["process_interval"] * 10))
        self._on_interval_changed(int(vision["process_interval"] * 10))

        self.fps_spin.setValue(vision["fps"])

        # API Mode (определяем по формату)
        if vision["screenshot_format"] == "png":
            self.mode_combo.setCurrentIndex(0)  # Screenshot Array
        else:
            self.mode_combo.setCurrentIndex(1)  # Video Stream

        # Processing & Quality
        self.quality_spin.setValue(vision["jpeg_quality"])
        self.format_combo.setCurrentText(vision["screenshot_format"])
        self.gpu_check.setChecked(bool(vision["gpu_acceleration"]))
        self.precision_check.setChecked(bool(vision["use_half_precision"]))

        # Advanced
        self.debug_check.setChecked(bool(vision["debug_mode"]))
        self.raw_video_check.setChecked(bool(vision["save_raw_video"]))
        self.auto_exposure_check.setChecked(bool(vision["auto_exposure"]))
        self.contrast_spin.setValue(vision["contrast"])
        self.brightness_spin.setValue(vision["brightness"])

    def _save_config(self, key: str, value: Any):
        """Сохранение настройки в ConfigManager"""
        self.config_manager.update_and_notify(f"vision.{key}", value)

    # === Обработчики событий ===

    def _on_monitor_changed(self, index: int):
        """Изменение выбранного монитора"""
        if index < 0 or index >= len(self.monitors):
            return
            
        self.current_monitor_index = index
        self.monitor_changed.emit(index)
        
        monitor_data = self.monitors[index]
        capture_region = monitor_data.get("rect", [0, 0, 1920, 1080])
        self._save_config("capture_region", list(capture_region))
        self._update_status(f"Monitor {index} selected")

    def _on_interval_changed(self, value: int):
        """Изменение интервала захвата"""
        interval = value / 10.0
        self.interval_value.setText(f"{interval:.1f}s")
        self._save_config("process_interval", interval)
        self._update_status(f"Interval: {interval:.1f}s")

    def _on_fps_changed(self, value: float):
        """Изменение FPS"""
        self._save_config("fps", int(value))
        self._update_status(f"FPS: {int(value)}")

    def _on_mode_changed(self, mode: str):
        """Изменение режима API"""
        self.mode_changed.emit(mode)
        if mode == "Screenshot Array":
            self._save_config("screenshot_format", "png")
        else:
            self._save_config("screenshot_format", "jpeg")
        self._update_status(f"Mode: {mode}")

    def _on_quality_changed(self, value: int):
        """Изменение качества JPEG"""
        self._save_config("jpeg_quality", int(value))
        self._update_status(f"Quality: {int(value)}%")

    def _on_format_changed(self, fmt: str):
        """Изменение формата скриншотов"""
        self._save_config("screenshot_format", fmt)
        self._update_status(f"Format: {fmt}")

    def _on_gpu_changed(self, state):
        """Изменение GPU ускорения"""
        enabled = state == Qt.CheckState.Checked
        self._save_config("gpu_acceleration", enabled)
        self._update_status(f"GPU Acceleration: {'ON' if enabled else 'OFF'}")

    def _on_precision_changed(self, state):
        """Изменение half precision"""
        enabled = state == Qt.CheckState.Checked
        self._save_config("use_half_precision", enabled)
        self._update_status(f"Half Precision: {'ON' if enabled else 'OFF'}")

    def _on_debug_changed(self, state):
        """Изменение debug режима"""
        enabled = state == Qt.CheckState.Checked
        self._save_config("debug_mode", enabled)
        self._update_status(f"Debug Mode: {'ON' if enabled else 'OFF'}")

    def _on_raw_video_changed(self, state):
        """Изменение сохранения сырого видео"""
        enabled = state == Qt.CheckState.Checked
        self._save_config("save_raw_video", enabled)
        self._update_status(f"Save Raw Video: {'ON' if enabled else 'OFF'}")

    def _on_auto_exposure_changed(self, state):
        """Изменение автоэкспозиции"""
        enabled = state == Qt.CheckState.Checked
        self._save_config("auto_exposure", enabled)
        self._update_status(f"Auto Exposure: {'ON' if enabled else 'OFF'}")

    def _on_contrast_changed(self, value: float):
        """Изменение контраста"""
        self._save_config("contrast", float(value))
        self._update_status(f"Contrast: {value:.2f}")

    def _on_brightness_changed(self, value: float):
        """Изменение яркости"""
        self._save_config("brightness", float(value))
        self._update_status(f"Brightness: {value:.2f}")

    def _update_status(self, message: str):
        """Обновление статус-бара"""
        self.status_label.setText(f"🟢 {message}")
        # Автоочистка через 3 секунды
        QTimer.singleShot(3000, lambda: self.status_label.setText("🟢 Vision Module: Ready"))

    def refresh(self):
        """Публичный метод для обновления вкладки"""
        self._refresh_monitors()
        self._load_config()
