# Implementation Plan: Vision Settings UI

## Phase 1: Базовая структура вкладки (UI)
- [x] Task: Создание файла \ui/tabs/vision_tab.py\ и базового класса \VisionTab(QWidget)\`r
- [x] Task: Разметка вкладки: Слайдер интервала, Список мониторов, Опции обработки, Выбор качества
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Логика выбора и Режимы API
- [x] Task: Реализация переключателя режимов: \\
Массив
скриншотов\\ vs \\Видеопоток\\
- [x] Task: Динамическое обновление списка доступных мониторов (через MSS)
- [x] Task: Реализация Статус-бара модуля (активность в реальном времени)
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Интеграция с Core (Config & Guide)
- [x] Task: Привязка виджетов к \ConfigManager\ (чтение/запись)
- [x] Task: Регистрация 7+ элементов вкладки в \Guide Engine\ (автоподсказки)
- [x] Task: Настройка сигналов (Qt Signals) для уведомления фонового процесса
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Тестирование и верификация
- [x] Task: Написание тестов UI: запись всех 5+ параметров (Покрытие 95%)
- [x] Task: Верификация режимов API через Gemini 2.5 Flash
- [x] Task: Финальный коммит и пуш в GitHub
- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
