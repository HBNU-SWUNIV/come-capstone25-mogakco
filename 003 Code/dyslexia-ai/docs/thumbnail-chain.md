# Textbook Thumbnail Chain: Design, APIs, and Spring Integration

## Overview
- When a textbook is uploaded, a background job generates a thumbnail image.
- By default, FastAPI extracts key cues (characters, narrative, background) via the transformation chain, builds a Recraft prompt with a fixed children-illustration style guide, generates an illustration, uploads it to S3, publishes progress/results to Redis, then sends a callback to Spring at `POST {SPRING_SERVER_BASE_URL}/api/textbook/thumbnail/{jobId}`.
- Fallback strategy renders a static thumbnail from the first PDF page or resizes an uploaded image (configurable).
- Spring persists the association of the generated thumbnail URL to the textbook by `jobId` and exposes retrieval APIs.

## Flow
1) React → Spring: textbook upload (existing)
2) Spring → FastAPI: start thumbnail job via multipart form (`file`, `job_id`)
3) FastAPI:
   - Create job and publish progress to Redis (`progress-channel`)
   - Generate thumbnail (PDF page 1 → PNG, or image → resized PNG)
   - Upload to S3 and get an access URL (public or presigned)
   - Publish result to Redis (`result-channel`)
   - Send callback to Spring: `POST /api/textbook/thumbnail/{jobId}` with JSON body containing `thumbnail_url`
4) Spring: verify token (optional), upsert thumbnail association for textbook by `jobId`, respond 200

## Environment
- `SPRING_SERVER_BASE_URL` (required): e.g., `http://localhost:8084`
- `EXTERNAL_CALLBACK_TOKEN` (optional): adds `X-Callback-Token` header for Spring verification
- `S3_BUCKET_NAME` or `S3_IMAGE_BUCKET_NAME`, `AWS_*`, `S3_IMAGE_PREFIX`, `S3_PRESIGN_URL`, `S3_PRESIGN_EXPIRES`
- Redis channels (defaults): `progress-channel`, `result-channel`, `failure-channel`
- `THUMBNAIL_STRATEGY` (optional, default: `recraft`): `recraft` | `render`
- `RECRAFT_PROMPT_MODEL` (optional): LLM model for block extraction (default `claude-sonnet-4-20250514`)

## FastAPI: Endpoints

- `POST /api/v1/thumbnails` (multipart)
  - Form fields: `file` (required, PDF or image), `job_id` (optional)
  - Response 202 JSON: `{ "jobId": string, "status": "ACCEPTED", "message": string }`
  - Side effects: starts background job, publishes progress to Redis

- `GET /api/v1/thumbnails/{jobId}/status`
  - Response JSON (JobProgress): `{ job_id, status, current_step, progress_percentage, ... }`

- `GET /api/v1/thumbnails/{jobId}/result`
  - Response JSON (JobResult): `{ job_id, status, filename, result_data: { thumbnail_url, s3_key, width, height }, ... }`

## FastAPI → Spring: Callback

- URL: `POST {SPRING_SERVER_BASE_URL}/api/textbook/thumbnail/{jobId}`
- Headers: `X-Callback-Token` when `EXTERNAL_CALLBACK_TOKEN` is set
- Body (snake + camel cases for compatibility):
  ```json
  {
    "job_id": "abcd-1234",
    "jobId": "abcd-1234",
    "pdf_name": "textbook.pdf",
    "pdfName": "textbook.pdf",
    "thumbnail_url": "https://bucket.s3.region.amazonaws.com/resources/2025/09/22/uuid.png",
    "thumbnailUrl": "https://bucket.s3.region.amazonaws.com/resources/2025/09/22/uuid.png",
    "s3_key": "resources/2025/09/22/uuid.png",
    "width": 512,
    "height": 362,
    "timestamp": "2025-01-15T12:34:56Z"
  }
  ```

## Recraft Prompt Style (Global)
- All Recraft image prompts use a fixed children’s illustration style:
  - Dreamy, whimsical fairy-tale; colored pencil + watercolor
  - Soft pastels, gentle, non-threatening, inclusive; picture book quality
  - Hand-drawn textures, soft diffused lighting
  - Age-appropriate for 7–12; promotes positive values
  - The subject description is dynamically composed from extracted blocks (PAGE_IMAGE prompt preferred, otherwise heading/text fallback).

## Redis Pub/Sub Messages
- Progress channel (`progress-channel`): `{ "jobId": string, "progress": number, "timestamp": string }`
- Result channel (`result-channel`): `{ "jobId": string, "s3_url": string, "timestamp": string }`
- Failure channel (`failure-channel`): `{ "jobId": string, "error": string }`

## Spring: API Design (Save & Retrieve)

Assumptions:
- Spring has a `jobId → textbook` correlation (from initial document upload step).
- Spring stores the thumbnail URL and S3 key associated with the textbook/document.

Endpoints (proposal):

- `POST /api/textbook/thumbnail/{jobId}` (callback receiver)
  - Headers: optional `X-Callback-Token`
  - Body: as above
  - Behavior:
    - Validate token if configured
    - Resolve `jobId → textbook` record
    - Persist/update thumbnail association: `{ textbook_id, job_id, s3_key?, thumbnail_url }`
    - 200 OK on success

- `GET /api/v1/textbooks/{textbookId}/thumbnail`
  - Response: `{ textbookId, thumbnailUrl, s3Key?, updatedAt }`

- `PUT /api/v1/textbooks/{textbookId}/thumbnail`
  - Body: `{ thumbnailUrl, s3Key? }`
  - Behavior: manual override/update (admin or repair tool)

### Spring: Pseudo DTOs
```java
public class ThumbnailCallbackRequest {
  public String jobId;       // or job_id
  public String pdfName;     // or pdf_name
  public String thumbnailUrl; // or thumbnail_url
  public String s3Key;       // optional
  public Integer width;      // optional
  public Integer height;     // optional
  public String timestamp;   // optional
}

public class TextbookThumbnailResponse {
  public Long textbookId;
  public String thumbnailUrl;
  public String s3Key;
  public String updatedAt;
}
```

### Spring: Pseudo Controller
```java
@RestController
@RequestMapping("/api")
public class TextbookThumbnailController {
  @PostMapping("/textbook/thumbnail/{jobId}")
  public ResponseEntity<?> receiveThumbnail(
    @PathVariable String jobId,
    @RequestBody ThumbnailCallbackRequest req,
    @RequestHeader(value = "X-Callback-Token", required = false) String token) {
      // 1) optional token verify
      // 2) find textbook by jobId
      // 3) upsert thumbnailUrl + s3Key
      // 4) return 200
      return ResponseEntity.ok(Map.of("jobId", jobId, "status", "RECEIVED"));
  }

  @GetMapping("/v1/textbooks/{textbookId}/thumbnail")
  public TextbookThumbnailResponse getThumbnail(@PathVariable Long textbookId) {
     // query by textbookId and return
  }

  @PutMapping("/v1/textbooks/{textbookId}/thumbnail")
  public TextbookThumbnailResponse putThumbnail(
      @PathVariable Long textbookId,
      @RequestBody TextbookThumbnailResponse body) {
     // update override
  }
}
```

## Validation & Testing
- FastAPI run: `uvicorn main:app --reload --port 10300`
- Health: `curl http://127.0.0.1:10300/` and `curl http://127.0.0.1:10300/health/redis`
- Start thumbnail job:
  ```bash
  curl -F "file=@/path/to/textbook.pdf" -F "job_id=job-123" http://127.0.0.1:10300/api/v1/thumbnails/
  ```
- Poll status:
  ```bash
  curl http://127.0.0.1:10300/api/v1/thumbnails/job-123/status
  ```
- Result:
  ```bash
  curl http://127.0.0.1:10300/api/v1/thumbnails/job-123/result
  ```

## Notes
- PDF rendering uses `pdfplumber` (PIL under the hood). If rendering fails, a gray placeholder is generated to keep the pipeline robust.
- S3 upload respects `S3_PRESIGN_URL` for presigned access URLs or defaults to public bucket URL.
- Callback failure does not block result persistence; failures are logged and the job is marked accordingly.
