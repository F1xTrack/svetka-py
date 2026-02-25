# Implementation Plan: AI & API Settings UI

## Phase 1: Базовая разметка вкладки (UI)
- [x] Task: Создание файла \ui/tabs/api_tab.py\ и базового класса \APISettingsTab(QWidget)\`r
- [x] Task: Разметка основных блоков: Провайдеры, Поля ввода Ключей, Параметры модели
- [x] Task: Реализация полей ввода ключей с кнопкой переключения видимости
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Логика выбора и Кастомные URL
- [x] Task: Реализация выпадающего списка Провайдеров и Схем API
- [x] Task: Добавление поля для ввода Custom Base URL
- [x] Task: Реализация слайдеров для Temperature и Top-P
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Функционал проверки и Интеграция
- [x] Task: Реализация асинхронного метода \	est_connection()\ (Ping API)
- [x] Task: Привязка виджетов к \ConfigManager\ (чтение/запись)
- [x] Task: Регистрация 7+ элементов вкладки в \Guide Engine\ (автоподсказки)
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Тестирование и верификация
- [x] Task: Написание тестов UI: проверка записи параметров API (Покрытие 95%)
- [x] Task: Верификация работы Теста соединения через Gemini 2.5 Flash
- [x] Task: Финальный коммит и пуш в GitHub
- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
