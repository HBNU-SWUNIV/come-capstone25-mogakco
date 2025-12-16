## Docker 실행 가이드

이 문서는 Dyslexia AI FastAPI 앱을 Docker/Compose로 실행하는 방법을 설명합니다.

### 사전 준비
- 루트 경로에 `.env` 파일이 있어야 합니다. 최소 필요 항목:
  - `ANTHROPIC_API_KEY` (필수, 개발 시 임의값 가능)
  - `REPLICATE_API_TOKEN` (필수, 개발 시 임의값 가능)
  - 선택: `AWS_*`, `S3_*` 등 S3 관련 설정
  - 선택: `REDIS_*` (Compose 사용 시 `REDIS_HOST`, `REDIS_PORT`는 자동 오버라이드됨)

주의: `.dockerignore`에 `.env`를 포함하여 이미지 빌드에 비밀정보가 포함되지 않습니다. 컨테이너에는 `env_file`로만 주입됩니다.

### 빌드 및 실행

1) 빌드 + 실행

```bash
docker compose up --build
```

Java(KoNLPy) 미사용 시 이미지 슬림화(옵션)

```bash
docker compose build --build-arg INSTALL_JAVA=false
docker compose up
```

2) 접속 URL
- 앱 상태: `http://localhost:10300/`
- API 문서: `http://localhost:10300/docs`
- Redis 헬스: `http://localhost:10300/health/redis`

3) 로그 확인/종료

```bash
docker compose logs -f app
docker compose down
```

### 구성 설명
- `app` 서비스
  - 포트: `10300` (호스트로 바인딩)
  - 코드 핫리로드를 위해 소스 디렉토리를 컨테이너 `/app`에 마운트
  - 기본 실행 커맨드: `uvicorn main:app --reload --host 0.0.0.0 --port 10300`
  - `env_file: .env` 로 환경변수 주입, Redis는 내부 네트워크 서비스(`redis`)를 사용하도록 `REDIS_HOST=redis`로 오버라이드
- `redis` 서비스
  - 이미지: `redis:7-alpine`
  - 기본 포트 `6379` 노출 및 헬스체크 포함

### 생산(프로덕션) 모드 팁
- 핫리로드/볼륨 마운트를 제거하고, `--reload` 없이 실행하도록 변경 권장:

```yaml
services:
  app:
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10300"]
    volumes: []
```

### 트러블슈팅
- 애플리케이션 시작 시 `.env`의 `ANTHROPIC_API_KEY`, `REPLICATE_API_TOKEN`이 없으면 부팅 시점에서 오류가 발생합니다. 개발 목적으로는 임의의 placeholder 값을 넣어도 됩니다.
- 이미지 빌드 중 Java 패키지 이슈가 발생하면 `INSTALL_JAVA=false`로 빌드하거나, 기본 설치 패키지(현재 `openjdk-21-jdk-headless`)가 네트워크/미러에서 사용 가능한지 확인하세요.
