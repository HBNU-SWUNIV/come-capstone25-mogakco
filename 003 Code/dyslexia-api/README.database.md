# 데이터베이스 설정 가이드

## 🐳 Docker를 사용한 PostgreSQL & Redis 설정

### 1. 환경 변수 설정
```bash
# .env.example 파일을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일을 편집하여 실제 값들을 입력
vi .env
```

### 2. 데이터베이스 실행
```bash
# PostgreSQL, Redis, 관리 도구들 실행
docker-compose -f docker-compose.db.yml up -d

# 로그 확인
docker-compose -f docker-compose.db.yml logs -f postgres redis

# 데이터베이스 상태 확인
docker-compose -f docker-compose.db.yml ps
```

### 3. 데이터베이스 접속 정보

#### PostgreSQL 직접 접속
- **Host**: localhost
- **Port**: 5433
- **Database**: dyslexia
- **Username**: dyslexia_user
- **Password**: dyslexia_password

#### Redis 직접 접속
- **Host**: localhost
- **Port**: 6379
- **Password**: (없음 - 개발환경)
- **Database**: 0

#### pgAdmin 웹 접속 (PostgreSQL 관리)
- **URL**: http://localhost:5050
- **Email**: admin@dyslexia.local
- **Password**: admin123

#### Redis Commander 웹 접속 (Redis 관리)
- **URL**: http://localhost:8081
- **Username**: admin
- **Password**: admin123

### 4. pgAdmin에서 서버 연결 설정
pgAdmin 접속 후 새 서버 등록:
- **Name**: Dyslexia Local DB
- **Host name/address**: postgres
- **Port**: 5432
- **Username**: dyslexia_user
- **Password**: dyslexia_password

### 5. 애플리케이션 실행
```bash
# 데이터베이스 실행 후 Spring Boot 애플리케이션 실행
./gradlew bootRun
```

## 🔧 유용한 Docker 명령어

```bash
# 데이터베이스만 실행
docker-compose -f docker-compose.db.yml up -d postgres

# 데이터베이스 중지
docker-compose -f docker-compose.db.yml stop

# 데이터베이스와 볼륨까지 완전 삭제 (데이터 초기화)
docker-compose -f docker-compose.db.yml down -v

# PostgreSQL 컨테이너에 직접 접속
docker exec -it dyslexia_postgres psql -U dyslexia_user -d dyslexia

# Redis 컨테이너에 직접 접속
docker exec -it dyslexia_redis redis-cli
```

## 📊 데이터베이스 최적화 설정

### PostgreSQL 최적화
- **최대 연결 수**: 200
- **공유 버퍼**: 256MB
- **효과적인 캐시 크기**: 1GB
- **체크포인트 완료 목표**: 90%
- **통계 목표**: 100
- **pg_stat_statements**: 쿼리 성능 모니터링 활성화

### Redis 최적화
- **최대 메모리**: 256MB
- **메모리 정책**: allkeys-lru (가장 오래된 키부터 삭제)
- **데이터 지속성**: AOF (Append Only File) 활성화
- **스냅샷**: 자동 저장 설정
- **슬로우 로그**: 10ms 이상 쿼리 기록

## 🚨 주의사항

1. **환경변수**: `.env` 파일을 반드시 설정하세요
2. **포트 충돌**: 5433, 6379, 5050, 8081 포트가 사용 가능한지 확인하세요
3. **데이터 백업**: 프로덕션 환경에서는 정기적인 백업을 설정하세요
4. **보안**: 실제 환경에서는 기본 패스워드를 변경하세요