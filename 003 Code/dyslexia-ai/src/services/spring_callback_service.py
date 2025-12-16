import logging
import os
from typing import Any, Dict, Optional

import httpx

from src.utils.env_config import get_spring_callback_url

logger = logging.getLogger(__name__)


def _get_callback_url() -> Optional[str]:
    # env_config 헬퍼 사용
    return get_spring_callback_url(required=False)


async def send_document_complete(job_id: str, pdf_name: str, data: Dict[str, Any]) -> bool:
    """스프링 서버로 작업 완료 콜백을 전송한다.

    Body 스키마:
      { "jobId": str, "pdfName": str, "data": object }
    """
    url = _get_callback_url()
    if not url:
        logger.warning("SPRING 콜백 URL이 설정되지 않았습니다. 콜백을 건너뜁니다.")
        return False

    payload = {
        "jobId": job_id,
        "pdfName": pdf_name,
        "data": data,
    }

    timeout = float(os.getenv("SPRING_CALLBACK_TIMEOUT", "10"))

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json=payload)
            if 200 <= resp.status_code < 300:
                logger.info(
                    f"Spring 콜백 성공: status={resp.status_code}, url={url}, jobId={job_id}"
                )
                return True
            else:
                logger.error(
                    f"Spring 콜백 실패: status={resp.status_code}, url={url}, body={resp.text[:500]}"
                )
                return False
    except Exception as e:
        logger.error(f"Spring 콜백 예외 발생: {e}")
        return False


async def send_vocabulary_complete(
    job_id: str, textbook_id: int, pdf_name: str, data: Dict[str, Any]
) -> bool:
    """어휘 분석 완료 콜백: 우선 SPRING_VOCAB_CALLBACK_URL → SPRING_CALLBACK_URL 순서로 사용.

    헤더에 X-Callback-Token을 포함할 수 있습니다.
    """
    url = os.getenv("SPRING_VOCAB_CALLBACK_URL") or _get_callback_url()
    if not url:
        logger.warning("SPRING_VOCAB_CALLBACK_URL/SPRING 콜백 URL 미설정. 콜백 스킵")
        return False

    payload = {**data}
    # 일관된 최소 필드 보강
    payload.setdefault("job_id", job_id)
    payload.setdefault("textbook_id", textbook_id)
    payload.setdefault("pdf_name", pdf_name)

    timeout = float(os.getenv("SPRING_CALLBACK_TIMEOUT", "10"))
    headers = {}
    token = os.getenv("EXTERNAL_CALLBACK_TOKEN")
    if token:
        headers["X-Callback-Token"] = token

    try:
        # 로그: 요청 요약
        try:
            stats = data.get("stats") or {}
            logger.info(
                f"Spring 어휘 완료 콜백 전송 준비: url={url}, jobId={job_id}, blocks={stats.get('blocks')}, items={stats.get('items')}"
            )
        except Exception:
            pass

        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            resp = await client.post(url, json=payload)
            if 200 <= resp.status_code < 300:
                logger.info(
                    f"Spring 어휘 콜백 성공: status={resp.status_code}, url={url}, jobId={job_id}, body={resp.text[:500]}"
                )
                return True
            else:
                logger.error(
                    f"Spring 어휘 콜백 실패: status={resp.status_code}, url={url}, body={resp.text[:500]}"
                )
                return False
    except Exception as e:
        logger.error(f"Spring 어휘 콜백 예외 발생: {e}")
        return False


async def send_vocabulary_block(
    job_id: str,
    textbook_id: int,
    block_payload: Dict[str, Any],
) -> bool:
    """블록 단위 어휘 결과 콜백.

    URL 우선순위:
      SPRING_VOCAB_BLOCK_CALLBACK_URL → (미설정 시 비활성화)
    본 함수는 URL이 없으면 False를 반환하고 아무 작업도 하지 않습니다.
    """
    url = os.getenv("SPRING_VOCAB_BLOCK_CALLBACK_URL")
    if not url or not url.strip():
        # 베이스 + 경로 조합 지원
        base = os.getenv("SPRING_SERVER_BASE_URL", "").strip().rstrip("/")
        path = os.getenv("SPRING_VOCAB_BLOCK_PATH", "/api/v1/ai/vocabulary/block").strip()
        if base:
            if not path.startswith("/"):
                path = "/" + path
            url = f"{base}{path}"
        else:
            return False

    timeout = float(os.getenv("SPRING_CALLBACK_TIMEOUT", "10"))
    headers = {}
    token = os.getenv("EXTERNAL_CALLBACK_TOKEN")
    if token:
        headers["X-Callback-Token"] = token

    # snake_case + camelCase 동시 제공으로 Spring Naming 전략 차이를 흡수
    payload_snake = {
        "job_id": job_id,
        "textbook_id": textbook_id,
        **block_payload,
    }
    # 블록 필드의 대표 키들을 camelCase로 복제
    payload_camel = {
        "jobId": job_id,
        "textbookId": textbook_id,
    }
    # 대표 블록 메타 키 변환
    if "page_number" in block_payload:
        payload_camel["pageNumber"] = block_payload.get("page_number")
    if "block_id" in block_payload:
        payload_camel["blockId"] = block_payload.get("block_id")
    if "original_sentence" in block_payload:
        payload_camel["originalSentence"] = block_payload.get("original_sentence")
    if "vocabulary_items" in block_payload:
        payload_camel["vocabularyItems"] = block_payload.get("vocabulary_items")
    if "created_at" in block_payload:
        payload_camel["createdAt"] = block_payload.get("created_at")

    # 중첩 아이템 키 보조 매핑(특히 phonemeAnalysisJson)
    try:
        vocab_items = payload_snake.get("vocabulary_items") or []
        vocab_items_camel = []
        for it in vocab_items:
            if not isinstance(it, dict):
                continue
            it_camel = {
                "word": it.get("word"),
                "startIndex": it.get("start_index"),
                "endIndex": it.get("end_index"),
                "definition": it.get("definition"),
                "simplifiedDefinition": it.get("simplified_definition"),
                "examples": it.get("examples"),
                "difficultyLevel": it.get("difficulty_level"),
                "reason": it.get("reason"),
                "gradeLevel": it.get("grade_level"),
                # 핵심: phonemeAnalysisJson 매핑
                "phonemeAnalysisJson": it.get("phoneme_analysis_json"),
            }
            vocab_items_camel.append(it_camel)
        if vocab_items_camel:
            payload_camel["vocabularyItems"] = vocab_items_camel
    except Exception:
        pass

    payload = {**payload_snake, **payload_camel}

    try:
        # 로그: 요청 요약
        try:
            block_id_val = payload.get("block_id") or payload.get("blockId")
            vocab_items = payload.get("vocabulary_items") or payload.get("vocabularyItems") or []
            logger.info(
                f"Spring 블록 콜백 전송 준비: url={url}, jobId={job_id}, blockId={block_id_val}, items={len(vocab_items)}"
            )
        except Exception:
            pass

        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            resp = await client.post(url, json=payload)
            if 200 <= resp.status_code < 300:
                logger.info(
                    f"Spring 블록 콜백 성공: status={resp.status_code}, url={url}, jobId={job_id}, blockId={payload.get('block_id') or payload.get('blockId')}, body={resp.text[:300]}"
                )
                return True
            else:
                logger.error(
                    f"Spring 블록 콜백 실패: status={resp.status_code}, url={url}, body={resp.text[:300]}"
                )
                return False
    except Exception as e:
        logger.error(f"Spring 블록 콜백 예외 발생: {e}")
        return False
