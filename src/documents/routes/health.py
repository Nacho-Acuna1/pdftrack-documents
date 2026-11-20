from fastapi import APIRouter
from fastapi.responses import JSONResponse

from documents.core.database import database

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/live")
async def liveness() -> dict:
    return {"status": "alive"}


@router.get("/ready", response_model=None)
async def readiness() -> JSONResponse | dict[str, str]:
    healthy = await database.is_healthy()
    if not healthy:
        return JSONResponse(
            status_code=503, content={"status": "unavailable"}
        )
    return {"status": "ready"}
