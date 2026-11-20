# PDFtrack Documents

Microservicio independiente de gestión documental con persistencia en MongoDB.  
Parte del ecosistema **PDFtrack** — responsable exclusivo de la persistencia y gestión de documentos PDF procesados.

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Runtime | Python 3.12 |
| Framework | FastAPI + Uvicorn (ASGI) |
| Base de datos | MongoDB (async via motor ≥ 3.7.1) |
| Validación | Pydantic v2 |
| Configuración | pydantic-settings (env vars) |
| Extracción PDF | PyMuPDF (en memoria) |
| Package manager | uv |
| Tests | pytest + httpx + pytest-asyncio + mongomock-motor |

## Inicio rápido

### 1. Instalar dependencias

```bash
uv sync
```

### 2. Configuración

Copiar `.env.example` a `.env` y ajustar según el entorno:

```bash
cp .env.example .env
```

Variables disponibles:

| Variable | Default | Descripción |
|---|---|---|
| `PORT` | `8001` | Puerto HTTP |
| `MONGODB_URL` | `mongodb://mongodb:27017` | URI de conexión a MongoDB |
| `MONGODB_DB_NAME` | `pdftrack` | Nombre de la base de datos |
| `MONGODB_COLLECTION_NAME` | `documents` | Nombre de la colección |
| `MAX_PDF_SIZE_MB` | `50` | Tamaño máximo de PDF en MB |
| `DEFAULT_PAGE_LIMIT` | `20` | Paginación por defecto |
| `MAX_PAGE_LIMIT` | `100` | Límite máximo de paginación |
| `LOG_LEVEL` | `INFO` | Nivel de logging |

### 3. Ejecutar tests

```bash
uv run pytest -v
```

### 4. Ejecutar localmente

```bash
# Requiere MongoDB corriendo en localhost:27017
MONGODB_URL=mongodb://localhost:27017 uv run python -m documents.entrypoint
```

### 5. Docker

```bash
# Build
docker build -t pdftrack-documents:latest .

# Run (apuntando a MongoDB local)
docker run -d \
  -p 8001:8001 \
  -e MONGODB_URL=mongodb://host.docker.internal:27017 \
  -e MONGODB_DB_NAME=pdftrack \
  --name pdftrack-documents \
  pdftrack-documents:latest
```

## API

Todos los endpoints bajo `/api/v1`:

| Método | Ruta | Descripción | Status |
|---|---|---|---|
| `POST` | `/api/v1/documents` | Subir PDF (multipart) | 201 / 400 / 409 / 413 / 415 |
| `GET` | `/api/v1/documents` | Listar documentos | 200 |
| `GET` | `/api/v1/documents/{id}` | Obtener documento | 200 / 404 |
| `PUT` | `/api/v1/documents/{id}` | Renombrar documento | 200 / 404 |
| `DELETE` | `/api/v1/documents/{id}` | Eliminar documento | 204 / 404 |
| `GET` | `/api/health/live` | Liveness probe | 200 |
| `GET` | `/api/health/ready` | Readiness probe | 200 / 503 |
| `GET` | `/api/openapi.json` | Schema OpenAPI | 200 |

## Arquitectura

```
routes → services → repositories → MongoDB
                ↘ schemas (Pydantic)
```

- **Repository pattern**: el acceso a MongoDB está abstraído detrás de `IDocumentRepository` (ABC)
- **Inyección de dependencias**: FastAPI `Depends()` inyecta el servicio en cada request
- **Twelve-Factor App**: configuración por env vars, stateless, logs JSON a stdout, shutdown limpio

## Licencia

MIT
