import { axiosClient } from '@/shared/api/axios';
import type {
	VocabularyAnalysis,
	VocabularyAnalysisSearchRequest,
} from '@/shared/api/types';

// Server payload (snake_case) as per new spec
interface ServerVocabularyAnalysis {
	id: number;
	// both camelCase and snake_case possible from backend
	textbook_id?: number;
	textbookId?: number;
	page_number?: number;
	pageNumber?: number;
	block_id?: string;
	blockId?: string;
	word: string;
	start_index?: number;
	startIndex?: number;
	end_index?: number;
	endIndex?: number;
	definition?: string;
	simplified_definition?: string;
	simplifiedDefinition?: string;
	examples?: string;
	difficulty_level?: string;
	difficultyLevel?: string;
	reason?: string;
	grade_level?: number | null;
	gradeLevel?: number | null;
	phoneme_analysis_json?: string | null;
	phonemeAnalysisJson?: string | null;
	created_at?: string;
	createdAt?: string;
}

interface ServerSearchResponse {
	timestamp: string;
	code: number;
	message: string;
	result: ServerVocabularyAnalysis[];
}

function normalizeItem(
	item: ServerVocabularyAnalysis,
	documentId: number,
): VocabularyAnalysis {
	const pageNumber = item.pageNumber ?? item.page_number ?? 0;
	const blockId = item.blockId ?? item.block_id ?? '';
	const startIndex = item.startIndex ?? item.start_index ?? 0;
	const endIndex = item.endIndex ?? item.end_index ?? 0;
	const simplifiedDefinition =
		item.simplifiedDefinition ?? item.simplified_definition ?? '';
	const difficultyLevel =
		item.difficultyLevel ?? item.difficulty_level ?? 'medium';
	const gradeLevel = item.gradeLevel ?? item.grade_level ?? 0;
	const phonemeAnalysisJson =
		item.phonemeAnalysisJson ?? item.phoneme_analysis_json ?? '';
	const createdAt = item.createdAt ?? item.created_at ?? '';

	return {
		id: item.id,
		documentId,
		pageNumber,
		blockId,
		word: item.word,
		startIndex,
		endIndex,
		definition: item.definition ?? '',
		simplifiedDefinition,
		examples: item.examples ?? '',
		difficultyLevel,
		reason: item.reason ?? '',
		gradeLevel: gradeLevel ?? 0,
		phonemeAnalysisJson,
		createdAt,
		originalSentence: '',
	};
}

export const vocabularyAnalysisApi = {
	async search(
		params: VocabularyAnalysisSearchRequest,
	): Promise<VocabularyAnalysis[]> {
		const data = (await axiosClient.post(
			'/vocabulary-analysis/search',
			params,
		)) as ServerSearchResponse | ServerVocabularyAnalysis[] | null | undefined;

		const list: ServerVocabularyAnalysis[] = Array.isArray(data)
			? data
			: (data?.result ?? []);

		if (!Array.isArray(list) || list.length === 0) return [];

		const sourceId = (params.documentId ?? params.textbookId ?? 0) as number;
		return list.map((item) => normalizeItem(item, sourceId));
	},

	async debugTextbookLookup(documentId: number) {
		return axiosClient.get(`/vocabulary-analysis/debug/textbook/${documentId}`);
	},
};
