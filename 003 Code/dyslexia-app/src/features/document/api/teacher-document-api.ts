import { axiosClient } from '@/shared/api/axios';

export type TeacherDocumentStatus = 'CREATING' | 'FAILED' | 'CREATED';

export interface TeacherDocumentSummaryDto {
	textbookId: number;
	title: string;
	createdAt: string;
	status: TeacherDocumentStatus;
	thumbnailUrl: string | null;
	assignedStudentsCount: number;
}

export interface TeacherDocumentSummaryListResponseDto {
	success: boolean;
	message: string;
	documents: TeacherDocumentSummaryDto[];
}

export const teacherDocumentApi = {
	list: async (
		teacherId: number,
	): Promise<TeacherDocumentSummaryListResponseDto> => {
		return (await axiosClient.get(
			`/teacher/documents/${teacherId}`,
		)) as unknown as TeacherDocumentSummaryListResponseDto;
	},
};
