# Implementation Plan: Personality Settings UI

## Phase 1: Базовая структура и Редактор (UI)
- [x] Task: Создание файла \ui/tabs/personality_tab.py\ и класса \PersonalityTab(QWidget)\`r
- [x] Task: Реализация списка выбора шаблонов и основного текстового поля (QTextEdit)
- [x] Task: Реализация подсветки тегов \{{...}}\ в редакторе
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Конструктор Блоков и Drag-and-Drop
- [x] Task: Создание виджета для отображения списка блоков по категориям
- [x] Task: Реализация логики Drag-and-Drop для изменения порядка выбранных блоков
- [x] Task: Реализация функции \ssemble_prompt()\, объединяющей MD-фрагменты
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Песочница и Интеграция
- [x] Task: Реализация виджета \\
Песочница\\ (Sandbox): ввод вопроса и вывод ответа LLM
- [x] Task: Привязка логики сохранения и сброса к TemplateManager
- [x] Task: Регистрация всех элементов вкладки в Guide Engine
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Тестирование и верификация
- [x] Task: Написание тестов UI: проверка сборки промпта из блоков (Покрытие 95%)
- [x] Task: Верификация работы Песочницы через Gemini 2.5 Flash
- [x] Task: Финальный коммит и пуш в GitHub
- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
