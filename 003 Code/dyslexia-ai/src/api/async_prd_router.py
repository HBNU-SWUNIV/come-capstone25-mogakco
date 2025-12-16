"""
PRD 명세에 따른 비동기 교안 생성 라우터
Spring 서버와의 연동을 위한 표준 인터페이스
"""
import asyncio
import logging
import uuid
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, Form, BackgroundTasks
from pydantic import BaseModel

from src.services.prd_async_processor import PRDAsyncProcessor
from src.services.redis_pub_sub_service import RedisPubSubService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["Async Processing PRD"])

# PRD 비동기 프로세서 초기화
prd_processor = PRDAsyncProcessor()
pub_sub_service = RedisPubSubService()


class AsyncProcessRequest(BaseModel):
    """비동기 처리 요청 모델"""
    job_id: str


class AsyncProcessResponse(BaseModel):
    """비동기 처리 응답 모델"""
    success: bool
    job_id: str
    message: str
    status: str = "PROCESSING"


class JobStatusResponse(BaseModel):
    """Job 상태 응답 모델"""
    job_id: str
    status: str  # PROCESSING, COMPLETED, FAILED
    progress: Optional[float] = None
    error: Optional[str] = None


@router.post("/process/async", response_model=AsyncProcessResponse)
async def process_pdf_async(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF 파일"),
    job_id: str = Form(..., description="Spring에서 생성한 고유 Job ID"),
    textbook_id: Optional[int] = Form(None, description="교재/문서 ID (어휘 저장용)")
):
    """
    비동기 교안 생성 요청 처리 (PRD 4.1)

    Spring 서버로부터 PDF 파일과 Job ID를 받아 비동기 교안 생성 프로세스를 시작합니다.
    처리 완료 후 Redis Pub/Sub으로 결과를 전달합니다.
    """

    try:
        # 파일 검증
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="파일이 제공되지 않았습니다.")

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="PDF 파일만 지원됩니다.")

        # Job ID 검증
        if not job_id or not job_id.strip():
            raise HTTPException(status_code=400, detail="job_id가 제공되지 않았습니다.")

        # 중복 작업 확인
        if await prd_processor.is_job_active(job_id):
            raise HTTPException(
                status_code=409,
                detail=f"Job {job_id}는 이미 처리 중입니다."
            )

        logger.info(f"비동기 PDF 처리 시작: job_id={job_id}, filename={file.filename}")

        # 응답 반환 전 파일 내용을 메모리로 복사하여 수명 보장
        file_bytes = await file.read()

        # 백그라운드 작업으로 처리 시작 (UploadFile 대신 안전한 바이트 전달)
        background_tasks.add_task(
            prd_processor.process_pdf_pipeline,
            job_id=job_id,
            file_bytes=file_bytes,
            filename=file.filename,
            textbook_id=textbook_id,
        )

        # 즉시 202 Accepted 응답 반환
        return AsyncProcessResponse(
            success=True,
            job_id=job_id,
            message="PDF 처리가 시작되었습니다.",
            status="PROCESSING"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"비동기 처리 시작 실패: job_id={job_id}, error={str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"비동기 처리 시작 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/process/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    작업 상태 조회 API (PRD 4.4)

    Spring 서버가 Redis 메시지를 놓쳤을 경우를 대비하여
    특정 작업의 현재 상태를 직접 조회할 수 있는 API입니다.
    """

    try:
        # Redis에서 작업 상태 조회
        job_status = await prd_processor.get_job_status(job_id)

        if not job_status:
            raise HTTPException(
                status_code=404,
                detail=f"작업 {job_id}를 찾을 수 없습니다."
            )

        return JobStatusResponse(
            job_id=job_id,
            status=job_status.get("status", "UNKNOWN"),
            progress=job_status.get("progress"),
            error=job_status.get("error")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"작업 상태 조회 실패: job_id={job_id}, error={str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"작업 상태 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/health/pubsub")
async def check_pubsub_health():
    """Redis Pub/Sub 연결 및 실제 발행/수신 동작 상태 확인"""

    try:
        is_healthy, message = await pub_sub_service.health_check_with_pubsub()

        if is_healthy:
            return {
                "status": "healthy",
                "service": "redis_pubsub",
                "message": message,
                "channels": {
                    "progress": pub_sub_service.progress_channel,
                    "result": pub_sub_service.result_channel,
                    "failure": pub_sub_service.failure_channel,
                },
            }
        else:
            raise HTTPException(status_code=503, detail=message)

    except Exception as e:
        logger.error(f"Pub/Sub 헬스 체크 실패: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=f"Redis Pub/Sub 상태 확인 중 오류가 발생했습니다: {str(e)}",
        )
