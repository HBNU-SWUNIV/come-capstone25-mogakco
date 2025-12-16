"""진행률 추적 API 라우터"""

import logging
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, status

from src.services.progress_service import ProgressService

# 로거 설정
logger = logging.getLogger(__name__)

# 라우터 설정
router = APIRouter(
    prefix="/progress",
    tags=["progress"],
    responses={404: {"description": "Not found"}},
)

# 서비스 인스턴스
try:
    progress_service = ProgressService()
except Exception as e:
    logger.error(f"ProgressService 초기화 실패: {e}")
    progress_service = None


@router.get("/", response_model=List[str])
async def get_all_active_tasks():
    """활성 태스크 목록 조회"""
    try:
        if not progress_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="진행률 서비스를 사용할 수 없습니다"
            )
        
        task_ids = progress_service.get_all_active_tasks()
        return task_ids
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"활성 태스크 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"활성 태스크 조회 실패: {str(e)}"
        )


@router.get("/{task_id}")
async def get_task_progress(task_id: str):
    """태스크 진행률 조회 (하위호환성)"""
    try:
        if not progress_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="진행률 서비스를 사용할 수 없습니다"
            )
        
        progress_data = progress_service.get_progress(task_id)
        if not progress_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"진행률 정보를 찾을 수 없습니다: {task_id}"
            )
        
        return progress_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"진행률 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"진행률 조회 실패: {str(e)}"
        )


@router.get("/file/{filename}/{task_id}")
async def get_progress_by_filename_and_task_id(filename: str, task_id: str):
    """파일명과 태스크 ID로 진행률 조회"""
    try:
        if not progress_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="진행률 서비스를 사용할 수 없습니다"
            )
        
        progress_data = progress_service.get_progress_by_filename_and_task_id(filename, task_id)
        if not progress_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"진행률 정보를 찾을 수 없습니다: {filename}:{task_id}"
            )
        
        return progress_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"진행률 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"진행률 조회 실패: {str(e)}"
        )


@router.delete("/{task_id}")
async def delete_task_progress(task_id: str):
    """특정 태스크의 진행률 데이터 삭제 (하위호환성)"""
    try:
        if not progress_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="진행률 서비스를 사용할 수 없습니다"
            )
        
        success = progress_service.delete_progress(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"태스크를 찾을 수 없습니다: {task_id}"
            )
        
        return {"message": f"태스크 {task_id}의 진행률 데이터가 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"진행률 삭제 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"진행률 삭제 실패: {str(e)}"
        )


@router.delete("/file/{filename}/{task_id}")
async def delete_progress_by_filename_and_task_id(filename: str, task_id: str):
    """파일명과 태스크 ID로 진행률 데이터 삭제"""
    try:
        if not progress_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="진행률 서비스를 사용할 수 없습니다"
            )
        
        success = progress_service.delete_progress_by_filename_and_task_id(filename, task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"태스크를 찾을 수 없습니다: {filename}:{task_id}"
            )
        
        return {"message": f"태스크 {filename}:{task_id}의 진행률 데이터가 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"진행률 삭제 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"진행률 삭제 실패: {str(e)}"
        )


 