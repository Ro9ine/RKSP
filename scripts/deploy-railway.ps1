# Деплой Workflow на Railway (требуется: railway login)
# Usage: .\scripts\deploy-railway.ps1

$ErrorActionPreference = "Stop"

if (-not (Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "Установка Railway CLI..."
    npm install -g @railway/cli
}

$whoami = railway whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Выполните вход: railway login"
    railway login
}

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

Write-Host @"

=== Railway: создайте проект вручную (первый раз) ===
1. https://railway.app → New Project → Add PostgreSQL
2. New Service → GitHub Repo (этот репозиторий)
3. Сервис API: Root Directory = apps/api, имя = workflow-api
   Variables: DATABASE_URL = `${{Postgres.DATABASE_URL}}
              JWT_SECRET = <случайная строка>
              CORS_ORIGINS = https://`${{workflow-web.RAILWAY_PUBLIC_DOMAIN}}
4. Сервис Web: Root Directory = apps/web, имя = workflow-web
   Build arg VITE_API_URL = https://<домен-api после деплоя>
5. Public Networking для api и web

Подробно: docs/railway-deploy.md

=== CLI: деплой API из apps/api ===
"@

Set-Location "$root\apps\api"
if (-not (Test-Path ".railway")) {
    Write-Host "Привязка сервиса API (выберите проект и создайте сервис workflow-api)..."
    railway link
}
railway up --detach
Write-Host "API deploy initiated. Затем настройте Web с VITE_API_URL и задеплойте apps/web."
