import hashlib

import pymupdf

from documents.repositories.interface import IDocumentRepository
from documents.schemas.document import DocumentCreate, DocumentResponse


class ConflictError(Exception):
    """Raised when a document with the same checksum already exists."""


class NotFoundError(Exception):
    """Raised when a document is not found."""


class InvalidPDFError(Exception):
    """Raised when the uploaded file is not a valid PDF or violates constraints."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DocumentService:
    def __init__(self, repository: IDocumentRepository) -> None:
        self._repository = repository

    @staticmethod
    def calculate_checksum(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def extract_text(data: bytes) -> tuple[str, int]:
        try:
            doc = pymupdf.open(stream=data, filetype="pdf")
        except Exception as exc:
            raise InvalidPDFError(
                "El archivo no es un PDF válido", status_code=415
            ) from exc

        page_count = len(doc)
        if page_count == 0:
            doc.close()
            raise InvalidPDFError("El PDF está vacío", status_code=400)

        text_parts: list[str] = []
        for i, page in enumerate(doc):
            page_text = page.get_text()
            text_parts.append(f"## Página {i + 1}\n{page_text}")

        doc.close()
        content = "\n\n".join(text_parts)
        return content, page_count

    async def create_document(
        self,
        filename: str,
        file_data: bytes,
        max_size_bytes: int,
    ) -> DocumentResponse:
        if len(file_data) == 0:
            raise InvalidPDFError("El archivo está vacío", status_code=400)

        if not file_data[:4] == b"%PDF":
            raise InvalidPDFError(
                "El archivo no es un PDF válido", status_code=415
            )

        if len(file_data) > max_size_bytes:
            raise InvalidPDFError(
                "El archivo excede el tamaño máximo permitido", status_code=413
            )

        checksum = self.calculate_checksum(file_data)

        content, page_count = self.extract_text(file_data)

        existing = await self._repository.find_by_checksum(checksum)
        if existing:
            raise ConflictError("Ya existe un documento con el mismo contenido")

        document = DocumentCreate(
            filename=filename,
            checksum=checksum,
            content=content,
            page_count=page_count,
            size_bytes=len(file_data),
        )

        return await self._repository.save(document)

    async def get_document(self, document_id: str) -> DocumentResponse:
        document = await self._repository.find_by_id(document_id)
        if not document:
            raise NotFoundError(f"Documento {document_id} no encontrado")
        return document

    async def list_documents(
        self, skip: int, limit: int
    ) -> list[DocumentResponse]:
        return await self._repository.find_all(skip=skip, limit=limit)

    async def update_document(
        self, document_id: str, filename: str
    ) -> DocumentResponse:
        document = await self._repository.update(document_id, filename)
        if not document:
            raise NotFoundError(f"Documento {document_id} no encontrado")
        return document

    async def delete_document(self, document_id: str) -> None:
        deleted = await self._repository.delete(document_id)
        if not deleted:
            raise NotFoundError(f"Documento {document_id} no encontrado")
