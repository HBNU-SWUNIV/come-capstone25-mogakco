import asyncio
import json
import logging
import os
import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Awaitable, Callable, cast

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from src.core.prompts import create_vocabulary_analysis_prompt
from src.models.vocabulary import (
    BlockVocabularyInput,
    VocabularyItem,
    BlockVocabularyResult,
    VocabJobResult,
)
from src.services.redis_pub_sub_service import publish_step_progress, publish_result, publish_failure
from src.utils.anthropic_client import count_tokens
from src.services.phoneme_analysis_service import analyze_words_phoneme

logger = logging.getLogger(__name__)


def _clean_json_array(text: str) -> List[Dict[str, Any]]:
    """LLM 응답에서 JSON 배열 파싱 시도"""
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
    except Exception:
        pass

    # 배열 패턴만 추출
    try:
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            frag = text[start : end + 1]
            data = json.loads(frag)
            if isinstance(data, list):
                return data
    except Exception:
        logger.warning("JSON 배열 파싱 실패, 빈 결과 반환")
    return []


def _resolve_provider(model_name: str) -> str:
    """환경변수 또는 모델명으로 LLM 제공자 결정 (anthropic|openai)"""
    provider = os.getenv("VOCAB_MODEL_PROVIDER", "").strip().lower()
    if provider in ("anthropic", "openai"):
        return provider
    name = (model_name or "").lower()
    if name.startswith("gpt-") or name.startswith("o1") or name.startswith("o3"):
        return "openai"
    return "anthropic"


def _is_openai_fixed_temperature_model(model_name: str) -> bool:
    n = (model_name or "").lower()
    prefixes = (
        "gpt-5",
        "o1",  # reasoning family
        "o3",  # reasoning family
        "gpt-4.1",
    )
    return any(n.startswith(p) for p in prefixes)


def _build_chat_model(model_name: str, *, temperature: float = 0, max_tokens: int = 2048, timeout: float = 60.0):
    """선택된 제공자에 맞게 LangChain Chat 모델 생성"""
    provider = _resolve_provider(model_name)
    if provider == "openai":
        try:
            from langchain_openai import ChatOpenAI  # type: ignore

            params = {
                "model": model_name,
                "max_tokens": max_tokens,
                "timeout": timeout,
            }
            # 일부 모델은 temperature가 고정(default=1)만 허용 → 명시적으로 1로 설정
            if _is_openai_fixed_temperature_model(model_name):
                params["temperature"] = 1
            else:
                params["temperature"] = temperature
            return ChatOpenAI(**params)
        except Exception as e:
            logger.error(f"ChatOpenAI 초기화 실패({e}) → Anthropic로 폴백")
            # 폴백: Anthropic 기본 모델로 교체
            model_name = os.getenv("ANTHROPIC_FALLBACK_MODEL", "claude-sonnet-4-20250514")
            return ChatAnthropic(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
            )
    # 기본: Anthropic
    return ChatAnthropic(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )


def _estimate_tokens(text: str, model_name: str) -> int:
    provider = _resolve_provider(model_name)
    if provider == "anthropic":
        return count_tokens(text, model_name)
    # OpenAI 대략 추정 (영어 기준 1 token ~= 4 chars)
    return max(1, len(text) // 4)


async def analyze_sentence_vocabulary(
    model: Any, sentence: str, *, max_tokens: int = 2048
) -> List[VocabularyItem]:
    """단일 문장에 대한 어휘 분석 수행"""
    prompt = create_vocabulary_analysis_prompt()
    chain = prompt | model
    try:
        result = await chain.ainvoke({"sentence": sentence})
        items = _normalize_items_from_llm(result.content, sentence)
        # 최대 5개로 제한
        items = items[:5]
        if items:
            return items

        # 2차 시도: 한 개 이상 강제 반환 프롬프트 (모델 제공자 무관 공용 템플릿)
        fallback_prompt = (
            "다음 문장에서 최소 1개 최대 5개의 어려운 단어를 JSON 배열로만 반환하세요.\n"
            "각 항목은 \"word\", \"startIndex\", \"endIndex\"만 포함하세요.\n"
            "문장:\n{sentence}"
        )
        fb_template = ChatPromptTemplate.from_messages([("user", fallback_prompt)])
        fb = await (fb_template | model).ainvoke({"sentence": sentence})
        items = _normalize_items_from_llm(getattr(fb, "content", str(fb)), sentence)
        items = items[:5]
        if items:
            return items

        # 3차 시도: 휴리스틱 최소 1개 생성
        return [_heuristic_min_one(sentence)]
    except Exception as e:
        logger.error(f"어휘 분석 실패: {e}")
        # 실패 시에도 최소 1개 생성
        return [_heuristic_min_one(sentence)]


def _normalize_items_from_llm(content: str, sentence: str) -> List[VocabularyItem]:
    items_raw = _clean_json_array(content)
    out: List[VocabularyItem] = []
    seen = set()

    def clamp_idx(i: int) -> int:
        return max(0, min(i, max(0, len(sentence) - 1)))

    for obj in items_raw:
        try:
            def g(k, default=None):
                return obj.get(k) or obj.get(k.replace("_", "")) or obj.get(k.replace("_", "").lower()) or default

            word = str(g("word", "")).strip()
            if not word:
                continue
            s = int(g("startIndex", g("start_index", -1)) or -1)
            e = int(g("endIndex", g("end_index", -1)) or -1)
            if s < 0 or e <= s or e > len(sentence):
                # 인덱스 보정: 첫 등장 위치로
                idx = sentence.find(word)
                if idx >= 0:
                    s = idx
                    e = idx + len(word)
                else:
                    # 대소문자/공백 변형 탐색
                    idx = sentence.lower().find(word.lower())
                    if idx >= 0:
                        s = idx
                        e = idx + len(word)
            s = clamp_idx(s if s >= 0 else 0)
            e = clamp_idx(e if e > s else s + len(word))

            examples_val = obj.get("examples")
            if isinstance(examples_val, str):
                try:
                    examples_val = json.loads(examples_val)
                    if not isinstance(examples_val, list):
                        examples_val = [str(examples_val)]
                except Exception:
                    examples_val = [examples_val]

            key = (word, s, e)
            if key in seen:
                continue
            seen.add(key)

            out.append(
                VocabularyItem(
                    word=word,
                    start_index=s,
                    end_index=e,
                    definition=g("definition"),
                    simplified_definition=g("simplifiedDefinition", g("simplified_definition")),
                    examples=examples_val if isinstance(examples_val, list) else None,
                    difficulty_level=g("difficultyLevel", g("difficulty_level")),
                    reason=g("reason"),
                    grade_level=g("gradeLevel", g("grade_level")),
                )
            )
        except Exception as e:
            logger.debug(f"어휘 항목 정규화 스킵: {e}")

    return out


def _heuristic_min_one(sentence: str) -> VocabularyItem:
    # 간단한 토큰화: 한글/영문/숫자 연속 토큰
    tokens = re.findall(r"[\w가-힣]+", sentence)
    # 길이 기준으로 정렬, 너무 짧은 토큰 제거
    candidates = sorted([t for t in tokens if len(t) >= 2], key=len, reverse=True)
    chosen = candidates[0] if candidates else (sentence.strip()[:4] or "단어")
    idx = sentence.find(chosen)
    if idx < 0:
        idx = max(0, len(sentence) // 2 - len(chosen) // 2)
    return VocabularyItem(
        word=chosen,
        start_index=idx,
        end_index=idx + len(chosen),
        definition=None,
        simplified_definition=None,
        examples=None,
        difficulty_level=None,
        reason="auto_fallback",
        grade_level=None,
    )


async def _enrich_with_phoneme(items: List[VocabularyItem]) -> List[VocabularyItem]:
    """선택된 어휘 항목에 대해 음운분석을 수행하고 JSON 문자열을 채운다."""
    if not items:
        return items
    words = [vi.word for vi in items if vi.word]
    try:
        result = await analyze_words_phoneme(words)
        analyses = result.get("phoneme_analyses", [])
        # word -> analysis 매핑 (중복 단어는 첫 번째 매핑만)
        mapping: Dict[str, Any] = {}
        for ar in analyses:
            if not ar.get("success"):
                continue
            w = ar.get("word")
            if w and w not in mapping and ar.get("phoneme_analysis"):
                mapping[w] = ar.get("phoneme_analysis")
        for vi in items:
            pa = mapping.get(vi.word)
            if pa:
                vi.phoneme_analysis = pa
                try:
                    vi.phoneme_analysis_json = json.dumps(pa, ensure_ascii=False)
                except Exception:
                    vi.phoneme_analysis_json = None
        return items
    except Exception as e:
        logger.warning(f"음운분석 보강 실패: {e}")
        return items


async def analyze_block_and_callback(
    *,
    job_id: str,
    textbook_id: Optional[int],
    page_number: Optional[int],
    block: Dict[str, Any],
    model_name: str = "gpt-4o-mini",
    enable_phoneme: bool = True,
) -> None:
    """단일 TEXT 블록에 대한 어휘 분석을 수행하고 Spring으로 블록 콜백을 전송한다.

    예외는 로깅만 하고 상위 흐름을 방해하지 않는다.
    """
    try:
        if not isinstance(block, dict) or block.get("type") != "TEXT":
            return
        text = block.get("text") or ""
        block_id = block.get("block_id") or block.get("id") or ""
        if not text or not block_id:
            return

        model = _build_chat_model(
            model_name,
            temperature=0,
            max_tokens=1024,
            timeout=60.0,
        )
        items = await analyze_sentence_vocabulary(model, text)
        if enable_phoneme:
            items = await _enrich_with_phoneme(items)
        try:
            logger.info(
                f"어휘 분석 완료(블록): job_id={job_id}, block_id={block_id}, page={page_number}, items={len(items)}"
            )
        except Exception:
            pass
        payload = {
            "page_number": page_number,
            "block_id": block_id,
            "original_sentence": text,
            "vocabulary_items": [vi.model_dump() for vi in items],
            "created_at": datetime.utcnow().isoformat(),
        }
        try:
            from src.services.spring_callback_service import send_vocabulary_block

            ok = await send_vocabulary_block(
                job_id,
                int(textbook_id) if textbook_id is not None else 0,
                payload,
            )
            try:
                logger.info(
                    f"어휘 블록 콜백 결과: job_id={job_id}, block_id={block_id}, success={ok}"
                )
            except Exception:
                pass
        except Exception as e:
            logger.warning(
                f"블록 콜백 전송 실패: job={job_id}, block={block_id}, err={e}"
            )
    except Exception as e:
        logger.debug(f"블록 어휘 분석 스킵/실패: {e}")


async def run_vocabulary_job(
    *,
    job_id: str,
    textbook_id: int,
    items: List[BlockVocabularyInput],
    model_name: str = "gpt-4o-mini",
    max_concurrent: int = 5,
    rate_limit_per_min: int = 30,
    enable_phoneme: bool = False,  # 확장 포인트
    progress_cb: Optional[Callable[[int, int], Awaitable[None]]] = None,
) -> Dict[str, Any]:
    """
    블록(문장) 목록에 대해 병렬 어휘 분석을 수행하고 결과를 집계합니다.
    완료 후 S3 업로드와(가능한 경우) 결과 채널 발행을 시도합니다.
    """
    await publish_step_progress(job_id, "VOCABULARY_ANALYSIS", 0)

    model = _build_chat_model(
        model_name,
        temperature=0,
        max_tokens=1024,
        timeout=120.0,
    )

    # 레이트 리미트(단순 토큰 버킷)
    rate_window = 60.0
    per_request_delay = max(0.0, rate_window / max(1, rate_limit_per_min))

    semaphore = asyncio.Semaphore(max_concurrent)
    results: List[BlockVocabularyResult] = []
    failures: List[str] = []

    start_total_tokens = 0
    for it in items:
        start_total_tokens += _estimate_tokens(it.text, model_name)

    async def worker(it: BlockVocabularyInput):
        async with semaphore:
            # 간단한 rate limit
            await asyncio.sleep(per_request_delay)
            analyzed = await analyze_sentence_vocabulary(model, it.text)
            if enable_phoneme:
                analyzed = await _enrich_with_phoneme(analyzed)
            created_at = datetime.utcnow().isoformat()
            res = BlockVocabularyResult(
                job_id=job_id,
                textbook_id=textbook_id,
                page_number=it.page_number,
                block_id=it.block_id,
                original_sentence=it.text,
                vocabulary_items=analyzed,
                created_at=created_at,
            )
            return res

    tasks = [worker(it) for it in items]

    completed = 0
    total = len(tasks)

    for coro in asyncio.as_completed(tasks):
        try:
            res = await coro
            results.append(res)
            # 블록 단위 콜백 (옵션 URL 설정 시)
            try:
                from src.services.spring_callback_service import send_vocabulary_block

                block_payload = {
                    "page_number": res.page_number,
                    "block_id": res.block_id,
                    "original_sentence": res.original_sentence,
                    "vocabulary_items": [vi.model_dump() for vi in res.vocabulary_items],
                    "created_at": res.created_at,
                }
                # 비동기로 날리고 기다리지 않음 (실패해도 작업은 계속)
                asyncio.create_task(
                    send_vocabulary_block(job_id, textbook_id, block_payload)
                )
            except Exception as e:
                logger.debug(f"블록 콜백 스킵/실패: {e}")
        except Exception as e:
            failures.append(str(e))
        finally:
            completed += 1
            progress = int(completed / max(1, total) * 100)
            await publish_step_progress(job_id, "VOCABULARY_ANALYSIS", progress)
            # 라우터 측 상태 갱신 콜백(있으면)
            if progress_cb:
                try:
                    await progress_cb(completed, total)
                except Exception:
                    pass

    # 집계 생성
    by_page = defaultdict(lambda: {"blocks": 0, "items": 0})
    diff_counter = Counter()
    total_items = 0
    for br in results:
        by_page[br.page_number]["blocks"] += 1
        item_count = len(br.vocabulary_items)
        by_page[br.page_number]["items"] += item_count
        total_items += item_count
        for vi in br.vocabulary_items:
            if vi.difficulty_level:
                diff_counter[vi.difficulty_level] += 1

    summary = {
        "blocks": len(results),
        "items": total_items,
        "by_difficulty": dict(diff_counter),
        "by_page": [
            {"page_number": k, **v} for k, v in sorted(by_page.items(), key=lambda x: x[0])
        ],
        "input_tokens_estimated": start_total_tokens,
    }

    job_result = VocabJobResult(
        job_id=job_id,
        textbook_id=textbook_id,
        blocks=results,
        summary=summary,
        created_at=datetime.utcnow().isoformat(),
    )

    # S3 업로드(가능 시)
    s3_url: Optional[str] = None
    try:
        # 지연 임포트로 자격증명 미설정 환경에서도 안전하게 동작
        from src.services.s3_json_uploader import upload_result_to_s3 as _upload

        s3_url = await _upload(job_id, job_result.model_dump())
        await publish_result(job_id, s3_url)
    except Exception as e:
        logger.warning(f"S3 업로드/결과 발행 스킵: {e}")

    result_payload = job_result.model_dump()
    if s3_url:
        result_payload["s3_url"] = s3_url
    if failures:
        result_payload["failures"] = failures

    try:
        logger.info(
            f"어휘 작업 완료: job_id={job_id}, blocks={len(results)}, items={total_items}, failures={len(failures)}, s3_url={s3_url}"
        )
    except Exception:
        pass

    return result_payload
