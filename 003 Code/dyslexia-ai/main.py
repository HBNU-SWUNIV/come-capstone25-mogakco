import logging
from src.utils.env_config import setup_environment
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.api import preprocessing_router, transformation_router, image_generation_router, progress_router, output_router
from src.services.redis_service import create_redis_service

# 로그 설정
logging.basicConfig(
    level=logging.INFO,  # INFO 레벨로 설정 (운영시에는 WARNING으로 변경)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 특정 모듈의 로그 레벨을 DEBUG로 설정 (디버깅용)
logging.getLogger('src.services.preprocessing_service').setLevel(logging.DEBUG)
logging.getLogger('src.utils.anthropic_client').setLevel(logging.DEBUG)

app = FastAPI(
    title="Dyslexia AI API",
    description="Transform PDF to educational content for dyslexia children.",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용 (개발 환경)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], # 명시적으로 허용할 메서드 지정
    allow_headers=[
        "accept",
        "accept-encoding", 
        "authorization",
        "content-type",
        "dnt",
        "origin",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
    ], # 명시적으로 허용할 헤더 지정
)

# 임시 디렉토리 설정
setup_environment()

# Redis 서비스 초기화
redis_service = create_redis_service()

# Redis 연결 테스트
try:
    redis_service.redis_client.redis_client.ping()
    logging.info("✅ Redis 연결 성공")
except Exception as e:
    logging.error(f"❌ Redis 연결 실패: {e}")

# 라우터 등록
app.include_router(preprocessing_router.router)
app.include_router(transformation_router.router)
app.include_router(image_generation_router.router)
app.include_router(progress_router.router)
app.include_router(output_router.router)
try:
    from src.api import thumbnail_router
    app.include_router(thumbnail_router.router)
except Exception as e:
    logging.error(f"썸네일 라우터 등록 실패: {e}")

# 비동기 처리 라우터 추가
from src.api import async_processing_router, async_processing_router_v2, async_prd_router
app.include_router(async_processing_router.router)
app.include_router(async_processing_router_v2.router)
# PRD 명세에 따른 새로운 비동기 라우터 (Spring 연동용)
app.include_router(async_prd_router.router)

# Vocabulary Analysis router
try:
    from src.api import vocabulary_router
    app.include_router(vocabulary_router.router)
except Exception as e:
    logging.error(f"어휘 분석 라우터 등록 실패: {e}")

# S3 연결 정보 부팅 시 1회 출력
@app.on_event("startup")
async def log_s3_connection_info_once():
    try:
        from src.services.image_uploader import uploader

        # 동기 로깅 함수 호출
        uploader.log_connection_info()
    except Exception as e:
        logging.error(f"S3 연결정보 로깅 중 오류: {e}")


@app.get("/")
async def root():
    """
    API 상태 확인 엔드포인트
    """
    return {
        "message": "Dyslexia AI API is running!",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health/redis")
async def redis_health():
    """
    Redis 연결 상태 확인 엔드포인트
    """
    try:
        # Redis 연결 테스트
        redis_client = redis_service.redis_client.redis_client
        redis_client.ping()
        
        return {
            "status": "healthy",
            "service": "redis",
            "message": "Redis connection is working"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "redis",
                "message": f"Redis connection failed: {str(e)}"
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10300)
