# Отчёт по fuzz-тестированию API

## Инструмент

**Schemathesis** — property-based тестирование на основе спецификации OpenAPI 3.x, сгенерированной FastAPI.

## Подготовка

```bash
# API должен быть запущен
curl -o openapi.json http://localhost:8000/openapi.json

pip install schemathesis
schemathesis run openapi.json \
  --base-url http://localhost:8000 \
  --checks all \
  --hypothesis-max-examples=30 \
  --report junit
```

## Ожидаемое поведение (защитные механизмы)

| Сценарий | Ожидаемый код | Реализация |
|----------|---------------|------------|
| Запрос без JWT к защищённым эндпоинтам | 401 | `HTTPBearer` + `get_current_user` |
| Сотрудник вызывает `POST /tasks` | 403 | `require_teamlead` |
| Невалидное тело (срок < 1 ч) | 422 | Pydantic `Field(ge=60, le=20160)` |
| Чужой `task_id` у сотрудника | 403 | `get_task_for_assignee` |
| Пустой комментарий при complete | 422 | `TaskCompleteRequest.comment` min_length=1 |
| Повторное завершение задачи | 400 | проверка `task.completion` |

## Ручные негативные тесты

```bash
# Логин сотрудника
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"anna@example.com","password":"password123"}' | jq -r .access_token)

# Сотрудник не может создать задачу → 403
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"x","assignee_id":"00000000-0000-0000-0000-000000000001","duration_minutes":120}'

# Истёкший/битый токен → 401
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/users/me \
  -H "Authorization: Bearer invalid.token.here"
```

## Типичные находки schemathesis и исправления

1. **422 на случайных UUID** — корректно: ресурс не найден или нет доступа обрабатывается до 404/403.
2. **Дублирование enum в теле** — отклоняется Pydantic.
3. **Очень длинные строки** — ограничены `max_length` в схемах.

## Вывод

API устойчив к некорректным входным данным за счёт валидации Pydantic и разграничения доступа через JWT и role-based `Depends`. Рекомендуется периодически повторять прогон после изменений контракта.
