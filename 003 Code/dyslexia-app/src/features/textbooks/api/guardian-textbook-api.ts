import { axiosClient } from '@/shared/api/axios';

export type ConvertProcessStatus =
	| 'PENDING'
	| 'PROCESSING'
	| 'COMPLETED'
	| 'FAILED';

export interface GuardianTextbookDto {
	id: number;
	guardianId?: number;
	title: string;
	pageCount: number;
	learnRate?: number;
	convertProcessStatus: ConvertProcessStatus;
	createdAt: string;
	updatedAt: string;
}

// API response wrapper per BE spec
export interface ApiResponse<T> {
	timestamp: string;
	code: number;
	message: string;
	result: T;
}

// Detail response (snake_case from BE)
export type ConvertStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
export interface TextbookDetail {
	textbook_id: number;
	textbook_name: string;
	total_pages: number;
	assigned_student_count: number;
	created_at: string;
	convert_status: ConvertStatus;
	original_file_name: string | null;
	// Quick analysis enrichment (optional)
	inferred_title?: string | null;
	subject?: string | null;
	topics?: string[];
	summary?: string | null;
	keywords?: string[];
	grade_range?: { min: number; max: number } | null;
	ai_confidence?: number | null;
	thumbnail_url?: string | null;
	analysis_status?:
		| 'PENDING'
		| 'PROCESSING'
		| 'ANALYZING'
		| 'THUMBNAIL'
		| 'COMPLETED'
		| 'FAILED';
}

// Internal: normalize camelCase/snake_case result to snake_case TextbookDetail
function normalizeTextbookDetail(input: unknown): TextbookDetail {
	const isSnake = (obj: any) =>
		obj && typeof obj === 'object' && 'textbook_id' in obj;
	const isCamel = (obj: any) =>
		obj && typeof obj === 'object' && 'textbookId' in obj;

	const pad2 = (n: number) => String(n).padStart(2, '0');
	const toLocalDateTimeString = (parts: number[]): string => {
		const [y, mo, d, h = 0, mi = 0, s = 0] = parts;
		return `${y}-${pad2(mo)}-${pad2(d)}T${pad2(h)}:${pad2(mi)}:${pad2(s)}`;
	};

	if (isSnake(input)) {
		return input as TextbookDetail;
	}
	if (isCamel(input)) {
		const obj = input as any;
		const createdAt = Array.isArray(obj.createdAt)
			? toLocalDateTimeString(obj.createdAt as number[])
			: String(obj.createdAt ?? '');
		return {
			textbook_id: obj.textbookId,
			textbook_name: obj.textbookName,
			total_pages: obj.totalPages,
			assigned_student_count: obj.assignedStudentCount,
			created_at: createdAt,
			convert_status: obj.convertStatus,
			original_file_name: obj.originalFileName ?? null,
			inferred_title: obj.inferredTitle ?? null,
			subject: obj.subject ?? null,
			topics: Array.isArray(obj.topics) ? obj.topics : [],
			summary: obj.summary ?? null,
			keywords: Array.isArray(obj.keywords) ? obj.keywords : [],
			grade_range: obj.gradeRange ?? null,
			ai_confidence: obj.aiConfidence ?? null,
			thumbnail_url: obj.thumbnailUrl ?? null,
			analysis_status: obj.analysisStatus ?? undefined,
		} satisfies TextbookDetail;
	}
	throw new Error('예상치 못한 교재 상세 응답 형식입니다.');
}

export const guardianTextbookApi = {
	listMyTextbooks: async (): Promise<GuardianTextbookDto[]> => {
		const data = (await axiosClient.get('/guardian/textbooks')) as unknown;
		// Be tolerant to both array and wrapped response shapes
		if (Array.isArray(data)) return data as GuardianTextbookDto[];
		// Some backends wrap in { result: [...] }
		if (
			data &&
			typeof data === 'object' &&
			Array.isArray((data as any).result)
		) {
			return (data as any).result as GuardianTextbookDto[];
		}
		// Some backends mistakenly return a single object
		if (data && typeof data === 'object') return [data as GuardianTextbookDto];
		return [];
	},

	// GET /guardian/textbooks/{textbookId}/detail
	getTextbookDetail: async (textbookId: number): Promise<TextbookDetail> => {
		const data = (await axiosClient.get(
			`/guardian/textbooks/${textbookId}/detail`,
		)) as unknown as ApiResponse<unknown> | unknown;

		if (data && typeof data === 'object' && 'result' in (data as any)) {
			const wrapped = data as ApiResponse<unknown>;
			if (wrapped.code === 1000 && wrapped.result) {
				return normalizeTextbookDetail(wrapped.result);
			}
			const msg =
				(wrapped as any)?.message ?? '교재 상세 정보를 불러오지 못했습니다.';
			throw new Error(msg);
		}

		return normalizeTextbookDetail(data);
	},
};
