# Implementation Plan: Appearance & Errors UI (Tab 6)

## Phase 1: Интеграция браузерного движка и Базовая разметка
- [x] Task: Настройка QtWebEngine для работы внутри PyQt6 приложения
- [x] Task: Создание файла ui/tabs/appearance_tab.py и связь его с веб-вью
- [x] Task: Разработка HTML/CSS шаблона для тёмной темы вкладок настроек
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Кастомизация Окна Ошибок
- [x] Task: Реализация веб-компонента для плавающего окна уведомлений
- [x] Task: Реализация логики Drag-and-Drop для окна ошибок и запись координат в ConfigManager
- [x] Task: Добавление слайдеров прозрачности и таймеров в UI настроек
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Системный трей и Интеграция
- [x] Task: Реализация QSystemTrayIcon с иконкой "Svetka"
- [x] Task: Создание контекстного меню трея с быстрыми действиями
- [x] Task: Регистрация всех элементов вкладки в Guide Engine (автоподсказки)
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Тестирование и верификация
- [x] Task: Написание тестов UI: проверка сохранения позиции окна (Покрытие 95%)
- [x] Task: Верификация работы трея и веб-интерфейса через Gemini 2.5 Flash
- [x] Task: Финальный коммит фазы и пуш в GitHub репозиторий
- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
