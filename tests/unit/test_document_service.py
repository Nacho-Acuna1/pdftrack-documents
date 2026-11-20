import pytest
import pymupdf

from documents.repositories.interface import IDocumentRepository
from documents.schemas.document import DocumentCreate, DocumentResponse
from documents.services.document import (
    ConflictError,
    DocumentService,
    NotFoundError,
)


# ---------------------------------------------------------------------------
# In-memory repository (no external dependencies)
# ---------------------------------------------------------------------------
class InMemoryDocumentRepository(IDocumentRepository):
    def __init__(self) -> None:
        self._documents: dict[str, dict] = {}
        self._counter = 0

    async def save(self, document: DocumentCreate) -> DocumentResponse:
        self._counter += 1
        doc_id = str(self._counter)
        doc_data = document.model_dump()
        doc_data["id"] = doc_id
        self._documents[doc_id] = doc_data
        return DocumentResponse(**doc_data)

    async def find_by_checksum(self, checksum: str) -> DocumentResponse | None:
        for doc in self._documents.values():
            if doc["checksum"] == checksum:
                return DocumentResponse(**doc)
        return None

    async def find_by_id(self, document_id: str) -> DocumentResponse | None:
        doc = self._documents.get(document_id)
        return DocumentResponse(**doc) if doc else None

    async def find_all(self, skip: int, limit: int) -> list[DocumentResponse]:
        docs = list(self._documents.values())[skip : skip + limit]
        return [DocumentResponse(**d) for d in docs]

    async def update(self, document_id: str, filename: str) -> DocumentResponse | None:
        doc = self._documents.get(document_id)
        if not doc:
            return None
        doc["filename"] = filename
        return DocumentResponse(**doc)

    async def delete(self, document_id: str) -> bool:
        return self._documents.pop(document_id, None) is not None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _create_test_pdf(text: str = "Test content") -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


MAX_SIZE = 50 * 1024 * 1024  # 50 MB


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def repo() -> InMemoryDocumentRepository:
    return InMemoryDocumentRepository()


@pytest.fixture
def service(repo: InMemoryDocumentRepository) -> DocumentService:
    return DocumentService(repo)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestChecksumConsistency:
    async def test_identical_pdfs_produce_same_checksum(
        self, service: DocumentService
    ) -> None:
        pdf = _create_test_pdf("Same content for checksum")
        c1 = service.calculate_checksum(pdf)
        c2 = service.calculate_checksum(pdf)
        assert c1 == c2

    async def test_different_pdfs_produce_different_checksum(
        self, service: DocumentService
    ) -> None:
        pdf_a = _create_test_pdf("Alpha")
        pdf_b = _create_test_pdf("Beta")
        assert service.calculate_checksum(pdf_a) != service.calculate_checksum(pdf_b)


class TestCreateDocument:
    async def test_conflict_on_duplicate_checksum(
        self, service: DocumentService
    ) -> None:
        pdf = _create_test_pdf("Duplicate detection")
        await service.create_document("first.pdf", pdf, MAX_SIZE)
        with pytest.raises(ConflictError):
            await service.create_document("second.pdf", pdf, MAX_SIZE)

    async def test_extracted_text_contains_page_header(
        self, service: DocumentService
    ) -> None:
        pdf = _create_test_pdf("Extraction test")
        result = await service.create_document("test.pdf", pdf, MAX_SIZE)
        assert "## Página 1" in result.content


class TestGetDocument:
    async def test_not_found_raises_error(
        self, service: DocumentService
    ) -> None:
        with pytest.raises(NotFoundError):
            await service.get_document("nonexistent-id")


class TestDeleteDocument:
    async def test_not_found_on_delete(
        self, service: DocumentService
    ) -> None:
        with pytest.raises(NotFoundError):
            await service.delete_document("missing-id")


class TestUpdateDocument:
    async def test_not_found_on_update(
        self, service: DocumentService
    ) -> None:
        with pytest.raises(NotFoundError):
            await service.update_document("missing-id", "new_name.pdf")
