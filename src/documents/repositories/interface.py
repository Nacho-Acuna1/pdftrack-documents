from abc import ABC, abstractmethod

from documents.schemas.document import DocumentCreate, DocumentResponse


class IDocumentRepository(ABC):
    @abstractmethod
    async def save(self, document: DocumentCreate) -> DocumentResponse: ...

    @abstractmethod
    async def find_by_checksum(self, checksum: str) -> DocumentResponse | None: ...

    @abstractmethod
    async def find_by_id(self, document_id: str) -> DocumentResponse | None: ...

    @abstractmethod
    async def find_all(self, skip: int, limit: int) -> list[DocumentResponse]: ...

    @abstractmethod
    async def update(self, document_id: str, filename: str) -> DocumentResponse | None: ...

    @abstractmethod
    async def delete(self, document_id: str) -> bool: ...
