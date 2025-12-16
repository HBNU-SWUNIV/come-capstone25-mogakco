package com.dyslexia.dyslexia.domain.pdf;

import com.dyslexia.dyslexia.entity.Page;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "vocabulary_analysis",
        uniqueConstraints = @UniqueConstraint(columnNames = {"page_id", "block_id", "word", "start_index", "end_index"}))
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class VocabularyAnalysis {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "page_id", nullable = false)
    private Page page;

    private String blockId;

    private String word;
    private Integer startIndex;
    private Integer endIndex;

    private String definition;
    private String simplifiedDefinition;
    @Column(columnDefinition = "TEXT")
    private String examples;

    private String difficultyLevel;
    private String reason;
    private Integer gradeLevel;

    @Column(columnDefinition = "TEXT")
    @JsonProperty("phoneme_analysis_json")
    private String phonemeAnalysisJson;

    private Long textbookId;
    private Integer pageNumber;
    private LocalDateTime createdAt;

    // 편의 메서드: textbookId 조회 (하위 호환성)
    public Long getTextbookId() {
        return page != null && page.getTextbook() != null
            ? page.getTextbook().getId()
            : null;
    }

    // 편의 메서드: pageNumber 조회 (하위 호환성)
    public Integer getPageNumber() {
        return page != null ? page.getPageNumber() : null;
    }
} 