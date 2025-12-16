import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status

from src.services.thumbnail_service import thumbnail_service
from src.services.job_manager import get_job_result, get_job_progress

router = APIRouter(
    prefix="/api/v1/thumbnails",
    tags=["thumbnail"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def create_thumbnail(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_id: Optional[str] = Form(None),
):
    """썸네일 생성 요청 (비동기)

    Form-data:
      - file: PDF 또는 이미지 파일
      - job_id: 선택 (없으면 생성)

    Returns 202 Accepted with jobId.
    """
    try:
        job = await thumbnail_service.start(file=file, job_id=job_id)
        return {"jobId": job, "status": "ACCEPTED", "message": "Thumbnail job queued"}
    except Exception as e:
        logger.error(f"썸네일 요청 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=f"썸네일 요청 실패: {str(e)}")


@router.get("/{job_id}/status")
async def get_thumbnail_status(job_id: str):
    """썸네일 작업 진행률 조회"""
    progress = get_job_progress(job_id)
    if not progress:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    return progress.to_dict()


@router.get("/{job_id}/result")
async def get_thumbnail_result(job_id: str):
    """썸네일 작업 결과 조회"""
    result = get_job_result(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다")
    return result.to_dict()

