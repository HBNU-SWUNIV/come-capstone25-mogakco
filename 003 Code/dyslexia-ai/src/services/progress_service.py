"""진행률 추적 서비스 모듈"""

import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional, List

try:
    from .redis_service import RedisService
    REDIS_AVAILABLE = True
except Exception as e:
    REDIS_AVAILABLE = False
    logging.warning(f"Redis 연결 실패, 메모리 모드로 동작: {e}")


@dataclass
class ProgressData:
    """진행률 데이터 클래스"""
    
    preprocessing: float = 0.0
    block_transformation: float = 0.0
    phoneme_analysis: float = 0.0
    block_word_phoneme_analysis: float = 0.0
    post_processing: float = 0.0
    overall: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """딕셔너리로 변환"""
        return {
            "preprocessing": self.preprocessing,
            "block_transformation": self.block_transformation,
            "phoneme_analysis": self.phoneme_analysis,
            "block_word_phoneme_analysis": self.block_word_phoneme_analysis,
            "post_processing": self.post_processing,
            "overall": self.overall
        }


# 메모리 기반 진행률 저장소 (Redis 연결 실패 시 사용)
_memory_progress_store = {}


class ProgressTracker:
    """진행률 추적기"""
    
    def __init__(self, task_id: Optional[str] = None, filename: Optional[str] = None):
        self.task_id = task_id or str(uuid.uuid4())
        self.filename = filename or "unknown"
        self.progress = ProgressData()
        self.start_time = time.time()
        self.step_start_times = {}  # 각 단계별 시작 시간 추적
        self.active_steps = set()
        self.completed_steps = set()
        self.logger = logging.getLogger(__name__)
        
        # Redis 서비스 설정
        try:
            from src.services.redis_service import RedisService
            self.redis_service = RedisService()
            self.use_redis = True
            self.logger.info(f"Redis 연결 성공: {self.task_id}")
        except Exception as e:
            self.logger.warning(f"Redis 연결 실패, 메모리 사용: {e}")
            self.use_redis = False
        
        # 시작 시 진행률 저장
        self._save_progress()
    
    def start_step(self, step_name: str) -> None:
        """단계 시작"""
        self.step_start_times[step_name] = time.time()
        self.logger.info(f"단계 시작: {step_name}")
    
    def update_progress(self, step_name: str, progress: float) -> None:
        """
        특정 단계의 진행률 업데이트
        
        Args:
            step_name: 단계 이름
            progress: 진행률 (0-100)
        """
        # 진행률 값 검증
        progress = max(0.0, min(100.0, progress))
        
        # 진행률 업데이트
        if step_name == "preprocessing":
            self.progress.preprocessing = progress
        elif step_name == "block_transformation":
            self.progress.block_transformation = progress
        elif step_name == "phoneme_analysis":
            self.progress.phoneme_analysis = progress
        elif step_name == "block_word_phoneme_analysis":
            self.progress.block_word_phoneme_analysis = progress
        elif step_name == "post_processing":
            self.progress.post_processing = progress
        else:
            self.logger.warning(f"알 수 없는 단계: {step_name}")
            return
        
        # 전체 진행률 계산
        self._calculate_overall_progress()
        
        # 저장
        self._save_progress()
        
        self.logger.info(f"진행률 업데이트: {step_name} = {progress:.1f}% (전체: {self.progress.overall:.1f}%)")
    
    def complete_step(self, step_name: str) -> None:
        """단계 완료"""
        self.update_progress(step_name, 100.0)
        
        # 처리 시간 계산
        if step_name in self.step_start_times:
            elapsed = time.time() - self.step_start_times[step_name]
            self.logger.info(f"단계 완료: {step_name} ({elapsed:.2f}초)")
    
    def _calculate_overall_progress(self) -> None:
        """전체 진행률 계산"""
        # 각 단계의 가중치 설정
        weights = {
            "preprocessing": 0.20,           # 20%
            "block_transformation": 0.40,    # 40%
            "phoneme_analysis": 0.15,        # 15%
            "block_word_phoneme_analysis": 0.15,  # 15%
            "post_processing": 0.10          # 10%
        }
        
        # 가중 평균 계산
        total_progress = (
            self.progress.preprocessing * weights["preprocessing"] +
            self.progress.block_transformation * weights["block_transformation"] +
            self.progress.phoneme_analysis * weights["phoneme_analysis"] +
            self.progress.block_word_phoneme_analysis * weights["block_word_phoneme_analysis"] +
            self.progress.post_processing * weights["post_processing"]
        )
        
        self.progress.overall = total_progress
    
    def _save_progress(self) -> None:
        """진행률 저장"""
        try:
            # 진행률 데이터 구성
            progress_data = {
                "task_id": self.task_id,
                "filename": self.filename,
                "progress": self.progress.overall  # 간단한 형식
            }
            
            if self.use_redis:
                # Redis에 저장 (progress:{filename}:{task_id} 형태)
                redis_key = f"progress:{self.filename}:{self.task_id}"
                expire_seconds = 24 * 3600  # 24시간 후 만료
                
                success = self.redis_service.redis_client.set_json(
                    redis_key, progress_data, expire_seconds
                )
                
                if not success:
                    self.logger.error(f"Redis 진행률 저장 실패: {self.filename}:{self.task_id}")
                    # Redis 실패 시 메모리에 저장
                    _memory_progress_store[self.task_id] = progress_data
            else:
                # 메모리에 저장
                _memory_progress_store[self.task_id] = progress_data
                
        except Exception as e:
            self.logger.error(f"진행률 저장 중 오류 발생: {e}")
            # 오류 발생 시 메모리에 저장
            _memory_progress_store[self.task_id] = progress_data
    
    def get_progress(self) -> Dict[str, Any]:
        """현재 진행률 조회 - 간단한 형식"""
        result = {
            "task_id": self.task_id,
            "progress": round(self.progress.overall, 1)
        }
        
        # 완료된 경우 output_id 추가
        if self.progress.overall >= 100.0:
            result["output_id"] = self.task_id
            
        return result
    
    def finish(self) -> Dict[str, Any]:
        """진행률 추적 완료"""
        # 모든 단계 완료로 설정
        self.progress.preprocessing = 100.0
        self.progress.block_transformation = 100.0
        self.progress.phoneme_analysis = 100.0
        self.progress.block_word_phoneme_analysis = 100.0
        self.progress.post_processing = 100.0
        self.progress.overall = 100.0
        
        # 최종 저장
        self._save_progress()
        
        total_time = time.time() - self.start_time
        self.logger.info(f"진행률 추적 완료: {self.task_id} ({total_time:.2f}초)")
        
        return self.get_progress()


class ProgressService:
    """진행률 서비스 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Redis 사용 가능 여부에 따라 서비스 초기화
        if REDIS_AVAILABLE:
            try:
                self.redis_service = RedisService()
                self.use_redis = True
            except Exception as e:
                self.logger.warning(f"Redis 서비스 초기화 실패, 메모리 모드로 전환: {e}")
                self.use_redis = False
        else:
            self.use_redis = False
    
    def create_tracker(self, task_id: Optional[str] = None, filename: Optional[str] = None) -> ProgressTracker:
        """새로운 진행률 추적기 생성"""
        return ProgressTracker(task_id, filename)
    
    def get_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        태스크 ID로 진행률 조회 - 간단한 형식 (하위호환성)
        
        Args:
            task_id: 태스크 ID
            
        Returns:
            {"task_id": str, "progress": float} 또는 None
        """
        try:
            if self.use_redis:
                # Redis에서 패턴 기반 검색
                pattern = f"progress:*:{task_id}"
                keys = self.redis_service.redis_client.get_keys_by_pattern(pattern)
                
                if keys:
                    # 첫 번째 매칭 키 사용
                    redis_key = keys[0]
                    progress_data = self.redis_service.redis_client.get_json(redis_key)
                    
                    if progress_data:
                        self.logger.info(f"Redis 진행률 조회 성공: {task_id}")
                        return {
                            "task_id": progress_data.get("task_id"),
                            "progress": round(progress_data.get("progress", 0), 1)
                        }
            
            # 메모리에서 조회
            if task_id in _memory_progress_store:
                progress_data = _memory_progress_store[task_id]
                self.logger.info(f"메모리 진행률 조회 성공: {task_id}")
                return {
                    "task_id": progress_data.get("task_id"),
                    "progress": round(progress_data.get("progress", 0), 1)
                }
            
            self.logger.warning(f"진행률 조회 실패: {task_id}")
            return None
                
        except Exception as e:
            self.logger.error(f"진행률 조회 중 오류 발생: {e}")
            return None
    
    def get_progress_by_filename_and_task_id(self, filename: str, task_id: str) -> Optional[Dict[str, Any]]:
        """
        파일명과 태스크 ID로 진행률 조회
        
        Args:
            filename: 파일명
            task_id: 태스크 ID
            
        Returns:
            {"task_id": str, "progress": float} 또는 None
        """
        try:
            if self.use_redis:
                # Redis에서 조회
                redis_key = f"progress:{filename}:{task_id}"
                progress_data = self.redis_service.redis_client.get_json(redis_key)
                
                if progress_data:
                    self.logger.info(f"Redis 진행률 조회 성공: {filename}:{task_id}")
                    return {
                        "task_id": progress_data.get("task_id"),
                        "progress": round(progress_data.get("progress", 0), 1)
                    }
            
            # 메모리에서 조회
            if task_id in _memory_progress_store:
                progress_data = _memory_progress_store[task_id]
                self.logger.info(f"메모리 진행률 조회 성공: {task_id}")
                return {
                    "task_id": progress_data.get("task_id"),
                    "progress": round(progress_data.get("progress", 0), 1)
                }
            
            self.logger.warning(f"진행률 조회 실패: {filename}:{task_id}")
            return None
                
        except Exception as e:
            self.logger.error(f"진행률 조회 중 오류 발생: {e}")
            return None
    
    def delete_progress(self, task_id: str) -> bool:
        """
        진행률 데이터 삭제 (하위호환성)
        
        Args:
            task_id: 태스크 ID
            
        Returns:
            삭제 성공 여부
        """
        try:
            success = False
            
            if self.use_redis:
                # Redis에서 패턴 기반 검색 후 삭제
                pattern = f"progress:*:{task_id}"
                keys = self.redis_service.redis_client.get_keys_by_pattern(pattern)
                
                for key in keys:
                    if self.redis_service.redis_client.delete_key(key):
                        success = True
            
            # 메모리에서도 삭제
            if task_id in _memory_progress_store:
                del _memory_progress_store[task_id]
                success = True
            
            if success:
                self.logger.info(f"진행률 삭제 성공: {task_id}")
            else:
                self.logger.warning(f"진행률 삭제 실패: {task_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"진행률 삭제 중 오류 발생: {e}")
            return False
    
    def delete_progress_by_filename_and_task_id(self, filename: str, task_id: str) -> bool:
        """
        파일명과 태스크 ID로 진행률 데이터 삭제
        
        Args:
            filename: 파일명
            task_id: 태스크 ID
            
        Returns:
            삭제 성공 여부
        """
        try:
            success = False
            
            if self.use_redis:
                # Redis에서 삭제
                redis_key = f"progress:{filename}:{task_id}"
                success = self.redis_service.redis_client.delete_key(redis_key)
            
            # 메모리에서도 삭제
            if task_id in _memory_progress_store:
                del _memory_progress_store[task_id]
                success = True
            
            if success:
                self.logger.info(f"진행률 삭제 성공: {filename}:{task_id}")
            else:
                self.logger.warning(f"진행률 삭제 실패: {filename}:{task_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"진행률 삭제 중 오류 발생: {e}")
            return False
    
    def get_all_active_tasks(self) -> List[str]:
        """
        모든 활성 태스크 ID 목록 조회
        
        Returns:
            활성 태스크 ID 목록
        """
        try:
            active_tasks = []
            
            if self.use_redis:
                # Redis에서 패턴 기반 검색
                pattern = "progress:*"
                keys = self.redis_service.redis_client.get_keys_by_pattern(pattern)
                
                # 키에서 task_id 추출 (progress:{filename}:{task_id} 형태)
                redis_task_ids = []
                for key in keys:
                    parts = key.split(":")
                    if len(parts) >= 3:
                        task_id = parts[2]  # task_id는 세 번째 부분
                        redis_task_ids.append(task_id)
                
                active_tasks.extend(redis_task_ids)
            
            # 메모리에서도 확인
            memory_task_ids = list(_memory_progress_store.keys())
            active_tasks.extend(memory_task_ids)
            
            # 중복 제거
            active_tasks = list(set(active_tasks))
            
            self.logger.info(f"활성 태스크 조회 성공: {len(active_tasks)}개")
            return active_tasks
            
        except Exception as e:
            self.logger.error(f"활성 태스크 조회 중 오류 발생: {e}")
            return []


# 편의 함수들
def create_progress_tracker(task_id: Optional[str] = None) -> ProgressTracker:
    """진행률 추적기 생성 편의 함수"""
    return ProgressTracker(task_id)


def get_progress_by_task_id(task_id: str) -> Optional[Dict[str, Any]]:
    """태스크 ID로 진행률 조회 편의 함수"""
    service = ProgressService()
    return service.get_progress(task_id) 