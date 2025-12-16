# 한밭대학교 소프트웨어융합대학 캡스톤디자인

## 리딩브릿지 - AI 기반 난독증 아동 맞춤형 학습 교재 자동 변환 플랫폼 개발
## Reading Bridge - AI-based Automatic Conversion Platform for Personalized Learning Materials for Children with Dyslexia

### 팀 구성

| 학번 | 이름 | 역할 |
|------|------|------|
| 20197123 | 최은기 | 팀장, AI 서비스 개발 |
| 20227128 | 김지훈 | 백엔드 개발 |
| 20227131 | 서동현 | 프론트엔드 개발 |

### Team Project Background

#### 필요성
- 난독증 아동은 일반 교육 자료로 학습 시 읽기 어려움을 겪어 학습 격차가 발생
- 교사와 학부모가 맞춤형 교재 제작에 평균 7일의 시간과 수십만 원의 비용 소요
- 전문 치료 기관은 수도권에 집중되어 지역적 교육 불균형 심화

#### 기존 해결책의 문제점
- **높은 비용**: 맞춤형 교재 제작을 위한 외주 비용 부담
- **시간 소요**: 전문가에 의한 수작업 교재 변환으로 인한 긴 제작 기간
- **접근성 부족**: 지역 및 소득에 따른 교육 기회 불평등
- **제한된 확장성**: 개별 맞춤 제작으로 대규모 적용 어려움

### System Design

#### System Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend (App)   │    │   Backend (API)   │    │    AI Service     │
│   React + Vite     │    │  Spring Boot      │    │     FastAPI       │
│   TanStack Router  │◄──►│   + PostgreSQL    │◄──►│  + Claude API     │
│   + Zustand        │    │   + JPA           │    │   + LangChain     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

#### System Requirements
- **기능 요구사항**: PDF 자동 변환, 맞춤형 교재 생성, 접근성 설정, 학습 진행 추적
- **성능 요구사항**: 5분 내 교재 변환, 100명 동시 접속 지원, 99.9% 가용성
- **품질 요구사항**: 웹 접근성 WCAG 2.1 준수, 데이터 보안, 실시간 동기화

#### 프로젝트 구조
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

### Case Study

#### Description
본 프로젝트는 AI 기술을 활용하여 난독증 아동을 위한 맞춤형 교재 자동 변환 플랫폼을 개발하였습니다. 기존의 수작업 교재 제작 방식의 한계를 극복하고, AI를 통한 자동화된 변환 프로세스로 시간과 비용을 획기적으로 단축했습니다.

#### 기술적 특징
1. **2-Tier 아키텍처**: Spring Boot와 FastAPI 서버 분리로 역할 명확화
2. **LangChain 체이닝**: 복합 AI 기능의 유연한 파이프라인 구성
3. **JWT 인증**: 안전한 사용자 인증 시스템 구축
4. **Redis 캐싱**: 실시간 응답 속도 향상
5. **Docker 컨테이너화**: 일관된 개발 및 배포 환경 제공

#### 교안 생성 프로세스
1. PDF 파일에서 텍스트와 메타데이터 추출
2. 텍스트 정규화 및 구조화된 JSON 데이터 변환
3. AI 기반 시각적 삽화 생성
4. 어휘 분석 및 쉬운 설명 추가
5. 최종 디지털 교안 데이터셋 완성

#### 데이터베이스 설계
- 보호자-학생 1:N 관계
- 교재-페이지 계층적 구조
- 학생-교재 다대다 관계
- 개인화된 접근성 설정 지원

### Conclusion

#### 기대효과
- **사회적 파급효과**: 난독증 아동의 교육 기회 확대 및 심리적 장벽 해소
- **기술적 파급효과**: 생성형 AI 기술의 교육 접근성 분야 선도적 적용
- **경제적 파급효과**: 연 28억 원 규모의 난독증 교육 시장 선점 기회

#### 활용방안
- **가정 및 학교 현장**: 맞춤형 교재 신속 제작으로 학습 효율 증대
- **교육 복지**: 지역 및 소득에 관계없는 동등한 교육 기회 제공
- **플랫폼 확장**: 교안 스토어, 영어 교재 등 추가 기능 개발 가능

---

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

## 📊 기술 스택

### Frontend
- **React 19** + TypeScript
- **Vite** (빌드 도구)
- **TanStack Router** (라우팅)
- **Zustand** (상태 관리)
- **Tailwind CSS** (스타일링)

### Backend
- **Java 17** + **Spring Boot 3.x**
- **PostgreSQL** (데이터베이스)
- **JPA** (ORM)
- **JWT** (인증)
- **Redis** (캐싱)

### AI Service
- **Python 3.12+** + **FastAPI**
- **Claude API** (텍스트 생성)
- **LangChain** (프롬프트 관리)
- **KoNLPy** (한국어 분석)

## 📄 라이선스

본 프로젝트는 교육 목적으로 사용되며, 관련 법률을 준수합니다.

---

## 주의사항

- 다른 Open Source SW를 사용하는 경우 저작권을 명시해야 함
- 산학연계 캡스톤의 경우 기업의 기밀이 담긴 데이터는 제외할 것
- **기업 기밀 데이터가 Github에 공개되었을 시의 책임은 공개한 학생에게 있음**

*마지막 업데이트: 2025년 11월 9일*