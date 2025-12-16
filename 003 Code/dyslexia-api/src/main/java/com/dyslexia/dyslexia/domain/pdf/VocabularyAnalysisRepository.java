package com.dyslexia.dyslexia.domain.pdf;

import com.dyslexia.dyslexia.entity.Page;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface VocabularyAnalysisRepository extends JpaRepository<VocabularyAnalysis, Long> {

    // Page 기반 조회 (새로운 기본 방식)
    List<VocabularyAnalysis> findByPage(Page page);
    List<VocabularyAnalysis> findByPageId(Long pageId);
    List<VocabularyAnalysis> findByPageIdAndBlockId(Long pageId, String blockId);

    Optional<VocabularyAnalysis> findByPageIdAndBlockIdAndWordAndStartIndexAndEndIndex(
        Long pageId,
        String blockId,
        String word,
        Integer startIndex,
        Integer endIndex
    );

    // Textbook 기반 조회 (하위 호환성 유지)
    @Query("SELECT va FROM VocabularyAnalysis va WHERE va.page.textbook.id = :textbookId")
    List<VocabularyAnalysis> findByTextbookId(@Param("textbookId") Long textbookId);

    @Query("SELECT va FROM VocabularyAnalysis va WHERE va.page.textbook.id = :textbookId AND va.page.pageNumber = :pageNumber")
    List<VocabularyAnalysis> findByTextbookIdAndPageNumber(@Param("textbookId") Long textbookId, @Param("pageNumber") Integer pageNumber);

    @Query("SELECT va FROM VocabularyAnalysis va WHERE va.page.textbook.id = :textbookId AND va.page.pageNumber = :pageNumber AND va.blockId = :blockId")
    List<VocabularyAnalysis> findByTextbookIdAndPageNumberAndBlockId(@Param("textbookId") Long textbookId, @Param("pageNumber") Integer pageNumber, @Param("blockId") String blockId);

    @Query("SELECT va FROM VocabularyAnalysis va WHERE va.page.textbook.id = :textbookId AND va.blockId = :blockId AND va.word = :word AND va.startIndex = :startIndex AND va.endIndex = :endIndex")
    Optional<VocabularyAnalysis> findByTextbookIdAndBlockIdAndWordAndStartIndexAndEndIndex(
        @Param("textbookId") Long textbookId,
        @Param("blockId") String blockId,
        @Param("word") String word,
        @Param("startIndex") Integer startIndex,
        @Param("endIndex") Integer endIndex
    );

    // Document 기반 조회 (교재 ID를 모를 때)
    @Query(value = "SELECT va.* FROM vocabulary_analysis va " +
                   "JOIN pages p ON va.page_id = p.id " +
                   "JOIN textbooks t ON p.textbook_id = t.id " +
                   "WHERE t.document_id = :documentId", nativeQuery = true)
    List<VocabularyAnalysis> findByDocumentId(@Param("documentId") Long documentId);

    @Query(value = "SELECT va.* FROM vocabulary_analysis va " +
                   "JOIN pages p ON va.page_id = p.id " +
                   "JOIN textbooks t ON p.textbook_id = t.id " +
                   "WHERE t.document_id = :documentId AND p.page_number = :pageNumber", nativeQuery = true)
    List<VocabularyAnalysis> findByDocumentIdAndPageNumber(@Param("documentId") Long documentId, @Param("pageNumber") Integer pageNumber);

    @Query(value = "SELECT va.* FROM vocabulary_analysis va " +
                   "JOIN pages p ON va.page_id = p.id " +
                   "JOIN textbooks t ON p.textbook_id = t.id " +
                   "WHERE t.document_id = :documentId AND p.page_number = :pageNumber AND va.block_id = :blockId", nativeQuery = true)
    List<VocabularyAnalysis> findByDocumentIdAndPageNumberAndBlockId(@Param("documentId") Long documentId, @Param("pageNumber") Integer pageNumber, @Param("blockId") String blockId);

    // 특정 단어로 검색
    List<VocabularyAnalysis> findByWord(String word);

    // 특정 난이도 레벨로 검색
    List<VocabularyAnalysis> findByDifficultyLevel(String difficultyLevel);
} 
