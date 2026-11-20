from datetime import datetime, timezone

from documents.schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate


class TestDocumentCreate:
    def test_serialization(self) -> None:
        doc = DocumentCreate(
            filename="test.pdf",
            checksum="abc123def456",
            content="Extracted text",
            page_count=3,
            size_bytes=2048,
        )
        data = doc.model_dump()
        assert data["filename"] == "test.pdf"
        assert data["checksum"] == "abc123def456"
        assert data["page_count"] == 3
        assert data["size_bytes"] == 2048
        assert isinstance(data["created_at"], datetime)

    def test_created_at_default(self) -> None:
        doc = DocumentCreate(
            filename="a.pdf",
            checksum="x",
            content="y",
            page_count=1,
            size_bytes=100,
        )
        assert doc.created_at.tzinfo is not None


class TestDocumentResponse:
    def test_serialization(self) -> None:
        now = datetime.now(timezone.utc)
        doc = DocumentResponse(
            id="507f1f77bcf86cd799439011",
            filename="report.pdf",
            checksum="deadbeef",
            content="Hello",
            page_count=1,
            size_bytes=512,
            created_at=now,
        )
        data = doc.model_dump()
        assert data["id"] == "507f1f77bcf86cd799439011"
        assert data["filename"] == "report.pdf"
        assert data["created_at"] == now


class TestDocumentUpdate:
    def test_validation(self) -> None:
        update = DocumentUpdate(filename="renamed.pdf")
        assert update.filename == "renamed.pdf"
