# ---------------------------------------------------------------------------
# Stage 1 – Builder
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies in /app/.venv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src/ src/
RUN uv sync --frozen --no-dev

# ---------------------------------------------------------------------------
# Stage 2 – Runtime
# ---------------------------------------------------------------------------
FROM python:3.12-slim

RUN groupadd -g 10001 app && \
    useradd -u 10001 -g app -s /bin/false -M app

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src/ src/
COPY entrypoint.py entrypoint.py

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src:$PYTHONPATH" \
    PYTHONUNBUFFERED=1

USER app

CMD ["python", "entrypoint.py"]
