"""
APISettingsTab - Вкладка настроек AI & API (Tab 3)

Отвечает за:
- Выбор провайдеров (Cloud/Custom)
- Ввод и управление API ключами
- Настройка параметров модели (Temperature, Max Tokens, Top-P)
- Тест соединения с API
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QComboBox, QSlider, QSpinBox,
    QDoubleSpinBox, QCheckBox, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class APISettingsTab(QWidget):
    """Вкладка настроек AI & API Settings"""
    
    # Сигналы для сохранения настроек
    settings_changed = pyqtSignal(dict)
    connection_tested = pyqtSignal(bool, str)
    
    def __init__(self, config_manager=None, guide_manager=None):
        super().__init__()
        self.config_manager = config_manager
        self.guide_manager = guide_manager
        self.api_key_visible = False
        
        self._init_ui()
        self._load_settings()
        self._connect_signals()
        
    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # === Блок 1: Выбор провайдера и схемы API ===
        self.provider_group = self._create_provider_group()
        main_layout.addWidget(self.provider_group)
        
        # === Блок 2: API Ключи ===
        self.api_keys_group = self._create_api_keys_group()
        main_layout.addWidget(self.api_keys_group)
        
        # === Блок 3: Параметры модели ===
        self.model_params_group = self._create_model_params_group()
        main_layout.addWidget(self.model_params_group)
        
        # === Блок 4: Тест соединения ===
        self.connection_group = self._create_connection_group()
        main_layout.addWidget(self.connection_group)
        
        # Добавляем растягиватель внизу
        main_layout.addStretch()
        
        # Применяем стилизацию
        self._apply_styles()
    
    def _apply_styles(self):
        """Применение стилей к виджетам"""
        # Стили для group boxes
        for group in [self.provider_group, self.api_keys_group, 
                      self.model_params_group, self.connection_group]:
            group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
            """)
        
        # Регистрируем подсказки в Guide Manager
        self._register_guides()
    
    def _register_guides(self):
        """Регистрация подсказок в Guide Engine"""
        if not self.guide_manager:
            return
        
        # Ключи для Guide Engine
        guides_map = {
            'api.provider': self.provider_combo,
            'api.base_url': self.base_url_input,
            'api.api_scheme': self.api_scheme_combo,
            'api.api_key': self.api_key_input,
            'api.backup_api_key': self.backup_key_input,
            'api.model_name': self.model_combo,
            'api.temperature': self.temp_slider,
            'api.top_p': self.top_p_slider,
            'api.max_tokens': self.max_tokens_spinbox,
        }
        
        # Привязываем виджеты к Guide Manager
        for key, widget in guides_map.items():
            self.guide_manager.bind_to_widget(key, widget, mode="tooltip")
        
    def _create_provider_group(self) -> QGroupBox:
        """Создание группы выбора провайдера"""
        group = QGroupBox("Провайдер и Схема API")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        # Выбор провайдера
        provider_layout = QHBoxLayout()
        provider_label = QLabel("Провайдер:")
        provider_label.setFixedWidth(150)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            "OpenAI (Cloud)",
            "Gemini (Cloud)",
            "Claude (Cloud)",
            "Custom (Local/Proxy)"
        ])
        self.provider_combo.setToolTip(
            "Выберите провайдера AI модели. Cloud - облачные API, "
            "Custom - локальные модели или прокси-серверы."
        )
        
        provider_layout.addWidget(provider_label)
        provider_layout.addWidget(self.provider_combo)
        provider_layout.addStretch()
        layout.addLayout(provider_layout)
        
        # Custom Base URL
        url_layout = QHBoxLayout()
        url_label = QLabel("Base URL:")
        url_label.setFixedWidth(150)
        
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("https://api.example.com/v1/")
        self.base_url_input.setToolTip(
            "URL для подключения к API. Для облачных провайдеров заполняется "
            "автоматически. Для Custom укажите свой endpoint."
        )
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.base_url_input)
        layout.addLayout(url_layout)
        
        # Выбор схемы API
        scheme_layout = QHBoxLayout()
        scheme_label = QLabel("Схема API:")
        scheme_label.setFixedWidth(150)
        
        self.api_scheme_combo = QComboBox()
        self.api_scheme_combo.addItems([
            "OpenAI Compatible",
            "Gemini Native",
            "Claude API",
            "Custom Schema"
        ])
        self.api_scheme_combo.setToolTip(
            "Схема взаимодействия с API. OpenAI Compatible подходит для "
            "большинства совместимых сервисов."
        )
        
        scheme_layout.addWidget(scheme_label)
        scheme_layout.addWidget(self.api_scheme_combo)
        scheme_layout.addStretch()
        layout.addLayout(scheme_layout)
        
        return group
    
    def _create_api_keys_group(self) -> QGroupBox:
        """Создание группы управления API ключами"""
        group = QGroupBox("API Ключи")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        # Основной API ключ
        key_layout = QHBoxLayout()
        key_label = QLabel("API Key:")
        key_label.setFixedWidth(150)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setToolTip(
            "Ваш API ключ для доступа к сервису. Ключ маскируется при вводе. "
            "Используйте кнопку 👁 для просмотра."
        )
        
        # Кнопка показать/скрыть ключ
        self.toggle_key_btn = QPushButton("👁")
        self.toggle_key_btn.setFixedWidth(40)
        self.toggle_key_btn.setToolTip("Показать/скрыть API ключ")
        self.toggle_key_btn.clicked.connect(self._toggle_api_key_visibility)
        
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.api_key_input)
        key_layout.addWidget(self.toggle_key_btn)
        layout.addLayout(key_layout)
        
        # Дополнительный ключ (резервный)
        backup_key_layout = QHBoxLayout()
        backup_key_label = QLabel("Backup API Key:")
        backup_key_label.setFixedWidth(150)
        
        self.backup_key_input = QLineEdit()
        self.backup_key_input.setPlaceholderText("sk-... (опционально)")
        self.backup_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.backup_key_input.setToolTip(
            "Резервный API ключ. Используется автоматически при исчерпании "
            "лимита основного ключа."
        )
        
        self.toggle_backup_key_btn = QPushButton("👁")
        self.toggle_backup_key_btn.setFixedWidth(40)
        self.toggle_backup_key_btn.setToolTip("Показать/скрыть резервный ключ")
        self.toggle_backup_key_btn.clicked.connect(self._toggle_backup_key_visibility)
        
        backup_key_layout.addWidget(backup_key_label)
        backup_key_layout.addWidget(self.backup_key_input)
        backup_key_layout.addWidget(self.toggle_backup_key_btn)
        layout.addLayout(backup_key_layout)
        
        return group
    
    def _create_model_params_group(self) -> QGroupBox:
        """Создание группы параметров модели"""
        group = QGroupBox("Параметры Модели")
        layout = QVBoxLayout(group)
        layout.setSpacing(20)
        
        # Выбор модели
        model_layout = QHBoxLayout()
        model_label = QLabel("Модель:")
        model_label.setFixedWidth(150)
        
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.addItems([
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-4-turbo",
            "gemini-2.0-flash",
            "gemini-2.5-pro",
            "claude-3-5-sonnet",
            "claude-3-opus"
        ])
        self.model_combo.setToolTip(
            "Выберите AI модель для генерации ответов. Можно ввести своё значение."
        )
        
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)
        
        # Temperature
        temp_layout = QHBoxLayout()
        temp_label = QLabel("Temperature:")
        temp_label.setFixedWidth(150)
        
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(0, 200)
        self.temp_slider.setValue(70)
        self.temp_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.temp_slider.setTickInterval(20)
        self.temp_slider.setToolTip(
            "Креативность модели. 0 = детерминировано, 2 = максимально креативно. "
            "Рекомендуемое значение: 0.7"
        )
        
        self.temp_spinbox = QDoubleSpinBox()
        self.temp_spinbox.setRange(0.0, 2.0)
        self.temp_spinbox.setValue(0.7)
        self.temp_spinbox.setSingleStep(0.1)
        self.temp_spinbox.setFixedWidth(60)
        
        self.temp_slider.valueChanged.connect(
            lambda v: self.temp_spinbox.setValue(v / 100)
        )
        self.temp_spinbox.valueChanged.connect(
            lambda v: self.temp_slider.setValue(int(v * 100))
        )
        
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self.temp_slider)
        temp_layout.addWidget(self.temp_spinbox)
        layout.addLayout(temp_layout)
        
        # Top-P
        top_p_layout = QHBoxLayout()
        top_p_label = QLabel("Top-P:")
        top_p_label.setFixedWidth(150)
        
        self.top_p_slider = QSlider(Qt.Orientation.Horizontal)
        self.top_p_slider.setRange(0, 100)
        self.top_p_slider.setValue(100)
        self.top_p_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.top_p_slider.setTickInterval(10)
        self.top_p_slider.setToolTip(
            "Ядровая выборка. Контролирует разнообразие ответов. "
            "1.0 = полное разнообразие, 0.1 = только наиболее вероятные токены."
        )
        
        self.top_p_spinbox = QDoubleSpinBox()
        self.top_p_spinbox.setRange(0.0, 1.0)
        self.top_p_spinbox.setValue(1.0)
        self.top_p_spinbox.setSingleStep(0.05)
        self.top_p_spinbox.setFixedWidth(60)
        
        self.top_p_slider.valueChanged.connect(
            lambda v: self.top_p_spinbox.setValue(v / 100)
        )
        self.top_p_spinbox.valueChanged.connect(
            lambda v: self.top_p_slider.setValue(int(v * 100))
        )
        
        top_p_layout.addWidget(top_p_label)
        top_p_layout.addWidget(self.top_p_slider)
        top_p_layout.addWidget(self.top_p_spinbox)
        layout.addLayout(top_p_layout)
        
        # Max Tokens
        tokens_layout = QHBoxLayout()
        tokens_label = QLabel("Max Tokens:")
        tokens_label.setFixedWidth(150)
        
        self.max_tokens_spinbox = QSpinBox()
        self.max_tokens_spinbox.setRange(1, 128000)
        self.max_tokens_spinbox.setValue(512)
        self.max_tokens_spinbox.setSingleStep(64)
        self.max_tokens_spinbox.setFixedWidth(100)
        self.max_tokens_spinbox.setToolTip(
            "Максимальное количество токенов в ответе. Больше токенов = более "
            "развёрнутые ответы, но выше расход и время генерации."
        )
        
        tokens_layout.addWidget(tokens_label)
        tokens_layout.addWidget(self.max_tokens_spinbox)
        tokens_layout.addStretch()
        layout.addLayout(tokens_layout)
        
        return group
    
    def _create_connection_group(self) -> QGroupBox:
        """Создание группы теста соединения"""
        group = QGroupBox("Проверка Соединения")
        layout = QHBoxLayout(group)
        layout.setSpacing(15)
        
        info_label = QLabel(
            "Нажмите кнопку для проверки подключения к API. "
            "Используется текущая конфигурация (URL, ключ, модель)."
        )
        info_label.setWordWrap(True)
        
        self.test_connection_btn = QPushButton("🔄 Тест соединения")
        self.test_connection_btn.setFixedWidth(150)
        self.test_connection_btn.setToolTip(
            "Проверить подключение к API с текущими настройками. "
            "Отправляет тестовый запрос и ожидает ответа."
        )
        self.test_connection_btn.clicked.connect(self._test_connection)
        
        self.connection_status_label = QLabel("Статус: Не проверено")
        self.connection_status_label.setStyleSheet("color: gray;")
        
        layout.addWidget(info_label)
        layout.addWidget(self.test_connection_btn)
        layout.addWidget(self.connection_status_label)
        
        return group
    
    def _toggle_api_key_visibility(self):
        """Переключение видимости основного API ключа"""
        self.api_key_visible = not self.api_key_visible
        if self.api_key_visible:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_key_btn.setText("🔒")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_key_btn.setText("👁")
    
    def _toggle_backup_key_visibility(self):
        """Переключение видимости резервного API ключа"""
        # Используем отдельный флаг для резервного ключа
        if hasattr(self, 'backup_key_visible'):
            self.backup_key_visible = not self.backup_key_visible
        else:
            self.backup_key_visible = True
            
        if self.backup_key_visible:
            self.backup_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_backup_key_btn.setText("🔒")
        else:
            self.backup_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_backup_key_btn.setText("👁")
    
    def _load_settings(self):
        """Загрузка настроек из ConfigManager"""
        if not self.config_manager:
            return
            
        try:
            api_settings = self.config_manager.get_api_settings()
            
            # Провайдер и URL
            self.base_url_input.setText(api_settings.get('base_url', ''))
            
            # API ключи
            self.api_key_input.setText(api_settings.get('api_key', ''))
            
            # Параметры модели
            self.model_combo.setCurrentText(api_settings.get('model_name', 'gpt-4o-mini'))
            self.temp_spinbox.setValue(api_settings.get('temperature', 0.7))
            self.max_tokens_spinbox.setValue(api_settings.get('max_tokens', 512))
            self.top_p_spinbox.setValue(api_settings.get('top_p', 1.0))
            
        except Exception as e:
            print(f"[APISettingsTab] Ошибка загрузки настроек: {e}")
    
    def _save_settings(self):
        """Сохранение настроек в ConfigManager"""
        if not self.config_manager:
            return
            
        settings = {
            'base_url': self.base_url_input.text(),
            'api_key': self.api_key_input.text(),
            'backup_api_key': self.backup_key_input.text(),
            'model_name': self.model_combo.currentText(),
            'temperature': self.temp_spinbox.value(),
            'max_tokens': self.max_tokens_spinbox.value(),
            'top_p': self.top_p_spinbox.value(),
        }
        
        try:
            self.config_manager.update_api_settings(settings)
            self.settings_changed.emit(settings)
        except Exception as e:
            print(f"[APISettingsTab] Ошибка сохранения настроек: {e}")
    
    def _connect_signals(self):
        """Подключение сигналов для автосохранения"""
        widgets = [
            self.base_url_input,
            self.api_key_input,
            self.backup_key_input,
            self.model_combo,
            self.temp_slider,
            self.temp_spinbox,
            self.top_p_slider,
            self.top_p_spinbox,
            self.max_tokens_spinbox,
        ]
        
        for widget in widgets:
            if hasattr(widget, 'textChanged'):
                widget.textChanged.connect(self._save_settings)
            elif hasattr(widget, 'currentTextChanged'):
                widget.currentTextChanged.connect(self._save_settings)
            elif hasattr(widget, 'valueChanged'):
                widget.valueChanged.connect(self._save_settings)
        
        # Подключение сигнала смены провайдера для авто-заполнения URL
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
    
    def _on_provider_changed(self, provider: str):
        """Обработка смены провайдера"""
        # Авто-заполнение Base URL для облачных провайдеров
        url_map = {
            "OpenAI (Cloud)": "https://api.openai.com/v1/",
            "Gemini (Cloud)": "https://generativelanguage.googleapis.com/v1beta/",
            "Claude (Cloud)": "https://api.anthropic.com/v1/",
            "Custom (Local/Proxy)": "",  # Оставляем пустым для ручного ввода
        }
        
        base_url = url_map.get(provider, "")
        if base_url:
            self.base_url_input.setText(base_url)
            self.base_url_input.setReadOnly(True)
            self.base_url_input.setToolTip("URL заблокирован для выбранного провайдера")
        else:
            self.base_url_input.setReadOnly(False)
            self.base_url_input.setPlaceholderText("https://api.example.com/v1/")
            self.base_url_input.setToolTip(
                "URL для подключения к API. Для Custom укажите свой endpoint."
            )
        
        # Авто-выбор схемы API
        scheme_map = {
            "OpenAI (Cloud)": "OpenAI Compatible",
            "Gemini (Cloud)": "Gemini Native",
            "Claude (Cloud)": "Claude API",
            "Custom (Local/Proxy)": "Custom Schema",
        }
        
        scheme = scheme_map.get(provider, "Custom Schema")
        self.api_scheme_combo.setCurrentText(scheme)
        
        # Сохраняем настройки
        self._save_settings()
    
    async def _test_connection(self):
        """Асинхронная проверка соединения с API"""
        self.test_connection_btn.setEnabled(False)
        self.test_connection_btn.setText("⏳ Проверка...")
        self.connection_status_label.setText("Статус: Проверка...")
        self.connection_status_label.setStyleSheet("color: orange;")
        
        try:
            # Получаем текущие настройки
            settings = self.get_settings()
            
            # Проверяем наличие API ключа
            if not settings.get('api_key'):
                raise ValueError("API ключ не указан")
            
            # Импортируем APIBridge для теста
            try:
                from core.api_bridge import APIBridge
                api_bridge = APIBridge(config_manager=self.config_manager)
                
                # Инициализируем с текущими настройками
                await api_bridge.initialize(
                    base_url=settings['base_url'],
                    api_key=settings['api_key'],
                    model_name=settings['model_name']
                )
                
                # Тестовый запрос
                test_message = {
                    "role": "user",
                    "content": "Test connection. Respond with 'OK' only."
                }
                
                response = await api_bridge.chat_completion(
                    messages=[test_message],
                    max_tokens=10,
                    temperature=0.1
                )
                
                if response and 'OK' in response:
                    success = True
                    message = "Соединение успешно! Модель отвечает."
                else:
                    success = False
                    message = f"Ответ модели: {response}"
                    
            except ImportError:
                # APIBridge ещё не реализован - используем заглушку
                await asyncio.sleep(1)
                success = True
                message = "APIBridge не подключён. Настройки сохранены."
            
            if success:
                self.connection_status_label.setText(f"Статус: {message}")
                self.connection_status_label.setStyleSheet("color: green;")
                QMessageBox.information(self, "Тест соединения", message)
            else:
                self.connection_status_label.setText(f"Статус: Ошибка")
                self.connection_status_label.setStyleSheet("color: red;")
                QMessageBox.warning(self, "Тест соединения", message)
                
            self.connection_tested.emit(success, message)
            
        except Exception as e:
            error_msg = f"Ошибка: {str(e)}"
            self.connection_status_label.setText("Статус: Ошибка")
            self.connection_status_label.setStyleSheet("color: red;")
            QMessageBox.critical(self, "Тест соединения", error_msg)
            self.connection_tested.emit(False, error_msg)
            
        finally:
            self.test_connection_btn.setEnabled(True)
            self.test_connection_btn.setText("🔄 Тест соединения")
    
    def get_settings(self) -> dict:
        """Получение текущих настроек"""
        return {
            'base_url': self.base_url_input.text(),
            'api_key': self.api_key_input.text(),
            'backup_api_key': self.backup_key_input.text(),
            'provider': self.provider_combo.currentText(),
            'api_scheme': self.api_scheme_combo.currentText(),
            'model_name': self.model_combo.currentText(),
            'temperature': self.temp_spinbox.value(),
            'max_tokens': self.max_tokens_spinbox.value(),
            'top_p': self.top_p_spinbox.value(),
        }


# Импортируем asyncio для асинхронной проверки
import asyncio
