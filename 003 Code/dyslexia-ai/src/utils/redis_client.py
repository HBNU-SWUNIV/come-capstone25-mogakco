import redis
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

class RedisClient:
    """Redis 클라이언트 유틸리티 클래스"""
    
    def __init__(self, host: str = '3.35.141.255', port: int = 6379, db: int = 0, 
                 decode_responses: bool = True, password: Optional[str] = None,
                 socket_timeout: Optional[int] = None, socket_connect_timeout: Optional[int] = None,
                 retry_on_timeout: bool = True, **kwargs):
        """
        Redis 클라이언트 초기화
        
        Args:
            host: Redis 서버 호스트
            port: Redis 서버 포트
            db: Redis 데이터베이스 번호
            decode_responses: 응답을 문자열로 디코딩할지 여부
            password: Redis 인증 비밀번호
            socket_timeout: 소켓 타임아웃
            socket_connect_timeout: 연결 타임아웃
            retry_on_timeout: 타임아웃 시 재시도 여부
            **kwargs: 기타 Redis 설정
        """
        self.host = host
        self.port = port
        self.db = db
        self.decode_responses = decode_responses
        self.password = password
        
        # Redis 연결 설정 준비
        redis_config = {
            'host': host,
            'port': port,
            'db': db,
            'decode_responses': decode_responses,
        }
        
        # 선택적 파라미터 추가
        if password:
            redis_config['password'] = password
        if socket_timeout:
            redis_config['socket_timeout'] = socket_timeout
        if socket_connect_timeout:
            redis_config['socket_connect_timeout'] = socket_connect_timeout
        if retry_on_timeout is not None:
            redis_config['retry_on_timeout'] = retry_on_timeout
        
        # 추가 설정 병합
        redis_config.update(kwargs)
        
        try:
            self.redis_client = redis.Redis(**redis_config)
            # 연결 테스트
            self.redis_client.ping()
            logging.info(f"Redis 연결 성공: {host}:{port} (DB: {db})")
        except Exception as e:
            logging.error(f"Redis 연결 실패: {e}")
            logging.error(f"Redis 설정: {redis_config}")
            print(f"Redis 연결 실패:")
            print(f"  - Host: {host}")
            print(f"  - Port: {port}")
            print(f"  - DB: {db}")
            print(f"  - 에러: {e}")
            raise
    
    def set_json(self, key: str, value: Dict[Any, Any], expire: Optional[int] = None) -> bool:
        """
        JSON 데이터를 Redis에 저장
        
        Args:
            key: Redis 키
            value: 저장할 JSON 데이터
            expire: 만료 시간 (초)
            
        Returns:
            저장 성공 여부
        """
        try:
            # 디버깅: 저장할 데이터 정보 출력
            print(f"Redis 저장 시도:")
            
            json_str = json.dumps(value, ensure_ascii=False)
            result = self.redis_client.set(key, json_str, ex=expire)
            
            # 저장 확인
            if result:
                # 즉시 조회해서 저장 확인
                check_result = self.redis_client.get(key)
                if check_result:
                    return True
                else:
                    return False
            else:
                print(f"저장 실패: Redis set 명령 실패")
                return False
                
        except Exception as e:
            print(f"JSON 저장 실패 - Key: {key}, Error: {e}")
            logging.error(f"JSON 저장 실패 - Key: {key}, Error: {e}")
            return False
    
    def get_json(self, key: str) -> Optional[Dict[Any, Any]]:
        """
        Redis에서 JSON 데이터 조회
        
        Args:
            key: Redis 키
            
        Returns:
            JSON 데이터 또는 None (키가 없는 경우)
        """
        try:
            # 디버깅: 조회 시도 정보 출력
            print(f"Redis 조회 시도:")
            print(f"  - Key: {key}")
            
            # 키 존재 여부 확인
            exists = self.redis_client.exists(key)
            print(f"  - Key exists: {exists}")
            
            if not exists:
                print(f"키가 존재하지 않음")
                return None
            
            json_str = self.redis_client.get(key)
            print(f"  - Retrieved data type: {type(json_str)}")
            print(f"  - Retrieved data length: {len(json_str) if json_str else 0}")
            
            if json_str is None:
                print(f"데이터가 None임 (만료되었을 수 있음)")
                return None
            
            data = json.loads(json_str)
            print(f"JSON 파싱 성공 (type: {type(data)})")
            return data
            
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 실패 - Key: {key}, Error: {e}")
            print(f"  - Raw data: {json_str[:200] if json_str else 'None'}...")
            logging.error(f"JSON 파싱 실패 - Key: {key}, Error: {e}")
            return None
        except Exception as e:
            print(f"JSON 조회 실패 - Key: {key}, Error: {e}")
            logging.error(f"JSON 조회 실패 - Key: {key}, Error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Redis에서 키 삭제
        
        Args:
            key: 삭제할 키
            
        Returns:
            삭제 성공 여부
        """
        try:
            result = self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logging.error(f"키 삭제 실패 - Key: {key}, Error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        키 존재 여부 확인
        
        Args:
            key: 확인할 키
            
        Returns:
            키 존재 여부
        """
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logging.error(f"키 존재 확인 실패 - Key: {key}, Error: {e}")
            return False
    
    def set_expiry(self, key: str, expire: int) -> bool:
        """
        키의 만료 시간 설정
        
        Args:
            key: 대상 키
            expire: 만료 시간 (초)
            
        Returns:
            설정 성공 여부
        """
        try:
            return self.redis_client.expire(key, expire)
        except Exception as e:
            logging.error(f"만료 시간 설정 실패 - Key: {key}, Error: {e}")
            return False 
    
    def delete_key(self, key: str) -> bool:
        """
        키 삭제 (delete 메서드의 alias)
        
        Args:
            key: 삭제할 키
            
        Returns:
            삭제 성공 여부
        """
        return self.delete(key)
    
    def get_keys_by_pattern(self, pattern: str) -> List[str]:
        """
        패턴에 맞는 모든 키 조회
        
        Args:
            pattern: 검색할 패턴 (예: "progress:*")
            
        Returns:
            패턴에 맞는 키 목록
        """
        try:
            keys = self.redis_client.keys(pattern)
            return [key.decode() if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
            logging.error(f"패턴 키 조회 실패 - Pattern: {pattern}, Error: {e}")
            return [] 