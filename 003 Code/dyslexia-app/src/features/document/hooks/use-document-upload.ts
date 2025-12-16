import { useMutation, useQuery } from '@tanstack/react-query';
import { type DocumentUploadResponse, documentApi } from '../api/upload';

export const useDocumentUpload = () => {
	return useMutation({
		mutationFn: async (formData: FormData): Promise<DocumentUploadResponse> => {
			const response = await documentApi.uploadDocument(formData);
			return response;
		},
	});
};

export const useDocumentStatus = (jobId: string, enabled: boolean) => {
	return useQuery({
		queryKey: ['document-status', jobId],
		queryFn: () => documentApi.getDocumentStatus(jobId),
		enabled,
		refetchInterval: (data) => {
			const status = data?.status;
			if (status === 'COMPLETED' || status === 'FAILED') {
				return false; // 폴링 중단
			}
			return 2000; // 2초 간격 폴링
		},
		retry: 3,
		retryDelay: 1000,
	});
};
