# Workflow — клиент-серверное управление рабочими процессами

Курсовой проект: веб-приложение для назначения задач команде, контроля сроков и фиксации результатов выполнения.

## Стек

| Компонент | Технологии |
|-----------|------------|
| Frontend | React 18, TypeScript, Vite, React Router, TanStack Query |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Alembic |
| БД | PostgreSQL 16 |
| Auth | JWT (Bearer) |
| Контейнеризация | Docker, docker-compose |

## Структура репозитория

```
├── apps/
│   ├── api/              # REST API (FastAPI)
│   │   ├── app/          # routers, models, schemas, services
│   │   ├── alembic/      # миграции БД
│   │   ├── scripts/      # seed.py
│   │   ├── tests/        # pytest (RBAC)
│   │   └── railway.toml  # конфиг деплоя Railway
│   └── web/              # SPA (React + Vite)
│       └── railway.toml
├── docs/                 # UML, fuzz-отчёт, railway-deploy.md
├── scripts/              # export-openapi.ps1
└── docker-compose.yml
```

## Роли

- **Teamlead** — создаёт сотрудников, формирует команду, назначает задачи со сроком от 1 часа до 14 дней.
- **Employee** — берёт задачи в работу, оставляет комментарии, отмечает успешное/неуспешное выполнение с обязательным комментарием.

## Быстрый старт (Docker)

```bash
docker compose up --build
```

При старте контейнера **api** автоматически выполняются миграции Alembic и `scripts/seed.py` (повторный seed пропускается, если данные уже есть).

| Сервис | URL |
|--------|-----|
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Web | http://localhost |

## Локальная разработка

### База данных

```bash
docker compose up db -d
```

### API

```bash
cd apps/api
pip install -r requirements.txt
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

`seed.py` нужен только при локальном запуске без Docker (в контейнере seed выполняется сам).

### Frontend

```bash
cd apps/web
npm install
cp .env.example .env
npm run dev
```

| Режим | URL фронтенда |
|-------|----------------|
| `npm run dev` (Vite) | http://localhost:5173 |
| Docker (`web`) | http://localhost |

### Тесты API (pytest)

```bash
cd apps/api
# БД запущена, seed выполнен
pytest
```

## Тестовые учётные записи

Доступны **после seed** (Docker — автоматически; локально — `python scripts/seed.py`).

| Роль | Email | Пароль |
|------|-------|--------|
| Тимлид | lead@example.com | password123 |
| Сотрудник | anna@example.com | password123 |
| Сотрудник | petr@example.com | password123 |
| Сотрудник | maria@example.com | password123 |

Seed также создаёт команду «Команда разработки» и **7 демо-задач** с разными статусами (назначена, в работе, завершена, провалена).

## Fuzz-тестирование

```bash
curl -o openapi.json http://localhost:8000/openapi.json
pip install schemathesis
schemathesis run openapi.json --base-url http://localhost:8000 --checks all --hypothesis-max-examples=50
```

Подробности: [docs/fuzz-report.md](docs/fuzz-report.md).

## Документация

- [Анализ предметной области](docs/domain-analysis.md)
- [UML-диаграммы](docs/uml/)
- [Отчёт по fuzz-тестированию](docs/fuzz-report.md)
- [Деплой на Railway](docs/railway-deploy.md)

## Переменные окружения

### API (`apps/api/.env`)

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | PostgreSQL URL (`postgresql+asyncpg://` или `postgresql://` — конвертируется автоматически) | `postgresql+asyncpg://workflow:workflow@localhost:5432/workflow` |
| `JWT_SECRET` | Секрет для JWT | `dev-secret-change-in-production` |
| `CORS_ORIGINS` | Разрешённые origin через запятую | `http://localhost:5173,http://localhost:80,http://localhost` |

### Web (`apps/web/.env`)

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `VITE_API_URL` | Базовый URL API (задаётся на этапе сборки Vite) | `http://localhost:8000` |

## Облачный деплой (Railway)

Развёртывание: PostgreSQL + API + Web в одном проекте Railway. Подробная инструкция — [docs/railway-deploy.md](docs/railway-deploy.md).

Кратко:

1. Добавить PostgreSQL, сервис API (`apps/api`), сервис Web (`apps/web`).
2. API: `DATABASE_URL` ← reference Postgres; `JWT_SECRET`; `CORS_ORIGINS` ← URL фронтенда.
3. Web: build-arg `VITE_API_URL` = `https://<домен-api>`.
4. Войти тестовым тимлидом (см. таблицу выше).
