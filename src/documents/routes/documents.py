from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from documents.config import settings
from documents.core.database import database
from documents.repositories.interface import IDocumentRepository
from documents.repositories.mongodb import MongoDocumentRepository
from documents.schemas.document import DocumentResponse, DocumentUpdate
from documents.services.document import (
    ConflictError,
    DocumentService,
    InvalidPDFError,
    NotFoundError,
)


router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


def get_document_repository() -> IDocumentRepository:
    return MongoDocumentRepository(database.collection)


def get_document_service(
    repo: IDocumentRepository = Depends(get_document_repository),
) -> DocumentService:
    return DocumentService(repo)


@router.post("", status_code=201, response_model=DocumentResponse)
async def create_document(
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    file_data = await file.read()
    max_size_bytes = settings.MAX_PDF_SIZE_MB * 1024 * 1024
    try:
        return await service.create_document(
            filename=file.filename or "unknown.pdf",
            file_data=file_data,
            max_size_bytes=max_size_bytes,
        )
    except InvalidPDFError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(
        default=settings.DEFAULT_PAGE_LIMIT,
        ge=1,
        le=settings.MAX_PAGE_LIMIT,
    ),
    service: DocumentService = Depends(get_document_service),
) -> list[DocumentResponse]:
    return await service.list_documents(skip=skip, limit=limit)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    try:
        return await service.get_document(document_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    body: DocumentUpdate,
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    try:
        return await service.update_document(document_id, body.filename)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
) -> None:
    try:
        await service.delete_document(document_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
