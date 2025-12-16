# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 개발 명령어

### 빌드 및 개발
```bash
npm run dev          # 개발 서버 실행 (Vite)
npm run build        # 프로덕션 빌드
npm run preview      # 빌드 결과 미리보기
```

### 코드 품질 관리
```bash
npm run lint         # Biome lint 실행 및 자동 수정
npm run format       # Biome 포맷팅 실행 및 자동 수정
npm run check        # Biome 전체 검사 및 자동 수정
npm run reporter     # Biome 요약 보고서
```

### 라우팅
```bash
npm run generate-route-tree  # TanStack Router 라우트 트리 생성
```

## 아키텍처 구조

이 프로젝트는 **Feature-Sliced Design (FSD)**을 기반으로 하는 React + TypeScript + Vite 애플리케이션입니다.

### 핵심 기술 스택
- **라우팅**: TanStack Router (file-based routing)
- **상태 관리**: TanStack Query + Zustand
- **UI**: Tailwind CSS + Radix UI + shadcn/ui
- **폼**: React Hook Form + Zod
- **HTTP**: Axios (인터셉터로 토큰 관리)
- **린팅**: Biome

### 디렉토리 구조
```
src/
├── features/          # 기능별 모듈 (auth, viewer, vocabulary-analysis, layouts)
│   └── [feature]/
│       ├── api/       # API 호출 함수
│       ├── components/# 기능 전용 컴포넌트
│       ├── lib/       # 기능 전용 유틸리티
│       ├── model/     # 상태 관리 (Zustand 스토어)
│       └── ui/        # UI 컴포넌트
├── shared/            # 공통 리소스
│   ├── api/          # 공통 API 설정 (axios)
│   ├── hooks/        # 공통 커스텀 훅
│   ├── lib/          # 공통 라이브러리
│   ├── ui/           # 재사용 가능한 UI 컴포넌트
│   └── utils/        # 공통 유틸리티
├── routes/           # TanStack Router 라우트 정의
├── page/            # 랜딩 페이지 등 특수 페이지
└── components/      # 레거시 컴포넌트 (점진적으로 features로 이동)
```

### Path Aliases
```typescript
'@'         : src/
'@ui'       : src/shared/ui
'@hooks'    : src/shared/hooks
'@lib'      : src/shared/lib
'@features' : src/features
'@page'     : src/page
```

### API 구조
- **Base Client**: `src/shared/api/axios.ts`
- **토큰 관리**: localStorage 기반 자동 토큰 관리 및 갱신
- **인터셉터**: 요청/응답 인터셉터로 토큰 자동 첨부 및 만료 처리

### 라우팅 시스템
- **File-based routing**: `src/routes/` 폴더 구조가 URL 구조와 매핑
- **자동 코드 스플리팅**: 비활성화 (autoCodeSplitting: false)
- **Route Tree**: 자동 생성된 `route-tree.gen.ts` (수정 금지)

## 코딩 규칙

### 파일 명명
- 파일명: kebab-case (예: `auth-modal.tsx`)
- 컴포넌트명: PascalCase (예: `AuthModal`)

### 컴포넌트 구조
```typescript
import { type FC } from 'react'
import { cn } from '@/lib/utils'

interface ComponentProps {
  className?: string
  children?: React.ReactNode
}

export const Component: FC<ComponentProps> = ({ className, children }) => {
  return (
    <div className={cn('default-styles', className)}>
      {children}
    </div>
  )
}
```

### TanStack Query 사용법
```typescript
// 쿼리 키 정의
const queryKeys = {
  courses: {
    all: ['courses'] as const,
    byTeacher: (teacherId: number) => [...queryKeys.courses.all, teacherId] as const,
  },
} as const

// 쿼리 훅
export const useTeacherCourses = (teacherId: number) => {
  return useQuery({
    queryKey: queryKeys.courses.byTeacher(teacherId),
    queryFn: () => fetchTeacherCourses(teacherId),
  })
}
```

### 접근성 요구사항
- 난독증 친화적 UI 설계가 핵심 요구사항
- 모든 상호작용 요소에 적절한 ARIA 레이블 제공
- 키보드 네비게이션 지원 필수
- WCAG 2.1 색상 대비 기준 준수
- 스크린 리더 호환성 보장

### Biome 설정
- 들여쓰기: 탭 사용 (indentStyle: "tab")
- 인용부호: JavaScript에서 single quotes, JSX에서 double quotes
- 라인 폭: 80자
- 세미콜론: 필수

## 프로젝트 특징

이 프로젝트는 **난독증 초등학생을 위한 교육 자료 뷰어 플랫폼**입니다.

### 주요 기능 영역
1. **사용자 관리**: 교사/학생 계정 시스템
2. **문서 관리**: PDF 업로드 및 변환 시스템
3. **콘텐츠 뷰어**: 난독증 친화적 텍스트 렌더링
4. **학습 도구**: TTS, 어휘 분석, 필기 연습
5. **대시보드**: 교사용 학생 모니터링

### 중요 고려사항
- 접근성이 최우선 요구사항
- 반응형 디자인 필수 (모바일 친화적)
- 성능 최적화 (대용량 교육 자료 처리)
- 직관적인 UI/UX (초등학생 대상)

## UI Draft 컴포넌트 분석

`ui-draft/` 디렉토리는 Lovable을 통해 작성된 전체 UI 컴포넌트 모음으로, Atomic Design 설계 원칙에 따라 구성되어 있습니다.

### 🏗️ 전체 아키텍처

#### 라우팅 구조 (App.tsx)
```
/                     → Index (랜딩 페이지)
/login                → Login
/signup/*             → 회원가입 플로우
/guardian/*           → 보호자 섹션
/student/*            → 학생 섹션
```

### 📱 페이지별 의미론적 분석

#### 🎯 랜딩 페이지 (Index.tsx)
**핵심 의미**: 제품 소개와 체험 유도
- **Hero Section**: 브랜드 정체성 및 핵심 가치 제안
- **Interactive Demo**: DocumentViewer 컴포넌트 직접 체험
- **Feature Showcase**: 3단계 핵심 기능 설명
- **Social Proof**: 언론 보도 및 통계 데이터

#### 🔐 인증 시스템
**Login.tsx**: 간소화된 카카오 단일 로그인
**Signup Flow**: 역할 선택 → 세부 정보 입력

#### 👩‍👧‍👦 보호자 (Guardian) 섹션
**의미론적 역할**: 관리자이자 학습 지원자

1. **Dashboard**: 학생 현황 모니터링 허브
   - 실시간 학습 활동 피드
   - 학생별 진도 현황
   - 칭찬하기 기능 (감정적 연결)

2. **Documents**: 교안 관리 시스템
   - AI 변환 상태 추적
   - 배정 및 미리보기 기능

3. **Students**: 학생 분석 및 관리
   - 개별 학습 분석
   - 필기 연습 결과 확인

4. **Store**: 큐레이션된 교육 자료 마켓플레이스

#### 🧒 학생 (Student) 섹션
**의미론적 역할**: 학습자이자 경험의 주체

1. **Dashboard**: 개인화된 학습 공간
   - Bento Grid 레이아웃으로 직관적 정보 구성
   - 칭찬 시스템을 통한 동기 부여
   - 성취 시각화

2. **Reader**: 핵심 읽기 경험 도구
   - 난독증 친화적 읽기 환경
   - 다양한 접근성 옵션

3. **Buddy**: AI 기반 상호작용 시스템

### 🎨 UI 컴포넌트 아키텍처

#### Atom 수준 (ui/ 폴더)
- **기본 입력**: Button, Input, Select, Slider
- **정보 표시**: Badge, Card, Progress, Avatar
- **네비게이션**: Breadcrumb, Pagination, Tabs
- **피드백**: Alert, Toast, Dialog, Popover
- **레이아웃**: Separator, Resizable, Sidebar

#### Molecule 수준
- **NavigationHeader**: 역할별 내비게이션 시스템
- **DocumentViewer**: 핵심 읽기 체험 컴포넌트

#### Organism 수준
- **Modal 시스템**:
  - PraiseModal: 감정적 피드백
  - DocumentUploadModal: 업로드 워크플로우
  - StudentInviteModal: 초대 시스템

### 🎯 핵심 설계 철학

#### 1. 접근성 우선 (Accessibility-First)
- `font-dyslexic` 전용 폰트 클래스
- 충분한 색상 대비 및 여백
- TTS 지원 및 음성 피드백
- 키보드 네비게이션 최적화

#### 2. 감정적 연결 (Emotional Connection)
- 칭찬 시스템과 스티커 보상
- 따뜻한 색상 팔레트 (`warm-`, `soft-`)
- 성취감을 주는 진도 표시
- AI 친구 개념

#### 3. 점진적 복잡성 (Progressive Complexity)
- 학생용: 단순하고 직관적인 인터페이스
- 보호자용: 상세한 분석과 관리 도구
- 설정의 단계적 노출

#### 4. 반응형 설계
- 모바일 우선 접근법
- Bento Grid 레이아웃 활용
- 터치 친화적 인터액션

### 🔄 상태 관리 패턴
- **Mock Data**: 모든 컴포넌트에 현실적인 가상 데이터
- **Local State**: useState를 통한 UI 상태 관리
- **Navigation**: React Router 기반 페이지 전환

### 🎨 디자인 시스템
- **색상**: Primary(파랑), Warm(주황), Soft(연보라) 팔레트
- **타이포그래피**: 난독증 친화적 폰트 우선
- **여백**: 관대한 패딩과 충분한 줄 간격
- **모양**: 둥근 모서리 (rounded-xl, rounded-2xl)

이 UI Draft는 실제 개발 시 참고할 완전한 디자인 시스템과 사용자 경험 가이드라인을 제공합니다.

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
