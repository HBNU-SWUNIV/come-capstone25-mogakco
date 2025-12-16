import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException, UploadFile

logger = logging.getLogger(__name__)


class S3ImageUploader:
    def __init__(self):
        # .env 로드 보장 (라우터 import 시점 초기화 대비)
        try:
            load_dotenv()
        except Exception:
            pass
        # Access Point 관련 설정을 제거하고, 항상 버킷명만 사용해 단순화
        # 우선순위: S3_IMAGE_BUCKET_NAME > S3_BUCKET_NAME (기본값: dyslexia-pdf-bucket)
        self.bucket_name = (
            os.getenv("S3_IMAGE_BUCKET_NAME")
            or os.getenv("S3_BUCKET_NAME", "dyslexia-pdf-bucket")
        )
        self.prefix = os.getenv("S3_IMAGE_PREFIX", "resources/")
        self.region = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-2")

        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
            logger.info(
                f"S3 이미지 업로더 초기화 완료 - bucket={self.bucket_name}, region={self.region}, prefix={self.prefix}"
            )
        except NoCredentialsError:
            logger.error("AWS 자격 증명을 찾을 수 없습니다.")
            raise HTTPException(
                status_code=500,
                detail="AWS 자격 증명이 설정되지 않았습니다."
            )

    def _mask(self, value: Optional[str], keep_start: int = 4, keep_end: int = 4) -> str:
        if not value:
            return "<unset>"
        if len(value) <= keep_start + keep_end:
            return "*" * len(value)
        return f"{value[:keep_start]}***{value[-keep_end:]}"

    def _log_boot_diagnostics(self) -> None:
        # 민감정보는 마스킹하여 출력
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        session_token = os.getenv("AWS_SESSION_TOKEN")
        object_acl = os.getenv("S3_OBJECT_ACL")
        encryption = os.getenv("S3_ENCRYPTION")
        kms_id = os.getenv("S3_KMS_KEY_ID")
        presign = os.getenv("S3_PRESIGN_URL")
        presign_expires = os.getenv("S3_PRESIGN_EXPIRES", "3600")
        s3_bucket_name = os.getenv("S3_BUCKET_NAME")
        s3_image_bucket = os.getenv("S3_IMAGE_BUCKET_NAME")
        s3_bucket_or_ap = os.getenv("S3_BUCKET_OR_ACCESS_POINT")
        s3_ap_alias = os.getenv("S3_ACCESS_POINT_ALIAS")
        s3_ap_arn = os.getenv("S3_ACCESS_POINT_ARN")
        s3_image_prefix = os.getenv("S3_IMAGE_PREFIX")
        aws_region_env = os.getenv("AWS_DEFAULT_REGION")

        logger.info(
            "S3 업로더 설정 요약: "
            f"bucket={self.bucket_name}, region={self.region}, prefix={self.prefix}, "
            f"presign={str(presign).lower() if presign is not None else 'false'}, presign_expires={presign_expires}"
        )
        logger.info(
            "환경변수(S3/AWS) 로드 상태: "
            f"S3_BUCKET_NAME={s3_bucket_name or '<unset>'}, "
            f"S3_IMAGE_BUCKET_NAME={s3_image_bucket or '<unset>'}, "
            f"S3_BUCKET_OR_ACCESS_POINT={s3_bucket_or_ap or '<unset>'}, "
            f"S3_ACCESS_POINT_ALIAS={s3_ap_alias or '<unset>'}, "
            f"S3_ACCESS_POINT_ARN={s3_ap_arn or '<unset>'}, "
            f"S3_IMAGE_PREFIX={s3_image_prefix or '<unset>'}, "
            f"AWS_DEFAULT_REGION={aws_region_env or '<unset>'}"
        )
        logger.info(
            "AWS 자격증명 상태: "
            f"access_key_id={self._mask(access_key)}, "
            f"secret_access_key={self._mask(secret_key, keep_start=2, keep_end=2)}, "
            f"session_token={'set' if session_token else 'unset'}"
        )
        logger.info(
            "버킷 정책 관련 옵션: "
            f"S3_OBJECT_ACL={object_acl or 'none'}, "
            f"S3_ENCRYPTION={encryption or 'none'}, "
            f"S3_KMS_KEY_ID={self._mask(kms_id, keep_start=6, keep_end=6) if kms_id else 'none'}"
        )

    def log_connection_info(self) -> None:
        """애플리케이션 부팅 시 1회 호출용: 설정 요약 + 버킷 연결 확인 로그"""
        self._log_boot_diagnostics()
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(
                f"S3 연결 확인 성공: bucket={self.bucket_name}, region={self.region}"
            )
        except ClientError as e:
            code = e.response.get('Error', {}).get('Code', 'Unknown')
            msg = e.response.get('Error', {}).get('Message', str(e))
            logger.error(
                f"S3 연결 확인 실패: bucket={self.bucket_name}, region={self.region}, code={code}, message={msg}"
            )
        # 추가 S3 점검: 버킷 리전 및 ListObjects 권한
        try:
            loc = self.s3_client.get_bucket_location(Bucket=self.bucket_name)
            logger.info(
                f"S3 버킷 리전: LocationConstraint={loc.get('LocationConstraint') or 'us-east-1(default)'}"
            )
        except ClientError as e:
            code = e.response.get('Error', {}).get('Code', 'Unknown')
            msg = e.response.get('Error', {}).get('Message', str(e))
            logger.warning(
                f"S3 버킷 리전 조회 실패: code={code}, message={msg}"
            )
        try:
            resp = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=self.prefix, MaxKeys=1)
            logger.info(
                f"S3 ListObjects 권한: KeyCount={resp.get('KeyCount', 0)}, Prefix={self.prefix}"
            )
        except ClientError as e:
            code = e.response.get('Error', {}).get('Code', 'Unknown')
            msg = e.response.get('Error', {}).get('Message', str(e))
            logger.warning(
                f"S3 ListObjects 실패: code={code}, message={msg}"
            )

    def _generate_presigned_url(self, s3_key: str, expires_in: int = 3600) -> Optional[str]:
        try:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expires_in
            )
        except Exception as e:
            logger.error(f"Presigned URL 생성 실패: {e}")
            return None

    def _build_access_url(self, s3_key: str) -> Optional[str]:
        # 단순화: presign 요청 시 프리사인드, 아니면 표준 버킷 정적 URL 반환
        presign_pref = os.getenv("S3_PRESIGN_URL")
        use_presign = presign_pref.lower() in ("1", "true", "yes", "on") if isinstance(presign_pref, str) else False

        if use_presign:
            return self._generate_presigned_url(s3_key, int(os.getenv("S3_PRESIGN_EXPIRES", "3600")))

        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
    
    def validate_image_file(self, file: UploadFile) -> bool:
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="파일이 제공되지 않았습니다.")
        
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"지원되지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_extensions)}"
            )
        
        if file.size and file.size > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=400, 
                detail="파일 크기가 10MB를 초과합니다."
            )
        
        return True
    
    def generate_s3_key(self, filename: str) -> str:
        file_extension = Path(filename).suffix.lower()
        current_date = datetime.now().strftime("%Y/%m/%d")
        unique_id = str(uuid.uuid4())
        s3_key = f"{self.prefix}{current_date}/{unique_id}{file_extension}"
        return s3_key
    
    def upload_to_s3(self, file_content: bytes, s3_key: str, content_type: str) -> str:
        try:
            upload_params = {
                'Bucket': self.bucket_name,
                'Key': s3_key,
                'Body': file_content,
                'ContentType': content_type,
                'CacheControl': 'max-age=31536000',
                'Metadata': {
                    'uploaded_at': datetime.now().isoformat(),
                    'service': 'dyslexia-ai'
                }
            }

            # 선택적 업로드 옵션 (버킷 정책 대응)
            object_acl = os.getenv('S3_OBJECT_ACL')  # 예: 'bucket-owner-full-control'
            if object_acl:
                upload_params['ACL'] = object_acl

            sse = os.getenv('S3_ENCRYPTION')  # 'AES256' 또는 'aws:kms'
            if sse:
                upload_params['ServerSideEncryption'] = sse
                if sse == 'aws:kms':
                    kms_key_id = os.getenv('S3_KMS_KEY_ID')
                    if kms_key_id:
                        upload_params['SSEKMSKeyId'] = kms_key_id

            self.s3_client.put_object(**upload_params)
            public_url = self._build_access_url(s3_key)
            
            logger.info(f"S3 업로드 성공: {s3_key}")
            return public_url
        except ClientError as e:
            logger.error(f"S3 업로드 실패: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"S3 업로드 중 오류가 발생했습니다: {str(e)}"
            )
    
    def get_content_type(self, filename: str) -> str:
        extension_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp'
        }
        
        file_extension = Path(filename).suffix.lower()
        return extension_map.get(file_extension, 'application/octet-stream')
    
    async def upload_image(self, file: UploadFile) -> Dict[str, Any]:
        """이미지 업로드 메인 함수"""
        
        try:
            self.validate_image_file(file)
            file_content = await file.read()
            s3_key = self.generate_s3_key(file.filename)
            content_type = self.get_content_type(file.filename)
            public_url = self.upload_to_s3(file_content, s3_key, content_type)
            result = {
                "url": public_url,
                "s3_key": s3_key,
                "bucket": self.bucket_name,
                "filename": file.filename,
                "content_type": content_type,
                "file_size": len(file_content),
                "uploaded_at": datetime.now().isoformat()
            }
            
            logger.info(f"이미지 업로드 완료: {file.filename} -> {public_url}")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"이미지 업로드 중 예상치 못한 오류: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"이미지 업로드 중 오류가 발생했습니다: {str(e)}"
            )
    
    def upload_local_image(self, file_path: str) -> Dict[str, Any]:
        """로컬 이미지 파일 업로드"""
        
        try:
            if not os.path.exists(file_path):
                raise HTTPException(
                    status_code=404, 
                    detail=f"파일을 찾을 수 없습니다: {file_path}"
                )
            with open(file_path, 'rb') as f:
                file_content = f.read()
            filename = os.path.basename(file_path)
            s3_key = self.generate_s3_key(filename)
            content_type = self.get_content_type(filename)
            public_url = self.upload_to_s3(file_content, s3_key, content_type)
            result = {
                "url": public_url,
                "s3_key": s3_key,
                "bucket": self.bucket_name,
                "filename": filename,
                "content_type": content_type,
                "file_size": len(file_content),
                "uploaded_at": datetime.now().isoformat()
            }
            
            logger.info(f"로컬 이미지 업로드 완료: {file_path} -> {public_url}")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"로컬 이미지 업로드 중 예상치 못한 오류: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"로컬 이미지 업로드 중 오류가 발생했습니다: {str(e)}"
            )
    
    def delete_image(self, s3_key: str) -> Dict[str, Any]:
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"S3 이미지 삭제 성공: {s3_key}")
            return {
                "success": True,
                "message": "이미지 삭제 성공",
                "data": {
                    "s3_key": s3_key,
                    "deleted_at": datetime.now().isoformat()
                }
            }
            
        except ClientError as e:
            logger.error(f"S3 이미지 삭제 실패: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"이미지 삭제 중 오류가 발생했습니다: {str(e)}"
            )
    
    def check_bucket_exists(self) -> bool:
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError:
            return False


uploader = S3ImageUploader()

async def upload_image_to_s3(file: UploadFile) -> Dict[str, Any]:
    """이미지 업로드 헬퍼 함수"""
    return await uploader.upload_image(file)


def upload_local_image_to_s3(file_path: str) -> Dict[str, Any]:
    """로컬 이미지 업로드 헬퍼 함수"""
    return uploader.upload_local_image(file_path)


def delete_image_from_s3(s3_key: str) -> Dict[str, Any]:
    """이미지 삭제 헬퍼 함수"""
    return uploader.delete_image(s3_key)
