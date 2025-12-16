from dotenv import load_dotenv
import os
from typing import Optional


def setup_environment():
    """환경변수 설정: .env 로드 → 키 검증/주입 → 디렉터리 생성"""
    load_dotenv()

    anthropic_api_key = get_anthropic_api_key(required=True)
    replicate_api_token = get_replicate_api_token(required=True)
    temp_dir = get_temp_dir(default="./temp")

    if anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key
    if replicate_api_token:
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

    os.makedirs(temp_dir, exist_ok=True)

    return None


def get_anthropic_api_key(required: bool = True) -> Optional[str]:
    """Anthropic API 키를 반환. required=True이면 없을 때 예외 발생."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    api_key = api_key.strip() if api_key else None
    if required and not api_key:
        raise ValueError("ANTHROPIC_API_KEY를 .env 파일에 설정해주세요.")
    return api_key


def get_replicate_api_token(required: bool = True) -> Optional[str]:
    """Replicate API 토큰을 반환. required=True이면 없을 때 예외 발생."""
    token = os.getenv("REPLICATE_API_TOKEN")
    token = token.strip() if token else None
    if required and not token:
        raise ValueError("REPLICATE_API_TOKEN을 .env 파일에 설정해주세요.")
    return token


def get_temp_dir(default: str = "./temp") -> str:
    """TEMP 디렉터리 경로를 반환. 부수효과(생성) 없이 경로만 반환."""
    temp_dir = os.getenv("TEMP_DIR", default)
    temp_dir = temp_dir.strip() or default
    return temp_dir


def get_redis_config():
    """Redis 설정을 반환하는 함수"""
    load_dotenv()

    redis_host = os.getenv("REDIS_HOST", "3.35.141.255")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_password = os.getenv("REDIS_PASSWORD", None)
    redis_db = int(os.getenv("REDIS_DB", "0"))

    config = {
        "host": redis_host,
        "port": redis_port,
        "db": redis_db,
        "decode_responses": True,
        "socket_timeout": 5,
        "socket_connect_timeout": 5,
        "retry_on_timeout": True,
    }

    if redis_password:
        config["password"] = redis_password

    return config


def get_spring_callback_url(required: bool = False) -> Optional[str]:
    """Spring 콜백 URL을 반환.

    우선순위:
      1) SPRING_CALLBACK_URL (전체 경로 지정)
      2) SPRING_SERVER_BASE_URL + SPRING_COMPLETE_PATH (기본 "/api/document/complete")
    """
    load_dotenv()

    direct = os.getenv("SPRING_CALLBACK_URL")
    if direct and direct.strip():
        return direct.strip()

    base = os.getenv("SPRING_SERVER_BASE_URL")
    if base and base.strip():
        base = base.strip().rstrip("/")
        path = os.getenv("SPRING_COMPLETE_PATH", "/api/document/complete").strip()
        if not path.startswith("/"):
            path = "/" + path
        return f"{base}{path}"

    if required:
        raise ValueError("Spring 콜백 URL이 설정되지 않았습니다. SPRING_CALLBACK_URL 또는 SPRING_SERVER_BASE_URL을 설정해주세요.")

    return None
