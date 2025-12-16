-- VocabularyAnalysis 데이터 모델링 개선 마이그레이션
-- 기존 textbookId, pageNumber 필드를 page_id 외래 키로 변경

-- 1. 새로운 page_id 컬럼 추가
ALTER TABLE vocabulary_analysis
ADD COLUMN page_id BIGINT;

-- 2. page_id 컬럼에 외래 키 제약 조건 추가
ALTER TABLE vocabulary_analysis
ADD CONSTRAINT fk_vocabulary_analysis_page
FOREIGN KEY (page_id) REFERENCES pages(id);

-- 3. 기존 데이터 마이그레이션
UPDATE vocabulary_analysis va
SET page_id = p.id
FROM pages p
WHERE p.textbook_id = va.textbook_id
  AND p.page_number = va.page_number;

-- 4. page_id가 null인 데이터 확인 (데이터 정합성 확인)
SELECT COUNT(*) as orphaned_records
FROM vocabulary_analysis
WHERE page_id IS NULL;

-- 5. page_id NOT NULL 제약 조건 추가 (데이터 정합성 보장 후 실행)
-- 주석: 아래 구문은 데이터 정합성 확인 후 실행 필요
-- ALTER TABLE vocabulary_analysis
-- ALTER COLUMN page_id SET NOT NULL;

-- 6. 기존 컬럼들 제거 (하위 호환성을 위해 임시 보관)
-- 주석: 기존 코드와의 호환성을 위해 일단 보관
-- ALTER TABLE vocabulary_analysis
-- DROP COLUMN textbook_id,
-- DROP COLUMN pageNumber;

-- 7. 고유 제약 조건 업데이트
ALTER TABLE vocabulary_analysis
DROP CONSTRAINT IF EXISTS uk_vocabulary_analysis;

ALTER TABLE vocabulary_analysis
ADD CONSTRAINT uk_vocabulary_analysis_page_block_word
UNIQUE (page_id, block_id, word, start_index, end_index);

-- 8. 인덱스 생성
CREATE INDEX idx_vocabulary_analysis_page_id ON vocabulary_analysis(page_id);
CREATE INDEX idx_vocabulary_analysis_word ON vocabulary_analysis(word);
CREATE INDEX idx_vocabulary_analysis_block_id ON vocabulary_analysis(block_id);

-- 마이그레이션 결과 확인
SELECT
    COUNT(*) as total_records,
    COUNT(CASE WHEN page_id IS NOT NULL THEN 1 END) as migrated_records,
    COUNT(CASE WHEN page_id IS NULL THEN 1 END) as orphaned_records
FROM vocabulary_analysis;

-- Textbook-Page-VocabularyAnalysis 관계 확인
SELECT
    t.id as textbook_id,
    t.title as textbook_title,
    COUNT(DISTINCT p.id) as page_count,
    COUNT(DISTINCT va.id) as vocabulary_count
FROM textbooks t
LEFT JOIN pages p ON t.id = p.textbook_id
LEFT JOIN vocabulary_analysis va ON p.id = va.page_id
GROUP BY t.id, t.title
ORDER BY t.id;