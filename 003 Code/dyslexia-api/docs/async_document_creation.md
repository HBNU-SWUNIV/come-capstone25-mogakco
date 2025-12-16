Spring Application: 비동기 교안 생성 PRD (Product Requirements Document)
1. 개요 (Overview)
   본 문서는 PDF 기반의 비동기 교안 생성 파이프라인에서 Spring 애플리케이션의 역할과 요구사항을 정의합니다. Spring 애플리케이션은 클라이언트로부터 PDF 파일을 받아 FastAPI 서버에 비동기 처리를 위임하고, Redis를 통해 처리 상태와 결과를 받아 최종적으로 RDB에 저장하는 핵심적인 역할을 수행합니다.

2. 목표 (Goals)
   비동기 처리 관리: 대용량 PDF 파일의 교안 생성 요청을 비동기적으로 처리하고, 전체 프로세스의 상태를 안정적으로 관리한다.

실시간 진행률 추적: 클라이언트가 교안 생성 작업의 진행 상황을 실시간으로 확인할 수 있는 기능을 제공한다.

데이터 파이프라인 구축: FastAPI에서 생성된 교안 데이터를 수신하여, 정해진 데이터 모델에 맞게 파싱하고 RDB에 영속화한다.

시스템 안정성 확보: 메시지 큐(Redis)를 활용하여 외부 시스템(FastAPI)과의 결합도를 낮추고, 오류 발생 시에도 데이터의 정합성을 유지할 수 있는 견고한 시스템을 구축한다.

3. 사용자 스토리 (User Stories)
   As a 사용자,
   I want to PDF 파일을 업로드하여 교안 생성을 요청하고,
   So that 시스템이 비동기적으로 교안을 처리하고 있다는 것을 즉시 확인할 수 있다.

As a 사용자,
I want to 내가 요청한 교안 생성 작업의 현재 진행률(%)을 언제든지 확인할 수 있고,
So that 작업이 얼마나 진행되었는지 파악하고 완료 시점을 예측할 수 있다.

As a 시스템(Spring),
I want to FastAPI의 교안 생성이 완료되면 생성된 대용량 JSON 데이터를 안정적으로 수신하고,
So that 해당 데이터를 파싱하여 페이지 및 콘텐츠 블록 단위로 데이터베이스에 저장할 수 있다.

As a 시스템(Spring),
I want to FastAPI에서 작업 처리 중 오류가 발생했다는 사실을 통보받고,
So that 해당 작업의 상태를 '실패'로 기록하고 잠재적인 재시도를 준비할 수 있다.

4. 기능 요구사항 (Functional Requirements)
   4.1. 교안 생성 요청 API
   설명: 클라이언트로부터 PDF 파일(multipart/form-data)을 받아 교안 생성 프로세스를 시작한다.

프로세스:

요청 수신 시, 전역적으로 고유한 Job ID (UUIDv7) 를 생성한다.

업로드된 PDF 파일과 생성된 Job ID를 FastAPI 서버의 교안 생성 API로 전달한다. (HTTP POST)

RDB에 Document 또는 유사한 엔티티를 생성하고, Job ID와 초기 상태(PENDING 또는 PROCESSING)를 저장한다.

클라이언트에게는 Job ID를 즉시 응답하여, 이후 상태를 추적할 수 있도록 한다. (202 Accepted)

4.2. 교안 생성 상태 조회 API
설명: 클라이언트가 Job ID를 이용해 특정 교안 생성 작업의 현재 상태와 진행률을 조회한다.

프로세스:

요청된 Job ID를 기준으로 RDB에서 작업 상태 정보를 조회한다.

현재 상태(PROCESSING, COMPLETED, FAILED)와 진행률(%)을 담아 클라이언트에게 응답한다.

4.3. Redis Pub/Sub 연동
설명: Redis의 Pub/Sub 기능을 이용해 FastAPI 서버와 비동기적으로 통신한다.

Subscriber 구현:

진행률 채널 구독: progress-channel (예시)을 구독한다.

메시지 수신 시, { "jobId": "...", "progress": 85 }와 같은 JSON 데이터를 파싱한다.

해당 jobId를 가진 작업의 진행률을 RDB에 업데이트한다.

결과 채널 구독: result-channel (예시)을 구독한다.

메시지 수신 시, { "jobId": "...", "s3_url": "..." }와 같이 S3에 저장된 결과 파일의 URL을 받는다.

해당 URL을 통해 S3에서 대용량 JSON 결과 파일을 다운로드한다.

다운로드한 JSON 데이터를 파싱한다. (Snake Case → Camel Case 변환 적용)

파싱된 데이터를 Page 및 하위 Block 엔티티 객체로 변환하여 RDB에 저장한다.

모든 데이터 저장이 완료되면, 해당 작업의 상태를 COMPLETED로 변경한다.

실패 채널 구독: failure-channel (예시)을 구독한다.

메시지 수신 시, { "jobId": "...", "error": "..." }와 같은 데이터를 파싱한다.

해당 jobId를 가진 작업의 상태를 FAILED로 변경하고, 오류 메시지를 로그 또는 RDB에 기록한다.

4.4. 데이터베이스 관리
엔티티 설계: 교안 생성 프로세스를 관리하고 결과를 저장하기 위한 엔티티를 설계한다. (기존 Document, Page 엔티티 활용 및 확장)

Document (or Job): jobId (PK), fileName, status (enum: PENDING, PROCESSING, COMPLETED, FAILED), progress (int), errorMessage, createdAt, completedAt 등의 필드를 포함한다.

Page: documentId (FK), pageNumber, processedContent (JSONB 타입) 등의 필드를 포함한다.

트랜잭션 관리: 교안 결과 데이터를 RDB에 저장하는 과정은 단일 트랜잭션으로 관리하여 데이터의 정합성을 보장한다.

5. 비기능 요구사항 (Non-Functional Requirements)
   성능 (Performance):

교안 생성 요청 API는 200ms 이내에 응답해야 한다.

상태 조회 API는 100ms 이내에 응답해야 한다.

확장성 (Scalability):

Spring 애플리케이션은 stateless하게 구현하여 수평 확장이 용이해야 한다.

Redis Subscriber는 다수의 메시지를 동시에 처리할 수 있도록 비동기/논블로킹 방식으로 구현하는 것을 고려한다. (e.g., Spring WebFlux, Lettuce)

안정성 (Reliability):

Redis 연결이 끊어질 경우, 재연결 로직을 구현하여 자동으로 복구되어야 한다.

JSON 파싱 또는 데이터 저장 중 오류 발생 시, 해당 트랜잭션을 롤백하고 작업 상태를 FAILED로 처리하는 로직이 반드시 포함되어야 한다.

보안 (Security):

PDF 업로드 시 파일 크기 제한, 확장자 검사 등을 통해 악의적인 파일 업로드를 방지한다.

모든 API 엔드포인트는 적절한 인증/인가 절차를 거쳐야 한다.

6. 기술 명세 (Technical Specifications)
   Framework: Spring Boot 3.x

Language: Java 17+ / Kotlin

Database: PostgreSQL

Messaging Queue: Redis (Lettuce 클라이언트)

Build Tool: Gradle

API Specification: RESTful API (세부 내용은 Swagger/OpenAPI로 문서화)

POST /api/v1/documents: 교안 생성 요청

GET /api/v1/documents/{jobId}/status: 교안 생성 상태 조회

JSON-Object Mapping:

Jackson 라이브러리를 사용한다.

application.yml에 spring.jackson.property-naming-strategy: SNAKE_CASE를 설정하여 FastAPI의 snake_case 응답을 Spring의 camelCase DTO/Entity 필드에 자동으로 매핑한다.

6.1. 외부 서비스 연동 설정 (External Service Configuration)
FastAPI 서버와 통신하기 위한 설정 정보를 application.yml과 환경 변수로 관리한다.

application.yml 설정 예시:

YAML

external:
fastapi:
url: ${FASTAPI_URL:http://localhost:8000} # 기본값 설정
endpoints:
process: /api/v2/process/async # 교안 생성 요청 엔드포인트

spring:
jackson:
property-naming-strategy: SNAKE_CASE
.env 파일 및 환경 변수 리스트:
애플리케이션 배포 환경에 따라 다음 환경 변수를 설정해야 한다.

환경 변수	설명	예시 값
FASTAPI_URL	교안 생성을 요청할 FastAPI 서버의 Base URL	http://fastapi-service.internal
REDIS_HOST	Redis 서버 호스트 주소	redis.cache.amazonaws.com
REDIS_PORT	Redis 서버 포트	6379
POSTGRES_URL	PostgreSQL 데이터베이스 JDBC URL	jdbc:postgresql://...
POSTGRES_USER	데이터베이스 사용자 이름	admin
POSTGRES_PASSWORD	데이터베이스 사용자 비밀번호	your-secure-password
S3_BUCKET_NAME	결과 JSON 파일을 저장할 S3 버킷 이름	my-dyslexia-app-results
AWS_ACCESS_KEY_ID	AWS IAM 사용자의 Access Key ID	AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY	AWS IAM 사용자의 Secret Access Key	wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

Sheets로 내보내기
7. 범위 외 (Out of Scope)
   FastAPI(LangChain) 서버의 상세 구현.

클라이언트(프론트엔드) UI/UX 개발.

교안 생성 완료 후 사용자에게 보내는 푸시 알림 기능.

실패한 작업에 대한 자동 재시도 로직 (초기 버전에서는 수동 재시도만 고려).