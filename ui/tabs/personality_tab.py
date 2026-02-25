"""
Personality Settings Tab (Tab 4)
Интерфейс для визуальной сборки личности бота с использованием шаблонов и блоков промптов.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Callable

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QTextEdit,
    QPushButton,
    QLabel,
    QSplitter,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QLineEdit,
    QScrollArea,
    QFrame,
    QApplication,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPoint
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor, QDrag, QPixmap

from core.prompt_manager import PromptManager, PromptBlock


class TemplateHighlighter:
    """Подсветка синтаксиса для шаблонов с тегами {{...}}"""

    def __init__(self, document):
        self.document = document
        self.highlighting_rules = []

        # Правило для тегов {{...}}
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor("#8B4513"))  # Коричневый
        tag_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((r"\{\{.*?\}\}", tag_format))

        # Правило для комментариев {# ... #}
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))  # Серый
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((r"\{#.*?#\}", comment_format))

        self.rehighlight()

    def rehighlight(self):
        text = self.document.toPlainText()
        for pattern, format_ in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                start = match.start()
                end = match.end()
                self._apply_format(start, end, format_)

    def _apply_format(self, start: int, end: int, format_: QTextCharFormat):
        cursor = QTextCursor(self.document)
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        cursor.setCharFormat(format_)


class PromptBlockItem(QListWidgetItem):
    """Элемент блока промпта с поддержкой Drag-and-Drop"""

    def __init__(self, name: str, content: str, category: str):
        super().__init__(name)
        self.name = name
        self.content = content
        self.category = category
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsDragEnabled)


class PromptBlocksList(QListWidget):
    """Список блоков промптов с поддержкой Drag-and-Drop"""

    blocks_reordered = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSpacing(4)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return

        mime_data = QMimeData()
        mime_data.setText(f"block:{item.name}")
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(QPixmap(64, 64))
        drag.exec(supportedActions)

    def dropEvent(self, event):
        super().dropEvent(event)
        self._emit_reordered()

    def dropEventExternal(self, event, block_data: dict):
        """Обработка внешнего drop события"""
        name = block_data.get("name", "Unknown")
        content = block_data.get("content", "")
        category = block_data.get("category", "custom")

        item = PromptBlockItem(name, content, category)
        self.addItem(item)
        self._emit_reordered()

    def _emit_reordered(self):
        blocks = []
        for i in range(self.count()):
            item = self.item(i)
            if isinstance(item, PromptBlockItem):
                blocks.append({
                    "name": item.name,
                    "content": item.content,
                    "category": item.category,
                })
        self.blocks_reordered.emit(blocks)

    def get_blocks(self) -> List[dict]:
        """Получить все блоки в текущем порядке"""
        blocks = []
        for i in range(self.count()):
            item = self.item(i)
            if isinstance(item, PromptBlockItem):
                blocks.append({
                    "name": item.name,
                    "content": item.content,
                    "category": item.category,
                })
        return blocks

    def set_blocks(self, blocks: List[dict]):
        """Установить блоки из списка"""
        self.clear()
        for block in blocks:
            item = PromptBlockItem(
                block.get("name", "Unknown"),
                block.get("content", ""),
                block.get("category", "custom"),
            )
            self.addItem(item)


class SandboxWidget(QWidget):
    """Виджет песочницы для тестирования промпта в реальном времени"""

    response_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
        title = QLabel("<b>🧪 Песочница</b>")
        layout.addWidget(title)

        # Поле ввода вопроса
        layout.addWidget(QLabel("Ваш вопрос:"))
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Введите тестовый вопрос...")
        self.input_field.setMaximumHeight(80)
        layout.addWidget(self.input_field)

        # Кнопка отправки
        self.send_btn = QPushButton("🚀 Отправить")
        self.send_btn.clicked.connect(self._on_send)
        layout.addWidget(self.send_btn)

        # Поле вывода ответа
        layout.addWidget(QLabel("Ответ бота:"))
        self.output_field = QTextEdit()
        self.output_field.setReadOnly(True)
        self.output_field.setPlaceholderText("Здесь появится ответ...")
        layout.addWidget(self.output_field)

    def _on_send(self):
        question = self.input_field.toPlainText().strip()
        if not question:
            QMessageBox.warning(self, "Внимание", "Введите вопрос!")
            return
        # Сигнал будет обработан внешним контроллером
        self.response_received.emit(question)

    def set_response(self, response: str):
        """Установить ответ от LLM"""
        self.output_field.setPlainText(response)

    def clear(self):
        """Очистить поля"""
        self.input_field.clear()
        self.output_field.clear()


class PersonalityTab(QWidget):
    """
    Вкладка настройки личности (Tab 4)
    
    Функционал:
    - Выбор MD-шаблонов из списка
    - Полноэкранный редактор текста с подсветкой тегов
    - Конструктор промпта из блоков (Drag-and-Drop)
    - Песочница для тестирования
    """

    # Сигналы для интеграции с ConfigManager
    config_changed = pyqtSignal(dict)
    save_requested = pyqtSignal(dict)

    def __init__(self, config_manager=None, guide_manager=None):
        super().__init__()
        self.config_manager = config_manager
        self.guide_manager = guide_manager
        self.prompt_manager = PromptManager()

        self._current_template = None
        self._templates: Dict[str, str] = {}
        self._prompt_blocks: Dict[str, dict] = {}

        self._init_ui()
        self._load_templates()
        self._load_prompt_blocks()

    def _init_ui(self):
        """Инициализация UI компонентов"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Заголовок вкладки
        header = QLabel("<h2>🎭 Настройка личности</h2>")
        main_layout.addWidget(header)

        # Основной сплиттер
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Левая панель: Шаблоны и редактор
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Выбор шаблона
        left_layout.addWidget(QLabel("<b>Шаблон личности:</b>"))
        self.template_combo = QComboBox()
        self.template_combo.currentTextChanged.connect(self._on_template_changed)
        left_layout.addWidget(self.template_combo)

        # Кнопки управления шаблонами
        btn_layout = QHBoxLayout()
        self.save_template_btn = QPushButton("💾 Сохранить")
        self.save_template_btn.clicked.connect(self._on_save_template)
        btn_layout.addWidget(self.save_template_btn)

        self.reset_template_btn = QPushButton("🔄 Сбросить")
        self.reset_template_btn.clicked.connect(self._on_reset_template)
        btn_layout.addWidget(self.reset_template_btn)

        self.new_template_btn = QPushButton("➕ Новый")
        self.new_template_btn.clicked.connect(self._on_new_template)
        btn_layout.addWidget(self.new_template_btn)

        btn_layout.addStretch()
        left_layout.addLayout(btn_layout)

        # Редактор шаблона
        left_layout.addWidget(QLabel("<b>Редактор шаблона:</b>"))
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Выберите шаблон или создайте новый...\n\nИспользуйте теги {{variable}} для переменных.")
        self.editor.textChanged.connect(self._on_editor_changed)
        left_layout.addWidget(self.editor)

        splitter.addWidget(left_widget)

        # Правая панель: Блоки промптов и песочница
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Группа блоков промптов
        blocks_group = QGroupBox("🧩 Конструктор промптов")
        blocks_layout = QVBoxLayout(blocks_group)

        # Поиск блоков
        self.block_search = QLineEdit()
        self.block_search.setPlaceholderText("🔍 Поиск блоков...")
        self.block_search.textChanged.connect(self._filter_blocks)
        blocks_layout.addWidget(self.block_search)

        # Список доступных блоков
        blocks_layout.addWidget(QLabel("Доступные блоки:"))
        self.available_blocks = QListWidget()
        self.available_blocks.setDragEnabled(True)
        self.available_blocks.setSpacing(4)
        blocks_layout.addWidget(self.available_blocks)

        # Кнопка добавления
        add_btn = QPushButton("➕ Добавить выбранный блок")
        add_btn.clicked.connect(self._add_selected_block)
        blocks_layout.addWidget(add_btn)

        # Список выбранных блоков
        blocks_layout.addWidget(QLabel("Ваша сборка:"))
        self.selected_blocks = PromptBlocksList()
        self.selected_blocks.blocks_reordered.connect(self._on_blocks_reordered)
        blocks_layout.addWidget(self.selected_blocks)

        # Кнопки управления сборкой
        assembly_btn_layout = QHBoxLayout()
        self.assemble_btn = QPushButton("🔗 Собрать промпт")
        self.assemble_btn.clicked.connect(self._on_assemble_prompt)
        assembly_btn_layout.addWidget(self.assemble_btn)

        self.clear_blocks_btn = QPushButton("🗑️ Очистить")
        self.clear_blocks_btn.clicked.connect(self._on_clear_blocks)
        assembly_btn_layout.addWidget(self.clear_blocks_btn)

        assembly_btn_layout.addStretch()
        blocks_layout.addLayout(assembly_btn_layout)

        right_layout.addWidget(blocks_group)

        # Песочница
        self.sandbox = SandboxWidget()
        self.sandbox.response_received.connect(self._on_sandbox_send)
        right_layout.addWidget(self.sandbox)

        splitter.addWidget(right_widget)

        # Настройка пропорций сплиттера
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        # Инициализация подсветки синтаксиса
        self.highlighter = TemplateHighlighter(self.editor.document())

        # Привязка к Guide Manager
        if self.guide_manager:
            self._bind_guides()

    def _bind_guides(self):
        """Привязка подсказок к виджетам"""
        guides_map = {
            "personality.template": self.template_combo,
            "personality.editor": self.editor,
            "personality.blocks": self.available_blocks,
            "personality.sandbox": self.sandbox,
        }

        for key, widget in guides_map.items():
            guide = self.guide_manager.get_guide(key)
            if guide:
                widget.setToolTip(self.guide_manager.get_tooltip(key))

    def _load_templates(self):
        """Загрузка шаблонов из assets/templates/"""
        templates_dir = Path(__file__).parent.parent.parent / "assets" / "templates"
        
        # Дефолтные шаблоны
        default_templates = {
            "Helper": self._get_default_helper_template(),
            "Critic": self._get_default_critic_template(),
            "Friend": self._get_default_friend_template(),
            "Professional": self._get_default_professional_template(),
        }

        # Загрузка из файлов
        if templates_dir.exists():
            for template_file in templates_dir.glob("*.md"):
                try:
                    content = template_file.read_text(encoding="utf-8")
                    default_templates[template_file.stem] = content
                except Exception as e:
                    print(f"Error loading template {template_file}: {e}")

        self._templates = default_templates
        
        # Заполнение комбобокса
        self.template_combo.clear()
        self.template_combo.addItems(sorted(self._templates.keys()))
        
        # Выбор первого шаблона
        if self._templates:
            self._current_template = sorted(self._templates.keys())[0]
            self.editor.setPlainText(self._templates[self._current_template])

    def _load_prompt_blocks(self):
        """Загрузка блоков промптов из PromptManager"""
        # Загрузка из модульных JSON файлов
        self.prompt_manager.load()
        
        # Преобразование в формат для UI
        self._prompt_blocks = {}
        for block in self.prompt_manager.get_all_blocks():
            self._prompt_blocks[block.id] = {
                "name": block.name,
                "content": block.content,
                "category": self.prompt_manager.CATEGORY_NAMES_RU.get(
                    block.category, block.category.title()
                ),
                "id": block.id,
                "tags": block.tags,
                "variables": block.variables,
            }
        
        self._populate_available_blocks()

    def _get_default_prompt_blocks(self) -> Dict[str, dict]:
        """Базовые блоки промптов по категориям"""
        return {
            # Категория: Роль
            "role_assistant": {
                "name": "Роль: Ассистент",
                "content": "Ты — полезный ИИ-ассистент по имени {{name}}. Твоя цель — помогать пользователю в решении его задач.",
                "category": "Роль",
            },
            "role_expert": {
                "name": "Роль: Эксперт",
                "content": "Ты — эксперт в области {{expertise}}. Отвечай профессионально, но доступно.",
                "category": "Роль",
            },
            "role_companion": {
                "name": "Роль: Компаньон",
                "content": "Ты — дружелюбный компаньон {{name}}. Общайся неформально и поддерживающе.",
                "category": "Роль",
            },
            # Категория: Стиль
            "style_formal": {
                "name": "Стиль: Формальный",
                "content": "Используй формальный стиль общения. Избегай сленга и фамильярности.",
                "category": "Стиль",
            },
            "style_casual": {
                "name": "Стиль: Неформальный",
                "content": "Общайся в неформальном стиле. Используй разговорные выражения.",
                "category": "Стиль",
            },
            "style_humorous": {
                "name": "Стиль: С юмором",
                "content": "Добавляй уместный юмор в ответы. Уровень юмора: {{humor_level}}.",
                "category": "Стиль",
            },
            # Категория: Поведение
            "behavior_proactive": {
                "name": "Поведение: Проактивный",
                "content": "Проявляй инициативу. Предлагай помощь до того, как пользователь попросит.",
                "category": "Поведение",
            },
            "behavior_reactive": {
                "name": "Поведение: Реактивный",
                "content": "Отвечай только на прямые запросы пользователя. Не проявляй излишней инициативы.",
                "category": "Поведение",
            },
            "behavior_empathetic": {
                "name": "Поведение: Эмпатичный",
                "content": "Проявляй эмпатию к эмоциям пользователя. Уровень эмпатии: {{empathy}}.",
                "category": "Поведение",
            },
            # Категория: Ограничения
            "constraint_brief": {
                "name": "Ограничение: Краткость",
                "content": "Отвечай кратко и по делу. Максимальная длина ответа: {{max_tokens}} токенов.",
                "category": "Ограничения",
            },
            "constraint_detailed": {
                "name": "Ограничение: Детальность",
                "content": "Давай развернутые ответы с примерами и объяснениями.",
                "category": "Ограничения",
            },
            "constraint_no_code": {
                "name": "Ограничение: Без кода",
                "content": "Не предоставляй примеры кода. Объясняй концепции словами.",
                "category": "Ограничения",
            },
        }

    def _populate_available_blocks(self):
        """Заполнение списка доступных блоков"""
        self.available_blocks.clear()

        # Группировка по категориям
        categories = {}
        for key, block in self._prompt_blocks.items():
            category = block.get("category", "Другое")
            if category not in categories:
                categories[category] = []
            categories[category].append(block)

        # Добавление заголовков категорий и блоков
        for category, blocks in sorted(categories.items()):
            # Заголовок категории (неперетаскиваемый элемент)
            header_item = QListWidgetItem(f"📁 {category}")
            header_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.available_blocks.addItem(header_item)

            for block in blocks:
                item = PromptBlockItem(
                    block["name"], 
                    block["content"], 
                    category
                )
                item.setData(Qt.ItemDataRole.UserRole, block.get("id", key))
                self.available_blocks.addItem(item)

    def _get_default_helper_template(self) -> str:
        """Шаблон по умолчанию для помощника"""
        return """# Роль
Ты — {{name}}, дружелюбный ИИ-помощник.

# Стиль общения
- Тон: {{formality}}
- Уровень юмора: {{humor_level}}
- Уровень сарказма: {{sarcasm_level}}

# Поведение
- Эмпатия: {{empathy}}
- Проактивность: {{'включена' if proactive_mode else 'выключена'}}
- Запоминание: {{'включено' if memory_enabled else 'выключено'}}

# Ограничения
- Максимальная длина ответа: {{max_tokens}} токенов
- Температура: {{temperature}}
- Кutoff знаний: {{knowledge_cutoff}}

# Инструкции
Отвечай полезно и точно. Если не знаешь ответа — так и скажи."""

    def _get_default_critic_template(self) -> str:
        """Шаблон критика"""
        return """# Роль
Ты — {{name}}, критически мыслящий ИИ-ассистент.

# Стиль общения
- Тон: Аналитический
- Уровень сарказма: {{sarcasm_level}}
- Прямота: Высокая

# Поведение
- Задавай уточняющие вопросы
- Указывай на логические противоречия
- Предлагай альтернативные точки зрения

# Ограничения
- Будь конструктивным в критике
- Не переходи на личности"""

    def _get_default_friend_template(self) -> str:
        """Шаблон друга"""
        return """# Роль
Ты — {{name}}, лучший друг пользователя.

# Стиль общения
- Тон: Неформальный
- Уровень юмора: {{humor_level}}
- Поддержка: Максимальная

# Поведение
- Проявляй искренний интерес
- Запоминай детали из прошлых разговоров
- Подбадривай и мотивируй

# Ограничения
- Избегай токсичной позитивности
- Будь честным, но тактичным"""

    def _get_default_professional_template(self) -> str:
        """Шаблон профессионала"""
        return """# Роль
Ты — {{name}}, профессиональный бизнес-ассистент.

# Стиль общения
- Тон: Формальный
- Точность: Приоритет №1
- Эффективность: Краткость и ясность

# Поведение
- Фокус на решении задач
- Минимум отступлений
- Структурированные ответы

# Ограничения
- Деловой этикет
- Конфиденциальность данных"""

    # ========== Обработчики событий ==========

    def _on_template_changed(self, template_name: str):
        """Обработка смены шаблона"""
        if template_name in self._templates:
            self._current_template = template_name
            self.editor.setPlainText(self._templates[template_name])
            self.highlighter.rehighlight()

    def _on_editor_changed(self):
        """Обработка изменений в редакторе"""
        # Пере-подсветка при изменении текста
        self.highlighter.rehighlight()
        
        # Отправка сигнала об изменении конфигурации
        if self._current_template:
            self._templates[self._current_template] = self.editor.toPlainText()
            self.config_changed.emit({
                "template": self._current_template,
                "content": self.editor.toPlainText(),
            })

    def _on_save_template(self):
        """Сохранение текущего шаблона"""
        if not self._current_template:
            QMessageBox.warning(self, "Ошибка", "Выберите шаблон для сохранения!")
            return

        content = self.editor.toPlainText()
        self._templates[self._current_template] = content
        
        # Сохранение в файл
        templates_dir = Path(__file__).parent.parent.parent / "assets" / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        template_file = templates_dir / f"{self._current_template}.md"
        try:
            template_file.write_text(content, encoding="utf-8")
            QMessageBox.information(
                self,
                "Успех",
                f"Шаблон '{self._current_template}' сохранен!",
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить шаблон: {e}")

    def _on_reset_template(self):
        """Сброс шаблона к оригиналу"""
        if not self._current_template:
            QMessageBox.warning(self, "Ошибка", "Выберите шаблон для сброса!")
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Сбросить шаблон '{self._current_template}' к оригиналу?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Перезагрузка из файла или дефолтного значения
            templates_dir = Path(__file__).parent.parent.parent / "assets" / "templates"
            template_file = templates_dir / f"{self._current_template}.md"
            
            if template_file.exists():
                try:
                    content = template_file.read_text(encoding="utf-8")
                except:
                    content = self._get_default_template(self._current_template)
            else:
                content = self._get_default_template(self._current_template)
            
            self.editor.setPlainText(content)
            self.highlighter.rehighlight()

    def _on_new_template(self):
        """Создание нового шаблона"""
        name, ok = QLineEdit.getText(
            self,
            "Новый шаблон",
            "Введите имя нового шаблона:",
            QLineEdit.EchoMode.Normal,
        )

        if ok and name:
            name = name.strip().replace(" ", "_")
            if name in self._templates:
                QMessageBox.warning(self, "Ошибка", "Шаблон с таким именем уже существует!")
                return

            self._templates[name] = "# Новый шаблон\n\nОпишите личность здесь..."
            self.template_combo.addItem(name)
            self.template_combo.setCurrentText(name)

    def _filter_blocks(self, search_text: str):
        """Фильтрация блоков по поисковому запросу"""
        search_lower = search_text.lower()
        
        self.available_blocks.setUpdatesEnabled(False)
        try:
            for i in range(self.available_blocks.count()):
                item = self.available_blocks.item(i)
                if isinstance(item, PromptBlockItem):
                    match = (search_lower in item.name.lower() or 
                             search_lower in item.content.lower() or
                             search_lower in item.category.lower())
                    item.setHidden(not match)
        finally:
            self.available_blocks.setUpdatesEnabled(True)

    def _add_selected_block(self):
        """Добавление выбранного блока в сборку"""
        current_item = self.available_blocks.currentItem()
        if not isinstance(current_item, PromptBlockItem):
            QMessageBox.warning(self, "Внимание", "Выберите блок для добавления!")
            return

        # Проверка на дубликат
        for i in range(self.selected_blocks.count()):
            existing = self.selected_blocks.item(i)
            if isinstance(existing, PromptBlockItem) and existing.name == current_item.name:
                QMessageBox.warning(self, "Внимание", "Этот блок уже добавлен!")
                return

        # Копирование блока
        new_item = PromptBlockItem(
            current_item.name,
            current_item.content,
            current_item.category,
        )
        self.selected_blocks.addItem(new_item)

    def _on_blocks_reordered(self, blocks: list):
        """Обработка изменения порядка блоков"""
        pass  # Порядок сохраняется в виджете

    def _on_assemble_prompt(self):
        """Сборка финального промпта из выбранных блоков"""
        blocks = self.selected_blocks.get_blocks()
        
        if not blocks:
            QMessageBox.warning(self, "Внимание", "Добавьте хотя бы один блок!")
            return

        assembled = []
        for block in blocks:
            assembled.append(f"# {block['name']}\n{block['content']}\n")

        full_prompt = "\n".join(assembled)
        
        # Вставка в редактор (добавление к текущему шаблону)
        current_text = self.editor.toPlainText()
        if current_text.strip():
            current_text += "\n\n"
        self.editor.setPlainText(current_text + full_prompt)
        self.highlighter.rehighlight()

    def _on_clear_blocks(self):
        """Очистка списка выбранных блоков"""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Очистить список выбранных блоков?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.selected_blocks.clear()

    def _on_sandbox_send(self, question: str):
        """Обработка отправки вопроса из песочницы"""
        # Здесь будет интеграция с API
        # Для покажем заглушку
        self.sandbox.set_response(
            "🔌 Песочница требует подключения к API.\n\n"
            "Вопрос: " + question + "\n\n"
            "Текущий промпт будет отправлен вместе с этим вопросом."
        )

    # ========== Публичные методы ==========

    def get_current_template(self) -> Optional[str]:
        """Получить текущий шаблон"""
        return self._current_template

    def get_template_content(self) -> str:
        """Получить содержимое текущего шаблона"""
        return self.editor.toPlainText()

    def get_assembled_prompt(self) -> str:
        """Получить собранный промпт из блоков"""
        blocks = self.selected_blocks.get_blocks()
        if not blocks:
            return ""
        
        assembled = []
        for block in blocks:
            assembled.append(f"# {block['name']}\n{block['content']}")
        return "\n\n".join(assembled)

    def set_template(self, name: str, content: str):
        """Установить шаблон программно"""
        if name not in self._templates:
            self._templates[name] = content
            self.template_combo.addItem(name)
        else:
            self._templates[name] = content
        
        self.template_combo.setCurrentText(name)

    def load_config(self, config: dict):
        """Загрузка конфигурации personality"""
        personality = config.get("personality", {})
        
        # Установка значений из конфига
        if "style" in personality:
            style = personality["style"]
            if style in self._templates:
                self.template_combo.setCurrentText(style)

    def get_config(self) -> dict:
        """Получение текущей конфигурации"""
        return {
            "personality": {
                "style": self._current_template,
                "template_content": self.editor.toPlainText(),
                "prompt_blocks": self.selected_blocks.get_blocks(),
            }
        }

    def _get_default_template(self, name: str) -> str:
        """Получение дефолтного шаблона по имени"""
        defaults = {
            "Helper": self._get_default_helper_template(),
            "Critic": self._get_default_critic_template(),
            "Friend": self._get_default_friend_template(),
            "Professional": self._get_default_professional_template(),
        }
        return defaults.get(name, "# Шаблон\n\nОпишите личность здесь...")
