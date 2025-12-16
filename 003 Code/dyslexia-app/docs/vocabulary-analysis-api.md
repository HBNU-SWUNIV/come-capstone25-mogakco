# 어휘 분석 API 응답 스키마

- 목적: 문장에서 어휘 학습을 요청할 때 서버가 반환하는 응답 구조를 명세합니다.
- 반환 형태: JSON 배열 (CommonResponse 래핑 없음)
- 네이밍: camelCase
- 인증: `Authorization: Bearer <JWT>`

## 엔드포인트

- Method/Path: `POST /vocabulary-analysis/search`
- Body(JSON):
  - `documentId` (number, required)
  - `pageNumber` (number, optional)
  - `blockId` (string, optional)
- Headers:
  - `Authorization: Bearer <JWT>`
  - `Content-Type: application/json`

## 응답 타입 구조 (TypeScript)

```ts
// 결과는 아래 VocabularyAnalysis 객체의 배열입니다.
export interface VocabularyAnalysis {
  id: number;
  documentId: number;
  pageNumber: number;
  blockId: string;
  word: string;
  startIndex: number;            // 0-based 시작 인덱스 (문자 단위)
  endIndex: number;              // 0-based 종료 인덱스 (권장: exclusive, slice(startIndex, endIndex) 호환)
  definition: string;            // 자세한 뜻
  simplifiedDefinition: string;  // 쉬운 풀이
  examples: string;              // 예문 문자열 (쉼표 구분 or '["예문1"...]' JSON 문자열)
  difficultyLevel: 'easy' | 'medium' | 'hard' | string;
  reason: string;                // 선정/난이도 사유 설명
  gradeLevel: number;            // 권장 학년
  phonemeAnalysisJson: string;   // 아래 PhonemeAnalysis를 직렬화한 JSON 문자열
  createdAt: string;             // ISO-8601 문자열
  originalSentence: string;      // 분석에 사용된 원문 문장
}

// phonemeAnalysisJson 내부 구조 (직렬화 전 타입)
export interface PhonemeComponent {
  consonant: string;       // 예: 'ㅇ', 'ㅈ'
  pronunciation: string;   // 예: 'ieung', 'jieut'
  sound: string;           // 예: '/ŋ/', '/dʑ/'
  difficulty: 'easy' | 'medium' | 'hard';
}

export interface SyllableComponents {
  initial: PhonemeComponent;
  medial: {
    vowel: string;         // 예: 'ㅕ', 'ㅜ'
    pronunciation: string; // 예: 'yeo', 'u'
    sound: string;         // 예: '/jʌ/', '/u/'
    difficulty: 'easy' | 'medium' | 'hard';
  };
  final?: PhonemeComponent; // 받침이 없을 수 있음
}

export interface SyllableInfo {
  syllable: string;           // 예: '영', '수', '증'
  combinedSound: string;      // 예: 'yeong', 'su'
  writingTips: string;        // 쓰기/발음 팁
  components: SyllableComponents;
}

export interface WritingStep {
  step: number;               // 1부터 시작하는 단계 번호
  syllable: string;           // 대상 음절
  phoneme: string;            // 예: 'ㅇ-ㅕ-ㅇ'
  description: string;        // 단계 설명
}

export interface LearningTips {
  commonMistakes: string[];   // 자주 하는 실수
  practiceWords: string[];    // 연습할 단어
  rhymingWords: string[];     // 비슷한 발음/운율 단어
}

export interface PhonemeAnalysis {
  syllables: SyllableInfo[];
  writingOrder: WritingStep[];
  learningTips: LearningTips;
}
```

## JSON 예시 (성공 시 응답 바디)

```json
[
  {
    "id": 101,
    "documentId": 7,
    "pageNumber": 1,
    "blockId": "b-12",
    "word": "영수증",
    "startIndex": 2,
    "endIndex": 5,
    "definition": "물품을 사거나 돈을 지불했다는 사실을 증명하는 문서.",
    "simplifiedDefinition": "물건을 샀다는 것을 알려주는 종이.",
    "examples": "[\"영수증을 꼭 챙기세요.\", \"전자영수증을 받았어요.\"]",
    "difficultyLevel": "medium",
    "reason": "학년 수준 대비 난이도 높은 어휘",
    "gradeLevel": 3,
    "phonemeAnalysisJson": "{\"syllables\":[{\"syllable\":\"영\",\"combinedSound\":\"yeong\",\"writingTips\":\"ㅇ의 시작 소리에 주의\",\"components\":{\"initial\":{\"consonant\":\"ㅇ\",\"pronunciation\":\"ieung\",\"sound\":\"/ŋ/\",\"difficulty\":\"easy\"},\"medial\":{\"vowel\":\"ㅕ\",\"pronunciation\":\"yeo\",\"sound\":\"/jʌ/\",\"difficulty\":\"medium\"},\"final\":{\"consonant\":\"ㅇ\",\"pronunciation\":\"ieung\",\"sound\":\"/ŋ/\",\"difficulty\":\"easy\"}}},{\"syllable\":\"수\",\"combinedSound\":\"su\",\"writingTips\":\"모음 ㅜ의 입모양\",\"components\":{\"initial\":{\"consonant\":\"ㅅ\",\"pronunciation\":\"siot\",\"sound\":\"/s/\",\"difficulty\":\"medium\"},\"medial\":{\"vowel\":\"ㅜ\",\"pronunciation\":\"u\",\"sound\":\"/u/\",\"difficulty\":\"easy\"}}},{\"syllable\":\"증\",\"combinedSound\":\"jeung\",\"writingTips\":\"ㅈ과 ㅡ 발음 구별\",\"components\":{\"initial\":{\"consonant\":\"ㅈ\",\"pronunciation\":\"jieut\",\"sound\":\"/dʑ/\",\"difficulty\":\"medium\"},\"medial\":{\"vowel\":\"ㅡ\",\"pronunciation\":\"eu\",\"sound\":\"/ɨ/\",\"difficulty\":\"medium\"},\"final\":{\"consonant\":\"ㅇ\",\"pronunciation\":\"ieung\",\"sound\":\"/ŋ/\",\"difficulty\":\"easy\"}}}],\"writingOrder\":[{\"step\":1,\"syllable\":\"영\",\"phoneme\":\"ㅇ-ㅕ-ㅇ\",\"description\":\"영을 순서대로 써 봐요\"},{\"step\":2,\"syllable\":\"수\",\"phoneme\":\"ㅅ-ㅜ\",\"description\":\"수의 자음과 모음을 연결해요\"},{\"step\":3,\"syllable\":\"증\",\"phoneme\":\"ㅈ-ㅡ-ㅇ\",\"description\":\"증의 받침 ㅇ을 마무리해요\"}],\"learningTips\":{\"commonMistakes\":[\"‘영수정’으로 잘못 쓰기\",\"받침 ㅇ 발음 누락\"],\"practiceWords\":[\"영수증\",\"증명서\",\"수증기\"],\"rhymingWords\":[\"증\",\"등\",\"승\"]}}",
    "originalSentence": "전자영수증을 확인했어요.",
    "createdAt": "2025-09-21T02:49:09"
  },
  {
    "id": 102,
    "documentId": 7,
    "pageNumber": 1,
    "blockId": "b-12",
    "word": "전자",
    "startIndex": 0,
    "endIndex": 2,
    "definition": "전기를 띄는 미립자. 또는 전자 장치를 사용하는 것을 뜻함.",
    "simplifiedDefinition": "전기와 관련된 것.",
    "examples": "전자책, 전자사전",
    "difficultyLevel": "easy",
    "reason": "과학 관련 기본 어휘",
    "gradeLevel": 3,
    "phonemeAnalysisJson": "{\"syllables\":[{\"syllable\":\"전\",\"combinedSound\":\"jeon\",\"writingTips\":\"ㅈ 발음 시작 주의\",\"components\":{\"initial\":{\"consonant\":\"ㅈ\",\"pronunciation\":\"jieut\",\"sound\":\"/dʑ/\",\"difficulty\":\"medium\"},\"medial\":{\"vowel\":\"ㅓ\",\"pronunciation\":\"eo\",\"sound\":\"/ʌ/\",\"difficulty\":\"easy\"},\"final\":{\"consonant\":\"ㄴ\",\"pronunciation\":\"nieun\",\"sound\":\"/n/\",\"difficulty\":\"easy\"}}},{\"syllable\":\"자\",\"combinedSound\":\"ja\",\"writingTips\":\"자음 ㅈ과 모음 ㅏ 결합\",\"components\":{\"initial\":{\"consonant\":\"ㅈ\",\"pronunciation\":\"jieut\",\"sound\":\"/dʑ/\",\"difficulty\":\"medium\"},\"medial\":{\"vowel\":\"ㅏ\",\"pronunciation\":\"a\",\"sound\":\"/a/\",\"difficulty\":\"easy\"}}}],\"writingOrder\":[{\"step\":1,\"syllable\":\"전\",\"phoneme\":\"ㅈ-ㅓ-ㄴ\",\"description\":\"전의 획순을 익혀요\"},{\"step\":2,\"syllable\":\"자\",\"phoneme\":\"ㅈ-ㅏ\",\"description\":\"자를 깔끔하게 마무리해요\"}],\"learningTips\":{\"commonMistakes\":[\"전자 → 정자로 혼동\"],\"practiceWords\":[\"전자\",\"전자제품\",\"전자책\"],\"rhymingWords\":[\"정자\",\"전차\"]}}",
    "originalSentence": "전자영수증을 확인했어요.",
    "createdAt": "2025-09-21T02:49:09"
  }
]
```

## HTTP 상태 코드

- 200 OK: 어휘 분석 결과 배열 반환 (빈 경우 `[]`).
- 400 Bad Request: 잘못된 요청 바디(`documentId` 누락 등).
- 401 Unauthorized: 인증 실패 또는 토큰 만료.
- 404 Not Found: 해당 `documentId`가 존재하지 않음.
- 500 Internal Server Error: 서버 내부 오류.

## 오류 응답 예시

```json
{
  "error": {
    "code": "BAD_REQUEST",
    "message": "'documentId' is required"
  }
}
```

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}
```

## 메모

- 빈 결과: 해당 문장에 분석된 어휘가 없으면 빈 배열(`[]`)을 반환하세요.
- `phonemeAnalysisJson`: 문자열로 직렬화된 JSON이어야 하며, 상단 PhonemeAnalysis 구조를 충족해야 합니다.
- `examples`: 문자열형 필드입니다. 쉼표 구분 텍스트 또는 JSON 문자열(`["문장1","문장2"]`) 모두 허용됩니다.
- 인덱스 기준: `startIndex`는 포함, `endIndex`는 미포함(exclusive) 기준을 권장합니다.
