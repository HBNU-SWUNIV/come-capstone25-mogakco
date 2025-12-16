"""
Redis Pub/Sub 서비스
PRD 명세에 따른 Spring 서버와의 비동기 통신
"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

import redis.asyncio as redis
import os
from ..utils.env_config import get_redis_config

logger = logging.getLogger(__name__)


class RedisPubSubService:
    """Redis Pub/Sub 통신 서비스"""

    def __init__(self):
        self.config = get_redis_config()
        self.redis_client: Optional[redis.Redis] = None

        # PRD 명세에 따른 채널명 (환경변수에서 가져오거나 기본값 사용)
        self.progress_channel = os.getenv("REDIS_PROGRESS_CHANNEL", "progress-channel")
        self.result_channel = os.getenv("REDIS_RESULT_CHANNEL", "result-channel")
        self.failure_channel = os.getenv("REDIS_FAILURE_CHANNEL", "failure-channel")

        logger.info(f"Redis Pub/Sub 서비스 초기화: {self.config}")
        logger.info(f"채널 설정 - Progress: {self.progress_channel}, Result: {self.result_channel}, Failure: {self.failure_channel}")

    async def connect(self):
        """Redis 연결 설정"""
        if self.redis_client is None:
            try:
                self.redis_client = redis.Redis(
                    host=self.config['host'],
                    port=self.config['port'],
                    password=self.config.get('password'),
                    decode_responses=True
                )

                # 연결 테스트
                await self.redis_client.ping()
                logger.info("Redis Pub/Sub 연결 성공")

            except Exception as e:
                logger.error(f"Redis Pub/Sub 연결 실패: {e}")
                raise

    async def disconnect(self):
        """Redis 연결 해제"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            logger.info("Redis Pub/Sub 연결 해제")

    async def publish_progress(self, job_id: str, progress: float):
        """
        진행률 메시지 발송 (PRD 4.3)

        채널: progress-channel
        형식: {"jobId": "...", "progress": ...}
        """
        await self.connect()

        try:
            message = {
                "jobId": job_id,
                "progress": progress,
                "timestamp": datetime.utcnow().isoformat()
            }

            await self.redis_client.publish(
                self.progress_channel,
                json.dumps(message)
            )

            logger.info(f"진행률 메시지 발송: job_id={job_id}, progress={progress}%")

        except Exception as e:
            logger.error(f"진행률 메시지 발송 실패: job_id={job_id}, error={str(e)}")
            raise

    async def publish_result(self, job_id: str, s3_url: str):
        """
        결과 메시지 발송 (PRD 4.3)

        채널: result-channel
        형식: {"jobId": "...", "s3_url": "..."}
        """
        await self.connect()

        try:
            message = {
                "jobId": job_id,
                "s3_url": s3_url,
                "timestamp": datetime.utcnow().isoformat()
            }

            await self.redis_client.publish(
                self.result_channel,
                json.dumps(message)
            )

            logger.info(f"결과 메시지 발송: job_id={job_id}, s3_url={s3_url}")

        except Exception as e:
            logger.error(f"결과 메시지 발송 실패: job_id={job_id}, error={str(e)}")
            raise

    async def publish_failure(self, job_id: str, error_message: str):
        """
        실패 메시지 발송 (PRD 4.3)

        채널: failure-channel
        형식: {"jobId": "...", "error": "..."}
        """
        await self.connect()

        try:
            # Spring FailureMessageDto(jobId, error)와 정확히 맞춤 (timestamp 제거)
            message = {
                "jobId": job_id,
                "error": error_message,
            }

            await self.redis_client.publish(
                self.failure_channel,
                json.dumps(message)
            )

            logger.info(f"실패 메시지 발송: job_id={job_id}, error={error_message}")

        except Exception as e:
            logger.error(f"실패 메시지 발송 실패: job_id={job_id}, error={str(e)}")
            raise

    async def health_check(self) -> bool:
        """Redis Pub/Sub 연결 상태 확인"""
        try:
            await self.connect()
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis Pub/Sub 헬스 체크 실패: {e}")
            return False

    async def health_check_with_pubsub(self) -> (bool, str):
        """실제 Pub/Sub 발행/수신을 테스트하는 헬스 체크"""
        try:
            await self.connect()

            test_channel = os.getenv("REDIS_HEALTHCHECK_CHANNEL", "health-check-channel")
            test_message = f"health-check-{datetime.utcnow().isoformat()}"

            async with self.redis_client.pubsub() as pubsub:
                await pubsub.subscribe(test_channel)

                # 테스트 메시지 발행
                await self.redis_client.publish(test_channel, test_message)

                # 메시지 수신 대기 (최대 2초, 폴링)
                deadline = asyncio.get_running_loop().time() + 2.0
                while asyncio.get_running_loop().time() < deadline:
                    try:
                        message = await pubsub.get_message(
                            ignore_subscribe_messages=True, timeout=0.5
                        )
                    except TypeError:
                        # 일부 버전은 timeout 파라미터 미지원 -> 대기 후 재시도
                        await asyncio.sleep(0.5)
                        message = await pubsub.get_message(
                            ignore_subscribe_messages=True
                        )

                    if message and message.get("data") == test_message:
                        logger.info("Redis Pub/Sub 헬스 체크 성공: 발행/수신 동작 확인")
                        return True, "Redis Pub/Sub is healthy and operational."

                logger.warning("Redis Pub/Sub 헬스 체크 실패: 메시지 수신 실패")
                return False, "Failed to receive correct message on test channel."

        except Exception as e:
            logger.error(f"Redis Pub/Sub 헬스 체크 중 예외 발생: {e}", exc_info=True)
            return False, f"An exception occurred during health check: {e}"

    async def publish_step_progress(self, job_id: str, step_name: str, progress: float):
        """
        단계별 진행률 발송

        Args:
            job_id: 작업 ID
            step_name: 단계명 (PDF_PREPROCESSING, TRANSFORMATION, etc.)
            progress: 진행률 (0-100)
        """
        await self.connect()

        try:
            message = {
                "jobId": job_id,
                "progress": progress,
                "step": step_name,
                "timestamp": datetime.utcnow().isoformat()
            }

            await self.redis_client.publish(
                self.progress_channel,
                json.dumps(message)
            )

            logger.info(f"단계별 진행률 발송: job_id={job_id}, step={step_name}, progress={progress}%")

        except Exception as e:
            logger.error(f"단계별 진행률 발송 실패: job_id={job_id}, error={str(e)}")
            raise


# 전역 인스턴스
pub_sub_service = RedisPubSubService()


async def publish_progress(job_id: str, progress: float):
    """헬퍼 함수: 진행률 발송"""
    await pub_sub_service.publish_progress(job_id, progress)


async def publish_result(job_id: str, s3_url: str):
    """헬퍼 함수: 결과 발송"""
    await pub_sub_service.publish_result(job_id, s3_url)


async def publish_failure(job_id: str, error_message: str):
    """헬퍼 함수: 실패 발송"""
    await pub_sub_service.publish_failure(job_id, error_message)


async def publish_step_progress(job_id: str, step_name: str, progress: float):
    """헬퍼 함수: 단계별 진행률 발송"""
    await pub_sub_service.publish_step_progress(job_id, step_name, progress)
