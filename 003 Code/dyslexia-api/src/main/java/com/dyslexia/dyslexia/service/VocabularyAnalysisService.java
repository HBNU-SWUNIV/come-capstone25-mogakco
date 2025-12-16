package com.dyslexia.dyslexia.service;

import com.dyslexia.dyslexia.domain.pdf.VocabularyAnalysis;
import com.dyslexia.dyslexia.domain.pdf.VocabularyAnalysisRepository;
import com.dyslexia.dyslexia.entity.Page;
import com.dyslexia.dyslexia.repository.PageRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class VocabularyAnalysisService {

    private final VocabularyAnalysisRepository vocabularyAnalysisRepository;
    private final PageRepository pageRepository;

    @Transactional(readOnly = true)
    public List<VocabularyAnalysis> searchVocabularyAnalysis(Long textbookId, Long documentId, Integer pageNumber, String blockId) {
        log.info("=== VocabularyAnalysisService 검색 실행 ===");
        log.info("검색 조건: textbookId={}, documentId={}, pageNumber={}, blockId={}", textbookId, documentId, pageNumber, blockId);

        List<VocabularyAnalysis> results = Collections.emptyList();

        // 새로운 방식: Page 기반 정확한 검색
        if (textbookId != null && pageNumber != null) {
            // Page 엔티티 조회
            Page page = pageRepository.findByTextbookIdAndPageNumber(textbookId, pageNumber)
                .orElse(null);

            if (page == null) {
                log.warn("Page를 찾을 수 없습니다: textbookId={}, pageNumber={}", textbookId, pageNumber);
                return Collections.emptyList();
            }

            // BlockId가 있는 경우 정확한 검색
            if (blockId != null && !blockId.isEmpty()) {
                results = vocabularyAnalysisRepository.findByPageIdAndBlockId(page.getId(), blockId);
                log.info("Page 기반 정확 검색 결과: pageId={}, blockId={} → {}개", page.getId(), blockId, results.size());
            } else {
                // BlockId가 없는 경우 페이지 전체 검색
                results = vocabularyAnalysisRepository.findByPageId(page.getId());
                log.info("Page 기반 페이지 전체 검색 결과: pageId={} → {}개", page.getId(), results.size());
            }
        }
        // 하위 호환성을 위한 기존 방식 (Page를 찾을 수 없는 경우만)
        else if (textbookId != null) {
            log.warn("Page 정보 없이 Textbook 기반 검색 실행 (하위 호환성): textbookId={}", textbookId);
            if (blockId != null && !blockId.isEmpty() && pageNumber != null) {
                results = vocabularyAnalysisRepository.findByTextbookIdAndPageNumberAndBlockId(textbookId, pageNumber, blockId);
            } else if (pageNumber != null) {
                results = vocabularyAnalysisRepository.findByTextbookIdAndPageNumber(textbookId, pageNumber);
            } else {
                results = vocabularyAnalysisRepository.findByTextbookId(textbookId);
            }
        } else if (documentId != null) {
            log.warn("Document 기반 검색 실행 (하위 호환성): documentId={}", documentId);
            if (blockId != null && !blockId.isEmpty() && pageNumber != null) {
                results = vocabularyAnalysisRepository.findByDocumentIdAndPageNumberAndBlockId(documentId, pageNumber, blockId);
            } else if (pageNumber != null) {
                results = vocabularyAnalysisRepository.findByDocumentIdAndPageNumber(documentId, pageNumber);
            } else {
                results = vocabularyAnalysisRepository.findByDocumentId(documentId);
            }
        }

        int count = results != null ? results.size() : 0;
        log.info("최종 검색 결과: {}개", count);

        // 디버깅 정보 로깅
        if (count > 0) {
            VocabularyAnalysis firstResult = results.get(0);
            log.debug("첫 번째 결과: word={}, blockId={}, pageId={}, textbookId={}",
                firstResult.getWord(),
                firstResult.getBlockId(),
                firstResult.getPage() != null ? firstResult.getPage().getId() : null,
                firstResult.getTextbookId());
        }

        return results != null ? results : Collections.emptyList();
    }

    /**
     * Page 기반 어휘 검색 (새로운 권장 방식)
     */
    @Transactional(readOnly = true)
    public List<VocabularyAnalysis> searchVocabularyAnalysisByPage(Long pageId, String blockId) {
        log.info("=== Page 기반 어휘 검색 ===");
        log.info("검색 조건: pageId={}, blockId={}", pageId, blockId);

        List<VocabularyAnalysis> results;
        if (blockId != null && !blockId.isEmpty()) {
            results = vocabularyAnalysisRepository.findByPageIdAndBlockId(pageId, blockId);
        } else {
            results = vocabularyAnalysisRepository.findByPageId(pageId);
        }

        log.info("Page 기반 검색 결과: {}개", results != null ? results.size() : 0);
        return results != null ? results : Collections.emptyList();
    }
}
