# Implementation Plan: Privacy Settings UI (Tab 7)

## Phase 1: Фильтрация Приложений (Blacklist)
- [x] Task: Создание файла ui/tabs/privacy_tab.py и базовой разметки
- [x] Task: Реализация списка игнорируемых окон (QListView/QListWidget)
- [x] Task: Реализация кнопки "Добавить активное окно" через Win32 API
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Маскирование и Offline Режим
- [x] Task: Реализация инструмента выбора зон маскирования на экране (Overlay selector)
- [x] Task: Добавление глобального переключателя "Offline-Only Mode"
- [x] Task: Реализация логики блокировки API запросов при включённом Offline режиме
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Аудит и Удаление данных
- [x] Task: Реализация виджета "Журнал передачи данных"
- [x] Task: Реализация кнопки "Очистка данных (Wipe)"
- [x] Task: Регистрация всех элементов вкладки в Guide Engine (автоподсказки)
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Тестирование и верификация
- [x] Task: Написание тестов UI: проверка блокировки чёрного списка (Покрытие 95%)
- [x] Task: Верификация работы Offline режима через Gemini 2.5 Flash
- [x] Task: Финальный коммит фазы и пуш в GitHub репозиторий
- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
