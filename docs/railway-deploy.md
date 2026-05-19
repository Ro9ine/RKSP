# Деплой на Railway

Три компонента: **PostgreSQL**, **API** (`apps/api`), **Web** (`apps/web`).  
Фронт ходит в API через **nginx proxy** (переменная `API_UPSTREAM`), отдельный `VITE_API_URL` при деплое не обязателен.

## Шаг 1. Проект и база

1. [railway.app](https://railway.app) → проект с подключённым GitHub-репозиторием.
2. **+ New** → **Database** → **PostgreSQL**.

## Шаг 2. Сервис API

1. **+ New** → **GitHub Repo** → тот же репозиторий (или **Empty Service** + Connect Repo).
2. **Settings** → **Service name:** `workflow-api` (важно для ссылок).
3. **Settings** → **Root Directory:** `apps/api`
4. **Settings** → **Networking** → **Generate Domain** (публичный URL).
5. **Variables:**

| Переменная | Значение |
|------------|----------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` |
| `JWT_SECRET` | случайная строка (32+ символов) |
| `CORS_ORIGINS` | `https://${{workflow-web.RAILWAY_PUBLIC_DOMAIN}}` |

6. Дождаться успешного деплоя. Проверка: `https://<домен-api>/health` → `{"status":"ok"}`.

При старте контейнера выполняются миграции и `seed.py` (тестовые пользователи).

## Шаг 3. Сервис Web

1. **+ New** → **GitHub Repo** → тот же репозиторий.
2. **Service name:** `workflow-web`
3. **Root Directory:** `apps/web`
4. **Networking** → **Generate Domain**
5. **Variables:**

| Переменная | Значение |
|------------|----------|
| `API_UPSTREAM` | `http://${{workflow-api.RAILWAY_PRIVATE_DOMAIN}}:${{workflow-api.PORT}}` |

6. После деплоя открыть `https://<домен-web>/login`.

## Шаг 4. Пересборка API (CORS)

После появления домена web обновите `CORS_ORIGINS` на API (если ещё не задано) и **Redeploy** сервис `workflow-api`.

## Шаг 5. CLI (опционально)

```bash
railway login
cd apps/api
railway link   # выбрать проект и workflow-api
railway up
```

Токен для CI: [Account Tokens](https://railway.app/account/tokens) → `RAILWAY_TOKEN`.

## Тестовые пользователи

| Роль | Email | Пароль |
|------|-------|--------|
| Тимлид | lead@example.com | password123 |
| Сотрудник | anna@ / petr@ / maria@example.com | password123 |

## Локальная разработка фронта

`apps/web/.env`: `VITE_API_URL=http://localhost:8000` (Vite без nginx-proxy).

## Частые ошибки

| Симптом | Решение |
|---------|---------|
| Build failed, Dockerfile not found | Указать Root Directory `apps/api` или `apps/web` |
| API 502 / DB error | Проверить `DATABASE_URL` = reference на Postgres |
| Логин 401 / CORS | Задать `CORS_ORIGINS` с доменом web; пересобрать API |
| Пустой экран после логина | Проверить `API_UPSTREAM` на web, redeploy web |
