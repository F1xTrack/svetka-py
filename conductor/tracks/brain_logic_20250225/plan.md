# Implementation Plan: Proactive Brain Logic

## Phase 1: Координатор и Цикл работы
- [ ] Task: Реализация класса ProactiveBrain в core/brain.py
- [ ] Task: Создание асинхронного цикла обработки (Main Loop)
- [ ] Task: Реализация механизма сборки Payload: скриншот + аудио + системный контекст
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Логика принятия решения (Decision Making)
- [ ] Task: Разработка специализированного промпта принятия решения
- [ ] Task: Реализация парсера JSON-ответа (should_speak, text)
- [ ] Task: Интеграция с модулем Personality для учета текущего характера
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Интеграция с TTS и Обратная связь
- [ ] Task: Реализация цепочки вызова: Brain Decision -> TTS Trigger -> Audio Output
- [ ] Task: Добавление поддержки команд пользователя на управление частотой
- [ ] Task: Реализация логики сброса "желания" после фразы
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Тестирование и верификация
- [ ] Task: Написание тестов для Main Loop и сборщика Payload (Покрытие 95%)
- [ ] Task: Симуляция событий для проверки принятия решения через Gemini 2.5 Flash
- [ ] Task: Финальный коммит фазы и пуш в GitHub
- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
