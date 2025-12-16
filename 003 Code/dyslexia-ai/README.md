# Dyslexia AI - 난독증 친화적 텍스트 변환 API

난독증 아동을 위한 PDF 텍스트 전처리 및 AI 변환 서비스

## 🚀 빠른 시작

### 사전 요구사항
- Python 3.13.x

### 설치 및 실행 방법
1. `py -m venv .venv`                          # 가상 환경 생성
2. `.\.venv\Scripts\Activate`                  # 가상 환경 활성화 (Windows)
3. `python.exe -m pip install --upgrade pip`   # pip 업데이트
4. `pip install -r requirements.txt`           # 패키지 설치
5. `uvicorn main:app --reload`                 # 서버 실행

### 접속 URL
- Health test: http://127.0.0.1:8000
- API 문서: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc


## 📝 환경 변수
- `/.env` 파일 생성

## 🐳 Docker로 실행하기
- 빠르게 컨테이너로 실행하려면 `docker-compose.yml`을 사용하세요.

```bash
docker compose up --build
```

- 접속: `http://localhost:10300/` (문서: `/docs`)
- 자세한 내용은 `docs/docker.md` 참고
