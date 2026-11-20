import pytest
import pymupdf
from httpx import AsyncClient

from documents.config import settings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _create_test_pdf(text: str = "Integration test content") -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# ---------------------------------------------------------------------------
# POST /api/v1/documents
# ---------------------------------------------------------------------------
class TestCreateDocument:
    async def test_create_valid_pdf(self, client: AsyncClient) -> None:
        pdf_bytes = _create_test_pdf("Hello World")
        response = await client.post(
            "/api/v1/documents",
            files={"file": ("test.pdf", pdf_bytes, "application/pdf")},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "test.pdf"
        assert len(data["checksum"]) == 64
        assert "Hello World" in data["content"]
        assert data["page_count"] == 1
        assert data["size_bytes"] == len(pdf_bytes)
        assert data["id"]
        assert data["created_at"]

    async def test_duplicate_checksum_returns_409(
        self, client: AsyncClient
    ) -> None:
        pdf_bytes = _create_test_pdf("Duplicate content")
        await client.post(
            "/api/v1/documents",
            files={"file": ("first.pdf", pdf_bytes, "application/pdf")},
        )
        response = await client.post(
            "/api/v1/documents",
            files={"file": ("second.pdf", pdf_bytes, "application/pdf")},
        )
        assert response.status_code == 409

    async def test_empty_file_returns_400(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/documents",
            files={"file": ("empty.pdf", b"", "application/pdf")},
        )
        assert response.status_code == 400

    async def test_non_pdf_returns_415(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/documents",
            files={"file": ("image.png", b"PNG fake content", "image/png")},
        )
        assert response.status_code == 415

    async def test_oversized_file_returns_413(
        self, client: AsyncClient
    ) -> None:
        original = settings.MAX_PDF_SIZE_MB
        try:
            settings.MAX_PDF_SIZE_MB = 0  # 0 bytes max
            pdf_bytes = _create_test_pdf("Too large")
            response = await client.post(
                "/api/v1/documents",
                files={"file": ("big.pdf", pdf_bytes, "application/pdf")},
            )
            assert response.status_code == 413
        finally:
            settings.MAX_PDF_SIZE_MB = original


# ---------------------------------------------------------------------------
# GET /api/v1/documents
# ---------------------------------------------------------------------------
class TestListDocuments:
    async def test_list_empty(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/documents")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_after_create(self, client: AsyncClient) -> None:
        pdf_bytes = _create_test_pdf("List test")
        await client.post(
            "/api/v1/documents",
            files={"file": ("list.pdf", pdf_bytes, "application/pdf")},
        )
        response = await client.get("/api/v1/documents")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["filename"] == "list.pdf"


# ---------------------------------------------------------------------------
# GET /api/v1/documents/{document_id}
# ---------------------------------------------------------------------------
class TestGetDocument:
    async def test_get_existing(self, client: AsyncClient) -> None:
        pdf_bytes = _create_test_pdf("Get by ID")
        create_resp = await client.post(
            "/api/v1/documents",
            files={"file": ("get.pdf", pdf_bytes, "application/pdf")},
        )
        doc_id = create_resp.json()["id"]
        response = await client.get(f"/api/v1/documents/{doc_id}")
        assert response.status_code == 200
        assert response.json()["id"] == doc_id

    async def test_get_nonexistent_returns_404(
        self, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/api/v1/documents/507f1f77bcf86cd799439011"
        )
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# PUT /api/v1/documents/{document_id}
# ---------------------------------------------------------------------------
class TestUpdateDocument:
    async def test_update_filename(self, client: AsyncClient) -> None:
        pdf_bytes = _create_test_pdf("Update test")
        create_resp = await client.post(
            "/api/v1/documents",
            files={"file": ("original.pdf", pdf_bytes, "application/pdf")},
        )
        doc_id = create_resp.json()["id"]
        response = await client.put(
            f"/api/v1/documents/{doc_id}",
            json={"filename": "renamed.pdf"},
        )
        assert response.status_code == 200
        assert response.json()["filename"] == "renamed.pdf"
        assert response.json()["id"] == doc_id

    async def test_update_nonexistent_returns_404(
        self, client: AsyncClient
    ) -> None:
        response = await client.put(
            "/api/v1/documents/507f1f77bcf86cd799439011",
            json={"filename": "nope.pdf"},
        )
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/documents/{document_id}
# ---------------------------------------------------------------------------
class TestDeleteDocument:
    async def test_delete_existing(self, client: AsyncClient) -> None:
        pdf_bytes = _create_test_pdf("Delete test")
        create_resp = await client.post(
            "/api/v1/documents",
            files={"file": ("del.pdf", pdf_bytes, "application/pdf")},
        )
        doc_id = create_resp.json()["id"]
        response = await client.delete(f"/api/v1/documents/{doc_id}")
        assert response.status_code == 204

    async def test_delete_already_deleted_returns_404(
        self, client: AsyncClient
    ) -> None:
        pdf_bytes = _create_test_pdf("Delete twice")
        create_resp = await client.post(
            "/api/v1/documents",
            files={"file": ("del2.pdf", pdf_bytes, "application/pdf")},
        )
        doc_id = create_resp.json()["id"]
        await client.delete(f"/api/v1/documents/{doc_id}")
        response = await client.delete(f"/api/v1/documents/{doc_id}")
        assert response.status_code == 404
