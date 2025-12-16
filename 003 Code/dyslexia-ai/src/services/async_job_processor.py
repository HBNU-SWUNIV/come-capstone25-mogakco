"""
개선된 비동기 작업 처리 서비스
"""
import asyncio
import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from fastapi import UploadFile

from src.services.job_manager import JobManager, JobStatus, JobStep, update_job_progress
from src.services.orchestration_service import ProcessingOrchestrator, OrchestrationOptions
from src.services.webhook_service import send_completion_webhook, send_failure_webhook

logger = logging.getLogger(__name__)


class ProcessingStage(Enum):
    """처리 단계 (진행률 계산용)"""
    INITIALIZATION = (0, 5, "초기화")
    PDF_EXTRACTION = (5, 20, "PDF 텍스트 추출")
    TEXT_PROCESSING = (20, 30, "텍스트 정규화 및 청킹")
    BLOCK_TRANSFORMATION = (30, 60, "블록 변환")
    IMAGE_GENERATION = (60, 75, "이미지 생성")
    PHONEME_ANALYSIS = (75, 90, "음운분석")
    FINAL_PROCESSING = (90, 100, "최종 처리")
    
    def __init__(self, start_percent: float, end_percent: float, description: str):
        self.start_percent = start_percent
        self.end_percent = end_percent
        self.description = description


@dataclass
class ProcessingContext:
    """처리 컨텍스트"""
    job_id: str
    filename: str
    webhook_url: Optional[str]
    processing_options: Dict[str, Any]
    file_path: str
    start_time: float
    

class AsyncJobProcessor:
    """비동기 작업 처리기"""
    
    def __init__(self):
        self.job_manager = JobManager()
        self.active_jobs: Dict[str, asyncio.Task] = {}
        
    async def start_processing(
        self,
        file: UploadFile,
        webhook_url: Optional[str],
        processing_options: Dict[str, Any]
    ) -> str:
        """비동기 처리 시작"""
        
        # 1. 작업 생성
        job_id = self.job_manager.create_job(
            filename=file.filename,
            webhook_url=webhook_url,
            **processing_options
        )
        
        # 2. 임시 파일 저장
        import tempfile
        import os
        
        temp_dir = "./temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_file_path = os.path.join(temp_dir, f"{job_id}_{file.filename}")
        
        file_content = await file.read()
        with open(temp_file_path, 'wb') as f:
            f.write(file_content)
            
        # 3. 처리 컨텍스트 생성
        context = ProcessingContext(
            job_id=job_id,
            filename=file.filename,
            webhook_url=webhook_url,
            processing_options=processing_options,
            file_path=temp_file_path,
            start_time=time.time()
        )
        
        # 4. 백그라운드 태스크 시작
        task = asyncio.create_task(self._process_pipeline(context))
        self.active_jobs[job_id] = task
        
        logger.info(f"비동기 처리 시작: {job_id} (파일: {file.filename})")
        return job_id
    
    async def _process_pipeline(self, context: ProcessingContext):
        """파이프라인 처리 (백그라운드 태스크)"""
        
        try:
            # 초기화
            await self._update_stage_progress(context, ProcessingStage.INITIALIZATION, 0)
            
            # 파일 객체 생성
            with open(context.file_path, 'rb') as f:
                file_content = f.read()
            
            from io import BytesIO
            from fastapi import UploadFile
            
            fake_file = UploadFile(
                file=BytesIO(file_content),
                filename=context.filename,
                size=len(file_content)
            )
            
            # 오케스트레이션 옵션 설정
            options = OrchestrationOptions(
                job_id=context.job_id,
                model_name=context.processing_options.get("model_name", "claude-sonnet-4-20250514"),
                max_concurrent=context.processing_options.get("max_concurrent", 8),
                temp_dir=context.processing_options.get("temp_dir", "./temp"),
                remove_headers_footers=context.processing_options.get("remove_headers_footers", True),
                header_height=context.processing_options.get("header_height", 30.0),
                footer_height=context.processing_options.get("footer_height", 30.0),
                max_tokens=context.processing_options.get("max_tokens", 12000),
                image_interval=context.processing_options.get("image_interval", 15),
                word_limit=context.processing_options.get("word_limit", 15),
                vocabulary_interval=context.processing_options.get("vocabulary_interval", 1),
                enable_phoneme_analysis=context.processing_options.get("enable_phoneme_analysis", True),
                phoneme_max_concurrent=context.processing_options.get("phoneme_max_concurrent", 3),
                enable_block_word_phoneme_analysis=context.processing_options.get("enable_block_word_phoneme_analysis", True),
                block_word_phoneme_max_concurrent=context.processing_options.get("block_word_phoneme_max_concurrent", 3),
            )
            
            # 단계별 처리
            await self._execute_pdf_extraction(context, fake_file, options)
            await self._execute_block_transformation(context, fake_file, options)
            await self._execute_image_generation(context)
            await self._execute_phoneme_analysis(context)
            await self._execute_final_processing(context)
            
            # 완료 처리
            await self._handle_completion(context)
            
        except Exception as e:
            logger.error(f"파이프라인 처리 실패: {context.job_id} - {e}", exc_info=True)
            await self._handle_failure(context, str(e))
            
        finally:
            # 정리
            await self._cleanup(context)
    
    async def _update_stage_progress(
        self, 
        context: ProcessingContext, 
        stage: ProcessingStage, 
        stage_progress: float
    ):
        """단계별 진행률 업데이트"""
        
        # 단계 내 진행률 (0-100)
        stage_progress = max(0, min(100, stage_progress))
        
        # 전체 진행률 계산
        total_progress = stage.start_percent + (stage.end_percent - stage.start_percent) * (stage_progress / 100)
        
        # 진행률 업데이트 (JobManager의 step_weights 무시하고 직접 설정)
        self._update_job_progress_direct(
            context.job_id,
            self._get_job_status(stage),
            self._get_job_step(stage),
            total_progress,
            {
                "stage": stage.name,
                "stage_description": stage.description,
                "stage_progress": stage_progress,
                "total_progress": total_progress,
                "message": f"{stage.description} ({stage_progress:.1f}%)"
            }
        )
        
        logger.info(f"진행률 업데이트 [{context.job_id}]: {stage.description} {stage_progress:.1f}% (전체: {total_progress:.1f}%)")
    
    def _update_job_progress_direct(
        self,
        job_id: str,
        status: JobStatus,
        current_step: JobStep,
        progress_percentage: float,
        step_details: dict
    ):
        """JobManager의 step_weights를 무시하고 직접 진행률 설정"""
        
        try:
            from datetime import datetime
            import json
            
            # 기존 진행률 조회
            existing_progress = self.job_manager.get_progress(job_id)
            if not existing_progress:
                logger.error(f"작업 {job_id}를 찾을 수 없습니다.")
                return False
            
            # 진행률 직접 설정
            from src.services.job_manager import JobProgress
            updated_progress = JobProgress(
                job_id=job_id,
                status=status,
                current_step=current_step,
                progress_percentage=progress_percentage,
                step_details=step_details,
                total_steps=existing_progress.total_steps,
                current_step_index=existing_progress.current_step_index,
                started_at=existing_progress.started_at,
                updated_at=datetime.now(),
                estimated_completion_time=self._estimate_completion_time_direct(existing_progress.started_at, progress_percentage),
                error_message=None,
            )
            
            # Redis에 직접 저장
            self.job_manager.redis_service.redis_client.redis_client.setex(
                f"{self.job_manager.job_progress_prefix}{job_id}",
                self.job_manager.job_expiry_hours * 3600,
                json.dumps(updated_progress.to_dict())
            )
            
            logger.debug(f"직접 진행률 업데이트: {job_id} - {progress_percentage:.1f}%")
            return True
            
        except Exception as e:
            logger.error(f"직접 진행률 업데이트 실패 ({job_id}): {e}")
            return False
    
    def _estimate_completion_time_direct(self, started_at, progress_percentage):
        """예상 완료 시간 계산"""
        if progress_percentage <= 0:
            return None
        
        from datetime import datetime, timedelta
        elapsed_time = (datetime.now() - started_at).total_seconds()
        estimated_total_time = elapsed_time / (progress_percentage / 100)
        remaining_time = estimated_total_time - elapsed_time
        
        if remaining_time > 0:
            return datetime.now() + timedelta(seconds=remaining_time)
        
        return None
    
    def _get_job_status(self, stage: ProcessingStage) -> JobStatus:
        """단계에 따른 JobStatus 반환"""
        status_map = {
            ProcessingStage.INITIALIZATION: JobStatus.PENDING,
            ProcessingStage.PDF_EXTRACTION: JobStatus.PREPROCESSING,
            ProcessingStage.TEXT_PROCESSING: JobStatus.PREPROCESSING,
            ProcessingStage.BLOCK_TRANSFORMATION: JobStatus.TRANSFORMING,
            ProcessingStage.IMAGE_GENERATION: JobStatus.GENERATING_IMAGES,
            ProcessingStage.PHONEME_ANALYSIS: JobStatus.ANALYZING_PHONEMES,
            ProcessingStage.FINAL_PROCESSING: JobStatus.TRANSFORMING,
        }
        return status_map.get(stage, JobStatus.PREPROCESSING)
    
    def _get_job_step(self, stage: ProcessingStage) -> JobStep:
        """단계에 따른 JobStep 반환"""
        step_map = {
            ProcessingStage.INITIALIZATION: JobStep.INITIALIZATION,
            ProcessingStage.PDF_EXTRACTION: JobStep.PDF_EXTRACTION,
            ProcessingStage.TEXT_PROCESSING: JobStep.CHUNKING,
            ProcessingStage.BLOCK_TRANSFORMATION: JobStep.BLOCK_TRANSFORMATION,
            ProcessingStage.IMAGE_GENERATION: JobStep.IMAGE_GENERATION,
            ProcessingStage.PHONEME_ANALYSIS: JobStep.PHONEME_ANALYSIS,
            ProcessingStage.FINAL_PROCESSING: JobStep.FINAL_PROCESSING,
        }
        return step_map.get(stage, JobStep.PDF_EXTRACTION)
    
    async def _execute_pdf_extraction(self, context: ProcessingContext, file: UploadFile, options: OrchestrationOptions):
        """PDF 추출 단계"""
        await self._update_stage_progress(context, ProcessingStage.PDF_EXTRACTION, 0)
        
        # 실제로는 전체 파이프라인을 한 번에 실행
        logger.info(f"전체 파이프라인 실행 시작: {context.job_id}")
        orchestrator = ProcessingOrchestrator()
        
        # 전체 파이프라인 실행
        result = await orchestrator.execute_complete_pipeline(file, options)
        
        if not result.get("success"):
            raise Exception(f"파이프라인 실패: {result.get('error', 'Unknown error')}")
        
        # 처리 결과 저장
        context.pipeline_result = result
        logger.info(f"전체 파이프라인 실행 완료: {context.job_id}")
        
        await self._update_stage_progress(context, ProcessingStage.PDF_EXTRACTION, 100)
    
    async def _execute_block_transformation(self, context: ProcessingContext, file: UploadFile, options: OrchestrationOptions):
        """블록 변환 단계 (이미 완료됨)"""
        await self._update_stage_progress(context, ProcessingStage.BLOCK_TRANSFORMATION, 0)
        
        # 파이프라인에서 이미 처리됨
        await self._update_stage_progress(context, ProcessingStage.BLOCK_TRANSFORMATION, 100)
    
    async def _execute_image_generation(self, context: ProcessingContext):
        """이미지 생성 단계"""
        await self._update_stage_progress(context, ProcessingStage.IMAGE_GENERATION, 0)
        
        # 이미지 생성은 블록 변환에서 이미 처리됨
        await self._update_stage_progress(context, ProcessingStage.IMAGE_GENERATION, 100)
    
    async def _execute_phoneme_analysis(self, context: ProcessingContext):
        """음운분석 단계"""
        await self._update_stage_progress(context, ProcessingStage.PHONEME_ANALYSIS, 0)
        
        # 음운분석은 선택사항이므로 일단 스킵
        await self._update_stage_progress(context, ProcessingStage.PHONEME_ANALYSIS, 100)
    
    async def _execute_final_processing(self, context: ProcessingContext):
        """최종 처리 단계"""
        await self._update_stage_progress(context, ProcessingStage.FINAL_PROCESSING, 0)
        
        # 파이프라인 결과에서 최종 결과 추출
        context.final_result = context.pipeline_result.get("data", {})
        
        await self._update_stage_progress(context, ProcessingStage.FINAL_PROCESSING, 100)
    
    async def _handle_completion(self, context: ProcessingContext):
        """완료 처리"""
        
        # 결과 저장
        metadata = {
            "filename": context.filename,
            "processing_options": context.processing_options,
            "pipeline_metadata": context.final_result.get("metadata", {}),
        }
        
        if context.webhook_url:
            # 웹훅 발송
            update_job_progress(
                job_id=context.job_id,
                status=JobStatus.WEBHOOK_SENDING,
                current_step=JobStep.WEBHOOK_NOTIFICATION,
                step_details={"message": "완료 알림 발송 중"}
            )
            
            await send_completion_webhook(
                job_id=context.job_id,
                webhook_url=context.webhook_url,
                result_data=context.final_result,
                metadata=metadata
            )
        else:
            # 결과만 저장
            self.job_manager.save_result(context.job_id, context.final_result, metadata)
            
            update_job_progress(
                job_id=context.job_id,
                status=JobStatus.COMPLETED,
                current_step=JobStep.COMPLETED,
                step_details={"message": "작업 완료"}
            )
        
        logger.info(f"파이프라인 완료: {context.job_id}")
    
    async def _handle_failure(self, context: ProcessingContext, error_message: str):
        """실패 처리"""
        
        if context.webhook_url:
            await send_failure_webhook(
                job_id=context.job_id,
                webhook_url=context.webhook_url,
                error_message=error_message,
                metadata={"filename": context.filename, "processing_options": context.processing_options}
            )
        else:
            from src.services.job_manager import mark_job_failed
            mark_job_failed(context.job_id, error_message)
    
    async def _cleanup(self, context: ProcessingContext):
        """정리 작업"""
        
        # 임시 파일 삭제
        try:
            import os
            if os.path.exists(context.file_path):
                os.unlink(context.file_path)
                logger.debug(f"임시 파일 삭제: {context.file_path}")
        except Exception as e:
            logger.warning(f"임시 파일 삭제 실패: {e}")
        
        # 활성 작업 목록에서 제거
        if context.job_id in self.active_jobs:
            del self.active_jobs[context.job_id]


# 글로벌 인스턴스
async_processor = AsyncJobProcessor()