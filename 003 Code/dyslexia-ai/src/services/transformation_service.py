import asyncio
import hashlib
import json
import logging
import random
import re
import time
from typing import Any, Awaitable, Callable, Dict, List, Optional, TypeVar

from langchain_anthropic import ChatAnthropic

from src.core.prompts import create_block_conversion_prompt
from src.services.redis_service import RedisService
from src.services.image_generation_service import generate_image_for_page_block
from src.utils.anthropic_client import count_tokens, get_anthropic_client

# 타입 변수 정의
T = TypeVar("T")

# 로거 설정
logger = logging.getLogger(__name__)


def clean_json_response(text: str) -> List[Dict[str, Any]]:
    """JSON 응답을 안전하게 파싱하는 함수"""

    try:
        # 1차 시도: 직접 파싱
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict):
            return [parsed]
        else:
            logger.warning(f"예상치 못한 JSON 타입: {type(parsed)}")
            return []

    except json.JSONDecodeError:
        try:
            # 2차 시도: JSON 객체나 배열 추출
            # JSON 배열 패턴 찾기
            array_pattern = r"\[.*?\]"
            array_match = re.search(array_pattern, text, re.DOTALL)

            if array_match:
                try:
                    parsed = json.loads(array_match.group())
                    if isinstance(parsed, list):
                        return parsed
                except json.JSONDecodeError:
                    pass

            # JSON 객체 패턴 찾기
            object_pattern = r"\{.*?\}"
            object_matches = re.findall(object_pattern, text, re.DOTALL)

            if object_matches:
                valid_objects = []
                for match in object_matches:
                    try:
                        parsed = json.loads(match)
                        if isinstance(parsed, dict):
                            valid_objects.append(parsed)
                    except json.JSONDecodeError:
                        continue

                if valid_objects:
                    return valid_objects

        except Exception as e:
            logger.error(f"JSON 파싱 2차 시도 실패: {e}")

        # 3차 시도: 텍스트 정리 후 파싱
        try:
            # 백틱 제거
            cleaned_text = text.strip().strip("```json").strip("```").strip()

            # 개행 문자 제거 후 파싱
            cleaned_text = re.sub(r"\n\s*", " ", cleaned_text)

            parsed = json.loads(cleaned_text)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                return [parsed]

        except json.JSONDecodeError:
            logger.error(f"JSON 파싱 3차 시도도 실패")

            logger.error(f"JSON 파싱 실패, 원본 텍스트: {text[:200]}...")
        return []


def create_redis_info(
    saved: bool,
    hash_key: Optional[str] = None,
    expire_hours: Optional[int] = None,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """Redis 정보 딕셔너리 생성"""

    return {
        "saved": saved,
        "hash_key": hash_key,
        "expire_hours": expire_hours,
        "redis_key": f"output:{hash_key}" if hash_key else None,
        "error": error,
    }


async def exponential_backoff_retry(
    async_func: Callable[[], Awaitable[T]],
    max_retries: int = 5,
    base_delay: float = 3.0,
    max_delay: float = 30.0,
    jitter: bool = True,
) -> T:
    """지수적 백오프와 지터를 사용한 재시도 로직"""

    for attempt in range(max_retries + 1):
        try:
            return await async_func()
        except Exception as e:
            if attempt == max_retries:
                logger.error(f"최대 재시도 횟수 도달. 마지막 오류: {e}")
                raise e

            # 지수 백오프 계산
            delay = min(base_delay * (2**attempt), max_delay)

            # 지터 추가 (랜덤 요소)
            if jitter:
                delay = delay * (0.5 + random.random() * 0.5)

            logger.info(
                f"재시도 {attempt + 1}/{max_retries}, {delay:.2f}초 후 재시도..."
            )
            await asyncio.sleep(delay)


async def process_single_chunk_async(
    model: ChatAnthropic,
    prompt_template: str,
    chunk: str,
    chunk_index: int,
    total_chunks: int,
    chunk_token_count: int,
    semaphore: asyncio.Semaphore,
) -> Dict[str, Any]:
    """단일 청크를 비동기로 처리하는 함수"""

    async with semaphore:
        logger.info(
            f"청크 {chunk_index + 1}/{total_chunks} 처리 시작 (토큰: {chunk_token_count})"
        )

        # 재시도 가능한 API 호출 함수
        async def async_api_call() -> str:
            try:
                chain = prompt_template | model
                result = await chain.ainvoke(
                    {"content": chunk}
                )

                logger.info(f"API 호출 성공 - Response type: {type(result)}")
                return result.content

            except Exception as e:
                logger.error(f"청크 {chunk_index + 1} API 호출 오류: {e}")
                logger.error(f"Exception type: {type(e)}")
                raise e

        # 지수 백오프 재시도로 API 호출
        content = await exponential_backoff_retry(async_api_call, max_retries=2)

        # JSON 파싱
        blocks = clean_json_response(content)

        if not blocks:
            logger.warning(f"청크 {chunk_index + 1}: JSON 파싱 실패, 빈 결과 반환")
            blocks = []

        logger.info(
            f"청크 {chunk_index + 1}/{total_chunks} 처리 완료 - {len(blocks)}개 블록 생성"
        )

        return {
            "chunk_index": chunk_index,
            "blocks": blocks,
            "block_count": len(blocks),
            "chunk_token_count": chunk_token_count,
        }


def save_to_redis_if_enabled(
    result: Dict[str, Any], save_to_redis: bool, expire_hours: int
) -> Dict[str, Any]:
    """Redis 저장 로직 (중복 코드 제거)"""
    
    if not save_to_redis:
        return result

    try:
        redis_service = RedisService()
        redis_key = redis_service.save_output_by_hash(result, expire_hours)

        if redis_key:
            logger.info(f"결과 데이터 Redis 저장 성공: {redis_key[:16]}...")
            result["redis_info"] = create_redis_info(
                saved=True, hash_key=redis_key, expire_hours=expire_hours
            )
        else:
            logger.warning("결과 데이터 Redis 저장 실패")
            result["redis_info"] = create_redis_info(
                saved=False, error="Redis 저장 실패"
            )

    except Exception as e:
        logger.error(f"Redis 저장 중 오류 발생: {e}")
        result["redis_info"] = create_redis_info(saved=False, error=str(e))

    return result


async def transform_content_to_blocks(
    content: List[str],
    model_name: str = "claude-sonnet-4-20250514",
    max_concurrent: int = 8,
    image_interval: int = 15,
    word_limit: int = 15,
    vocabulary_interval: int = 5,
    save_to_redis: bool = True,
    expire_hours: int = 24,
    generate_images: bool = True,
) -> Dict[str, Any]:
    """전처리된 의미적 청크들을 난독증 아동 친화적 블록 구조로 비동기 동시 변환"""

    try:
        start_time = time.time()

        # AI 모델 초기화
        model = ChatAnthropic(
            model=model_name,
            temperature=0,
            max_tokens=8192,
            timeout=300.0,
            max_retries=2,
        )

        # 프롬프트 템플릿 생성
        prompt_template = create_block_conversion_prompt(
            image_interval=image_interval,
            word_limit=word_limit,
            vocabulary_interval=vocabulary_interval,
        )

        logger.info(f"블록 변환 시작 - {len(content)}개 청크, 모델: {model_name}")

        # 각 청크의 토큰 수 계산
        chunk_tokens = []
        total_input_tokens = 0

        for i, chunk in enumerate(content):
            tokens = count_tokens(chunk, model_name)
            chunk_tokens.append(tokens)
            total_input_tokens += tokens

        # 동시 요청 수 제한을 위한 세마포어
        semaphore = asyncio.Semaphore(max_concurrent)

        # 모든 청크를 비동기로 동시 처리
        tasks = []
        for i, (chunk, chunk_token_count) in enumerate(zip(content, chunk_tokens)):
            task = process_single_chunk_async(
                model=model,
                prompt_template=prompt_template,
                chunk=chunk,
                chunk_index=i,
                total_chunks=len(content),
                chunk_token_count=chunk_token_count,
                semaphore=semaphore,
            )
            tasks.append(task)

        # 모든 작업 동시 실행 및 결과 수집
        chunk_results = await asyncio.gather(*tasks)

        # 결과 정렬 및 병합
        chunk_results.sort(key=lambda x: x["chunk_index"])

        all_transformed_blocks = []
        chunk_blocks = []
        total_blocks = 0

        for result in chunk_results:
            all_transformed_blocks.extend(result["blocks"])
            chunk_blocks.append(result["blocks"])
            total_blocks += result["block_count"]

        block_processing_time = round(time.time() - start_time, 2)

        logger.info(
            f"블록 변환 완료 - {total_blocks}개 블록 생성 ({block_processing_time}초)"
        )
        
        # PAGE_IMAGE 블록 이미지 생성 처리
        if generate_images:
            logger.info("PAGE_IMAGE 블록 이미지 생성 시작...")
            image_generation_start = time.time()
            
            try:
                # PAGE_IMAGE 블록 찾기
                page_image_blocks = []
                for i, block in enumerate(all_transformed_blocks):
                    if block.get("type") == "PAGE_IMAGE":
                        page_image_blocks.append((i, block))
                
                if page_image_blocks:
                    logger.info(f"{len(page_image_blocks)}개 PAGE_IMAGE 블록 발견")
                    
                    # 이미지 생성 작업 생성
                    image_tasks = []
                    for i, (block_index, block) in enumerate(page_image_blocks):
                        task = generate_image_for_page_block(
                            page_image_block=block,
                            style="any",
                            size="1536x1024",
                            model="google/nano-banana",
                            output_format="jpg",
                        )
                        image_tasks.append((block_index, task))
                    
                    # 이미지 생성 실행 (동시 처리)
                    try:
                        image_results = await asyncio.gather(*[task for _, task in image_tasks], return_exceptions=True)
                        
                        # 성공한 결과와 실패한 결과 분리
                        successful_results = []
                        failed_results = []
                        
                        for i, result in enumerate(image_results):
                            if isinstance(result, Exception):
                                logger.error(f"이미지 생성 {i+1} 실패: {result}")
                                failed_results.append(result)
                                # 실패한 경우 원본 블록 유지
                                successful_results.append(page_image_blocks[i][1])
                            else:
                                successful_results.append(result)
                        
                        # 생성된 이미지 정보를 원본 블록에 업데이트
                        for (block_index, _), updated_block in zip(image_tasks, successful_results):
                            all_transformed_blocks[block_index] = updated_block
                        
                        image_generation_time = round(time.time() - image_generation_start, 2)
                        
                        # 성공적으로 생성된 이미지 수 계산
                        successful_images = sum(1 for block in successful_results if block.get("url"))
                        
                        logger.info(
                            f"이미지 생성 완료 - {successful_images}/{len(page_image_blocks)}개 성공 ({image_generation_time}초)"
                        )
                        
                    except Exception as e:
                        logger.error(f"이미지 생성 전체 실패: {e}")
                        image_generation_time = round(time.time() - image_generation_start, 2)
                        
                else:
                    logger.info("PAGE_IMAGE 블록이 없어 이미지 생성을 건너뜁니다.")
                    image_generation_time = 0
                    
            except Exception as e:
                logger.error(f"이미지 생성 처리 중 오류: {e}")
                image_generation_time = round(time.time() - image_generation_start, 2)
                
        else:
            logger.info("이미지 생성이 비활성화되어 있습니다.")
            image_generation_time = 0

        # 결과 데이터 구조 생성
        total_processing_time = round(time.time() - start_time, 2)
        
        result = {
            "transformed_blocks": all_transformed_blocks,
            "chunk_blocks": chunk_blocks,
            "metadata": {
                "model": model_name,
                "total_blocks": total_blocks,
                "processing_time": block_processing_time,
                "image_generation_time": image_generation_time,
                "total_processing_time": total_processing_time,
                "input_chunks": len(content),
                "total_input_tokens": total_input_tokens,
                "max_concurrent": max_concurrent,
                "processing_method": "async_concurrent_blocks_with_images",
                "images_generated": generate_images,
            },
        }

        # Redis 저장 처리
        result = save_to_redis_if_enabled(result, save_to_redis, expire_hours)

        return result

    except Exception as e:
        # 상위 호출자(prd_async_processor)에서 정확한 job_id 문맥으로 처리되도록 메시지만 풍부하게
        logger.error(
            f"콘텐츠 변환 중 오류 발생: {str(e)}", exc_info=True
        )
        raise RuntimeError(f"콘텐츠 변환 중 오류: {str(e)}") from e


def get_cached_result_by_hash(hash_key: str) -> Optional[Dict[str, Any]]:
    """해시 키로 캐시된 결과 조회"""

    try:
        redis_service = RedisService()
        cached_result = redis_service.get_output_by_hash(hash_key)

        if cached_result:
            logger.info(f"캐시된 결과 조회 성공: {hash_key[:16]}...")
            return cached_result
        else:
            logger.warning(f"캐시된 결과 없음: {hash_key[:16]}...")
            return None

    except Exception as e:
        logger.error(f"캐시 조회 중 오류 발생: {e}")
        return None


def get_content_hash(content: List[str], model_name: str, **kwargs) -> str:
    """입력 컨텐츠와 설정의 해시 생성 (중복 처리 방지용)"""

    # 입력 데이터 구조 생성
    input_data = {"content": content, "model_name": model_name, "settings": kwargs}

    # JSON 문자열로 변환 후 해시 생성
    json_str = json.dumps(input_data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(json_str.encode("utf-8")).hexdigest()


def create_cache_info(
    cache_hit: bool,
    input_hash: str,
    retrieved_from_cache: bool = False,
    newly_cached: bool = False,
) -> Dict[str, Any]:
    """캐시 정보 딕셔너리 생성 (중복 코드 제거)"""
    return {
        "cache_hit": cache_hit,
        "input_hash": input_hash,
        "retrieved_from_cache": retrieved_from_cache,
        "newly_cached": newly_cached,
    }


async def transform_with_caching(
    content: List[str],
    model_name: str = "claude-sonnet-4-20250514",
    max_concurrent: int = 8,
    image_interval: int = 15,
    word_limit: int = 15,
    vocabulary_interval: int = 5,
    expire_hours: int = 24,
    use_cache: bool = True,
    generate_images: bool = True,
) -> Dict[str, Any]:
    """캐싱을 지원하는 블록 변환 함수"""

    # 캐시 확인
    if use_cache:
        input_hash = get_content_hash(
            content=content,
            model_name=model_name,
            max_concurrent=max_concurrent,
            image_interval=image_interval,
            word_limit=word_limit,
            vocabulary_interval=vocabulary_interval,
            generate_images=generate_images,
        )

        logger.info(f"캐시 확인 중... (해시: {input_hash[:16]}...)")

        # 캐시된 결과 조회
        redis_service = RedisService()
        cached_result = redis_service.get_output_by_hash(input_hash)

        if cached_result:
            logger.info(f"캐시된 결과 발견! 처리 시간 단축")
            cached_result["cache_info"] = create_cache_info(
                cache_hit=True, input_hash=input_hash, retrieved_from_cache=True
            )
            return cached_result
        else:
            logger.warning(f"캐시된 결과 없음. 새로 처리합니다.")

    # 새로운 처리 실행
    result = await transform_content_to_blocks(
        content=content,
        model_name=model_name,
        max_concurrent=max_concurrent,
        image_interval=image_interval,
        word_limit=word_limit,
        vocabulary_interval=vocabulary_interval,
        save_to_redis=use_cache,
        expire_hours=expire_hours,
        generate_images=generate_images,
    )

    # 캐시 정보 추가
    if use_cache:
        input_hash = get_content_hash(
            content=content,
            model_name=model_name,
            max_concurrent=max_concurrent,
            image_interval=image_interval,
            word_limit=word_limit,
            vocabulary_interval=vocabulary_interval,
            generate_images=generate_images,
        )

        result["cache_info"] = create_cache_info(
            cache_hit=False,
            input_hash=input_hash,
            newly_cached=result.get("redis_info", {}).get("saved", False),
        )

    return result
