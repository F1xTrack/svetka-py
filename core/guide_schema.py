"""
Схема валидации для базы гайдов (guides.json).
Использует Pydantic для строгой типизации и валидации.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional
from pathlib import Path
import json


class GuideEntry(BaseModel):
    """Модель одной записи гайда для параметра."""
    
    purpose: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Назначение параметра: за что отвечает"
    )
    impact: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Влияние параметра: на что влияет"
    )
    examples: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Список примеров использования (1-10 примеров)"
    )
    risks: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Риски и побочные эффекты"
    )
    complexity: Optional[str] = Field(
        default=None,
        description="Уровень сложности настройки"
    )
    risk_level: Optional[str] = Field(
        default=None,
        description="Уровень риска изменения параметра"
    )
    recommendation: Optional[str] = Field(
        default=None,
        description="Рекомендация по настройке"
    )
    related: Optional[List[str]] = Field(
        default=None,
        description="Связанные параметры"
    )
    
    @field_validator('examples')
    @classmethod
    def validate_examples(cls, v):
        if not v:
            raise ValueError("Примеры не могут быть пустыми")
        for i, example in enumerate(v):
            if len(example) < 5:
                raise ValueError(f"Пример {i+1} слишком короткий (минимум 5 символов)")
        return v


class SectionGuides(BaseModel):
    """Модель гайдов для одной секции (vision, audio, etc)."""
    
    model_config = {"extra": "allow"}
    
    # Динамические поля для каждого параметра в секции
    # Каждый параметр должен соответствовать GuideEntry


class GuidesMeta(BaseModel):
    """Модель метаданных файла guides.json."""
    
    version: str = Field(..., pattern=r'^\d+\.\d+\.\d+$')
    created: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    description: str = Field(..., min_length=10)
    style: str = Field(..., min_length=5)


class GuidesSchema(BaseModel):
    """Основная модель схемы guides.json."""
    
    model_config = {"extra": "allow", "populate_by_name": True}
    
    meta: GuidesMeta
    schema_def: Dict[str, List[str]] = Field(
        ...,
        alias="schema",
        description="Описание обязательных и опциональных полей"
    )
    guides: Dict[str, Dict[str, GuideEntry]] = Field(
        ...,
        description="Гайды по секциям и параметрам"
    )
    
    @field_validator('guides')
    @classmethod
    def validate_guides_count(cls, v):
        """Проверяет что есть минимум 50 параметров."""
        total_params = sum(len(params) for params in v.values())
        if total_params < 50:
            raise ValueError(f"Минимум 50 параметров требуется, найдено: {total_params}")
        return v
    
    def get_total_params(self) -> int:
        """Возвращает общее количество параметров."""
        return sum(len(params) for params in self.guides.values())
    
    def get_sections(self) -> List[str]:
        """Возвращает список секций."""
        return list(self.guides.keys())
    
    def get_params_for_section(self, section: str) -> List[str]:
        """Возвращает список параметров для секции."""
        if section not in self.guides:
            return []
        return list(self.guides[section].keys())
    
    def get_schema_info(self) -> Dict[str, List[str]]:
        """Возвращает информацию о схеме (required/optional fields)."""
        return self.schema_def


class GuidesValidator:
    """Класс для валидации файла guides.json."""
    
    def __init__(self, file_path: str = "assets/guides.json"):
        self.file_path = Path(file_path)
        self.schema: Optional[GuidesSchema] = None
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def load(self) -> bool:
        """Загружает и валидирует файл guides.json."""
        if not self.file_path.exists():
            self.errors.append(f"Файл не найден: {self.file_path}")
            return False
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Ошибка JSON: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Ошибка чтения: {e}")
            return False
        
        try:
            self.schema = GuidesSchema(**data)
            return True
        except Exception as e:
            self.errors.append(f"Ошибка валидации схемы: {e}")
            return False
    
    def validate_all(self) -> bool:
        """Полная валидация с детальными проверками."""
        if not self.load():
            return False
        
        # Проверка количества параметров
        total = self.schema.get_total_params()
        print(f"[OK] Найдено параметров: {total}")
        
        if total < 50:
            self.errors.append(f"Недостаточно параметров: {total} < 50")
        
        # Проверка секций
        sections = self.schema.get_sections()
        expected_sections = ['vision', 'audio', 'api', 'personality', 'memory', 'privacy', 'appearance']
        
        for section in expected_sections:
            if section not in sections:
                self.warnings.append(f"Отсутствует секция: {section}")
            else:
                params = self.schema.get_params_for_section(section)
                print(f"[OK] Секция '{section}': {len(params)} параметров")
        
        # Проверка обязательных полей для каждого параметра
        required_fields = ['purpose', 'impact', 'examples', 'risks']
        for section_name, section_data in self.schema.guides.items():
            for param_name, param_data in section_data.items():
                for field in required_fields:
                    if not getattr(param_data, field):
                        self.errors.append(
                            f"{section_name}.{param_name}: отсутствует '{field}'"
                        )
        
        return len(self.errors) == 0
    
    def report(self) -> str:
        """Формирует отчёт о валидации."""
        report = []
        report.append("=" * 50)
        report.append("ОТЧЁТ ВАЛИДАЦИИ guides.json")
        report.append("=" * 50)
        
        if self.schema:
            report.append(f"Версия: {self.schema.meta.version}")
            report.append(f"Создано: {self.schema.meta.created}")
            report.append(f"Описание: {self.schema.meta.description}")
            report.append(f"Всего параметров: {self.schema.get_total_params()}")
            report.append("")
        
        if self.errors:
            report.append("ОШИБКИ:")
            for error in self.errors:
                report.append(f"  [X] {error}")
            report.append("")
        
        if self.warnings:
            report.append("ПРЕДУПРЕЖДЕНИЯ:")
            for warning in self.warnings:
                report.append(f"  [!] {warning}")
            report.append("")
        
        if not self.errors:
            report.append("[OK] ВАЛИДАЦИЯ ПРОЙДЕНА")
        else:
            report.append(f"[FAIL] ВАЛИДАЦИЯ ПРОВАЛЕНА ({len(self.errors)} ошибок)")
        
        return "\n".join(report)


def validate_guides(file_path: str = "assets/guides.json") -> bool:
    """Функция для быстрой валидации guides.json."""
    validator = GuidesValidator(file_path)
    is_valid = validator.validate_all()
    print(validator.report())
    return is_valid


if __name__ == "__main__":
    import sys
    
    file_path = sys.argv[1] if len(sys.argv) > 1 else "assets/guides.json"
    is_valid = validate_guides(file_path)
    sys.exit(0 if is_valid else 1)
