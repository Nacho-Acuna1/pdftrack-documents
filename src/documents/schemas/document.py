from datetime import datetime, timezone

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    filename: str
    checksum: str
    content: str
    page_count: int
    size_bytes: int
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class DocumentResponse(BaseModel):
    id: str
    filename: str
    checksum: str
    content: str
    page_count: int
    size_bytes: int
    created_at: datetime


class DocumentUpdate(BaseModel):
    filename: str
