-- 난독증 API 프로젝트를 위한 PostgreSQL 확장 설정

-- UUID 생성을 위한 확장
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 전문 검색을 위한 확장 (한국어 텍스트 검색에 유용)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 성능 모니터링을 위한 확장
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- JSON 처리 개선을 위한 함수들
-- (교육 콘텐츠나 설정 정보를 JSON으로 저장할 때 유용)