from enum import Enum


class ProcessingStep(Enum):
    """
    처리 단계 열거형
    
    Attributes:
        PREPROCESSING: 전처리
        BLOCK_TRANSFORMATION: 블록 변환
        PHONEME_ANALYSIS: 음운분석
        BLOCK_WORD_PHONEME_ANALYSIS: 블록별 단어 음운분석
        POST_PROCESSING: 후처리
    """

    PREPROCESSING = "preprocessing"
    BLOCK_TRANSFORMATION = "block_transformation"
    PHONEME_ANALYSIS = "phoneme_analysis"
    BLOCK_WORD_PHONEME_ANALYSIS = "block_word_phoneme_analysis"
    POST_PROCESSING = "post_processing"
