import asyncio
import logging
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from fastapi import UploadFile

from src.services.image_uploader import upload_local_image_to_s3
from src.services.job_manager import (
    JobManager,
    JobStatus,
    JobStep,
    save_job_result,
    update_job_progress,
)
from src.services.redis_pub_sub_service import (
    publish_progress as publish_redis_progress,
    publish_result as publish_redis_result,
    publish_failure as publish_redis_failure,
)

logger = logging.getLogger(__name__)


@dataclass
class ThumbnailResult:
    job_id: str
    filename: str
    s3_url: str
    s3_key: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: str = datetime.utcnow().isoformat() + "Z"


class ThumbnailService:
    """썸네일 생성 서비스 (PDF 첫 페이지 또는 이미지 리사이즈)"""

    def __init__(self, max_size: Tuple[int, int] = (512, 512)):
        self.max_size = max_size
        self.job_manager = JobManager()

    async def start(self, file: UploadFile, job_id: Optional[str] = None) -> str:
        """비동기 썸네일 생성 파이프라인 시작"""
        if job_id:
            # 외부에서 전달된 job_id를 사용해 초기 상태를 저장
            try:
                # create_job은 새 job_id를 생성하므로, 외부 job_id를 존중하기 위해 직접 progress 초기화
                now = datetime.now()
                from src.services.job_manager import JobProgress

                progress = JobProgress(
                    job_id=job_id,
                    status=JobStatus.PENDING,
                    current_step=JobStep.INITIALIZATION,
                    progress_percentage=0.0,
                    step_details={},
                    total_steps=len(self.job_manager.step_weights) - 1,
                    current_step_index=0,
                    started_at=now,
                    updated_at=now,
                )
                # Redis 저장
                self.job_manager.redis_service.redis_client.redis_client.setex(
                    f"{self.job_manager.job_progress_prefix}{job_id}",
                    self.job_manager.job_expiry_hours * 3600,
                    __import__("json").dumps(progress.to_dict()),
                )
            except Exception as e:
                logger.warning(f"외부 job_id 초기화 실패, 새로 생성합니다: {e}")
                job_id = None

        if not job_id:
            job_id = self.job_manager.create_job(filename=file.filename)

        # 파일을 임시 저장
        temp_dir = os.getenv("TEMP_DIR", "./temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_input_path = os.path.join(temp_dir, f"{job_id}_{file.filename}")
        content = await file.read()
        with open(temp_input_path, "wb") as f:
            f.write(content)

        # 백그라운드 실행
        asyncio.create_task(self._run_pipeline(job_id, file.filename, temp_input_path))
        return job_id

    async def _run_pipeline(self, job_id: str, filename: str, input_path: str) -> None:
        try:
            # 초기화 단계
            update_job_progress(
                job_id=job_id,
                status=JobStatus.PREPROCESSING,
                current_step=JobStep.PDF_EXTRACTION,
                step_details={"message": "썸네일 준비"},
            )
            await publish_redis_progress(job_id, 5)

            # 전략 선택: recraft(기본) | render
            strategy = os.getenv("THUMBNAIL_STRATEGY", "recraft").strip().lower()
            if strategy not in {"recraft", "render"}:
                strategy = "recraft"

            if strategy == "recraft":
                s3_url, s3_key, size = await self._generate_thumbnail_via_recraft(
                    job_id, filename, input_path
                )
            else:
                # 로컬 썸네일 생성 후 업로드
                thumb_path, size = await asyncio.get_event_loop().run_in_executor(
                    None, self._generate_thumbnail_sync, input_path, filename
                )
                upload_result = upload_local_image_to_s3(thumb_path)
                s3_url = upload_result.get("url")
                s3_key = upload_result.get("s3_key")
            update_job_progress(
                job_id=job_id,
                status=JobStatus.GENERATING_IMAGES,
                current_step=JobStep.IMAGE_GENERATION,
                step_details={"message": "썸네일 생성 중", "size": size},
            )
            await publish_redis_progress(job_id, 50)

            # Redis 결과 발행
            if s3_url:
                await publish_redis_result(job_id, s3_url)

            update_job_progress(
                job_id=job_id,
                status=JobStatus.WEBHOOK_SENDING,
                current_step=JobStep.WEBHOOK_NOTIFICATION,
                step_details={"message": "Spring 콜백 전송"},
            )
            await publish_redis_progress(job_id, 90)

            # 결과 저장
            result_payload: Dict[str, Any] = {
                "thumbnail_url": s3_url,
                "s3_key": s3_key,
                "width": size[0] if size else None,
                "height": size[1] if size else None,
            }
            metadata = {"filename": filename, "type": "thumbnail"}
            save_job_result(job_id, result_payload, metadata)

            # Spring 완료 콜백 전송 (기존 문서 완료 콜백 포맷 재활용)
            # 요구사항: SPRING_SERVER_BASE_URL 기반 /api/textbook/thumbnail/{jobId}
            # send_document_complete는 기본 complete 엔드포인트용이므로, 여기선 별도 호출 구현
            await self._send_thumbnail_callback(job_id, filename, s3_url, s3_key, size)

            update_job_progress(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                current_step=JobStep.COMPLETED,
                step_details={"message": "썸네일 생성 완료"},
            )
            await publish_redis_progress(job_id, 100)

        except Exception as e:
            logger.error(f"썸네일 파이프라인 실패: job_id={job_id}, error={e}", exc_info=True)
            await publish_redis_failure(job_id, str(e))
            from src.services.job_manager import mark_job_failed

            mark_job_failed(job_id, str(e))
        finally:
            try:
                if os.path.exists(input_path):
                    os.unlink(input_path)
            except Exception:
                pass

    async def _generate_thumbnail_via_recraft(self, job_id: str, filename: str, input_path: str):
        """체인을 통해 인물/서사/배경을 추출하고 Recraft 이미지로 썸네일 생성"""
        try:
            # 1) 간단 전처리: 텍스트 추출 → 청킹
            from src.models import PreprocessingOptions
            from src.services.preprocessing_service import run_preprocessing_pipeline
            from src.services.transformation_service import transform_content_to_blocks
            from src.core.prompts import create_image_generation_prompt
            from src.services.image_generation_service import generate_image_with_s3_upload

            with open(input_path, "rb") as f:
                content = f.read()
            fake_file = UploadFile(file=BytesIO(content), filename=filename, size=len(content))

            prep_options = PreprocessingOptions(
                temp_dir=os.getenv("TEMP_DIR", "./temp"),
                remove_headers_footers=True,
                header_height=30.0,
                footer_height=30.0,
                max_tokens=8000,
            )
            prep = run_preprocessing_pipeline(
                file=fake_file,
                options=prep_options,
                return_text=False,
                return_chunks=True,
                model=os.getenv("RECRAFT_PROMPT_MODEL", "claude-sonnet-4-20250514"),
            )

            chunks = prep.get("chunks") or []
            if not chunks:
                raise ValueError("전처리 결과 청크가 없습니다")

            # 2) 블록 변환만 실행 (이미지 생성 비활성화)
            transformed = await transform_content_to_blocks(
                content=chunks,
                model_name=os.getenv("RECRAFT_PROMPT_MODEL", "claude-sonnet-4-20250514"),
                max_concurrent=4,
                image_interval=12,
                word_limit=15,
                vocabulary_interval=5,
                save_to_redis=False,
                expire_hours=12,
                generate_images=False,
            )

            blocks = transformed.get("transformed_blocks", [])
            # 3) PAGE_IMAGE 블록 우선, 없으면 HEADING/TEXT로 대체
            subject = None
            for b in blocks:
                if b.get("type") == "PAGE_IMAGE":
                    subject = b.get("prompt") or b.get("concept") or b.get("alt")
                    if subject:
                        break
            if not subject:
                for b in blocks:
                    if b.get("type", "").startswith("HEADING") and b.get("text"):
                        subject = b.get("text")
                        break
                if not subject:
                    for b in blocks:
                        if b.get("type") == "TEXT" and b.get("text"):
                            subject = (b.get("text") or "").strip()[:180]
                            break
            if not subject:
                subject = os.path.splitext(filename)[0]

            # 4) 주제 설명만 전달 (고정 스타일은 내부 프롬프트 생성 함수에서 결합)
            gen = await asyncio.get_event_loop().run_in_executor(
                None,
                generate_image_with_s3_upload,
                subject,
                "any",
                "1536x1024",
                "google/nano-banana",
                "jpg",
                True,
            )

            url = gen.get("url")
            s3_key = gen.get("s3_key")
            try:
                w, h = (int(x) for x in "1536x1024".split("x"))
                size = (w, h)
            except Exception:
                size = None
            return url, s3_key, size
        except Exception as e:
            logger.error(f"Recraft 썸네일 생성 실패, 렌더링 방식으로 대체: {e}")
            # 폴백: 로컬 렌더 + 업로드
            thumb_path, size = self._generate_thumbnail_sync(input_path, filename)
            upload_result = upload_local_image_to_s3(thumb_path)
            return upload_result.get("url"), upload_result.get("s3_key"), size

    def _generate_thumbnail_sync(self, input_path: str, orig_filename: str) -> Tuple[str, Optional[Tuple[int, int]]]:
        """동기 썸네일 생성 (PIL + pdfplumber)"""
        from PIL import Image
        suffix = Path(orig_filename).suffix.lower()

        # 출력 경로 준비
        temp_dir = os.getenv("TEMP_DIR", "./temp")
        os.makedirs(temp_dir, exist_ok=True)
        out_path = os.path.join(temp_dir, f"{Path(orig_filename).stem}_thumb.png")

        if suffix in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}:
            with Image.open(input_path) as im:
                im = im.convert("RGB") if im.mode in ("P", "LA", "RGBA") else im
                im.thumbnail(self.max_size)
                im.save(out_path, format="PNG")
                return out_path, im.size

        if suffix == ".pdf":
            try:
                import pdfplumber

                with pdfplumber.open(input_path) as pdf:
                    if not pdf.pages:
                        raise ValueError("PDF에 페이지가 없습니다.")
                    page = pdf.pages[0]
                    # to_image()는 내부적으로 PIL 이미지를 생성함
                    page_image = page.to_image(resolution=150)
                    pil_im = page_image.original
                    if pil_im.mode in ("P", "LA", "RGBA"):
                        pil_im = pil_im.convert("RGB")
                    pil_im.thumbnail(self.max_size)
                    pil_im.save(out_path, format="PNG")
                    return out_path, pil_im.size
            except Exception as e:
                logger.error(f"PDF 썸네일 생성 실패, 플레이스홀더 생성으로 대체: {e}")
                # 플레이스홀더(회색) 이미지 생성
                from PIL import Image, ImageDraw

                im = Image.new("RGB", self.max_size, color=(230, 230, 230))
                d = ImageDraw.Draw(im)
                d.text((10, 10), "No preview", fill=(120, 120, 120))
                im.save(out_path, format="PNG")
                return out_path, im.size

        # 알 수 없는 형식: 원본을 PNG로 리랩 (가능한 경우)
        try:
            from PIL import Image

            with Image.open(input_path) as im:
                im = im.convert("RGB") if im.mode in ("P", "LA", "RGBA") else im
                im.thumbnail(self.max_size)
                im.save(out_path, format="PNG")
                return out_path, im.size
        except Exception as e:
            raise ValueError(f"지원하지 않는 파일 형식입니다: {orig_filename} ({e})")

    async def _send_thumbnail_callback(
        self,
        job_id: str,
        filename: str,
        s3_url: str,
        s3_key: Optional[str],
        size: Optional[Tuple[int, int]],
    ) -> bool:
        """SPRING_SERVER_BASE_URL 기반 /api/textbook/thumbnail/{jobId}로 콜백"""
        import os
        import httpx
        import json

        base = os.getenv("SPRING_SERVER_BASE_URL", "").strip().rstrip("/")
        path = f"/api/textbook/thumbnail/{job_id}"
        if not base:
            logger.warning("SPRING_SERVER_BASE_URL 미설정: 썸네일 콜백 스킵")
            return False

        url = f"{base}{path}"
        headers = {"Content-Type": "application/json"}
        token = os.getenv("EXTERNAL_CALLBACK_TOKEN")
        if token:
            headers["X-Callback-Token"] = token

        # snake_case 필수 필드 + 필요 시 camelCase 보조 키 포함
        # Spring DTO는 LocalDateTime을 사용하므로 'Z' 없는 ISO-8601 형식을 사용
        ts_local_dt = datetime.utcnow().replace(tzinfo=None).isoformat(timespec="seconds")
        payload = {
            "job_id": job_id,
            "pdf_name": filename,
            "thumbnail_url": s3_url,
            "s3_key": s3_key,
            "width": size[0] if size else None,
            "height": size[1] if size else None,
            "timestamp": ts_local_dt,
            # camelCase 동시 제공(스프링 글로별 설정 호환 목적)
            "jobId": job_id,
            "pdfName": filename,
            "thumbnailUrl": s3_url,
        }

        timeout = float(os.getenv("SPRING_CALLBACK_TIMEOUT", "10"))

        # 전송 전 요약 로그 (사용자 요청)
        try:
            logger.info(
                "Spring 썸네일 콜백 전송 준비: "
                f"url={url}, job_id={job_id}, pdf_name={filename}, "
                f"thumbnail_url={s3_url}, s3_key={s3_key}, "
                f"width={(size[0] if size else None)}, height={(size[1] if size else None)}, "
                f"timestamp={payload['timestamp']}"
            )
            # 디버그 용으로 페이로드 일부 출력
            logger.debug(f"썸네일 콜백 payload={json.dumps(payload)[:500]}")
        except Exception:
            pass
        try:
            async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
                resp = await client.post(url, json=payload)
                if 200 <= resp.status_code < 300:
                    logger.info(
                        f"Spring 썸네일 콜백 성공: status={resp.status_code}, url={url}, jobId={job_id}"
                    )
                    try:
                        logger.debug(f"Spring 응답 본문: {resp.text[:300]}")
                    except Exception:
                        pass
                    return True
                logger.error(
                    f"Spring 썸네일 콜백 실패: status={resp.status_code}, body={resp.text[:300]}"
                )
                return False
        except Exception as e:
            logger.error(f"Spring 썸네일 콜백 예외: {e}")
            return False


# 전역 인스턴스
thumbnail_service = ThumbnailService()
