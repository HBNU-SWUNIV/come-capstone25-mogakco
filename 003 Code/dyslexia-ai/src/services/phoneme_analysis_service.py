import asyncio
import json
import logging
import re
import time
from typing import Any, Dict, List, Set

from langchain_anthropic import ChatAnthropic

from src.core.prompts import create_phoneme_analysis_prompt
from src.utils.anthropic_client import count_tokens

# 로거 설정
logger = logging.getLogger(__name__)


def clean_json_response(content: str) -> str:
    """
    LLM 응답에서 JSON 부분을 추출한다.

    Args:
        content: LLM 응답

    Returns:
        str: JSON 문자열
    """
    if not content or not content.strip():
        return content

    # 1. 코드블록 제거 (```json ... ``` 또는 ``` ... ```)
    content = re.sub(r"```(?:json)?\s*\n?(.*?)\n?```", r"\1", content, flags=re.DOTALL)

    # 2. 앞뒤 공백 제거
    content = content.strip()

    # 3. JSON 객체 {} 또는 배열 [] 찾기
    obj_start = content.find("{")
    obj_end = content.rfind("}")

    if obj_start != -1:
        if obj_end != -1 and obj_start < obj_end:
            json_str = content[obj_start : obj_end + 1]
        else:
            # JSON이 중간에 잘린 경우, 복구 단계 비활성화로 복구 생략
            json_str = content[obj_start:]
            # json_str = _repair_incomplete_json(json_str)
            logger.info("불완전한 JSON 감지: 복구 단계 비활성화로 복구 호출 생략")

        # JSON 유효성 검사
        try:
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            logger.info("JSON 파싱 실패: 복구 단계 비활성화로 원본 콘텐츠 반환")
            return content

    return content


def _is_korean_word(word: str) -> bool:
    """한글(가-힣)이 하나라도 포함되어 있으면 한국어 단어로 간주"""
    if not word:
        return False
    return bool(re.search(r"[가-힣]", word))

# TODO: 안정화 테스트 완료 시 삭제
def _repair_incomplete_json(json_str: str) -> str:
    """
    불완전한 JSON 문자열을 복구한다.

    Args:
        json_str: 불완전한 JSON 문자열

    Returns:
        str: 복구된 JSON 문자열
    """
    if not json_str.strip():
        return json_str

    json_str = json_str.strip()
    original_len = len(json_str)

    # 1. 기본적인 닫기 괄호 추가 시도
    basic_repairs = [
        json_str,  # 원본
        json_str + "}",  # 끝에 } 추가
        json_str + '"}',  # 끝에 "} 추가
        json_str + '"]',  # 끝에 "] 추가
        json_str + "}]",  # 끝에 }] 추가
        json_str + '"}]',  # 끝에 "}] 추가
        json_str + '"}}',  # 끝에 "}} 추가
        json_str + '"]}}',  # 끝에 "]}} 추가
        json_str + '"}]}}',  # 끝에 "}]}}} 추가
    ]

    # 2. 마지막 불완전한 부분 제거 후 복구
    if "," in json_str:
        last_comma = json_str.rfind(",")
        if last_comma != -1:
            truncated = json_str[:last_comma]
            basic_repairs.extend(
                [
                    truncated + "}",
                    truncated + "}]",
                    truncated + '"}}',
                    truncated + '"]}}',
                    truncated + '"}]}}',
                ]
            )

    # 3. 음운분석 특화 복구 - 특정 필드 패턴 감지
    if '"syllables":' in json_str and not json_str.endswith("]}"):
        # syllables 배열이 불완전한 경우
        syllables_start = json_str.find('"syllables":')
        if syllables_start != -1:
            after_syllables = json_str[syllables_start:]
            if '"syllables": [' in after_syllables and not "]}" in after_syllables:
                basic_repairs.extend(
                    [
                        json_str + "}]}",
                        json_str + '"}]}',
                        json_str + "]}}",
                        json_str + '"}]}}',
                    ]
                )

    # 4. learningTips 필드가 불완전한 경우
    if '"learningTips":' in json_str:
        learning_tips_pos = json_str.rfind('"learningTips":')
        if learning_tips_pos != -1:
            after_learning = json_str[learning_tips_pos:]
            if not after_learning.endswith("}}"):
                basic_repairs.extend(
                    [
                        json_str + "}}",
                        json_str + "]}}",
                        json_str + '"}}}',
                    ]
                )

    # 5. 각 복구 시도
    for i, repaired in enumerate(basic_repairs):
        try:
            json.loads(repaired)
            logger.info(
                f"JSON 복구 성공 (방법 {i+1}): {original_len} -> {len(repaired)} 문자"
            )
            return repaired
        except json.JSONDecodeError:
            continue

    # 6. 최후의 수단: 최소 유효한 JSON 구조 생성
    try:
        # 단어만 추출해서 최소 구조 생성
        word_match = re.search(r'"word":\s*"([^"]*)"', json_str)
        if word_match:
            word = word_match.group(1)
            minimal_json = (
                f'{{"word": "{word}", "syllables": [], "difficultyLevel": "medium"}}'
            )
            logger.warning(f"최소 JSON 구조로 복구: {word}")
            return minimal_json
    except Exception:
        pass

    # 모든 복구 시도 실패
    logger.error(f"JSON 복구 완전 실패: {json_str[:200]}...")
    return json_str


async def _analyze_single_word_phoneme(
    model: ChatAnthropic,
    word: str,
    word_index: int,
    semaphore: asyncio.Semaphore,
    block_id: str = None,
    difficulty_level: str = None,
    word_type: str = None,
    definition: str = None,
) -> Dict[str, Any]:
    """
    단일 단어의 음운분석을 수행한다.

    Args:
        model: 모델
        word: 단어
        word_index: 단어 인덱스
        semaphore: 세마포어
        block_id: 블록 ID
        difficulty_level: 난이도 레벨
        word_type: 단어 타입
        definition: 단어 정의

    Returns:
        Dict[str, Any]: 음운분석 결과
    """
    async with semaphore:
        try:
            # 프롬프트 템플릿 생성 및 호출
            prompt_template = create_phoneme_analysis_prompt()
            chain = prompt_template | model

            result = await chain.ainvoke({"word": word})

            # JSON 파싱 시도 - clean_json_response 사용
            cleaned_content = clean_json_response(result.content)
            phoneme_data = json.loads(cleaned_content)

            # 성공! 기본 필드 검증
            if not isinstance(phoneme_data, dict) or "word" not in phoneme_data:
                raise ValueError("응답에 필수 'word' 필드가 없습니다")

            log_msg = f"음운분석 성공: '{word}'"
            if block_id:
                log_msg += f" (블록: {block_id})"
            logger.info(log_msg)

            result_dict = {
                "word_index": word_index,
                "word": word,
                "phoneme_analysis": phoneme_data,
                "success": True,
            }

            # 블록 정보가 있으면 추가
            if block_id is not None:
                result_dict.update(
                    {
                        "block_id": block_id,
                        "difficulty_level": difficulty_level or "unknown",
                        "word_type": word_type or "unknown",
                        "definition": definition or "",
                    }
                )

            return result_dict

        except (json.JSONDecodeError, ValueError) as parse_error:
            logger.warning(f"음운분석 JSON 파싱 실패: '{word}' - {parse_error}")

            result_dict = {
                "word_index": word_index,
                "word": word,
                "phoneme_analysis": None,
                "success": False,
                "error": str(parse_error),
            }

            if block_id is not None:
                result_dict.update(
                    {
                        "block_id": block_id,
                        "difficulty_level": difficulty_level or "unknown",
                        "word_type": word_type or "unknown",
                        "definition": definition or "",
                    }
                )

            return result_dict

        except Exception as api_error:
            logger.error(
                f"음운분석 API 오류: '{word}' - {api_error}",
                exc_info=True,
            )
            # 심각한 API 오류는 상위 호출자로 전파하여 일관된 실패 처리를 보장
            raise RuntimeError(f"음운분석 실패: '{word}'") from api_error


def extract_difficult_words_from_blocks(blocks: List[Dict[str, Any]]) -> Set[str]:
    """
    블록 배열에서 어려운 단어들을 추출한다.

    Args:
        blocks: 블록 배열

    Returns:
        Set[str]: 어려운 단어들
    """
    difficult_words = set()

    for block in blocks:
        if "vocabularyAnalysis" in block and block["vocabularyAnalysis"]:
            for vocab_item in block["vocabularyAnalysis"]:
                if "word" in vocab_item:
                    word = vocab_item["word"].strip()
                    difficulty_level = vocab_item.get("difficultyLevel", "")

                    # medium 또는 hard 난이도의 단어들을 추출
                    if difficulty_level in ["medium", "hard"]:
                        difficult_words.add(word)

    logger.info(
        f"추출된 어려운 단어 {len(difficult_words)}개: {list(difficult_words)[:10]}{'...' if len(difficult_words) > 10 else ''}"
    )
    return difficult_words


async def analyze_words_phoneme(
    words: List[str],
    model_name: str = "claude-sonnet-4-20250514",
    max_concurrent: int = 3,  # 음운분석 최대 동시 요청 수 (API rate limit 고려)
) -> Dict[str, Any]:
    """
    단어 목록에 대해 음운분석을 수행한다.

    Args:
        words: 단어 목록
        model_name: 모델 이름
        max_concurrent: 최대 동시 요청 수

    Returns:
        Dict[str, Any]: 음운분석 결과
    """

    start_time = time.time()

    # 빈 문자열 제거
    suitable_words = [word.strip() for word in words if word and word.strip()]
    # 한국어 단어 필터링 (비한글 단어는 음운분석 스킵)
    korean_words = [w for w in suitable_words if _is_korean_word(w)]
    skipped = len(suitable_words) - len(korean_words)
    if skipped > 0:
        logger.info(f"음운분석 대상에서 비한글 단어 {skipped}개 스킵: 예시={suitable_words[:5]}")

    if not korean_words:
        logger.warning("분석할 단어가 없습니다")
        return {
            "phoneme_analyses": [],
            "metadata": {
                "model": model_name,
                "processing_time": 0.0,
                "total_words": 0,
                "unique_words": 0,
                "successful_analyses": 0,
                "failed_analyses": 0,
            },
        }
    logger.info(f"음운분석 시작: {len(korean_words)}개 단어 (스킵: {skipped})")

    # TODO: 모델 초기화 로직 수정
    # AI 모델 초기화 (음운분석 최적화 설정)
    model = ChatAnthropic(
        model=model_name,
        temperature=0,
        max_tokens=8000,  # 음운분석 응답이 잘리지 않도록 충분한 토큰
        timeout=60,  # 60초 타임아웃
        max_retries=3,  # 모델 레벨 재시도
    )

    # 동시 요청 수 제한을 위한 세마포어
    semaphore = asyncio.Semaphore(max_concurrent)

    # 모든 단어를 비동기로 동시 처리
    tasks = []
    for i, word in enumerate(korean_words):
        task = _analyze_single_word_phoneme(
            model=model,
            word=word,
            word_index=i,
            semaphore=semaphore,
        )
        tasks.append(task)

    # 모든 작업 동시 실행 및 결과 수집
    word_results = await asyncio.gather(*tasks)

    # 결과 정렬 및 분석
    word_results.sort(key=lambda x: x["word_index"])

    successful_analyses = sum(1 for result in word_results if result["success"])
    failed_analyses = len(word_results) - successful_analyses

    processing_time = round(time.time() - start_time, 2)

    logger.info(
        f"음운분석 완료: {successful_analyses}/{len(korean_words)}개 성공 ({processing_time}초)"
    )

    return {
        "phoneme_analyses": word_results,
        "metadata": {
            "model": model_name,
            "processing_time": processing_time,
            "total_words": len(words),
            "unique_words": len(suitable_words),
            "successful_analyses": successful_analyses,
            "failed_analyses": failed_analyses,
        },
    }


async def extract_and_analyze_phonemes_from_chunk_blocks(
    chunk_blocks: List[List[Dict[str, Any]]],
    model_name: str = "claude-sonnet-4-20250514",
    max_concurrent: int = 3,  # 음운분석 최대 동시 요청 수 (API rate limit 고려)
) -> Dict[str, Any]:
    """
    청크 블록들에서 어려운 단어를 추출하고 음운분석을 수행한다.

    Args:
        chunk_blocks: 청크 블록들
        model_name: 모델 이름
        max_concurrent: 최대 동시 요청 수

    Returns:
        Dict[str, Any]: 음운분석 결과
    """

    logger.info(f"청크별 어려운 단어 추출 시작 - {len(chunk_blocks)}개 청크")

    # 모든 블록을 평면화하여 단일 리스트로 만들기
    all_blocks = []
    for chunk_blocks_list in chunk_blocks:
        all_blocks.extend(chunk_blocks_list)

    logger.info(f"총 {len(all_blocks)}개 블록에서 어려운 단어 추출")

    # 어려운 단어 추출
    difficult_words = extract_difficult_words_from_blocks(all_blocks)

    if not difficult_words:
        logger.warning("분석할 어려운 단어가 없습니다")
        return {
            "phoneme_analyses": [],
            "metadata": {
                "model": model_name,
                "processing_time": 0.0,
                "total_words": 0,
                "unique_words": 0,
                "successful_analyses": 0,
                "failed_analyses": 0,
            },
        }

    # 중복 제거된 단어 리스트로 변환
    unique_words = list(difficult_words)

    logger.info(f"음운분석 대상: {len(unique_words)}개 단어")

    # 음운분석 수행
    result = await analyze_words_phoneme(
        words=unique_words,
        model_name=model_name,
        max_concurrent=max_concurrent,
    )

    return result


def extract_words_with_block_ids_from_blocks(
    blocks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    블록 배열에서 vocabularyAnalysis의 단어들을 블록 ID와 함께 추출한다.

    Args:
        blocks: 블록 배열

    Returns:
        List[Dict[str, Any]]: 블록 ID와 함께 추출된 단어들
    """
    words_with_block_ids = []

    for block_index, block in enumerate(blocks):
        # 블록 ID 생성 (기존에 있으면 사용, 없으면 인덱스 기반으로 생성)
        block_id = block.get("id", f"block_{block_index}")

        # vocabularyAnalysis가 있는 블록만 처리
        if "vocabularyAnalysis" in block and block["vocabularyAnalysis"]:
            for vocab_item in block["vocabularyAnalysis"]:
                if "word" in vocab_item:
                    word = vocab_item["word"].strip()
                    if word:  # 빈 문자열 제외
                        words_with_block_ids.append(
                            {
                                "word": word,
                                "block_id": block_id,
                                "difficulty_level": vocab_item.get(
                                    "difficultyLevel", "unknown"
                                ),
                                "word_type": vocab_item.get("wordType", "unknown"),
                                "definition": vocab_item.get("definition", ""),
                            }
                        )

    logger.info(f"블록별 단어 추출 완료: {len(words_with_block_ids)}개 단어")
    return words_with_block_ids


async def analyze_words_with_block_ids_phoneme(
    words_with_block_ids: List[Dict[str, Any]],
    model_name: str = "claude-sonnet-4-20250514",
    max_concurrent: int = 3,  # 음운분석 최대 동시 요청 수 (API rate limit 고려)
) -> Dict[str, Any]:
    """
    블록 ID가 포함된 단어 목록에 대해 음운분석을 수행한다.

    Args:
        words_with_block_ids: 블록 ID가 포함된 단어 목록
        model_name: 모델 이름
        max_concurrent: 최대 동시 요청 수

    Returns:
        Dict[str, Any]: 음운분석 결과
    """

    start_time = time.time()

    # 한국어 단어만 필터링
    filtered = [w for w in words_with_block_ids if _is_korean_word(w.get("word", ""))]
    skipped = len(words_with_block_ids) - len(filtered)

    if not filtered:
        logger.warning("분석할 단어가 없습니다")
        return {
            "block_word_phoneme_analyses": [],
            "metadata": {
                "model": model_name,
                "processing_time": 0.0,
                "total_words": 0,
                "unique_words": 0,
                "successful_analyses": 0,
                "failed_analyses": 0,
            },
        }

    logger.info(f"블록별 음운분석 시작: {len(filtered)}개 단어 (스킵: {skipped})")

    # AI 모델 초기화 (음운분석 최적화 설정)
    model = ChatAnthropic(
        model=model_name,
        temperature=0,
        max_tokens=8000,  # 음운분석 응답이 잘리지 않도록 충분한 토큰
        timeout=60,  # 60초 타임아웃
        max_retries=3,  # 모델 레벨 재시도
    )

    # 동시 요청 수 제한을 위한 세마포어
    semaphore = asyncio.Semaphore(max_concurrent)

    # 모든 단어를 비동기로 동시 처리
    tasks = []
    for i, word_data in enumerate(filtered):
        task = _analyze_single_word_phoneme(
            model=model,
            word=word_data["word"],
            word_index=i,
            semaphore=semaphore,
            block_id=word_data["block_id"],
            difficulty_level=word_data["difficulty_level"],
            word_type=word_data["word_type"],
            definition=word_data["definition"],
        )
        tasks.append(task)

    # 모든 작업 동시 실행 및 결과 수집
    word_results = await asyncio.gather(*tasks)

    # 결과 정렬 및 분석
    word_results.sort(key=lambda x: x["word_index"])

    successful_analyses = sum(1 for result in word_results if result["success"])
    failed_analyses = len(word_results) - successful_analyses

    processing_time = round(time.time() - start_time, 2)

    logger.info(
        f"블록별 음운분석 완료: {successful_analyses}/{len(filtered)}개 성공 ({processing_time}초)"
    )

    return {
        "block_word_phoneme_analyses": word_results,
        "metadata": {
            "model": model_name,
            "processing_time": processing_time,
            "total_words": len(filtered),
            "unique_words": len(set(word_data["word"] for word_data in filtered)),
            "successful_analyses": successful_analyses,
            "failed_analyses": failed_analyses,
            "skipped_non_korean": skipped,
        },
    }


async def extract_and_analyze_block_words_phoneme(
    transformed_blocks: List[Dict[str, Any]],
    model_name: str = "claude-sonnet-4-20250514",
    max_concurrent: int = 3,  # 음운분석 최대 동시 요청 수 (API rate limit 고려)
) -> Dict[str, Any]:
    """
    변환된 블록들에서 vocabularyAnalysis의 모든 단어를 추출하고 블록 ID와 함께 음운분석을 수행한다.

    Args:
        transformed_blocks: 변환된 블록들
        model_name: 모델 이름
        max_concurrent: 최대 동시 요청 수

    Returns:
        Dict[str, Any]: 음운분석 결과
    """

    logger.info(f"블록별 단어 음운분석 시작 - {len(transformed_blocks)}개 블록")

    # 블록별 단어 추출
    words_with_block_ids = extract_words_with_block_ids_from_blocks(transformed_blocks)

    if not words_with_block_ids:
        logger.warning("분석할 단어가 없습니다")
        return {
            "block_word_phoneme_analyses": [],
            "metadata": {
                "model": model_name,
                "processing_time": 0.0,
                "total_words": 0,
                "unique_words": 0,
                "successful_analyses": 0,
                "failed_analyses": 0,
            },
        }

    logger.info(f"블록별 음운분석 대상: {len(words_with_block_ids)}개 단어")

    # 음운분석 수행
    result = await analyze_words_with_block_ids_phoneme(
        words_with_block_ids=words_with_block_ids,
        model_name=model_name,
        max_concurrent=max_concurrent,
    )

    return result
