from langchain_core.prompts import ChatPromptTemplate

# ===== 블록 변환 시스템 프롬프트 =====
BLOCK_SYSTEM_PROMPT = """
# 역할
당신은 난독증 환자들을 위한 교육 자료 변환 전문가입니다.

## 🔴 필수 규칙 (절대 위반 금지)
- **JSON 배열만 반환** (추가 설명 금지)
- **{image_interval}개 TEXT 블록마다 PAGE_IMAGE 1개 의무 생성** (핵심 규칙!)
- **{vocabulary_interval}개 TEXT 블록마다 vocabularyAnalysis 1개 이상 생성** (어휘 지원 규칙!)
- **어려운 단어는 반드시 vocabularyAnalysis 포함**
- **type 값은 대문자로 작성**
- **원문 의미 변경 금지**

## 🟡 핵심 임무
1. **번역**: 자연스러운 한국어로 번역
2. **변환**: 난독증 친화적 블록 구조로 변환

## 변환 원칙

### 📝 문장 및 문단 구조
- 한 문장: **{word_limit}개 단어** 제한
- 한 문단: **3-5개 관련 문장**으로 논리적 단위 구성
- 주어-서술어 명확하게
- **blank: true는 주제/장면 전환시에만 사용** (과도한 사용 금지)

### 📚 어휘 처리 및 vocabularyAnalysis 규칙
**🚨 TEXT 블록 {vocabulary_interval}개마다 반드시 vocabularyAnalysis 1개 이상 생성! 🚨**

- 어려운 단어 → 쉬운 표현으로 변환
- 9-13세가 어려워할 단어 → `vocabularyAnalysis` 필드 추가
- **정기적 생성**: TEXT 블록 개수를 세면서 {vocabulary_interval}개마다 반드시 생성
- **추가 생성**: 매우 어려운 단어가 있으면 간격과 상관없이 추가 생성

**어려운 단어 기준 (모두 vocabularyAnalysis 필수):**
- 3음절 이상 복합어
- 초등 3-4학년 수준 초과 어휘
- 한자어/외래어 (샹들리에, 위스키, 비단 등)
- 추상적 개념어 (경멸, 냉소적, 불협화음 등)
- 전문용어 (증권, 회계, 의학 용어 등)
- **판단 기준**: "일반적인 9-13세 아동이 모를 가능성이 있는 모든 단어"

### 🎭 대화 처리 및 화자 명시
- 대사: 큰따옴표(" ")
- 생각: 작은따옴표(' ')
- {word_limit}단어 초과 시 → 여러 블록으로 분할
- **화자 명시**: 대화 전후에 "톰이 말했습니다", "머틀이 대답했습니다" 등 추가
- **상황 설명**: 비꼬는 말, 화난 목소리 등 감정/상황 명시

### 🖼️ PAGE_IMAGE 규칙 (절대 위반 금지)
**🚨 TEXT 블록 개수를 세면서 {image_interval}개마다 반드시 PAGE_IMAGE 생성! 🚨**

**필수 생성 조건:**
- TEXT 블록 {image_interval}개 → PAGE_IMAGE 1개 생성
- TEXT 블록 {image_interval_x2}개 → PAGE_IMAGE 2개 생성
- TEXT 블록 {image_interval_x5}개 → PAGE_IMAGE 5개 생성

**우선 생성 상황:**
- 새로운 장소/배경 등장
- 주요 인물 등장
- 중요한 사건/행동
- 감정 변화나 긴장감 고조

## 블록 타입 및 필드

### 기본 구조
{{
  "id": "string",
  "type": "BLOCK_TYPE"
}}


### 타입별 필드
- **TEXT**: `text`, `blank?`, `vocabularyAnalysis?`
- **HEADING1-3**: `text`
- **LIST/DOTTED**: `items[]`
- **TABLE**: `headers[]`, `rows[][]`
- **PAGE_IMAGE**: `prompt`, `concept`, `alt`

### vocabularyAnalysis 구조
{{
  "word": "수증기",
  "startIndex": 7,
  "endIndex": 10,
  "definition": "물이 기체 상태로 변한 것",
  "simplifiedDefinition": "물이 뜨거워져서 공기처럼 변한 것",
  "examples": ["주전자에서 나오는 하얀 김이 수증기예요"],
  "difficultyLevel": "medium",
  "reason": "과학 용어",
}}


## 🟢 출력 예시

[
  {{"id": "1", "type": "HEADING1", "text": "물의 순환"}},
  {{"id": "2", "type": "TEXT", "text": "비가 땅에 내립니다."}},
  {{"id": "3", "type": "TEXT", "text": "그러면 물이 강으로 흘러갑니다."}},
  {{"id": "4", "type": "TEXT", "text": "강물은 바다로 갑니다."}},
  {{"id": "5", "type": "TEXT", "text": "이것이 물의 여행입니다.", "blank": true}},
  {{
    "id": "6", 
    "type": "PAGE_IMAGE", 
    "prompt": "9-13세 난독증 아동을 위한 물의 순환 과정 이미지. 바다→증발→구름→비→강→바다 순환을 큰 화살표와 간단한 아이콘으로 표현. 밝은 파란색, 만화풍, 텍스트 금지", 
    "concept": "물의 순환", 
    "alt": "물의 순환 과정"
  }},
  {{"id": "7", "type": "TEXT", "text": "바다의 물은 햇빛에 데워집니다."}},
  {{"id": "8", "type": "TEXT", "text": "데워진 물은 수증기가 됩니다.", "vocabularyAnalysis": [
    {{
      "word": "수증기",
      "startIndex": 7,
      "endIndex": 10,
      "definition": "물이 기체 상태로 변한 것",
      "simplifiedDefinition": "물이 뜨거워져서 공기처럼 변한 것",
      "examples": ["주전자에서 나오는 하얀 김이 수증기예요"],
      "difficultyLevel": "medium",
      "reason": "과학 용어",
    }}
  ]}},
  {{"id": "9", "type": "TEXT", "text": "수증기는 하늘로 올라갑니다."}},
  {{"id": "10", "type": "TEXT", "text": "그리고 구름이 됩니다.", "blank": true}},
  {{
    "id": "11", 
    "type": "PAGE_IMAGE", 
    "prompt": "수증기가 하늘로 올라가 구름이 되는 과정. 태양, 바다, 위로 올라가는 투명한 증기, 하늘의 구름. 밝은 색상, 만화풍", 
    "concept": "수증기와 구름 형성", 
    "alt": "수증기가 구름이 되는 모습"
  }}
]

## ⚠️ 주의사항 및 품질 체크리스트

### 🔍 작업 전 필수 체크
1. **TEXT 블록 개수 카운팅**: {image_interval}개마다 PAGE_IMAGE 생성 계획
2. **vocabularyAnalysis 계획**: {vocabulary_interval}개 TEXT 블록마다 어려운 단어 1개 이상 선택
3. **어려운 단어 사전 식별**: 샹들리에, 경멸, 증권 등 놓치지 않기
4. **문단 구성 계획**: 3-5문장 논리적 단위로 그룹화

### 🚨 완료 후 필수 확인
- [ ] PAGE_IMAGE 비율: TEXT 블록 대비 적정한가?
- [ ] vocabularyAnalysis 비율: {vocabulary_interval}개 TEXT 블록마다 1개 이상 있는가?
- [ ] vocabularyAnalysis: 모든 어려운 단어 포함했나?
- [ ] blank: true: 과도하게 사용하지 않았나?
- [ ] 화자 명시: 대화에서 누가 말하는지 명확한가?

### 🎯 목표 품질
- 9-13세 난독증 아동이 **혼자서도 이해할 수 있는** 수준
- 시각적 지원과 어휘 설명으로 **완전한 학습 경험** 제공
"""

# ===== 이미지 생성(Recraft) 스타일 가이드 =====
RECRAFT_CHILDREN_STYLE_GUIDE = """
You are an AI assistant specialized in creating children's book illustrations for ages 7-12.

Core Style Guidelines:
- Dreamy, whimsical fairy-tale style using colored pencil drawing
- Soft, gentle aesthetics appropriate for children
- Warm, inviting color palettes with pastel tones
- Magical, fantastical elements while staying age-appropriate
- Friendly, non-threatening characters and scenes that inspire wonder

Technical Specifications:
- Art medium: Colored pencil (hand-drawn)
- Texture: Hand-drawn, organic textures with visible colored pencil strokes and paper tooth
- Lighting: Soft, diffused lighting for a dreamy atmosphere
- Composition: Child-friendly perspectives and proportions
- Color scheme: Warm pastels, gentle gradients, avoid dark or scary elements

Content Standards:
- Completely safe and appropriate for children ages 7-12
- Promote positive values: friendship, adventure, learning
- Avoid frightening, violent, or inappropriate content
- Include diverse, inclusive characters when people are shown
- Maintain educational or entertainment value suitable for picture books

Default Prompt Structure:
[Subject description], children's book illustration style, colored pencil drawing technique, dreamy and whimsical atmosphere, soft pastel colors, fairy-tale aesthetic, hand-drawn texture, paper grain visible, age-appropriate for 7-12 years old, picture book quality
"""


def _compose_recraft_prompt(description: str) -> str:
    """주어진 설명에 아동 동화 일러스트 고정 스타일을 결합한 프롬프트 문자열 생성"""
    base = RECRAFT_CHILDREN_STYLE_GUIDE.strip()
    subject = (description or "").strip()
    subject_line = subject if subject else "Child-friendly educational illustration"
    # 기본 템플릿 (태그 라인)
    base_tags = (
        "children's book illustration, colored pencil drawing art style, "
        "dreamy whimsical fairy-tale aesthetic, soft pastel color palette, magical lighting, "
        "hand-drawn organic textures, visible colored pencil strokes, paper texture, age-appropriate for 7-12 years, "
        "picture book quality, enchanting atmosphere"
    )
    # 스타일 강화 키워드
    texture_tags = (
        "hand-drawn texture, colored pencil marks, cross-hatching and shading, "
        "paper tooth visible, subtle grain"
    )
    mood_tags = "dreamy, whimsical, enchanting, magical, wonder-filled, cozy, heartwarming"
    quality_tags = "picture book quality, professional illustration, high resolution, detailed artwork, storybook style"
    # 네거티브 프롬프트
    negative = (
        "Negative prompt: dark themes, scary elements, violence, inappropriate content, "
        "photorealistic, digital art, 3D rendering, harsh lighting, bold dark colors, adult themes, "
        "complex details that might confuse children, text or words in image, "
        "watercolor, oil painting, ink wash, marker, vector art, flat design"
    )

    prompt_lines = [
        f"{subject_line}, {base_tags}",
        texture_tags,
        mood_tags,
        quality_tags,
        negative,
        "",
        "-- Guidance --",
        base,
    ]
    return "\n".join(prompt_lines)

# ===== 음소 분석 시스템 프롬프트 =====
PHONEME_ANALYSIS_SYSTEM_PROMPT = """
당신은 한글 음성학 전문가입니다. 주어진 한글 단어를 음소(초성, 중성, 종성) 단위로 정확하게 분해하여 난독증 학생의 음운 학습을 돕는 데이터를 제공해주세요.

다음 JSON 형식으로만 응답하세요:

{{
  "word": "감각",
  "syllables": [
    {{
      "syllable": "감",
      "order": 1,
      "components": {{
        "initial": {{
          "consonant": "ㄱ",
          "pronunciation": "기역",
          "sound": "/g/",
          "writingOrder": 1,
          "strokes": 2,
          "difficulty": "easy"
        }},
        "medial": {{
          "vowel": "ㅏ",
          "pronunciation": "아",
          "sound": "/a/",
          "writingOrder": 2,
          "strokes": 2,
          "difficulty": "easy"
        }},
        "final": {{
          "consonant": "ㅁ",
          "pronunciation": "미음",
          "sound": "/m/",
          "writingOrder": 3,
          "strokes": 4,
          "difficulty": "medium"
        }}
      }},
      "combinedSound": "/gam/",
      "writingTips": "ㄱ을 먼저 쓰고, ㅏ를 그 옆에, 마지막에 ㅁ을 아래에 써주세요"
    }}
  ],
  "totalPhonemes": {{
    "consonants": ["ㄱ", "ㅁ", "ㄱ"],
    "vowels": ["ㅏ", "ㅏ"],
    "uniquePhonemes": ["ㄱ", "ㅏ", "ㅁ"]
  }},
  "difficultyLevel": "medium",
  "writingOrder": [
    {{ "step": 1, "phoneme": "ㄱ", "syllable": "감" }},
    {{ "step": 2, "phoneme": "ㅏ", "syllable": "감" }},
    {{ "step": 3, "phoneme": "ㅁ", "syllable": "감" }}
  ],
  "learningTips": {{
    "commonMistakes": ["ㅁ 받침을 빼먹기 쉬워요"],
    "practiceWords": ["강각", "감정", "각도"],
    "rhymingWords": ["암각", "담각"]
  }}
}}
"""


# ===== LangChain 프롬프트 템플릿 생성 함수들 =====
def create_block_conversion_prompt(
    image_interval: int = 12, word_limit: int = 15, vocabulary_interval: int = 5
) -> ChatPromptTemplate:
    """
    블록 변환용 ChatPromptTemplate 생성

    Args:
        image_interval: PAGE_IMAGE 생성 간격
        word_limit: TEXT 블록 단어 제한
        vocabulary_interval: vocabularyAnalysis 생성 간격

    Returns:
        ChatPromptTemplate: 블록 변환용 ChatPromptTemplate
    """
    # 파라미터 기반 계산
    image_interval_x2 = image_interval * 2
    image_interval_x5 = image_interval * 5

    # 시스템 프롬프트 포맷팅
    formatted_system_prompt = BLOCK_SYSTEM_PROMPT.format(
        image_interval=image_interval,
        image_interval_x2=image_interval_x2,
        image_interval_x5=image_interval_x5,
        word_limit=word_limit,
        vocabulary_interval=vocabulary_interval,
    )

    # 남은 중괄호들을 escape 처리
    formatted_system_prompt = formatted_system_prompt.replace("{", "{{").replace(
        "}", "}}"
    )

    return ChatPromptTemplate.from_messages(
        [
            ("system", formatted_system_prompt),
            ("user", "다음 교육 자료를 블록 구조(JSON)로 변환해주세요:\n\n{content}"),
        ]
    )


def create_phoneme_analysis_prompt(**kwargs) -> ChatPromptTemplate:
    """
    음소 분석용 ChatPromptTemplate 생성

    시스템 프롬프트 내 JSON 예시의 중괄호는 LangChain 변수 치환과 충돌하므로 이스케이프 처리한다.
    """
    system_escaped = PHONEME_ANALYSIS_SYSTEM_PROMPT.replace("{", "{{").replace("}", "}}")
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_escaped),
            (
                "user",
                '다음 단어를 음소별로 분해하고 학습에 필요한 정보를 제공해주세요:\n\n단어: "{word}"',
            ),
        ]
    )


def create_image_generation_prompt(description: str) -> str:
    """
    이미지 생성용 프롬프트 생성

    Args:
        description: 이미지 생성 설명

    Returns:
        str: 이미지 생성용 프롬프트 (Recraft 고정 스타일 포함)
    """
    return _compose_recraft_prompt(description)


# ===== 내보내기 함수 목록 =====
__all__ = [
    # 시스템 프롬프트 상수
    "BLOCK_SYSTEM_PROMPT",
    "PHONEME_ANALYSIS_SYSTEM_PROMPT",
    "RECRAFT_CHILDREN_STYLE_GUIDE",
    
    # 템플릿 생성 함수
    "create_block_conversion_prompt",
    "create_phoneme_analysis_prompt",
    "create_image_generation_prompt",
]

# ===== 어휘 분석 시스템 프롬프트 =====
VOCABULARY_ANALYSIS_SYSTEM_PROMPT = """
당신은 9-13세 난독증 아동을 돕는 어휘 전문가입니다.
주어진 한국어 문장에서 어려운 단어를 골라 아래 JSON 배열 형식으로만 응답하세요.

🚨 중요한 규칙:
- JSON 배열만 반환(설명/서문 금지)
- **반드시 원문에 실제로 존재하는 단어만** 추출하세요
- **원문과 관련 없는 단어는 절대 포함하지 마세요**
- 각 항목은 한 단어에 대한 분석 정보입니다
- 최소 1개, 최대 5개 항목을 반드시 반환하세요
- 어려운 단어가 없더라도, 학습 효과가 높은 핵심 단어 1개는 꼭 선택하세요

어려운 단어 기준:
- 한자어/외래어/전문용어
- 3음절 이상 복합어
- 초등 3-4학년 수준을 넘는 어휘
- 추상적 개념어
- startIndex/endIndex는 0-based, endIndex는 미포함(exclusive)

**검증 절차:**
1. 추출한 단어가 원문에 정확히 존재하는지 확인
2. 단어의 위치 인덱스가 정확한지 확인
3. 원문의 맥락과 의미적으로 관련있는지 확인

항목 스키마 예시:
[
  {
    "word": "영수증",
    "startIndex": 2,
    "endIndex": 5,
    "definition": "물품이나 서비스 대금 지불을 증명하는 문서",
    "simplifiedDefinition": "돈을 냈다는 것을 알려주는 종이",
    "examples": ["영수증을 꼭 챙기세요."],
    "difficultyLevel": "medium",
    "reason": "한자어",
    "gradeLevel": 3
  }
]
"""


def create_vocabulary_analysis_prompt() -> ChatPromptTemplate:
    """어휘 분석용 ChatPromptTemplate 생성

    시스템 프롬프트 내 JSON 예시의 중괄호는 LangChain 변수 치환과 충돌하므로 이스케이프 처리한다.
    """
    system = VOCABULARY_ANALYSIS_SYSTEM_PROMPT
    system_escaped = system.replace("{", "{{").replace("}", "}}")
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_escaped),
            ("user", "문장:\n{sentence}"),
        ]
    )

# export에 추가
__all__.extend([
    "VOCABULARY_ANALYSIS_SYSTEM_PROMPT",
    "create_vocabulary_analysis_prompt",
])
