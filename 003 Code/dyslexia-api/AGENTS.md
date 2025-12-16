# Repository Guidelines

## Project Structure & Module Organization
- Java 17 + Spring Boot 3.
- Source: `src/main/java/com/dyslexia/dyslexia/{controller,service,repository,entity,dto,mapper,config,exception,util}`
- Resources: `src/main/resources/application.yml` (loads `.env`).
- Tests: `src/test/java/...` mirror the main packages.
- Dev tooling: `Makefile`, `run-local.sh`, `docker-compose.db.yml`, `Dockerfile`.

## Build, Test, and Development Commands
- Build (with tests): `./gradlew clean build`
- Build (skip tests): `./gradlew clean build -x test` (used by `make build`)
- Run locally: `./gradlew bootRun` or `./run-local.sh` (loads `.env` and prompts to build)
- Unit tests: `./gradlew test` (example: `./gradlew test --tests '*UserServiceTest'`)
- Databases for local dev: `docker compose -f docker-compose.db.yml up -d`
- Docker-run app: `make up` (after `make build` copies `app.jar`), stop: `make down`
- Swagger UI (local): `http://localhost:8084/api/swagger-ui.html`

## Coding Style & Naming Conventions
- Indentation: 4 spaces; keep lines readable; no wildcard imports.
- Packages: `com.dyslexia.dyslexia.*`. Class suffixes: `*Controller`, `*Service`, `*Repository`, `*Entity`, `*Dto`, `*Mapper`.
- Prefer constructor injection with Lombok `@RequiredArgsConstructor`; log via `@Slf4j`.
- Use MapStruct for DTO/entity mapping; mapper interfaces live in `mapper`.

## Testing Guidelines
- Frameworks: JUnit 5, Mockito, AssertJ.
- Test classes end with `*Test` and mirror package structure.
- Unit tests use `@ExtendWith(MockitoExtension.class)`; integration tests may use `@SpringBootTest` (start DB/Redis via `docker-compose.db.yml` if needed).

## Commit & Pull Request Guidelines
- Conventional types: `feat`, `fix`, `chore`, `refactor`, `docs`, `test` (optionally `[#{issue}]`), e.g. `feat(controller): 비동기 교안 생성 추가`.
- PRs must include: summary (what/why), linked issues, test plan/commands, env or DB notes, and API screenshots or Swagger link when endpoints change.
- Ensure `./gradlew build` passes before requesting review.

## Security & Configuration Tips
- Copy `.env.example` to `.env`; never commit secrets. Common keys: `POSTGRES_*`, `JWT_SECRET`, `OPENAI_API_KEY`, `AWS_*`, `DEEPL_SECRET`, `REPLICATE_API_KEY`, `REDIS_HOST/PORT`, `FASTAPI_URL`.
- App context path: `/api`; default port: `8084` (override via env if needed).

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

### Dev/Env Checklist
- `.env` keys across apps
  - Spring: `FASTAPI_URL`, `POSTGRES_*`, `REDIS_HOST/PORT`, `AWS_*`, `CALLBACK_TOKEN`, `JWT_SECRET`.
  - FastAPI: Redis connection, S3 credentials, callback URL/token, CORS allowed origins.
  - React: API base URL (`http://localhost:8084/api` by default), WebSocket endpoint if used.
- Local workflow
  - Start DB/Redis: `docker compose -f docker-compose.db.yml up -d`
  - Run Spring API: `./gradlew bootRun` (Swagger: `http://localhost:8084/api/swagger-ui.html`)
  - Run FastAPI app at `${FASTAPI_URL}`; ensure Redis and callback token align.

### References (in‑repo)
- FastAPI collaboration details: `docs/fastapi.md`
- Async document pipeline PRD: `docs/async_document_creation.md`
