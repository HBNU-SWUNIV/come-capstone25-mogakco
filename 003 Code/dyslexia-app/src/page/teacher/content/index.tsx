import { Button } from '@/components/ui/button';
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Route as ViewerRoute } from '@/routes/teacher/viewer/$documentId';
import { useNavigate } from '@tanstack/react-router';
import { Calendar, Eye, FileText, Search, Upload, Users } from 'lucide-react';
import { useState } from 'react';

export default function ContentManagePage() {
	const navigate = useNavigate();
	const [searchTerm, setSearchTerm] = useState('');

	const lessons = [
		{
			id: 1,
			title: '우리 동네 동물들',
			grade: '초등 1-2학년',
			uploadDate: '2024-01-15',
			assigned: 2,
			status: '완료',
			pageCount: 20,
			progress: 100,
			color: 'bg-orange-300',
		},
		{
			id: 2,
			title: '우주 탐험 이야기',
			grade: '초등 3-4학년',
			uploadDate: '2024-01-12',
			assigned: 1,
			status: '변환중',
			pageCount: 0,
			progress: 25,
			color: 'bg-blue-700',
		},
		{
			id: 3,
			title: '마법의 숲 모험',
			grade: '초등 1-2학년',
			uploadDate: '2024-01-10',
			assigned: 0,
			status: '완료',
			pageCount: 18,
			progress: 100,
			color: 'bg-green-400',
		},
	];

	const filteredLessons = lessons.filter((lesson) =>
		lesson.title.toLowerCase().includes(searchTerm.toLowerCase()),
	);

	return (
		<div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50 font-dyslexic">
			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
				<div className="flex items-center justify-between mb-8">
					<div>
						<h2 className="text-3xl font-bold text-gray-800">교안 보관함</h2>
						<p className="text-gray-600 mt-2">
							업로드한 교안을 관리하고 학생들에게 할당해보세요
						</p>
					</div>
					<Button className="bg-primary hover:bg-primary/90">
						<Upload className="w-4 h-4 mr-2" />새 교안 업로드
					</Button>
				</div>

				<div className="mb-6">
					<div className="relative max-w-md">
						<Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
						<Input
							placeholder="교안 제목으로 검색..."
							value={searchTerm}
							onChange={(e) => setSearchTerm(e.target.value)}
							className="pl-10"
						/>
					</div>
				</div>

				<div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
					{filteredLessons.map((lesson) => (
						<Card
							key={lesson.id}
							className="border-gray-200 hover:border-primary/30 hover:shadow-lg transition-all duration-300"
						>
							<CardHeader className="pb-4">
								<div
									className={`${lesson.color} h-32 rounded-lg mb-4 flex items-center justify-center relative`}
								>
									<div className="text-center text-white">
										<FileText className="w-8 h-8 mx-auto mb-2 opacity-80" />
										<p className="text-sm font-medium">
											{lesson.pageCount}페이지
										</p>
									</div>
									{lesson.status === '변환중' && (
										<div className="absolute inset-0 bg-black/50 rounded-lg flex flex-col items-center justify-center">
											<div className="text-white text-center w-full px-4">
												<p className="text-sm font-medium mb-2">변환 중...</p>
												<div className="w-full">
													<Progress
														value={lesson.progress}
														className="h-2 bg-white/20"
													/>
													<p className="text-xs mt-1">
														{Math.round(lesson.progress)}%
													</p>
												</div>
											</div>
										</div>
									)}
								</div>
								<div className="flex items-center justify-between">
									<div className="flex-1">
										<CardTitle className="text-lg leading-tight">
											{lesson.title}
										</CardTitle>
										<CardDescription className="mt-1">
											{lesson.grade}
										</CardDescription>
									</div>
									<span
										className={`px-2 py-1 rounded-full text-xs font-medium ${lesson.status === '완료' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}
									>
										{lesson.status === '완료' ? '변환 완료' : '변환 중'}
									</span>
								</div>
							</CardHeader>
							<CardContent className="space-y-4 text-sm">
								<div className="space-y-2">
									<div className="flex items-center justify-between">
										<div className="flex items-center space-x-1 text-gray-600">
											<Calendar className="w-3 h-3" />
											<span>업로드</span>
										</div>
										<span className="text-gray-800">{lesson.uploadDate}</span>
									</div>
									<div className="flex items-center justify-between">
										<div className="flex items-center space-x-1 text-gray-600">
											<Users className="w-3 h-3" />
											<span>할당된 학생</span>
										</div>
										<span className="text-gray-800">{lesson.assigned}명</span>
									</div>
								</div>
								<div className="flex space-x-2">
									<Button
										onClick={() =>
											navigate({
												to: ViewerRoute.id,
												params: { documentId: String(lesson.id) },
											})
										}
										variant="outline"
										className="flex-1"
										disabled={lesson.status !== '완료'}
									>
										<Eye className="w-4 h-4 mr-1" />
										미리보기
									</Button>
									<Button
										variant="outline"
										className="flex-1"
										disabled={lesson.status !== '완료'}
									>
										<Users className="w-4 h-4 mr-1" />
										할당
									</Button>
								</div>
							</CardContent>
						</Card>
					))}
				</div>

				{filteredLessons.length === 0 && (
					<Card className="border-dashed border-2 border-gray-300 mt-8">
						<CardContent className="p-12 text-center">
							<FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
							<h3 className="text-xl font-semibold text-gray-600 mb-2">
								검색 결과가 없습니다
							</h3>
							<p className="text-gray-500 mb-4">
								"{searchTerm}"와 일치하는 교안을 찾을 수 없습니다
							</p>
							<Button className="bg-primary hover:bg-primary/90">
								<Upload className="w-4 h-4 mr-2" />
								교안 업로드하기
							</Button>
						</CardContent>
					</Card>
				)}
			</div>
		</div>
	);
}
