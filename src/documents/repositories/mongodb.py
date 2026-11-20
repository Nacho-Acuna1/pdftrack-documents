from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument

from documents.repositories.interface import IDocumentRepository
from documents.schemas.document import DocumentCreate, DocumentResponse


class MongoDocumentRepository(IDocumentRepository):
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self._collection = collection

    @staticmethod
    def _to_response(doc: dict) -> DocumentResponse:
        return DocumentResponse(
            id=str(doc["_id"]),
            filename=doc["filename"],
            checksum=doc["checksum"],
            content=doc["content"],
            page_count=doc["page_count"],
            size_bytes=doc["size_bytes"],
            created_at=doc["created_at"],
        )

    async def save(self, document: DocumentCreate) -> DocumentResponse:
        doc_dict = document.model_dump()
        result = await self._collection.insert_one(doc_dict)
        doc_dict["_id"] = result.inserted_id
        return self._to_response(doc_dict)

    async def find_by_checksum(self, checksum: str) -> DocumentResponse | None:
        doc = await self._collection.find_one({"checksum": checksum})
        return self._to_response(doc) if doc else None

    async def find_by_id(self, document_id: str) -> DocumentResponse | None:
        try:
            oid = ObjectId(document_id)
        except Exception:
            return None
        doc = await self._collection.find_one({"_id": oid})
        return self._to_response(doc) if doc else None

    async def find_all(self, skip: int, limit: int) -> list[DocumentResponse]:
        cursor = self._collection.find().skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._to_response(doc) for doc in docs]

    async def update(self, document_id: str, filename: str) -> DocumentResponse | None:
        try:
            oid = ObjectId(document_id)
        except Exception:
            return None
        doc = await self._collection.find_one_and_update(
            {"_id": oid},
            {"$set": {"filename": filename}},
            return_document=ReturnDocument.AFTER,
        )
        return self._to_response(doc) if doc else None

    async def delete(self, document_id: str) -> bool:
        try:
            oid = ObjectId(document_id)
        except Exception:
            return False
        result = await self._collection.delete_one({"_id": oid})
        return result.deleted_count > 0
