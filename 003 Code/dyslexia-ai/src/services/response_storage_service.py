import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..utils.redis_client import RedisClient


class ResponseStorageService:
    """응답 데이터 저장 서비스"""

    def __init__(self, redis_client: RedisClient):
        """
        응답 저장 서비스 초기화

        Args:
            redis_client: Redis 클라이언트 인스턴스
        """
        self.redis_client = redis_client
        self.logger = logging.getLogger(__name__)

    def save_processing_response(
        self, filename: str, results: Dict[str, Any], expire_hours: int = 24
    ) -> bool:
        """
        PDF 처리 응답을 Redis에 저장

        Args:
            filename: 처리된 파일명
            results: 처리 결과 데이터
            expire_hours: 만료 시간 (시간)

        Returns:
            저장 성공 여부
        """
        try:
            # 키 생성 전략: response:{filename}
            key = f"response:{filename}"

            # 저장할 데이터 구조
            response_data = {
                "filename": filename,
                "results": results,
                "created_at": datetime.now().isoformat(),
                "status": "completed",
            }

            # 만료 시간을 초로 변환
            expire_seconds = expire_hours * 3600

            # Redis에 저장
            success = self.redis_client.set_json(key, response_data, expire_seconds)

            if success:
                self.logger.info(f"응답 데이터 저장 성공: {filename}")

                # 파일명 인덱스도 저장 (검색용)
                self._save_filename_index(filename)

                return True
            else:
                self.logger.error(f"응답 데이터 저장 실패: {filename}")
                return False

        except Exception as e:
            self.logger.error(f"응답 저장 중 오류 발생: {e}")
            return False

    def get_processing_response(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        파일명으로 처리 응답 조회

        Args:
            filename: 조회할 파일명

        Returns:
            응답 데이터 또는 None
        """
        try:
            key = f"response:{filename}"
            response_data = self.redis_client.get_json(key)

            if response_data:
                self.logger.info(f"응답 데이터 조회 성공: {filename}")
                return response_data
            else:
                self.logger.warning(f"응답 데이터 없음: {filename}")
                return None

        except Exception as e:
            self.logger.error(f"응답 조회 중 오류 발생: {e}")
            return None

    def delete_processing_response(self, filename: str) -> bool:
        """
        처리 응답 삭제

        Args:
            filename: 삭제할 파일명

        Returns:
            삭제 성공 여부
        """
        try:
            key = f"response:{filename}"
            success = self.redis_client.delete(key)

            if success:
                self.logger.info(f"응답 데이터 삭제 성공: {filename}")
                # 인덱스에서도 제거
                self._remove_filename_index(filename)
                return True
            else:
                self.logger.warning(f"응답 데이터 삭제 실패 (키 없음): {filename}")
                return False

        except Exception as e:
            self.logger.error(f"응답 삭제 중 오류 발생: {e}")
            return False

    def response_exists(self, filename: str) -> bool:
        """
        응답 데이터 존재 여부 확인

        Args:
            filename: 확인할 파일명

        Returns:
            존재 여부
        """
        try:
            key = f"response:{filename}"
            return self.redis_client.exists(key)
        except Exception as e:
            self.logger.error(f"존재 확인 중 오류 발생: {e}")
            return False

    def save_from_json_file(self, json_file_path: str, expire_hours: int = 24) -> bool:
        """
        JSON 파일에서 데이터를 읽어서 Redis에 저장

        Args:
            json_file_path: JSON 파일 경로
            expire_hours: 만료 시간 (시간)

        Returns:
            저장 성공 여부
        """
        try:
            # JSON 파일 읽기
            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 파일명과 결과 추출
            filename = data.get("filename")
            results = data.get("results")

            if not filename or not results:
                self.logger.error(f"JSON 파일 형식 오류: filename 또는 results 없음")
                return False

            # Redis에 저장
            return self.save_processing_response(filename, results, expire_hours)

        except FileNotFoundError:
            self.logger.error(f"JSON 파일을 찾을 수 없음: {json_file_path}")
            return False
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 파싱 오류: {e}")
            return False
        except Exception as e:
            self.logger.error(f"JSON 파일 처리 중 오류 발생: {e}")
            return False

    def _save_filename_index(self, filename: str):
        """파일명 인덱스 저장 (검색용)"""
        try:
            index_key = "filename_index"
            # 기존 인덱스 가져오기
            existing_files = self.redis_client.get_json(index_key) or []

            # 중복 제거하고 새 파일명 추가
            if filename not in existing_files:
                existing_files.append(filename)
                self.redis_client.set_json(index_key, existing_files)
        except Exception as e:
            self.logger.error(f"파일명 인덱스 저장 실패: {e}")

    def _remove_filename_index(self, filename: str):
        """파일명 인덱스에서 제거"""
        try:
            index_key = "filename_index"
            existing_files = self.redis_client.get_json(index_key) or []

            if filename in existing_files:
                existing_files.remove(filename)
                self.redis_client.set_json(index_key, existing_files)
        except Exception as e:
            self.logger.error(f"파일명 인덱스 제거 실패: {e}")

    def get_all_filenames(self) -> List[str]:
        """저장된 모든 파일명 조회"""
        try:
            index_key = "filename_index"
            return self.redis_client.get_json(index_key) or []
        except Exception as e:
            self.logger.error(f"파일명 목록 조회 실패: {e}")
            return []
