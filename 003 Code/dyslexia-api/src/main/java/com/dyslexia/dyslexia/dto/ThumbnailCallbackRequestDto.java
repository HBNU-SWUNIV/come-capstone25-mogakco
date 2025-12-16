package com.dyslexia.dyslexia.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@Schema(description = "썸네일 생성 완료 콜백 요청 DTO")
public class ThumbnailCallbackRequestDto {

    @NotBlank(message = "job_id is required")
    @JsonProperty("job_id")
    @Schema(description = "작업 ID", example = "thumbnail-job-12345")
    private String jobId;

    @JsonProperty("pdf_name")
    @Schema(description = "원본 PDF 파일명", example = "textbook.pdf")
    private String pdfName;

    @NotBlank(message = "thumbnail_url is required")
    @JsonProperty("thumbnail_url")
    @Schema(description = "생성된 썸네일 URL", example = "https://s3.amazonaws.com/bucket/thumbnail.png")
    private String thumbnailUrl;

    @JsonProperty("s3_key")
    @Schema(description = "S3 키", example = "thumbnails/textbook-123/thumbnail.png")
    private String s3Key;

    @Positive(message = "width must be positive")
    @Schema(description = "썸네일 너비", example = "200")
    private Integer width;

    @Positive(message = "height must be positive")
    @Schema(description = "썸네일 높이", example = "300")
    private Integer height;

    @NotNull(message = "timestamp is required")
    @Schema(description = "생성 완료 시간")
    private LocalDateTime timestamp;
}