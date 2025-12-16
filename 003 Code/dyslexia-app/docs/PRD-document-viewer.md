# PRD: Document Viewer Refactoring

## 1. 개요

**목표:** `@src/routes/teacher/viewer/$documentId.tsx`를 리팩터링하여 Notion API와 유사하게 JSON 객체에서 다양한 블록 타입을 파싱하고 렌더링하여 풍부한 책과 같은 경험을 제공합니다.

**배경:** 현재 뷰어는 `processedContent` 내의 `blocks` 배열을 기반으로 동적 콘텐츠를 렌더링해야 합니다. 각 블록은 `TEXT`, `HEADING1`, `PAGE_IMAGE` 등과 같은 특정 타입을 가지고 있으며, 이를 적절한 UI 컴포넌트로 변환하여 사용자에게 매끄러운 읽기 경험을 제공해야 합니다.

## 2. 기능 요구사항

### 2.1. 블록 파싱 및 렌더링

- **블록 처리:** `processedContent.blocks` 배열을 반복하여 각 블록 객체를 파싱해야 합니다.
- **동적 렌더링:** `parseBlocks` 유틸리티 함수(`@/features/viewer/lib/parse-blocks.tsx`에서 제공)를 사용하여 각 블록을 해당 React 노드로 변환해야 합니다.
- **지원 블록 유형:**
    - `HEADING1`, `HEADING2`, `HEADING3`: 각각 `<h2>`, `<h3>`, `<h4>` 태그로 렌더링되며, 적절한 타이포그래피 스타일이 적용됩니다.
    - `TEXT`: `<p>` 또는 `<div>` 태그로 렌더링됩니다.
    - `PAGE_IMAGE`: `<img>` 태그와 선택적 캡션(`figcaption`)으로 렌더링됩니다.
    - `LIST`, `DOTTED`: `<ul>` 및 `<li>` 항목으로 렌더링됩니다.
    - `TABLE`: `<table>` 구조로 렌더링됩니다.
    - `PAGE_TIP`: 뷰어 내에서 특별히 처리되어야 합니다.

### 2.2. 컴포넌트 구조

- **데이터 페칭:** `$documentId.tsx`의 메인 컴포넌트는 `result` 배열이 포함된 문서를 페칭합니다.
- **`DocumentRenderer` 컴포넌트:**
    - `blocks` 배열과 렌더링 옵션을 받는 새로운 `DocumentRenderer` 컴포넌트를 생성합니다.
    - 이 컴포넌트는 `parseBlocks`를 호출하여 블록을 React 노드로 변환하고 렌더링합니다.

### 2.3. 스타일링

- **타이포그래피 및 레이아웃:** 가독성 높은 책과 같은 인터페이스를 위해 적절한 간격, 타이포그래피 및 레이아웃을 보장합니다.
- **활성 블록 하이라이트:** 사용자가 상호작용하는 활성 블록을 시각적으로 하이라이트하는 기능을 지원합니다.

## 3. 기술 구현 계획

1. **`@/routes/teacher/viewer/$documentId.tsx` 수정:**
    - API로부터 문서를 페칭하고 `processedContent.blocks`를 추출합니다.
    - 페칭한 데이터를 `DocumentRenderer` 컴포넌트로 전달합니다.

2. **`DocumentRenderer` 컴포넌트 생성:**
    - 이 컴포넌트는 `blocks`를 props로 받아 `parseBlocks`를 사용하여 렌더링 로직을 처리합니다.

3. **`@/features/viewer/lib/parse-blocks.tsx` 업데이트:**
    - `PAGE_TIP`과 같은 누락된 블록 유형을 처리하고 기존 블록 유형의 렌더링을 개선하기 위해 `parseBlocks` 함수를 업데이트합니다.

4. **블록 스타일링:**
    - 모든 지원 블록 유형에 대한 CSS 스타일을 구현하여 일관되고 시각적으로 매력적인 디자인을 보장합니다.

5. **통합:**
    - `DocumentRenderer`를 뷰어 페이지에 통합하여 전체 기능이 올바르게 작동하는지 확인합니다.

## 4. 기대 결과

- 사용자는 Notion과 유사한 방식으로 렌더링된 포맷된 문서를 볼 수 있습니다.
- 다양한 콘텐츠 유형(텍스트, 제목, 이미지 등)이 명확하고 읽기 쉬운 형식으로 표시됩니다.
- 코드는 재사용 가능한 컴포넌트로 모듈화되어 유지보수 및 확장이 용이합니다.
