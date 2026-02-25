# Implementation Plan: Memory Settings UI (Tab 5)

## Phase 1: Базовая структура и Контекст (UI)
- [x] Task: Создание файла ui/tabs/memory_tab.py и базового класса MemorySettingsTab(QWidget)
- [x] Task: Разметка блока "Управление контекстом": Слайдер токенов, Очередь (N), Чекбокс Авто-саммаризации
- [x] Task: Реализация прогресс-бара "Индикатор Токенов" с цветовой индикацией
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Настройки RAG и Файловые операции
- [x] Task: Разметка блока "База знаний (RAG)": Выбор пути к файлу, Слайдер глубины поиска (K)
- [x] Task: Реализация кнопок "Экспорт" и "Импорт" памяти (QFileDialog)
- [x] Task: Реализация кнопки "Очистка памяти" с диалогом подтверждения
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Интеграция и Реактивность
- [x] Task: Привязка виджетов к ConfigManager (чтение/запись)
- [x] Task: Регистрация всех 7+ элементов вкладки в Guide Engine (автоподсказки)
- [x] Task: Реализация метода update_token_counter(current, limit)
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Тестирование и верификация
- [x] Task: Написание тестов UI: проверка записи параметров памяти (Покрытие 95%)
- [x] Task: Верификация работы Индикатора токенов через Gemini 2.5 Flash
- [x] Task: Финальный коммит фазы и пуш в GitHub репозиторий
- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
