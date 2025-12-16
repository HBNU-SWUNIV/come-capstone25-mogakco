"""
LangChain LCEL 기반 교안 생성 단일 파이프라인

입력: {"job_id": str, "file_bytes": bytes, "filename": str, "created_at": iso8601?}
출력: 최종 결과 JSON (Spring 호환 단순 구조)
"""
import asyncio
import io
import os
from datetime import datetime
from typing import Any, Dict, List

from langchain_core.runnables import RunnableLambda
from langchain_anthropic import ChatAnthropic
from src.core.prompts import create_block_conversion_prompt
from src.services.transformation_service import clean_json_response
from src.utils.anthropic_client import count_tokens
import logging
import time

from src.services.preprocessing_service import run_preprocessing_pipeline
from src.models import PreprocessingOptions
from src.services.transformation_service import transform_content_to_blocks
from src.services.redis_pub_sub_service import publish_step_progress
from src.services.image_generation_service import generate_image_with_s3_upload
from src.utils.env_config import get_temp_dir
from src.services.vocabulary_analysis_service import analyze_block_and_callback


class BytesUploadFile:
    """UploadFile 호환 래퍼 (filename, file.read() 제공)"""

    def __init__(self, filename: str, data: bytes):
        self.filename = filename
        self.file = io.BytesIO(data)


async def preprocess_step(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """PDF 바이트를 받아 전처리 후 청크를 반환"""
    job_id = input_dict["job_id"]
    filename = input_dict["filename"]
    file_bytes = input_dict["file_bytes"]

    # 단계 시작 알림
    await publish_step_progress(job_id, "PDF_PREPROCESSING", 10)

    # UploadFile 래퍼 구성
    upload = BytesUploadFile(filename=filename, data=file_bytes)

    # 전처리 옵션
    options = PreprocessingOptions(
        temp_dir=get_temp_dir("./temp"),
        remove_headers_footers=True,
        header_height=30.0,
        footer_height=30.0,
        max_tokens=12000,
    )

    # 동기 전처리를 실행자에서 실행
    loop = asyncio.get_event_loop()
    preprocessed = await loop.run_in_executor(
        None,
        lambda: run_preprocessing_pipeline(
            file=upload,
            options=options,
            return_text=True,
            return_chunks=True,
            model="claude-sonnet-4-20250514",
        ),
    )

    # 결과 병합
    input_dict["preprocessed"] = preprocessed
    input_dict["chunks"] = preprocessed.get("chunks", []) or []
    input_dict["pre_meta"] = preprocessed.get("metadata", {})

    # 단계 완료 알림
    await publish_step_progress(job_id, "PDF_PREPROCESSING", 25)

    return input_dict


async def transform_step(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """청크를 받아 변환된 블록을 반환"""
    job_id = input_dict["job_id"]
    chunks: List[str] = input_dict.get("chunks", [])

    await publish_step_progress(job_id, "TRANSFORMATION", 30)

    logger = logging.getLogger(__name__)

    # 문자열/딕셔너리 혼용 안전 처리
    if chunks and not isinstance(chunks[0], str):
        chunks = [
            (c.get("text") if isinstance(c, dict) else str(c))
            for c in chunks
        ]

    enable_images = os.getenv("ENABLE_IMAGE_GENERATION", "true").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )

    # 순차 처리 설정: 모델/프롬프트 초기화
    model_name = "claude-sonnet-4-20250514"
    model = ChatAnthropic(
        model=model_name,
        temperature=0,
        max_tokens=8192,
        timeout=300.0,
        max_retries=2,
    )
    prompt_template = create_block_conversion_prompt(
        image_interval=15,
        word_limit=15,
        vocabulary_interval=5,
    )
    chain = prompt_template | model

    chunk_blocks: List[List[Dict[str, Any]]] = []
    all_blocks: List[Dict[str, Any]] = []
    start_time = time.time()

    total_chunks = len(chunks) or 0
    for i, chunk_text in enumerate(chunks):
        # 진행률 업데이트 (30% → 60% 범위)
        progress = 30 + int(((i) / max(total_chunks, 1)) * 30) if total_chunks > 0 else 30
        await publish_step_progress(job_id, "TRANSFORMATION", progress)

        try:
            logger.info(f"Job[{job_id}]: 청크 {i+1}/{total_chunks} 변환 시작")
            result = await chain.ainvoke({"content": chunk_text})
            content = result.content if hasattr(result, "content") else str(result)
            blocks = clean_json_response(content)
            if not isinstance(blocks, list):
                blocks = []
            # 블록 단위 어휘 분석 비동기 체인: TEXT 블록을 즉시 분석하고 Spring 블록 콜백 전송
            try:
                textbook_id = input_dict.get("textbook_id")
                page_number = i + 1
                for b in blocks:
                    if isinstance(b, dict) and b.get("type") == "TEXT":
                        asyncio.create_task(
                            analyze_block_and_callback(
                                job_id=job_id,
                                textbook_id=textbook_id,
                                page_number=page_number,
                                block=b,
                            )
                        )
            except Exception as e:
                logger.warning(f"Job[{job_id}]: 어휘 분석 체인 스폰 실패: {e}")
            chunk_blocks.append(blocks)
            all_blocks.extend(blocks)
            logger.info(f"Job[{job_id}]: 청크 {i+1}/{total_chunks} 변환 완료 - {len(blocks)}개 블록")
        except Exception as e:
            logger.error(f"Job[{job_id}]: 청크 {i+1} 처리 중 오류: {e}", exc_info=True)
            raise

    # 최종 메타데이터
    total_processing_time = round(time.time() - start_time, 2)
    total_input_tokens = sum(count_tokens(c, model_name) for c in chunks) if chunks else 0

    input_dict["chunk_texts"] = chunks
    input_dict["chunk_blocks"] = chunk_blocks
    input_dict["transformed_blocks"] = all_blocks
    input_dict["transform_meta"] = {
        "model": model_name,
        "total_blocks": sum(len(b) for b in chunk_blocks),
        "total_processing_time": total_processing_time,
        "input_chunks": total_chunks,
        "total_input_tokens": total_input_tokens,
        "processing_method": "sequential_lcel",
        "images_generated": False,
    }

    await publish_step_progress(job_id, "TRANSFORMATION", 60)
    return input_dict


async def image_processing_step(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """PAGE_IMAGE 블록을 감지하여 이미지 생성 및 S3 업로드 후 URL 채움"""
    job_id = input_dict["job_id"]
    logger = logging.getLogger(__name__)

    # 진행 시작
    await publish_step_progress(job_id, "IMAGE_PROCESSING", 65)

    enable_images = os.getenv("ENABLE_IMAGE_GENERATION", "true").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )

    chunk_blocks: List[List[Dict[str, Any]]] = input_dict.get("chunk_blocks", [])
    all_blocks: List[Dict[str, Any]] = input_dict.get("transformed_blocks", [])

    if not enable_images:
        logger.info(f"Job[{job_id}]: 이미지 생성 비활성화 - ENABLE_IMAGE_GENERATION=false")
        meta = input_dict.get("transform_meta", {})
        meta["images_generated"] = False
        input_dict["transform_meta"] = meta
        await publish_step_progress(job_id, "IMAGE_PROCESSING", 80)
        return input_dict

    # PAGE_IMAGE 블록 수집 (chunk_index, block_index, block)
    image_targets: List[tuple] = []
    for ci, blocks in enumerate(chunk_blocks):
        for bi, block in enumerate(blocks or []):
            try:
                if isinstance(block, dict) and (block.get("type") == "PAGE_IMAGE"):
                    image_targets.append((ci, bi, block))
            except Exception:
                continue

    if not image_targets:
        logger.info(f"Job[{job_id}]: PAGE_IMAGE 블록 없음 - 이미지 처리 스킵")
        meta = input_dict.get("transform_meta", {})
        meta["images_generated"] = False
        input_dict["transform_meta"] = meta
        await publish_step_progress(job_id, "IMAGE_PROCESSING", 80)
        return input_dict

    logger.info(f"Job[{job_id}]: PAGE_IMAGE {len(image_targets)}개 이미지 생성 시작")

    # 동시 실행 준비: 동기 함수를 스레드로 실행
    async def run_generate(block: Dict[str, Any]) -> Dict[str, Any]:
        description = (
            block.get("prompt")
            or block.get("concept")
            or block.get("alt")
            or "education image"
        )
        return await asyncio.to_thread(
            generate_image_with_s3_upload,
            description,
            "any",
            "1536x1024",
            "google/nano-banana",
            "jpg",
            True,
        )

    # 작업 생성 및 실행
    tasks = [run_generate(block) for (_, _, block) in image_targets]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 결과 반영 + 진행률 보고 (65→80)
    total = len(results)
    success_count = 0
    for idx, res in enumerate(results):
        (ci, bi, block) = image_targets[idx]
        if isinstance(res, Exception):
            logger.error(
                f"Job[{job_id}]: 이미지 생성 실패 (chunk={ci}, block={bi}): {res}"
            )
        else:
            url = res.get("url")
            if url:
                try:
                    # chunk_blocks에 URL 반영
                    chunk_blocks[ci][bi]["url"] = url
                    # transformed_blocks의 동일 블록을 찾아 업데이트 (옵션)
                    # 안전하게: all_blocks 내 동일 dict 참조가 아닐 수 있어 skip
                    success_count += 1
                except Exception as e:
                    logger.warning(
                        f"Job[{job_id}]: URL 업데이트 중 경고 (chunk={ci}, block={bi}): {e}"
                    )

        # 중간 진행률
        progress = 65 + int(((idx + 1) / max(total, 1)) * 15)
        await publish_step_progress(job_id, "IMAGE_PROCESSING", progress)

    logger.info(
        f"Job[{job_id}]: 이미지 생성 완료 - {success_count}/{total} 성공"
    )

    # 딕셔너리 갱신
    input_dict["chunk_blocks"] = chunk_blocks
    # all_blocks 재구성 (플랫)
    try:
        input_dict["transformed_blocks"] = [b for blocks in chunk_blocks for b in (blocks or [])]
    except Exception:
        pass
    meta = input_dict.get("transform_meta", {})
    meta["images_generated"] = True if success_count > 0 else False
    input_dict["transform_meta"] = meta

    await publish_step_progress(job_id, "IMAGE_PROCESSING", 80)
    return input_dict

def final_assembly_step(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """최종 JSON 구조로 조립 (Spring 호환)"""
    job_id = input_dict["job_id"]
    filename = input_dict["filename"]
    created_at = input_dict.get("created_at")
    if not created_at:
        created_at = datetime.utcnow().isoformat()

    completed_at = datetime.utcnow().isoformat()

    chunk_texts: List[str] = input_dict.get("chunk_texts", [])
    chunk_blocks: List[List[Dict[str, Any]]] = input_dict.get("chunk_blocks", [])

    # 메타데이터 집계
    pre_meta = input_dict.get("pre_meta", {})
    tr_meta = input_dict.get("transform_meta", {})

    total_blocks = sum(len(b) for b in chunk_blocks)
    total_chunks = len(chunk_texts)

    # 페이지(=청크) 단위로 단순 매핑 (실제 PDF 페이지 매핑이 필요한 경우 후속 개선)
    # 시작 진행률 보고 (조립 단계는 짧게 유지)
    try:
        # 조립 단계는 비동기가 아니므로 best-effort로 보고
        import anyio
        anyio.from_thread.run(publish_step_progress, job_id, "FINAL_ASSEMBLY", 82)
    except Exception:
        pass

    pages = []
    for i, text in enumerate(chunk_texts):
        pages.append(
            {
                "page_number": i + 1,
                "original_content": text,
                "blocks": chunk_blocks[i] if i < len(chunk_blocks) else [],
            }
        )

    # 처리 시간 계산
    try:
        dt_created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        dt_completed = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
        processing_seconds = (dt_completed - dt_created).total_seconds()
    except Exception:
        processing_seconds = tr_meta.get("total_processing_time") or 0

    final_json = {
        "jobId": job_id,
        "fileName": filename,
        "status": "COMPLETED",
        "createdAt": created_at,
        "completedAt": completed_at,
        "processingTimeSeconds": processing_seconds,
        "metadata": {
            "model": tr_meta.get("model"),
            "total_pages_from_pdf": pre_meta.get("total_pages"),
            "total_chunks": total_chunks,
            "total_blocks": total_blocks,
        },
        "pages": pages,
    }

    try:
        import anyio
        anyio.from_thread.run(publish_step_progress, job_id, "FINAL_ASSEMBLY", 84)
    except Exception:
        pass

    return final_json


# LCEL 파이프라인 구성
main_pipeline = (
    RunnableLambda(preprocess_step)
    | RunnableLambda(transform_step)
    | RunnableLambda(image_processing_step)
    | RunnableLambda(final_assembly_step)
)
