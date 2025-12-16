import logging
import os
from functools import lru_cache

import anthropic
from src.utils.env_config import get_anthropic_api_key

# 로거 설정
logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_anthropic_client():
    """Anthropic 클라이언트 인스턴스 생성 (캐시)"""
    try:
        api_key = get_anthropic_api_key(required=True)
        client = anthropic.Anthropic(api_key=api_key)
        return client
    except Exception as e:
        logger.error(f"Anthropic 클라이언트 초기화 실패: {e}")
        return None


def count_tokens(text: str, model: str = "claude-sonnet-4-20250514") -> int:
    """토큰 수 계산"""
    
    # 빈 텍스트 처리
    if not text or not text.strip():
        return 0
    
    # 너무 긴 텍스트는 즉시 추정값 반환 (API 호출 시간 단축)
    if len(text) > 500000:  # 50만 글자 이상
        estimated_tokens = len(text) // 4
        logger.info(f"대용량 텍스트 - 문자 기반 추정 토큰: {estimated_tokens:,}")
        return estimated_tokens

    try:
        client = get_anthropic_client()
        if not client:
            logger.warning("Anthropic 클라이언트 없음 - 추정값 사용")
            estimated_tokens = len(text) // 4
            return estimated_tokens

        # 토큰 계산 시도 (타임아웃 방지를 위해 간단한 메시지 사용)
        response = client.messages.count_tokens(
            model=model,
            messages=[{"role": "user", "content": text[:10000]}],  # 처음 10,000자만 사용
        )
        
        # 전체 텍스트에 비례하여 계산
        if len(text) > 10000:
            ratio = len(text) / 10000
            estimated_total = int(response.input_tokens * ratio)
            logger.debug(f"API 기반 추정 토큰: {estimated_total:,}")
            return estimated_total
        else:
            logger.debug(f"API 계산 토큰: {response.input_tokens:,}")
            return response.input_tokens
            
    except Exception as e:
        logger.warning(f"Anthropic 토큰 계산 실패: {e} - 추정값 사용")
        
        # 문자 수 기반 추정 (더 정확한 계산)
        # 한국어/영어 혼합 텍스트에 대한 개선된 추정
        if any('\u4e00' <= char <= '\u9fff' or '\uac00' <= char <= '\ud7af' for char in text[:1000]):
            # 한중일 문자가 포함된 경우 (더 많은 토큰 필요)
            estimated_tokens = len(text) // 2
        else:
            # 영어 위주인 경우
            estimated_tokens = len(text) // 4
            
        logger.info(f"문자 기반 추정 토큰: {estimated_tokens:,}")
        return estimated_tokens


def validate_model(model: str) -> bool:
    """지원되는 Claude 모델인지 검증 (Anthropic 공식 문서 기준)"""
    supported_models = [
        # Claude 4 시리즈
        "claude-opus-4-20250514",
        "claude-sonnet-4-20250514",
        # Claude 3.7 시리즈
        "claude-3-7-sonnet-20250219",
        "claude-3-7-sonnet-latest",
        # Claude 3.5 시리즈
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-latest",
        "claude-3-5-sonnet-20240620",
        "claude-3-5-haiku-20241022",
        "claude-3-5-haiku-latest",
        # Claude 3 시리즈
        "claude-3-opus-20240229",
        "claude-3-opus-latest",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]
    return model in supported_models


def get_supported_models() -> list[str]:
    """지원되는 Claude 모델 목록 반환 (최신 모델 우선)"""
    return [
        # Claude 4 시리즈 (최신)
        "claude-opus-4-20250514",
        "claude-sonnet-4-20250514",
        # Claude 3.7 시리즈
        "claude-3-7-sonnet-20250219",
        # Claude 3.5 시리즈
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620",
        "claude-3-5-haiku-20241022",
        # Claude 3 시리즈
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]
