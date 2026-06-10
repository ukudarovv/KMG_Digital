# KMG Onboarding Backend

FastAPI + PostgreSQL + Alembic. Этапы онбординга, Culture Fit, RAG по ВНД, Bitrix skeleton, HR dashboard, risk engine, APScheduler.

## Запуск

### Docker (рекомендуется)

```bash
docker compose up --build -d
```

- Swagger: http://localhost:8010/docs
- Health: http://localhost:8010/api/health

Миграции и seed выполняются сервисом `backend-init` автоматически.

### Локально

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.scripts.seed
uvicorn app.main:app --reload --port 8000
```

## Seed

```bash
python -m app.scripts.seed
```

Создаёт:
- сотрудника ID=1 (Азамат Нурланов, bitrix_user_id=1001)
- 23 Culture Fit nudges
- задачи Дня 1 и Вовлечения (F-10, F-11)
- 4 документа ВНД (PDF из `KMG Digital/Docs` если доступны)
- данные адаптации (1:1, SMART, обучение)

## Индексация ВНД для RAG

```bash
python -m app.scripts.index_vnd
```

Извлекает текст из PDF (pypdf), дополняет `app/data/vnd_rag_chunks.json`. Сканированные PDF используют предзагруженные чанки.

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| `DATABASE_URL` | PostgreSQL connection string |
| `BITRIX_WEBHOOK_URL` | REST webhook Bitrix24 (пусто = mock) |
| `BITRIX_BOT_ID` | ID imbot |
| `BITRIX_HR_USER_ID` | ID HR для алертов |
| `CHAIRMAN_VIDEO_URL` | Ссылка на видео ПП |
| `RISK_ENGINE_INTERVAL_MINUTES` | Интервал risk engine |

## APScheduler

- 00:00 — сброс `sent_today` для nudges
- 16:00 — HR-алерт по незакрытым инструктажам Дня 1
- День 14/30 — триггер опросов
- За 2 дня до 1:1 — напоминание
- День 90 — HR sentiment-отчёт
- Risk engine — каждые N минут

## Bitrix интеграция

`app/integrations/bitrix/`:
- `client.py` — REST (imbot.send, tasks.task.add)
- `service.py` — OnUserLogin, sync задач

Webhook:
- `POST /api/webhooks/on-user-login/{employee_id}`
- `POST /api/webhooks/on-user-login/bitrix/{bitrix_user_id}`

## Digital Buddy + локальная LLM

Digital Buddy использует **Ollama** с моделью `qwen2.5:3b` (русский и казахский) и контекстом из ВНД (RAG).

```bash
docker compose up --build -d
docker compose up ollama-init   # первичная загрузка модели (~2 GB)
```

Проверка:

```http
GET /api/digital-buddy/status
POST /api/digital-buddy/ask
```

Если Ollama недоступна, backend автоматически переключается на keyword-RAG и шаблонные ответы.

Переменные:

| Переменная | Описание |
|------------|----------|
| `LLM_ENABLED` | Включить локальную модель |
| `OLLAMA_BASE_URL` | URL Ollama (`http://ollama:11434` в Docker) |
| `OLLAMA_MODEL` | Имя модели (`qwen2.5:3b`) |

Локально без Docker:

```bash
ollama pull qwen2.5:3b
OLLAMA_BASE_URL=http://127.0.0.1:11434
```


```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
```

Текущая head: `005_vnd_and_task_fields`
