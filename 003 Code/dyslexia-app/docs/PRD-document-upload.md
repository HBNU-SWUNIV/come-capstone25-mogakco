# PRD: 교안 업로드 기능

## 📋 개요

### 목표
보호자가 PDF 교육 자료를 업로드하여 난독증 친화적 디지털 교안으로 자동 변환하는 비동기 처리 시스템 구현

### 배경
- 난독증 학생들을 위한 맞춤형 학습 자료 제공 필요
- 기존 PDF 자료의 접근성 개선 필요
- 실시간 변환 진행률 추적을 통한 사용자 경험 향상

## 🎯 핵심 요구사항

### 기능적 요구사항

#### 1. 파일 업로드 기능
- **파일 형식**: PDF 파일만 지원
- **업로드 방식**: FormData를 통한 multipart/form-data 전송
- **필수 입력**: 파일, 교안 제목
- **파일 검증**:
  - MIME 타입 검증 (application/pdf)
  - 파일 크기 제한 (추후 정의)

#### 2. 비동기 처리 시스템
- **초기 응답**: JobId 반환으로 즉시 응답
- **상태 관리**: PENDING → PROCESSING → COMPLETED/FAILED
- **진행률 추적**: 0-100% 실시간 업데이트

#### 3. 상태 모니터링
- **실시간 폴링**: JobId 기반 상태 조회
- **사용자 피드백**: 진행률 시각화
- **오류 처리**: 실패 시 재시도 옵션 제공

### 비기능적 요구사항

#### 사용성
- **직관적 UI**: 드래그 앤 드롭 또는 클릭 업로드
- **진행률 표시**: 프로그래스 바를 통한 시각적 피드백
- **상태 알림**: 토스트 메시지를 통한 실시간 알림

#### 성능
- **업로드 최적화**: 청크 업로드 지원 (향후)
- **폴링 최적화**: 적응적 폴링 간격 조정
- **응답성**: 2초 이내 초기 응답

#### 안정성
- **오류 복구**: 네트워크 오류 시 재시도
- **상태 일관성**: 새로고침 후에도 상태 유지
- **데이터 무결성**: 업로드 실패 시 정리

## 🔌 API 설계

### 1. 교안 생성 요청
```typescript
POST /v1/documents
Content-Type: multipart/form-data

Request:
{
  file: File (PDF)
}

Response: 202 Accepted
{
  jobId: string
  message: string
}
```

### 2. 상태 조회
```typescript
GET /v1/documents/{jobId}/status

Response: 200 OK
{
  jobId: string
  fileName: string
  status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED"
  progress: number (0-100)
  errorMessage?: string
  createdAt: string (ISO 8601)
  completedAt?: string (ISO 8601)
}
```

## 🎨 UI/UX 설계

### 모달 컴포넌트 구조
```
DocumentUploadModal
├── 업로드 준비 단계
│   ├── 파일 선택 영역 (드래그앤드롭)
│   ├── 교안 이름 입력
│   ├── 업로드 가이드
│   └── 액션 버튼 (취소/생성하기)
└── 업로드 진행 단계
    ├── 진행률 표시
    ├── 상태 메시지
    └── 확인 버튼
```

### 상태별 UI 변화
1. **초기 상태**: 파일 선택 대기
2. **업로드 중**: 프로그래스 바 + 진행 메시지
3. **변환 중**: 폴링을 통한 실시간 상태 업데이트
4. **완료**: 성공 메시지 + 교안 보관함 이동 옵션
5. **실패**: 오류 메시지 + 재시도 옵션

## 💻 기술 구현 사양

### React Query 구조
```typescript
// 업로드 뮤테이션
const useDocumentUpload = () => {
  return useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await axios.post('/v1/documents', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    }
  });
};

// 상태 조회 쿼리
const useDocumentStatus = (jobId: string, enabled: boolean) => {
  return useQuery({
    queryKey: ['document-status', jobId],
    queryFn: () => axios.get(`/v1/documents/${jobId}/status`),
    enabled,
    refetchInterval: (data) => {
      const status = data?.status;
      if (status === 'COMPLETED' || status === 'FAILED') {
        return false; // 폴링 중단
      }
      return 2000; // 2초 간격 폴링
    }
  });
};
```

### 상태 관리
```typescript
interface UploadState {
  phase: 'idle' | 'uploading' | 'processing' | 'completed' | 'failed';
  jobId?: string;
  progress: number;
  error?: string;
}
```

## 📱 사용자 플로우

### 성공 시나리오
1. **파일 선택**: 보호자가 PDF 파일 선택
2. **정보 입력**: 교안 이름 입력
3. **업로드 시작**: "생성하기" 버튼 클릭
4. **초기 업로드**: FormData로 파일 전송, JobId 수신
5. **상태 폴링**: 2초 간격으로 진행률 확인
6. **변환 완료**: 성공 메시지 표시
7. **페이지 이동**: 교안 보관함으로 자동 이동

### 실패 시나리오
1. **파일 검증 실패**: PDF 아닌 파일 선택 시 즉시 오류
2. **업로드 실패**: 네트워크 오류 시 재시도 옵션
3. **변환 실패**: 서버 처리 오류 시 오류 메시지 + 재시도

## 🧪 테스트 요구사항

### 단위 테스트
- [ ] 파일 타입 검증 로직
- [ ] API 호출 함수들
- [ ] 상태 변화 로직
- [ ] 폴링 중단 조건

### 통합 테스트
- [ ] 전체 업로드 플로우
- [ ] 네트워크 오류 시나리오
- [ ] 상태 폴링 동작
- [ ] 모달 상태 변화

### E2E 테스트
- [ ] 파일 선택 → 업로드 → 완료 전체 플로우
- [ ] 오류 상황에서의 사용자 경험
- [ ] 페이지 새로고침 후 상태 복구

## 🚀 개발 우선순위

### Phase 1 (MVP)
- [x] 기본 모달 UI 구현
- [ ] 파일 업로드 API 연동
- [ ] 기본 상태 폴링
- [ ] 진행률 표시

### Phase 2 (Enhancement)
- [ ] 드래그 앤 드롭 지원
- [ ] 업로드 취소 기능
- [ ] 오프라인 상태 처리
- [ ] 성능 최적화

### Phase 3 (Advanced)
- [ ] 청크 업로드
- [ ] 백그라운드 업로드
- [ ] 배치 업로드
- [ ] 진도 상태 WebSocket 연동

## 📊 성공 지표

### 기술적 지표
- 업로드 성공률: >95%
- 평균 업로드 시간: <10초 (10MB 기준)
- 상태 폴링 정확도: 100%
- 오류 복구율: >90%

### 사용자 경험 지표
- 업로드 완료까지 이탈률: <10%
- 재시도 성공률: >80%
- 사용자 만족도: 4.5/5 이상

## 🔄 향후 개선 사항

### 기능 확장
- 다중 파일 업로드
- 이미지 파일 지원 (JPG, PNG)
- Word 문서 지원
- 클라우드 스토리지 연동

### 성능 최적화
- CDN을 통한 업로드 가속화
- 압축 알고리즘 적용
- 캐싱 전략 개선

### 사용성 개선
- 실시간 미리보기
- 변환 옵션 설정
- 템플릿 기반 변환