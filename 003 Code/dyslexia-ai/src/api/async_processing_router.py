import asyncio
import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, File, HTTPException, UploadFile, Query
from pydantic import BaseModel

from src.services.job_manager import (
    create_job, get_job_progress, get_job_result as get_job_result_from_manager, mark_job_failed,
    JobStatus, JobStep, update_job_progress
)
from src.services.webhook_service import send_completion_webhook, send_failure_webhook
from src.services.orchestration_service import execute_complete_pipeline, OrchestrationOptions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/async", tags=["Async Processing"])

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


async def process_pdf_pipeline_async(
    job_id: str,
    file_path: str,
    filename: str,
    webhook_url: Optional[str],
    processing_options: dict
):
    """비동기 PDF 처리 파이프라인"""
    
    try:
        logger.info(f"비동기 파이프라인 시작: {job_id} (파일: {filename})")
        
        # 1. 초기화 단계
        update_job_progress(
            job_id=job_id,
            status=JobStatus.PREPROCESSING,
            current_step=JobStep.INITIALIZATION,
            step_details={"message": "파이프라인 초기화 중"}
        )
        
        # 파일 읽기
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # UploadFile 객체 생성 (orchestration_service 호환)
        from io import BytesIO
        from fastapi import UploadFile
        
        fake_file = UploadFile(
            file=BytesIO(file_content),
            filename=filename,
            size=len(file_content)
        )
        
        # 2. 전처리 시작
        update_job_progress(
            job_id=job_id,
            status=JobStatus.PREPROCESSING,
            current_step=JobStep.PDF_EXTRACTION,
            step_details={"message": "PDF 텍스트 추출 시작"}
        )
        
        # 3. 오케스트레이션 옵션 설정
        options = OrchestrationOptions(
            job_id=job_id,  # 진행률 업데이트를 위한 job_id 전달
            model_name=processing_options.get("model_name", "claude-sonnet-4-20250514"),
            max_concurrent=processing_options.get("max_concurrent", 8),
            temp_dir=processing_options.get("temp_dir", "./temp"),
            remove_headers_footers=processing_options.get("remove_headers_footers", True),
            header_height=processing_options.get("header_height", 30.0),
            footer_height=processing_options.get("footer_height", 30.0),
            max_tokens=processing_options.get("max_tokens", 12000),
            image_interval=processing_options.get("image_interval", 15),
            word_limit=processing_options.get("word_limit", 15),
            vocabulary_interval=processing_options.get("vocabulary_interval", 1),
            enable_phoneme_analysis=processing_options.get("enable_phoneme_analysis", True),
            phoneme_max_concurrent=processing_options.get("phoneme_max_concurrent", 3),
            enable_block_word_phoneme_analysis=processing_options.get("enable_block_word_phoneme_analysis", True),
            block_word_phoneme_max_concurrent=processing_options.get("block_word_phoneme_max_concurrent", 3),
        )
        
        # 4. 실제 파이프라인 실행 시작 (job_id가 포함된 options 사용)
        logger.info(f"오케스트레이터 파이프라인 실행 시작: {job_id}")
        from src.services.orchestration_service import ProcessingOrchestrator
        orchestrator = ProcessingOrchestrator()
        
        try:
            result = await orchestrator.execute_complete_pipeline(fake_file, options)
            logger.info(f"오케스트레이터 파이프라인 완료: {job_id} - 성공: {result.get('success', False)}")
        except Exception as e:
            logger.error(f"오케스트레이터 파이프라인 실행 중 오류: {job_id} - {e}")
            raise
        
        # 8. 최종 처리
        update_job_progress(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            current_step=JobStep.FINAL_PROCESSING,
            step_details={"message": "최종 처리 중"}
        )
        
        # 9. 결과 확인
        if result.get("success"):
            logger.info(f"파이프라인 완료: {job_id}")
            
            # 메타데이터 준비
            metadata = {
                "filename": filename,
                "processing_options": processing_options,
                "pipeline_metadata": result.get("metadata", {}),
            }
            
            # 10. 웹훅 발송
            if webhook_url:
                update_job_progress(
                    job_id=job_id,
                    status=JobStatus.WEBHOOK_SENDING,
                    current_step=JobStep.WEBHOOK_NOTIFICATION,
                    step_details={"message": "완료 알림 발송 중"}
                )
                
                await send_completion_webhook(
                    job_id=job_id,
                    webhook_url=webhook_url,
                    result_data=result.get("data", {}),
                    metadata=metadata
                )
            else:
                # 웹훅 없이 결과만 저장
                from src.services.job_manager import job_manager
                job_manager.save_result(job_id, result.get("data", {}), metadata)
                
                update_job_progress(
                    job_id=job_id,
                    status=JobStatus.COMPLETED,
                    current_step=JobStep.COMPLETED,
                    step_details={"message": "작업 완료"}
                )
            
        else:
            # 파이프라인 실패
            error_message = result.get("error", "Unknown pipeline error")
            logger.error(f"파이프라인 실패: {job_id} - {error_message}")
            
            if webhook_url:
                await send_failure_webhook(
                    job_id=job_id,
                    webhook_url=webhook_url,
                    error_message=error_message,
                    metadata={"filename": filename, "processing_options": processing_options}
                )
            else:
                mark_job_failed(job_id, error_message)
                
    except Exception as e:
        error_message = f"비동기 처리 중 오류 발생: {str(e)}"
        logger.error(f"파이프라인 오류: {job_id} - {error_message}")
        logger.error(f"파이프라인 오류 스택 트레이스: {job_id}", exc_info=True)
        
        if webhook_url:
            await send_failure_webhook(
                job_id=job_id,
                webhook_url=webhook_url,
                error_message=error_message,
                metadata={"filename": filename, "processing_options": processing_options}
            )
        else:
            mark_job_failed(job_id, error_message)
    
    finally:
        # 임시 파일 정리
        try:
            import os
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.debug(f"임시 파일 삭제: {file_path}")
        except Exception as e:
            logger.warning(f"임시 파일 삭제 실패: {e}")


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
    """PDF 비동기 처리 시작"""
    
    try:
        # 파일 검증
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="파일이 제공되지 않았습니다.")
        
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="PDF 파일만 지원됩니다.")
        
        # 작업 생성
        job_id = create_job(
            filename=file.filename,
            webhook_url=webhook_url,
            model_name=model_name,
            max_concurrent=max_concurrent
        )
        
        # 임시 파일 저장
        import tempfile
        import os
        
        temp_dir = "./temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_file_path = os.path.join(temp_dir, f"{job_id}_{file.filename}")
        
        # 파일 내용 저장
        file_content = await file.read()
        with open(temp_file_path, 'wb') as f:
            f.write(file_content)
        
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
        
        # 백그라운드 작업 추가 (asyncio.create_task 사용)
        asyncio.create_task(
            process_pdf_pipeline_async(
                job_id,
                temp_file_path,
                file.filename,
                webhook_url,
                processing_options
            )
        )
        
        logger.info(f"비동기 PDF 처리 시작: {job_id} (파일: {file.filename})")
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "PDF 처리가 시작되었습니다. job_id로 진행상황을 확인할 수 있습니다.",
            "status_check_url": f"/async/status/{job_id}",
            "result_url": f"/async/result/{job_id}",
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
    """작업 상태 조회"""
    
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
    """작업 결과 조회"""
    
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