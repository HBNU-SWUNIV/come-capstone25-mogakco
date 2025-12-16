@@ -0,0 +1,127 @@
# Dyslexia AI 프로젝트 - CLAUDE.md

## 📋 프로젝트 개요
난독증 아동을 위한 PDF 텍스트 전처리 및 AI 변환 서비스입니다.

## 🔧 자주 사용하는 명령어

### 개발 환경 설정
```bash
# 가상 환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# 패키지 설치
pip install -r requirements.txt

# 서버 실행
uvicorn main:app --reload --port 10300
```

### 개발 도구
```bash
# 린트 (사용 가능한 경우)
python -m flake8 src/
python -m black src/

# 타입 체크 (사용 가능한 경우)
python -m mypy src/
```

## 🏗️ 프로젝트 구조

```
dyslexia-ai/
├── main.py                    # FastAPI 애플리케이션 진입점
├── requirements.txt           # 의존성 패키지
├── src/
│   ├── api/                   # API 라우터
│   │   ├── preprocessing_router.py
│   │   ├── transformation_router.py
│   │   └── pipeline_router.py
│   ├── prompts/               # AI 프롬프트 템플릿
│   │   ├── system_prompts.py
│   │   └── user_prompts.py
│   ├── services/              # 비즈니스 로직
│   │   ├── preprocessing_service.py
│   │   └── transformation_service.py
│   └── utils/                 # 유틸리티 함수
│       └── anthropic_client.py
└── temp/                      # 임시 파일 저장소
```

## 🛠️ 기술 스택

### 웹 프레임워크
- **FastAPI**: 고성능 Python 웹 프레임워크
- **Uvicorn**: ASGI 서버

### AI & LLM
- **Anthropic Claude**: 텍스트 변환 및 생성
- **LangChain**: LLM 체인 및 프롬프트 관리

### 문서 처리
- **PDFPlumber**: PDF 텍스트 추출
- **KoNLPy**: 한국어 자연어 처리

## 🔑 핵심 기능

### 1. PDF 전처리 (preprocessing_service.py)
- **텍스트 추출**: 머리말/꼬리말 제거 옵션
- **구조 정규화**: 문단 구분자 통일
- **의미 단위 청킹**: 토큰 제한 내에서 그리디 알고리즘 적용

### 2. AI 변환 (transformation_service.py)
- **Claude API 연동**: 난독증 친화적 텍스트 변환
- **프롬프트 관리**: 시스템/사용자 프롬프트 템플릿

### 3. API 엔드포인트
- **POST /preprocess**: PDF 전처리 및 청킹
- **POST /transform**: 텍스트 AI 변환
- **POST /pipeline**: 전체 파이프라인 처리

## 🌐 환경 변수

```bash
# .env 파일
ANTHROPIC_API_KEY=your_api_key_here
TEMP_DIR=./temp

# AWS S3 설정 (이미지 업로드용)
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=ap-northeast-2
```

## 🚀 개발 가이드

### 코드 스타일
- **PEP 8** 준수
- **Type Hints** 사용
- **함수 주석** 포함

### 보안 고려사항
- Path Traversal 방지
- 업로드 파일 검증
- API 키 환경 변수 관리

### 성능 최적화
- 그리디 청킹 알고리즘
- 토큰 수 계산 최적화
- 임시 파일 자동 정리

## 📊 모니터링

### 로그 출력
- PDF 처리 상태
- 토큰 수 계산
- 처리 시간 측정

### 에러 처리
- HTTPException 사용
- 상세한 에러 메시지
- 스택 트레이스 출력

## 🔗 참고 링크

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Anthropic Claude API](https://docs.anthropic.com/claude/docs/)
- [LangChain 공식 문서](https://python.langchain.com/)
- [PDFPlumber 문서](https://pdfplumber.readthedocs.io/)
- [KoNLPy 문서](https://konlpy.org/)
  No newline at end of file
