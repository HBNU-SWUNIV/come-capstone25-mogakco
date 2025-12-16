import logging
import os
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, Query

from src.models import ProcessingMetadata, TransformationMetadata
from src.services.orchestration_service import execute_complete_pipeline

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transform", tags=["Content Transformation"])

TEMP_DIR = os.getenv("TEMP_DIR", "./temp")  # 임시 디렉토리 설정


@router.post(
    "/pdf-to-dyslexia-blocks",
    summary="PDF to Dyslexia-Friendly Blocks Transformation",
    description="Transform PDF documents into dyslexia-friendly text blocks with phoneme analysis",
)
async def transform_pdf_to_dyslexia_blocks(
    file: UploadFile = File(...),                       # PDF 파일
    remove_headers_footers: bool = True,                # 머리말/꼬리말 제거 여부
    header_height: float = 30.0,                        # 머리말 높이
    footer_height: float = 30.0,                        # 꼬리말 높이
    max_tokens: int = 12000,                            # 청크당 최대 토큰 수
    model_name: str = "claude-sonnet-4-20250514",       # 사용할 Claude 모델명
    max_concurrent: int = 8,                            # 최대 동시 요청 수
    image_interval: int = 15,                           # PAGE_IMAGE 생성 간격
    word_limit: int = 15,                               # 한 문장당 단어 수 제한
    vocabulary_interval: int = 1,                       # vocabularyAnalysis 생성 간격
    enable_phoneme_analysis: bool = True,               # 음운분석 활성화 여부
    phoneme_max_concurrent: int = 3,                    # 음운분석 최대 동시 요청 수
    enable_block_word_phoneme_analysis: bool = True,    # 블록별 단어 음운분석 활성화 여부
    block_word_phoneme_max_concurrent: int = 3,         # 블록별 단어 음운분석 최대 동시 요청 수
    task_id: Optional[str] = Query(None, description="진행률 추적을 위한 태스크 ID (선택사항)"),
):
    """PDF 문서를 난독증 아동이 읽기 쉬운 텍스트 블록으로 변환하는 통합 서비스"""

    try:
        print(f"PDF 변환 시작: {file.filename}")
        
        # 오케스트레이션 서비스를 통한 완전한 변환 파이프라인 실행
        result = await execute_complete_pipeline(
            file=file,
            model_name=model_name,
            max_concurrent=max_concurrent,
            temp_dir=TEMP_DIR,
            remove_headers_footers=remove_headers_footers,
            header_height=header_height,
            footer_height=footer_height,
            max_tokens=max_tokens,
            image_interval=image_interval,
            word_limit=word_limit,
            vocabulary_interval=vocabulary_interval,
            enable_phoneme_analysis=enable_phoneme_analysis,
            phoneme_max_concurrent=phoneme_max_concurrent,
            enable_block_word_phoneme_analysis=enable_block_word_phoneme_analysis,
            block_word_phoneme_max_concurrent=block_word_phoneme_max_concurrent,
            task_id=task_id,
        )

        # 결과 구조는 이미 오케스트레이션 서비스에서 완성된 형태로 반환됨
        if result.get("success"):
            filename = result.get("data", {}).get("filename", "unknown")
            processing_time = result.get("metadata", {}).get("total_processing_time", 0)
            logger.info(f"PDF 변환 완료: {filename} ({processing_time:.2f}초)")
        else:
            logger.error(f"PDF 변환 실패: {result.get('error', 'unknown error')}")
        
        return result

    except Exception as e:
        logger.error(f"PDF 변환 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"PDF 변환 처리 중 오류가 발생했습니다: {str(e)}"
        ) 