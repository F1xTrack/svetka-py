# Implementation Plan: Guide System Engine

## Phase 1: Базовая логика и хранилище
- [x] Task: Разработка механизма извлечения текстов подсказок из \config.yaml\`r
- [x] Task: Создание интерфейса \GuideManager\ для управления базой данных гайдов
- [x] Task: Реализация поддержки Rich Text (HTML) для отображения в Tooltips
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Автоматизация и связь с UI
- [x] Task: Реализация алгоритма автоматической привязки (Auto-bind) к виджетам по ключу конфига
- [x] Task: Добавление поддержки Inline подсказок в базовые виджеты настроек
- [x] Task: Реализация Modal окна помощи (PyQt6 QDialog с прокруткой)
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Интерактивность и UX
- [x] Task: Разработка системы \\
Интерактивного
тура\\ (подсветка элементов при первом запуске)
- [x] Task: Реализация метода \
efresh_guides()\ для динамического обновления текстов в UI
- [x] Task: Оптимизация задержки отображения Tooltips
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Тестирование и верификация
- [x] Task: Написание тестов для проверки автосвязки и парсинга текстов (Покрытие 95%)
- [x] Task: Тестирование UI с использованием видео-тестов (Vision) для верификации \\Тура\\
- [x] Task: Финальный коммит фазы и пуш в GitHub репозиторий
- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
