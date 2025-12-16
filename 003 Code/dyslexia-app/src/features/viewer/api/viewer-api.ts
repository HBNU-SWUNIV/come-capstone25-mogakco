import { axiosClient } from '@/shared/api/axios';
import type {
	Document,
	PageContentDto,
	PageImageResponse,
	PageTipResponse,
} from '../model/types';

export const viewerApi = {
	// Note: Document metadata endpoint not defined in current OpenAPI (docs/api.json)
	// Keeping signature for compatibility; no current usage in code.
	getDocument: async (documentId: number): Promise<Document> => {
		return await axiosClient.get(`/documents/${documentId}`);
	},

	// Fetch textbook pages (GET /textbooks/pages) and return data.result as-is
	getPageContent: async (
		documentId: number,
		pageNumber?: number,
	): Promise<PageContentDto[]> => {
		const params = pageNumber
			? { textbookId: documentId, page: pageNumber }
			: { textbookId: documentId };

		const data = (await axiosClient.get('/textbooks/pages', {
			params,
		})) as unknown as any;
		return (data?.result ?? []) as PageContentDto[];
	},

	// Page tips endpoint for textbook pages
	getPageTips: async (pageId: number): Promise<PageTipResponse[]> => {
		const data = (await axiosClient.get(
			`/textbooks/pages/${pageId}/tips`,
		)) as unknown as any;
		if (Array.isArray(data)) return data as PageTipResponse[];
		if (data && typeof data === 'object' && Array.isArray(data.result))
			return data.result as PageTipResponse[];
		return [];
	},

	// Not defined in current spec for textbooks; keeping for compatibility if needed
	getPageImages: async (pageId: number): Promise<PageImageResponse[]> => {
		const data = (await axiosClient.get(
			`/document-contents/pages/${pageId}/images`,
		)) as unknown as any;
		if (Array.isArray(data)) return data as PageImageResponse[];
		if (data && typeof data === 'object' && Array.isArray(data.result))
			return data.result as PageImageResponse[];
		return [];
	},
};
