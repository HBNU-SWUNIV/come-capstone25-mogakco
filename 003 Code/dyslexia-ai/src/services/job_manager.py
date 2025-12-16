import json
import logging
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

from src.services.redis_service import RedisService

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """작업 상태 열거형"""
    PENDING = "pending"          # 대기 중
    PREPROCESSING = "preprocessing"    # 전처리 중
    TRANSFORMING = "transforming"     # 변환 중
    GENERATING_IMAGES = "generating_images"  # 이미지 생성 중
    ANALYZING_PHONEMES = "analyzing_phonemes"  # 음운분석 중
    WEBHOOK_SENDING = "webhook_sending"  # 웹훅 발송 중
    COMPLETED = "completed"      # 완료
    FAILED = "failed"           # 실패


class JobStep(Enum):
    """작업 단계 열거형"""
    INITIALIZATION = "initialization"
    PDF_EXTRACTION = "pdf_extraction"
    TEXT_NORMALIZATION = "text_normalization"
    CHUNKING = "chunking"
    BLOCK_TRANSFORMATION = "block_transformation"
    IMAGE_GENERATION = "image_generation"
    PHONEME_ANALYSIS = "phoneme_analysis"
    BLOCK_WORD_PHONEME_ANALYSIS = "block_word_phoneme_analysis"
    FINAL_PROCESSING = "final_processing"
    WEBHOOK_NOTIFICATION = "webhook_notification"
    COMPLETED = "completed"


@dataclass
class JobProgress:
    """작업 진행률 데이터 클래스"""
    job_id: str
    status: JobStatus
    current_step: JobStep
    progress_percentage: float  # 0-100
    step_details: Dict[str, Any]  # 단계별 상세 정보
    total_steps: int
    current_step_index: int
    started_at: datetime
    updated_at: datetime
    estimated_completion_time: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "current_step": self.current_step.value,
            "progress_percentage": self.progress_percentage,
            "step_details": self.step_details,
            "total_steps": self.total_steps,
            "current_step_index": self.current_step_index,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "estimated_completion_time": self.estimated_completion_time.isoformat() if self.estimated_completion_time else None,
            "error_message": self.error_message,
        }


@dataclass
class JobResult:
    """작업 결과 데이터 클래스"""
    job_id: str
    status: JobStatus
    filename: str
    created_at: datetime
    completed_at: Optional[datetime]
    processing_time: float
    result_data: Dict[str, Any]
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "filename": self.filename,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "processing_time": self.processing_time,
            "result_data": self.result_data,
            "metadata": self.metadata,
            "error_message": self.error_message,
        }


class JobManager:
    """비동기 작업 관리자"""
    
    def __init__(self):
        self.redis_service = RedisService()
        self.job_progress_prefix = "job:progress:"
        self.job_result_prefix = "job:result:"
        self.job_expiry_hours = 24  # 24시간 후 만료
        
        # 작업 단계별 가중치 (진행률 계산용)
        self.step_weights = {
            JobStep.INITIALIZATION: 5,
            JobStep.PDF_EXTRACTION: 10,
            JobStep.TEXT_NORMALIZATION: 10,
            JobStep.CHUNKING: 10,
            JobStep.BLOCK_TRANSFORMATION: 30,
            JobStep.IMAGE_GENERATION: 20,
            JobStep.PHONEME_ANALYSIS: 10,
            JobStep.BLOCK_WORD_PHONEME_ANALYSIS: 3,
            JobStep.FINAL_PROCESSING: 1,
            JobStep.WEBHOOK_NOTIFICATION: 1,
            JobStep.COMPLETED: 0,
        }
        
        logger.info("JobManager 초기화 완료")
    
    def generate_job_id(self) -> str:
        """고유한 작업 ID 생성"""
        return f"job_{uuid.uuid4().hex[:16]}_{int(time.time())}"
    
    def create_job(self, filename: str, **metadata) -> str:
        """새 작업 생성"""
        job_id = self.generate_job_id()
        now = datetime.now()
        
        # 초기 진행률 설정
        progress = JobProgress(
            job_id=job_id,
            status=JobStatus.PENDING,
            current_step=JobStep.INITIALIZATION,
            progress_percentage=0.0,
            step_details={},
            total_steps=len(self.step_weights) - 1,  # COMPLETED 제외
            current_step_index=0,
            started_at=now,
            updated_at=now,
        )
        
        # Redis에 진행률 저장
        try:
            self.redis_service.redis_client.redis_client.setex(
                f"{self.job_progress_prefix}{job_id}",
                self.job_expiry_hours * 3600,
                json.dumps(progress.to_dict())
            )
            
            logger.info(f"작업 생성 완료: {job_id} (파일: {filename})")
            return job_id
            
        except Exception as e:
            logger.error(f"작업 생성 실패: {e}")
            raise Exception(f"작업 생성 중 오류 발생: {str(e)}")
    
    def update_progress(
        self,
        job_id: str,
        status: JobStatus,
        current_step: JobStep,
        step_details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """작업 진행률 업데이트"""
        try:
            # 기존 진행률 조회
            existing_progress = self.get_progress(job_id)
            if not existing_progress:
                logger.error(f"작업 {job_id}를 찾을 수 없습니다.")
                return False
            
            # 진행률 계산
            current_step_index = list(self.step_weights.keys()).index(current_step)
            progress_percentage = self._calculate_progress_percentage(current_step_index)
            
            # 예상 완료 시간 계산
            estimated_completion = self._estimate_completion_time(
                existing_progress.started_at,
                progress_percentage
            )
            
            # 진행률 업데이트
            updated_progress = JobProgress(
                job_id=job_id,
                status=status,
                current_step=current_step,
                progress_percentage=progress_percentage,
                step_details=step_details or {},
                total_steps=existing_progress.total_steps,
                current_step_index=current_step_index,
                started_at=existing_progress.started_at,
                updated_at=datetime.now(),
                estimated_completion_time=estimated_completion,
                error_message=error_message,
            )
            
            # Redis에 저장
            self.redis_service.redis_client.redis_client.setex(
                f"{self.job_progress_prefix}{job_id}",
                self.job_expiry_hours * 3600,
                json.dumps(updated_progress.to_dict())
            )
            
            logger.debug(f"작업 {job_id} 진행률 업데이트: {progress_percentage:.1f}% ({current_step.value})")
            return True
            
        except Exception as e:
            logger.error(f"진행률 업데이트 실패 ({job_id}): {e}")
            return False
    
    def get_progress(self, job_id: str) -> Optional[JobProgress]:
        """작업 진행률 조회"""
        try:
            redis_key = f"{self.job_progress_prefix}{job_id}"
            progress_data = self.redis_service.redis_client.redis_client.get(redis_key)
            
            if not progress_data:
                logger.warning(f"작업 {job_id}의 진행률 데이터를 찾을 수 없습니다.")
                return None
            
            # JSON 데이터 파싱
            progress_dict = json.loads(progress_data)
            
            # JobProgress 객체로 변환
            progress = JobProgress(
                job_id=progress_dict["job_id"],
                status=JobStatus(progress_dict["status"]),
                current_step=JobStep(progress_dict["current_step"]),
                progress_percentage=progress_dict["progress_percentage"],
                step_details=progress_dict["step_details"],
                total_steps=progress_dict["total_steps"],
                current_step_index=progress_dict["current_step_index"],
                started_at=datetime.fromisoformat(progress_dict["started_at"]),
                updated_at=datetime.fromisoformat(progress_dict["updated_at"]),
                estimated_completion_time=datetime.fromisoformat(progress_dict["estimated_completion_time"]) if progress_dict["estimated_completion_time"] else None,
                error_message=progress_dict.get("error_message"),
            )
            
            return progress
            
        except Exception as e:
            logger.error(f"진행률 조회 실패 ({job_id}): {e}")
            return None
    
    def save_result(self, job_id: str, result_data: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """작업 결과 저장"""
        try:
            # 기존 진행률 조회
            progress = self.get_progress(job_id)
            if not progress:
                logger.error(f"작업 {job_id}를 찾을 수 없습니다.")
                return False
            
            # 결과 데이터 생성
            now = datetime.now()
            processing_time = (now - progress.started_at).total_seconds()
            
            job_result = JobResult(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                filename=metadata.get("filename", "unknown"),
                created_at=progress.started_at,
                completed_at=now,
                processing_time=processing_time,
                result_data=result_data,
                metadata=metadata,
            )
            
            # Redis에 결과 저장
            self.redis_service.redis_client.redis_client.setex(
                f"{self.job_result_prefix}{job_id}",
                self.job_expiry_hours * 3600,
                json.dumps(job_result.to_dict())
            )
            
            # 진행률을 완료로 업데이트
            self.update_progress(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                current_step=JobStep.COMPLETED,
                step_details={"completed_at": now.isoformat()}
            )
            
            logger.info(f"작업 결과 저장 완료: {job_id} ({processing_time:.2f}초)")
            return True
            
        except Exception as e:
            logger.error(f"작업 결과 저장 실패 ({job_id}): {e}")
            return False
    
    def get_result(self, job_id: str) -> Optional[JobResult]:
        """작업 결과 조회"""
        try:
            redis_key = f"{self.job_result_prefix}{job_id}"
            result_data = self.redis_service.redis_client.redis_client.get(redis_key)
            
            if not result_data:
                logger.warning(f"작업 {job_id}의 결과 데이터를 찾을 수 없습니다.")
                return None
            
            # JSON 데이터 파싱
            result_dict = json.loads(result_data)
            
            # JobResult 객체로 변환
            job_result = JobResult(
                job_id=result_dict["job_id"],
                status=JobStatus(result_dict["status"]),
                filename=result_dict["filename"],
                created_at=datetime.fromisoformat(result_dict["created_at"]),
                completed_at=datetime.fromisoformat(result_dict["completed_at"]) if result_dict["completed_at"] else None,
                processing_time=result_dict["processing_time"],
                result_data=result_dict["result_data"],
                metadata=result_dict["metadata"],
                error_message=result_dict.get("error_message"),
            )
            
            return job_result
            
        except Exception as e:
            logger.error(f"작업 결과 조회 실패 ({job_id}): {e}")
            return None
    
    def mark_failed(self, job_id: str, error_message: str) -> bool:
        """작업 실패 처리"""
        try:
            # 진행률을 실패로 업데이트
            success = self.update_progress(
                job_id=job_id,
                status=JobStatus.FAILED,
                current_step=JobStep.COMPLETED,
                error_message=error_message
            )
            
            if success:
                logger.error(f"작업 {job_id} 실패 처리 완료: {error_message}")
            else:
                logger.error(f"작업 {job_id} 실패 처리 중 오류 발생")
                
            return success
            
        except Exception as e:
            logger.error(f"작업 실패 처리 오류 ({job_id}): {e}")
            return False
    
    def _calculate_progress_percentage(self, current_step_index: int) -> float:
        """진행률 계산"""
        if current_step_index >= len(self.step_weights) - 1:
            return 100.0
        
        # 완료된 단계들의 가중치 합계
        completed_weight = sum(
            weight for i, (step, weight) in enumerate(self.step_weights.items())
            if i < current_step_index
        )
        
        # 전체 가중치 합계 (COMPLETED 제외)
        total_weight = sum(
            weight for step, weight in self.step_weights.items()
            if step != JobStep.COMPLETED
        )
        
        return min(100.0, (completed_weight / total_weight) * 100)
    
    def _estimate_completion_time(self, started_at: datetime, progress_percentage: float) -> Optional[datetime]:
        """예상 완료 시간 계산"""
        if progress_percentage <= 0:
            return None
        
        elapsed_time = (datetime.now() - started_at).total_seconds()
        estimated_total_time = elapsed_time / (progress_percentage / 100)
        remaining_time = estimated_total_time - elapsed_time
        
        if remaining_time > 0:
            from datetime import timedelta
            return datetime.now() + timedelta(seconds=remaining_time)
        
        return None
    
    def cleanup_expired_jobs(self) -> int:
        """만료된 작업 정리"""
        try:
            # Redis에서 만료된 키들은 자동으로 삭제되므로
            # 여기서는 추가적인 정리 작업을 수행할 수 있음
            logger.info("만료된 작업 정리 실행")
            return 0
            
        except Exception as e:
            logger.error(f"만료된 작업 정리 중 오류 발생: {e}")
            return 0


# 전역 인스턴스
job_manager = JobManager()


# 헬퍼 함수들
def create_job(filename: str, **metadata) -> str:
    """새 작업 생성 헬퍼 함수"""
    return job_manager.create_job(filename, **metadata)


def update_job_progress(
    job_id: str,
    status: JobStatus,
    current_step: JobStep,
    step_details: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None
) -> bool:
    """작업 진행률 업데이트 헬퍼 함수"""
    return job_manager.update_progress(job_id, status, current_step, step_details, error_message)


def get_job_progress(job_id: str) -> Optional[JobProgress]:
    """작업 진행률 조회 헬퍼 함수"""
    return job_manager.get_progress(job_id)


def save_job_result(job_id: str, result_data: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
    """작업 결과 저장 헬퍼 함수"""
    return job_manager.save_result(job_id, result_data, metadata)


def get_job_result(job_id: str) -> Optional[JobResult]:
    """작업 결과 조회 헬퍼 함수"""
    return job_manager.get_result(job_id)


def mark_job_failed(job_id: str, error_message: str) -> bool:
    """작업 실패 처리 헬퍼 함수"""
    return job_manager.mark_failed(job_id, error_message)