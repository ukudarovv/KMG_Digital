# KMG Digital Onboarding

Прототип цифрового онбординга для хакатона KMG Digital: 5 этапов адаптации, Culture Fit nudges, Digital Buddy с RAG по ВНД, Bitrix24-интеграция (mock/demo), HR-аналитика.

## Быстрый старт

### Весь стек в Docker (рекомендуется)

```bash
docker compose up --build -d
```

- **UI:** http://localhost:5174
- **API:** http://localhost:8010/docs
- **PostgreSQL:** localhost:5433

Миграции и seed выполняются автоматически (`backend-init`).  
Фронтенд собирается в образ и отдаётся через nginx; запросы `/api` проксируются на backend.

### Локальная разработка фронтенда (опционально)

```bash
npm install
npm run dev
```

- UI: http://localhost:5174
- Переменная `VITE_API_URL` в `.env`: `http://127.0.0.1:8010/api`

## Демо-сценарии ТЗ

### Сценарий 1 — День 1 (Знакомство)

1. Откройте `/introduction`
2. Выполните 6 задач: видео, ТБ, ИБ, пропускной режим, кодекс, комплаенс
3. Для задач с ВНД нажмите «Открыть материал» → PDF из `backend/app/data/vnd/`
4. Подтвердите ознакомление кнопкой «Подтвердить ознакомление»

### Сценарий 2 — Culture Fit (Вовлечение)

1. Откройте `/engagement`
2. При первом входе показывается popup с карточкой дня
3. «Отправить в чат» → imbot.send (mock без Bitrix webhook)
4. Банк 23 карточек — клик открывает любую карточку
5. Задачи F-10 (ДИ, день 3) и F-11 (КПД, день 5) — блок «ДИ и цели КПД»

### Сценарий 3 — Digital Buddy RAG

1. На `/introduction` откройте чат Digital Buddy
2. Задайте вопросы:
   - «Какие правила пропускного режима?»
   - «Что такое конфликт интересов?»
   - «Как вести деловую переписку?»
3. Ответ содержит источник (код ВНД) и раздел

## ВНД и RAG

PDF копируются из `KMG Digital/Docs` при seed (если папка доступна). Для сканированных PDF используются предзагруженные чанки в `backend/app/data/vnd_rag_chunks.json`.

Переиндексация (опционально):

```bash
docker compose exec backend python -m app.scripts.index_vnd
```

## Локальная LLM (Digital Buddy)

Стек включает **Ollama** с моделью `qwen2.5:3b` для диалога на русском и казахском.

```bash
docker compose up -d ollama
docker compose run --rm ollama-init
```

Статус модели: `GET http://localhost:8010/api/digital-buddy/status`


## Bitrix24 (опционально)

В `backend/.env`:

```env
BITRIX_WEBHOOK_URL=https://your-portal.bitrix24.ru/rest/1/xxx/
BITRIX_BOT_ID=123
BITRIX_HR_USER_ID=456
```

Webhook OnUserLogin:

```http
POST /api/webhooks/on-user-login/{employee_id}
POST /api/webhooks/on-user-login/bitrix/{bitrix_user_id}
```

Без webhook — mock-режим: задачи и nudges логируются локально.

## Ключевые API

| Endpoint | Назначение |
|----------|------------|
| `GET /api/vnd/documents` | Список ВНД |
| `GET /api/vnd/documents/{code}/file` | Скачать PDF |
| `GET /api/onboarding/day-one/tasks/{id}` | Задачи Дня 1 |
| `GET /api/onboarding/engagement/tasks/{id}` | Задачи F-10/F-11 |
| `POST /api/onboarding/tasks/{id}/complete` | Подтвердить задачу |
| `POST /api/digital-buddy/ask` | RAG-ответ |
| `POST /api/webhooks/on-user-login/{id}` | OnUserLogin |
| `GET /api/hr/employees/{id}/detail` | HR-отчёт (этап 5) |

## Мобильное приложение (Flutter)

Приложение для сотрудников в папке `mobile/` — функциональный паритет с employee-частью сайта (этапы 2–5, Digital Buddy, задачи, Culture Fit, опросы). Работает с тем же backend.

### Запуск

```bash
cd mobile
flutter pub get
flutter run
```

### API URL

По умолчанию приложение само выбирает адрес backend:

- Debug, Android-эмулятор: `http://10.0.2.2:8010/api`
- Debug, iOS-симулятор и desktop: `http://127.0.0.1:8010/api`
- Release: `https://api.kmg.aqlant.com/api` (продакшн)

Переопределить можно при сборке:

```bash
flutter run --dart-define=API_URL=https://api.kmg.aqlant.com/api
```

## Продакшн-домены

| Домен | Назначение | A-запись |
|-------|------------|----------|
| `kmg.aqlant.com` | Frontend (React SPA) | 194.32.141.90 |
| `api.kmg.aqlant.com` | Backend API (FastAPI) | 194.32.141.90 |

Для продакшн-сборки фронтенда: `VITE_API_URL=https://api.kmg.aqlant.com/api`.
В `backend/.env`: `ENVIRONMENT=production` и `FRONTEND_URL=https://kmg.aqlant.com` (CORS).

### Demo-сценарии в приложении

1. **День 1** — экран «Знакомство»: welcome-попап Digital Buddy, 6 задач, ВНД-PDF во встроенном viewer, кнопка «Симулировать вход» в шапке.
2. **Culture Fit** — экран «Вовлечение»: попап карточки дня, банк 23 карточек, «Отправить в чат», сдвиг дня адаптации (2–30), опросы дня 14 и 30.
3. **Digital Buddy RAG** — кнопка «Buddy» на любом экране: вопросы по ВНД на русском и казахском, ответ с источником.

## Тестовый сотрудник

```
ID: 1
ФИО: Азамат Нурланов
Bitrix User ID: 1001
```

## Структура этапов

| Этап | Страница | Статус |
|------|----------|--------|
| 1 Подготовка | — | disabled (на team.kmg.kz) |
| 2 Знакомство | `/introduction` | 6 задач + Digital Buddy |
| 3 Вовлечение | `/engagement` | 23 nudges, опросы 14/30 |
| 4 Адаптация | `/adaptation` | 1:1, SMART, обучение |
| 5 Закрепление | `/retention` | Sentiment, at_risk, Final NPS |
