from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class VocabularyItem(BaseModel):
    word: str = Field(min_length=1)
    start_index: int = Field(ge=0)
    end_index: int = Field(ge=0)
    definition: Optional[str] = None
    simplified_definition: Optional[str] = None
    examples: Optional[List[str]] = None
    difficulty_level: Optional[str] = None
    reason: Optional[str] = None
    grade_level: Optional[int] = None
    phoneme_analysis: Optional[Dict[str, Any]] = None
    phoneme_analysis_json: Optional[str] = None


class BlockVocabularyInput(BaseModel):
    page_number: int = Field(ge=1)
    block_id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class StartVocabularyRequest(BaseModel):
    job_id: str = Field(min_length=1)
    textbook_id: int = Field(ge=1)
    items: List[BlockVocabularyInput] = Field(min_length=1)

    # 옵션들
    model_name: str = Field(default="gpt-4o-mini")
    max_concurrent: int = Field(default=5, ge=1, le=20)
    rate_limit_per_min: int = Field(default=30, ge=1, le=240)
    enable_phoneme: bool = Field(default=False)


class AsyncStartResponse(BaseModel):
    job_id: str
    status: str
    message: str


class VocabJobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    total_blocks: int
    completed_blocks: int
    failed_blocks: int


class BlockVocabularyResult(BaseModel):
    job_id: str
    textbook_id: int
    page_number: int
    block_id: str
    original_sentence: str
    vocabulary_items: List[VocabularyItem]
    created_at: str


class VocabJobResult(BaseModel):
    job_id: str
    textbook_id: int
    blocks: List[BlockVocabularyResult]
    summary: Dict[str, Any]
    created_at: str
