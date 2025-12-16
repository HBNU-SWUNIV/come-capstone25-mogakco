"""Redis 서비스 통합 모듈"""

import hashlib
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..utils.env_config import get_redis_config
from ..utils.redis_client import RedisClient
from .response_storage_service import ResponseStorageService


class RedisService:
    """Redis 서비스 통합 클래스"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Redis 서비스 초기화
        
        Args:
            config: Redis 설정 (None이면 환경변수에서 자동 로드)
        """
        self.config = config or get_redis_config()
        self.logger = logging.getLogger(__name__)
        
        # Redis 연결 설정 디버깅
        self.logger.info(f"Redis 연결 설정: {self.config}")
        
        # Redis 클라이언트 초기화
        try:
            self.redis_client = RedisClient(**self.config)
            self.logger.info(f"Redis 클라이언트 초기화 성공: {self.config['host']}:{self.config['port']}")
        except Exception as e:
            self.logger.error(f"Redis 클라이언트 초기화 실패: {e}")
            raise
        
        # 응답 저장 서비스 초기화
        self.response_storage = ResponseStorageService(self.redis_client)
    
    def save_response_from_json(self, json_file_path: str, expire_hours: int = 24) -> bool:
        """
        JSON 파일에서 응답 데이터 저장
        
        Args:
            json_file_path: JSON 파일 경로
            expire_hours: 만료 시간 (시간)
            
        Returns:
            저장 성공 여부
        """
        return self.response_storage.save_from_json_file(json_file_path, expire_hours)
    
    def save_response_data(self, filename: str, results: Dict[str, Any], expire_hours: int = 24) -> bool:
        """
        응답 데이터 직접 저장
        
        Args:
            filename: 파일명
            results: 처리 결과 데이터
            expire_hours: 만료 시간 (시간)
            
        Returns:
            저장 성공 여부
        """
        return self.response_storage.save_processing_response(filename, results, expire_hours)
    
    def save_output_by_hash(self, output_data: Dict[str, Any], expire_hours: int = 24) -> str:
        """
        생성된 output 데이터를 해시를 키로 하여 저장
        
        Args:
            output_data: 저장할 output 데이터
            expire_hours: 만료 시간 (시간)
            
        Returns:
            저장에 사용된 해시 키
        """
        try:
            # 결과 데이터를 JSON 문자열로 변환
            json_str = json.dumps(output_data, sort_keys=True, ensure_ascii=False)
            
            # SHA256 해시 생성
            hash_key = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
            
            # Redis 키 생성 (output: 접두사 사용)
            redis_key = f"output:{hash_key}"
            
            # 저장할 데이터 구조
            stored_data = {
                "output_data": output_data,
                "hash_key": hash_key,
                "created_at": datetime.now().isoformat(),
                "storage_type": "output_hash"
            }
            
            # 만료 시간을 초로 변환
            expire_seconds = expire_hours * 3600
            
            # Redis에 저장
            success = self.redis_client.set_json(redis_key, stored_data, expire_seconds)
            
            if success:
                self.logger.info(f"Output 해시 저장 성공: {hash_key[:16]}...")
                
                # 해시 인덱스에 추가
                self._add_to_hash_index(hash_key)
                
                return hash_key
            else:
                self.logger.error(f"Output 해시 저장 실패: {hash_key[:16]}...")
                return None
                
        except Exception as e:
            self.logger.error(f"Output 해시 저장 중 오류 발생: {e}")
            return None
    
    def save_output_by_timestamp(self, output_data: Dict[str, Any], expire_hours: int = 24) -> str:
        """
        생성된 output 데이터를 타임스탬프를 키로 하여 저장
        
        Args:
            output_data: 저장할 output 데이터
            expire_hours: 만료 시간 (시간)
            
        Returns:
            저장에 사용된 타임스탬프 키
        """
        try:
            # 타임스탬프 기반 키 생성
            timestamp_key = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # 밀리초까지
            
            # Redis 키 생성 (output_ts: 접두사 사용)
            redis_key = f"output_ts:{timestamp_key}"
            
            # 저장할 데이터 구조
            stored_data = {
                "output_data": output_data,
                "timestamp_key": timestamp_key,
                "created_at": datetime.now().isoformat(),
                "storage_type": "output_timestamp"
            }
            
            # 만료 시간을 초로 변환
            expire_seconds = expire_hours * 3600
            
            # Redis에 저장
            success = self.redis_client.set_json(redis_key, stored_data, expire_seconds)
            
            if success:
                self.logger.info(f"Output 타임스탬프 저장 성공: {timestamp_key}")
                
                # 타임스탬프 인덱스에 추가
                self._add_to_timestamp_index(timestamp_key)
                
                return timestamp_key
            else:
                self.logger.error(f"Output 타임스탬프 저장 실패: {timestamp_key}")
                return None
                
        except Exception as e:
            self.logger.error(f"Output 타임스탬프 저장 중 오류 발생: {e}")
            return None
    
    def save_output_by_uuid(self, output_data: Dict[str, Any], expire_hours: int = 24) -> str:
        """
        생성된 output 데이터를 UUID를 키로 하여 저장
        
        Args:
            output_data: 저장할 output 데이터
            expire_hours: 만료 시간 (시간)
            
        Returns:
            저장에 사용된 UUID 키
        """
        try:
            # UUID 생성
            uuid_key = str(uuid.uuid4())
            
            # Redis 키 생성 (output_uuid: 접두사 사용)
            redis_key = f"output_uuid:{uuid_key}"
            
            # 저장할 데이터 구조
            stored_data = {
                "output_data": output_data,
                "uuid_key": uuid_key,
                "created_at": datetime.now().isoformat(),
                "storage_type": "output_uuid"
            }
            
            # 만료 시간을 초로 변환
            expire_seconds = expire_hours * 3600
            
            # Redis에 저장
            success = self.redis_client.set_json(redis_key, stored_data, expire_seconds)
            
            if success:
                self.logger.info(f"Output UUID 저장 성공: {uuid_key}")
                
                # UUID 인덱스에 추가
                self._add_to_uuid_index(uuid_key)
                
                return uuid_key
            else:
                self.logger.error(f"Output UUID 저장 실패: {uuid_key}")
                return None
                
        except Exception as e:
            self.logger.error(f"Output UUID 저장 중 오류 발생: {e}")
            return None
    
    def save_output_by_task_id(self, task_id: str, filename: str, output_data: Dict[str, Any], expire_hours: int = 24) -> bool:
        """
        생성된 output 데이터를 filename:task_id를 키로 하여 저장
        
        Args:
            task_id: 태스크 ID
            filename: 파일명
            output_data: 저장할 output 데이터
            expire_hours: 만료 시간 (시간)
            
        Returns:
            저장 성공 여부
        """
        try:
            # Redis 키 생성 (output_task:{filename}:{task_id} 형태)
            redis_key = f"output_task:{filename}:{task_id}"
            
            # 저장할 데이터 구조
            stored_data = {
                "output_data": output_data,
                "task_id": task_id,
                "filename": filename,
                "created_at": datetime.now().isoformat(),
                "storage_type": "output_task"
            }
            
            # 만료 시간을 초로 변환
            expire_seconds = expire_hours * 3600
            
            # Redis에 저장
            success = self.redis_client.set_json(redis_key, stored_data, expire_seconds)
            
            if success:
                self.logger.info(f"Output task_id 저장 성공: {filename}:{task_id}")
                
                # task_id 인덱스에 추가
                self._add_to_task_id_index(task_id)
                
                # 파일명별 인덱스에 추가
                self._add_to_file_index(filename, task_id)
                
                return True
            else:
                self.logger.error(f"Output task_id 저장 실패: {filename}:{task_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Output task_id 저장 중 오류 발생: {e}")
            return False
    
    def get_output_by_hash(self, hash_key: str) -> Optional[Dict[str, Any]]:
        """
        해시 키로 output 데이터 조회
        
        Args:
            hash_key: 조회할 해시 키
            
        Returns:
            output 데이터 또는 None
        """
        try:
            redis_key = f"output:{hash_key}"
            stored_data = self.redis_client.get_json(redis_key)
            
            if stored_data:
                self.logger.info(f"Output 해시 조회 성공: {hash_key[:16]}...")
                return stored_data.get("output_data")
            else:
                self.logger.warning(f"Output 해시 조회 실패: {hash_key[:16]}...")
                return None
                
        except Exception as e:
            self.logger.error(f"Output 해시 조회 중 오류 발생: {e}")
            return None
    
    def get_output_by_timestamp(self, timestamp_key: str) -> Optional[Dict[str, Any]]:
        """
        타임스탬프 키로 output 데이터 조회
        
        Args:
            timestamp_key: 조회할 타임스탬프 키
            
        Returns:
            output 데이터 또는 None
        """
        try:
            redis_key = f"output_ts:{timestamp_key}"
            stored_data = self.redis_client.get_json(redis_key)
            
            if stored_data:
                self.logger.info(f"Output 타임스탬프 조회 성공: {timestamp_key}")
                return stored_data.get("output_data")
            else:
                self.logger.warning(f"Output 타임스탬프 조회 실패: {timestamp_key}")
                return None
                
        except Exception as e:
            self.logger.error(f"Output 타임스탬프 조회 중 오류 발생: {e}")
            return None
    
    def get_output_by_uuid(self, uuid_key: str) -> Optional[Dict[str, Any]]:
        """
        UUID 키로 output 데이터 조회
        
        Args:
            uuid_key: 조회할 UUID 키
            
        Returns:
            output 데이터 또는 None
        """
        try:
            redis_key = f"output_uuid:{uuid_key}"
            stored_data = self.redis_client.get_json(redis_key)
            
            if stored_data:
                self.logger.info(f"Output UUID 조회 성공: {uuid_key}")
                return stored_data.get("output_data")
            else:
                self.logger.warning(f"Output UUID 조회 실패: {uuid_key}")
                return None
                
        except Exception as e:
            self.logger.error(f"Output UUID 조회 중 오류 발생: {e}")
            return None
    
    def get_output_by_task_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        task_id로 output 데이터 조회
        
        Args:
            task_id: 조회할 task_id
            
        Returns:
            output 데이터 또는 None
        """
        try:
            # 파일명별 인덱스에서 조회
            index_key = "file_index" # 파일명별 인덱스 키
            file_index = self.redis_client.get_json(index_key) or {}
            
            for filename, task_list in file_index.items():
                if task_id in task_list:
                    redis_key = f"output_task:{filename}:{task_id}"
                    stored_data = self.redis_client.get_json(redis_key)
                    
                    if stored_data:
                        self.logger.info(f"Output task_id 조회 성공: {task_id} (파일: {filename})")
                        return stored_data.get("output_data")
                    else:
                        self.logger.warning(f"Output task_id 조회 실패: {task_id} (파일: {filename})")
                        continue
            
            self.logger.warning(f"Output task_id 조회 실패: {task_id} (인덱스 또는 데이터 없음)")
            return None
                
        except Exception as e:
            self.logger.error(f"Output task_id 조회 중 오류 발생: {e}")
            return None
    
    def get_response_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        응답 데이터 조회
        
        Args:
            filename: 파일명
            
        Returns:
            응답 데이터 또는 None
        """
        return self.response_storage.get_processing_response(filename)
    
    def delete_response_data(self, filename: str) -> bool:
        """
        응답 데이터 삭제
        
        Args:
            filename: 파일명
            
        Returns:
            삭제 성공 여부
        """
        return self.response_storage.delete_processing_response(filename)
    
    def response_exists(self, filename: str) -> bool:
        """
        응답 데이터 존재 여부 확인
        
        Args:
            filename: 파일명
            
        Returns:
            존재 여부
        """
        return self.response_storage.response_exists(filename)
    
    def get_all_filenames(self) -> List[str]:
        """
        저장된 모든 파일명 조회
        
        Returns:
            파일명 목록
        """
        return self.response_storage.get_all_filenames()
    
    def get_all_hash_keys(self) -> List[str]:
        """
        저장된 모든 해시 키 조회
        
        Returns:
            해시 키 목록
        """
        try:
            index_key = "hash_index"
            return self.redis_client.get_json(index_key) or []
        except Exception as e:
            self.logger.error(f"해시 키 목록 조회 실패: {e}")
            return []
    
    def get_all_timestamp_keys(self) -> List[str]:
        """
        저장된 모든 타임스탬프 키 조회
        
        Returns:
            타임스탬프 키 목록 (최신순)
        """
        try:
            index_key = "timestamp_index"
            keys = self.redis_client.get_json(index_key) or []
            return sorted(keys, reverse=True)  # 최신순 정렬
        except Exception as e:
            self.logger.error(f"타임스탬프 키 목록 조회 실패: {e}")
            return []
    
    def get_all_uuid_keys(self) -> List[str]:
        """
        저장된 모든 UUID 키 조회
        
        Returns:
            UUID 키 목록
        """
        try:
            index_key = "uuid_index"
            return self.redis_client.get_json(index_key) or []
        except Exception as e:
            self.logger.error(f"UUID 키 목록 조회 실패: {e}")
            return []
    
    def get_all_task_ids(self) -> List[str]:
        """
        저장된 모든 task_id 조회
        
        Returns:
            task_id 목록
        """
        try:
            index_key = "task_id_index"
            return self.redis_client.get_json(index_key) or []
        except Exception as e:
            self.logger.error(f"task_id 목록 조회 실패: {e}")
            return []
    
    def get_all_files_with_tasks(self) -> Dict[str, List[str]]:
        """
        파일명별 태스크 ID 목록 조회
        
        Returns:
            파일명: [task_id1, task_id2, ...] 형태의 딕셔너리
        """
        try:
            index_key = "file_index"
            return self.redis_client.get_json(index_key) or {}
        except Exception as e:
            self.logger.error(f"파일명별 태스크 ID 목록 조회 실패: {e}")
            return {}
    
    def get_file_task_ids(self, filename: str) -> List[str]:
        """
        특정 파일의 태스크 ID 목록 조회
        
        Args:
            filename: 파일명
            
        Returns:
            해당 파일의 태스크 ID 목록
        """
        try:
            index_key = "file_index"
            file_index = self.redis_client.get_json(index_key) or {}
            return file_index.get(filename, [])
        except Exception as e:
            self.logger.error(f"파일별 태스크 ID 목록 조회 실패: {e}")
            return []
    
    def get_output_by_filename_and_task_id(self, filename: str, task_id: str) -> Optional[Dict[str, Any]]:
        """
        파일명과 태스크 ID로 output 데이터 조회
        
        Args:
            filename: 파일명
            task_id: 태스크 ID
            
        Returns:
            output 데이터 또는 None
        """
        try:
            redis_key = f"output_task:{filename}:{task_id}"
            stored_data = self.redis_client.get_json(redis_key)
            
            if stored_data:
                self.logger.info(f"Output 조회 성공: {filename}:{task_id}")
                return stored_data.get("output_data")
            else:
                self.logger.warning(f"Output 조회 실패: {filename}:{task_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Output 조회 중 오류 발생: {e}")
            return None
    
    def get_latest_output_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        파일명으로 가장 최근 output 데이터 조회
        
        Args:
            filename: 파일명
            
        Returns:
            가장 최근 output 데이터 또는 None
        """
        try:
            task_ids = self.get_file_task_ids(filename)
            if not task_ids:
                return None
            
            # 가장 최근 태스크 ID 선택 (마지막 요소)
            latest_task_id = task_ids[-1]
            return self.get_output_by_filename_and_task_id(filename, latest_task_id)
            
        except Exception as e:
            self.logger.error(f"최근 Output 조회 중 오류 발생: {e}")
            return None
    
    def get_response_summary(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        응답 데이터 요약 정보 조회
        
        Args:
            filename: 파일명
            
        Returns:
            요약 정보 또는 None
        """
        response_data = self.get_response_data(filename)
        if not response_data:
            return None
        
        results = response_data.get('results', {})
        transformation = results.get('transformation', {})
        metadata = results.get('metadata', {})
        
        return {
            "filename": response_data.get('filename'),
            "created_at": response_data.get('created_at'),
            "status": response_data.get('status'),
            "preprocessing": {
                "total_chunks": metadata.get('total_chunks', 0),
                "total_tokens": metadata.get('total_tokens', 0),
                "processing_time": metadata.get('preprocessing_time', 0)
            },
            "transformation": {
                "total_blocks": transformation.get('metadata', {}).get('total_blocks', 0),
                "processing_time": transformation.get('metadata', {}).get('processing_time', 0)
            }
        }
    
    def cleanup_expired_responses(self) -> int:
        """
        만료된 응답 데이터 정리
        
        Returns:
            정리된 항목 수
        """
        all_filenames = self.get_all_filenames()
        cleaned_count = 0
        
        for filename in all_filenames:
            if not self.response_exists(filename):
                # Redis에서는 만료되었지만 인덱스에는 남아있는 경우
                self.response_storage._remove_filename_index(filename)
                cleaned_count += 1
        
        self.logger.info(f"정리된 만료 응답 수: {cleaned_count}")
        return cleaned_count
    
    def _add_to_hash_index(self, hash_key: str):
        """해시 키를 인덱스에 추가"""
        try:
            index_key = "hash_index"
            existing_keys = self.redis_client.get_json(index_key) or []
            
            if hash_key not in existing_keys:
                existing_keys.append(hash_key)
                self.redis_client.set_json(index_key, existing_keys)
        except Exception as e:
            self.logger.error(f"해시 인덱스 추가 실패: {e}")
    
    def _add_to_timestamp_index(self, timestamp_key: str):
        """타임스탬프 키를 인덱스에 추가"""
        try:
            index_key = "timestamp_index"
            existing_keys = self.redis_client.get_json(index_key) or []
            
            if timestamp_key not in existing_keys:
                existing_keys.append(timestamp_key)
                self.redis_client.set_json(index_key, existing_keys)
        except Exception as e:
            self.logger.error(f"타임스탬프 인덱스 추가 실패: {e}")
    
    def _add_to_uuid_index(self, uuid_key: str):
        """UUID 키를 인덱스에 추가"""
        try:
            index_key = "uuid_index"
            existing_keys = self.redis_client.get_json(index_key) or []
            
            if uuid_key not in existing_keys:
                existing_keys.append(uuid_key)
                self.redis_client.set_json(index_key, existing_keys)
        except Exception as e:
            self.logger.error(f"UUID 인덱스 추가 실패: {e}")
    
    def _add_to_task_id_index(self, task_id: str):
        """task_id를 인덱스에 추가"""
        try: 
            index_key = "task_id_index" # TODO: 파일명으로 전달하기
            existing_keys = self.redis_client.get_json(index_key) or []
            
            if task_id not in existing_keys:
                existing_keys.append(task_id)
                self.redis_client.set_json(index_key, existing_keys)
        except Exception as e:
            self.logger.error(f"task_id 인덱스 추가 실패: {e}")

    def _add_to_file_index(self, filename: str, task_id: str):
        """파일명별 태스크 ID 인덱스에 추가"""
        try:
            index_key = "file_index"
            existing_files = self.redis_client.get_json(index_key) or {}
            
            if filename not in existing_files:
                existing_files[filename] = []
            
            if task_id not in existing_files[filename]:
                existing_files[filename].append(task_id)
                
            self.redis_client.set_json(index_key, existing_files)
        except Exception as e:
            self.logger.error(f"파일명별 태스크 ID 인덱스 추가 실패: {e}")


def create_redis_service() -> RedisService:
    """Redis 서비스 팩토리 함수"""
    return RedisService()


# 편의 함수들
def save_json_response(json_file_path: str, expire_hours: int = 24) -> bool:
    """JSON 파일에서 응답 저장 (편의 함수)"""
    service = create_redis_service()
    return service.save_response_from_json(json_file_path, expire_hours)


def save_output_by_hash(output_data: Dict[str, Any], expire_hours: int = 24) -> str:
    """Output 데이터를 해시 키로 저장 (편의 함수)"""
    service = create_redis_service()
    return service.save_output_by_hash(output_data, expire_hours)


def save_output_by_timestamp(output_data: Dict[str, Any], expire_hours: int = 24) -> str:
    """Output 데이터를 타임스탬프 키로 저장 (편의 함수)"""
    service = create_redis_service()
    return service.save_output_by_timestamp(output_data, expire_hours)


def get_response(filename: str) -> Optional[Dict[str, Any]]:
    """응답 조회 (편의 함수)"""
    service = create_redis_service()
    return service.get_response_data(filename)


def get_output_by_hash(hash_key: str) -> Optional[Dict[str, Any]]:
    """해시 키로 output 조회 (편의 함수)"""
    service = create_redis_service()
    return service.get_output_by_hash(hash_key)


def get_output_by_task_id(task_id: str) -> Optional[Dict[str, Any]]:
    """task_id로 output 조회 (편의 함수)"""
    service = create_redis_service()
    return service.get_output_by_task_id(task_id)


def delete_response(filename: str) -> bool:
    """응답 삭제 (편의 함수)"""
    service = create_redis_service()
    return service.delete_response_data(filename) 