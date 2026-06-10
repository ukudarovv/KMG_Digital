# Resume Screening Service

Локальный микросервис для AI-проверки резюме кандидатов. Принимает PDF или DOCX, извлекает текст, анализирует через Ollama (локальная LLM) и возвращает структурированный JSON для HR.

Резюме не отправляются во внешние сервисы — всё работает локально в Docker.

## Требования

- Docker и Docker Compose
- ~5 GB свободного места для модели `qwen2.5:7b`

## Быстрый старт

### 1. Запуск сервисов

```bash
docker compose up --build
```

### 2. Загрузка модели Ollama

После запуска контейнеров скачайте модель (один раз):

```bash
docker exec -it ollama ollama pull qwen2.5:7b
```

### 3. Проверка health

```bash
curl http://localhost:8000/health
```

Ответ:

```json
{
  "status": "ok",
  "service": "resume-screening-service"
}
```

### 4. Swagger UI

Откройте в браузере: [http://localhost:8000/docs](http://localhost:8000/docs)

## Пример запроса

```bash
curl -X POST "http://localhost:8000/screen-resume" \
  -F "file=@resume.pdf" \
  -F "vacancy_title=Junior Python Developer" \
  -F "required_skills=Python,Django,PostgreSQL,Git" \
  -F "optional_skills=Docker,FastAPI" \
  -F "min_experience_years=1"
```

## API

### `GET /health`

Проверка работоспособности сервиса.

### `POST /screen-resume`

Проверка резюме по требованиям вакансии.

**Параметры (multipart/form-data):**

| Поле | Тип | Описание |
|------|-----|----------|
| `file` | file | PDF или DOCX, до 10 MB |
| `vacancy_title` | string | Название вакансии |
| `required_skills` | string | Обязательные навыки через запятую |
| `optional_skills` | string | Желательные навыки через запятую |
| `min_experience_years` | int | Минимальный опыт в годах |

**Логика решения:**

- Совпадение обязательных навыков ≥ 80% и опыт подходит → `pass`
- Совпадение 50–79% → `review`
- Совпадение < 50% → `reject`
- Неполные данные или ошибка LLM → `review`

Финальное решение всегда принимает HR.

## Конфигурация

Скопируйте `.env.example` в `.env` при необходимости:

```bash
cp .env.example .env
```

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `APP_PORT` | `8000` | Внешний порт API (внутри контейнера — 8000) |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | URL Ollama |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Модель LLM |
| `MAX_FILE_SIZE_MB` | `10` | Лимит размера файла |
| `LLM_TIMEOUT_SECONDS` | `120` | Таймаут запроса к LLM |

## Архитектура

```
main backend / сайт
        ↓
POST /screen-resume
        ↓
resume-screening-service (FastAPI)
        ↓
Ollama (локальная LLM)
        ↓
JSON результат
```

## Структура проекта

```
resume-screening-service/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── services/
│   │   ├── file_reader.py
│   │   ├── llm_client.py
│   │   └── screening_service.py
│   └── utils/
│       └── json_parser.py
├── uploads/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Ошибки

| Код | Причина |
|-----|---------|
| 400 | Неверный формат файла, пустой файл, превышен размер |
| 422 | Не удалось извлечь текст из резюме |
| 503 | Ollama недоступна |
| 504 | Таймаут ответа от Ollama |
