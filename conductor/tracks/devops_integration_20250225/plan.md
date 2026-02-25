# Implementation Plan: DevOps & Integration

## Phase 1: Poetry и Зависимости
- [ ] Task: Инициализация Poetry в корне проекта (pyproject.toml)
- [ ] Task: Перенос всех зависимостей в Poetry
- [ ] Task: Настройка скриптов запуска и тестирования
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: GitHub и CI/CD
- [ ] Task: Создание GitHub репозитория через API
- [ ] Task: Настройка GitHub Actions для прогона тестов (pytest)
- [ ] Task: Настройка GitHub Actions для автоматической сборки
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Сборка EXE (PyInstaller)
- [ ] Task: Подготовка конфигурационного файла .spec для PyInstaller
- [ ] Task: Реализация скрипта сборки с учетом assets и templates
- [ ] Task: Тестирование запуска .exe на чистой системе
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Финальная интеграция и Релиз
- [ ] Task: Написание тестов для проверки полноты сборки (Покрытие 95%)
- [ ] Task: Создание первого официального релиза (Tag v0.1.0) на GitHub
- [ ] Task: Финальная верификация всего проекта
- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
