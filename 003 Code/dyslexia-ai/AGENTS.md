# Repository Guidelines

## Project Structure & Module Organization
- `main.py` — FastAPI entrypoint; configures CORS, Redis, and registers routers.
- `src/api/` — FastAPI routers (`*_router.py`), e.g., `preprocessing_router.py`, `transformation_router.py`.
- `src/services/` — Business logic and async jobs (Redis pub/sub, S3, image/phoneme processing).
- `src/utils/` — Clients and helpers (e.g., `env_config.py`, `anthropic_client.py`, `redis_client.py`).
- `src/models/` — Pydantic models and enums.
- `src/core/` — Prompt templates and core constants.
- `docs/` — Architecture/PRD notes and integration guides.
- `temp/` — Transient files; avoid committing large artifacts.

## Build, Test, and Development Commands
- Setup: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run (dev): `bash run.sh` or `uvicorn main:app --reload --host 0.0.0.0 --port 10300`
- Health checks: `curl http://127.0.0.1:10300/` and `curl http://127.0.0.1:10300/health/redis`
- Redis: set `REDIS_URL` in `.env` (see `src/utils/env_config.py` for defaults/validation).

## Coding Style & Naming Conventions
- Python 3.13, PEP 8, 4‑space indent; use type hints and module‑level `logging` (avoid `print`).
- Names: files/functions `snake_case`, classes `PascalCase`, constants `SCREAMING_SNAKE_CASE`.
- Routers: `<feature>_router.py` exporting `router`; Services: `<feature>_service.py`.
- Formatting: follow Black style (88 cols) if available; otherwise keep lines readable and consistent.

## Testing Guidelines
- Place tests under `tests/` using `test_*.py` naming.
- Prefer `pytest` and `httpx.AsyncClient` for API tests; unit‑test services in isolation.
- Example: `pip install pytest httpx` then `pytest -q`. Aim to cover critical paths (routers, services, env helpers).

## Commit & Pull Request Guidelines
- Conventional Commits: `feat:`, `fix:`, `refactor(scope):`, `chore:`, `docs:` (as seen in history).
- Example: `feat(api): add async processing v2 router` with a concise body and rationale.
- PRs include: clear description, linked issues, before/after notes, test plan or curl snippets, and relevant logs/screenshots.
- Keep diffs focused; when adding endpoints, register the router in `main.py` and update `docs/` as needed.

## Security & Configuration Tips
- Never commit secrets; use `.env` (e.g., `ANTHROPIC_API_KEY`, `REPLICATE_API_TOKEN`, `REDIS_URL`, AWS creds if needed).
- Access config via getters in `src/utils/env_config.py`; add new keys there and document them.

## Agent‑Specific Instructions
- Keep changes minimal and scoped; follow naming patterns and structure above.
- Avoid unrelated refactors; update docs/tests alongside code changes.
- After adding routers/services, verify with the health endpoints and sample `curl` calls.

## Multi‑App Collaboration (Copy‑Paste Ready)

This system is composed of three cooperating apps: React (frontend), Spring Boot (API), and LangChain FastAPI (AI). The following sections are modular and can be pasted into sibling repos to align conventions and data contracts.

### Apps & Local Paths
- React app: `/Volumes/eungu/projects/dyslexia/dyslexia-app`
- Spring API: `/Volumes/eungu/projects/dyslexia/dyslexia-api`
- LangChain (FastAPI): `/Volumes/eungu/projects/dyslexia/dyslexia-ai`

Update these paths as needed when reusing this section in other environments.

### Shared Conventions
- Identity/Auth
    - Client → Spring: `Authorization: Bearer <JWT>` (Spring extracts `clientId`, `userType`).
    - Internal calls (Spring ↔ FastAPI): secured by private network or service token. For callbacks, use `X-Callback-Token` header.
- Correlation
    - Use `jobId` as the idempotency/correlation key across services, logs, Redis, and S3 objects.
    - Include `requestId`/`traceId` headers when present; propagate to logs.
- Serialization
    - FastAPI emits `snake_case`; Spring maps via `spring.jackson.property-naming-strategy: SNAKE_CASE`.
    - Timestamps are ISO‑8601 UTC (e.g., `2025-01-15T12:34:56Z`).
- Versioning
    - Prefer explicit API version in path (e.g., `/api/v1/...`). Optionally add `X-API-Version` header for cross‑app evolution.
- Errors
    - Provide `error_code`, human message, and a stable `jobId` context. Avoid leaking stack traces to clients.

### React → Spring: Endpoints & Payloads
- Start async document processing
    - `POST /api/v1/documents` (multipart form)
    - Form fields: `file` (PDF, required)
    - Response 202 JSON (AsyncDocumentCreateResponse): `{ "jobId": string, "message": string }`
- Poll job status
    - `GET /api/v1/documents/{jobId}/status`
    - Response (DocumentProcessingStatus): `{ jobId, fileName, status: [PENDING|PROCESSING|COMPLETED|FAILED], progress?: number, errorMessage?: string, createdAt, completedAt }`
- Legacy upload (synchronous ingestion trigger)
    - `POST /api/documents/upload` (multipart form)
    - Form fields: `guardianId`, `file` (PDF), `title`
    - Response: `CommonResponse<DocumentDto>`
- Headers
    - Always send `Authorization: Bearer <JWT>`; `Content-Type: multipart/form-data` for file uploads.

### Spring ↔ FastAPI: Request/Response
- Start processing (Spring → FastAPI)
    - `POST ${FASTAPI_URL}${external.fastapi.endpoints.process}` (multipart)
    - Form fields: `file`, `job_id` (same as Spring’s `jobId`)
    - Expected response: `{ "job_id"|"jobId": string, "status": "ACCEPTED"|"QUEUED"|..., "message": string }`
- Progress & result streaming (FastAPI → Redis)
    - Channel names (configurable via `application.yml`):
        - `redis.channels.progress` (default: `progress-channel`)
        - `redis.channels.result` (default: `result-channel`)
        - `redis.channels.failure` (default: `failure-channel`)
    - Progress message JSON (mapped to `ProgressMessageDto`): `{ "jobId": string, "progress": number, "timestamp"?: string }`
    - Result message JSON (mapped to `ResultMessageDto`): `{ "jobId": string, "s3Url": string, "timestamp"?: string }`
    - Failure message JSON (mapped to `FailureMessageDto`): `{ "jobId": string, "error"|"errorMessage": string }`
- Result callback (optional, FastAPI → Spring)
    - `POST /api/document/complete`
    - Headers: `X-Callback-Token: <token>` when enabled (`external.callback.token`)
    - Body (DocumentCompleteRequestDto): `{ jobId|job_id: string, pdfName|pdf_name: string, data: object }`

### Data Ownership & Persistence
- Source of truth
    - Spring persists Documents/Textbooks/Pages and consumes AI outputs for durable storage.
    - FastAPI is stateless for processing; it publishes progress, stores large results to S3, and notifies Spring.
- Mapping rules
    - Keep FastAPI responses stable; add fields additively. Spring DTOs tolerate unknown fields (`@JsonIgnoreProperties(ignoreUnknown = true)`).

### Frontend Integration Notes
- Start job, then poll `/api/v1/documents/{jobId}/status` every 2–5s until `COMPLETED|FAILED`.
- For real‑time UX, WebSocket/SSE can mirror Redis updates; see `docs/fastapi.md` for a STOMP example.
- Display granular states: `PENDING → PROCESSING (percent) → COMPLETED | FAILED` and surface `errorMessage` when present.
