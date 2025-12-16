import { useCallback, useEffect, useState } from 'react';

interface DocumentStatus {
	id: number;
	status: string;
	progress: number;
	totalPages?: number;
}

export const useDocumentPolling = (documentId: number, isActive: boolean) => {
	const [status, setStatus] = useState<DocumentStatus | null>(null);
	const [isPolling, setIsPolling] = useState(false);

	const fetchStatus = useCallback(async () => {
		try {
			// Mock API call - 실제로는 서버에서 상태를 가져옴
			// const response = await fetch(`/api/documents/status/${documentId}`);
			// const data = await response.json();

			// 시뮬레이션: 진행률을 점진적으로 증가
			setStatus((prev) => {
				if (!prev) {
					return { id: documentId, status: '변환 중', progress: 10 };
				}

				const newProgress = Math.min(prev.progress + Math.random() * 15, 100);
				const newStatus = newProgress >= 100 ? '변환 완료' : '변환 중';

				return {
					...prev,
					progress: newProgress,
					status: newStatus,
					totalPages:
						newProgress >= 100
							? Math.floor(Math.random() * 30) + 10
							: undefined,
				};
			});
		} catch (error) {
			console.error('Failed to fetch document status:', error);
			setStatus((prev) => (prev ? { ...prev, status: '변환 실패' } : null));
		}
	}, [documentId]);

	useEffect(() => {
		if (!isActive || !documentId) return;

		setIsPolling(true);

		const interval = setInterval(() => {
			fetchStatus();
		}, 3000); // 3초마다 폴링

		// 초기 상태 가져오기
		fetchStatus();

		return () => {
			clearInterval(interval);
			setIsPolling(false);
		};
	}, [documentId, isActive, fetchStatus]);

	// 변환 완료시 폴링 중지
	useEffect(() => {
		if (
			status &&
			(status.status === '변환 완료' || status.status === '변환 실패')
		) {
			setIsPolling(false);
		}
	}, [status]);

	return { status, isPolling };
};
