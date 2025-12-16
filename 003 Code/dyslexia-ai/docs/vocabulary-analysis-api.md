# 어휘 분석 API 응답 스키마

- 목적: 문장에서 어휘 학습을 요청할 때 서버가 반환하는 응답 구조를 명세합니다.
- 반환 형태: JSON 배열 (CommonResponse 래핑 없음)
- 네이밍: camelCase
- 인증: `Authorization: Bearer <JWT>`

## 엔드포인트

- Method/Path: `POST /vocabulary-analysis/search`
- Body(JSON):
  - `textbookId` (number, required)
  - `pageNumber` (number, optional)
  - `blockId` (string, optional)
- Headers:
  - `Authorization: Bearer <JWT>`
  - `Content-Type: application/json`

## 응답 타입 구조 (TypeScript)

```ts
// 결과는 아래 VocabularyAnalysis 객체의 배열입니다.
export interface VocabularyAnalysis {
  id: number;
  textbookId: number;
  pageNumber: number;
  blockId: string;
  word: string;
  startIndex: number;            // 0-based 시작 인덱스 (문자 단위)
  endIndex: number;              // 0-based 종료 인덱스 (권장: exclusive, slice(startIndex, endIndex) 호환)
  definition: string;            // 자세한 뜻
  simplifiedDefinition: string;  // 쉬운 풀이
  examples: string;              // 예문 문자열 (쉼표 구분 or '["예문1"...]' JSON 문자열)
  difficultyLevel: 'easy' | 'medium' | 'hard' | string;
  reason: string;                // 선정/난이도 사유 설명
  gradeLevel: number;            // 권장 학년
  phonemeAnalysisJson: string;   // 아래 PhonemeAnalysis를 직렬화한 JSON 문자열
  createdAt: string;             // ISO-8601 문자열
  originalSentence: string;      // 분석에 사용된 원문 문장
}

// phonemeAnalysisJson 내부 구조 (직렬화 전 타입)
export interface PhonemeComponent {
  consonant: string;       // 예: 'ㅇ', 'ㅈ'
  pronunciation: string;   // 예: 'ieung', 'jieut'
  sound: string;           // 예: '/ŋ/', '/dʑ/'
  difficulty: 'easy' | 'medium' | 'hard';
}

export interface SyllableComponents {
  initial: PhonemeComponent;
  medial: {
    vowel: string;         // 예: 'ㅕ', 'ㅜ'
    pronunciation: string; // 예: 'yeo', 'u'
    sound: string;         // 예: '/jʌ/', '/u/'
    difficulty: 'easy' | 'medium' | 'hard';
  };
  final?: PhonemeComponent; // 받침이 없을 수 있음
}

export interface SyllableInfo {
  syllable: string;           // 예: '영', '수', '증'
  combinedSound: string;      // 예: 'yeong', 'su'
  writingTips: string;        // 쓰기/발음 팁
  components: SyllableComponents;
}

export interface WritingStep {
  step: number;               // 1부터 시작하는 단계 번호
  syllable: string;           // 대상 음절
  phoneme: string;            // 예: 'ㅇ-ㅕ-ㅇ'
  description: string;        // 단계 설명
}

export interface LearningTips {
  commonMistakes: string[];   // 자주 하는 실수
  practiceWords: string[];    // 연습할 단어
  rhymingWords: string[];     // 비슷한 발음/운율 단어
}

export interface PhonemeAnalysis {
  syllables: SyllableInfo[];
  writingOrder: WritingStep[];
  learningTips: LearningTips;
}
```

## JSON 예시 (성공 시 응답 바디)

```json
[
  {
    "id": 101,
    "textbookId": 7,
    "pageNumber": 1,
    "blockId": "b-12",
    "word": "영수증",
    "startIndex": 2,
    "endIndex": 5,
    "definition": "물품을 사거나 돈을 지불했다는 사실을 증명하는 문서.",
    "simplifiedDefinition": "물건을 샀다는 것을 알려주는 종이.",
    "examples": "[\"영수증을 꼭 챙기세요.\", \"전자영수증을 받았어요.\"]",
    "difficultyLevel": "medium",
    "reason": "학년 수준 대비 난이도 높은 어휘",
    "gradeLevel": 3,
    "phonemeAnalysisJson": "{\"syllables\":[{\"syllable\":\"영\",\"combinedSound\":\"yeong\",\"writingTips\":\"ㅇ의 시작 소리에 주의\",\"components\":{\"initial\":{\"consonant\":\"ㅇ\",\"pronunciation\":\"ieung\",\"sound\":\"/ŋ/\",\"difficulty\":\"easy\"},\"medial\":{\"vowel\":\"ㅕ\",\"pronunciation\":\"yeo\",\"sound\":\"/jʌ/\",\"difficulty\":\"medium\"},\"final\":{\"consonant\":\"ㅇ\",\"pronunciation\":\"ieung\",\"sound\":\"/ŋ/\",\"difficulty\":\"easy\"}}},{\"syllable\":\"수\",\"combinedSound\":\"su\",\"writingTips\":\"모음 ㅜ의 입모양\",\"components\":{\"initial\":{\"consonant\":\"ㅅ\",\"pronunciation\":\"siot\",\"sound\":\"/s/\",\"difficulty\":\"medium\"},\"medial\":{\"vowel\":\"ㅜ\",\"pronunciation\":\"u\",\"sound\":\"/u/\",\"difficulty\":\"easy\"}}},{\"syllable\":\"증\",\"combinedSound\":\"jeung\",\"writingTips\":\"ㅈ과 ㅡ 발음 구별\",\"components\":{\"initial\":{\"consonant\":\"ㅈ\",\"pronunciation\":\"jieut\",\"sound\":\"/dʑ/\",\"difficulty\":\"medium\"},\"medial\":{\"vowel\":\"ㅡ\",\"pronunciation\":\"eu\",\"sound\":\"/ɨ/\",\"difficulty\":\"medium\"},\"final\":{\"consonant\":\"ㅇ\",\"pronunciation\":\"ieung\",\"sound\":\"/ŋ/\",\"difficulty\":\"easy\"}}}],\"writingOrder\":[{\"step\":1,\"syllable\":\"영\",\"phoneme\":\"ㅇ-ㅕ-ㅇ\",\"description\":\"영을 순서대로 써 봐요\"},{\"step\":2,\"syllable\":\"수\",\"phoneme\":\"ㅅ-ㅜ\",\"description\":\"수의 자음과 모음을 연결해요\"},{\"step\":3,\"syllable\":\"증\",\"phoneme\":\"ㅈ-ㅡ-ㅇ\",\"description\":\"증의 받침 ㅇ을 마무리해요\"}],\"learningTips\":{\"commonMistakes\":[\"‘영수정’으로 잘못 쓰기\",\"받침 ㅇ 발음 누락\"],\"practiceWords\":[\"영수증\",\"증명서\",\"수증기\"],\"rhymingWords\":[\"증\",\"등\",\"승\"]}}",
    "originalSentence": "전자영수증을 확인했어요.",
    "createdAt": "2025-09-21T02:49:09"
  },
  {
    "id": 102,
    "textbookId": 7,
    "pageNumber": 1,
    "blockId": "b-12",
    "word": "전자",
    "startIndex": 0,
    "endIndex": 2,
    "definition": "전기를 띄는 미립자. 또는 전자 장치를 사용하는 것을 뜻함.",
    "simplifiedDefinition": "전기와 관련된 것.",
    "examples": "전자책, 전자사전",
    "difficultyLevel": "easy",
    "reason": "과학 관련 기본 어휘",
    "gradeLevel": 3,
    "phonemeAnalysisJson": "{\"syllables\":[{\"syllable\":\"전\",\"combinedSound\":\"jeon\",\"writingTips\":\"ㅈ 발음 시작 주의\",\"components\":{\"initial\":{\"consonant\":\"ㅈ\",\"pronunciation\":\"jieut\",\"sound\":\"/dʑ/\",\"difficulty\":\"medium\"},\"medial\":{\"vowel\":\"ㅓ\",\"pronunciation\":\"eo\",\"sound\":\"/ʌ/\",\"difficulty\":\"easy\"},\"final\":{\"consonant\":\"ㄴ\",\"pronunciation\":\"nieun\",\"sound\":\"/n/\",\"difficulty\":\"easy\"}}},{\"syllable\":\"자\",\"combinedSound\":\"ja\",\"writingTips\":\"자음 ㅈ과 모음 ㅏ 결합\",\"components\":{\"initial\":{\"consonant\":\"ㅈ\",\"pronunciation\":\"jieut\",\"sound\":\"/dʑ/\",\"difficulty\":\"medium\"},\"medial\":{\"vowel\":\"ㅏ\",\"pronunciation\":\"a\",\"sound\":\"/a/\",\"difficulty\":\"easy\"}}}],\"writingOrder\":[{\"step\":1,\"syllable\":\"전\",\"phoneme\":\"ㅈ-ㅓ-ㄴ\",\"description\":\"전의 획순을 익혀요\"},{\"step\":2,\"syllable\":\"자\",\"phoneme\":\"ㅈ-ㅏ\",\"description\":\"자를 깔끔하게 마무리해요\"}],\"learningTips\":{\"commonMistakes\":[\"전자 → 정자로 혼동\"],\"practiceWords\":[\"전자\",\"전자제품\",\"전자책\"],\"rhymingWords\":[\"정자\",\"전차\"]}}",
    "originalSentence": "전자영수증을 확인했어요.",
    "createdAt": "2025-09-21T02:49:09"
  }
]
```

## 메모

- 빈 결과: 해당 문장에 분석된 어휘가 없으면 빈 배열(`[]`)을 반환하세요.
- `phonemeAnalysisJson`: 문자열로 직렬화된 JSON이어야 하며, 상단 PhonemeAnalysis 구조를 충족해야 합니다.
- `examples`: 문자열형 필드입니다. 쉼표 구분 텍스트 또는 JSON 문자열(`["문장1","문장2"]`) 모두 허용됩니다.
- 인덱스 기준: `startIndex`는 포함, `endIndex`는 미포함(exclusive) 기준을 권장합니다.

---

# PDF → 문장(블록) 단위 어휘 분석: 시스템 설계

본 섹션은 PDF로부터 생성된 각 문장(고유 `block_id`) 단위로 어휘 분석을 수행하는 전체 시스템 설계를 정의합니다. 다중 앱 협업(React ↔ Spring ↔ FastAPI)과 기존 비동기 파이프라인(Redis Pub/Sub, S3)을 준수합니다.

## 목표와 범위

- 목표: PDF에서 추출된 텍스트를 문장(=블록) 단위로 나누고, 각 블록에 대해 어휘 분석 결과를 생성/저장/스트리밍합니다.
- 범위: FastAPI 파이프라인(전처리→블록화→어휘 분석→옵션: 음운 분석→저장/스트리밍), API 계약, 메시지 스키마, 저장 구조, 상태/에러 처리.
- 식별자: 전 구간에서 `jobId`를 상관키로 사용, 문장 단위 식별은 `block_id`로 통일.

## 파이프라인 개요

1) 텍스트 추출(Preprocess)
   - PDF 업로드 → 텍스트 추출 → 의미 단위 청킹(토큰 한도 고려)
2) 블록 변환(Transform)
   - 각 청크를 LLM으로 블록 구조화(TEXT/PAGE_IMAGE 등)하고, 각 블록에 고유 `block_id` 부여
   - 필요 시 LLM 1차 결과에 `vocabularyAnalysis` 포함(빈 경우 허용)
3) 어휘 분석(Vocabulary Pass)
   - TEXT 블록 대상으로 단어 후보 추출(토큰화/품사/빈도/CEFR/사전 매핑)
   - LLM/사전/규칙 기반 하이브리드로 `VocabularyItem[]` 산출 및 보강
4) (옵션) 음운 분석(Phoneme Pass)
   - 선택된 단어만 추가 음운 분석 수행(동시성/요금 제한 반영)
5) 저장 및 스트리밍
   - Per-block 중간 결과와 진행률을 Redis Pub/Sub으로 발행
   - 최종 결과는 S3에 `jobs/{jobId}/vocabulary/...`로 저장, Spring에 완료 콜백(옵션)

## 데이터 단위와 식별자 규칙

- `jobId`: 요청 단위 상관키. 재시도/중복 방지에 사용(멱등성)
- `textbook_id`: Spring의 교재/문서 ID. FastAPI는 비영속, 결과는 S3/콜백으로 전달
- `block_id`: 문장 단위 고유 키. 문서 내 유일(예: `p{page}-b{index}`)
- `page_number`: 1-based 페이지 번호(가능하면 좌표/라인 정보도 메타데이터로 유지)

## API 설계 (FastAPI ↔ Spring)

FastAPI는 snake_case JSON을 사용하고, Spring은 SNAKE_CASE 매핑을 통해 React와 camelCase로 상호 변환합니다.

- 시작(파일 업로드)
  - POST `/api/v1/async/vocabulary/analyze`
  - multipart: `file`, `job_id` (string, required)
  - 응답 202
    ```json
    { "job_id": "abc-123", "status": "ACCEPTED", "message": "queued" }
    ```

- 시작(문장 목록 직접 전달)
  - POST `/api/v1/async/vocabulary/start`
  - body(JSON):
    ```json
    {
      "job_id": "abc-123",
      "textbook_id": 7,
      "items": [
        { "page_number": 1, "block_id": "b-1", "text": "첫 번째 문장." },
        { "page_number": 1, "block_id": "b-2", "text": "두 번째 문장." }
      ]
    }
    ```
  - 응답 202: 위와 동일

- 상태 조회
  - GET `/api/v1/async/vocabulary/status/{job_id}`
  - 응답 예시
    ```json
    {
      "job_id": "abc-123",
      "status": "PROCESSING",
      "progress": 62,
      "total_blocks": 40,
      "completed_blocks": 25,
      "failed_blocks": 0,
      "created_at": "2025-01-15T12:34:56Z",
      "updated_at": "2025-01-15T12:35:51Z"
    }
    ```

- 결과 조회(집계)
  - GET `/api/v1/async/vocabulary/result/{job_id}`
  - 응답: job 단위 집계 JSON(S3에 저장된 summary를 그대로 전달)

- 블록 단건 결과 조회(선택)
  - GET `/api/v1/async/vocabulary/blocks/{job_id}/{block_id}`

- 취소(선택)
  - DELETE `/api/v1/async/vocabulary/cancel/{job_id}`

## Redis Pub/Sub 메시지 스키마

- 채널명: 기존 가이드 준수(기본값)
  - `progress-channel`, `result-channel`, `failure-channel`

- 진행률(progress)
  ```json
  {
    "jobId": "abc-123",
    "blockId": "b-12",
    "status": "PROCESSING",  // WAITING|PROCESSING|COMPLETED|FAILED
    "progress": 52,           // job 전역 또는 per-block 진행률
    "message": "b-12 vocab analyzing",
    "timestamp": "2025-01-15T12:35:10Z"
  }
  ```

- 블록 결과(result)
  ```json
  {
    "jobId": "abc-123",
    "blockId": "b-12",
    "pageNumber": 1,
    "vocabularyItems": [
      {
        "word": "영수증",
        "startIndex": 2,
        "endIndex": 5,
        "definition": "...",
        "simplifiedDefinition": "...",
        "examples": ["..."],
        "difficultyLevel": "medium",
        "reason": "학년 대비 난이도"
      }
    ],
    "timestamp": "2025-01-15T12:35:12Z"
  }
  ```

- 실패(failure)
  ```json
  {
    "jobId": "abc-123",
    "blockId": "b-12",
    "error": "LLM_TIMEOUT",
    "errorMessage": "Anthropic request timeout"
  }
  ```

## S3 저장 구조(권장)

- `jobs/{jobId}/vocabulary/blocks/{block_id}.json`  // per-block 결과
- `jobs/{jobId}/vocabulary/summary.json`            // 전체 집계(페이지/난이도/빈도 통계 포함)

summary 예시(요약):
```json
{
  "job_id": "abc-123",
  "textbook_id": 7,
  "totals": { "blocks": 40, "items": 128 },
  "by_page": [ { "page_number": 1, "blocks": 12, "items": 43 } ],
  "by_difficulty": { "easy": 51, "medium": 61, "hard": 16 },
  "generated_at": "2025-01-15T12:40:00Z"
}
```

## 처리 전략과 동시성 설계

- 블록 큐잉: 각 TEXT 블록을 작업 단위로 생성(`vocab:{jobId}:{blockId}`)
- 동시성 제한: `VOCAB_MAX_CONCURRENT`(예: 5)로 Async 실행 제한, LLM 호출은 레이트리미터(`VOCAB_RATE_LIMIT_PER_MIN`)
- 하이브리드 분석: 사전/빈도/품사 기반 규칙으로 후보군 추출 → LLM으로 정의/쉬운풀이/예문 보강(빈 결과 보완)
- 실패 재시도: 지수 백오프(최대 N회), 영구 실패 시 `failure-channel` 발행 후 집계에 반영
- 부분 결과 스트리밍: 블록 단위 `result-channel` 발행 → UI는 실시간 하이라이트/툴팁 업데이트 가능

## 모델 스키마(요약, snake_case)

VocabularyItem
```json
{
  "word": "string",
  "start_index": 0,
  "end_index": 3,
  "definition": "string",
  "simplified_definition": "string",
  "examples": ["string"],
  "difficulty_level": "easy|medium|hard",
  "reason": "string",
  "grade_level": 3,
  "phoneme_analysis": { "...": "..." } // 선택
}
```

BlockVocabularyResult
```json
  {
    "job_id": "abc-123",
    "textbook_id": 7,
    "page_number": 1,
    "block_id": "b-12",
    "original_sentence": "전자영수증을 확인했어요.",
    "vocabulary_items": [ { "word": "영수증", "start_index": 2, "end_index": 5, "definition": "..." } ],
    "created_at": "2025-01-15T12:35:12Z"
  }
```

## 에러/멱등성/보안

- 멱등성: 동일 `job_id` 재요청 시 기존 진행 상태/결과 반환(중복 실행 방지)
- 에러 응답: `error_code`, `message`, `job_id` 포함. 내부 스택트레이스는 숨김
- 콜백 보호: `X-Callback-Token` 헤더(옵션)로 Spring 콜백 검증

## 샘플 cURL

- 파일 업로드 시작
```bash
curl -X POST "http://localhost:10300/api/v1/async/vocabulary/analyze" \
  -H "Authorization: Bearer <JWT>" \
  -F "file=@/path/to/file.pdf" \
  -F "job_id=abc-123"
```

- 문장 배열 직접 분석 시작
```bash
curl -X POST "http://localhost:10300/api/v1/async/vocabulary/start" \
  -H "Authorization: Bearer <JWT>" -H "Content-Type: application/json" \
  -d '{
    "job_id": "abc-123",
    "document_id": 7,
    "items": [
      { "page_number": 1, "block_id": "b-1", "text": "첫 번째 문장." },
      { "page_number": 1, "block_id": "b-2", "text": "두 번째 문장." }
    ]
  }'
```

- 상태/결과 조회
```bash
curl "http://localhost:10300/api/v1/async/vocabulary/status/abc-123"
curl "http://localhost:10300/api/v1/async/vocabulary/result/abc-123"
curl "http://localhost:10300/api/v1/async/vocabulary/blocks/abc-123/b-12"
```

## 구현 팁(현재 코드와의 연결)

- 라우터: `src/api/`에 `vocabulary_router.py` 추가(프리픽스 `/api/v1/async/vocabulary`)
- 서비스: `src/services/vocabulary_analysis_service.py`(후보 추출/사전 매핑/LLM 보강), 기존 `phoneme_analysis_service.py`와 결합 가능
- 오케스트레이션: 기존 `async_job_processor.py`/`orchestration_service.py` 패턴 재사용, per-block 태스크/동시성/재시도 포함
- Redis: 기존 `redis_pub_sub_service.py`/`redis_service.py` 활용하여 progress/result/failure 발행 및 캐싱
- 환경 변수: `VOCAB_MAX_CONCURRENT`, `VOCAB_RATE_LIMIT_PER_MIN`, `VOCAB_ENABLE_PHONEME`, `VOCAB_S3_BUCKET`

## 테스트 계획

- 단위: 토큰화/품사/빈도/사전 매핑 유닛 테스트, LLM 실패 시 폴백 검증
- API: `pytest + httpx.AsyncClient`로 시작/상태/결과/블록단 조회 케이스 작성
- 통합: Redis Pub/Sub 수신 모킹, S3 업로더 모킹, 멱등/재시도/취소 흐름 검증

---

# 스프링 콜백 & RDB 저장 설계

어휘 분석이 “완전히 완료”되면, FastAPI는 최종 요약과 S3 위치 정보를 Spring으로 전송하고, Spring은 이를 영속화(RDB 저장)합니다. 대용량을 고려해 ‘요약+S3 포인터’ 방식(권장)과 ‘인라인 전송’(소규모 문서) 2가지 패턴을 정의합니다.

## 콜백 타이밍과 흐름

1. FastAPI가 모든 블록의 어휘 분석을 완료하고 S3에 per-block JSON과 summary.json을 저장
2. FastAPI → Spring 최종 콜백(요약 + S3 URL/Prefix)
3. Spring은 트랜잭션 내에서 idempotent upsert 수행 → 성공 시 2xx 응답
4. FastAPI는 2xx 수신 시 ‘delivered’로 마킹, 5xx/timeout 시 지수 백오프 재시도

## 콜백 엔드포인트(SPRING)

- Path: `POST /api/v1/ai/vocabulary/complete`
- Headers:
  - `X-Callback-Token: <token>`
  - `Content-Type: application/json`
  - 선택: `X-Request-Id`, `X-Trace-Id`
- Body(JSON) v1(권장: 요약 + S3 포인터)
  ```json
  {
    "payload_version": 1,
    "result_type": "VOCABULARY",
    "job_id": "abc-123",
    "textbook_id": 7,
    "pdf_name": "sample.pdf",
    "s3_summary_url": "s3://bucket/jobs/abc-123/vocabulary/summary.json",
    "s3_blocks_prefix": "s3://bucket/jobs/abc-123/vocabulary/blocks/",
    "stats": {
      "blocks": 40,
      "items": 128,
      "by_difficulty": { "easy": 51, "medium": 61, "hard": 16 }
    },
    "created_at": "2025-01-15T12:40:00Z"
  }
  ```

- Body(JSON) v1-inline(소규모 문서용, 선택)
  ```json
  {
    "payload_version": 1,
    "result_type": "VOCABULARY",
    "job_id": "abc-123",
    "textbook_id": 7,
    "pdf_name": "sample.pdf",
    "summary": { "blocks": 40, "items": 128 },
    "blocks": [
      {
        "page_number": 1,
        "block_id": "b-12",
        "original_sentence": "전자영수증을 확인했어요.",
        "vocabulary_items": [
          { "word": "영수증", "start_index": 2, "end_index": 5, "definition": "..." }
        ]
      }
    ],
    "created_at": "2025-01-15T12:40:00Z"
  }
  ```

FastAPI는 기본적으로 v1(요약+포인터)로 콜백하고, 문서가 매우 작거나 운영 정책상 필요한 경우에만 v1-inline을 사용합니다.

## FastAPI 측 구현 포인트

- 서비스: `spring_callback_service.py`
  - `send_vocabulary_complete(job_id, textbook_id, pdf_name, payload)` 추가 권장
  - 성공(2xx) 시 delivered 마킹, 실패 시 지수 백오프 재시도(최대 N회, 예: 5회)
  - 반복 실패 시 Redis 리스트(`callback:dlq`)에 적재하여 운영 도구로 재전송(replay) 가능
- 환경 변수
  - `SPRING_CALLBACK_URL` (예: `http://spring:8080/api/v1/ai/vocabulary/complete`)
  - `EXTERNAL_CALLBACK_TOKEN` (헤더 전송용)
  - `SPRING_CALLBACK_TIMEOUT` (초)

## Spring 측 저장 모델(RDB)

운영 DB 스키마(제공) 기준으로 설계를 맞춥니다. 대상 테이블은 `public.vocabulary_analysis`입니다.

제공된 스키마
```sql
create table public.vocabulary_analysis (
  id bigint generated by default as identity primary key,
  block_id varchar(255),
  created_at timestamp(6),
  definition varchar(255),
  difficulty_level varchar(255),
  end_index integer,
  examples text,
  grade_level integer,
  page_number integer,
  phoneme_analysis_json text,
  reason varchar(255),
  simplified_definition varchar(255),
  start_index integer,
  textbook_id bigint,
  word varchar(255)
);
```

매핑 규칙(FastAPI → Spring → DB)
- job_id: DB 컬럼 없음. 멱등성/추적은 Spring 서비스 레벨에서 보장(아래 upsert 전략 참고)
- textbook_id: 요청/콜백에 포함 → DB `textbook_id`
- page_number: 페이지 번호 → DB `page_number`
- block_id: 문장 블록 식별자 → DB `block_id`
- word/start_index/end_index: 그대로 매핑
- definition/simplified_definition/reason: 255자 제한. 초과 시 잘라 저장하고 전문은 S3 유지 권장
- examples: 배열 → JSON 문자열 직렬화 또는 쉼표 구분 텍스트. DB는 `text` 수용
- difficulty_level/grade_level: 그대로 매핑
- phoneme_analysis_json: JSON 문자열로 직렬화하여 저장(선택)
- created_at: 서버측 now() 기본값 또는 페이로드 필드 사용

권장 제약/인덱스(멱등/성능)
```sql
-- 동일 아이템 중복 방지(멱등 업서트 키)
create unique index if not exists uq_vocab_item
  on public.vocabulary_analysis(textbook_id, block_id, word, start_index, end_index);

create index if not exists ix_vocab_textbook on public.vocabulary_analysis(textbook_id);
create index if not exists ix_vocab_block on public.vocabulary_analysis(block_id);
create index if not exists ix_vocab_page on public.vocabulary_analysis(page_number);
create index if not exists ix_vocab_word on public.vocabulary_analysis(word);
```

업서트 전략(예시: PostgreSQL)
```sql
insert into public.vocabulary_analysis (
  textbook_id, page_number, block_id,
  word, start_index, end_index,
  definition, simplified_definition, reason,
  examples, difficulty_level, grade_level,
  phoneme_analysis_json, created_at
)
values (
  :textbook_id, :page_number, :block_id,
  :word, :start_index, :end_index,
  left(:definition, 255), left(:simplified_definition, 255), left(:reason, 255),
  :examples_text, :difficulty_level, :grade_level,
  :phoneme_analysis_json, coalesce(:created_at, now())
)
on conflict (textbook_id, block_id, word, start_index, end_index)
do update set
  definition = excluded.definition,
  simplified_definition = excluded.simplified_definition,
  reason = excluded.reason,
  examples = excluded.examples,
  difficulty_level = excluded.difficulty_level,
  grade_level = excluded.grade_level,
  phoneme_analysis_json = excluded.phoneme_analysis_json,
  created_at = coalesce(public.vocabulary_analysis.created_at, excluded.created_at);
```

서비스 처리 흐름(Sring)
1) 콜백 수신 → 토큰 검증 → 요청의 `textbook_id` 확인
2) v1(포인터)인 경우 S3에서 블록 파일을 스트리밍 파싱하여 행 단위 upsert
3) v1-inline은 메모리 크기 확인 후 동일 upsert 수행
4) 예외 발생 시 트랜잭션 경계/배치 크기(예: 1000행)로 나눠 재시도

## Spring DTO/Service 설계

- DTOs (스니펫)
  - `VocabularyCompleteRequestDto`
    - `payloadVersion`, `resultType`, `jobId`, `documentId`, `pdfName`,
      `s3SummaryUrl?`, `s3BlocksPrefix?`, `summary?`, `blocks?`, `createdAt`
  - `BlockVocabularyResultDto`와 `VocabularyItemDto`는 기존 스키마를 snake_case로 매핑

- 서비스 흐름
  1) 토큰 검증(X-Callback-Token)
  2) 트랜잭션 시작
  3) `vocab_job_summary` upsert(ON CONFLICT UPDATE 또는 JPA + native)
  4) v1(포인터)인 경우 S3에서 summary/blocks를 스트리밍 파싱하며
     - `vocab_block` upsert → `vocab_item` bulk upsert
     - 대용량은 배치 단위(commit size, 예: 1000)
  5) v1-inline은 메모리 크기 점검 후 동일 처리
  6) 트랜잭션 커밋 후 2xx 응답

- 멱등 처리
  - 고유 제약조건(Unique)로 중복 삽입 차단
  - 업데이트 정책: 정의/쉬운풀이/예문 등은 최신값으로 갱신하거나 변경 불가 정책 중 택1

## 운영/신뢰성

- 재시도 정책(FastAPI): 5xx/timeout에 한해 지수 백오프, 최대 N회. 4xx는 429만 재시도
- DLQ: 재시도 실패 시 `callback:dlq`(Redis) 적재 → 운영자가 재전송
- 모니터링: FastAPI/Spring 양측에 `jobId`, `blockId`, `requestId`/`traceId` 로그 포함
- 사이즈 제한: 콜백 바디 제한(예: 5–10MB). 초과 시 반드시 S3 포인터 방식 사용

## 예시: FastAPI → Spring 콜백 요청

```bash
curl -X POST "http://spring.local/api/v1/ai/vocabulary/complete" \
  -H "X-Callback-Token: $EXTERNAL_CALLBACK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payload_version": 1,
    "result_type": "VOCABULARY",
    "job_id": "abc-123",
    "textbook_id": 7,
    "pdf_name": "sample.pdf",
    "s3_summary_url": "s3://bucket/jobs/abc-123/vocabulary/summary.json",
    "s3_blocks_prefix": "s3://bucket/jobs/abc-123/vocabulary/blocks/",
    "stats": { "blocks": 40, "items": 128 },
    "created_at": "2025-01-15T12:40:00Z"
  }'
```

## 참고

- 직렬화 규칙: FastAPI는 snake_case, Spring은 SNAKE_CASE 전략으로 자동 매핑
- 버전 관리: `payload_version` 필드로 호환성 유지
- 권장 기본: v1(요약+포인터) + 배치 upsert, 인덱스/제약조건으로 멱등 보장
