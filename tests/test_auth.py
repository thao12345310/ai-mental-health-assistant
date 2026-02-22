"""
Integration tests for the authentication endpoints.
Uses an in-memory SQLite DB via conftest fixtures.
"""
import pytest
from httpx import AsyncClient


REGISTER_PAYLOAD = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "Secure123",
    "full_name": "Test User",
}


@pytest.mark.asyncio
class TestAuthEndpoints:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == REGISTER_PAYLOAD["email"]
        assert data["username"] == REGISTER_PAYLOAD["username"]
        assert "id" in data
        assert "hashed_password" not in data  # never exposed

    async def test_register_duplicate_email(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        resp = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        assert resp.status_code == 409

    async def test_login_success(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data["tokens"]
        assert data["tokens"]["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": REGISTER_PAYLOAD["email"], "password": "Wrong999"},
        )
        assert resp.status_code == 401

    async def test_get_me_authenticated(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
        )
        token = login.json()["tokens"]["access_token"]
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["email"] == REGISTER_PAYLOAD["email"]

    async def test_get_me_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 403  # No Bearer token → HTTPBearer returns 403

    async def test_health_check(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"
