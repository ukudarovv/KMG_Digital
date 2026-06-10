# KMG Digital Onboarding — Mobile

Flutter-приложение для сотрудников: этапы адаптации 2–5, Digital Buddy, задачи Дня 1, Culture Fit Nudges, опросы и HR-аналитика. Использует тот же FastAPI-backend, что и веб-версия (`../backend`).

## Запуск

```bash
flutter pub get
flutter run
```

Backend должен быть запущен (`docker compose up -d` в корне репозитория).

## API URL

Выбирается автоматически:

- Debug, Android-эмулятор: `http://10.0.2.2:8010/api`
- Debug, iOS-симулятор / desktop: `http://127.0.0.1:8010/api`
- Release: `https://api.kmg.aqlant.com/api` (продакшн)

Переопределение: `flutter run --dart-define=API_URL=https://api.kmg.aqlant.com/api`

## Структура

```
lib/
├── main.dart, app.dart        # точка входа, тема, go_router
├── core/                      # config (API URL), theme (палитра KMG), dio
├── models/                    # Dart-модели (зеркало src/api/*.ts сайта)
├── api/                       # onboarding, digital buddy, surveys, adaptation, hr
├── features/
│   ├── home/                  # 5 этапов адаптации
│   ├── introduction/          # День 1: задачи, видео, welcome-попап
│   ├── engagement/            # Culture Fit, опросы 14/30
│   ├── adaptation/            # 1:1, SMART-цели, обучение (read-only)
│   ├── retention/             # sentiment, риски, Final NPS
│   └── digital_buddy/         # чат с RAG по ВНД (RU/KK)
└── shared/widgets/            # TaskCard, ProgressCard, PDF viewer, scaffold
```

Демо-режим: сотрудник с ID 1 (Азамат Нурланов), как на сайте.
