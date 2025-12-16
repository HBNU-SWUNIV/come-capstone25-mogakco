import asyncio
import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

from src.models.vocabulary import (
    StartVocabularyRequest,
    AsyncStartResponse,
    VocabJobStatus,
)
from src.services.vocabulary_analysis_service import run_vocabulary_job
from src.services.spring_callback_service import send_vocabulary_complete
from src.services.redis_pub_sub_service import publish_failure

router = APIRouter(prefix="/api/v1/async/vocabulary", tags=["Vocabulary Analysis"])

logger = logging.getLogger(__name__)

# 간단한 인메모리 상태 저장소
_VOCAB_ACTIVE: Dict[str, asyncio.Task] = {}
_VOCAB_STATUS: Dict[str, VocabJobStatus] = {}
_VOCAB_RESULTS: Dict[str, Dict[str, Any]] = {}


@router.post("/start", response_model=AsyncStartResponse)
async def start_vocabulary_analysis(req: StartVocabularyRequest):
    job_id = req.job_id
    if job_id in _VOCAB_ACTIVE and not _VOCAB_ACTIVE[job_id].done():
        raise HTTPException(status_code=409, detail={
            "job_id": job_id,
            "status": "RUNNING",
            "message": "Job already running"
        })

    # 초기 상태 세팅
    _VOCAB_STATUS[job_id] = VocabJobStatus(
        job_id=job_id,
        status="PENDING",
        progress=0,
        total_blocks=len(req.items),
        completed_blocks=0,
        failed_blocks=0,
    )

    async def runner():
        try:
            _VOCAB_STATUS[job_id].status = "PROCESSING"
            result = await run_vocabulary_job(
                job_id=job_id,
                textbook_id=req.textbook_id,
                items=req.items,
                model_name=req.model_name,
                max_concurrent=req.max_concurrent,
                rate_limit_per_min=req.rate_limit_per_min,
                enable_phoneme=req.enable_phoneme,
                progress_cb=_make_progress_cb(job_id),
            )
            _VOCAB_RESULTS[job_id] = result
            _VOCAB_STATUS[job_id].status = "COMPLETED"
            _VOCAB_STATUS[job_id].progress = 100
            _VOCAB_STATUS[job_id].completed_blocks = _VOCAB_STATUS[job_id].total_blocks

            # Spring 콜백(요약+S3 포인터) 시도
            try:
                logger.info(
                    f"어휘 작업 최종 콜백 전송 준비: job_id={job_id}, textbook_id={req.textbook_id}"
                )
                s3_url = result.get("s3_url")
                summary = result.get("summary", {})
                payload = {
                    "payload_version": 1,
                    "result_type": "VOCABULARY",
                    "job_id": job_id,
                    "textbook_id": req.textbook_id,
                    "pdf_name": "vocabulary.json",
                    "s3_summary_url": s3_url,
                    "s3_blocks_prefix": s3_url,  # 단일 파일 업로드이므로 동일 URL 제공(향후 prefix 구조로 확장 가능)
                    "stats": {
                        "blocks": summary.get("blocks", 0),
                        "items": summary.get("items", 0),
                        "by_difficulty": summary.get("by_difficulty", {}),
                    },
                    "created_at": result.get("created_at"),
                }
                ok = await send_vocabulary_complete(job_id, req.textbook_id, "vocabulary.json", payload)
                logger.info(
                    f"어휘 작업 최종 콜백 결과: job_id={job_id}, success={ok}"
                )
            except Exception as cb_err:
                logger.warning(f"Spring 콜백 실패: job_id={job_id}, err={cb_err}")

        except Exception as e:
            logger.error(f"어휘 분석 작업 실패: {e}", exc_info=True)
            _VOCAB_STATUS[job_id].status = "FAILED"
            _VOCAB_STATUS[job_id].failed_blocks = _VOCAB_STATUS[job_id].total_blocks
            await publish_failure(job_id, str(e))

    _VOCAB_ACTIVE[job_id] = asyncio.create_task(runner())

    return AsyncStartResponse(job_id=job_id, status="ACCEPTED", message="queued")


def _make_progress_cb(job_id: str):
    async def _cb(done: int, total: int):
        st = _VOCAB_STATUS.get(job_id)
        if not st:
            return
        st.completed_blocks = done
        st.failed_blocks = 0  # 세밀한 실패 카운트는 추후 확장
        st.progress = int(done / max(1, total) * 100)
    return _cb


@router.get("/status/{job_id}", response_model=VocabJobStatus)
async def get_status(job_id: str):
    st = _VOCAB_STATUS.get(job_id)
    if not st:
        raise HTTPException(status_code=404, detail="job not found")
    return st


@router.get("/result/{job_id}")
async def get_result(job_id: str):
    res = _VOCAB_RESULTS.get(job_id)
    if not res:
        st = _VOCAB_STATUS.get(job_id)
        if st and st.status in ("PENDING", "PROCESSING"):
            raise HTTPException(status_code=202, detail={"status": st.status})
        raise HTTPException(status_code=404, detail="result not found")
    return res


@router.get("/blocks/{job_id}/{block_id}")
async def get_block_result(job_id: str, block_id: str):
    res = _VOCAB_RESULTS.get(job_id)
    if not res:
        raise HTTPException(status_code=404, detail="result not found")
    blocks = res.get("blocks", [])
    for b in blocks:
        if b.get("block_id") == block_id:
            return b
    raise HTTPException(status_code=404, detail="block not found")


@router.delete("/cancel/{job_id}")
async def cancel_job(job_id: str):
    t = _VOCAB_ACTIVE.get(job_id)
    if t and not t.done():
        t.cancel()
        _VOCAB_STATUS[job_id].status = "CANCELLED"
        return {"job_id": job_id, "status": "CANCELLED"}
    return {"job_id": job_id, "status": "NOT_FOUND_OR_DONE"}
