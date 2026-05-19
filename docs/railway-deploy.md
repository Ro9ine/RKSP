# Деплой на Railway

Проект разворачивается как **три сервиса** в одном Railway-проекте: PostgreSQL, API, Web.

## 1. Создать проект

1. [railway.app](https://railway.app) → **New Project**.
2. **Add PostgreSQL** (плагин базы данных).
3. **New Service** → **GitHub Repo** → репозиторий RKSP (или `railway link` из CLI).

## 2. Сервис API (`workflow-api`)

| Параметр | Значение |
|----------|----------|
| Root Directory | `apps/api` |
| Builder | Dockerfile |

**Variables** (вкладка Variables → подключить Postgres):

| Переменная | Значение |
|------------|----------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (reference) |
| `JWT_SECRET` | случайная длинная строка |
| `CORS_ORIGINS` | `https://${{workflow-web.RAILWAY_PUBLIC_DOMAIN}}` |

**Networking:** включить **Public Networking** → получить домен API.

Имя сервиса в Railway должно быть **`workflow-api`** (для ссылки из web) или поправьте `apps/web/railway.toml`.

## 3. Сервис Web (`workflow-web`)

| Параметр | Значение |
|----------|----------|
| Root Directory | `apps/web` |
| Builder | Dockerfile |

**Build argument** (если reference из toml не сработал):

| ARG | Значение |
|-----|----------|
| `VITE_API_URL` | `https://<домен-api>.up.railway.app` |

**Networking:** Public Networking → домен фронтенда.

После первого деплоя API скопируйте его публичный URL в `VITE_API_URL` и **пересоберите** web.

## 4. Порядок деплоя

1. PostgreSQL  
2. API (дождаться `/health`)  
3. Web (с корректным `VITE_API_URL`)  
4. Обновить `CORS_ORIGINS` на API, если менялся домен web → redeploy API  

## 5. CLI (опционально)

```bash
npm install -g @railway/cli
railway login
cd apps/api
railway link
railway up
```

## 6. Тестовые пользователи

При старте контейнера API выполняются миграции и `scripts/seed.py` (идемпотентно).

| Роль | Email | Пароль |
|------|-------|--------|
| Тимлид | lead@example.com | password123 |
| Сотрудник | anna@ / petr@ / maria@example.com | password123 |

Seed также создаёт команду и 7 демо-задач.

## 7. Проверка

- `https://<api>/health` → `{"status":"ok"}`
- `https://<api>/docs` → Swagger
- `https://<web>/login` → вход тимлидом
