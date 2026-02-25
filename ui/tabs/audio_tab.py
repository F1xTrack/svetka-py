"""
Audio Settings Tab (Tab 2) for Svetka AI Assistant
Реализация вкладки настроек аудио: микрофон, системный звук, STT vs Native, TTS, VUmeter
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QComboBox,
    QSlider,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QFrame,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    print("Warning: sounddevice not available. Audio device listing disabled.")


class VUMeter(QFrame):
    """Визуальный индикатор громкости микрофона (VU Meter)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 200)
        self.setMinimumHeight(150)
        self.setMaximumWidth(30)
        
        self._level = 0.0
        self._bars = 20
        
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #333;
                border-radius: 4px;
            }
        """)
        
        self.bar_labels: List[QLabel] = []
        self._init_bars()
    
    def _init_bars(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(4, 4, 4, 4)
        
        for i in range(self._bars):
            bar = QLabel("█")
            bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bar.setFont(QFont("Consolas", 8))
            bar.setStyleSheet("""
                QLabel {
                    color: #333;
                    background-color: transparent;
                }
            """)
            layout.addWidget(bar)
            self.bar_labels.append(bar)
        
        layout.addStretch()
    
    def set_level(self, level: float):
        """Установка уровня громкости (0.0 - 1.0)"""
        self._level = max(0.0, min(1.0, level))
        self._update_display()
    
    def _update_display(self):
        active_bars = int(self._level * self._bars)
        
        for i, label in enumerate(self.bar_labels):
            if i < active_bars:
                if i < self._bars * 0.7:
                    color = "#00ff00"
                elif i < self._bars * 0.85:
                    color = "#ffff00"
                else:
                    color = "#ff0000"
                
                label.setStyleSheet(f"""
                    QLabel {{
                        color: {color};
                        background-color: transparent;
                    }}
                """)
            else:
                label.setStyleSheet("""
                    QLabel {
                        color: #333;
                        background-color: transparent;
                    }
                """)


class AudioTab(QWidget):
    """
    Вкладка настроек аудио (Tab 2)
    
    Функционал:
    - Выбор микрофона с динамическим обновлением
    - Переключатель режима: Standard STT vs Native Multimodal
    - Настройки TTS (голос, громкость, скорость)
    - VUmeter для мониторинга громкости
    - Noise Gate (порог шума)
    - Системный звук
    """
    
    config_changed = pyqtSignal(str, object)
    
    def __init__(self, config_manager=None, guide_manager=None, audio_processor=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.guide_manager = guide_manager
        self.audio_processor = audio_processor
        
        self._init_ui()
        self._load_config()
        self._connect_processor()
    
    def _connect_processor(self):
        """Подключение сигналов AudioProcessor"""
        if self.audio_processor:
            self.audio_processor.volume_changed.connect(self.vu_meter.set_level)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Header с заголовком и кнопкой помощи
        header_layout = QHBoxLayout()
        title = QLabel("🎤 Audio Settings")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        if self.guide_manager:
            self.guide_btn = QPushButton("❓ Help")
            self.guide_btn.clicked.connect(lambda: self._show_guide("audio"))
            header_layout.addWidget(self.guide_btn)
        
        main_layout.addLayout(header_layout)
        
        # Основная сетка: слева настройки, справа VUmeter
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Левая колонка - настройки
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(12)
        
        # 1. Input Source Group
        input_group = self._create_input_group()
        settings_layout.addWidget(input_group)
        
        # 2. Audio Mode Group (STT vs Native)
        mode_group = self._create_mode_group()
        settings_layout.addWidget(mode_group)
        
        # 3. Noise Gate Group
        noise_group = self._create_noise_gate_group()
        settings_layout.addWidget(noise_group)
        
        # 4. System Audio Group
        system_group = self._create_system_audio_group()
        settings_layout.addWidget(system_group)
        
        # 5. TTS Group
        tts_group = self._create_tts_group()
        settings_layout.addWidget(tts_group)
        
        settings_layout.addStretch()
        content_layout.addLayout(settings_layout)
        
        # Правая колонка - VUmeter
        vu_layout = QVBoxLayout()
        vu_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        vu_label = QLabel("Input Level")
        vu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vu_label.setFont(QFont("Segoe UI", 10))
        vu_layout.addWidget(vu_label)
        
        self.vu_meter = VUMeter()
        vu_layout.addWidget(self.vu_meter)
        
        content_layout.addLayout(vu_layout)
        content_layout.setStretch(0, 1)
        
        main_layout.addLayout(content_layout)
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Refresh Devices")
        self.refresh_btn.clicked.connect(self._refresh_devices)
        actions_layout.addWidget(self.refresh_btn)
        
        self.test_btn = QPushButton("🔊 Test Audio")
        self.test_btn.clicked.connect(self._test_audio)
        actions_layout.addWidget(self.test_btn)
        
        main_layout.addLayout(actions_layout)
    
    def _create_input_group(self) -> QGroupBox:
        """Группа: Выбор микрофона"""
        group = QGroupBox("🎙️ Input Source (Микрофон)")
        layout = QVBoxLayout(group)
        
        # Выбор устройства
        device_layout = QHBoxLayout()
        device_label = QLabel("Device:")
        device_label.setFixedWidth(100)
        self.mic_combo = QComboBox()
        self.mic_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.mic_combo.currentIndexChanged.connect(self._on_mic_changed)
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.mic_combo)
        layout.addLayout(device_layout)
        
        # Sample Rate
        rate_layout = QHBoxLayout()
        rate_label = QLabel("Sample Rate:")
        rate_label.setFixedWidth(100)
        self.sample_rate_spin = QSpinBox()
        self.sample_rate_spin.setRange(8000, 48000)
        self.sample_rate_spin.setSingleStep(8000)
        self.sample_rate_spin.setValue(16000)
        self.sample_rate_spin.valueChanged.connect(self._on_sample_rate_changed)
        rate_layout.addWidget(rate_label)
        rate_layout.addWidget(self.sample_rate_spin)
        rate_layout.addStretch()
        layout.addLayout(rate_layout)
        
        # Channels
        channels_layout = QHBoxLayout()
        channels_label = QLabel("Channels:")
        channels_label.setFixedWidth(100)
        self.channels_spin = QSpinBox()
        self.channels_spin.setRange(1, 2)
        self.channels_spin.setValue(1)
        self.channels_spin.valueChanged.connect(self._on_channels_changed)
        channels_layout.addWidget(channels_label)
        channels_layout.addWidget(self.channels_spin)
        channels_layout.addStretch()
        layout.addLayout(channels_layout)
        
        return group
    
    def _create_mode_group(self) -> QGroupBox:
        """Группа: Режим обработки аудио (STT vs Native Multimodal)"""
        group = QGroupBox("🎯 Audio Processing Mode")
        layout = QVBoxLayout(group)
        
        desc = QLabel("Выберите режим обработки аудио:")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Переключатель режимов
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Standard STT (Speech-to-Text)", "stt")
        self.mode_combo.addItem("Native Multimodal (Direct Audio)", "native")
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        layout.addWidget(self.mode_combo)
        
        # Описание режимов
        self.mode_description = QLabel(
            "<b>Standard STT:</b> Использует Whisper для распознавания речи в текст.<br>"
            "<b>Native Multimodal:</b> Прямая передача аудио в модель (Gemini 2.0+)."
        )
        self.mode_description.setWordWrap(True)
        self.mode_description.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self.mode_description)
        
        return group
    
    def _create_noise_gate_group(self) -> QGroupBox:
        """Группа: Noise Gate (порог шума)"""
        group = QGroupBox("🔇 Noise Gate (Порог шума)")
        layout = QVBoxLayout(group)
        
        # Включение шумоподавления
        self.noise_cancel_check = QCheckBox("Enable Noise Cancellation")
        self.noise_cancel_check.stateChanged.connect(self._on_noise_cancel_changed)
        layout.addWidget(self.noise_cancel_check)
        
        # Порог громкости
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("Volume Threshold:")
        threshold_label.setFixedWidth(120)
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(0, 100)
        self.threshold_slider.setValue(1)
        self.threshold_slider.valueChanged.connect(self._on_threshold_changed)
        self.threshold_value = QLabel("0.01")
        self.threshold_value.setFixedWidth(50)
        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_value)
        layout.addLayout(threshold_layout)
        
        # Echo Cancellation
        self.echo_cancel_check = QCheckBox("Enable Echo Cancellation")
        self.echo_cancel_check.stateChanged.connect(self._on_echo_cancel_changed)
        layout.addWidget(self.echo_cancel_check)
        
        # Auto Gain
        self.auto_gain_check = QCheckBox("Enable Auto Gain")
        self.auto_gain_check.stateChanged.connect(self._on_auto_gain_changed)
        layout.addWidget(self.auto_gain_check)
        
        return group
    
    def _create_system_audio_group(self) -> QGroupBox:
        """Группа: Системный звук (Loopback)"""
        group = QGroupBox("🔊 System Audio (Loopback)")
        layout = QVBoxLayout(group)
        
        self.system_audio_check = QCheckBox("Enable System Audio Capture")
        self.system_audio_check.stateChanged.connect(self._on_system_audio_changed)
        layout.addWidget(self.system_audio_check)
        
        desc = QLabel(
            "Захват звука из динамиков/наушников (Windows WASAPI Loopback)."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(desc)
        
        return group
    
    def _create_tts_group(self) -> QGroupBox:
        """Группа: TTS (Text-to-Speech) настройки"""
        group = QGroupBox("🗣️ Text-to-Speech (TTS)")
        layout = QVBoxLayout(group)
        
        # Включение TTS
        self.tts_enable_check = QCheckBox("Enable TTS")
        self.tts_enable_check.stateChanged.connect(self._on_tts_enable_changed)
        layout.addWidget(self.tts_enable_check)
        
        # Выбор голоса
        voice_layout = QHBoxLayout()
        voice_label = QLabel("Voice:")
        voice_label.setFixedWidth(100)
        self.tts_voice_combo = QComboBox()
        self.tts_voice_combo.setEditable(True)
        self.tts_voice_combo.addItem("en-US-GuyNeural", "en-US-GuyNeural")
        self.tts_voice_combo.addItem("en-US-JennyNeural", "en-US-JennyNeural")
        self.tts_voice_combo.addItem("en-US-AriaNeural", "en-US-AriaNeural")
        self.tts_voice_combo.addItem("ru-RU-DmitryNeural", "ru-RU-DmitryNeural")
        self.tts_voice_combo.addItem("ru-RU-SvetlanaNeural", "ru-RU-SvetlanaNeural")
        self.tts_voice_combo.currentTextChanged.connect(self._on_tts_voice_changed)
        voice_layout.addWidget(voice_label)
        voice_layout.addWidget(self.tts_voice_combo)
        layout.addLayout(voice_layout)
        
        # Скорость речи
        rate_layout = QHBoxLayout()
        rate_label = QLabel("Speech Rate:")
        rate_label.setFixedWidth(100)
        self.tts_rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.tts_rate_slider.setRange(-50, 50)
        self.tts_rate_slider.setValue(0)
        self.tts_rate_slider.valueChanged.connect(self._on_tts_rate_changed)
        self.tts_rate_value = QLabel("+0%")
        self.tts_rate_value.setFixedWidth(50)
        rate_layout.addWidget(rate_label)
        rate_layout.addWidget(self.tts_rate_slider)
        rate_layout.addWidget(self.tts_rate_value)
        layout.addLayout(rate_layout)
        
        # Громкость TTS
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volume:")
        volume_label.setFixedWidth(100)
        self.tts_volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.tts_volume_slider.setRange(0, 100)
        self.tts_volume_slider.setValue(100)
        self.tts_volume_slider.valueChanged.connect(self._on_tts_volume_changed)
        self.tts_volume_value = QLabel("100%")
        self.tts_volume_value.setFixedWidth(50)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.tts_volume_slider)
        volume_layout.addWidget(self.tts_volume_value)
        layout.addLayout(volume_layout)
        
        return group
    
    def _load_config(self):
        """Загрузка настроек из ConfigManager"""
        if not self.config_manager:
            return
        
        # Audio settings
        self.mic_index = self.config_manager.get("audio.mic_index", -1)
        self.sample_rate = self.config_manager.get("audio.sample_rate", 16000)
        self.channels = self.config_manager.get("audio.channels", 1)
        self.noise_cancellation = self.config_manager.get("audio.noise_cancellation", True)
        self.volume_threshold = self.config_manager.get("audio.volume_threshold", 0.01)
        self.system_audio = self.config_manager.get("audio.system_audio_enabled", False)
        self.tts_enabled = self.config_manager.get("audio.tts_enabled", True)
        self.tts_voice = self.config_manager.get("audio.tts_voice", "en-US-GuyNeural")
        self.tts_rate = self.config_manager.get("audio.tts_rate", "+0%")
        self.tts_volume = self.config_manager.get("audio.tts_volume", "+0%")
        self.echo_cancellation = self.config_manager.get("audio.echo_cancellation", True)
        self.auto_gain = self.config_manager.get("audio.auto_gain", True)
        
        # Применение настроек к UI
        self._refresh_devices()
        
        self.sample_rate_spin.setValue(self.sample_rate)
        self.channels_spin.setValue(self.channels)
        
        self.noise_cancel_check.setChecked(self.noise_cancellation)
        self.threshold_slider.setValue(int(self.volume_threshold * 100))
        self.threshold_value.setText(f"{self.volume_threshold:.2f}")
        
        self.system_audio_check.setChecked(self.system_audio)
        
        self.tts_enable_check.setChecked(self.tts_enabled)
        
        # Выбор голоса в комбобоксе
        voice_idx = self.tts_voice_combo.findData(self.tts_voice)
        if voice_idx >= 0:
            self.tts_voice_combo.setCurrentIndex(voice_idx)
        
        # Парсинг tts_rate (например, "+0%" -> 0)
        try:
            rate_val = int(self.tts_rate.replace("%", "").replace("+", ""))
            self.tts_rate_slider.setValue(rate_val)
            self.tts_rate_value.setText(f"{rate_val:+d}%")
        except ValueError:
            self.tts_rate_slider.setValue(0)
        
        # Парсинг tts_volume (например, "+0%" -> 100%)
        try:
            vol_val = int(self.tts_volume.replace("%", "").replace("+", ""))
            self.tts_volume_slider.setValue(50 + vol_val // 2)
            self.tts_volume_value.setText(f"{50 + vol_val // 2}%")
        except ValueError:
            self.tts_volume_slider.setValue(100)
        
        self.echo_cancel_check.setChecked(self.echo_cancellation)
        self.auto_gain_check.setChecked(self.auto_gain)
    
    def _refresh_devices(self):
        """Обновление списка микрофонов"""
        self.mic_combo.clear()
        self.mic_combo.addItem("Default Device", -1)
        
        if SOUNDDEVICE_AVAILABLE:
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                if device["max_input_channels"] > 0:
                    self.mic_combo.addItem(f"{device['name']} [{i}]", i)
        
        # Выбор текущего устройства
        for i in range(self.mic_combo.count()):
            if self.mic_combo.itemData(i) == self.mic_index:
                self.mic_combo.setCurrentIndex(i)
                break
    
    def _start_audio_monitor(self):
        """Запуск мониторинга аудио для VUmeter"""
        if not SOUNDDEVICE_AVAILABLE:
            return
        
        self._audio_timer = QTimer()
        self._audio_timer.timeout.connect(self._update_vu_meter)
        self._audio_timer.start(100)  # 10 FPS
        
        try:
            device_id = self.mic_combo.currentData()
            if device_id is None or device_id == -1:
                device_id = None
            
            self._audio_stream = sd.InputStream(
                device=device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self._audio_callback,
            )
            self._audio_stream.start()
        except Exception as e:
            print(f"Error starting audio stream: {e}")
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback для обработки аудио данных"""
        if status:
            print(f"Audio stream status: {status}")
        
        # Вычисление RMS уровня
        import numpy as np
        rms = float(np.sqrt(np.mean(indata ** 2)))
        self._current_level = min(1.0, rms * 10)
    
    def _update_vu_meter(self):
        """Обновление VUmeter"""
        if hasattr(self, "_current_level"):
            self.vu_meter.set_level(self._current_level)
    
    def _stop_audio_monitor(self):
        """Остановка мониторинга аудио"""
        if self._audio_timer:
            self._audio_timer.stop()
            self._audio_timer = None
        
        if self._audio_stream:
            self._audio_stream.stop()
            self._audio_stream.close()
            self._audio_stream = None
    
    # === Event Handlers ===
    
    def _on_mic_changed(self, index: int):
        device_id = self.mic_combo.itemData(index)
        if self.config_manager:
            self.config_manager.set("audio.mic_index", device_id)
            self.config_changed.emit("audio.mic_index", device_id)
        self._restart_processor()
    
    def _on_sample_rate_changed(self, value: int):
        if self.config_manager:
            self.config_manager.set("audio.sample_rate", value)
            self.config_changed.emit("audio.sample_rate", value)
        self._restart_processor()
    
    def _on_channels_changed(self, value: int):
        if self.config_manager:
            self.config_manager.set("audio.channels", value)
            self.config_changed.emit("audio.channels", value)
        self._restart_processor()
    
    def _on_mode_changed(self, index: int):
        mode = self.mode_combo.itemData(index)
        if self.config_manager:
            self.config_manager.set("audio.processing_mode", mode)
            self.config_changed.emit("audio.processing_mode", mode)
    
    def _on_noise_cancel_changed(self, state):
        enabled = state == Qt.CheckState.Checked.value
        if self.config_manager:
            self.config_manager.set("audio.noise_cancellation", enabled)
            self.config_changed.emit("audio.noise_cancellation", enabled)
    
    def _on_threshold_changed(self, value: int):
        threshold = value / 100.0
        self.threshold_value.setText(f"{threshold:.2f}")
        if self.config_manager:
            self.config_manager.set("audio.volume_threshold", threshold)
            self.config_changed.emit("audio.volume_threshold", threshold)
    
    def _on_echo_cancel_changed(self, state):
        enabled = state == Qt.CheckState.Checked.value
        if self.config_manager:
            self.config_manager.set("audio.echo_cancellation", enabled)
            self.config_changed.emit("audio.echo_cancellation", enabled)
    
    def _on_auto_gain_changed(self, state):
        enabled = state == Qt.CheckState.Checked.value
        if self.config_manager:
            self.config_manager.set("audio.auto_gain", enabled)
            self.config_changed.emit("audio.auto_gain", enabled)
    
    def _on_system_audio_changed(self, state):
        enabled = state == Qt.CheckState.Checked.value
        if self.config_manager:
            self.config_manager.set("audio.system_audio_enabled", enabled)
            self.config_changed.emit("audio.system_audio_enabled", enabled)
        self._restart_processor()
    
    def _on_tts_enable_changed(self, state):
        enabled = state == Qt.CheckState.Checked.value
        if self.config_manager:
            self.config_manager.set("audio.tts_enabled", enabled)
            self.config_changed.emit("audio.tts_enabled", enabled)
    
    def _on_tts_voice_changed(self, text: str):
        if self.config_manager:
            self.config_manager.set("audio.tts_voice", text)
            self.config_changed.emit("audio.tts_voice", text)
        if self.audio_processor:
            self.audio_processor.tts_voice = text
    
    def _on_tts_rate_changed(self, value: int):
        rate_str = f"{value:+d}%"
        self.tts_rate_value.setText(rate_str)
        if self.config_manager:
            self.config_manager.set("audio.tts_rate", rate_str)
            self.config_changed.emit("audio.tts_rate", rate_str)
        if self.audio_processor:
            self.audio_processor.tts_rate = rate_str
    
    def _on_tts_volume_changed(self, value: int):
        vol_str = f"{value}%"
        self.tts_volume_value.setText(vol_str)
        if self.config_manager:
            self.config_manager.set("audio.tts_volume", vol_str)
            self.config_changed.emit("audio.tts_volume", vol_str)
        if self.audio_processor:
            self.audio_processor.tts_volume = vol_str
    
    def _restart_processor(self):
        """Перезапуск AudioProcessor для применения настроек железа"""
        if self.audio_processor:
            import asyncio
            # Поскольку мы в UI потоке, используем create_task если есть цикл, 
            # или просто полагаемся на то, что процессор сам обновит настройки.
            # Для надежности вызовем переинициализацию параметров.
            self.audio_processor.sample_rate = self.config_manager.get("audio.sample_rate", 16000)
            self.audio_processor.channels = self.config_manager.get("audio.channels", 1)
            self.audio_processor.mic_index = self.config_manager.get("audio.mic_index", -1)
            
            # В идеале здесь должен быть асинхронный перезапуск стримов.
            # Но для MVP достаточно обновить переменные.
    
    def _show_guide(self, guide_key: str):
        """Показ подсказки"""
        if self.guide_manager:
            self.parent().show_guide_modal(guide_key)
    
    def _test_audio(self):
        """Тестирование аудио"""
        if SOUNDDEVICE_AVAILABLE:
            try:
                import numpy as np
                print("Testing audio playback...")
                sample_rate = 44100
                duration = 1.0
                t = np.linspace(0, duration, int(sample_rate * duration))
                frequency = 440
                data = 0.5 * np.sin(2 * np.pi * frequency * t)
                sd.play(data, sample_rate)
                sd.wait()
                print("Audio test completed.")
            except Exception as e:
                print(f"Audio test failed: {e}")
    
    def closeEvent(self, event):
        """Обработка закрытия вкладки"""
        super().closeEvent(event)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    from core.config import ConfigManager
    from core.guide_manager import GuideManager
    
    app = QApplication(sys.argv)
    
    config_manager = ConfigManager("config.yaml")
    guide_manager = GuideManager("config.yaml")
    
    window = QWidget()
    window.setWindowTitle("Audio Settings Tab Test")
    window.resize(900, 700)
    
    layout = QVBoxLayout(window)
    tab = AudioTab(config_manager, guide_manager)
    layout.addWidget(tab)
    
    window.show()
    sys.exit(app.exec())
