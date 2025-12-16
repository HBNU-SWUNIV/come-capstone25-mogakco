# Textbook Quick Analysis & Thumbnail Pipeline

This document describes the end-to-end flow to analyze the first 1–2 pages of an uploaded textbook (PDF) to infer title/subject/topic and generate kid‑friendly thumbnails.

## Overview

- Trigger: PDF upload (Spring) creates a textbook and starts an async analysis job.
- Steps: Extract → Analyze (title/subject/summary/keywords) → Build prompt → Generate thumbnails → Persist → Update textbook.
- Surfaces: Extended fields on `GET /guardian/textbooks/{id}/detail` for FE; progress via Redis or callback.

## Status & Fields

- Status enum: `PENDING | PROCESSING | ANALYZING | THUMBNAIL | COMPLETED | FAILED`
- Textbook (BE → FE, snake_case additions):
  - `inferred_title?: string | null`
  - `subject?: string | null`
  - `topics?: string[]`
  - `summary?: string | null`
  - `keywords?: string[]`
  - `grade_range?: { min: number; max: number } | null`
  - `ai_confidence?: number | null`
  - `thumbnail_url?: string | null`
  - `analysis_status?: Status`

## Flow

1. Spring API
   - Accept PDF → create textbook row (status=PENDING) → upload PDF (S3) → emit job to FastAPI with `jobId` and `textbookId`.
2. FastAPI (LangChain/Graph)
   - Extract first 1–2 pages; OCR fallback if needed.
   - LLM chains: title/subject/topic, summary (1–2 sentences), keywords, grade range, confidence.
   - Build safe thumbnail prompt; generate images in 16:9, 4:3, 1:1. Select cover.
   - Upload images to S3; publish progress and final payload.
3. Spring persists
   - Update textbook columns and set `analysis_status` and `thumbnail_url`.
4. FE reads
   - Viewer/detail uses existing detail API to display thumbnail, subject/topics, summary.

## Contracts

### Start Job (Spring → FastAPI)

- `POST {FASTAPI_URL}/process/analyze`
```json
{
  "job_id": "a1b2c3",
  "textbook_id": 7,
  "s3_pdf_url": "s3://bucket/textbooks/7/source.pdf",
  "page_range": { "start": 1, "end": 2 }
}
```

### Progress (FastAPI → Redis pub)

```json
{ "jobId": "a1b2c3", "textbookId": 7, "phase": "ANALYZING", "progress": 40 }
```

### Result (FastAPI → Redis pub or HTTP callback)

```json
{
  "jobId": "a1b2c3",
  "textbookId": 7,
  "analysis": {
    "inferred_title": "전자영수증 이해하기",
    "subject": "사회",
    "topics": ["소비", "거래", "영수증"],
    "summary": "전자영수증의 의미와 활용을 간단히 소개합니다.",
    "keywords": ["전자영수증", "구매", "확인"],
    "grade_range": { "min": 3, "max": 4 },
    "confidence": 0.82,
    "sample_text": "… 첫 두 페이지에서 발췌한 본문 …"
  },
  "thumbnail": {
    "prompt": "초등학생 친화적 평면 일러스트, '영수증' 주제, 상징적 아이콘(계산서, 간단한 쇼핑백), 높은 대비, 따뜻한 색감, 단순한 형태, 텍스트 없음",
    "negative_prompt": "실사, 과도한 텍스트, 폭력적 요소",
    "style_preset": "child_friendly_flat",
    "seed": 12345,
    "images": [
      { "ratio": "16:9", "width": 1280, "height": 720, "s3_url": "https://cdn/.../16x9.png" },
      { "ratio": "4:3",  "width": 1200, "height": 900, "s3_url": "https://cdn/.../4x3.png" },
      { "ratio": "1:1",  "width": 1024, "height": 1024, "s3_url": "https://cdn/.../1x1.png" }
    ],
    "cover_selected": { "ratio": "16:9", "s3_url": "https://cdn/.../16x9.png" }
  }
}
```

### Error (FastAPI → Redis/Callback)

```json
{ "jobId": "a1b2c3", "textbookId": 7, "phase": "THUMBNAIL", "error_code": "IMAGE_GEN_TIMEOUT", "message": "Image generation timed out" }
```

## Persistence (Spring)

- textbooks table: `analysis_json`, `subject`, `summary`, `keywords` (json), `grade_min`, `grade_max`, `ai_confidence`, `thumbnail_url`, `analysis_status`.
- textbook_thumbnails table (optional): `textbook_id`, `ratio`, `s3_url`, `seed`.
- S3 layout: `textbooks/{id}/analysis.json`, `textbooks/{id}/thumbnails/{ratio}/{seed}.png`.

## FE Integration

- Existing detail API returns the new fields in snake_case. UI:
  - Title: `inferred_title || textbook_name`
  - Badges: `subject` and `topics[]`
  - Summary paragraph
  - Thumbnail image from `thumbnail_url`
  - Status badge from `analysis_status`

## Operational Notes

- Idempotency: guard by `jobId`, allow re-run with `force=true` endpoint.
- Timeouts/retries: backoff on extraction and image gen.
- Safety: filter prompts/outputs for child‑friendly content.
- Observability: log per phase with `jobId` and `textbookId`.
