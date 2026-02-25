"""
Тесты для системы гайдов (guides.json и guide_schema.py).
Покрывает валидацию схемы, наличие всех параметров и полей.
"""

import pytest
import json
from pathlib import Path
from core.guide_schema import (
    GuideEntry,
    GuidesSchema,
    GuidesValidator,
    validate_guides,
)


# Фикстуры
@pytest.fixture
def guides_file_path() -> str:
    """Путь к файлу guides.json."""
    return "assets/guides.json"


@pytest.fixture
def guides_data(guides_file_path: str) -> dict:
    """Загружает данные guides.json."""
    with open(guides_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture
def guides_schema(guides_data: dict) -> GuidesSchema:
    """Создаёт валидную схему guides.json."""
    return GuidesSchema(**guides_data)


# Тесты метаданных
class TestGuidesMetadata:
    """Тесты метаданных файла guides.json."""
    
    def test_meta_exists(self, guides_data: dict):
        """Проверяет наличие секции meta."""
        assert 'meta' in guides_data
        assert isinstance(guides_data['meta'], dict)
    
    def test_meta_version_format(self, guides_schema: GuidesSchema):
        """Проверяет формат версии (semver)."""
        assert guides_schema.meta.version
        assert len(guides_schema.meta.version.split('.')) == 3
    
    def test_meta_created_date(self, guides_schema: GuidesSchema):
        """Проверяет формат даты создания (YYYY-MM-DD)."""
        assert guides_schema.meta.created
        parts = guides_schema.meta.created.split('-')
        assert len(parts) == 3
        assert len(parts[0]) == 4  # год
        assert len(parts[1]) == 2  # месяц
        assert len(parts[2]) == 2  # день
    
    def test_meta_description(self, guides_schema: GuidesSchema):
        """Проверяет наличие описания."""
        assert guides_schema.meta.description
        assert len(guides_schema.meta.description) >= 10
    
    def test_meta_style(self, guides_schema: GuidesSchema):
        """Проверяет наличие стиля."""
        assert guides_schema.meta.style
        assert len(guides_schema.meta.style) >= 5


# Тесты схемы
class TestGuidesSchemaStructure:
    """Тесты структуры схемы guides.json."""
    
    def test_schema_section_exists(self, guides_data: dict):
        """Проверяет наличие секции schema."""
        assert 'schema' in guides_data
    
    def test_schema_required_fields(self, guides_data: dict):
        """Проверяет наличие required_fields в schema."""
        assert 'required_fields' in guides_data['schema']
        required = guides_data['schema']['required_fields']
        assert 'purpose' in required
        assert 'impact' in required
        assert 'examples' in required
        assert 'risks' in required
    
    def test_schema_optional_fields(self, guides_data: dict):
        """Проверяет наличие optional_fields в schema."""
        assert 'optional_fields' in guides_data['schema']
        optional = guides_data['schema']['optional_fields']
        assert 'complexity' in optional
        assert 'risk_level' in optional
        assert 'recommendation' in optional


# Тесты количества параметров
class TestParameterCount:
    """Тесты количества параметров."""
    
    def test_total_params_minimum_50(self, guides_schema: GuidesSchema):
        """Проверяет что всего параметров минимум 50."""
        total = guides_schema.get_total_params()
        assert total >= 50, f"Недостаточно параметров: {total} < 50"
    
    def test_vision_section_exists(self, guides_schema: GuidesSchema):
        """Проверяет наличие секции vision."""
        assert 'vision' in guides_schema.guides
    
    def test_audio_section_exists(self, guides_schema: GuidesSchema):
        """Проверяет наличие секции audio."""
        assert 'audio' in guides_schema.guides
    
    def test_api_section_exists(self, guides_schema: GuidesSchema):
        """Проверяет наличие секции api."""
        assert 'api' in guides_schema.guides
    
    def test_personality_section_exists(self, guides_schema: GuidesSchema):
        """Проверяет наличие секции personality."""
        assert 'personality' in guides_schema.guides
    
    def test_memory_section_exists(self, guides_schema: GuidesSchema):
        """Проверяет наличие секции memory."""
        assert 'memory' in guides_schema.guides
    
    def test_privacy_section_exists(self, guides_schema: GuidesSchema):
        """Проверяет наличие секции privacy."""
        assert 'privacy' in guides_schema.guides
    
    def test_appearance_section_exists(self, guides_schema: GuidesSchema):
        """Проверяет наличие секции appearance."""
        assert 'appearance' in guides_schema.guides
    
    def test_vision_params_count(self, guides_schema: GuidesSchema):
        """Проверяет количество параметров в секции vision (минимум 7)."""
        vision_params = guides_schema.get_params_for_section('vision')
        assert len(vision_params) >= 7, f"vision: {len(vision_params)} < 7"
    
    def test_audio_params_count(self, guides_schema: GuidesSchema):
        """Проверяет количество параметров в секции audio (минимум 7)."""
        audio_params = guides_schema.get_params_for_section('audio')
        assert len(audio_params) >= 7, f"audio: {len(audio_params)} < 7"
    
    def test_api_params_count(self, guides_schema: GuidesSchema):
        """Проверяет количество параметров в секции api (минимум 7)."""
        api_params = guides_schema.get_params_for_section('api')
        assert len(api_params) >= 7, f"api: {len(api_params)} < 7"
    
    def test_personality_params_count(self, guides_schema: GuidesSchema):
        """Проверяет количество параметров в секции personality (минимум 7)."""
        personality_params = guides_schema.get_params_for_section('personality')
        assert len(personality_params) >= 7, f"personality: {len(personality_params)} < 7"
    
    def test_memory_params_count(self, guides_schema: GuidesSchema):
        """Проверяет количество параметров в секции memory (минимум 7)."""
        memory_params = guides_schema.get_params_for_section('memory')
        assert len(memory_params) >= 7, f"memory: {len(memory_params)} < 7"


# Тесты обязательных полей
class TestRequiredFields:
    """Тесты обязательных полей каждого параметра."""
    
    @pytest.mark.parametrize("section_name,params", [
        ('vision', ['enabled', 'fps', 'capture_region', 'model', 'threshold']),
        ('audio', ['mic_enabled', 'sample_rate', 'stt_model', 'tts_enabled']),
        ('api', ['base_url', 'api_key', 'model_name', 'temperature']),
        ('personality', ['name', 'style', 'humor_level', 'empathy']),
        ('memory', ['storage_type', 'long_term_enabled', 'rag_enabled']),
        ('privacy', ['screen_logging_enabled', 'data_retention_days']),
        ('appearance', ['theme', 'language', 'font_size']),
    ])
    def test_sample_params_have_required_fields(
        self,
        guides_schema: GuidesSchema,
        section_name: str,
        params: list
    ):
        """Проверяет наличие обязательных полей у выбранных параметров."""
        for param_name in params:
            param = guides_schema.guides[section_name][param_name]
            assert param.purpose, f"{section_name}.{param_name}.purpose пуст"
            assert param.impact, f"{section_name}.{param_name}.impact пуст"
            assert param.risks, f"{section_name}.{param_name}.risks пуст"
            assert param.examples, f"{section_name}.{param_name}.examples пуст"
            assert len(param.examples) >= 1, f"{section_name}.{param_name}.examples пуст"
    
    def test_all_params_have_required_fields(self, guides_schema: GuidesSchema):
        """Проверяет наличие обязательных полей у ВСЕХ параметров."""
        for section_name, section_data in guides_schema.guides.items():
            for param_name, param_data in section_data.items():
                assert param_data.purpose, f"{section_name}.{param_name}.purpose пуст"
                assert len(param_data.purpose) >= 10, f"{section_name}.{param_name}.purpose слишком короткий"
                
                assert param_data.impact, f"{section_name}.{param_name}.impact пуст"
                assert len(param_data.impact) >= 10, f"{section_name}.{param_name}.impact слишком короткий"
                
                assert param_data.risks, f"{section_name}.{param_name}.risks пуст"
                assert len(param_data.risks) >= 10, f"{section_name}.{param_name}.risks слишком короткий"
                
                assert param_data.examples, f"{section_name}.{param_name}.examples пуст"
                assert len(param_data.examples) >= 1, f"{section_name}.{param_name}.examples пуст"


# Тесты качества контента
class TestContentQuality:
    """Тесты качества контента гайдов."""
    
    def test_examples_not_empty(self, guides_schema: GuidesSchema):
        """Проверяет что примеры не пустые."""
        for section_name, section_data in guides_schema.guides.items():
            for param_name, param_data in section_data.items():
                assert len(param_data.examples) >= 1, \
                    f"{section_name}.{param_name}: примеры пустые"
    
    def test_examples_min_length(self, guides_schema: GuidesSchema):
        """Проверяет минимальную длину примеров."""
        for section_name, section_data in guides_schema.guides.items():
            for param_name, param_data in section_data.items():
                for i, example in enumerate(param_data.examples):
                    assert len(example) >= 5, \
                        f"{section_name}.{param_name}[{i}]: пример слишком короткий"
    
    def test_purpose_min_length(self, guides_schema: GuidesSchema):
        """Проверяет минимальную длину purpose."""
        for section_name, section_data in guides_schema.guides.items():
            for param_name, param_data in section_data.items():
                assert len(param_data.purpose) >= 10, \
                    f"{section_name}.{param_name}.purpose слишком короткий"
    
    def test_impact_min_length(self, guides_schema: GuidesSchema):
        """Проверяет минимальную длину impact."""
        for section_name, section_data in guides_schema.guides.items():
            for param_name, param_data in section_data.items():
                assert len(param_data.impact) >= 10, \
                    f"{section_name}.{param_name}.impact слишком короткий"
    
    def test_risks_min_length(self, guides_schema: GuidesSchema):
        """Проверяет минимальную длину risks."""
        for section_name, section_data in guides_schema.guides.items():
            for param_name, param_data in section_data.items():
                assert len(param_data.risks) >= 10, \
                    f"{section_name}.{param_name}.risks слишком короткий"


# Тесты валидатора
class TestGuidesValidator:
    """Тесты класса GuidesValidator."""
    
    def test_validator_load_success(self, guides_file_path: str):
        """Проверяет успешную загрузку валидного файла."""
        validator = GuidesValidator(guides_file_path)
        assert validator.load() is True
        assert validator.schema is not None
    
    def test_validator_report(self, guides_file_path: str):
        """Проверяет формирование отчёта."""
        validator = GuidesValidator(guides_file_path)
        validator.validate_all()
        report = validator.report()
        assert "ОТЧЁТ ВАЛИДАЦИИ" in report
        assert "Всего параметров:" in report
    
    def test_validate_guides_function(self, guides_file_path: str):
        """Проверяет функцию validate_guides."""
        result = validate_guides(guides_file_path)
        assert result is True


# Тесты для несуществующего файла
class TestMissingFile:
    """Тесты обработки отсутствующего файла."""
    
    def test_missing_file(self, tmp_path):
        """Проверяет обработку отсутствующего файла."""
        missing_file = str(tmp_path / "nonexistent.json")
        validator = GuidesValidator(missing_file)
        assert validator.load() is False
        assert len(validator.errors) > 0
        assert "Файл не найден" in validator.errors[0]


# Тесты для невалидного JSON
class TestInvalidJSON:
    """Тесты обработки невалидного JSON."""
    
    def test_invalid_json(self, tmp_path):
        """Проверяет обработку невалидного JSON."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json }")
        
        validator = GuidesValidator(str(invalid_file))
        assert validator.load() is False
        assert len(validator.errors) > 0
        assert "Ошибка JSON" in validator.errors[0]


# Интеграционный тест
class TestIntegration:
    """Интеграционные тесты."""
    
    def test_full_validation_workflow(self, guides_file_path: str):
        """Полный цикл валидации."""
        validator = GuidesValidator(guides_file_path)
        is_valid = validator.validate_all()
        
        assert is_valid is True, f"Валидация провалена: {validator.errors}"
        assert validator.schema is not None
        assert validator.schema.get_total_params() >= 50
        assert len(validator.errors) == 0
