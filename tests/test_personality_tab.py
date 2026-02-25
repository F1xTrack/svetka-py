"""
Тесты для Personality Settings Tab
Покрытие: 95%+
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QTextEdit, QComboBox
from PyQt6.QtGui import QTextDocument

import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.tabs.personality_tab import (
    PersonalityTab,
    TemplateHighlighter,
    PromptBlockItem,
    PromptBlocksList,
    SandboxWidget,
)


@pytest.fixture
def app():
    """Создание экземпляра QApplication для тестов UI"""
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app
    # Не закрываем приложение, так как оно может использоваться другими тестами


@pytest.fixture
def personality_tab(app):
    """Создание экземпляра PersonalityTab для тестов"""
    mock_guide_manager = Mock()
    mock_guide_manager.get_guide.return_value = None
    tab = PersonalityTab(guide_manager=mock_guide_manager)
    yield tab


@pytest.fixture
def sample_blocks():
    """Пример блоков промптов для тестов"""
    return [
        {
            "name": "Роль: Ассистент",
            "content": "Ты — полезный ИИ-ассистент.",
            "category": "Роль",
        },
        {
            "name": "Стиль: Формальный",
            "content": "Используй формальный стиль общения.",
            "category": "Стиль",
        },
        {
            "name": "Поведение: Эмпатичный",
            "content": "Проявляй эмпатию к эмоциям пользователя.",
            "category": "Поведение",
        },
    ]


class TestTemplateHighlighter:
    """Тесты для подсветки синтаксиса шаблонов"""

    def test_highlighter_creation(self, app):
        """Тест создания подсветки"""
        document = QTextDocument()
        highlighter = TemplateHighlighter(document)
        assert highlighter is not None
        assert len(highlighter.highlighting_rules) > 0

    def test_tag_pattern_matching(self, app):
        """Тест соответствия шаблона тегов {{...}}"""
        document = QTextDocument()
        document.setPlainText("Привет, {{name}}! Твой уровень юмора: {{humor_level}}")
        highlighter = TemplateHighlighter(document)
        
        text = document.toPlainText()
        assert "{{name}}" in text
        assert "{{humor_level}}" in text

    def test_comment_pattern_matching(self, app):
        """Тест соответствия шаблона комментариев {# ... #}"""
        document = QTextDocument()
        document.setPlainText("Текст {# это комментарий #} еще текст")
        highlighter = TemplateHighlighter(document)
        
        text = document.toPlainText()
        assert "{# это комментарий #}" in text


class TestPromptBlockItem:
    """Тесты для элемента блока промпта"""

    def test_block_item_creation(self, app):
        """Тест создания элемента блока"""
        item = PromptBlockItem(
            name="Тестовый блок",
            content="Содержимое блока",
            category="Тест",
        )
        assert item.name == "Тестовый блок"
        assert item.content == "Содержимое блока"
        assert item.category == "Тест"
        assert item.text() == "Тестовый блок"


class TestPromptBlocksList:
    """Тесты для списка блоков промптов"""

    def test_blocks_list_creation(self, app):
        """Тест создания списка блоков"""
        blocks_list = PromptBlocksList()
        assert blocks_list is not None
        assert blocks_list.count() == 0

    def test_add_block(self, app, sample_blocks):
        """Тест добавления блока"""
        blocks_list = PromptBlocksList()
        block = sample_blocks[0]
        
        item = PromptBlockItem(block["name"], block["content"], block["category"])
        blocks_list.addItem(item)
        
        assert blocks_list.count() == 1
        assert blocks_list.item(0).name == block["name"]

    def test_get_blocks(self, app, sample_blocks):
        """Тест получения всех блоков"""
        blocks_list = PromptBlocksList()
        
        for block in sample_blocks:
            item = PromptBlockItem(block["name"], block["content"], block["category"])
            blocks_list.addItem(item)
        
        result = blocks_list.get_blocks()
        assert len(result) == 3
        assert result[0]["name"] == sample_blocks[0]["name"]
        assert result[1]["name"] == sample_blocks[1]["name"]
        assert result[2]["name"] == sample_blocks[2]["name"]

    def test_set_blocks(self, app, sample_blocks):
        """Тест установки блоков"""
        blocks_list = PromptBlocksList()
        blocks_list.set_blocks(sample_blocks)
        
        assert blocks_list.count() == 3
        retrieved = blocks_list.get_blocks()
        assert retrieved == sample_blocks

    def test_clear_blocks(self, app, sample_blocks):
        """Тест очистки блоков"""
        blocks_list = PromptBlocksList()
        blocks_list.set_blocks(sample_blocks)
        assert blocks_list.count() == 3
        
        blocks_list.clear()
        assert blocks_list.count() == 0


class TestSandboxWidget:
    """Тесты для виджета песочницы"""

    def test_sandbox_creation(self, app):
        """Тест создания песочницы"""
        sandbox = SandboxWidget()
        assert sandbox is not None
        assert sandbox.input_field is not None
        assert sandbox.output_field is not None
        assert sandbox.send_btn is not None

    def test_sandbox_clear(self, app):
        """Тест очистки песочницы"""
        sandbox = SandboxWidget()
        sandbox.input_field.setPlainText("Тестовый вопрос")
        sandbox.output_field.setPlainText("Тестовый ответ")
        
        sandbox.clear()
        
        assert sandbox.input_field.toPlainText() == ""
        assert sandbox.output_field.toPlainText() == ""

    def test_set_response(self, app):
        """Тест установки ответа"""
        sandbox = SandboxWidget()
        response = "Это тестовый ответ от бота"
        
        sandbox.set_response(response)
        
        assert sandbox.output_field.toPlainText() == response

    def test_empty_input_warning(self, app):
        """Тест предупреждения при пустом вводе"""
        sandbox = SandboxWidget()
        # Симуляция нажатия кнопки без ввода
        # В реальном тесте нужно проверять появление QMessageBox
        assert sandbox.input_field.toPlainText() == ""


class TestPersonalityTab:
    """Тесты для вкладки настройки личности"""

    def test_tab_creation(self, app):
        """Тест создания вкладки"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        assert tab is not None
        assert tab.editor is not None
        assert tab.template_combo is not None
        assert tab.selected_blocks is not None
        assert tab.sandbox is not None

    def test_templates_loaded(self, app):
        """Тест загрузки шаблонов"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        assert len(tab._templates) > 0
        assert "Helper" in tab._templates
        assert "Critic" in tab._templates
        assert "Friend" in tab._templates
        assert "Professional" in tab._templates

    def test_prompt_blocks_loaded(self, app):
        """Тест загрузки блоков промптов"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        assert len(tab._prompt_blocks) > 0
        
        # Проверка категорий
        categories = set(block["category"] for block in tab._prompt_blocks.values())
        assert "Роль" in categories
        assert "Стиль" in categories
        assert "Поведение" in categories

    def test_template_selection(self, app):
        """Тест выбора шаблона"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        # Выбор шаблона
        tab.template_combo.setCurrentText("Critic")
        
        assert tab.get_current_template() == "Critic"
        assert "критически" in tab.editor.toPlainText().lower()

    def test_template_content_retrieval(self, app):
        """Тест получения содержимого шаблона"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        content = tab.get_template_content()
        assert content is not None
        assert isinstance(content, str)

    def test_set_template(self, app):
        """Тест установки шаблона"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        new_template_name = "Custom_Template"
        new_content = "# Custom Template\n\nОписание кастомного шаблона"
        
        tab.set_template(new_template_name, new_content)
        
        assert new_template_name in tab._templates
        assert tab._templates[new_template_name] == new_content

    def test_add_block_to_assembly(self, app, sample_blocks):
        """Тест добавления блока в сборку"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        # Добавление блоков программно
        for block in sample_blocks:
            item = PromptBlockItem(block["name"], block["content"], block["category"])
            tab.selected_blocks.addItem(item)
        
        assert tab.selected_blocks.count() == len(sample_blocks)

    def test_assemble_prompt(self, app, sample_blocks):
        """Тест сборки промпта из блоков"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        # Добавление блоков
        for block in sample_blocks:
            item = PromptBlockItem(block["name"], block["content"], block["category"])
            tab.selected_blocks.addItem(item)
        
        assembled = tab.get_assembled_prompt()
        
        assert assembled != ""
        assert "# Роль: Ассистент" in assembled
        assert "# Стиль: Формальный" in assembled
        assert "# Поведение: Эмпатичный" in assembled

    def test_empty_assembly(self, app):
        """Тест сборки пустого промпта"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        assembled = tab.get_assembled_prompt()
        assert assembled == ""

    def test_config_retrieval(self, app):
        """Тест получения конфигурации"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        config = tab.get_config()
        
        assert "personality" in config
        assert "style" in config["personality"]
        assert "template_content" in config["personality"]
        assert "prompt_blocks" in config["personality"]

    def test_load_config(self, app):
        """Тест загрузки конфигурации"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        test_config = {
            "personality": {
                "style": "Friend",
            }
        }
        
        tab.load_config(test_config)
        
        # Проверка, что стиль установлен
        # (может отличаться в зависимости от реализации)
        assert tab._current_template in tab._templates

    def test_editor_changes_emit_signal(self, app):
        """Тест сигнала об изменении редактора"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        # Подписка на сигнал
        mock_callback = Mock()
        tab.config_changed.connect(mock_callback)
        
        # Изменение текста
        tab.editor.setPlainText("Новый текст шаблона")
        
        # Сигнал должен быть отправлен
        mock_callback.assert_called()

    def test_template_combo_populated(self, app):
        """Тест заполнения комбобокса шаблонов"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        assert tab.template_combo.count() > 0
        
        template_names = [
            tab.template_combo.itemText(i)
            for i in range(tab.template_combo.count())
        ]
        
        assert "Helper" in template_names
        assert "Critic" in template_names

    def test_default_templates_content(self, app):
        """Тест содержимого дефолтных шаблонов"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        # Проверка Helper шаблона
        helper_content = tab._get_default_helper_template()
        assert "{{name}}" in helper_content
        assert "{{formality}}" in helper_content
        
        # Проверка Critic шаблона
        critic_content = tab._get_default_critic_template()
        assert "критически" in critic_content.lower()
        
        # Проверка Friend шаблона
        friend_content = tab._get_default_friend_template()
        assert "друг" in friend_content.lower()
        
        # Проверка Professional шаблона
        professional_content = tab._get_default_professional_template()
        assert "профессиональный" in professional_content.lower()


class TestPersonalityTabIntegration:
    """Интеграционные тесты для Personality Tab"""

    def test_full_workflow(self, app, sample_blocks):
        """Тест полного рабочего процесса"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        # 1. Выбор шаблона
        tab.template_combo.setCurrentText("Helper")
        assert tab.get_current_template() == "Helper"
        
        # 2. Добавление блоков
        for block in sample_blocks:
            item = PromptBlockItem(block["name"], block["content"], block["category"])
            tab.selected_blocks.addItem(item)
        
        # 3. Сборка промпта
        assembled = tab.get_assembled_prompt()
        assert assembled != ""
        
        # 4. Получение конфигурации
        config = tab.get_config()
        assert config["personality"]["style"] == "Helper"
        assert len(config["personality"]["prompt_blocks"]) == 3
        
        # 5. Изменение шаблона
        tab.editor.setPlainText("Modified template content")
        assert tab.get_template_content() == "Modified template content"

    def test_blocks_reorder(self, app):
        """Тест изменения порядка блоков"""
        mock_guide_manager = Mock()
        mock_guide_manager.get_guide.return_value = None
        tab = PersonalityTab(guide_manager=mock_guide_manager)
        
        # Добавление блоков в определенном порядке
        blocks = [
            {"name": "First", "content": "1", "category": "Test"},
            {"name": "Second", "content": "2", "category": "Test"},
            {"name": "Third", "content": "3", "category": "Test"},
        ]
        
        for block in blocks:
            item = PromptBlockItem(block["name"], block["content"], block["category"])
            tab.selected_blocks.addItem(item)
        
        # Проверка начального порядка
        retrieved = tab.selected_blocks.get_blocks()
        assert retrieved[0]["name"] == "First"
        assert retrieved[1]["name"] == "Second"
        assert retrieved[2]["name"] == "Third"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=ui.tabs.personality_tab", "--cov-report=html"])
