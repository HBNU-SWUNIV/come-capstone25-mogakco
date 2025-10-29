# 난독증 교육 플랫폼 (Dyslexia Educational Platform)

## 📋 프로젝트 개요

본 프로젝트는 난독증이 있는 초등학생들을 위한 종합 교육 자료 뷰어 플랫폼입니다. AI 기반의 문서 변환, 개인화된 접근성 설정, 학습 진행 추적 기능을 통해 난독증 학생의 효과적인 학습을 지원합니다.

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend (App)   │    │   Backend (API)   │    │    AI Service     │
│   React + Vite     │    │  Spring Boot      │    │     FastAPI       │
│   TanStack Router  │◄──►│   + PostgreSQL    │◄──►│  + Claude API     │
│   + Zustand        │    │   + JPA           │    │   + LangChain     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 프로젝트 구조

```
003 Code/
├── dyslexia-app/          # React 프론트엔드 애플리케이션
│   ├── src/
│   │   ├── features/      # 기능별 모듈 (auth, viewer, layouts)
│   │   ├── shared/        # 공통 리소스
│   │   ├── routes/        # 라우팅 설정
│   │   └── components/    # UI 컴포넌트
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── dyslexia-api/          # Spring Boot 백엔드 API
│   ├── src/main/java/
│   │   └── com/dyslexia/
│   │       ├── entity/     # JPA 엔티티
│   │       ├── service/    # 비즈니스 로직
│   │       ├── controller/ # REST 컨트롤러
│   │       └── repository/ # 데이터 접근
│   ├── build.gradle
│   ├── Dockerfile
│   └── Makefile
├── dyslexia-ai/           # FastAPI AI 서비스
│   ├── src/
│   │   ├── api/           # API 라우터
│   │   ├── prompts/       # AI 프롬프트
│   │   ├── services/      # 비즈니스 로직
│   │   └── utils/         # 유틸리티
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.sh
└── README.md
```

## 🚀 빌드 및 실행 환경

### 개발 환경
- **Frontend**: Node.js 18+, React 19, TypeScript, Vite
- **Backend**: Java 17, Spring Boot 3.x, PostgreSQL
- **AI Service**: Python 3.12+, FastAPI, Uvicorn

### 빌드 도구
- **Frontend**: npm/Vite
- **Backend**: Gradle
- **AI Service**: Python venv/pip

## 🛠️ 실행 방법

### 1. AI 서비스 (FastAPI)
```bash
cd dyslexia-ai
./run.sh
# 또는 수동 실행
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 10300
```

### 2. 백엔드 API (Spring Boot)
```bash
cd dyslexia-api
make build
make up
# 또는
./gradlew bootRun
```

### 3. 프론트엔드 (React)
```bash
cd dyslexia-app
npm install
npm run dev
```

### Docker 기반 실행 (권장)
```bash
# 각 프로젝트 디렉터리에서
docker compose up --build -d
```

## 📊 데이터베이스 스키마

주요 엔티티 관계:

- **Guardians** 1:N **Students** (보호자-학생)
- **Guardians** 1:N **Documents** (문서 업로드)
- **Documents** 1:N **Textbooks** (문서 변환)
- **Textbooks** 1:N **Pages** (페이지 분할)
- **Pages** 1:N **VocabularyAnalysis** (어휘 분석)
- **Students** N:M **Textbooks** (교재 할당)

## 🔧 주요 기능

### 1. 문서 처리 파이프라인
- PDF 업로드 및 AI 변환
- 페이지별 분할 및 처리
- 난독증 친화적 콘텐츠 생성

### 2. 접근성 개인화
- 개인별 폰트, 간격, 색상 설정
- 텍스트 음성 변환 (TTS)
- 읽기 강조 표시 기능

### 3. 학습 관리
- 교재 할당 및 진행 추적
- 페이지별 학습 시간 기록
- 이해도 평가 시스템

### 4. AI 기반 어휘 학습
- 문장 내 어휘 자동 추출
- 난이도 레벨별 분석
- 음소 분해 및 발음 연습

## 🤖 AI 기술 스택

### 사용된 AI 서비스
- **Claude API**: 텍스트 변환 및 생성
- **LangChain**: 프롬프트 관리 및 체인
- **자연어 처리**: KoNLPy (한국어 분석)

### 주요 처리 로직
1. **텍스트 전처리**: 구두/꼬리말 제거, 청킹 최적화
2. **의미 단위 분할**: 토큰 제한 내 그리디 알고리즘
3. **난독증 친화적 변환**: 문장 구조 단순화, 시각적 보조 추가

## 🔐 API 인증

### 사용자 인증
- 카카오 로그인 통합
- JWT 토큰 기반 세션 관리
- 역할별 접근 제어 (교사/보호자/학생)

### 보안 기능
- 토큰 자동 갱신
- API 엔드포인트 보호
- CORS 설정

## 📱 접근성 특징

### 난독증 친화적 디자인
- **OpenDyslexic** 전용 폰트 지원
- 충분한 색상 대비 (WCAG 2.1 준수)
- 키보드 네비게이션 최적화
- 스크린 리더 호환성

### 개인화 설정
- 동적 폰트 크기 조정
- 줄 간격 및 문자 간격 제어
- 색상 테마 선택 (라이트/다크/커스텀)
- TTS 속도 및 음성 선택

## 📈 성능 최적화

### 프론트엔드
- 코드 스플리팅 및 지연 로딩
- 컴포넌트 메모이제이션
- 이미지 최적화

### 백엔드
- 데이터베이스 쿼리 최적화
- 캐싱 전략 (Redis)
- API 응답 시간 개선

### AI 서비스
- 요청 큐 관리
- 배치 처리 최적화
- 결과 캐싱

## 🔧 개발 가이드

### 코드 스타일
- **Frontend**: TypeScript, React Hooks, Tailwind CSS
- **Backend**: Java 17, Spring Boot 3.x, JPA
- **AI**: Python 3.12+, FastAPI, Async/Await

### 커밋 규칙
- Conventional Commits 사용
- 코드 리뷰 필수
- 자동화된 린트/포맷팅

## 📄 라이선스

본 프로젝트는 교육 목적으로 사용되며, 관련 법률을 준수합니다.

---

## 주의사항

- 다른 Open Source SW를 사용하는 경우 저작권을 명시해야 함
- 산학연계 캡스톤의 경우 기업의 기밀이 담긴 데이터는 제외할 것
- **기업 기밀 데이터가 Github에 공개되었을 시의 책임은 공개한 학생에게 있음**

*마지막 업데이트: 2025년 10월 29일* 
