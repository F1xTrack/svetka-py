"""
Prompt Blocks Manager - Модуль для загрузки и управления prompt блоками.

Этот модуль предоставляет функциональность для:
- Загрузки модульных JSON файлов с prompt блоками
- Агрегации блоков по категориям
- Валидации структуры блоков
- Поиска и фильтрации блоков
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class PromptBlock:
    """Класс представляющий отдельный prompt блок."""

    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id", "")
        self.name = data.get("name", "")
        self.category = data.get("category", "")
        self.content = data.get("content", "")
        self.description = data.get("description", "")
        self.tags = data.get("tags", [])
        self.variables = data.get("variables", [])
        self.conditional_logic = data.get("conditional_logic", {})
        self.priority = data.get("priority", 50)
        self.locale = data.get("locale", "ru")

    def to_dict(self) -> Dict[str, Any]:
        """Возвращает блок как словарь."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "content": self.content,
            "description": self.description,
            "tags": self.tags,
            "variables": self.variables,
            "conditional_logic": self.conditional_logic,
            "priority": self.priority,
            "locale": self.locale,
        }

    def has_variable(self, var_name: str) -> bool:
        """Проверяет наличие переменной в блоке."""
        return var_name in self.variables

    def has_tag(self, tag: str) -> bool:
        """Проверяет наличие тега у блока."""
        return tag in self.tags

    def conflicts_with(self, other_block_id: str) -> bool:
        """Проверяет конфликт с другим блоком."""
        conflicts = self.conditional_logic.get("conflicts", [])
        return other_block_id in conflicts

    def requires(self, other_block_id: str) -> bool:
        """Проверяет требует ли блок другой блок."""
        requires = self.conditional_logic.get("requires", [])
        return other_block_id in requires


class PromptManager:
    """Менеджер для управления prompt блоками."""

    CATEGORIES = [
        "roles",
        "styles",
        "behaviors",
        "constraints",
        "intelligence",
        "humor",
        "habits",
        "context",
        "tone",
        "special_modes",
    ]

    CATEGORY_NAMES_RU = {
        "roles": "Роли",
        "styles": "Стили",
        "behaviors": "Поведение",
        "constraints": "Ограничения",
        "intelligence": "Интеллект",
        "humor": "Юмор",
        "habits": "Привычки",
        "context": "Контекст",
        "tone": "Тон",
        "special_modes": "Спецрежимы",
    }

    def __init__(self, blocks_dir: Optional[Path] = None):
        """
        Инициализирует менеджер prompt блоков.

        Args:
            blocks_dir: Директория с JSON файлами блоков.
        """
        if blocks_dir is None:
            blocks_dir = Path(__file__).parent.parent / "assets" / "prompt_blocks"
        self.blocks_dir = Path(blocks_dir)
        self.blocks: List[PromptBlock] = []
        self.blocks_by_id: Dict[str, PromptBlock] = {}
        self.blocks_by_category: Dict[str, List[PromptBlock]] = {
            cat: [] for cat in self.CATEGORIES
        }
        self._loaded = False

    def load(self) -> bool:
        """
        Загружает все prompt блоки из модульных JSON файлов.

        Returns:
            True если загрузка успешна, False иначе.
        """
        if self._loaded:
            logger.debug("Prompt blocks already loaded")
            return True

        if not self.blocks_dir.exists():
            logger.error(f"Blocks directory not found: {self.blocks_dir}")
            return False

        loaded_count = 0
        for file_path in self.blocks_dir.glob("*.json"):
            if file_path.name == "schema.json":
                continue
            try:
                count = self._load_file(file_path)
                loaded_count += count
                logger.debug(f"Loaded {count} blocks from {file_path.name}")
            except Exception as e:
                logger.error(f"Error loading {file_path.name}: {e}")

        self._loaded = True
        logger.info(f"Loaded {loaded_count} prompt blocks from {len(self.blocks_by_category)} categories")
        return True

    def _load_file(self, file_path: Path) -> int:
        """
        Загружает блоки из одного JSON файла.

        Args:
            file_path: Путь к JSON файлу.

        Returns:
            Количество загруженных блоков.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            logger.warning(f"Expected list in {file_path}, got {type(data)}")
            return 0

        count = 0
        for item in data:
            try:
                block = PromptBlock(item)
                if block.category not in self.CATEGORIES:
                    logger.warning(
                        f"Unknown category '{block.category}' for block '{block.id}'"
                    )
                self.blocks.append(block)
                self.blocks_by_id[block.id] = block
                if block.category in self.blocks_by_category:
                    self.blocks_by_category[block.category].append(block)
                count += 1
            except Exception as e:
                logger.error(f"Error parsing block in {file_path}: {e}")

        return count

    def get_block(self, block_id: str) -> Optional[PromptBlock]:
        """Возвращает блок по ID."""
        return self.blocks_by_id.get(block_id)

    def get_blocks_by_category(self, category: str) -> List[PromptBlock]:
        """Возвращает все блоки категории."""
        return self.blocks_by_category.get(category, [])

    def get_all_blocks(self) -> List[PromptBlock]:
        """Возвращает все загруженные блоки."""
        return self.blocks.copy()

    def search(self, query: str) -> List[PromptBlock]:
        """
        Ищет блоки по запросу в name, description, tags и content.

        Args:
            query: Поисковый запрос.

        Returns:
            Список найденных блоков.
        """
        query_lower = query.lower()
        results = []
        for block in self.blocks:
            if (
                query_lower in block.name.lower()
                or query_lower in block.description.lower()
                or query_lower in block.content.lower()
                or any(query_lower in tag.lower() for tag in block.tags)
            ):
                results.append(block)
        return results

    def search_by_tags(self, tags: List[str]) -> List[PromptBlock]:
        """
        Ищет блоки по тегам.

        Args:
            tags: Список тегов для поиска.

        Returns:
            Список блоков содержащих хотя бы один из тегов.
        """
        results = []
        for block in self.blocks:
            if any(tag in block.tags for tag in tags):
                results.append(block)
        return results

    def get_blocks_with_variable(self, var_name: str) -> List[PromptBlock]:
        """Возвращает блоки использующие указанную переменную."""
        return [b for b in self.blocks if b.has_variable(var_name)]

    def validate_block(self, block: PromptBlock) -> List[str]:
        """
        Валидирует prompt блок.

        Args:
            block: Блок для валидации.

        Returns:
            Список ошибок валидации (пуст если блок корректен).
        """
        errors = []

        if not block.id:
            errors.append("Block ID is required")
        if not block.name:
            errors.append("Block name is required")
        if not block.category:
            errors.append("Block category is required")
        elif block.category not in self.CATEGORIES:
            errors.append(f"Unknown category: {block.category}")
        if not block.content:
            errors.append("Block content is required")

        if block.priority < 0 or block.priority > 100:
            errors.append("Priority must be between 0 and 100")

        return errors

    def validate_all(self) -> Dict[str, List[str]]:
        """
        Валидирует все загруженные блоки.

        Returns:
            Словарь {block_id: [errors]} для блоков с ошибками.
        """
        errors = {}
        for block in self.blocks:
            block_errors = self.validate_block(block)
            if block_errors:
                errors[block.id] = block_errors
        return errors

    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику по блокам."""
        return {
            "total_blocks": len(self.blocks),
            "blocks_by_category": {
                cat: len(blocks) for cat, blocks in self.blocks_by_category.items()
            },
            "categories_with_blocks": sum(
                1 for blocks in self.blocks_by_category.values() if blocks
            ),
            "blocks_with_variables": sum(1 for b in self.blocks if b.variables),
            "blocks_with_conditional_logic": sum(
                1 for b in self.blocks if b.conditional_logic
            ),
        }

    def export_to_json(self, output_path: Path) -> bool:
        """
        Экспортирует все блоки в один JSON файл.

        Args:
            output_path: Путь для выходного файла.

        Returns:
            True если экспорт успешен.
        """
        try:
            data = [block.to_dict() for block in self.blocks]
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Exported {len(data)} blocks to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting blocks: {e}")
            return False


# Singleton instance для удобного доступа
_manager: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """Возвращает singleton экземпляр PromptManager."""
    global _manager
    if _manager is None:
        _manager = PromptManager()
    return _manager


def load_prompt_blocks() -> List[PromptBlock]:
    """Удобная функция для загрузки всех prompt блоков."""
    manager = get_prompt_manager()
    manager.load()
    return manager.get_all_blocks()
