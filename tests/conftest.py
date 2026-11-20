import pytest
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from documents.core.database import database
from documents.main import app


@pytest.fixture
async def client():
    """HTTP test client backed by mongomock-motor (no real MongoDB needed)."""
    mock_client = AsyncMongoMockClient()
    mock_db = mock_client["test_pdftrack"]
    mock_collection = mock_db["documents"]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Override database references AFTER lifespan has started
        database.client = mock_client
        database.db = mock_db
        database.collection = mock_collection
        yield ac
        # Cleanup before lifespan shutdown
        await mock_collection.drop()
