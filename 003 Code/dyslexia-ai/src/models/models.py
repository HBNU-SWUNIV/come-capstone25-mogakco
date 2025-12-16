from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .enums import ProcessingStep


class ProcessingMetadata(BaseModel):
    """PDF 전처리 메타데이터 모델"""
    total_tokens: int = Field(description="총 토큰 수", ge=0)
    processing_time: float = Field(description="처리 시간 (초)", ge=0.0)
    total_chunks: Optional[int] = Field(default=0, description="생성된 총 청크 수", ge=0)


class TransformationMetadata(BaseModel):
    """AI 변환 메타데이터 모델"""
    model: str = Field(description="LLM 모델명", min_length=1)
    total_blocks: int = Field(description="총 블록 수", ge=0)
    processing_time: float = Field(description="처리 시간 (초)", ge=0.0)
    input_chunks: int = Field(description="입력 청크 수", ge=0)
    total_input_tokens: Optional[int] = Field(default=0, description="총 입력 토큰 수", ge=0)
    avg_blocks_per_chunk: Optional[float] = Field(default=0.0, description="청크당 평균 블록 수", ge=0.0)


class PDFProcessResponse(BaseModel):
    """PDF 처리 응답 모델"""
    filename: str = Field(description="파일명", min_length=1)
    text: Optional[str] = Field(default=None, description="추출된 텍스트")
    chunks: Optional[List[str]] = Field(default=None, description="생성된 청크들")
    metadata: ProcessingMetadata = Field(description="처리 메타데이터")


class ChunkResponse(BaseModel):
    """청크 생성 응답 모델"""
    chunks: List[str] = Field(description="청크들", min_length=0)
    total_chunks: int = Field(description="총 청크 수", ge=0)

    @model_validator(mode='after')
    def validate_chunk_consistency(self) -> 'ChunkResponse':
        """총 청크 수가 실제 청크 리스트 길이와 일치하는지 검증"""
        actual_count = len(self.chunks)
        if self.total_chunks != actual_count:
            raise ValueError(f"total_chunks ({self.total_chunks})가 실제 청크 개수 ({actual_count})와 일치하지 않습니다")
        return self


class TextExtractionResponse(BaseModel):
    """텍스트 추출 응답 모델"""
    filename: str = Field(description="파일명", min_length=1)
    text: str = Field(description="추출된 텍스트")
    total_sentences: int = Field(description="총 문장 수", ge=0)


class TransformationRequest(BaseModel):
    """변환 요청 모델"""
    content: List[str] = Field(description="전처리에서 생성된 청크 배열", min_length=1)
    model: str = Field(default="claude-sonnet-4-20250514", description="Claude 모델명", min_length=1)
    image_interval: int = Field(default=12, description="PAGE_IMAGE 생성 간격 (TEXT 블록 개수)", ge=1, le=50)
    word_limit: int = Field(default=15, description="한 문장당 단어 수 제한", ge=5, le=30)
    vocabulary_interval: int = Field(default=5, description="vocabularyAnalysis 생성 간격 (TEXT 블록 개수)", ge=1, le=20)
    enable_phoneme_analysis: bool = Field(default=True, description="음운분석 활성화 여부")
    phoneme_max_concurrent: int = Field(default=3, description="음운분석 최대 동시 요청 수", ge=1, le=10)


# Hierarchical Option Models

class PreprocessingOptions(BaseModel):
    """전처리 옵션"""
    temp_dir: str = Field(default="./temp", description="임시 디렉토리 경로", min_length=1)
    remove_headers_footers: bool = Field(default=True, description="머리말/꼬리말 제거 여부")
    header_height: float = Field(default=30.0, ge=0, le=100, description="머리말 높이 (pt)")
    footer_height: float = Field(default=30.0, ge=0, le=100, description="꼬리말 높이 (pt)")
    max_tokens: int = Field(default=12000, ge=1000, le=200000, description="최대 토큰 수")


class TransformationOptions(BaseModel):
    """변환 옵션"""
    image_interval: int = Field(default=15, ge=1, le=50, description="이미지 생성 간격")
    word_limit: int = Field(default=15, ge=5, le=30, description="문장당 단어 제한")
    vocabulary_interval: int = Field(default=5, ge=1, le=20, description="어휘 분석 간격")


class PhonemeAnalysisOptions(BaseModel):
    """음운분석 옵션"""
    enable_phoneme_analysis: bool = Field(default=True, description="음운분석 활성화 여부")
    phoneme_max_concurrent: int = Field(default=3, ge=1, le=10, description="음운분석 최대 동시 실행 수")
    enable_block_word_phoneme_analysis: bool = Field(default=True, description="블록별 단어 음운분석 활성화 여부")
    block_word_phoneme_max_concurrent: int = Field(default=3, ge=1, le=10, description="블록별 단어 음운분석 최대 동시 실행 수")


class OrchestrationOptions(BaseModel):
    """오케스트레이션 옵션을 담는 Pydantic 모델"""
    
    # 공통 옵션
    model_name: str = Field(default="claude-sonnet-4-20250514", description="사용할 모델명", min_length=1)
    max_concurrent: int = Field(default=8, ge=1, le=20, description="최대 동시 실행 수")
    
    # 세부 옵션들
    preprocessing: PreprocessingOptions = Field(default_factory=PreprocessingOptions)
    transformation: TransformationOptions = Field(default_factory=TransformationOptions)
    phoneme_analysis: PhonemeAnalysisOptions = Field(default_factory=PhonemeAnalysisOptions)
    
    model_config = ConfigDict(
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "model_name": "claude-sonnet-4-20250514",
                "max_concurrent": 8,
                "preprocessing": {
                    "temp_dir": "./temp",
                    "remove_headers_footers": True,
                    "header_height": 30.0,
                    "footer_height": 30.0,
                    "max_tokens": 12000
                },
                "transformation": {
                    "image_interval": 15,
                    "word_limit": 15,
                    "vocabulary_interval": 5
                },
                "phoneme_analysis": {
                    "enable_phoneme_analysis": True,
                    "phoneme_max_concurrent": 3,
                    "enable_block_word_phoneme_analysis": True,
                    "block_word_phoneme_max_concurrent": 3
                }
            }
        }
    )


class StepResult(BaseModel):
    """각 단계의 결과를 담는 Pydantic 모델"""
    
    step: ProcessingStep = Field(description="처리 단계")
    success: bool = Field(description="성공 여부")
    processing_time: float = Field(description="처리 시간 (초)", ge=0.0)
    data: Dict[str, Any] = Field(default_factory=dict, description="처리 결과")
    error: Optional[str] = Field(default=None, description="오류 메시지")
    
    model_config = ConfigDict(
        validate_assignment=True
    )

    @model_validator(mode='after')
    def validate_error_message(self) -> 'StepResult':
        """실패 시 에러 메시지가 없으면 기본 메시지를 설정"""
        if not self.success and not self.error:
            self.error = "Unknown error occurred"
        return self
