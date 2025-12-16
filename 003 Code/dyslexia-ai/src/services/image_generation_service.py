import logging
import os
import tempfile
from typing import Dict, Any, Optional
from io import BytesIO

import requests
from fastapi import UploadFile

from src.core.prompts import create_image_generation_prompt
from src.services.image_uploader import upload_local_image_to_s3

# 로거 설정
logger = logging.getLogger(__name__)


def generate_image(
    description: str,
    style: str = "any",
    size: str = "1536x1024",
    model: str = "google/nano-banana",
    output_format: str = "jpg",
):
    """
    replicate 모델을 사용하여 이미지를 생성한다.

    Args:
        description: 이미지 생성 설명
        style: 이미지 스타일
        size: 이미지 크기
        model: 사용할 모델
        output_format: 출력 형식

    Returns:
        output_file: 생성된 이미지 파일 경로
    """

    prompt = create_image_generation_prompt(description)

    # nano-banana 호출 (Replicate HTTP API)
    logger.info(f"Replicate nano-banana 호출 시작: model={model}")
    prediction = _replicate_predict_nano_banana(prompt=prompt, model=model, output_format=output_format)

    # prediction에서 output 추출
    output = prediction.get("output") if isinstance(prediction, dict) else prediction

    # 저장 경로
    output_file = f"./temp/output.{output_format}"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 출력 저장 (URL 또는 바이너리 대응)
    data = extract_image_data(output)
    with open(output_file, "wb") as f:
        f.write(data)

    return {
        "file_path": output_file,
        "style": style,
        "size": size,
        "model": model,
        "output_format": output_format,
    }


def generate_image_with_s3_upload(
    description: str,
    style: str = "any",
    size: str = "1536x1024",
    model: str = "google/nano-banana",
    output_format: str = "jpg",
    upload_to_s3: bool = True,
) -> Dict[str, Any]:
    """이미지 생성 후 S3 업로드까지 수행하는 함수"""
    
    logger.info(f"이미지 생성 시작: {description[:50]}...")
    
    prompt = create_image_generation_prompt(description)
    
    default_model = "google/nano-banana"

    try:
        logger.debug(f"Replicate API 호출: {model}")
        prediction = _replicate_predict_nano_banana(
            prompt=prompt,
            model=model or default_model,
            output_format=output_format,
        )
        output = prediction.get("output") if isinstance(prediction, dict) else prediction
    except Exception as e:
        logger.error(f"모델 '{model}' 실행 실패: {str(e)}")
        logger.info(f"기본 모델 '{default_model}'로 대체하여 재시도...")
        prediction = _replicate_predict_nano_banana(
            prompt=prompt,
            model=default_model,
            output_format=output_format,
        )
        output = prediction.get("output") if isinstance(prediction, dict) else prediction
    
    # 이미지 바이너리 데이터 추출
    image_data = extract_image_data(output)
    
    if not upload_to_s3:
        # S3 업로드 없이 바이너리 데이터만 반환
        return {
            "image_data": image_data,
            "style": style,
            "size": size,
            "model": model,
            "output_format": output_format,
        }
    
    # 임시 파일 생성 및 S3 업로드
    try:
        # 안전한 파일명 생성
        safe_description = "".join(c for c in description if c.isalnum() or c in (' ', '-', '_'))[:30]
        temp_filename = f"generated_image_{safe_description.replace(' ', '_')}.{output_format}"
        
        # 임시 파일에 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_format}") as temp_file:
            temp_file.write(image_data)
            temp_file_path = temp_file.name
        
        # S3 업로드
        logger.debug(f"S3 업로드 시작: {temp_filename}")
        upload_result = upload_local_image_to_s3(temp_file_path)
        
        # 임시 파일 삭제
        os.unlink(temp_file_path)
        
        # 성공 결과 반환
        result = {
            "success": True,
            "url": upload_result["url"],
            "s3_key": upload_result["s3_key"],
            "filename": upload_result["filename"],
            "file_size": upload_result["file_size"],
            "style": style,
            "size": size,
            "model": model,
            "output_format": output_format,
            "description": description,
            "uploaded_at": upload_result["uploaded_at"],
        }
        
        logger.info(f"이미지 생성 및 S3 업로드 완료: {upload_result['url']}")
        return result
        
    except Exception as e:
        logger.error(f"S3 업로드 중 오류 발생: {e}")
        raise Exception(f"이미지 S3 업로드 실패: {str(e)}")


def extract_image_data(output) -> bytes:
    """Replicate 출력에서 이미지 바이너리 데이터 추출"""
    
    try:
        # 출력 객체가 URL을 가진 경우
        if hasattr(output, "url"):
            response = requests.get(output.url)
            response.raise_for_status()
            return response.content
            
        # 출력 객체가 직접 읽기 가능한 경우
        elif hasattr(output, "read"):
            return output.read()
            
        # 출력이 이터러블인 경우 (리스트, 제너레이터 등)
        elif hasattr(output, "__iter__") and not isinstance(output, (str, bytes)):
            for item in output:
                if hasattr(item, "url"):
                    response = requests.get(item.url)
                    response.raise_for_status()
                    return response.content
                elif hasattr(item, "read"):
                    return item.read()
                else:
                    # 문자열 URL 요소 처리
                    if isinstance(item, str) and (item.startswith("http://") or item.startswith("https://")):
                        response = requests.get(item)
                        response.raise_for_status()
                        return response.content
                    return item if isinstance(item, bytes) else str(item).encode()
                    
        # 출력이 문자열인 경우: URL이면 다운로드, 아니면 바이트로 간주
        elif isinstance(output, str):
            if output.startswith("http://") or output.startswith("https://"):
                response = requests.get(output)
                response.raise_for_status()
                return response.content
            return output.encode()
        elif isinstance(output, bytes):
            return output
            
        else:
            # 마지막 대안: 문자열로 변환
            return str(output).encode()
            
    except Exception as e:
        logger.error(f"이미지 데이터 추출 실패: {e}")
        raise Exception(f"이미지 데이터 추출 중 오류 발생: {str(e)}")


async def generate_image_for_page_block(
    page_image_block: Dict[str, Any],
    style: str = "any",
    size: str = "1536x1024",
    model: str = "google/nano-banana",
    output_format: str = "jpg",
) -> Dict[str, Any]:
    """PAGE_IMAGE 블록을 위한 이미지 생성 및 S3 업로드"""
    
    try:
        # PAGE_IMAGE 블록에서 설명 추출
        description = page_image_block.get("prompt", "")
        if not description:
            # prompt가 없으면 concept나 alt 사용
            description = page_image_block.get("concept", page_image_block.get("alt", "교육용 이미지"))
        
        logger.info(f"PAGE_IMAGE 블록 이미지 생성 시작: {description[:50]}...")
        
        # 이미지 생성 및 S3 업로드
        result = generate_image_with_s3_upload(
            description=description,
            style=style,
            size=size,
            model=model,
            output_format=output_format,
            upload_to_s3=True,
        )
        
        # PAGE_IMAGE 블록에 URL 추가
        updated_block = page_image_block.copy()
        updated_block["url"] = result["url"]
        updated_block["s3_key"] = result["s3_key"]
        updated_block["file_size"] = result["file_size"]
        updated_block["generated_at"] = result["uploaded_at"]
        
        logger.info(f"PAGE_IMAGE 블록 이미지 생성 완료: {result['url']}")
        return updated_block
        
    except Exception as e:
        logger.error(f"PAGE_IMAGE 블록 이미지 생성 실패: {e}")
        # 실패 시 원본 블록 반환 (서비스 중단 방지)
        return page_image_block
def save_replicate_output(output, output_file: str) -> str:
    """
    Replicate API 출력을 파일로 저장

    Args:
        output: Replicate API 응답 객체
        output_file: 저장할 파일 경로

    Returns:
        str: 저장된 파일 경로

    Raises:
        RuntimeError: 파일 저장 실패 시
    """
    try:
        # 1. URL 기반 출력 (가장 일반적)
        if hasattr(output, "url") and output.url:
            logger.info(f"URL에서 이미지 다운로드: {output.url}")
            response = requests.get(output.url, timeout=30)
            response.raise_for_status()

            with open(output_file, "wb") as f:
                f.write(response.content)

        # 2. 파일 객체/스트림
        elif hasattr(output, "read"):
            logger.info("스트림에서 이미지 읽기")
            with open(output_file, "wb") as f:
                f.write(output.read())

        # 3. 리스트/배열 (첫 번째 유효한 항목 사용)
        elif isinstance(output, (list, tuple)) and output:
            logger.info("배열에서 첫 번째 항목 처리")
            return save_replicate_output(output[0], output_file)

        # 4. 직접 바이트 데이터
        elif isinstance(output, bytes):
            logger.info("바이트 데이터 직접 저장")
            with open(output_file, "wb") as f:
                f.write(output)

        # 5. 문자열 (Base64 등)
        elif isinstance(output, str):
            # 문자열이 URL인 경우 이미지 데이터를 다운로드하여 저장
            if output.startswith("http://") or output.startswith("https://"):
                logger.info("URL에서 이미지 다운로드(문자열)")
                response = requests.get(output, timeout=30)
                response.raise_for_status()
                with open(output_file, "wb") as f:
                    f.write(response.content)
            else:
                logger.info("문자열 데이터 저장")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(output)

        else:
            raise ValueError(f"지원하지 않는 출력 타입: {type(output)}")

        logger.info(f"파일 저장 완료: {output_file}")
        return output_file

    except Exception as e:
        logger.error(f"파일 저장 실패: {e}")
        raise RuntimeError(f"이미지 저장 중 오류 발생: {e}") from e


def _replicate_predict_nano_banana(
    prompt: str,
    model: str = "google/nano-banana",
    output_format: str = "jpg",
    image_inputs: Optional[list] = None,
) -> Dict[str, Any]:
    """Replicate HTTP API를 사용해 nano-banana 모델 호출(PREFER: wait)."""
    token = os.getenv("REPLICATE_API_TOKEN")
    if not token:
        raise RuntimeError("REPLICATE_API_TOKEN 환경변수가 설정되어 있지 않습니다.")

    base_url = "https://api.replicate.com/v1"
    url = f"{base_url}/models/{model}/predictions"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Prefer": "wait",
    }

    # 입력 구성: 프롬프트와 출력 포맷, 선택적으로 이미지 입력
    input_payload: Dict[str, Any] = {
        "prompt": prompt,
        "output_format": output_format,
    }
    if image_inputs:
        # Replicate 예시 형식에 맞게 포장
        input_payload["image_input"] = [{"value": u} for u in image_inputs]

    body = {"input": input_payload}

    resp = requests.post(url, headers=headers, json=body, timeout=60)
    if not (200 <= resp.status_code < 300):
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise RuntimeError(f"Replicate 호출 실패(status={resp.status_code}): {detail}")

    try:
        return resp.json()
    except Exception as e:
        raise RuntimeError(f"Replicate 응답 JSON 파싱 실패: {e}")
