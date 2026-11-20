import os
import uvicorn

from documents.config import settings


def main() -> None:
    port = int(os.getenv("PORT", settings.PORT))
    uvicorn.run(
        "documents.main:app",
        host="0.0.0.0",
        port=port,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()
