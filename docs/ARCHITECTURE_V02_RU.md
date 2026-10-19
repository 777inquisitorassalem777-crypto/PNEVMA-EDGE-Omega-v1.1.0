
# Архитектура SCR v0.2.0

## Контур
- **Память**: SQLite остаётся журналом событий для простого запуска; `PostgresSemanticMemory` — необязательное долговременное хранилище в PostgreSQL с `pgvector`.
- **Векторизация**: `SentenceTransformerEmbedding` для локальной модели; `HashEmbedding` — только воспроизводимый тестовый baseline, не семантическая модель.
- **LLM Mesh**: `OpenAICompatibleClient` обращается к `/v1/chat/completions`. Поддерживает OpenAI-совместимые шлюзы, Ollama в режиме OpenAI API и локальные серверы моделей. Реальный провайдер включается через переменные среды.
- **Агенты**: analyst → critic → ethics → synthesis. При недоступности LLM workflow переходит к явно маркированному эвристическому fallback.
- **Эксперименты**: фиксированный набор сценариев, лексические proxy-метрики, JSON-артефакт с версией схемы и SHA-256.
- **API/UI**: FastAPI endpoints и минимальная HTML-панель мониторинга.

## Векторная память: пример использования
```python
from symbio_core.semantic_memory import PostgresSemanticMemory
from symbio_core.embeddings import SentenceTransformerEmbedding

embedder = SentenceTransformerEmbedding()
memory = PostgresSemanticMemory(dimensions=embedder.dimensions)
memory.add("Решение было пересмотрено после новых доказательств",
           embedder.encode("решение пересмотрено новые доказательства"),
           {"kind": "reflection", "experiment": "pilot-01"})
matches = memory.search(embedder.encode("пересмотр решения"), limit=5)
memory.close()
```

## Запуск
```bash
cp .env.example .env
docker compose up --build
```
Панель: `http://localhost:8000`; Swagger: `/docs`.

Для локального Ollama API:
```bash
ollama pull llama3.2
ollama serve
# Set SYMBIO_USE_LLM=true and SYMBIO_LLM_BASE_URL=http://localhost:11434/v1
```
В Docker на Linux адрес хоста может потребовать настройки `host-gateway` или запуска API вне контейнера.

## Границы
- Векторное хранилище и адаптеры подключаются явно; SQLite hash-chain не заменяет резервное копирование или внешнее неизменяемое хранилище.
- SHA-256 артефакта — контроль целостности, не цифровая подпись.
- Автоматические proxy-метрики проверяют наличие признаков в тексте, а не качество морального решения.
- LLM-ответы недетерминированы, могут ошибаться и должны сохранять указание модели/конфигурации при публикации результатов.
- API пока рассчитан на локальный исследовательский запуск; до публичного развертывания нужны аутентификация, TLS, rate limiting и управление секретами.
