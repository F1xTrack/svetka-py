# Implementation Plan: Audio Settings UI

## Phase 1: Базовая структура вкладки (UI)
- [x] Task: Создание файла \ui/tabs/audio_tab.py\ и базового класса \AudioTab(QWidget)\`r
- [x] Task: Разметка вкладки: Список микрофонов, Системный звук, Настройки TTS (Громкость/Скорость/Голос)
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Логика аудио и Выбор режима
- [x] Task: Реализация переключателя режимов: \\
Standard
STT\\ vs \\Native
Multimodal
\\
- [x] Task: Динамическое обновление списка микрофонов (через Sounddevice)
- [x] Task: Реализация VUmeter (Индикатор громкости микрофона)
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Интеграция с Core (Config & Guide)
- [x] Task: Привязка виджетов к \ConfigManager\ (чтение/запись)
- [x] Task: Регистрация 7+ элементов вкладки в \Guide Engine\ (автоподсказки)
- [x] Task: Реализация фильтра \\Noise
Gate\\ (Порог шума) в UI логике
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Тестирование и верификация
- [x] Task: Написание тестов UI: проверка записи параметров Audio (Покрытие 95%)
- [x] Task: Верификация работы VUmeter через Gemini 2.5 Flash
- [x] Task: Финальный коммит и пуш в GitHub
- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
