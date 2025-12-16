# 난독 교안 변환 체인: Mermaid 순서흐름

본 문서는 난독 교안 변환 파이프라인과 각 체인(Chain) 단위의 처리 순서를 Mermaid 다이어그램으로 요약합니다.

관련 구현 주요 위치:
- 파이프라인: `src/pipelines/main_pipeline.py`
- 전처리: `src/services/preprocessing_service.py`
- 블록 변환: `src/services/transformation_service.py`, `src/core/prompts.py`
- 이미지 처리: `src/services/image_generation_service.py`
- 어휘 분석: `src/services/vocabulary_analysis_service.py`
- 결과 저장/발행/콜백: `src/services/prd_async_processor.py`, `src/services/redis_pub_sub_service.py`, `src/services/spring_callback_service.py`

## 전체 파이프라인 개요
```mermaid
flowchart LR
  A[React Spring 업로드 multipart: file + jobId] --> B[FastAPI PRD Async Router /api/v2/process/async]
  B --> C[PRDAsyncProcessor 상태 저장 PROCESSING + progress 0]
  C --> D[LCEL Main Pipeline]

  subgraph D[LCEL Pipeline]
    D1[PDF_PREPROCESSING 텍스트 추출 정규화 시맨틱 청킹] --> D2[TRANSFORMATION LLM JSON 블록 변환]
    D2 --> D3[IMAGE_PROCESSING PAGE_IMAGE 이미지 생성 S3]
    D3 --> D4[FINAL_ASSEMBLY 페이지별 블록 집계]
  end

  D4 --> E[STORAGE output/{jobId}.json 저장 + S3 업로드]
  E --> F[Redis result-channel 발행]
  F --> G[Spring 완료 콜백 POST /api/document/complete]
  G --> H[COMPLETED]

  D2 -. 병렬 스폰 .-> I[TEXT 블록 단위 어휘 분석 체인]
  I --> J[Spring 블록 콜백 /api/v1/ai/vocabulary/block]

  C -- 오류 --> X[FAILED]
  X -.-> Y[Redis failure-channel 발행]
```

## 상태/진행률 타임라인
```mermaid
stateDiagram-v2
  [*] --> PENDING
  PENDING --> PROCESSING: 작업 시작
  state PROCESSING {
    [*] --> PDF_PREPROCESSING: 10%
    PDF_PREPROCESSING --> TRANSFORMATION: 25%
    TRANSFORMATION --> IMAGE_PROCESSING: 60%
    IMAGE_PROCESSING --> FINAL_ASSEMBLY: 80%
    FINAL_ASSEMBLY --> STORAGE: 84% → 85%
    STORAGE --> COMPLETING: 95%
  }
  PROCESSING --> COMPLETED: result 발행 + Spring 콜백
  PROCESSING --> FAILED: failure 발행
  COMPLETED --> [*]
  FAILED --> [*]
```

- 진행률 발행: `publish_step_progress(job_id, step, progress)` → Redis `progress-channel`
- 최종 결과: `publish_result(job_id, s3_url)` → Redis `result-channel`
- 실패 알림: `publish_failure(job_id, error)` → Redis `failure-channel`

## 체인별 순서흐름

### 1) 전처리 체인 (PDF_PREPROCESSING)
```mermaid
sequenceDiagram
  participant PRE as Preprocess Step
  participant PDF as pdfplumber
  participant REDIS as Redis Pub/Sub

  PRE->>REDIS: publish_step_progress PDF_PREPROCESSING 10
  PRE->>PDF: open+extract_text - 모든 페이지
  PRE->>PRE: normalize_text_structure
  PRE->>PRE: split_into_paragraphs → create_semantic_chunks
  PRE-->>PRE: { text, chunks, metadata }
  PRE->>REDIS: publish_step_progress PDF_PREPROCESSING 25
```

입력/출력:
- 입력: `file_bytes`, `filename`
- 출력: `chunks: List[str]`, `metadata`

### 2) 블록 변환 체인 (TRANSFORMATION)
```mermaid
sequenceDiagram
  participant TR as Transform Step
  participant LLM as ChatAnthropic
  participant REDIS as Redis Pub/Sub
  participant VA as 어휘 분석 체인 스폰

  TR->>REDIS: publish_step_progress TRANSFORMATION 30
  loop for each chunk
    TR->>LLM: create_block_conversion_prompt + ainvoke with content
    LLM-->>TR: JSON blocks TEXT HEADING PAGE_IMAGE 등
    TR->>TR: clean_json_response → 누적
    opt TEXT 블록 존재
      TR->>VA: analyze_block_and_callback as task - 비동기
    end
  end
  TR->>REDIS: publish_step_progress TRANSFORMATION 60
```

특징:
- LangChain LCEL: `prompt | model`
- TEXT 블록마다 어휘 분석 체인 비동기 스폰(부하 분산)

### 3) 이미지 처리 체인 (IMAGE_PROCESSING)
```mermaid
sequenceDiagram
  participant IMG as Image Processing Step
  participant REP as Replicate API nano-banana
  participant S3 as S3
  participant REDIS as Redis Pub/Sub

  IMG->>REDIS: publish_step_progress IMAGE_PROCESSING 65
  loop for each PAGE_IMAGE block
    IMG->>REP: POST /predictions - prompt with children style
    REP-->>IMG: output url 또는 bytes
    IMG->>S3: upload_local_image_to_s3
    S3-->>IMG: s3_url
    IMG->>IMG: block.url = s3_url
    IMG->>REDIS: progress 65 에서 80
  end
  IMG->>REDIS: publish_step_progress IMAGE_PROCESSING 80
```

토글:
- `ENABLE_IMAGE_GENERATION=true|false`

### 4) 어휘 분석 체인 (TEXT 블록 단위)
```mermaid
sequenceDiagram
  participant VA as Vocabulary Analysis Chain
  participant LLM as Chat Model
  participant PH as Phoneme Service
  participant SPR as Spring 블록 콜백

  VA->>LLM: create_vocabulary_analysis_prompt + ainvoke with sentence
  LLM-->>VA: JSON 배열 items
  opt enable_phoneme
    VA->>PH: analyze_words_phoneme - words
    PH-->>VA: phoneme_analyses 와 JSON 문자열화
  end
  VA->>SPR: POST /api/v1/ai/vocabulary/block - X-Callback-Token 사용 가능
  VA-->>VA: return - 상위 체인 비차단
```

확장 포인트:
- 모델 제공자 자동 선택(OpenAI/Anthropic) 및 토큰 추정
- 실패 시 최소 1개 항목 휴리스틱 생성

### 5) 최종 조립/저장/발행/콜백 (FINAL_ASSEMBLY + STORAGE)
```mermaid
sequenceDiagram
  participant ASM as Final Assembly
  participant PRD as PRDAsyncProcessor
  participant S3 as S3
  participant REDIS as Redis Pub/Sub
  participant SPR as Spring Callback

  ASM-->>PRD: final_json { pages, blocks, metadata }
  PRD->>REDIS: publish_step_progress STORAGE 85
  PRD->>PRD: output/{jobId}.json 로컬 저장
  PRD->>S3: upload_result_to_s3 - job_id 및 final_json
  S3-->>PRD: s3_url
  PRD->>REDIS: publish_step_progress STORAGE 95
  PRD->>REDIS: publish_result job_id 와 s3_url
  PRD->>SPR: POST /api/document/complete - body: jobId pdfName data
```

## Redis 채널 규격
- `progress-channel`: `{ "jobId": string, "progress": number, "step"?: string, "timestamp": string }`
- `result-channel`: `{ "jobId": string, "s3_url": string, "timestamp": string }`
- `failure-channel`: `{ "jobId": string, "error": string }`

## 추가 전체 흐름
```mermaid
sequenceDiagram
  autonumber
  participant FE as React App
  participant SPR as Spring API
  participant AI as FastAPI Service
  participant R as Redis
  participant S3 as S3
  participant IMG as Replicate

  FE->>SPR: POST api v1 documents file
  SPR-->>FE: 202 accepted with jobId
  SPR->>AI: POST api v2 process async multipart file job_id
  AI-->>R: publish progress to progress channel
  AI->>AI: preprocess transform image process assemble
  AI->>IMG: generate image
  IMG-->>AI: image data
  AI->>S3: upload images and final json
  S3-->>AI: s3 urls
  AI-->>R: publish result to result channel
  AI->>SPR: POST api document complete callback
  loop client poll until done
    FE->>SPR: GET api v1 documents jobId status
    SPR-->>FE: status percent
  end
  FE->>SPR: GET api v1 documents jobId result
  SPR-->>FE: result with s3 url
```

## 참고 메모
- 파이프라인 기본 모델: `claude-sonnet-4-20250514`
- 이미지 스타일: 동화풍(Children’s illustration) 고정 가이드 적용
- S3/Replicate/Redis/Spring 설정은 `.env`와 `src/utils/env_config.py` 참조
