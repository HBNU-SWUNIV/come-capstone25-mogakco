"""
S3 JSON 업로드 서비스
PRD 명세에 따른 대용량 JSON 파일 S3 업로드
"""
import json
import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class S3JsonUploader:
    """S3 JSON 파일 업로더"""

    def __init__(self):
        # S3 대상 (Access Point Alias/ARN 또는 버킷명)
        # 우선순위: S3_BUCKET_OR_ACCESS_POINT > S3_ACCESS_POINT_ALIAS > S3_ACCESS_POINT_ARN > S3_BUCKET_NAME
        self.bucket_or_ap = (
            os.getenv("S3_BUCKET_OR_ACCESS_POINT")
            or os.getenv("S3_ACCESS_POINT_ALIAS")
            or os.getenv("S3_ACCESS_POINT_ARN")
            or os.getenv("S3_BUCKET_NAME", "dyslexia-pdf")
        )
        self.prefix = os.getenv("S3_JSON_PREFIX", "dyslexia-results/")
        self.region = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-2")

        # AWS 자격증명 확인
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        if not self.aws_access_key_id or not self.aws_secret_access_key:
            logger.error("AWS 자격증명이 설정되지 않았습니다.")
            raise NoCredentialsError()

        # 실제 S3 쓰기(put/delete)에 사용할 대상 계산
        ap_arn = os.getenv("S3_ACCESS_POINT_ARN")
        bucket_name = os.getenv("S3_BUCKET_NAME", "dyslexia-pdf")
        if ap_arn:
            self.write_target = ap_arn
        else:
            if ("s3alias" in (self.bucket_or_ap or "")) or ("s3-accesspoint" in (self.bucket_or_ap or "")):
                self.write_target = bucket_name
            else:
                self.write_target = self.bucket_or_ap

        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            logger.info(
                (
                    "S3 JSON 업로더 초기화 완료 - "
                    f"target(read)={self.bucket_or_ap}, target(write)={self.write_target}, "
                    f"region={self.region}, prefix={self.prefix}"
                )
            )

        except Exception as e:
            logger.error(f"S3 클라이언트 초기화 실패: {e}")
            raise

    def generate_s3_key(self, job_id: str) -> str:
        """
        S3 키 생성 (PRD 4.2)

        형식: dyslexia-results/YYYY/MM/DD/{job_id}.json
        """
        current_date = datetime.now().strftime("%Y/%m/%d")
        s3_key = f"{self.prefix}{current_date}/{job_id}.json"
        return s3_key

    def _is_access_point(self) -> bool:
        ap = self.bucket_or_ap or ""
        return ap.startswith("arn:aws:s3") or ("s3alias" in ap) or ("s3-accesspoint" in ap)

    def _is_mrap_alias(self) -> bool:
        # 간단한 식별: 제공된 별칭에 's3alias'가 포함된 경우 MRAP 별칭으로 간주
        ap = self.bucket_or_ap or ""
        return "s3alias" in ap

    def _build_access_url(self, s3_key: str) -> str:
        # Access Point 사용 시 일반적으로 공개 URL을 사용하지 않으므로 프리사인드 URL을 권장
        presign_pref = os.getenv("S3_PRESIGN_RESULT_URL")
        presign_default = self._is_access_point()
        use_presign = (
            presign_pref.lower() in ("1", "true", "yes", "on") if isinstance(presign_pref, str) else presign_default
        )

        if use_presign:
            try:
                return self.s3_client.generate_presigned_url(
                    'get_object',
                    # 프리사인드는 실제 업로드 대상(write_target)에 대해 생성
                    Params={'Bucket': self.write_target, 'Key': s3_key},
                    ExpiresIn=int(os.getenv("S3_PRESIGN_EXPIRES", "3600"))
                )
            except Exception as e:
                logger.error(f"결과 프리사인드 URL 생성 실패: {e}")
                # presign 실패 시 도메인 기반 URL로 폴백

        if self._is_access_point():
            if self._is_mrap_alias():
                # MRAP 별칭의 글로벌 엔드포인트
                return f"https://{self.bucket_or_ap}.s3-global.amazonaws.com/{s3_key}"
            else:
                # Access Point 별칭의 리전 엔드포인트
                return f"https://{self.bucket_or_ap}.s3-accesspoint.{self.region}.amazonaws.com/{s3_key}"
        else:
            # 표준 버킷 도메인
            return f"https://{self.bucket_or_ap}.s3.{self.region}.amazonaws.com/{s3_key}"

    async def upload_json_result(self, job_id: str, result_data: Dict[str, Any]) -> str:
        """
        교안 생성 결과 JSON을 S3에 업로드 (PRD 4.2)

        Args:
            job_id: 작업 ID
            result_data: 교안 생성 결과 데이터

        Returns:
            S3 URL 또는 URI
        """
        try:
            # S3 키 생성
            s3_key = self.generate_s3_key(job_id)

            # 메타데이터 추가
            enhanced_data = {
                **result_data,
                "metadata": {
                    "job_id": job_id,
                    "generated_at": datetime.utcnow().isoformat(),
                    "service": "dyslexia-ai",
                    "version": "1.0.0"
                }
            }

            # JSON 직렬화
            json_content = json.dumps(enhanced_data, ensure_ascii=False, indent=2)
            json_bytes = json_content.encode('utf-8')

            # S3 업로드 파라미터
            upload_params = {
                # 업로드는 write_target에 수행
                'Bucket': self.write_target,
                'Key': s3_key,
                'Body': json_bytes,
                'ContentType': 'application/json',
                'ContentEncoding': 'utf-8',
                'CacheControl': 'max-age=31536000',  # 1년
                'Metadata': {
                    'job-id': job_id,
                    'uploaded-at': datetime.utcnow().isoformat(),
                    'service': 'dyslexia-ai',
                    'file-type': 'teaching-material-json'
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

            # S3에 업로드 (버킷 또는 Access Point)
            self.s3_client.put_object(**upload_params)

            # S3 URL 생성 (Access Point 고려)
            s3_url = self._build_access_url(s3_key)

            logger.info(f"JSON 결과 S3 업로드 성공: job_id={job_id}, key={s3_key}")

            return s3_url

        except ClientError as e:
            error_msg = f"S3 업로드 실패: {str(e)}"
            logger.error(f"JSON 업로드 실패: job_id={job_id}, error={error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)

        except json.JSONEncodeError as e:
            error_msg = f"JSON 직렬화 실패: {str(e)}"
            logger.error(f"JSON 직렬화 실패: job_id={job_id}, error={error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)

        except Exception as e:
            error_msg = f"예상치 못한 오류: {str(e)}"
            logger.error(f"JSON 업로드 중 예상치 못한 오류: job_id={job_id}, error={error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)

    def delete_json_result(self, job_id: str) -> bool:
        """S3에서 JSON 결과 삭제"""
        try:
            s3_key = self.generate_s3_key(job_id)

            self.s3_client.delete_object(
                Bucket=self.write_target,
                Key=s3_key
            )

            logger.info(f"S3 JSON 삭제 성공: job_id={job_id}, s3_key={s3_key}")
            return True

        except ClientError as e:
            logger.error(f"S3 JSON 삭제 실패: job_id={job_id}, error={str(e)}")
            return False

    def check_bucket_exists(self) -> bool:
        """S3 버킷 존재 여부 확인"""
        try:
            self.s3_client.head_bucket(Bucket=self.write_target)
            return True
        except ClientError:
            return False

    async def get_json_metadata(self, job_id: str) -> Optional[Dict[str, Any]]:
        """S3에서 JSON 파일 메타데이터 조회"""
        try:
            s3_key = self.generate_s3_key(job_id)

            response = self.s3_client.head_object(
                Bucket=self.write_target,
                Key=s3_key
            )

            return {
                "job_id": job_id,
                "s3_key": s3_key,
                "size": response['ContentLength'],
                "last_modified": response['LastModified'].isoformat(),
                "content_type": response['ContentType'],
                "metadata": response.get('Metadata', {})
            }

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            else:
                logger.error(f"S3 메타데이터 조회 실패: job_id={job_id}, error={str(e)}")
                raise


# 전역 인스턴스
s3_json_uploader = S3JsonUploader()


async def upload_result_to_s3(job_id: str, result_data: Dict[str, Any]) -> str:
    """헬퍼 함수: 교안 결과를 S3에 업로드"""
    return await s3_json_uploader.upload_json_result(job_id, result_data)


def delete_result_from_s3(job_id: str) -> bool:
    """헬퍼 함수: S3에서 교안 결과 삭제"""
    return s3_json_uploader.delete_json_result(job_id)


async def get_result_metadata(job_id: str) -> Optional[Dict[str, Any]]:
    """헬퍼 함수: S3 교안 결과 메타데이터 조회"""
    return await s3_json_uploader.get_json_metadata(job_id)
