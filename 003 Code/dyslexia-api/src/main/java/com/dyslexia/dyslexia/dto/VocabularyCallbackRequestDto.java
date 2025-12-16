package com.dyslexia.dyslexia.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@Schema(description = "어휘 분석 완료 콜백 요청 DTO")
public class VocabularyCallbackRequestDto {

    @NotNull(message = "payload_version is required")
    @JsonProperty("payload_version")
    @Schema(description = "페이로드 버전", example = "1")
    private Integer payloadVersion;

    @NotBlank(message = "result_type is required")
    @JsonProperty("result_type")
    @Schema(description = "결과 타입", example = "VOCABULARY")
    private String resultType;

    @NotBlank(message = "job_id is required")
    @JsonProperty("job_id")
    @Schema(description = "작업 ID", example = "job-123")
    private String jobId;

    @JsonProperty("jobId")
    @Schema(description = "작업 ID (대체 필드)", example = "job-123")
    private String jobIdAlt;

    @NotNull(message = "textbook_id is required")
    @JsonProperty("textbook_id")
    @Schema(description = "교재 ID", example = "7")
    private Long textbookId;

    @JsonProperty("textbookId")
    @Schema(description = "교재 ID (대체 필드)", example = "7")
    private Long textbookIdAlt;

    @JsonProperty("pdf_name")
    @Schema(description = "PDF 파일명", example = "vocabulary.json")
    private String pdfName;

    @JsonProperty("pdfName")
    @Schema(description = "PDF 파일명 (대체 필드)", example = "vocabulary.json")
    private String pdfNameAlt;

    @JsonProperty("s3_summary_url")
    @Schema(description = "S3 요약 URL", example = "https://s3.ap-northeast-2.amazonaws.com/bucket/jobs/job-123/vocabulary.json")
    private String s3SummaryUrl;

    @JsonProperty("s3SummaryUrl")
    @Schema(description = "S3 요약 URL (대체 필드)")
    private String s3SummaryUrlAlt;

    @JsonProperty("s3_blocks_prefix")
    @Schema(description = "S3 블록 프리픽스")
    private String s3BlocksPrefix;

    @JsonProperty("s3BlocksPrefix")
    @Schema(description = "S3 블록 프리픽스 (대체 필드)")
    private String s3BlocksPrefixAlt;

    @Schema(description = "통계 정보")
    private StatsDto stats;

    @JsonProperty("created_at")
    @Schema(description = "생성 시간")
    private LocalDateTime createdAt;

    @JsonProperty("createdAt")
    @Schema(description = "생성 시간 (대체 필드)")
    private LocalDateTime createdAtAlt;

    @Getter
    @Setter
    @NoArgsConstructor
    @Schema(description = "통계 정보")
    public static class StatsDto {

        @Schema(description = "총 블록 수", example = "42")
        private Integer blocks;

        @Schema(description = "총 아이템 수", example = "87")
        private Integer items;

        @JsonProperty("by_difficulty")
        @Schema(description = "난이도별 통계")
        private DifficultyStatsDto byDifficulty;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @Schema(description = "난이도별 통계")
    public static class DifficultyStatsDto {

        @Schema(description = "쉬운 난이도 개수", example = "15")
        private Integer easy;

        @Schema(description = "중간 난이도 개수", example = "56")
        private Integer medium;

        @Schema(description = "어려운 난이도 개수", example = "16")
        private Integer hard;
    }

    // 대체 필드 값을 메인 필드로 설정하는 헬퍼 메서드들
    public String getEffectiveJobId() {
        return jobId != null ? jobId : jobIdAlt;
    }

    public Long getEffectiveTextbookId() {
        return textbookId != null ? textbookId : textbookIdAlt;
    }

    public String getEffectivePdfName() {
        return pdfName != null ? pdfName : pdfNameAlt;
    }

    public String getEffectiveS3SummaryUrl() {
        return s3SummaryUrl != null ? s3SummaryUrl : s3SummaryUrlAlt;
    }

    public String getEffectiveS3BlocksPrefix() {
        return s3BlocksPrefix != null ? s3BlocksPrefix : s3BlocksPrefixAlt;
    }

    public LocalDateTime getEffectiveCreatedAt() {
        return createdAt != null ? createdAt : createdAtAlt;
    }
}