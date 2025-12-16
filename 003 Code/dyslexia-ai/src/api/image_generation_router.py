from typing import List
from src.services.image_generation_service import generate_image
from fastapi import APIRouter

router = APIRouter(prefix="/image", tags=["Image Generation"])


@router.post("/generate")
async def image_generation(
    content: str,  # 전처리에서 생성된 청크 배열
    style: str = "any",  # 이미지 스타일 (기본값: "any")
    size: str = "1024x1024",  # 이미지 크기 (기본값: "1024x1024")
    model: str = "google/nano-banana",  # 사용할 모델
    output_format: str = "jpg",  # 출력 형식 (기본값: "jpg")
):
    """AI 이미지 생성"""
    try:
        # 동기 함수를 비동기로 실행
        import asyncio
        result = await asyncio.get_event_loop().run_in_executor(
            None, generate_image, content, style, size, model, output_format
        )
        
        return {
            "success": True,
            "message": "이미지가 성공적으로 생성되었습니다.",
            "output_path": result["file_path"],
            "settings": {
                "style": result["style"],
                "size": result["size"],
                "model": result["model"],
                "output_format": result["output_format"]
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"이미지 생성 중 오류가 발생했습니다: {str(e)}"
        }
