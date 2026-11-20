import pytest
from httpx import AsyncClient

from documents.core.database import database


class TestLiveness:
    async def test_liveness_always_200(self, client: AsyncClient) -> None:
        response = await client.get("/api/health/live")
        assert response.status_code == 200
        assert response.json() == {"status": "alive"}


class TestReadiness:
    async def test_ready_with_db(self, client: AsyncClient) -> None:
        response = await client.get("/api/health/ready")
        assert response.status_code == 200
        assert response.json() == {"status": "ready"}

    async def test_unavailable_without_db(self, client: AsyncClient) -> None:
        original_client = database.client
        try:
            database.client = None
            response = await client.get("/api/health/ready")
            assert response.status_code == 503
            assert response.json() == {"status": "unavailable"}
        finally:
            database.client = original_client


class TestOpenAPI:
    async def test_openapi_schema(self, client: AsyncClient) -> None:
        response = await client.get("/api/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["openapi"].startswith("3.")
        assert data["info"]["title"] == "PDFtrack Documents"
