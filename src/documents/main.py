from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from documents.config import settings
from documents.core.database import database
from documents.core.logging import RequestLoggingMiddleware, setup_logging
from documents.routes.documents import router as documents_router
from documents.routes.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging(settings.LOG_LEVEL)
    database.configure(
        mongodb_url=settings.MONGODB_URL,
        db_name=settings.MONGODB_DB_NAME,
        collection_name=settings.MONGODB_COLLECTION_NAME,
    )
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(
    title="PDFtrack Documents",
    description="Microservicio de gestión documental con persistencia en MongoDB",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url="/api/openapi.json",
)

app.add_middleware(RequestLoggingMiddleware)
app.include_router(documents_router)
app.include_router(health_router)
