package com.dyslexia.dyslexia.entity;

import jakarta.persistence.*;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "textbook_thumbnails")
@Getter
@NoArgsConstructor
public class TextbookThumbnail {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "textbook_id", nullable = false, unique = true)
    private Textbook textbook;

    @Column(name = "job_id", nullable = false, unique = true)
    private String jobId;

    @Column(name = "pdf_name")
    private String pdfName;

    @Column(name = "thumbnail_url", nullable = false)
    private String thumbnailUrl;

    @Column(name = "s3_key")
    private String s3Key;

    @Column(name = "width")
    private Integer width;

    @Column(name = "height")
    private Integer height;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @Builder
    public TextbookThumbnail(Textbook textbook, String jobId, String pdfName, String thumbnailUrl,
                           String s3Key, Integer width, Integer height) {
        this.textbook = textbook;
        this.jobId = jobId;
        this.pdfName = pdfName;
        this.thumbnailUrl = thumbnailUrl;
        this.s3Key = s3Key;
        this.width = width;
        this.height = height;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    public void updateThumbnailInfo(String pdfName, String thumbnailUrl, String s3Key, Integer width, Integer height) {
        this.pdfName = pdfName;
        this.thumbnailUrl = thumbnailUrl;
        this.s3Key = s3Key;
        this.width = width;
        this.height = height;
        this.updatedAt = LocalDateTime.now();
    }
}