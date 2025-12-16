# CLAUDE.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소의 코드를 작업할 때 참고하는 가이드입니다.

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

# 전체 프로젝트 구조 및 빌드 환경

## 🏗️ 프로젝트 아키텍처 개요

이 저장소는 다음 4개의 하위 프로젝트로 구성된 마이크로서비스 아키텍처입니다:

```
dyslexia/
├── dyslexia-app/          # React 프론트엔드 (메인)
├── dyslexia-api/          # Spring Boot 백엔드 (메인)
├── dyslexia-ai/           # FastAPI AI 서비스 (Python)
├── reading-buddy-playground/  # React 테스트 플레이그라운드
└── swai-competition25-team5/  # 대회용 프로젝트
    ├── app/              # React 프론트엔드
    └── api/              # Spring Boot 백엔드
```

## 🐳 Docker 환경

### 1. dyslexia-app (React 프론트엔드)
```bash
# 개발 서버 실행
docker compose up --build

# Dockerfile 구조
# 1단계: Node.js 빌드 (Vite)
# 2단계: Nginx 정적 파일 서빙
```

**Dockerfile**: Multi-stage build
- **Builder**: `node:18-alpine` - Vite 빌드
- **Runtime**: `nginx:alpine` - 정적 파일 서빙

**환경 변수**:
- `VITE_API_BASE_URL`: API 서버 URL
- `VITE_KAKAO_CLIENT_ID`: 카카오 로그인 클라이언트 ID
- `VITE_KAKAO_REDIRECT_URI`: 카카오 리디렉션 URI

**포트**: 5173 → 80 (내부)

### 2. dyslexia-api (Spring Boot 백엔드)
```bash
# 빌드 및 실행
make build && make up

# 개별 실행
./gradlew clean build -x test
docker compose up --build -d
```

**Makefile**:
```bash
make build    # Gradle 빌드
make up       # Docker 컨테이너 실행
make down     # 컨테이너 중지
make re       # 재시작 (down + up)
```

**Docker 설정**:
- **이미지**: `openjdk:17-slim`
- **포트**: 8084:8084
- **JAR**: `./app.jar` 실행

### 3. dyslexia-ai (FastAPI AI 서비스)
```bash
# 자동 실행 스크립트
./run.sh

# Docker 실행
docker compose up --build -d

# 수동 실행
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 10300
```

**Docker 설정**:
- **베이스**: Python 빌드
- **포트**: 10300:10300
- **볼륨**: Named volumes (temp, output)
- **서버**: Uvicorn ASGI

**실행 스크립트 (run.sh)**:
- 가상 환경 자동 생성 및 활성화
- 패키지 설치 (requirements.txt)
- 환경 변수 확인
- 서버 실행

## 🛠️ 빌드 환경 상세

### React 프로젝트 공통

#### 1. dyslexia-app (메인)
- **빌드**: `npm run build`
- **개발**: `npm run dev`
- **코드 품질**: Biome 사용
- **라우팅**: TanStack Router
- **상태 관리**: TanStack Query + Zustand

#### 2. reading-buddy-playground
- **프레임워크**: React + Vite
- **라우팅**: React Router
- **UI**: Radix UI + Tailwind CSS
- **빌드**: `npm run build`
- **릿트**: ESLint 사용

#### 3. swai-competition25-team5/app
- dyslexia-app와 동일한 구조
- 별도의 대회용 기능 구현

### Spring Boot 백엔드 공통

#### 1. dyslexia-api (메인)
- **빌드**: Gradle + Java 17
- **빌드 스크립트**: `./gradlew clean build -x test`
- **결과물**: `build/libs/dyslexia-0.0.1-SNAPSHOT.jar`
- **실행**: `java -jar app.jar`

#### 2. swai-competition25-team5/api
- dyslexia-api와 동일한 빌드 환경
- 별도의 대회용 API 기능

### Python AI 서비스

#### dyslexia-ai
- **의존성**: `requirements.txt`
- **웹 프레임워크**: FastAPI
- **AI 라이브러리**:
  - LangChain
  - Anthropic Claude
  - OpenAI
  - Replicate
- **문서 처리**: PDFPlumber, KoNLPy
- **실행**: Uvicorn

## 🚀 개발 워크플로우

### 1. 전체 시스템 실행
```bash
# 1. AI 서비스 실행
cd dyslexia-ai && ./run.sh

# 2. 백엔드 API 실행
cd dyslexia-api && make re

# 3. 프론트엔드 실행
cd dyslexia-app && npm run dev
```

### 2. Docker 기반 실행
```bash
# 각 프로젝트 디렉터리에서
docker compose up --build -d
```

### 3. 개발 환경 포트
- **Frontend**: 5173 (Vite dev)
- **Backend API**: 8084 (Spring Boot)
- **AI Service**: 10300 (FastAPI)
- **Nginx (Docker)**: 80

## 📦 의존성 관리

### Frontend (npm)
```bash
npm install          # 패키지 설치
npm run build       # 프로덕션 빌드
npm run lint        # 코드 린트
npm run check       # 전체 검사 (Biome)
```

### Backend (Gradle)
```bash
./gradlew build     # 전체 빌드
./gradlew test      # 테스트 실행
./gradlew bootRun   # 애플리케이션 실행
```

### AI Service (Python)
```bash
source .venv/bin/activate  # 가상 환경
pip install -r requirements.txt  # 패키지 설치
uvicorn main:app --reload  # 개발 서버
```

## 🌐 네트워크 구성

### 내부 통신
- **Frontend → Backend**: `/api` 엔드포인트
- **Backend → AI Service**: 내부 API 호출
- **Frontend → AI Service**: 직접 통신 (일부 기능)

### 환경 변수 설정
```bash
# Frontend (.env)
VITE_API_BASE_URL=http://localhost:8084/api
VITE_AI_SERVICE_URL=http://localhost:10300

# Backend (application.yml)
spring.datasource.url=jdbc:postgresql://localhost:5432/dyslexia
ai.service.url=http://localhost:10300

# AI Service (.env)
ANTHROPIC_API_KEY=your_key
REPLICATE_API_TOKEN=your_token
REDIS_URL=redis://localhost:6379
```

## 🔧 트러블슈팅

### 공통 문제
1. **포트 충돌**: 다른 프로세스 확인 후 종료
2. **환경 변수**: .env 파일 존재 및 권한 확인
3. **의존성**: node_modules, .venv 정리 후 재설치

### Docker 관련
1. **빌드 실패**: Dockerfile 경로 및 권한 확인
2. **컨테이너 충돌**: `docker compose down` 후 재시작
3. **볼륨 마운트**: host 경로 권한 확인

### 개발 환경
1. **React 개발 서버**: Vite HMR 확인
2. **Spring Boot**: JAR 파일 빌드 상태 확인
3. **FastAPI**: 가상 환경 및 패키지 버전 확인