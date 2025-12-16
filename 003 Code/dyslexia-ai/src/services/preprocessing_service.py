import logging
import os
import re
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List

import pdfplumber
from fastapi import HTTPException, UploadFile

from src.utils.anthropic_client import count_tokens
from src.models import PreprocessingOptions

# 로거 설정
logger = logging.getLogger(__name__)


def extract_text_from_page(
    page,
    header_height: float = 30,
    footer_height: float = 30,
) -> str:
    """
    페이지에서 텍스트를 추출하며, 선택적으로 머리말과 꼬리말을 제거한다.

    Args:
        page: 페이지 객체
        header_height: 머리말 높이(pt)
        footer_height: 꼬리말 높이(pt)

    Returns:
        str: 페이지에서 추출된 텍스트

    Raises:
        HTTPException: 페이지 추출 실패 시
    """

    page_height = page.height

    content_bbox = (
        0,
        header_height,
        page.width,
        page_height - footer_height,
    )

    cropped_page = page.crop(content_bbox)
    return cropped_page.extract_text() or ""


def normalize_text_structure(text: str) -> str:
    """
    PDF에서 추출된 원본 텍스트를 정규화하여 문단 분할에 적합하게 만든다.

    Args:
        text: 텍스트

    Returns:
        str: 정규화된 텍스트

    Raises:
        HTTPException: 텍스트 정규화 실패 시
    """

    logger.info(f"텍스트 정규화 중 (길이: {len(text):,} 문자)")

    # TODO: 문단을 추출하는 로직의 한계가 분명함. NLP 임베딩 유사도 기반으로 문단 추출하는 방법 고민해보기
    # 연속된 줄바꿈 패턴
    original_breaks = len(re.findall(r"\n{2,}", text))
    text = re.sub(r"\n{2,}", "##P_BREAK##", text)

    # 문장 끝 + 줄바꿈 + 대문자 시작 패턴
    sentence_breaks = len(re.findall(r'([.!?"])\n([A-Z])', text))
    text = re.sub(r'([.!?"])\n([A-Z])', r"\1##P_BREAK##\2", text)

    # 문장 끝 + 줄바꿈 + 번호 목록 시작 패턴
    number_breaks = len(re.findall(r'([.!?"])\n(\d+\.)', text))
    text = re.sub(r'([.!?"])\n(\d+\.)', r"\1##P_BREAK##\2", text)

    # 문장 끝 + 줄바꿈 + 로마숫자 목록 시작 패턴
    roman_breaks = len(re.findall(r'([.!?"])\n([IVX]+\.)', text))
    text = re.sub(r'([.!?"])\n([IVX]+\.)', r"\1##P_BREAK##\2", text)

    # 문장 끝 + 줄바꿈 + 챕터/섹션 시작 패턴
    section_breaks = len(
        re.findall(
            r'([.!?"])\n(Chapter|Section|Part|Figure|Table)', text, flags=re.IGNORECASE
        )
    )
    text = re.sub(
        r'([.!?"])\n(Chapter|Section|Part|Figure|Table)',
        r"\1##P_BREAK##\2",
        text,
        flags=re.IGNORECASE,
    )

    # 총 복원된 문단 수 계산
    total_restored = sentence_breaks + number_breaks + roman_breaks + section_breaks
    total_paragraphs = original_breaks + total_restored
    logger.info(f"문단 구조 복원 완료: {total_paragraphs}개 문단 감지")

    # 나머지 단일 줄바꿈을 공백으로 치환 (페이지 내 자동 줄바꿈 해결)
    text = re.sub(r"(?<!##P_BREAK##)\n(?!##P_BREAK##)", " ", text)

    # 최종 문단 구분자를 표준 형태로 변환
    text = text.replace("##P_BREAK##", "\n\n")

    # 중복된 문단 구분자 정리
    text = re.sub(r"\n{3,}", "\n\n", text)

    text = text.strip()

    return text


def split_into_paragraphs(text: str) -> List[str]:
    """
    정규화된 텍스트를 문단 단위로 분할한다.

    Args:
        text: 텍스트

    Returns:
        List[str]: 문단들의 리스트

    Raises:
        HTTPException: 문단 분할 실패 시
    """

    # 문단 구분자(\n\n)로 분할
    raw_paragraphs = text.split("\n\n")

    # 완전히 빈 문단만 제거 (공백만 있는 경우)
    paragraphs = []
    for paragraph in raw_paragraphs:
        paragraph = paragraph.strip()
        if paragraph:
            paragraphs.append(paragraph)

    logger.info(f"문단 분할 완료: {len(paragraphs)}개 문단 추출")

    return paragraphs


def create_semantic_chunks(
    paragraphs: List[str],  # 문단들의 리스트
    max_tokens: int = 120000,  # Input 최대 토큰 수
    model: str = "claude-sonnet-4-20250514",  # 토큰 계산용 모델
) -> List[str]:
    """
    문단 단위로 시멘틱 청킹을 수행하여 블록 변환 시 문맥 손실을 방지한다.
    그리디 알고리즘을 사용해 문단들을 최적의 크기로 그룹화하여 청크를 생성한다.

    Args:
        paragraphs: 문단들의 리스트
        max_tokens: 최대 토큰 수
        model: 토큰 계산용 모델

    Returns:
        List[str]: 청크들의 리스트
    """
    # TODO: 문자 임베딩을 활용한 의미 기반 청킹 고민해보기

    logger.debug(
        f"시맨틱 청킹 시작: {len(paragraphs)}개 문단, 최대 토큰: {max_tokens:,}"
    )

    chunks = []
    current_chunk = ""
    current_token_count = 0
    processed_paragraphs = 0

    for i, paragraph in enumerate(paragraphs):
        logger.debug(f"문단 {i+1}/{len(paragraphs)} 처리 중...")

        # 현재 문단의 토큰 수 계산
        try:
            paragraph_tokens = count_tokens(paragraph, model)
            logger.debug(f"문단 {i+1} 토큰 수: {paragraph_tokens:,}")
        except Exception as e:
            logger.warning(f"문단 {i+1} 토큰 계산 실패: {e} - 추정값 사용")
            paragraph_tokens = len(paragraph) // 4

        # 현재 청크에 문단을 추가했을 때의 토큰 수 예상
        if current_chunk:
            estimated_total_tokens = current_token_count + paragraph_tokens + 10  # 여백
        else:
            estimated_total_tokens = paragraph_tokens

        # 토큰 한계를 초과하지 않으면 현재 청크에 추가
        if estimated_total_tokens <= max_tokens:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
            current_token_count = estimated_total_tokens
            logger.debug(f"문단 {i+1} 추가됨. 현재 청크 토큰: {current_token_count:,}")
        else:
            # 토큰 한계 초과: 현재 청크를 완료하고 새 청크 시작
            if current_chunk:
                chunks.append(current_chunk)
                logger.debug(f"청크 {len(chunks)} 완료: {current_token_count:,} 토큰")
                current_chunk = paragraph
                current_token_count = paragraph_tokens
                logger.debug(f"새 청크 시작: {paragraph_tokens:,} 토큰")
            else:
                # 단일 문단이 토큰 한계를 초과하는 경우
                logger.warning(
                    f"문단 {i+1}이 토큰 한계 초과 ({paragraph_tokens:,} > {max_tokens:,})"
                )
                chunks.append(paragraph)
                current_chunk = ""
                current_token_count = 0

        processed_paragraphs += 1
        if processed_paragraphs % 10 == 0:
            logger.debug(
                f"진행률: {processed_paragraphs}/{len(paragraphs)} 문단 처리됨"
            )

    # 마지막 청크 추가
    if current_chunk:
        chunks.append(current_chunk)
        logger.debug(f"마지막 청크 {len(chunks)} 완료: {current_token_count:,} 토큰")

    logger.info(f"시맨틱 청킹 완료: {len(chunks)}개 청크 생성")

    return chunks


def save_uploaded_file(
    file: UploadFile, 
    temp_dir: str
) -> str:
    """
    업로드된 파일을 임시 디렉토리에 저장

    Args:
        file: 업로드된 파일
        temp_dir: 임시 디렉토리 경로

    Returns:
        str: 저장된 파일 경로

    Raises:
        HTTPException: 파일 저장 실패 시
    """

    # 파일 존재 여부 확인
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # 파일 확장자 검증
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # 안전한 파일명 생성 (Path Traversal 방지)
    safe_filename = Path(file.filename).name
    file_path = os.path.join(temp_dir, safe_filename)

    return file_path


def run_preprocessing_pipeline(
    file: UploadFile,  # 업로드된 PDF 파일
    options: PreprocessingOptions,  # 전처리 옵션 모델
    return_text: bool = True,  # 텍스트 반환 여부
    return_chunks: bool = True,  # 청크 반환 여부
    model: str = "claude-sonnet-4-20250514",  # Claude 모델명 (토큰 계산용)
) -> Dict[str, Any]:
    """
    PDF를 완전한 파이프라인으로 처리한다.

    Args:
        file: 업로드된 PDF 파일
        options: 전처리 옵션(임시 디렉토리, 헤더/푸터 제거, 높이, 최대 토큰 등)
        return_text: 텍스트 반환 여부
        return_chunks: 청크 반환 여부
        model: Claude 모델명(토큰 계산용)

    Raises:
        HTTPException: PDF 처리 실패 시
    """

    file_path = None
    start_time = time.time()

    try:
        logger.info(f"PDF 변환 시작: {file.filename}")

        # 파일 검증 및 저장 경로 생성
        logger.debug("1. 임시 파일 경로 생성 중...")
        file_path = save_uploaded_file(file, options.temp_dir)
        logger.debug(f"임시 파일 경로: {file_path}")

        # 파일 저장
        logger.debug("2. 파일 저장 중...")
        contents = file.file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        logger.debug(f"파일 저장 완료: {len(contents)} bytes")

        logger.info(f"PDF 파일 처리 중: {file.filename}")

        # 1. PDF에서 텍스트 추출
        logger.debug("3. PDF 텍스트 추출 시작...")
        with pdfplumber.open(file_path) as pdf:
            all_page_texts = []
            logger.debug(f"PDF 총 페이지 수: {len(pdf.pages)}")

            # 모든 페이지에서 텍스트 추출
            for page_num, page in enumerate(pdf.pages, 1):
                logger.debug(f"페이지 {page_num} 처리 중...")
                if options.remove_headers_footers:
                    page_text = extract_text_from_page(
                        page, options.header_height, options.footer_height
                    )
                else:
                    page_text = page.extract_text()

                if page_text:
                    page_text = page_text.strip()
                    if page_text:
                        all_page_texts.append(page_text)
                        logger.debug(f"페이지 {page_num} 텍스트 길이: {len(page_text)}")

            if not all_page_texts:
                raise HTTPException(
                    status_code=422, detail="Failed to extract text from PDF"
                )

            logger.debug(f"총 {len(all_page_texts)}개 페이지에서 텍스트 추출 완료")

            # 모든 페이지 텍스트를 결합
            logger.debug("4. 텍스트 결합 중...")
            raw_text = "\n\n".join(all_page_texts)
            logger.debug(f"결합된 텍스트 길이: {len(raw_text)} 문자")

            # 원본 텍스트 전체 토큰 수 계산
            logger.debug("5. 토큰 수 계산 중...")
            total_tokens = count_tokens(raw_text, model)
            logger.info(f"원본 텍스트 토큰 수: {total_tokens:,}")

            # 2. 텍스트 정규화
            logger.debug("6. 텍스트 정규화 중...")
            manuscript = normalize_text_structure(raw_text)
            logger.debug(f"정규화된 텍스트 길이: {len(manuscript)} 문자")

            # 3. 그리디 청킹 처리
            chunks = None

            if return_chunks:
                logger.debug("7. 문단 분리 중...")
                paragraphs = split_into_paragraphs(manuscript)
                logger.debug(f"분리된 문단 수: {len(paragraphs)}개")

                logger.debug("8. 시맨틱 청킹 중...")
                chunks = create_semantic_chunks(
                    paragraphs, max_tokens=options.max_tokens, model=model
                )
                logger.info(f"생성된 청크 수: {len(chunks)}개")

            # 처리 시간 계산
            processing_time = round(time.time() - start_time, 2)
            logger.debug(f"총 처리 시간: {processing_time}초")

            # 결과 구성
            result = {
                "total_tokens": total_tokens,
                "total_chunks": len(chunks) if chunks else 0,
                "processing_time": processing_time,
            }

            if return_text:
                result["text"] = manuscript

            if return_chunks and chunks:
                result["chunks"] = chunks

            # 파일 정보 추가
            result.update(
                {
                    "filename": file.filename,
                    "created_at": time.time(),
                    "metadata": {
                        "total_pages": len(all_page_texts),
                        "original_text_length": len(raw_text),
                        "normalized_text_length": len(manuscript),
                        "total_tokens": total_tokens,
                        "total_chunks": len(chunks) if chunks else 0,
                        "processing_time": processing_time,
                        "max_tokens": options.max_tokens,
                        "model": model,
                        "remove_headers_footers": options.remove_headers_footers,
                    },
                }
            )

            # 완료 로그
            if chunks:
                logger.info(
                    f"PDF 처리 완료: {len(chunks)}개 청크, {total_tokens:,} 토큰 ({processing_time}초)"
                )
            else:
                logger.info(
                    f"PDF 텍스트 추출 완료: {total_tokens:,} 토큰 ({processing_time}초)"
                )

            return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF 처리 중 오류 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    finally:
        # 임시 파일 정리
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.debug(f"임시 파일 삭제: {file_path}")
            except Exception as e:
                logger.warning(f"임시 파일 삭제 실패: {e}")
