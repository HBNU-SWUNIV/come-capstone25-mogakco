import os
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.models import PDFProcessResponse, ProcessingMetadata, PreprocessingOptions
from src.services import preprocessing_service
from src.utils.anthropic_client import validate_model, get_supported_models

router = APIRouter(prefix="/preprocess", tags=["PDF Processing"])

TEMP_DIR = os.getenv("TEMP_DIR", "./temp")  # 임시 디렉토리 설정


@router.post(
    "/pdf",
    response_model=PDFProcessResponse,
    summary="Extract and Preprocess Text from PDF",
    description="PDF 텍스트 추출 및 전처리: 텍스트 추출, 정규화, 그리디 청킹",
)
async def preprocess_pdf(
    file: UploadFile = File(...),  # PDF 파일
    remove_headers_footers: bool = True,  # 머리말/꼬리말 제거 여부
    header_height: float = 30.0,  # 머리말 높이 (포인트)
    footer_height: float = 30.0,  # 꼬리말 높이 (포인트)
    return_text: bool = True,  # 전체 텍스트 반환 여부
    return_chunks: bool = True,  # 청크 배열 반환 여부
    max_tokens: int = 4000,  # 최대 토큰 수
    model: str = "claude-sonnet-4-20250514",  # Claude 모델명
):
    """PDF에서 텍스트를 추출하고 그리디 알고리즘으로 청킹을 수행합니다."""

    try:
        if max_tokens < 0 or max_tokens > 120000: # TODO: max_tokens 값을 Config 값에서 관리하도록 수정
            raise HTTPException(
                status_code=400, detail="Max tokens must be between 0 and 120,000"
            )

        if not validate_model(model):
            supported_models = get_supported_models()
            raise HTTPException(
                status_code=400,
                detail=f"지원되지 않는 모델: {model}. 지원 모델: {', '.join(supported_models[:3])}...",
            )

        if not return_text and not return_chunks:
            raise HTTPException(
                status_code=400,
                detail="At least one of return_text or return_chunks must be True",
            )

        options = PreprocessingOptions(
            temp_dir=TEMP_DIR,
            remove_headers_footers=remove_headers_footers,
            header_height=header_height,
            footer_height=footer_height,
            max_tokens=max_tokens,
        )

        result = preprocessing_service.run_preprocessing_pipeline(
            file=file,
            options=options,
            return_text=return_text,
            return_chunks=return_chunks,
            model=model,
        )

        return PDFProcessResponse(
            filename=file.filename,
            text=result.get("text"),
            chunks=result.get("chunks"),
            metadata=ProcessingMetadata(
                total_tokens=result["total_tokens"],
                processing_time=result["processing_time"],
                total_chunks=result.get("total_chunks", 0),
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
