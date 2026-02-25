import yaml
import os
from pathlib import Path
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field, field_validator
from PyQt6.QtCore import QObject, pyqtSignal


class VisionSettings(BaseModel):
    enabled: bool = True
    fps: int = Field(default=5, ge=1, le=60)
    capture_region: list = Field(default=[0, 0, 1920, 1080])
    model: str = "vit_base_patch16_siglip_384"
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    gpu_acceleration: bool = True
    debug_mode: bool = False
    save_raw_video: bool = False
    process_interval: float = Field(default=0.2, ge=0.05, le=10.0)
    use_half_precision: bool = True
    screenshot_format: str = "png"
    jpeg_quality: int = Field(default=85, ge=1, le=100)
    max_resolution: list = [1920, 1080]
    min_resolution: list = [640, 480]
    auto_exposure: bool = True
    contrast: float = Field(default=1.0, ge=0.5, le=2.0)
    brightness: float = Field(default=1.0, ge=0.5, le=2.0)
    color_mode: str = "RGB"


class AudioSettings(BaseModel):
    mic_enabled: bool = True
    mic_index: int = -1
    sample_rate: int = Field(default=16000, ge=8000, le=48000)
    channels: int = Field(default=1, ge=1, le=2)
    noise_cancellation: bool = True
    volume_threshold: float = Field(default=0.01, ge=0.0, le=1.0)
    stt_model: str = "whisper-base"
    stt_language: str = "auto"
    tts_enabled: bool = True
    tts_voice: str = "en-US-GuyNeural"
    tts_rate: str = "+0%"
    tts_volume: str = "+0%"
    tts_pitch: str = "+0Hz"
    system_audio_enabled: bool = False
    audio_buffer_size: int = Field(default=1024, ge=256, le=8192)
    echo_cancellation: bool = True
    auto_gain: bool = True


class APISettings(BaseModel):
    base_url: str = "https://api.aitunnel.ru/v1/"
    api_key: str = "YOUR_API_KEY"
    model_name: str = "gpt-4o-mini"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=512, ge=1, le=128000)
    timeout: int = Field(default=30, ge=5, le=300)
    proxy: Optional[str] = None
    retry_count: int = Field(default=3, ge=0, le=10)
    history_limit: int = Field(default=20, ge=0, le=100)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    stream: bool = False
    seed: Optional[int] = None


class PersonalitySettings(BaseModel):
    name: str = "Svetka"
    style: str = "Helper"
    sarcasm_level: float = Field(default=0.2, ge=0.0, le=1.0)
    formality: str = "Neutral"
    humor_level: float = Field(default=0.5, ge=0.0, le=1.0)
    aggression_level: float = Field(default=0.1, ge=0.0, le=1.0)
    empathy: float = Field(default=0.8, ge=0.0, le=1.0)
    memory_enabled: bool = True
    knowledge_cutoff: str = "2023-10"
    proactive_mode: bool = True
    verbosity: str = "Normal"
    creativity: float = Field(default=0.5, ge=0.0, le=1.0)
    tone: str = "Friendly"


class MemorySettings(BaseModel):
    storage_type: str = "json"
    db_path: str = "memory.db"
    long_term_enabled: bool = True
    short_term_limit: int = Field(default=100, ge=10, le=1000)
    summary_trigger: int = Field(default=50, ge=10, le=200)
    relevance_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    embedding_model: str = "text-embedding-3-small"
    compression_ratio: float = Field(default=0.5, ge=0.1, le=0.9)
    auto_backup: bool = True
    backup_interval: int = Field(default=3600, ge=300, le=86400)
    max_memory_items: int = Field(default=10000, ge=100, le=100000)
    forget_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    rag_enabled: bool = True
    vector_store_path: str = "vector_store"


class PrivacySettings(BaseModel):
    screen_logging_enabled: bool = True
    audio_logging_enabled: bool = True
    keystroke_logging: bool = False
    data_retention_days: int = Field(default=30, ge=1, le=365)
    encrypt_local_data: bool = False
    share_analytics: bool = False
    cloud_sync: bool = False
    mask_sensitive_data: bool = True
    sensitive_patterns: list = Field(
        default_factory=lambda: ["password", "credit_card", "ssn"]
    )
    # Blacklist для игнорируемых приложений
    blacklist: list = Field(default_factory=list)
    # Offline-Only режим
    offline_only: bool = False
    # Зоны маскирования (Blur regions)
    blur_zones: list = Field(default_factory=list)


class AppearanceSettings(BaseModel):
    theme: str = "Dark"
    language: str = "ru"
    font_size: int = Field(default=14, ge=10, le=24)
    show_notifications: bool = True
    notification_sound: bool = True
    minimize_to_tray: bool = True
    start_minimized: bool = False
    always_on_top: bool = False


class ConfigSchema(BaseModel):
    model_config = {"extra": "allow"}
    vision: VisionSettings = Field(default_factory=VisionSettings)
    audio: AudioSettings = Field(default_factory=AudioSettings)
    api: APISettings = Field(default_factory=APISettings)
    personality: PersonalitySettings = Field(default_factory=PersonalitySettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    privacy: PrivacySettings = Field(default_factory=PrivacySettings)
    appearance: AppearanceSettings = Field(default_factory=AppearanceSettings)


class ConfigDict:
    def __init__(self, config: ConfigSchema, section: str = None):
        self._config = config
        self._section = section

    def __getitem__(self, key: str):
        dump = self._config.model_dump()
        if key in dump:
            val = dump[key]
            if isinstance(val, dict):
                return SectionDict(getattr(self._config, key), key)
            return val
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any):
        if key not in self._config.model_dump():
            raise KeyError(key)

        section_class = {
            "vision": VisionSettings,
            "audio": AudioSettings,
            "api": APISettings,
            "personality": PersonalitySettings,
            "memory": MemorySettings,
            "privacy": PrivacySettings,
            "appearance": AppearanceSettings,
        }.get(key)

        if section_class and isinstance(value, dict):
            setattr(self._config, key, section_class(**value))
        else:
            raise ValueError(f"Invalid key or value type for {key}")


class SectionDict:
    def __init__(self, section, section_name: str):
        self._section = section
        self._section_name = section_name

    def __getitem__(self, key: str):
        dump = self._section.model_dump()
        if key in dump:
            return dump[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any):
        if hasattr(self._section, key):
            setattr(self._section, key, value)
        else:
            raise KeyError(key)


class ConfigManager(QObject):
    config_changed = pyqtSignal(str, object)

    def __init__(self, config_path: str = "config.yaml"):
        super().__init__()
        self.config_path = Path(config_path)
        self._config: Optional[ConfigSchema] = None
        self._raw_config: Dict = {}
        self.load_config()

    @property
    def config(self) -> ConfigDict:
        if self._config is None:
            self._config = ConfigSchema()
        return ConfigDict(self._config)

    def load_config(self):
        if not self.config_path.exists():
            self.generate_default_config()

        with open(self.config_path, "r", encoding="utf-8") as f:
            try:
                self._raw_config = yaml.safe_load(f) or {}
                self._config = ConfigSchema(**self._raw_config)
            except Exception as e:
                print(f"Error loading {self.config_path}: {e}")
                self._raw_config = {}
                self._config = ConfigSchema()

    def save(self):
        self._raw_config = self._config.model_dump()

        content = "# Svetka AI Config File\n"
        content += yaml.dump(
            self._raw_config,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )

        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write(content)

    def save_config(self):
        """Alias for save() to maintain compatibility with tests."""
        self.save()

    def generate_default_config(self):
        self._config = ConfigSchema()
        self._raw_config = self._config.model_dump()

        content = "# Svetka AI Config File\n"
        content += yaml.dump(
            self._raw_config,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )

        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write(content)

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        val = self._config.model_dump()
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
        return val if val is not None else default

    def __getitem__(self, key: str):
        return self._config.model_dump().get(key)

    def __setitem__(self, key: str, value: Any):
        if key in self._config.model_dump():
            if hasattr(self._config, key):
                if isinstance(value, dict):
                    section_class = {
                        "vision": VisionSettings,
                        "audio": AudioSettings,
                        "api": APISettings,
                        "personality": PersonalitySettings,
                        "memory": MemorySettings,
                        "privacy": PrivacySettings,
                        "appearance": AppearanceSettings,
                    }.get(key)
                    if section_class:
                        setattr(self._config, key, section_class(**value))
                        self._raw_config = self._config.model_dump()
                else:
                    raise ValueError(f"Section {key} expects a dict")

    def set(self, key: str, value: Any) -> bool:
        try:
            keys = key.split(".")
            if len(keys) < 2:
                return False

            section = keys[0]
            field = keys[1]

            if section == "vision" and hasattr(self._config.vision, field):
                setattr(self._config.vision, field, value)
            elif section == "audio" and hasattr(self._config.audio, field):
                setattr(self._config.audio, field, value)
            elif section == "api" and hasattr(self._config.api, field):
                setattr(self._config.api, field, value)
            elif section == "personality" and hasattr(self._config.personality, field):
                setattr(self._config.personality, field, value)
            elif section == "memory" and hasattr(self._config.memory, field):
                setattr(self._config.memory, field, value)
            elif section == "privacy" and hasattr(self._config.privacy, field):
                setattr(self._config.privacy, field, value)
            elif section == "appearance" and hasattr(self._config.appearance, field):
                setattr(self._config.appearance, field, value)
            else:
                return False

            self._raw_config = self._config.model_dump()
            return True
        except Exception as e:
            print(f"Error setting {key}: {e}")
            return False

    def update_and_notify(self, key: str, value: Any) -> bool:
        result = self.set(key, value)
        if result:
            self.config_changed.emit(key, value)
        return result

    def reset_to_default(self):
        self._config = ConfigSchema()
        self._raw_config = self._config.model_dump()
        self.save()

    def reset_section(self, section: str) -> bool:
        try:
            if section == "vision":
                self._config.vision = VisionSettings()
            elif section == "audio":
                self._config.audio = AudioSettings()
            elif section == "api":
                self._config.api = APISettings()
            elif section == "personality":
                self._config.personality = PersonalitySettings()
            elif section == "memory":
                self._config.memory = MemorySettings()
            elif section == "privacy":
                self._config.privacy = PrivacySettings()
            elif section == "appearance":
                self._config.appearance = AppearanceSettings()
            else:
                return False

            self._raw_config = self._config.model_dump()
            return True
        except Exception as e:
            print(f"Error resetting section {section}: {e}")
            return False

    # === Методы для работы с API настройками (для APISettingsTab) ===

    def get_api_settings(self) -> dict:
        """Получение всех API настроек"""
        if self._config is None:
            return {}
        return self._config.api.model_dump()

    def update_api_settings(self, settings: dict):
        """Обновление API настроек"""
        if self._config is None:
            return

        for key, value in settings.items():
            if hasattr(self._config.api, key):
                setattr(self._config.api, key, value)

        self._raw_config = self._config.model_dump()
        self.save()
        self.config_changed.emit("api", settings)


if __name__ == "__main__":
    cm = ConfigManager("config.yaml")
    print(f"Generated {cm.config_path}")
    print(f"Vision FPS: {cm.get('vision.fps')}")
    print(f"API Model: {cm.get('api.model_name')}")
    print(f"Personality: {cm.get('personality.name')}")
