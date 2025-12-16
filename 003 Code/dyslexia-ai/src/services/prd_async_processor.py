"""
PRD 비동기 프로세서
PRD 명세에 따른 백그라운드 교안 생성 파이프라인
"""
import asyncio
import json
import logging
import tempfile
import os
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import UploadFile, HTTPException

from .redis_pub_sub_service import (
    publish_progress,
    publish_result,
    publish_failure,
    publish_step_progress,
    pub_sub_service,
)
from .s3_json_uploader import upload_result_to_s3
from .preprocessing_service import run_preprocessing_pipeline
from ..models import PreprocessingOptions
from .transformation_service import transform_content_to_blocks
from .redis_service import create_redis_service
from src.pipelines.main_pipeline import main_pipeline
from .spring_callback_service import send_document_complete

logger = logging.getLogger(__name__)


class PRDAsyncProcessor:
    """PRD 명세에 따른 비동기 처리 프로세서"""

    def __init__(self):
        self.redis_service = create_redis_service()

        # 활성 작업 관리
        self.active_jobs: Dict[str, asyncio.Task] = {}

        logger.info("PRD 비동기 프로세서 초기화 완료")

    async def is_job_active(self, job_id: str) -> bool:
        """작업이 현재 활성 상태인지 확인"""
        return job_id in self.active_jobs

    async def process_pdf_pipeline(self, job_id: str, file_bytes: bytes, filename: str, textbook_id: Optional[int] = None):
        """
        백그라운드 교안 생성 파이프라인 (PRD 4.2)

        1. 초기 상태 설정: PROCESSING
        2. PDF 전처리 (진행률 발송)
        3. 핵심 콘텐츠 변환 (페이지별 진행률 발송)
        4. 결과 집계 및 S3 저장
        5. 완료/실패 메시지 발송
        """
        try:
            logger.info(f"Job[{job_id}]: 교안 생성 파이프라인 시작")

            # 1. 초기 상태 설정
            await self._set_job_status(job_id, "PROCESSING", 0)
            await publish_progress(job_id, 0)

            # 2~4. LCEL 단일 파이프라인 실행 (전처리 → 변환 → 조립)
            logger.info(f"Job[{job_id}]: LCEL 파이프라인 실행 시작")
            pipeline_input = {
                "job_id": job_id,
                "file_bytes": file_bytes,
                "filename": filename,
                "created_at": datetime.utcnow().isoformat(),
                "textbook_id": textbook_id,
            }
            final_result = await main_pipeline.ainvoke(pipeline_input)
            logger.info(f"Job[{job_id}]: LCEL 파이프라인 실행 완료")

            # 5. 결과 저장 및 발행
            await publish_step_progress(job_id, "STORAGE", 85)
            logger.info(f"Job[{job_id}]: 최종 결과를 파일로 저장합니다.")
            await self._save_result_to_file(job_id, final_result)

            logger.info(f"Job[{job_id}]: 최종 결과를 S3에 업로드합니다.")
            s3_url = await upload_result_to_s3(job_id, final_result)
            logger.info(f"Job[{job_id}]: S3 업로드를 완료했습니다. URL: {s3_url}")

            await publish_step_progress(job_id, "STORAGE", 95)

            await self._set_job_status(job_id, "COMPLETED", 100)
            logger.info(
                f"Job[{job_id}]: 처리 완료 메시지를 Redis 채널({pub_sub_service.result_channel})에 발행합니다."
            )
            await publish_result(job_id, s3_url)
            # Spring 서버 콜백 (POST /api/document/complete)
            try:
                callback_ok = await send_document_complete(job_id, filename, final_result)
                if callback_ok:
                    logger.info(f"Job[{job_id}]: Spring 콜백을 성공적으로 전송했습니다.")
                else:
                    logger.warning(f"Job[{job_id}]: Spring 콜백 전송에 실패했습니다.")
            except Exception as cb_e:
                logger.error(f"Job[{job_id}]: Spring 콜백 처리 중 오류: {cb_e}")
            logger.info(f"Job[{job_id}]: 교안 생성 파이프라인이 성공적으로 완료되었습니다.")

        except Exception as e:
            error_message = f"교안 생성 중 예상치 못한 오류 발생: {str(e)}"
            logger.error(
                f"Job[{job_id}]: 파이프라인 실행에 실패했습니다. Error: {error_message}",
                exc_info=True,
            )

            # 실패 처리
            await self._set_job_status(job_id, "FAILED", None, error_message)

            # Redis 실패 메시지 발행
            try:
                logger.info(
                    f"Job[{job_id}]: 처리 실패 메시지를 Redis 채널({pub_sub_service.failure_channel})에 발행합니다."
                )
                await publish_failure(job_id, error_message)
                logger.info(f"Job[{job_id}]: 실패 메시지를 성공적으로 발행했습니다.")
            except Exception as pub_e:
                logger.error(
                    f"Job[{job_id}]: Redis 실패 메시지 발행 중 추가 오류 발생: {str(pub_e)}",
                    exc_info=True,
                )

        finally:
            # 활성 작업에서 제거
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]

    async def _save_result_to_file(self, job_id: str, result_data: Dict[str, Any]) -> Optional[str]:
        """결과 데이터를 output/{job_id}.json 파일로 저장"""
        try:
            output_dir = os.path.join(os.getcwd(), "output")
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"{job_id}.json")

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Job[{job_id}]: 최종 결과가 파일로 저장되었습니다: {file_path}")
            return file_path
        except Exception as e:
            logger.error(
                f"Job[{job_id}]: 최종 결과를 파일로 저장하는 데 실패했습니다: {e}",
                exc_info=True,
            )
            return None

    async def _save_temp_file(self, file_bytes: bytes, filename: str) -> str:
        """PDF 바이트를 임시 위치에 저장"""
        try:
            # 임시 파일 생성
            suffix = ".pdf"
            try:
                if filename and "." in filename:
                    suffix = os.path.splitext(filename)[1] or ".pdf"
            except Exception:
                pass

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(file_bytes)
                temp_file_path = temp_file.name

            logger.info(f"임시 파일 저장 완료: {temp_file_path}")
            return temp_file_path

        except Exception as e:
            logger.error(f"임시 파일 저장 실패: {str(e)}")
            raise HTTPException(status_code=500, detail=f"파일 저장 실패: {str(e)}")

    async def _preprocess_pdf(self, file_path: str) -> Dict[str, Any]:
        """PDF 전처리 실행"""
        try:
            # 전처리 옵션 설정
            options = PreprocessingOptions(
                temp_dir=os.path.dirname(file_path),
                remove_headers_footers=True,
                header_height=30.0,
                footer_height=30.0,
                max_tokens=12000
            )

            # UploadFile 객체 생성을 위한 파일 래퍼 클래스
            class FileWrapper:
                def __init__(self, file_path: str):
                    self.file_path = file_path
                    self.filename = os.path.basename(file_path)
                    self._file = None

                @property
                def file(self):
                    if self._file is None:
                        self._file = open(self.file_path, 'rb')
                    return self._file

            file_wrapper = FileWrapper(file_path)

            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: run_preprocessing_pipeline(
                    file=file_wrapper,
                    options=options,
                    return_text=True,
                    return_chunks=True,
                    model="claude-sonnet-4-20250514"
                )
            )

            return result

        except Exception as e:
            logger.error(f"PDF 전처리 실패: {str(e)}")
            raise

    async def _transform_content(self, job_id: str, preprocessed_data: Dict[str, Any], textbook_id: Optional[int] = None) -> Dict[str, Any]:
        """콘텐츠 변환 실행 (페이지별 진행률 업데이트)"""
        try:
            chunks = preprocessed_data.get("chunks", [])
            total_chunks = len(chunks)

            if total_chunks == 0:
                return {"transformed_content": []}

            # 모든 청크를 한 번에 변환
            # 전처리 결과는 List[str] 형태이며, 과거 버전의 List[dict]도 지원
            if chunks and isinstance(chunks[0], str):
                chunk_texts = chunks
            else:
                chunk_texts = [
                    (chunk.get("text") if isinstance(chunk, dict) else str(chunk))
                    for chunk in chunks
                ]

            enable_images = os.getenv("ENABLE_IMAGE_GENERATION", "true").lower() in ("1", "true", "yes", "on")

            transformed_result = await transform_content_to_blocks(
                content=chunk_texts,
                model_name="claude-sonnet-4-20250514",
                max_concurrent=8,
                image_interval=15,
                word_limit=15,
                vocabulary_interval=5,
                save_to_redis=True,
                expire_hours=24,
                generate_images=enable_images,
            )

            # 변환 결과 병합: transformation_service는 chunk 순서대로 chunk_blocks를 반환
            chunk_blocks = transformed_result.get("chunk_blocks", [])

            transformed_chunks = []
            # 블록 어휘 분석 비동기 체인 태스크 저장소
            vocab_tasks: list[asyncio.Task] = []

            for i in range(total_chunks):
                blocks_for_chunk = chunk_blocks[i] if i < len(chunk_blocks) else []
                transformed_chunks.append({
                    "chunk_index": i,
                    "text": chunk_texts[i] if i < len(chunk_texts) else "",
                    "blocks": blocks_for_chunk,
                    "block_count": len(blocks_for_chunk),
                })

                # 각 TEXT 블록에 대해 즉시 어휘 분석 체인을 비동기로 실행하고 Spring 블록 콜백 전송
                if blocks_for_chunk:
                    try:
                        from src.services.vocabulary_analysis_service import analyze_block_and_callback
                        for b in blocks_for_chunk:
                            if isinstance(b, dict) and b.get("type") == "TEXT":
                                # page_number 정보가 없다면 None으로 전달
                                task = asyncio.create_task(
                                    analyze_block_and_callback(
                                        job_id=job_id,
                                        textbook_id=textbook_id,
                                        page_number=b.get("page_number"),
                                        block=b,
                                    )
                                )
                                vocab_tasks.append(task)
                    except Exception as e:
                        logger.warning(f"어휘 분석 체인 스폰 실패: {e}")

                # 진행률 계산 (30% ~ 80% 구간)
                progress = 30 + int((i + 1) / total_chunks * 50)
                await publish_step_progress(job_id, "TRANSFORMATION", progress)

            # 어휘 분석 태스크는 백그라운드로 계속 진행(완료 대기하지 않음)
            return {
                "total_chunks": total_chunks,
                "transformed_chunks": transformed_chunks,
                "metadata": transformed_result.get("metadata", {}),
            }

        except Exception as e:
            logger.error(f"콘텐츠 변환 실패: {str(e)}")
            raise

    async def _aggregate_results(self, transformed_data: Dict[str, Any]) -> Dict[str, Any]:
        """최종 결과 집계"""
        try:
            final_result = {
                "job_completed_at": datetime.utcnow().isoformat(),
                "content_type": "dyslexia_teaching_material",
                "total_chunks": transformed_data.get("total_chunks", 0),
                "content": transformed_data.get("transformed_chunks", []),
                "processing_summary": {
                    "preprocessed_chunks": transformed_data.get("total_chunks", 0),
                    "transformed_chunks": len(transformed_data.get("transformed_chunks", [])),
                    "success_rate": 100.0  # 성공적으로 완료된 경우
                }
            }

            return final_result

        except Exception as e:
            logger.error(f"결과 집계 실패: {str(e)}")
            raise

    async def _set_job_status(self, job_id: str, status: str, progress: Optional[float], error: Optional[str] = None):
        """Redis에 작업 상태 저장"""
        try:
            job_status = {
                "status": status,
                "progress": progress,
                "updated_at": datetime.utcnow().isoformat(),
                "error": error
            }

            # Redis에 저장 (24시간 TTL)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.redis_service.redis_client.redis_client.setex(
                    f"job_status:{job_id}",
                    86400,  # 24시간
                    str(job_status)
                )
            )

        except Exception as e:
            logger.error(f"작업 상태 저장 실패: job_id={job_id}, error={str(e)}")

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Redis에서 작업 상태 조회"""
        try:
            status_data = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.redis_service.redis_client.redis_client.get(f"job_status:{job_id}")
            )

            if status_data:
                import ast
                return ast.literal_eval(status_data.decode() if isinstance(status_data, bytes) else status_data)

            return None

        except Exception as e:
            logger.error(f"작업 상태 조회 실패: job_id={job_id}, error={str(e)}")
            return None
