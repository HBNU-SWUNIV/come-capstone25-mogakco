"""최종 output 조회 API 라우터"""

import logging
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, status

from src.services.redis_service import RedisService

# 로거 설정
logger = logging.getLogger(__name__)

# 라우터 설정
router = APIRouter(
    prefix="/output",
    tags=["output"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{task_id}")
async def get_output_by_task_id(task_id: str):
    """task_id로 최종 output 조회 (하위호환성)"""
    try:
        redis_service = RedisService()
        output_data = redis_service.get_output_by_task_id(task_id)
        
        if not output_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"완료된 결과를 찾을 수 없습니다: {task_id}"
            )
        
        return output_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Output 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Output 조회 실패: {str(e)}"
        )


@router.get("/file/{filename}/{task_id}")
async def get_output_by_filename_and_task_id(filename: str, task_id: str):
    """파일명과 task_id로 최종 output 조회"""
    try:
        redis_service = RedisService()
        output_data = redis_service.get_output_by_filename_and_task_id(filename, task_id)
        
        if not output_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"완료된 결과를 찾을 수 없습니다: {filename}:{task_id}"
            )
        
        return output_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Output 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Output 조회 실패: {str(e)}"
        )


@router.get("/file/{filename}/latest")
async def get_latest_output_by_filename(filename: str):
    """파일명으로 가장 최근 output 조회"""
    try:
        redis_service = RedisService()
        output_data = redis_service.get_latest_output_by_filename(filename)
        
        if not output_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"완료된 결과를 찾을 수 없습니다: {filename}"
            )
        
        return output_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Output 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Output 조회 실패: {str(e)}"
        )


@router.get("/file/{filename}/tasks")
async def get_file_task_ids(filename: str):
    """파일명으로 모든 task_id 목록 조회"""
    try:
        redis_service = RedisService()
        task_ids = redis_service.get_file_task_ids(filename)
        
        return {
            "filename": filename,
            "task_ids": task_ids,
            "count": len(task_ids)
        }
    except Exception as e:
        logger.error(f"파일별 task_id 목록 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일별 task_id 목록 조회 실패: {str(e)}"
        )


@router.get("/{task_id}/summary")
async def get_output_summary(task_id: str):
    """task_id로 output 요약 정보 조회 (하위호환성)"""
    try:
        redis_service = RedisService()
        output_data = redis_service.get_output_by_task_id(task_id)
        
        if not output_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"완료된 결과를 찾을 수 없습니다: {task_id}"
            )
        
        # 요약 정보 추출
        summary = {
            "task_id": task_id,
            "filename": output_data.get("filename", "unknown"),
            "processing_time": output_data.get("processing_time", 0),
            "total_blocks": output_data.get("transformation", {}).get("metadata", {}).get("total_blocks", 0),
            "has_phoneme_analysis": "phoneme_analysis" in output_data,
            "has_block_word_phoneme_analysis": "block_word_phoneme_analysis" in output_data,
            "created_at": output_data.get("created_at"),
        }
        
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Output 요약 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Output 요약 조회 실패: {str(e)}"
        )


@router.get("/")
async def get_all_completed_tasks():
    """완료된 모든 task 목록 조회"""
    try:
        redis_service = RedisService()
        task_ids = redis_service.get_all_task_ids()
        
        return {
            "task_ids": task_ids,
            "count": len(task_ids)
        }
    except Exception as e:
        logger.error(f"완료된 task 목록 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"완료된 task 목록 조회 실패: {str(e)}"
        )


@router.get("/files/")
async def get_all_files_with_tasks():
    """모든 파일과 해당 task_id 목록 조회"""
    try:
        redis_service = RedisService()
        files_with_tasks = redis_service.get_all_files_with_tasks()
        
        return {
            "files": files_with_tasks,
            "total_files": len(files_with_tasks),
            "total_tasks": sum(len(tasks) for tasks in files_with_tasks.values())
        }
    except Exception as e:
        logger.error(f"파일별 task 목록 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일별 task 목록 조회 실패: {str(e)}"
        ) 