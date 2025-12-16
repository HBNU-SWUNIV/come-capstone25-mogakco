import { useQueryClient } from '@tanstack/react-query';
import { useCallback, useEffect, useRef } from 'react';
import { documentApi } from '../api/upload';

interface ProcessingDocument {
	jobId: string;
	fileName?: string;
	startedAt: number;
}

/**
 * 전역 문서 처리 상태 폴링 훅
 * PROCESSING 상태인 모든 문서들을 10초마다 병렬로 상태 확인
 */
export const useGlobalDocumentPolling = () => {
	const queryClient = useQueryClient();
	const processingDocsRef = useRef<Map<string, ProcessingDocument>>(new Map());
	const intervalRef = useRef<NodeJS.Timeout | null>(null);

	// 처리 중인 문서 추가
	const addProcessingDocument = useCallback(
		(jobId: string, fileName?: string) => {
			processingDocsRef.current.set(jobId, {
				jobId,
				fileName,
				startedAt: Date.now(),
			});

			// 폴링 시작 (아직 시작하지 않았다면)
			if (!intervalRef.current) {
				startPolling();
			}
		},
		[],
	);

	// 처리 중인 문서 제거
	const removeProcessingDocument = useCallback((jobId: string) => {
		processingDocsRef.current.delete(jobId);

		// 더 이상 처리 중인 문서가 없으면 폴링 중지
		if (processingDocsRef.current.size === 0 && intervalRef.current) {
			clearInterval(intervalRef.current);
			intervalRef.current = null;
		}
	}, []);

	// 폴링 시작
	const startPolling = useCallback(() => {
		if (intervalRef.current) return; // 이미 시작된 경우

		const pollDocuments = async () => {
			const processingDocs = Array.from(processingDocsRef.current.values());

			if (processingDocs.length === 0) {
				if (intervalRef.current) {
					clearInterval(intervalRef.current);
					intervalRef.current = null;
				}
				return;
			}

			// Promise.allSettled로 모든 문서 상태를 병렬로 확인
			const statusPromises = processingDocs.map(async (doc) => {
				try {
					const data = await documentApi.getDocumentStatus(doc.jobId);
					return { jobId: doc.jobId, data, error: null };
				} catch (error) {
					return { jobId: doc.jobId, data: null, error };
				}
			});

			const results = await Promise.allSettled(statusPromises);

			results.forEach((result, index) => {
				if (result.status === 'fulfilled' && result.value.data) {
					const { jobId, data } = result.value;

					// 완료 또는 실패한 문서는 폴링에서 제거
					if (data.status === 'COMPLETED' || data.status === 'FAILED') {
						removeProcessingDocument(jobId);

						// 교안 목록 갱신
						queryClient.invalidateQueries({
							queryKey: ['guardian', 'textbooks'],
						});
						queryClient.invalidateQueries({ queryKey: ['teacher'] });
					}
				}
			});
		};

		// 10초마다 폴링
		intervalRef.current = setInterval(pollDocuments, 10000);

		// 즉시 한 번 실행
		pollDocuments();
	}, [removeProcessingDocument, queryClient]);

	// 폴링 중지
	const stopPolling = useCallback(() => {
		if (intervalRef.current) {
			clearInterval(intervalRef.current);
			intervalRef.current = null;
		}
		processingDocsRef.current.clear();
	}, []);

	// 컴포넌트 언마운트 시 정리
	useEffect(() => {
		return () => {
			if (intervalRef.current) {
				clearInterval(intervalRef.current);
			}
		};
	}, []);

	return {
		addProcessingDocument,
		removeProcessingDocument,
		startPolling,
		stopPolling,
		getProcessingDocuments: () =>
			Array.from(processingDocsRef.current.values()),
		isPolling: () => intervalRef.current !== null,
	};
};
