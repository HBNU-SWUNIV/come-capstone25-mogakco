import { Button } from '@/shared/ui/button';
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from '@/shared/ui/card';
import { ProgressBar } from '@/shared/ui/progress-bar';
import { Typography } from '@/shared/ui/typography';
import { useNavigate } from '@tanstack/react-router';
import { BookOpen, Calendar, Clock, Eye, Plus, Users } from 'lucide-react';
import { useState } from 'react';

export default function StudentManagementPage() {
	const navigate = useNavigate();
	const [students] = useState([
		{
			id: 1,
			name: '김민지',
			age: 8,
			profileColor: 'bg-orange-200',
			totalProgress: 65,
			lastActivity: '2일 전',
			documentsAssigned: 3,
			totalReadingTime: '2시간 30분',
			averageScore: 85,
			completedDocuments: 2,
		},
		{
			id: 2,
			name: '이준호',
			age: 10,
			profileColor: 'bg-green-200',
			totalProgress: 45,
			lastActivity: '1일 전',
			documentsAssigned: 2,
			totalReadingTime: '1시간 45분',
			averageScore: 78,
			completedDocuments: 1,
		},
	]);

	return (
		<div className="min-h-screen bg-gray-50 font-dyslexic">
			<div className="max-w-7xl mx-auto p-6 space-y-6">
				<div className="flex items-center justify-between">
					<div>
						<Typography
							variant="h3"
							className="text-3xl font-bold text-gray-800"
						>
							학생 관리
						</Typography>
						<Typography variant="p" className="text-gray-600 mt-1">
							등록된 학생들의 학습 현황을 관리하고 분석해보세요
						</Typography>
					</div>
					<Button
						type="button"
						variant="outline"
						size="sm"
						onClick={() => navigate({ to: '/teacher/dashboard' })}
					>
						<Plus className="w-4 h-4 mr-2" />
						학생 초대하기
					</Button>
				</div>

				<div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
					{students.map((student) => (
						<Card
							key={student.id}
							className="border border-gray-200 rounded-2xl hover:border-primary/30 hover:shadow-lg transition-all duration-300"
						>
							<CardHeader className="flex items-center space-x-4 pb-4">
								<div
									className={`${student.profileColor} w-16 h-16 rounded-full flex items-center justify-center`}
								>
									<Users className="w-8 h-8 text-white" />
								</div>
								<div className="flex-1">
									<CardTitle className="text-xl">{student.name}</CardTitle>
									<CardDescription>{student.age}세</CardDescription>
								</div>
							</CardHeader>

							<CardContent className="space-y-4">
								<div>
									<div className="flex items-center justify-between text-sm text-gray-600 mb-2">
										<span>전체 진행률</span>
										<span className="font-medium text-primary">
											{student.totalProgress}%
										</span>
									</div>
									<ProgressBar
										progress={student.totalProgress}
										className="h-2"
									/>
								</div>

								<div className="grid grid-cols-2 gap-3 text-sm">
									<div className="bg-blue-50 p-3 rounded-lg text-center">
										<div className="font-medium text-blue-700">평균 점수</div>
										<div className="text-blue-600">
											{student.averageScore}점
										</div>
									</div>
									<div className="bg-green-50 p-3 rounded-lg text-center">
										<div className="font-medium text-green-700">완료 교안</div>
										<div className="text-green-600">
											{student.completedDocuments}권
										</div>
									</div>
								</div>

								<div className="space-y-2 text-xs text-gray-500 border-t pt-3">
									<div className="flex items-center justify-between">
										<div className="flex items-center space-x-1">
											<Calendar className="w-3 h-3" />
											<span>최근 활동</span>
										</div>
										<span>{student.lastActivity}</span>
									</div>
									<div className="flex items-center justify-between">
										<div className="flex items-center space-x-1">
											<BookOpen className="w-3 h-3" />
											<span>할당 교안</span>
										</div>
										<span>{student.documentsAssigned}권</span>
									</div>
									<div className="flex items-center justify-between">
										<div className="flex items-center space-x-1">
											<Clock className="w-3 h-3" />
											<span>총 학습시간</span>
										</div>
										<span>{student.totalReadingTime}</span>
									</div>
								</div>

								<Button
									type="button"
									variant="outline"
									size="sm"
									className="w-full mt-4"
									onClick={() =>
										navigate({ to: `/teacher/student/${student.id}/analytics` })
									}
								>
									<Eye className="w-4 h-4 mr-2" />
									상세 분석 보기
								</Button>
							</CardContent>
						</Card>
					))}
				</div>

				{students.length === 0 && (
					<Card className="border-dashed border-2 border-gray-300">
						<CardContent className="p-12 text-center">
							<Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
							<h3 className="text-xl font-semibold text-gray-600 mb-2">
								아직 등록된 학생이 없습니다
							</h3>
							<p className="text-gray-500 mb-4">
								학생을 초대하여 학습 관리를 시작해보세요
							</p>
							<Button
								type="button"
								onClick={() => navigate({ to: '/teacher/dashboard' })}
							>
								<Plus className="w-4 h-4 mr-2" />
								학생 초대하기
							</Button>
						</CardContent>
					</Card>
				)}
			</div>
		</div>
	);
}
