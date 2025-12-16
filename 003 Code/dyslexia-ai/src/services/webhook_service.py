import json
import logging
from typing import Dict, Any, Optional
import httpx
import asyncio
from datetime import datetime

from src.services.job_manager import JobManager, JobResult, JobStatus

logger = logging.getLogger(__name__)


class WebhookService:
    """웹훅 서비스 클래스"""
    
    def __init__(self):
        self.job_manager = JobManager()
        self.timeout = 30  # 30초 타임아웃
        self.max_retry_attempts = 3
        self.retry_delay = 2  # 2초 대기
        
        logger.info("WebhookService 초기화 완료")
    
    async def send_completion_webhook(
        self,
        job_id: str,
        webhook_url: str,
        result_data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> bool:
        """작업 완료 웹훅 발송"""
        
        try:
            logger.info(f"작업 완료 웹훅 발송 시작: {job_id} -> {webhook_url}")
            
            # 웹훅 페이로드 생성
            webhook_payload = self._create_completion_payload(
                job_id, result_data, metadata
            )
            
            # 웹훅 발송 시도
            success = await self._send_webhook_with_retry(
                url=webhook_url,
                payload=webhook_payload,
                job_id=job_id
            )
            
            if success:
                logger.info(f"작업 완료 웹훅 발송 성공: {job_id}")
                
                # 작업 결과를 Redis에 저장
                self.job_manager.save_result(job_id, result_data, metadata)
                
            else:
                logger.error(f"작업 완료 웹훅 발송 실패: {job_id}")
                
                # 실패해도 결과는 저장
                self.job_manager.save_result(job_id, result_data, metadata)
            
            return success
            
        except Exception as e:
            logger.error(f"웹훅 발송 중 예상치 못한 오류 ({job_id}): {e}")
            
            # 오류 발생시에도 결과 저장
            try:
                self.job_manager.save_result(job_id, result_data, metadata)
            except Exception as save_error:
                logger.error(f"결과 저장 중 오류 ({job_id}): {save_error}")
            
            return False
    
    async def send_failure_webhook(
        self,
        job_id: str,
        webhook_url: str,
        error_message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """작업 실패 웹훅 발송"""
        
        try:
            logger.info(f"작업 실패 웹훅 발송 시작: {job_id} -> {webhook_url}")
            
            # 웹훅 페이로드 생성
            webhook_payload = self._create_failure_payload(
                job_id, error_message, metadata or {}
            )
            
            # 웹훅 발송 시도
            success = await self._send_webhook_with_retry(
                url=webhook_url,
                payload=webhook_payload,
                job_id=job_id
            )
            
            if success:
                logger.info(f"작업 실패 웹훅 발송 성공: {job_id}")
            else:
                logger.error(f"작업 실패 웹훅 발송 실패: {job_id}")
            
            # 작업을 실패로 마킹
            self.job_manager.mark_failed(job_id, error_message)
            
            return success
            
        except Exception as e:
            logger.error(f"실패 웹훅 발송 중 예상치 못한 오류 ({job_id}): {e}")
            
            # 오류 발생시에도 실패 마킹
            try:
                self.job_manager.mark_failed(job_id, error_message)
            except Exception as mark_error:
                logger.error(f"실패 마킹 중 오류 ({job_id}): {mark_error}")
            
            return False
    
    def _create_completion_payload(
        self,
        job_id: str,
        result_data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """완료 웹훅 페이로드 생성"""
        
        return {
            "event_type": "job_completed",
            "job_id": job_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "result": result_data,
                "metadata": metadata,
            },
            "message": "작업이 성공적으로 완료되었습니다."
        }
    
    def _create_failure_payload(
        self,
        job_id: str,
        error_message: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """실패 웹훅 페이로드 생성"""
        
        return {
            "event_type": "job_failed",
            "job_id": job_id,
            "status": "failed",
            "timestamp": datetime.now().isoformat(),
            "error": {
                "message": error_message,
                "metadata": metadata,
            },
            "message": "작업 처리 중 오류가 발생했습니다."
        }
    
    async def _send_webhook_with_retry(
        self,
        url: str,
        payload: Dict[str, Any],
        job_id: str
    ) -> bool:
        """재시도 로직이 포함된 웹훅 발송"""
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "DyslexiaAI-WebhookService/1.0",
            "X-Job-ID": job_id,
            "X-Event-Type": payload.get("event_type", "unknown"),
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retry_attempts):
                try:
                    logger.debug(f"웹훅 발송 시도 {attempt + 1}/{self.max_retry_attempts}: {job_id}")
                    
                    response = await client.post(
                        url=url,
                        json=payload,
                        headers=headers
                    )
                    
                    # 응답 상태 확인
                    if response.status_code in [200, 201, 202]:
                        logger.info(f"웹훅 발송 성공 ({attempt + 1}차 시도): {job_id} (상태: {response.status_code})")
                        return True
                    
                    else:
                        logger.warning(
                            f"웹훅 응답 오류 ({attempt + 1}차 시도): {job_id} "
                            f"(상태: {response.status_code}, 응답: {response.text[:200]})"
                        )
                        
                        # 4xx 오류는 재시도하지 않음
                        if 400 <= response.status_code < 500:
                            logger.error(f"클라이언트 오류로 인한 웹훅 발송 중단: {job_id}")
                            return False
                
                except httpx.TimeoutException:
                    logger.warning(f"웹훅 타임아웃 ({attempt + 1}차 시도): {job_id}")
                
                except httpx.ConnectError:
                    logger.warning(f"웹훅 연결 실패 ({attempt + 1}차 시도): {job_id}")
                
                except Exception as e:
                    logger.warning(f"웹훅 발송 오류 ({attempt + 1}차 시도): {job_id} - {str(e)}")
                
                # 마지막 시도가 아니면 대기
                if attempt < self.max_retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))  # 지수 백오프
        
        logger.error(f"모든 웹훅 발송 시도 실패: {job_id}")
        return False
    
    async def send_progress_webhook(
        self,
        job_id: str,
        webhook_url: str,
        progress_percentage: float,
        current_step: str,
        step_details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """진행률 웹훅 발송 (선택적)"""
        
        try:
            payload = {
                "event_type": "job_progress",
                "job_id": job_id,
                "status": "in_progress",
                "timestamp": datetime.now().isoformat(),
                "progress": {
                    "percentage": progress_percentage,
                    "current_step": current_step,
                    "step_details": step_details or {},
                },
                "message": f"작업 진행 중: {progress_percentage:.1f}% 완료"
            }
            
            # 단일 시도 (진행률 웹훅은 실패해도 큰 문제 없음)
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    url=webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Job-ID": job_id,
                        "X-Event-Type": "job_progress",
                    }
                )
                
                if response.status_code in [200, 201, 202]:
                    logger.debug(f"진행률 웹훅 발송 성공: {job_id} ({progress_percentage:.1f}%)")
                    return True
                else:
                    logger.debug(f"진행률 웹훅 발송 실패: {job_id} (상태: {response.status_code})")
                    return False
        
        except Exception as e:
            logger.debug(f"진행률 웹훅 발송 오류: {job_id} - {str(e)}")
            return False


# 전역 인스턴스
webhook_service = WebhookService()


# 헬퍼 함수들
async def send_completion_webhook(
    job_id: str,
    webhook_url: str,
    result_data: Dict[str, Any],
    metadata: Dict[str, Any]
) -> bool:
    """작업 완료 웹훅 발송 헬퍼 함수"""
    return await webhook_service.send_completion_webhook(
        job_id, webhook_url, result_data, metadata
    )


async def send_failure_webhook(
    job_id: str,
    webhook_url: str,
    error_message: str,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """작업 실패 웹훅 발송 헬퍼 함수"""
    return await webhook_service.send_failure_webhook(
        job_id, webhook_url, error_message, metadata
    )


async def send_progress_webhook(
    job_id: str,
    webhook_url: str,
    progress_percentage: float,
    current_step: str,
    step_details: Optional[Dict[str, Any]] = None
) -> bool:
    """진행률 웹훅 발송 헬퍼 함수"""
    return await webhook_service.send_progress_webhook(
        job_id, webhook_url, progress_percentage, current_step, step_details
    )