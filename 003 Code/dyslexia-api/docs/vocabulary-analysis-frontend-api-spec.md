# 어휘 분석 API - React 프론트엔드 연동 명세서

## 📋 개요

어휘 분석 기능이 FastAPI 콜백 방식으로 강화되어, React 프론트엔드에서 실시간 어휘 분석 결과를 조회할 수 있는 새로운 API가 제공됩니다.

### 주요 변경사항
- ✅ **음운 분석 데이터 추가**: `phoneme_analysis_json` 필드로 음성학적 정보 제공
- ✅ **실시간 콜백 기반**: FastAPI에서 블록 단위로 실시간 데이터 수신
- ✅ **향상된 디버깅**: 상세 로그 및 디버그 엔드포인트 제공
- ✅ **안정성 강화**: null 처리 및 에러 핸들링 개선

---

## 🔗 API 엔드포인트

### 1. 어휘 분석 결과 검색 (기존 개선)

**Endpoint**: `POST /api/vocabulary-analysis/search`

**Request Body**:
```json
{
  "documentId": 24,          // 문서 ID (필수)
  "pageNumber": 1,           // 페이지 번호 (선택)
  "blockId": "43"           // 블록 ID (선택)
}
```

**Response** (성공):
```json
{
  "timestamp": "2025-09-22 06:26:35",
  "code": 1000,
  "message": "어휘 분석 검색 완료",
  "result": [
    {
      "id": 1,
      "textbookId": 7,
      "pageNumber": 1,
      "blockId": "block-1",
      "word": "영수증",
      "startIndex": 2,
      "endIndex": 5,
      "definition": "구매한 물품에 대한 증명서",
      "simplifiedDefinition": "물건을 사고 받는 종이",
      "examples": "영수증을 잘 보관하세요, 영수증이 없으면 교환이 어려워요",
      "difficultyLevel": "medium",
      "reason": "초등 고학년에서 배우는 경제 용어",
      "gradeLevel": 4,
      "phoneme_analysis_json": "{\"phonemes\":[\"영\",\"수\",\"증\"],\"syllables\":3,\"difficulty\":\"medium\"}",
      "createdAt": "2025-01-15T12:35:12"
    }
  ]
}
```

**Response** (빈 결과):
```json
{
  "timestamp": "2025-09-22 06:26:35",
  "code": 1000,
  "message": "어휘 분석 검색 완료",
  "result": []
}
```

### 2. 디버그용 Textbook 조회 (신규)

**Endpoint**: `GET /api/vocabulary-analysis/debug/textbook/{documentId}`

**사용 목적**: `documentId`로 `Textbook`을 찾을 수 있는지 확인 (개발/디버그용)

**Example**: `GET /api/vocabulary-analysis/debug/textbook/24`

**Response** (성공):
```json
{
  "success": true,
  "textbook": {
    "id": 7,
    "documentId": 24,
    "title": "초등 국어 교재",
    "pageCount": 100
  }
}
```

**Response** (실패):
```json
{
  "success": false,
  "message": "DocumentId 24에 해당하는 Textbook을 찾을 수 없습니다"
}
```

---

## 📊 데이터 구조

### VocabularyAnalysis 객체

| 필드명 | 타입 | 설명 | 예시 |
|--------|------|------|------|
| `id` | `number` | 고유 ID | `1` |
| `textbookId` | `number` | 교재 ID | `7` |
| `pageNumber` | `number` | 페이지 번호 | `1` |
| `blockId` | `string` | 블록 ID | `"block-1"` |
| `word` | `string` | 분석된 단어 | `"영수증"` |
| `startIndex` | `number` | 단어 시작 위치 | `2` |
| `endIndex` | `number` | 단어 끝 위치 | `5` |
| `definition` | `string` | 단어 정의 | `"구매한 물품에 대한 증명서"` |
| `simplifiedDefinition` | `string` | 쉬운 정의 | `"물건을 사고 받는 종이"` |
| `examples` | `string` | 예문 (쉼표 구분) | `"영수증을 잘 보관하세요, 영수증이 없으면..."` |
| `difficultyLevel` | `string` | 난이도 | `"easy"`, `"medium"`, `"hard"` |
| `reason` | `string` | 선정 이유 | `"초등 고학년에서 배우는 경제 용어"` |
| `gradeLevel` | `number` | 권장 학년 | `4` |
| `phoneme_analysis_json` | `string` | 음운 분석 JSON | `"{\"phonemes\":[\"영\",\"수\",\"증\"]}"` |
| `createdAt` | `string` | 생성 시간 | `"2025-01-15T12:35:12"` |

### 음운 분석 JSON 구조

`phoneme_analysis_json` 필드를 파싱하면 다음 구조입니다:

```typescript
interface PhonemeAnalysis {
  phonemes: string[];        // 음소 배열 ["영", "수", "증"]
  syllables: number;         // 음절 수 3
  difficulty: string;        // 발음 난이도 "easy|medium|hard"
  pronunciation?: string;    // 발음 기호 (선택적)
}
```

---

## 🛠 프론트엔드 구현 가이드

### 1. TypeScript 타입 정의

```typescript
// types/vocabulary.ts
export interface VocabularyAnalysis {
  id: number;
  textbookId: number;
  pageNumber: number;
  blockId: string;
  word: string;
  startIndex: number;
  endIndex: number;
  definition: string;
  simplifiedDefinition?: string;
  examples?: string;
  difficultyLevel?: string;
  reason?: string;
  gradeLevel?: number;
  phoneme_analysis_json?: string;
  createdAt: string;
}

export interface PhonemeAnalysis {
  phonemes: string[];
  syllables: number;
  difficulty: string;
  pronunciation?: string;
}

export interface VocabularySearchRequest {
  documentId: number;
  pageNumber?: number;
  blockId?: string;
}

export interface VocabularySearchResponse {
  timestamp: string;
  code: number;
  message: string;
  result: VocabularyAnalysis[];
}
```

### 2. API 클라이언트 구현

```typescript
// api/vocabularyApi.ts
import { ApiClient } from './base';

export class VocabularyApi extends ApiClient {

  /**
   * 어휘 분석 결과 검색
   */
  async searchVocabularyAnalysis(request: VocabularySearchRequest): Promise<VocabularyAnalysis[]> {
    const response = await this.post<VocabularySearchResponse>(
      '/vocabulary-analysis/search',
      request
    );
    return response.result;
  }

  /**
   * 디버그: DocumentId로 Textbook 조회
   */
  async debugTextbookLookup(documentId: number): Promise<any> {
    return await this.get(`/vocabulary-analysis/debug/textbook/${documentId}`);
  }
}
```

### 3. React Hook 구현

```typescript
// hooks/useVocabularyAnalysis.ts
import { useState, useCallback } from 'react';
import { VocabularyApi } from '../api/vocabularyApi';
import { VocabularyAnalysis, VocabularySearchRequest, PhonemeAnalysis } from '../types/vocabulary';

export const useVocabularyAnalysis = () => {
  const [vocabularyData, setVocabularyData] = useState<VocabularyAnalysis[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const vocabularyApi = new VocabularyApi();

  const searchVocabulary = useCallback(async (request: VocabularySearchRequest) => {
    setLoading(true);
    setError(null);

    try {
      const results = await vocabularyApi.searchVocabularyAnalysis(request);
      setVocabularyData(results);
      return results;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '어휘 분석 검색 중 오류가 발생했습니다';
      setError(errorMessage);
      console.error('Vocabulary search error:', err);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // 음운 분석 JSON 파싱 유틸리티
  const parsePhonemeAnalysis = useCallback((phonemeJson: string | undefined): PhonemeAnalysis | null => {
    if (!phonemeJson) return null;

    try {
      return JSON.parse(phonemeJson) as PhonemeAnalysis;
    } catch (error) {
      console.warn('Failed to parse phoneme analysis:', error);
      return null;
    }
  }, []);

  return {
    vocabularyData,
    loading,
    error,
    searchVocabulary,
    parsePhonemeAnalysis
  };
};
```

### 4. 컴포넌트 예시

```tsx
// components/VocabularyViewer.tsx
import React, { useEffect } from 'react';
import { useVocabularyAnalysis } from '../hooks/useVocabularyAnalysis';

interface Props {
  documentId: number;
  pageNumber?: number;
  blockId?: string;
}

export const VocabularyViewer: React.FC<Props> = ({ documentId, pageNumber, blockId }) => {
  const { vocabularyData, loading, error, searchVocabulary, parsePhonemeAnalysis } = useVocabularyAnalysis();

  useEffect(() => {
    searchVocabulary({ documentId, pageNumber, blockId });
  }, [documentId, pageNumber, blockId, searchVocabulary]);

  if (loading) return <div>어휘 분석 결과를 불러오는 중...</div>;
  if (error) return <div className="error">오류: {error}</div>;
  if (!vocabularyData.length) return <div>어휘 분석 결과가 없습니다.</div>;

  return (
    <div className="vocabulary-viewer">
      <h3>어휘 분석 결과 ({vocabularyData.length}개)</h3>

      {vocabularyData.map((item) => {
        const phonemeData = parsePhonemeAnalysis(item.phoneme_analysis_json);

        return (
          <div key={item.id} className="vocabulary-item">
            <div className="word-info">
              <span className="word">{item.word}</span>
              {item.difficultyLevel && (
                <span className={`difficulty ${item.difficultyLevel}`}>
                  {item.difficultyLevel}
                </span>
              )}
              {item.gradeLevel && (
                <span className="grade">권장: {item.gradeLevel}학년</span>
              )}
            </div>

            <div className="definition">
              <strong>정의:</strong> {item.definition}
            </div>

            {item.simplifiedDefinition && (
              <div className="simple-definition">
                <strong>쉬운 설명:</strong> {item.simplifiedDefinition}
              </div>
            )}

            {item.examples && (
              <div className="examples">
                <strong>예문:</strong>
                <ul>
                  {item.examples.split(',').map((example, idx) => (
                    <li key={idx}>{example.trim()}</li>
                  ))}
                </ul>
              </div>
            )}

            {phonemeData && (
              <div className="phoneme-analysis">
                <strong>발음 분석:</strong>
                <div>음절: {phonemeData.syllables}개</div>
                <div>음소: {phonemeData.phonemes.join(' - ')}</div>
                <div>발음 난이도: {phonemeData.difficulty}</div>
              </div>
            )}

            {item.reason && (
              <div className="selection-reason">
                <strong>선정 이유:</strong> {item.reason}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
```

---

## 🐛 디버깅 가이드

### 1. 검색 결과가 빈 배열일 때

**확인 순서**:
1. 디버그 API로 `Textbook` 존재 확인:
   ```bash
   GET /api/vocabulary-analysis/debug/textbook/{documentId}
   ```

2. 서버 로그 확인:
   - `documentId` → `textbookId` 매핑 과정
   - DB 검색 쿼리 실행 결과
   - Repository 리턴 값

3. 파라미터 확인:
   - `pageNumber`, `blockId`가 DB의 실제 값과 일치하는지
   - 대소문자, 공백 등 정확한 매칭 확인

### 2. 음운 분석 데이터가 없을 때

```typescript
// 안전한 음운 분석 데이터 처리
const phonemeData = item.phoneme_analysis_json
  ? (() => {
      try {
        return JSON.parse(item.phoneme_analysis_json);
      } catch {
        return null;
      }
    })()
  : null;
```

### 3. 에러 핸들링

```typescript
// API 호출 시 에러 처리
try {
  const results = await vocabularyApi.searchVocabularyAnalysis(request);
  if (results.length === 0) {
    console.warn('No vocabulary data found for:', request);
    // 사용자에게 안내 메시지 표시
  }
} catch (error) {
  if (error.response?.status === 404) {
    console.warn('Document not found:', request.documentId);
  } else {
    console.error('API error:', error);
  }
}
```

---

## 📝 체크리스트

### 개발 전 확인사항
- [ ] Spring Boot 서버가 8084 포트에서 실행 중인지 확인
- [ ] 어휘 분석 데이터가 DB에 존재하는지 확인
- [ ] `documentId`에 해당하는 `Textbook`이 존재하는지 확인

### 구현 체크리스트
- [ ] TypeScript 타입 정의 완료
- [ ] API 클라이언트 구현 완료
- [ ] React Hook 구현 완료
- [ ] 컴포넌트 구현 완료
- [ ] 에러 핸들링 구현 완료
- [ ] 음운 분석 JSON 파싱 로직 구현 완료

### 테스트 체크리스트
- [ ] 정상 케이스: 어휘 데이터가 있는 경우
- [ ] 빈 결과 케이스: 어휘 데이터가 없는 경우
- [ ] 에러 케이스: 잘못된 `documentId`인 경우
- [ ] 음운 분석 데이터 표시 확인
- [ ] 로딩 상태 및 에러 메시지 확인

---

## 📞 지원

문제가 발생하거나 추가 기능이 필요한 경우:
- 백엔드 개발팀에 문의하여 디버그 로그 확인 요청
- API 명세 변경이 필요한 경우 백엔드 팀과 협의
- 새로운 검색 조건이나 필터링 기능 요청 시 백엔드 팀에 요구사항 전달