"""
Скрипт валидации prompt блоков.

Проверяет:
- Целостность JSON файлов
- Соответствие схеме
- Уникальность ID
- Корректность {{variables}}
- Статистику по блокам
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Добавляем корень проекта в path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.prompt_manager import PromptManager, PromptBlock


def validate_json_files(blocks_dir: Path) -> Tuple[List[str], List[str]]:
    """
    Валидирует все JSON файлы в директории.

    Returns:
        (errors, warnings) - списки ошибок и предупреждений.
    """
    errors = []
    warnings = []

    if not blocks_dir.exists():
        errors.append(f"Directory not found: {blocks_dir}")
        return errors, warnings

    json_files = list(blocks_dir.glob("*.json"))
    print(f"Found {len(json_files)} JSON files")

    all_ids = set()
    total_blocks = 0

    for file_path in json_files:
        if file_path.name == "schema.json":
            continue

        print(f"\nValidating {file_path.name}...")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                errors.append(f"{file_path.name}: Expected list, got {type(data)}")
                continue

            file_blocks = 0
            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    errors.append(f"{file_path.name}[{i}]: Expected dict, got {type(item)}")
                    continue

                # Проверка обязательных полей
                required = ["id", "name", "category", "content"]
                for field in required:
                    if field not in item:
                        errors.append(f"{file_path.name}[{i}]: Missing required field '{field}'")

                block_id = item.get("id", f"unknown_{i}")

                # Проверка уникальности ID
                if block_id in all_ids:
                    errors.append(f"{file_path.name}: Duplicate ID '{block_id}'")
                else:
                    all_ids.add(block_id)

                # Проверка категории
                category = item.get("category", "")
                valid_categories = [
                    "roles", "styles", "behaviors", "constraints",
                    "intelligence", "humor", "habits", "context",
                    "tone", "special_modes"
                ]
                if category and category not in valid_categories:
                    warnings.append(f"{file_path.name}[{block_id}]: Unknown category '{category}'")

                # Проверка variables в контенте
                content = item.get("content", "")
                variables = item.get("variables", [])
                
                # Извлекаем {{variables}} из контента
                import re
                found_vars = re.findall(r'\{\{(\w+)\}', content)
                
                for var in found_vars:
                    if var not in variables:
                        warnings.append(
                            f"{file_path.name}[{block_id}]: Variable '{var}' used in content "
                            f"but not declared in variables"
                        )

                for var in variables:
                    if f"{{{{{var}}}}}" not in content:
                        warnings.append(
                            f"{file_path.name}[{block_id}]: Variable '{var}' declared but not used"
                        )

                # Проверка priority
                priority = item.get("priority", 50)
                if not (0 <= priority <= 100):
                    errors.append(f"{file_path.name}[{block_id}]: Priority {priority} not in range [0, 100]")

                # Проверка conditional_logic
                cond_logic = item.get("conditional_logic", {})
                if cond_logic:
                    if "requires" in cond_logic and not isinstance(cond_logic["requires"], list):
                        errors.append(f"{file_path.name}[{block_id}]: 'requires' must be a list")
                    if "conflicts" in cond_logic and not isinstance(cond_logic["conflicts"], list):
                        errors.append(f"{file_path.name}[{block_id}]: 'conflicts' must be a list")

                file_blocks += 1

            total_blocks += file_blocks
            print(f"  OK - {file_blocks} blocks validated")

        except json.JSONDecodeError as e:
            errors.append(f"{file_path.name}: Invalid JSON - {e}")
        except Exception as e:
            errors.append(f"{file_path.name}: Error - {e}")

    print(f"\nTotal blocks: {total_blocks}")
    return errors, warnings


def test_prompt_manager():
    """Тестирует PromptManager."""
    print("\n" + "=" * 60)
    print("Testing PromptManager")
    print("=" * 60)

    manager = PromptManager()
    success = manager.load()

    if not success:
        print("Failed to load prompt manager")
        return False

    stats = manager.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total blocks: {stats['total_blocks']}")
    print(f"  Categories with blocks: {stats['categories_with_blocks']}")
    print(f"  Blocks with variables: {stats['blocks_with_variables']}")
    print(f"  Blocks with conditional logic: {stats['blocks_with_conditional_logic']}")
    print(f"\nBlocks by category:")
    for cat, count in stats['blocks_by_category'].items():
        print(f"  {cat}: {count}")

    # Валидация всех блоков
    print("\nValidating all blocks...")
    errors = manager.validate_all()
    if errors:
        print(f"Found {len(errors)} blocks with errors:")
        for block_id, block_errors in errors.items():
            print(f"  {block_id}: {block_errors}")
        return False
    else:
        print("All blocks passed validation")

    # Тест поиска
    print("\nTesting search...")
    results = manager.search("помощник")
    print(f"  Search 'помощник': {len(results)} results")

    results = manager.search_by_tags(["юмор", "творчество"])
    print(f"  Search by tags: {len(results)} results")

    return True


def main():
    """Main функция."""
    blocks_dir = project_root / "assets" / "prompt_blocks"
    
    print("=" * 60)
    print("Prompt Blocks Validation")
    print("=" * 60)
    print(f"\nBlocks directory: {blocks_dir}")

    # Валидация JSON файлов
    errors, warnings = validate_json_files(blocks_dir)

    print("\n" + "=" * 60)
    print("Validation Results")
    print("=" * 60)

    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings[:10]:  # Показываем первые 10
            print(f"  - {w}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return 1
    else:
        print("\nNo errors found!")

    # Тест PromptManager
    if not test_prompt_manager():
        return 1

    print("\n" + "=" * 60)
    print("All validations passed!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
