import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { Send, User } from 'lucide-react';
import { useState } from 'react';

interface Student {
	id: number;
	name: string;
	grade: string;
	status: string;
	lastActivity: string;
}

interface DocumentAssignModalProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	documentTitle: string;
	students?: Student[];
}

const DocumentAssignModal = ({
	open,
	onOpenChange,
	documentTitle,
	students = [],
}: DocumentAssignModalProps) => {
	const { toast } = useToast();
	const [assigningStudents, setAssigningStudents] = useState<Set<number>>(
		new Set(),
	);

	// Mock students data if not provided
	const mockStudents: Student[] = [
		{
			id: 1,
			name: '민지',
			grade: '초등학교 2학년',
			status: 'active',
			lastActivity: '2시간 전',
		},
		{
			id: 2,
			name: '준호',
			grade: '초등학교 1학년',
			status: 'needs_attention',
			lastActivity: '1일 전',
		},
		{
			id: 3,
			name: '서연',
			grade: '초등학교 3학년',
			status: 'active',
			lastActivity: '30분 전',
		},
	];

	const studentList = students.length > 0 ? students : mockStudents;

	const handleAssignDocument = async (
		studentId: number,
		studentName: string,
	) => {
		setAssigningStudents((prev) => new Set(prev).add(studentId));

		try {
			// Simulate API call
			await new Promise((resolve) => setTimeout(resolve, 1000));

			toast({
				title: '교안이 전달되었습니다! 📚',
				description: `${studentName}에게 "${documentTitle}" 교안을 성공적으로 전달했습니다.`,
			});

			console.log(
				`Document "${documentTitle}" assigned to student ${studentName} (ID: ${studentId})`,
			);
		} catch (error) {
			toast({
				title: '전달 실패',
				description: '교안 전달 중 오류가 발생했습니다. 다시 시도해주세요.',
				variant: 'destructive',
			});
		} finally {
			setAssigningStudents((prev) => {
				const newSet = new Set(prev);
				newSet.delete(studentId);
				return newSet;
			});
		}
	};

	const getStatusColor = (status: string) => {
		switch (status) {
			case 'active':
				return 'bg-green-100 text-green-700';
			case 'needs_attention':
				return 'bg-yellow-100 text-yellow-700';
			default:
				return 'bg-gray-100 text-gray-700';
		}
	};

	const getStatusText = (status: string) => {
		switch (status) {
			case 'active':
				return '활발';
			case 'needs_attention':
				return '관심 필요';
			default:
				return '일반';
		}
	};

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden">
				<DialogHeader>
					<DialogTitle className="text-xl font-bold">교안 할당</DialogTitle>
					<DialogDescription className="text-base">
						"<span className="font-medium text-gray-800">{documentTitle}</span>"
						교안을 할당할 학생을 선택해주세요
					</DialogDescription>
				</DialogHeader>

				<div className="overflow-y-auto max-h-[60vh] pr-2">
					<div className="space-y-4">
						{studentList.map((student) => (
							<Card
								key={student.id}
								className="border-gray-200 hover:border-primary/30 transition-colors"
							>
								<CardContent className="p-4">
									<div className="flex items-center justify-between">
										<div className="flex items-center space-x-4">
											<div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
												<User className="w-6 h-6 text-white" />
											</div>
											<div className="flex-1">
												<h3 className="font-semibold text-gray-900 text-lg">
													{student.name}
												</h3>
												<p className="text-sm text-gray-600 mb-1">
													{student.grade}
												</p>
												<div className="flex items-center space-x-2">
													<Badge
														variant="outline"
														className={`text-xs ${getStatusColor(student.status)}`}
													>
														{getStatusText(student.status)}
													</Badge>
													<span className="text-xs text-gray-500">
														마지막 활동: {student.lastActivity}
													</span>
												</div>
											</div>
										</div>

										<Button
											onClick={() =>
												handleAssignDocument(student.id, student.name)
											}
											disabled={assigningStudents.has(student.id)}
											className="ml-4"
										>
											{assigningStudents.has(student.id) ? (
												<>전달 중...</>
											) : (
												<>
													<Send className="w-4 h-4 mr-2" />
													전달하기
												</>
											)}
										</Button>
									</div>
								</CardContent>
							</Card>
						))}

						{studentList.length === 0 && (
							<div className="text-center py-8">
								<User className="w-12 h-12 text-gray-400 mx-auto mb-4" />
								<p className="text-gray-500">등록된 학생이 없습니다.</p>
								<p className="text-sm text-gray-400 mt-1">
									먼저 학생을 초대해주세요.
								</p>
							</div>
						)}
					</div>
				</div>
			</DialogContent>
		</Dialog>
	);
};

export default DocumentAssignModal;
