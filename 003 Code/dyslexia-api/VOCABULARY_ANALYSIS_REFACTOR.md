# 어휘 분석 데이터 모델링 개선 안내

## 개요

다른 문서의 어휘가 잘못 조회되는 문제를 해결하기 위해 VocabularyAnalysis 데이터 모델링을 개선했습니다. 핵심 변경은 Textbook/Page 간접 관계에서 Page 직접 관계로 전환하는 것입니다.

## 주요 변경 사항

### 1. VocabularyAnalysis 엔티티 개선
- **변경 전**: `textbookId`, `pageNumber` 필드 사용
- **변경 후**: `page` 엔티티와 직접적인 `@ManyToOne` 관계 설정
- **이점**: 데이터 무결성 보장, 정확한 문서별 어휘 격리

### 2. Repository 로직 개선
- **새로운 메서드**: `findByPageId()`, `findByPageIdAndBlockId()`
- **하위 호환성**: 기존 메서드 유지 (JPQL 쿼리로 변환)
- **성능 향상**: Join 쿼리 최적화

### 3. Service 로직 개선
- **Fallback 로직 제거**: 부정확한 검색 결과 방지
- **Page 기반 검색**: 정확한 페이지-어휘 매핑
- **상세 로깅**: 디버깅 및 문제 추적 용이

## 배포 절차

### 1단계: 데이터베이스 마이그레이션
```bash
# 마이그레이션 스크립트 실행
psql -d your_database -f src/main/resources/db/migration/V1__Update_VocabularyAnalysis_Schema.sql
```

### 2단계: 애플리케이션 재배포
```bash
# 빌드 및 배포
./gradlew build
# 기존 프로세스 중지 후 새 버전 실행
```

### 3단계: 데이터 정합성 확인
```sql
-- 마이그레이션 결과 확인
SELECT COUNT(*) as total_records,
       COUNT(CASE WHEN page_id IS NOT NULL THEN 1 END) as migrated_records
FROM vocabulary_analysis;
```

## 주의사항

### 하위 호환성
- 기존 API는 그대로 동작합니다 (편의 메서드 제공)
- 기존 필드(`textbookId`, `pageNumber`)는 계속 사용 가능
- 새로운 API는 `pageId` 기반으로 권장됩니다

### 성능 영향
- Page 기반 검색이 더 빠릅니다
- Join 쿼리가 최적화되었습니다
- 인덱스가 추가되어 검색 성능 향상

### 롤백 계획
문제 발생 시 아래 SQL로 롤백 가능:
```sql
-- 기존 구조로 복원
ALTER TABLE vocabulary_analysis DROP CONSTRAINT fk_vocabulary_analysis_page;
ALTER TABLE vocabulary_analysis ADD COLUMN textbook_id BIGINT;
ALTER TABLE vocabulary_analysis ADD COLUMN page_number INTEGER;
-- 데이터 복원 스크립트 필요
```

## 검증 방법

### 1. 정확성 테스트
```bash
# 특정 문서의 특정 페이지 어휘만 조회되는지 확인
curl -X POST "http://localhost:8080/vocabulary-analysis/search" \
  -H "Content-Type: application/json" \
  -d '{
    "textbookId": 123,
    "pageNumber": 5,
    "blockId": "block_1"
  }'
```

### 2. 데이터 격리 확인
- 다른 문서(documentId: 456)의 어휘가 조회되지 않는지 확인
- 동일한 페이지의 다른 블록 어휘가 조회되지 않는지 확인

## 문제 해결 효과

1. **정확성**: 어휘가 해당 문서의 해당 페이지에서만 조회됨
2. **성능**: 불필요한 Fallback 로직 제거로 응답 시간 개선
3. **유지보수**: 명확한 엔티티 관계로 코드 이해도 향상
4. **확장성**: 새로운 검색 기능 추가 용이

## 지원 필요 시

배포 후 문제 발생 시 아래 정보를 포함하여 문의:
- 실행한 API 요청 (파라미터 포함)
- 기대 결과 vs 실제 결과
- 로그 메시지 (DEBUG 레벨 활성화)
- 데이터베이스 상태 (관련 테이블 데이터)