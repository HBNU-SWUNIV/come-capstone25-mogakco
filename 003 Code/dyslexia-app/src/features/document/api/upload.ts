import { axiosClient } from '@/shared/api/axios';

export interface DocumentUploadRequest {
	file: File;
}

export interface DocumentUploadResponse {
	jobId: string;
	message: string;
}

export interface DocumentStatusResponse {
	jobId: string;
	fileName: string;
	status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
	progress: number;
	errorMessage?: string;
	createdAt: string;
	completedAt?: string;
}

export const documentApi = {
	uploadDocument: async (
		formData: FormData,
	): Promise<DocumentUploadResponse> => {
		const res = await axiosClient.post<DocumentUploadResponse>(
			'/v1/documents',
			formData,
			{
				headers: {
					'Content-Type': 'multipart/form-data',
				},
			},
		);
		return res;
	},

	getDocumentStatus: async (jobId: string): Promise<DocumentStatusResponse> => {
		const res = await axiosClient.get<DocumentStatusResponse>(
			`/v1/documents/${jobId}/status`,
		);
		return res;
	},
};
