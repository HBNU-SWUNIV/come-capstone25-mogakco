FastAPI Application: 비동기 교안 생성 PRD (Product Requirements Document)
1. 개요 (Overview)
   본 문서는 PDF 기반의 비동기 교안 생성 파이프라인에서 FastAPI(LangChain) 애플리케이션의 역할과 요구사항을 정의합니다. FastAPI 애플리케이션은 Spring 서버로부터 PDF 파일과 Job ID를 받아, LangChain을 활용한 핵심적인 교안 생성 및 가공 로직을 수행하고, 처리 과정과 최종 결과를 Spring 서버에 비동기적으로 전달하는 역할을 담당합니다.

2. 목표 (Goals)
   핵심 로직 수행: PDF 문서의 내용을 파싱하고, LangChain 모델을 통해 난독증 사용자를 위한 맞춤형 교안 콘텐츠(JSON 형식)를 생성한다.

비동기 통신: 전체 처리 파이프라인의 진행 상황, 최종 결과, 그리고 잠재적 오류를 Redis Pub/Sub을 통해 Spring 서버에 실시간으로 전달한다.

성능 및 확장성: 대용량 PDF 파일 처리와 다수의 동시 요청에 대응할 수 있도록 효율적이고 확장 가능한 아키텍처를 구현한다.

모듈화: PDF 파싱, 텍스트 변환, 이미지 생성 등 각 단계를 독립적인 모듈로 구현하여 유지보수성과 재사용성을 높인다.

3. 시스템 중심 스토리 (System Stories)
   As a 시스템(FastAPI),
   I want to Spring 서버로부터 PDF 파일과 고유 Job ID를 포함한 교안 생성 요청을 수신하고,
   So that 해당 요청을 즉시 백그라운드 작업으로 등록하고 처리를 시작할 수 있다.

As a 시스템(FastAPI),
I want to 교안 생성 파이프라인의 주요 단계(e.g., 텍스트 추출, 내용 변환, 이미지 생성)를 거칠 때마다 진행률을 계산하고,
So that { "jobId": "...", "progress": ... } 형태의 메시지를 Redis에 Publish하여 Spring 서버에 진행 상황을 알릴 수 있다.

As a 시스템(FastAPI),
I want to 교안 생성이 성공적으로 완료되면, 생성된 대용량 JSON 파일을 S3에 업로드하고,
So that 두 가지 방식으로 완료를 알린다: (1) Redis result 채널에 { "jobId": "...", "s3_url": "..." } 를 발행하고, (2) Spring 콜백 URL(POST /api/document/complete)로 { "jobId": "...", "pdfName": "...", "data": {...} } 바디를 전송한다.

As a 시스템(FastAPI),
I want to 처리 과정 중 예상치 못한 오류가 발생하면 즉시 작업을 중단하고,
So that { "jobId": "...", "error": "..." } 형태의 실패 메시지를 Redis에 Publish하여 Spring 서버가 오류 상황을 인지하고 처리할 수 있도록 한다.

4. 기능 요구사항 (Functional Requirements)
   4.1. 비동기 교안 생성 요청 API
   엔드포인트: POST /api/v2/process/async

설명: Spring 서버로부터 PDF 파일과 Job ID를 받아 비동기 교안 생성 프로세스를 시작한다.

Request Body:

file: UploadFile (PDF 파일)

job_id: str (Spring에서 생성한 고유 ID)

프로세스:

요청을 수신하면 즉시 유효성을 검증한다.

job_id와 임시 저장된 file 정보를 백그라운드 작업 큐(e.g., background_tasks)에 추가한다.

클라이언트(Spring)에게는 작업이 정상적으로 접수되었음을 알리는 202 Accepted 응답을 즉시 반환한다.

4.2. 백그라운드 교안 생성 파이프라인
설명: 백그라운드에서 실제 교안 생성 로직을 순차적으로 수행한다.

프로세스:

초기 상태 설정: Job의 상태를 PROCESSING으로 설정하고 Redis에 기록한다.

PDF 전처리 (Preprocessing): PDF 파일에서 텍스트와 이미지를 페이지 단위로 추출하고 구조화한다. 진행률을 계산하여 Redis에 Publish한다.

핵심 콘텐츠 변환 (Transformation): 추출된 텍스트를 의미 있는 단위(Chunk)로 나누어 LangChain 모델에 전달한다. 모델은 각 Chunk를 난독증 친화적인 콘텐츠 블록(텍스트, 리스트, 테이블 등)으로 변환한다. 각 페이지 변환 완료 시마다 진행률을 Publish한다.

보조 콘텐츠 생성 (Generation): 변환된 콘텐츠를 기반으로 요약 팁, 관련 이미지 등을 추가로 생성할 수 있다. (선택적 단계)

결과 집계 및 저장: 모든 페이지의 처리 결과를 종합하여 최종적인 대용량 JSON 객체를 생성한다.

생성된 JSON 파일을 S3 버킷에 job_id를 키로 하여 업로드한다.

4.3. Redis Pub/Sub 연동
설명: Spring 서버와의 비동기 통신을 위해 Redis 채널에 메시지를 Publish한다.

Publisher 구현:

진행률 채널 (progress-channel): 파이프라인의 각 주요 단계가 완료될 때마다 현재 진행률(%)을 job_id와 함께 Publish한다.

결과 채널 (result-channel): 최종 JSON 파일이 S3에 성공적으로 업로드되면, 해당 파일의 S3 URL(또는 URI)을 job_id와 함께 Publish한다.
또한 Spring 콜백도 병행하여 호출한다(구성 가능).

실패 채널 (failure-channel): 파이프라인 실행 중 오류 발생 시, 오류 내용과 job_id를 함께 Publish한다.

4.4. 상태 관리 API (선택적)
엔드포인트: GET /api/v2/process/status/{job_id}

설명: Spring 서버가 Redis 메시지를 놓쳤을 경우를 대비하여, 특정 작업의 현재 상태를 직접 조회할 수 있는 보조 API를 제공한다.

프로세스:

요청된 job_id를 키로 Redis 또는 내부 상태 저장소에서 작업의 현재 상태(PROCESSING, COMPLETED, FAILED)와 진행률을 조회하여 반환한다.

5. 비기능 요구사항 (Non-Functional Requirements)
   성능 (Performance):

API 요청(작업 접수)은 100ms 이내에 응답해야 한다.

백그라운드 작업은 리소스(CPU, 메모리)를 효율적으로 사용해야 하며, 특정 작업이 다른 작업에 과도한 영향을 미치지 않도록 설계한다.

확장성 (Scalability):

애플리케이션은 Docker 컨테이너화를 통해 수평 확장이 가능해야 한다. (e.g., Kubernetes 환경에서 Pod 수 증설)

Uvicorn과 Gunicorn 등을 사용하여 여러 워커 프로세스를 운영하여 동시성을 확보한다.

안정성 (Reliability):

LangChain 모델 API 호출 실패, Redis 연결 오류 등 외부 서비스와의 통신 실패 시 재시도(Retry) 로직을 구현한다.

파이프라인의 각 단계에서 발생하는 예외를 명확하게 처리하고, 실패 원인을 로그로 기록한다.

보안 (Security):

내부망 통신을 가정하지만, 필요한 경우 API Key 등을 통해 Spring 서버로부터의 요청만 허용하도록 API를 보호한다.

6. 기술 명세 (Technical Specifications)
   Framework: FastAPI

Language: Python 3.12+

Key Libraries:

AI/ML: langchain, anthropic (or openai)

Web: uvicorn, gunicorn, python-multipart

Async: redis (asyncio support)

Cloud: boto3 (for AWS S3)

Configuration: pydantic-settings

데이터 모델 (Pydantic): API 요청/응답 및 최종 결과 JSON의 구조를 Pydantic 모델로 명확하게 정의한다. 최종 결과는 snake_case로 필드명을 통일한다.

환경 변수 관리:

.env 파일과 pydantic-settings를 사용하여 주요 설정값을 관리한다.

환경 변수	설명	예시 값
ANTHROPIC_API_KEY	Anthropic Claude 모델 API 키	sk-ant-xxxxxxxx
REDIS_HOST	Redis 서버 호스트 주소	localhost / redis.internal
REDIS_PORT	Redis 서버 포트	6379
REDIS_PASSWORD	Redis 서버 비밀번호 (필요시)	your-secure-password
S3_BUCKET_NAME	결과 JSON 파일을 저장할 S3 버킷 이름	my-dyslexia-app-results
AWS_ACCESS_KEY_ID	AWS IAM 사용자의 Access Key ID	AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY	AWS IAM 사용자의 Secret Access Key	wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
REDIS_PROGRESS_CHANNEL	진행률을 Publish할 Redis 채널 이름	progress-channel
REDIS_RESULT_CHANNEL	결과물 위치를 Publish할 Redis 채널 이름	result-channel
REDIS_FAILURE_CHANNEL	실패 알림을 Publish할 Redis 채널 이름	failure-channel
SPRING_CALLBACK_URL 또는 SPRING_SERVER_BASE_URL	Spring 콜백 엔드포인트 설정	https://spring.example.com/api/document/complete

Sheets로 내보내기
7. 범위 외 (Out of Scope)
   Spring 애플리케이션의 상세 구현.

사용자 인증 및 인가 처리 (모든 요청은 신뢰할 수 있는 Spring 서버로부터 온다고 가정).

처리 완료된 교안 데이터의 영구적인 데이터베이스 저장.
