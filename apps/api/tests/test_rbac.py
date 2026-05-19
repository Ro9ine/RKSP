"""Базовые тесты RBAC (запускать при поднятой БД и seed)."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

pytestmark = pytest.mark.asyncio


async def _login(client: AsyncClient, email: str, password: str = "password123") -> str:
    response = await client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_employee_cannot_create_task(client: AsyncClient) -> None:
    token = await _login(client, "anna@example.com")
    response = await client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Запрещено",
            "description": "",
            "assignee_id": "00000000-0000-0000-0000-000000000000",
            "duration_minutes": 120,
        },
    )
    assert response.status_code == 403


async def test_unauthorized_me(client: AsyncClient) -> None:
    response = await client.get("/users/me")
    assert response.status_code == 401
