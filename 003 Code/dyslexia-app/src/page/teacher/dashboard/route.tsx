import PraiseModal from '@/components/PraiseModal';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { useQuery } from '@tanstack/react-query';
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import clsx from 'clsx';
import {
	BarChart3,
	BookOpen,
	Clock,
	Plus,
	Star,
	TrendingUp,
	Upload,
	UserPlus,
	Users,
} from 'lucide-react';
import { useState } from 'react';
import StudentInviteModal from './invite-modal';

interface Student {
	id: number;
	name: string;
	grade: keyof typeof gradeMap | string;
	currentBook: string;
	progress: number;
	status: 'active' | 'needs_attention';
	lastActivity: string;
}

const gradeMap = {
	GRADE_1: '초등학교 1학년',
	GRADE_2: '초등학교 2학년',
	GRADE_3: '초등학교 3학년',
	GRADE_4: '초등학교 4학년',
	GRADE_5: '초등학교 5학년',
	GRADE_6: '초등학교 6학년',
} as const;

export const Route = createFileRoute('/teacher/dashboard')({
	component: GuardianDashboardPage,
});

async function fetchStudents(): Promise<Student[]> {
	const token = localStorage.getItem('accessToken');
	if (!token) {
		throw new Error('토큰이 없습니다');
	}

	const res = await fetch(
		`${import.meta.env.VITE_API_BASE_URL}/guardian/students`,
		{
			headers: {
				Authorization: `Bearer ${token}`,
				'Content-Type': 'application/json',
			},
		},
	);

	if (!res.ok) {
		throw new Error(`API 오류: ${res.status}`);
	}

	const json = await res.json();
	return json.result || [];
}

function GuardianDashboardPage() {
	const navigate = useNavigate();
	const { toast } = useToast();

	const {
		data: students = [],
		error,
		isLoading,
	} = useQuery({
		queryKey: ['guardian-students'],
		queryFn: fetchStudents,
		retry: 0, // 재시도 하지 않음
		refetchOnWindowFocus: false, // 윈도우 포커스 시 재요청 방지
	});
	const [recentActivities] = useState([
		{
			id: 1,
			student: '민지',
			description: '독서 목표 달성',
			time: '30분 전',
			icon: Star,
		},
		{
			id: 2,
			student: '준호',
			description: '새 교안 배정: 마법의 숲 모험',
			time: '2시간 전',
			icon: BookOpen,
		},
		{
			id: 3,
			student: '민지',
			description: '학습 진도 80% 달성',
			time: '4시간 전',
			icon: TrendingUp,
		},
	]);
	const [recentDocuments] = useState([
		{
			id: 1,
			title: '우리 동네 동물들',
			type: '자체 제작',
			uploadDate: '2024-01-15',
			status: 'processing',
		},
		{
			id: 2,
			title: '우주 탐험 이야기',
			type: '스토어 구매',
			uploadDate: '2024-01-10',
			status: 'completed',
		},
	]);

	const [isPraiseModalOpen, setIsPraiseModalOpen] = useState(false);
	const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
	const [selectedStudent, setSelectedStudent] = useState<{
		id: number;
		name: string;
	} | null>(null);

	// 에러가 발생한 경우 콘솔에 로그 출력
	if (error) {
		console.error('학생 목록 조회 오류:', error);
	}

	const handlePraiseStudent = (id: number, name: string) => {
		setSelectedStudent({ id, name });
		setIsPraiseModalOpen(true);
	};

	const handleSavePraise = (_: string, stickers: number) => {
		toast({
			title: '칭찬이 전달되었습니다! ⭐',
			description: `${selectedStudent?.name}에게 ${stickers}개의 스티커와 함께 칭찬을 보냈습니다.`,
		});
	};

	return (
		<div className="min-h-screen bg-gradient-to-br from-blue-25 via-indigo-25 to-purple-25">
			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
				<div className="mb-8">
					<h1 className="text-3xl font-bold text-gray-900 mb-2">대시보드</h1>
					<p className="text-gray-600">
						학생들의 학습 현황을 한눈에 확인하세요
					</p>
				</div>

				<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
					<Card
						className="hover:shadow-lg transition-shadow cursor-pointer"
						onClick={() => navigate({ to: '/teacher/content' })}
					>
						<CardContent className="p-6 flex items-center">
							<div className="p-3 bg-blue-100 rounded-lg">
								<Upload className="w-6 h-6 text-blue-600" />
							</div>
							<div className="ml-4 flex-1">
								<h3 className="font-semibold text-gray-900">새 교안 업로드</h3>
								<p className="text-sm text-gray-600">
									PDF를 업로드하여 AI 변환
								</p>
							</div>
							<Button size="sm" className="ml-auto">
								업로드
							</Button>
						</CardContent>
					</Card>

					<Card
						className="hover:shadow-lg transition-shadow cursor-pointer"
						onClick={() => setIsInviteModalOpen(true)}
					>
						<CardContent className="p-6 flex items-center">
							<div className="p-3 bg-green-100 rounded-lg">
								<UserPlus className="w-6 h-6 text-green-600" />
							</div>
							<div className="ml-4 flex-1">
								<h3 className="font-semibold text-gray-900">학생 초대</h3>
								<p className="text-sm text-gray-600">새로운 학생을 초대</p>
							</div>
							<Button size="sm" variant="outline" className="ml-auto">
								링크 복사
							</Button>
						</CardContent>
					</Card>

					<Card
						className="hover:shadow-lg transition-shadow cursor-pointer"
						onClick={() => navigate({ to: '/teacher/student' })}
					>
						<CardContent className="p-6 flex items-center">
							<div className="p-3 bg-orange-100 rounded-lg">
								<BarChart3 className="w-6 h-6 text-orange-600" />
							</div>
							<div className="ml-4 flex-1">
								<h3 className="font-semibold text-gray-900">학습 분석</h3>
								<p className="text-sm text-gray-600">상세 학습 데이터 확인</p>
							</div>
							<Button size="sm" variant="outline" className="ml-auto">
								분석
							</Button>
						</CardContent>
					</Card>
				</div>
				<div className="grid lg:grid-cols-3 gap-8">
					<div className="lg:col-span-2 space-y-6">
						<Card>
							<CardHeader>
								<CardTitle className="flex items-center space-x-2">
									<Clock className="w-5 h-5" />
									<span>최근 활동</span>
								</CardTitle>
							</CardHeader>
							<CardContent>
								<div className="space-y-4">
									{recentActivities.map(
										({ id, student, description, time, icon: Icon }) => (
											<div
												key={id}
												className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
											>
												<div className="p-2 bg-white rounded-lg shadow-sm">
													<Icon className="w-4 h-4 text-gray-600" />
												</div>
												<div className="flex-1 min-w-0">
													<div className="flex items-center space-x-2">
														<Badge className="text-xs bg-green-100 text-green-800 px-2 py-0.5">
															{student}
														</Badge>
														<span className="text-xs text-gray-500">
															{time}
														</span>
													</div>
													<p className="text-sm text-gray-900 mt-1">
														{description}
													</p>
												</div>
											</div>
										),
									)}
								</div>
							</CardContent>
						</Card>

						<Card>
							<CardHeader className="flex justify-between items-center">
								<CardTitle className="flex items-center space-x-2">
									<Users className="w-5 h-5" />
									<span>학생 현황</span>
								</CardTitle>
								<Button
									variant="outline"
									size="sm"
									onClick={() => navigate({ to: '/teacher/student' })}
								>
									전체 보기
								</Button>
							</CardHeader>
							<CardContent className="space-y-6">
								{isLoading ? (
									<p className="text-sm text-gray-500">로딩 중...</p>
								) : error ? (
									<p className="text-sm text-red-500">
										학생 목록을 불러올 수 없습니다
									</p>
								) : students.length === 0 ? (
									<p className="text-sm text-gray-500">
										연결된 학생이 없습니다
									</p>
								) : (
									students.map((stu) => (
										<div
											key={stu.id}
											className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
										>
											<div className="flex items-center space-x-4">
												<div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
													<span className="text-white font-semibold">
														{stu.name.charAt(0)}
													</span>
												</div>
												<div>
													<h3 className="font-semibold text-gray-900">
														{stu.name}
													</h3>
													<p className="text-sm text-gray-600">
														{(gradeMap as Record<string, string>)[stu.grade] ??
															stu.grade}
													</p>
													<p className="text-sm text-gray-500">
														현재 도서: {stu.currentBook}
													</p>
												</div>
											</div>
											<div className="text-right space-y-2">
												<div className="flex items-center space-x-2">
													<Badge
														className={clsx(
															stu.status === 'active'
																? 'bg-blue-100 text-blue-800'
																: 'bg-gray-100 text-gray-600',
															'text-xs px-2 py-0.5',
														)}
													>
														{stu.status === 'active' ? '활발' : '관심 필요'}
													</Badge>
													<Button
														size="sm"
														variant="outline"
														onClick={() =>
															handlePraiseStudent(stu.id, stu.name)
														}
														className="border-yellow-400 text-yellow-600 hover:bg-yellow-50"
													>
														<Star className="w-4 h-4 mr-1" /> 칭찬하기
													</Button>
												</div>
												<div className="flex items-center space-x-2">
													<div className="w-24">
														<Progress value={stu.progress} className="h-2" />
													</div>
													<span className="text-sm font-medium">
														{stu.progress}%
													</span>
												</div>
												<p className="text-xs text-gray-500">
													마지막 활동: {stu.lastActivity}
												</p>
											</div>
										</div>
									))
								)}
							</CardContent>
						</Card>
					</div>

					<div className="space-y-6">
						<Card>
							<CardHeader>
								<CardTitle>빠른 작업</CardTitle>
							</CardHeader>
							<CardContent className="space-y-3">
								<Button
									className="w-full justify-start"
									onClick={() => navigate({ to: '/teacher/content' })}
								>
									<Plus className="w-4 h-4 mr-2" /> 새 교안 업로드
								</Button>
								<Button
									variant="outline"
									className="w-full justify-start"
									onClick={() => navigate({ to: '/teacher/student' })}
								>
									<Users className="w-4 h-4 mr-2" /> 학생 관리
								</Button>
							</CardContent>
						</Card>

						<Card>
							<CardHeader className="flex justify-between items-center">
								<CardTitle className="flex items-center space-x-2">
									<BookOpen className="w-5 h-5" /> <span>최근 교안</span>
								</CardTitle>
								<Button
									variant="outline"
									size="sm"
									onClick={() => navigate({ to: '/teacher/content' })}
								>
									전체 보기
								</Button>
							</CardHeader>
							<CardContent className="space-y-3">
								{recentDocuments.map((doc) => (
									<div
										key={doc.id}
										className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
									>
										<div>
											<p className="font-medium text-sm">{doc.title}</p>
											<div className="flex items-center space-x-2 mt-1">
												<Badge variant="outline" className="text-xs">
													{doc.type}
												</Badge>
												<span className="text-xs text-gray-500">
													{doc.uploadDate}
												</span>
											</div>
										</div>
										<Badge
											className={clsx(
												doc.status === 'completed'
													? 'bg-blue-100 text-blue-800'
													: 'bg-gray-100 text-gray-700',
												'text-xs',
											)}
										>
											{doc.status === 'completed' ? '완료' : '처리중'}
										</Badge>
									</div>
								))}
							</CardContent>
						</Card>
					</div>
				</div>
			</div>

			<PraiseModal
				isOpen={isPraiseModalOpen}
				onClose={() => setIsPraiseModalOpen(false)}
				onSavePraise={handleSavePraise}
				studentName={selectedStudent?.name}
			/>
			<StudentInviteModal
				isOpen={isInviteModalOpen}
				onClose={() => setIsInviteModalOpen(false)}
			/>
		</div>
	);
}

export default GuardianDashboardPage;
