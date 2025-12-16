package com.dyslexia.dyslexia.dto;

import com.dyslexia.dyslexia.entity.TextbookThumbnail;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Getter
@NoArgsConstructor
@Schema(description = "교재 썸네일 응답 DTO")
public class TextbookThumbnailResponseDto {

    @Schema(description = "썸네일 ID", example = "1")
    private Long id;

    @Schema(description = "교재 ID", example = "1")
    private Long textbookId;

    @Schema(description = "작업 ID", example = "thumbnail-job-12345")
    private String jobId;

    @Schema(description = "원본 PDF 파일명", example = "textbook.pdf")
    private String pdfName;

    @Schema(description = "썸네일 URL", example = "https://s3.amazonaws.com/bucket/thumbnail.png")
    private String thumbnailUrl;

    @Schema(description = "S3 키", example = "thumbnails/textbook-123/thumbnail.png")
    private String s3Key;

    @Schema(description = "썸네일 너비", example = "200")
    private Integer width;

    @Schema(description = "썸네일 높이", example = "300")
    private Integer height;

    @Schema(description = "생성 시간")
    private LocalDateTime createdAt;

    @Schema(description = "수정 시간")
    private LocalDateTime updatedAt;

    public TextbookThumbnailResponseDto(TextbookThumbnail thumbnail) {
        this.id = thumbnail.getId();
        this.textbookId = thumbnail.getTextbook().getId();
        this.jobId = thumbnail.getJobId();
        this.pdfName = thumbnail.getPdfName();
        this.thumbnailUrl = thumbnail.getThumbnailUrl();
        this.s3Key = thumbnail.getS3Key();
        this.width = thumbnail.getWidth();
        this.height = thumbnail.getHeight();
        this.createdAt = thumbnail.getCreatedAt();
        this.updatedAt = thumbnail.getUpdatedAt();
    }

    public static TextbookThumbnailResponseDto from(TextbookThumbnail thumbnail) {
        return new TextbookThumbnailResponseDto(thumbnail);
    }
}