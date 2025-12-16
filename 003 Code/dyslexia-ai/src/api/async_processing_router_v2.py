"""
개선된 비동기 처리 라우터
"""
import asyncio
import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, File, HTTPException, UploadFile, Query
from pydantic import BaseModel

from src.services.async_job_processor import async_processor
from src.services.job_manager import (
    get_job_progress, get_job_result as get_job_result_from_manager,
    JobStatus, JobStep
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/async/v2", tags=["Async Processing V2"])

# 스레드 풀 실행기 (Redis 조회 비동기 처리용)
executor = ThreadPoolExecutor(max_workers=10)


class JobStatusResponse(BaseModel):
    """작업 상태 응답 모델"""
    job_id: str
    status: str
    current_step: str
    progress_percentage: float
    estimated_completion_time: Optional[str]
    error_message: Optional[str]
    step_details: dict


class JobResultResponse(BaseModel):
    """작업 결과 응답 모델"""
    job_id: str
    status: str
    filename: str
    created_at: str
    completed_at: Optional[str]
    processing_time: float
    result_data: dict
    metadata: dict
    error_message: Optional[str]


@router.post("/process-pdf")
async def start_async_pdf_processing(
    file: UploadFile = File(...),
    webhook_url: Optional[str] = Query(None, description="작업 완료 시 호출할 웹훅 URL"),
    model_name: str = Query("claude-sonnet-4-20250514", description="사용할 Claude 모델명"),
    max_concurrent: int = Query(8, description="최대 동시 요청 수"),
    remove_headers_footers: bool = Query(True, description="머리말/꼬리말 제거 여부"),
    header_height: float = Query(30.0, description="머리말 높이"),
    footer_height: float = Query(30.0, description="꼬리말 높이"),
    max_tokens: int = Query(12000, description="청크당 최대 토큰 수"),
    image_interval: int = Query(15, description="PAGE_IMAGE 생성 간격"),
    word_limit: int = Query(15, description="한 문장당 단어 수 제한"),
    vocabulary_interval: int = Query(1, description="vocabularyAnalysis 생성 간격"),
    enable_phoneme_analysis: bool = Query(True, description="음운분석 활성화 여부"),
    phoneme_max_concurrent: int = Query(3, description="음운분석 최대 동시 요청 수"),
    enable_block_word_phoneme_analysis: bool = Query(True, description="블록별 단어 음운분석 활성화 여부"),
    block_word_phoneme_max_concurrent: int = Query(3, description="블록별 단어 음운분석 최대 동시 요청 수"),
):
    """PDF 비동기 처리 시작 (개선된 버전)"""
    
    try:
        # 파일 검증
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="파일이 제공되지 않았습니다.")
        
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="PDF 파일만 지원됩니다.")
        
        # 처리 옵션 구성
        processing_options = {
            "model_name": model_name,
            "max_concurrent": max_concurrent,
            "remove_headers_footers": remove_headers_footers,
            "header_height": header_height,
            "footer_height": footer_height,
            "max_tokens": max_tokens,
            "image_interval": image_interval,
            "word_limit": word_limit,
            "vocabulary_interval": vocabulary_interval,
            "enable_phoneme_analysis": enable_phoneme_analysis,
            "phoneme_max_concurrent": phoneme_max_concurrent,
            "enable_block_word_phoneme_analysis": enable_block_word_phoneme_analysis,
            "block_word_phoneme_max_concurrent": block_word_phoneme_max_concurrent,
        }
        
        # 비동기 처리 시작
        job_id = await async_processor.start_processing(
            file=file,
            webhook_url=webhook_url,
            processing_options=processing_options
        )
        
        logger.info(f"비동기 PDF 처리 시작: {job_id} (파일: {file.filename})")
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "PDF 처리가 시작되었습니다. job_id로 진행상황을 확인할 수 있습니다.",
            "status_check_url": f"/async/v2/status/{job_id}",
            "result_url": f"/async/v2/result/{job_id}",
            "estimated_time": "5-10분 (파일 크기에 따라 변동)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"비동기 처리 시작 실패: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"비동기 처리 시작 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """작업 상태 조회 (개선된 버전)"""
    
    try:
        # Redis 조회를 비동기로 처리
        loop = asyncio.get_event_loop()
        progress = await loop.run_in_executor(executor, get_job_progress, job_id)
        
        if not progress:
            raise HTTPException(
                status_code=404, 
                detail=f"작업 {job_id}를 찾을 수 없습니다."
            )
        
        return JobStatusResponse(
            job_id=progress.job_id,
            status=progress.status.value,
            current_step=progress.current_step.value,
            progress_percentage=progress.progress_percentage,
            estimated_completion_time=progress.estimated_completion_time.isoformat() if progress.estimated_completion_time else None,
            error_message=progress.error_message,
            step_details=progress.step_details
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"작업 상태 조회 실패: {job_id} - {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"작업 상태 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/result/{job_id}", response_model=JobResultResponse)
async def get_job_result(job_id: str):
    """작업 결과 조회 (개선된 버전)"""
    
    try:
        # Redis 조회를 비동기로 처리
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, get_job_result_from_manager, job_id)
        
        if not result:
            # 진행 중인 작업인지 확인
            progress = await loop.run_in_executor(executor, get_job_progress, job_id)
            if progress:
                if progress.status == JobStatus.FAILED:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"작업 {job_id}가 실패했습니다: {progress.error_message}"
                    )
                else:
                    raise HTTPException(
                        status_code=202, 
                        detail=f"작업 {job_id}가 아직 진행 중입니다. (진행률: {progress.progress_percentage:.1f}%)"
                    )
            else:
                raise HTTPException(
                    status_code=404, 
                    detail=f"작업 {job_id}를 찾을 수 없습니다."
                )
        
        return JobResultResponse(
            job_id=result.job_id,
            status=result.status.value,
            filename=result.filename,
            created_at=result.created_at.isoformat(),
            completed_at=result.completed_at.isoformat() if result.completed_at else None,
            processing_time=result.processing_time,
            result_data=result.result_data,
            metadata=result.metadata,
            error_message=result.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"작업 결과 조회 실패: {job_id} - {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"작업 결과 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/active-jobs")
async def get_active_jobs():
    """활성 작업 목록 조회"""
    
    try:
        active_jobs = list(async_processor.active_jobs.keys())
        return {
            "active_jobs": active_jobs,
            "count": len(active_jobs)
        }
        
    except Exception as e:
        logger.error(f"활성 작업 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"활성 작업 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    """작업 취소"""
    
    try:
        if job_id not in async_processor.active_jobs:
            raise HTTPException(
                status_code=404, 
                detail=f"활성 작업 {job_id}를 찾을 수 없습니다."
            )
        
        task = async_processor.active_jobs[job_id]
        task.cancel()
        
        # 작업 목록에서 제거
        del async_processor.active_jobs[job_id]
        
        return {
            "success": True,
            "message": f"작업 {job_id}가 취소되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"작업 취소 실패: {job_id} - {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"작업 취소 중 오류가 발생했습니다: {str(e)}"
        )