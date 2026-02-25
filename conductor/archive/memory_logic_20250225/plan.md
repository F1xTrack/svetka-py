# Implementation Plan: Memory & Context Logic

## Phase 1: Контекст и Подсчет токенов
- [x] Task: Реализация класса ContextManager в core/memory/context.py
- [x] Task: Выбор и реализация единого метода подсчета токенов
- [x] Task: Настройка асинхронного обновления счетчика
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Алгоритм сжатия и Очередь
- [x] Task: Реализация логики "Очередь сохранения": защита последних N сообщений
- [x] Task: Разработка фонового процесса саммаризации через Gemini 2.5 Flash
- [x] Task: Реализация метода подстановки саммари в контекст
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Долгосрочная память (RAG)
- [x] Task: Реализация RAGProcessor с поддержкой FAISS/ChromaDB
- [x] Task: Разработка системы извлечения фактов из диалога
- [x] Task: Реализация поиска по памяти и вставки в системный промпт
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Тестирование и верификация
- [x] Task: Написание тестов для проверки логики сжатия (Покрытие 95%)
- [x] Task: Верификация работы RAG через Gemini 2.5 Flash
- [x] Task: Финальный коммит фазы и пуш в GitHub
- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
