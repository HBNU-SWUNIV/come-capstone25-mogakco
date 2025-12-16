import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Union

from fastapi import UploadFile

from src.models import (
    OrchestrationOptions,
    ProcessingStep,
    StepResult,
    PreprocessingOptions,
    TransformationOptions,
    PhonemeAnalysisOptions,
)
from src.services import preprocessing_service, transformation_service
from src.services.phoneme_analysis_service import (
    extract_and_analyze_block_words_phoneme,
    extract_and_analyze_phonemes_from_chunk_blocks)
from src.services.progress_service import ProgressTracker

# 로거 설정
logger = logging.getLogger(__name__)

class ProcessingOrchestrator:
    """
    전체 처리 파이프라인을 오케스트레이트하는 클래스
    
    Attributes:
        total_processing_time: 총 처리 시간
        progress_tracker: 진행률 추적기
    """

    def __init__(self, task_id: Optional[str] = None, filename: Optional[str] = None):
        self.total_processing_time = 0.0
        self.progress_tracker = ProgressTracker(task_id, filename)

    def _log_step_start(self, step: ProcessingStep, additional_info: str = ""):
        """단계 시작 로그
        
        Args:
            step: 처리 단계
            additional_info: 추가 정보
        """
        step_names = {
            ProcessingStep.PREPROCESSING: "전처리",
            ProcessingStep.BLOCK_TRANSFORMATION: "블록 변환",
            ProcessingStep.PHONEME_ANALYSIS: "음운분석",
            ProcessingStep.BLOCK_WORD_PHONEME_ANALYSIS: "블록별 단어 음운분석",
            ProcessingStep.POST_PROCESSING: "후처리",
        }
        logger.info(f"{step_names[step]} 시작 {additional_info}")

    def _log_step_complete(self, step_result: StepResult):
        """단계 완료 로그
        
        Args:
            step_result: 단계 결과
        """
        # Pydantic 설정(use_enum_values=True) 때문에 Enum이 문자열로 변환될 수 있으므로 안전 처리
        step_name = getattr(step_result.step, "value", step_result.step)
        if step_result.success:
            logger.info(
                f"{step_name} 완료 ({step_result.processing_time:.2f}초)"
            )
        else:
            logger.error(f"{step_name} 실패: {step_result.error}")

    async def _execute_preprocessing(
        self, file: UploadFile, options: OrchestrationOptions
    ) -> StepResult:
        """전처리 단계 실행
        
        Args:
            file: 파일
            options: 옵션
        """
        start_time = time.time()

        try:
            self._log_step_start(ProcessingStep.PREPROCESSING, f"파일: {file.filename}")
            
            # 진행률 업데이트: PDF 추출 시작
            if options.job_id:
                update_job_progress(
                    job_id=options.job_id,
                    status=JobStatus.PREPROCESSING,
                    current_step=JobStep.PDF_EXTRACTION,
                    step_details={"message": f"PDF 텍스트 추출 시작: {file.filename}"}
                )

            # 단계 시작 - 진행률 추적
            self.progress_tracker.start_step("preprocessing")
            self.progress_tracker.update_progress("preprocessing", 10.0)  # 시작

            # 전처리 실행
            preprocessing_result = preprocessing_service.run_preprocessing_pipeline(
                file=file,
                options=options.preprocessing,
                return_text=True,
                return_chunks=True,
                model=options.model_name,
            )

            # 중간 진행률 업데이트
            self.progress_tracker.update_progress("preprocessing", 80.0)  # 처리 완료

            # 결과 검증
            if not preprocessing_result.get("chunks"):
                raise ValueError("전처리 결과에 청크 데이터가 없습니다")

            # 처리 시간 계산
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time

            # 단계 완료 - 진행률 추적
            self.progress_tracker.complete_step("preprocessing")

            # 결과 반환
            step_result = StepResult(
                step=ProcessingStep.PREPROCESSING,
                success=True,
                processing_time=processing_time,
                data=preprocessing_result,
            )

            self._log_step_complete(step_result)
            return step_result

        except Exception as e:
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time

            step_result = StepResult(
                step=ProcessingStep.PREPROCESSING,
                success=False,
                processing_time=processing_time,
                error=str(e),
            )

            self._log_step_complete(step_result)
            return step_result

    async def _execute_block_transformation(
        self, content: List[str], options: OrchestrationOptions
    ) -> StepResult:
        """블록 변환 단계 실행
        
        Args:
            content: 청크
            options: 옵션
        """
        start_time = time.time()

        try:
            self._log_step_start(
                ProcessingStep.BLOCK_TRANSFORMATION, f"청크 수: {len(content)}"
            )
            
            # 진행률 업데이트: 블록 변환 시작
            if options.job_id:
                update_job_progress(
                    job_id=options.job_id,
                    status=JobStatus.TRANSFORMING,
                    current_step=JobStep.BLOCK_TRANSFORMATION,
                    step_details={"message": f"블록 변환 시작: {len(content)}개 청크"}
                )

            # 단계 시작 - 진행률 추적
            self.progress_tracker.start_step("block_transformation")
            self.progress_tracker.update_progress("block_transformation", 5.0)  # 시작

            # 변환 실행
            transformation_result = (
                await transformation_service.transform_content_to_blocks(
                    content=content,
                    model_name=options.model_name,
                    max_concurrent=options.max_concurrent,
                    image_interval=options.transformation.image_interval,
                    word_limit=options.transformation.word_limit,
                    vocabulary_interval=options.transformation.vocabulary_interval,
                    save_to_redis=False,  # 오케스트레이션에서는 Redis 저장 안 함
                    expire_hours=24,
                )
            )

            # 중간 진행률 업데이트
            self.progress_tracker.update_progress(
                "block_transformation", 90.0
            )  # 처리 완료

            # 결과 검증
            if not transformation_result.get("chunk_blocks"):
                raise ValueError("변환 결과에 블록 데이터가 없습니다")

            # 진행률 업데이트: 블록 변환 완료
            if options.job_id:
                update_job_progress(
                    job_id=options.job_id,
                    status=JobStatus.TRANSFORMING,
                    current_step=JobStep.BLOCK_TRANSFORMATION,
                    step_details={"message": f"블록 변환 완료: {transformation_result.get('metadata', {}).get('total_blocks', 0)}개 블록 생성"}
                )

            # 처리 시간 계산
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time

            # 단계 완료 - 진행률 추적
            self.progress_tracker.complete_step("block_transformation")

            # 결과 반환
            step_result = StepResult(
                step=ProcessingStep.BLOCK_TRANSFORMATION,
                success=True,
                processing_time=processing_time,
                data=transformation_result,
            )

            self._log_step_complete(step_result)
            return step_result

        except Exception as e:
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time

            step_result = StepResult(
                step=ProcessingStep.BLOCK_TRANSFORMATION,
                success=False,
                processing_time=processing_time,
                error=str(e),
            )

            self._log_step_complete(step_result)
            return step_result

    async def _execute_phoneme_analysis(
        self, chunk_blocks: List[List[Dict[str, Any]]], options: OrchestrationOptions
    ) -> StepResult:
        """음운분석 단계 실행
        
        Args:
            chunk_blocks: 청크 블록
            options: 옵션
        """
        start_time = time.time()

        try:
            self._log_step_start(
                ProcessingStep.PHONEME_ANALYSIS, f"청크 블록 수: {len(chunk_blocks)}"
            )
            
            # 진행률 업데이트: 음운분석 시작
            if options.job_id:
                update_job_progress(
                    job_id=options.job_id,
                    status=JobStatus.ANALYZING_PHONEMES,
                    current_step=JobStep.PHONEME_ANALYSIS,
                    step_details={"message": f"음운분석 시작: {len(chunk_blocks)}개 청크 블록"}
                )

            # 단계 시작 - 진행률 추적
            self.progress_tracker.start_step("phoneme_analysis")
            self.progress_tracker.update_progress("phoneme_analysis", 10.0)  # 시작

            # 음운분석 실행
            phoneme_result = await extract_and_analyze_phonemes_from_chunk_blocks(
                chunk_blocks=chunk_blocks,
                model_name=options.model_name,
                max_concurrent=options.phoneme_analysis.phoneme_max_concurrent,
            )

            # 중간 진행률 업데이트
            self.progress_tracker.update_progress("phoneme_analysis", 85.0)  # 처리 완료

            # 처리 시간 계산
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time

            # 단계 완료 - 진행률 추적
            self.progress_tracker.complete_step("phoneme_analysis")

            # 결과 반환
            step_result = StepResult(
                step=ProcessingStep.PHONEME_ANALYSIS,
                success=True,
                processing_time=processing_time,
                data=phoneme_result,
            )

            self._log_step_complete(step_result)
            return step_result

        except Exception as e:
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time

            step_result = StepResult(
                step=ProcessingStep.PHONEME_ANALYSIS,
                success=False,
                processing_time=processing_time,
                error=str(e),
            )

            self._log_step_complete(step_result)
            return step_result

    async def _execute_block_word_phoneme_analysis(
        self, transformed_blocks: List[Dict[str, Any]], options: OrchestrationOptions
    ) -> StepResult:
        """블록별 단어 음운분석 단계 실행
        
        Args:
            transformed_blocks: 변환된 블록
            options: 옵션
        """
        start_time = time.time()

        try:
            self._log_step_start(
                ProcessingStep.BLOCK_WORD_PHONEME_ANALYSIS,
                f"변환된 블록 수: {len(transformed_blocks)}",
            )
            
            # 진행률 업데이트: 블록별 단어 음운분석 시작
            if options.job_id:
                update_job_progress(
                    job_id=options.job_id,
                    status=JobStatus.ANALYZING_PHONEMES,
                    current_step=JobStep.BLOCK_WORD_PHONEME_ANALYSIS,
                    step_details={"message": f"블록별 단어 음운분석 시작: {len(transformed_blocks)}개 블록"}
                )

            # 단계 시작 - 진행률 추적
            self.progress_tracker.start_step("block_word_phoneme_analysis")
            self.progress_tracker.update_progress(
                "block_word_phoneme_analysis", 10.0
            )  # 시작

            # 블록별 단어 음운분석 실행
            block_word_phoneme_result = await extract_and_analyze_block_words_phoneme(
                transformed_blocks=transformed_blocks,
                model_name=options.model_name,
                max_concurrent=options.phoneme_analysis.block_word_phoneme_max_concurrent,
            )

            # 중간 진행률 업데이트
            self.progress_tracker.update_progress(
                "block_word_phoneme_analysis", 85.0
            )  # 처리 완료

            # 처리 시간 계산
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time

            # 단계 완료 - 진행률 추적
            self.progress_tracker.complete_step("block_word_phoneme_analysis")

            # 결과 반환
            step_result = StepResult(
                step=ProcessingStep.BLOCK_WORD_PHONEME_ANALYSIS,
                success=True,
                processing_time=processing_time,
                data=block_word_phoneme_result,
            )

            self._log_step_complete(step_result)
            return step_result

        except Exception as e:
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time

            step_result = StepResult(
                step=ProcessingStep.BLOCK_WORD_PHONEME_ANALYSIS,
                success=False,
                processing_time=processing_time,
                error=str(e),
            )

            self._log_step_complete(step_result)
            return step_result

    async def _execute_post_processing(
        self,
        preprocessing_result: StepResult,
        transformation_result: StepResult,
        phoneme_result: Optional[StepResult] = None,
        block_word_phoneme_result: Optional[StepResult] = None,
        options: Optional[OrchestrationOptions] = None,
    ) -> StepResult:
        """후처리 단계 실행
        
        Args:
            preprocessing_result: 전처리 결과
            transformation_result: 변환 결과
            phoneme_result: 음운분석 결과
            block_word_phoneme_result: 블록별 단어 음운분석 결과
        """
        start_time = time.time()

        try:
            self._log_step_start(ProcessingStep.POST_PROCESSING)
            
            # 진행률 업데이트: 후처리 시작
            if options and options.job_id:
                update_job_progress(
                    job_id=options.job_id,
                    status=JobStatus.TRANSFORMING,
                    current_step=JobStep.FINAL_PROCESSING,
                    step_details={"message": "후처리 및 결과 통합 중"}
                )

            # 단계 시작 - 진행률 추적
            self.progress_tracker.start_step("post_processing")
            self.progress_tracker.update_progress("post_processing", 10.0)  # 시작

            # transformation 데이터에서 chunk_blocks 제거
            transformation_data = transformation_result.data.copy()
            transformation_data.pop("chunk_blocks", None)

            # 기본 결과 구성
            final_result = {
                "transformation": transformation_data,
                "filename": preprocessing_result.data.get("filename", "unknown"),
                "created_at": preprocessing_result.data.get("created_at"),
                "processing_time": self.total_processing_time,
                "metadata": {
                    "preprocessing_time": preprocessing_result.processing_time,
                    "transformation_time": transformation_result.processing_time,
                    "total_processing_time": self.total_processing_time,
                    "total_chunks": preprocessing_result.data.get("metadata", {}).get(
                        "total_chunks", 0
                    ),
                    "total_tokens": preprocessing_result.data.get("metadata", {}).get(
                        "total_tokens", 0
                    ),
                    "model_name": transformation_result.data.get("metadata", {}).get(
                        "model_name"
                    ),
                    "image_interval": transformation_result.data.get(
                        "metadata", {}
                    ).get("image_interval"),
                    "word_limit": transformation_result.data.get("metadata", {}).get(
                        "word_limit"
                    ),
                    "vocabulary_interval": transformation_result.data.get(
                        "metadata", {}
                    ).get("vocabulary_interval"),
                },
            }

            # 음운분석 결과 추가
            if phoneme_result and phoneme_result.success:
                final_result["phoneme_analysis"] = phoneme_result.data
                final_result["metadata"][
                    "phoneme_analysis_time"
                ] = phoneme_result.processing_time

                # 블록에 음운분석 결과 통합
                if "phoneme_analyses" in phoneme_result.data:
                    enhanced_blocks = self._merge_phoneme_analysis_to_blocks(
                        transformation_result.data.get("transformed_blocks", []),
                        phoneme_result.data["phoneme_analyses"],
                    )
                    final_result["transformation"][
                        "transformed_blocks"
                    ] = enhanced_blocks
                    logger.info(
                        f"음운분석 결과를 {len(enhanced_blocks)}개 블록에 통합 완료"
                    )

            # 블록별 단어 음운분석 결과 추가
            if block_word_phoneme_result and block_word_phoneme_result.success:
                final_result["block_word_phoneme_analysis"] = (
                    block_word_phoneme_result.data
                )
                final_result["metadata"][
                    "block_word_phoneme_analysis_time"
                ] = block_word_phoneme_result.processing_time

                # 블록에 블록별 단어 음운분석 결과 통합
                if "block_word_phoneme_analyses" in block_word_phoneme_result.data:
                    enhanced_blocks = self._merge_block_word_phoneme_analysis_to_blocks(
                        final_result["transformation"]["transformed_blocks"],
                        block_word_phoneme_result.data["block_word_phoneme_analyses"],
                    )
                    final_result["transformation"][
                        "transformed_blocks"
                    ] = enhanced_blocks

            # 중간 진행률 업데이트
            self.progress_tracker.update_progress(
                "post_processing", 50.0
            )  # 데이터 구성 완료

            # Redis에 완성된 결과 저장
            redis_result = self._save_final_result_to_redis(final_result)
            final_result["redis_info"] = redis_result

            # 중간 진행률 업데이트
            self.progress_tracker.update_progress(
                "post_processing", 90.0
            )  # Redis 저장 완료

            # 처리 시간 계산
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time

            # 단계 완료 - 진행률 추적
            self.progress_tracker.complete_step("post_processing")

            # 결과 반환
            step_result = StepResult(
                step=ProcessingStep.POST_PROCESSING,
                success=True,
                processing_time=processing_time,
                data=final_result,
            )

            self._log_step_complete(step_result)
            return step_result

        except Exception as e:
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time

            step_result = StepResult(
                step=ProcessingStep.POST_PROCESSING,
                success=False,
                processing_time=processing_time,
                error=str(e),
            )

            self._log_step_complete(step_result)
            return step_result

    def _merge_phoneme_analysis_to_blocks(
        self, blocks: List[Dict[str, Any]], phoneme_analyses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """음운분석 결과를 블록에 통합
        
        Args:
            blocks: 블록
            phoneme_analyses: 음운분석 결과
        """

        # 단어별 음운분석 결과 매핑
        phoneme_by_word = {}
        for analysis in phoneme_analyses:
            if analysis["success"] and analysis["phoneme_analysis"]:
                phoneme_by_word[analysis["word"]] = analysis["phoneme_analysis"]

        # 각 블록의 vocabularyAnalysis에 음운분석 결과 추가
        enhanced_blocks = []
        for block in blocks:
            enhanced_block = block.copy()

            if "vocabularyAnalysis" in block and block["vocabularyAnalysis"]:
                enhanced_vocab = []
                for vocab_item in block["vocabularyAnalysis"]:
                    enhanced_vocab_item = vocab_item.copy()

                    if "word" in vocab_item:
                        word = vocab_item["word"]
                        if word in phoneme_by_word:
                            enhanced_vocab_item["phonemeAnalysis"] = phoneme_by_word[
                                word
                            ]

                    enhanced_vocab.append(enhanced_vocab_item)

                enhanced_block["vocabularyAnalysis"] = enhanced_vocab

            enhanced_blocks.append(enhanced_block)

        return enhanced_blocks

    def _merge_block_word_phoneme_analysis_to_blocks(
        self,
        blocks: List[Dict[str, Any]],
        block_word_phoneme_analyses: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """블록별 단어 음운분석 결과를 블록에 통합"""

        # 블록별 음운분석 결과 매핑
        phoneme_by_block = {}
        for analysis in block_word_phoneme_analyses:
            if analysis["success"] and analysis["phoneme_analysis"]:
                block_id = analysis.get("block_id", "unknown")
                word = analysis["word"]

                if block_id not in phoneme_by_block:
                    phoneme_by_block[block_id] = {}

                phoneme_by_block[block_id][word] = analysis["phoneme_analysis"]

        # 각 블록의 vocabularyAnalysis에 블록별 단어 음운분석 결과 추가
        enhanced_blocks = []
        for block_index, block in enumerate(blocks):
            enhanced_block = block.copy()
            block_id = block.get("id", f"block_{block_index}")

            if block_id in phoneme_by_block:
                logger.info(
                    f"블록 {block_id}에 {len(phoneme_by_block[block_id])}개 단어 음운분석 추가"
                )

                if "vocabularyAnalysis" in block and block["vocabularyAnalysis"]:
                    enhanced_vocab = []
                    for vocab_item in block["vocabularyAnalysis"]:
                        enhanced_vocab_item = vocab_item.copy()

                        if "word" in vocab_item:
                            word = vocab_item["word"]
                            if word in phoneme_by_block[block_id]:
                                enhanced_vocab_item["blockWordPhonemeAnalysis"] = (
                                    phoneme_by_block[block_id][word]
                                )

                        enhanced_vocab.append(enhanced_vocab_item)

                    enhanced_block["vocabularyAnalysis"] = enhanced_vocab

            enhanced_blocks.append(enhanced_block)

        return enhanced_blocks

    def _save_final_result_to_redis(
        self, final_result: Dict[str, Any], expire_hours: int = 24
    ) -> Dict[str, Any]:
        """완성된 결과를 Redis에 저장"""
        try:
            from src.services.redis_service import RedisService

            redis_service = RedisService()

            # task_id와 filename을 키로 저장
            success = redis_service.save_output_by_task_id(
                self.progress_tracker.task_id,
                self.progress_tracker.filename,
                final_result,
                expire_hours=expire_hours,
            )

            if success:
                logger.info(
                    f"완성된 데이터 Redis 저장 성공: {self.progress_tracker.filename}:{self.progress_tracker.task_id}"
                )
                return {
                    "saved": True,
                    "task_id": self.progress_tracker.task_id,
                    "filename": self.progress_tracker.filename,
                    "expire_hours": expire_hours,
                }
            else:
                logger.error("완성된 데이터 Redis 저장 실패")
                return {"saved": False, "error": "Redis 저장 실패"}
        except Exception as e:
            logger.error(f"Redis 저장 중 오류 발생: {e}")
            return {"saved": False, "error": str(e)}

    def _log_orchestration_summary(self, final_result: StepResult):
        """오케스트레이션 요약 로그"""
        if final_result.success:
            logger.info(f"파이프라인 완료 ({self.total_processing_time:.2f}초)")

            results = final_result.data
            logger.info(f"파일: {final_result.data['filename']}")
            logger.info(f"청크: {results['metadata']['total_chunks']}개")
            logger.info(
                f"블록: {results['transformation']['metadata']['total_blocks']}개"
            )

            # 음운분석 결과 로그
            if "phoneme_analysis" in results:
                phoneme_meta = results["phoneme_analysis"]["metadata"]
                logger.info(f"음운분석: {phoneme_meta['unique_words']}개 단어")

            # 블록별 단어 음운분석 결과 로그
            if "block_word_phoneme_analysis" in results:
                block_word_phoneme_meta = results["block_word_phoneme_analysis"][
                    "metadata"
                ]
                logger.info(
                    f"블록별 단어 음운분석: {block_word_phoneme_meta['total_words']}개 단어 (고유: {block_word_phoneme_meta['unique_words']}개)"
                )
        else:
            logger.error(f"파이프라인 실패: {final_result.error}")

    async def execute_complete_pipeline(
        self,
        file: UploadFile,
        options: OrchestrationOptions,
    ) -> Dict[str, Any]:
        """전체 파이프라인 실행"""

        self.total_processing_time = 0.0
        logger.info(f"파이프라인 시작: {file.filename} (job_id: {options.job_id})")

        try:
            # 1. 전처리
            logger.info(f"전처리 단계 시작: {file.filename}")
            preprocessing_result = await self._execute_preprocessing(file, options)
            if not preprocessing_result.success:
                raise Exception(f"전처리 실패: {preprocessing_result.error}")
            logger.info(f"전처리 단계 완료: {len(preprocessing_result.data.get('chunks', []))}개 청크")

            # 2. 블록 변환
            logger.info(f"블록 변환 단계 시작: {len(preprocessing_result.data['chunks'])}개 청크")
            transformation_result = await self._execute_block_transformation(
                preprocessing_result.data["chunks"], options
            )
            if not transformation_result.success:
                raise Exception(f"블록 변환 실패: {transformation_result.error}")
            logger.info(f"블록 변환 단계 완료: {transformation_result.data.get('metadata', {}).get('total_blocks', 0)}개 블록")

            # 3. 음운분석
            phoneme_result = None
            if options.phoneme_analysis.enable_phoneme_analysis:
                phoneme_result = await self._execute_phoneme_analysis(
                    transformation_result.data["chunk_blocks"], options
                )
                if not phoneme_result.success:
                    logger.warning(f"음운분석 실패: {phoneme_result.error}")
            else:
                logger.info("음운분석 스킵")

            # 4. 블록별 단어 음운분석
            block_word_phoneme_result = None
            if options.phoneme_analysis.enable_block_word_phoneme_analysis:
                block_word_phoneme_result = (
                    await self._execute_block_word_phoneme_analysis(
                        transformation_result.data["transformed_blocks"], options
                    )
                )
                if not block_word_phoneme_result.success:
                    logger.warning(
                        f"블록별 단어 음운분석 실패: {block_word_phoneme_result.error}"
                    )
            else:
                logger.info("블록별 단어 음운분석 스킵")

            # 5. 후처리
            final_result = await self._execute_post_processing(
                preprocessing_result,
                transformation_result,
                phoneme_result,
                block_word_phoneme_result,
                options,
            )
            if not final_result.success:
                raise Exception(f"후처리 실패: {final_result.error}")

            # 요약 로그
            self._log_orchestration_summary(final_result)

            # 진행률 추적 완료
            final_progress = self.progress_tracker.finish()

            return {
                "success": True,
                "data": final_result.data,
                "metadata": {
                    "total_processing_time": self.total_processing_time,
                    "preprocessing_time": preprocessing_result.processing_time,
                    "transformation_time": transformation_result.processing_time,
                    "phoneme_analysis_time": (
                        phoneme_result.processing_time if phoneme_result else 0
                    ),
                    "block_word_phoneme_analysis_time": (
                        block_word_phoneme_result.processing_time
                        if block_word_phoneme_result
                        else 0
                    ),
                    "post_processing_time": final_result.processing_time,
                    "options": options.dict(),
                },
                "progress": final_progress,
            }

        except Exception as e:
            logger.error(
                f"파이프라인 실패: {str(e)} ({self.total_processing_time:.2f}초)"
            )

            # 실패 시에도 진행률 정보 포함
            current_progress = self.progress_tracker.get_progress()

            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "total_processing_time": self.total_processing_time,
                    "options": options.dict(),
                },
                "progress": current_progress,
            }

    async def execute_transformation_only(
        self,
        content: List[str],
        options: OrchestrationOptions,
    ) -> Dict[str, Any]:
        """변환만 실행하는 파이프라인
        
        Args:
            content: 청크
            options: 옵션
        """

        self.total_processing_time = 0.0
        logger.info(f"변환 시작: {len(content)}개 청크")

        try:
            # 1. 블록 변환
            transformation_result = await self._execute_block_transformation(
                content, options
            )
            if not transformation_result.success:
                raise Exception(f"블록 변환 실패: {transformation_result.error}")

            # 2. 음운분석 (옵션)
            phoneme_result = None
            if options.phoneme_analysis.enable_phoneme_analysis:
                phoneme_result = await self._execute_phoneme_analysis(
                    transformation_result.data["chunk_blocks"], options
                )
                if not phoneme_result.success:
                    logger.warning(f"음운분석 실패: {phoneme_result.error}")
            else:
                logger.info("음운분석 스킵")

            # 3. 블록별 단어 음운분석 (옵션)
            block_word_phoneme_result = None
            if options.phoneme_analysis.enable_block_word_phoneme_analysis:
                block_word_phoneme_result = (
                    await self._execute_block_word_phoneme_analysis(
                        transformation_result.data["transformed_blocks"], options
                    )
                )
                if not block_word_phoneme_result.success:
                    logger.warning(
                        f"블록별 단어 음운분석 실패: {block_word_phoneme_result.error}"
                    )
            else:
                logger.info("블록별 단어 음운분석 스킵")

            # 4. 결과 구성
            # transformation 데이터에서 chunk_blocks 제거
            transformation_data = transformation_result.data.copy()
            transformation_data.pop("chunk_blocks", None)

            final_result = {
                "transformation": transformation_data,
                "processing_time": self.total_processing_time,
                "metadata": {
                    "transformation_time": transformation_result.processing_time,
                    "total_processing_time": self.total_processing_time,
                    "model_name": transformation_result.data.get("metadata", {}).get(
                        "model_name"
                    ),
                    "image_interval": transformation_result.data.get(
                        "metadata", {}
                    ).get("image_interval"),
                    "word_limit": transformation_result.data.get("metadata", {}).get(
                        "word_limit"
                    ),
                    "vocabulary_interval": transformation_result.data.get(
                        "metadata", {}
                    ).get("vocabulary_interval"),
                },
            }

            # 음운분석 결과 추가
            if phoneme_result and phoneme_result.success:
                final_result["phoneme_analysis"] = phoneme_result.data
                final_result["metadata"][
                    "phoneme_analysis_time"
                ] = phoneme_result.processing_time

            # 블록별 단어 음운분석 결과 추가
            if block_word_phoneme_result and block_word_phoneme_result.success:
                final_result["block_word_phoneme_analysis"] = (
                    block_word_phoneme_result.data
                )
                final_result["metadata"][
                    "block_word_phoneme_analysis_time"
                ] = block_word_phoneme_result.processing_time

            logger.info(f"변환 완료 ({self.total_processing_time:.2f}초)")

            # 진행률 추적 완료
            final_progress = self.progress_tracker.finish()

            return {
                "success": True,
                "data": final_result,
                "metadata": {
                    "total_processing_time": self.total_processing_time,
                    "transformation_time": transformation_result.processing_time,
                    "phoneme_analysis_time": (
                        phoneme_result.processing_time if phoneme_result else 0
                    ),
                    "block_word_phoneme_analysis_time": (
                        block_word_phoneme_result.processing_time
                        if block_word_phoneme_result
                        else 0
                    ),
                    "options": options.dict(),
                },
                "progress": final_progress,
            }

        except Exception as e:
            logger.error(f"변환 실패: {str(e)} ({self.total_processing_time:.2f}초)")

            # 실패 시에도 진행률 정보 포함
            current_progress = self.progress_tracker.get_progress()

            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "total_processing_time": self.total_processing_time,
                    "options": options.dict(),
                },
                "progress": current_progress,
            }


# 편의 함수들
async def execute_complete_pipeline(
    file: UploadFile,
    model_name: str = "claude-sonnet-4-20250514",
    max_concurrent: int = 8,
    temp_dir: str = "./temp",
    remove_headers_footers: bool = True,
    header_height: float = 30.0,
    footer_height: float = 30.0,
    max_tokens: int = 12000,
    image_interval: int = 15,
    word_limit: int = 15,
    vocabulary_interval: int = 5,
    enable_phoneme_analysis: bool = True,
    phoneme_max_concurrent: int = 3,
    enable_block_word_phoneme_analysis: bool = True,
    block_word_phoneme_max_concurrent: int = 3,
    task_id: Optional[str] = None,
) -> Dict[str, Any]:
    """전체 파이프라인 실행을 위한 편의 함수
    
    Args:
        file: 파일
        model_name: 모델 이름
        max_concurrent: 최대 동시 실행 수
        temp_dir: 임시 디렉토리 경로
        remove_headers_footers: 머리말/꼬리말 제거 여부
        header_height: 머리말 높이 (pt)
        footer_height: 꼬리말 높이 (pt)
        max_tokens: 최대 토큰 수
        image_interval: 이미지 간격
        word_limit: 단어 제한
        vocabulary_interval: 어휘 간격
        enable_phoneme_analysis: 음운분석 활성화 여부
        phoneme_max_concurrent: 음운분석 최대 동시 실행 수
        enable_block_word_phoneme_analysis: 블록별 단어 음운분석 활성화 여부
        block_word_phoneme_max_concurrent: 블록별 단어 음운분석 최대 동시 실행 수
        task_id: 작업 ID
    """

    options = OrchestrationOptions(
        model_name=model_name,
        max_concurrent=max_concurrent,
        temp_dir=temp_dir,
        remove_headers_footers=remove_headers_footers,
        header_height=header_height,
        footer_height=footer_height,
        max_tokens=max_tokens,
        image_interval=image_interval,
        word_limit=word_limit,
        vocabulary_interval=vocabulary_interval,
        enable_phoneme_analysis=enable_phoneme_analysis,
        phoneme_max_concurrent=phoneme_max_concurrent,
        enable_block_word_phoneme_analysis=enable_block_word_phoneme_analysis,
        block_word_phoneme_max_concurrent=block_word_phoneme_max_concurrent,
    )

    orchestrator = ProcessingOrchestrator(task_id, file.filename)
    return await orchestrator.execute_complete_pipeline(file, options)


async def execute_transformation_only(
    content: List[str],
    model_name: str = "claude-sonnet-4-20250514",
    max_concurrent: int = 8,
    image_interval: int = 15,
    word_limit: int = 15,
    vocabulary_interval: int = 5,
    enable_phoneme_analysis: bool = True,
    phoneme_max_concurrent: int = 3,
    enable_block_word_phoneme_analysis: bool = True,
    block_word_phoneme_max_concurrent: int = 3,
    task_id: Optional[str] = None,
) -> Dict[str, Any]:
    """변환만 실행하기 위한 편의 함수
    
    Args:
        content: 청크
        model_name: 모델 이름
        max_concurrent: 최대 동시 실행 수
        image_interval: 이미지 간격
        word_limit: 단어 제한
        vocabulary_interval: 어휘 간격
        enable_phoneme_analysis: 음운분석 활성화 여부
        phoneme_max_concurrent: 음운분석 최대 동시 실행 수
        enable_block_word_phoneme_analysis: 블록별 단어 음운분석 활성화 여부
        block_word_phoneme_max_concurrent: 블록별 단어 음운분석 최대 동시 실행 수
        task_id: 작업 ID
    """

    options = OrchestrationOptions(
        model_name=model_name,
        max_concurrent=max_concurrent,
        image_interval=image_interval,
        word_limit=word_limit,
        vocabulary_interval=vocabulary_interval,
        enable_phoneme_analysis=enable_phoneme_analysis,
        phoneme_max_concurrent=phoneme_max_concurrent,
        enable_block_word_phoneme_analysis=enable_block_word_phoneme_analysis,
        block_word_phoneme_max_concurrent=block_word_phoneme_max_concurrent,
    )

    orchestrator = ProcessingOrchestrator(task_id, "text_content")
    return await orchestrator.execute_transformation_only(content, options)
