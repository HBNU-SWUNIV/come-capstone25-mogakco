import { useAuth } from '@/shared/hooks/use-auth';
import { Card, CardContent } from '@/shared/ui/card';
import { Typography } from '@/shared/ui/typography';
import { Award, Clock, Star, Target } from 'lucide-react';
import { Book } from 'lucide-react';
import { useState } from 'react';
import LibraryView from './library';

export default function StudentDashboardPage() {
	const { my } = useAuth();
	const studentName = my?.name ?? '유저';

	const [todayStickers] = useState(3);
	const [todayProgress] = useState(65);
	const [todayPagesCompleted] = useState<[number, number]>([13, 20]);

	const recentPraises = [
		{
			id: 1,
			content:
				"오늘 '우리 동네 동물들' 책을 정말 열심히 읽었네요! 특히 강아지가 나오는 부분을 읽을 때 표정이 너무 밝았어요. 계속 이렇게 열심히 해주세요!",
			stickers: 3,
			date: '오늘',
			guardian: '엄마',
		},
		{
			id: 2,
			content:
				'어제 숙제를 끝까지 포기하지 않고 완성해서 정말 대단해요! 어려운 부분도 스스로 해결하려고 노력하는 모습이 훌륭했어요.',
			stickers: 2,
			date: '어제',
			guardian: '아빠',
		},
		{
			id: 3,
			content:
				'책 읽기 시간에 집중력이 정말 좋아졌어요. 10분 동안 한 번도 딴짓하지 않고 책에 집중하는 모습이 감동적이었어요!',
			stickers: 2,
			date: '2일 전',
			guardian: '엄마',
		},
	];

	return (
		<div className="min-h-screen bg-gray-50 p-6 max-w-5xl mx-auto space-y-8">
			<div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
				<Card className="lg:col-span-3 p-[1px] bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-2xl shadow-lg">
					<div className="bg-white rounded-2xl h-full">
						<CardContent className="p-6 flex items-center justify-between">
							<div>
								<Typography
									variant="h2"
									size="xl"
									weight="bold"
									className="text-gray-800"
								>
									안녕하세요, {studentName}님! 👋
								</Typography>
								<Typography variant="p" size="sm" className="text-gray-600">
									오늘도 즐거운 읽기 시간을 가져봐요
								</Typography>
							</div>
							<div className="text-center bg-yellow-50 rounded-2xl p-6">
								<div className="flex items-center justify-center mb-2 space-x-1">
									{Array.from(
										{ length: todayStickers },
										(_, i) => `today-star-${i}`,
									).map((starId) => (
										<Star
											key={starId}
											className="w-6 h-6 text-yellow-400 fill-current animate-pulse"
										/>
									))}
								</div>
								<Typography variant="p" className="text-gray-800 font-semibold">
									오늘의 칭찬 스티커
								</Typography>
							</div>
						</CardContent>
					</div>
				</Card>

				<Card className="rounded-2xl bg-gradient-to-br from-green-500 to-emerald-500 shadow-lg text-white flex items-center">
					<CardContent className="p-6 text-center w-full">
						<Target className="w-8 h-8 mb-2 mx-auto" />
						<Typography
							variant="h2"
							size="xl"
							weight="bold"
							className="text-white-600"
						>
							{todayProgress}%
						</Typography>
						<Typography variant="p" size="sm" className="text-white-600">
							오늘의 목표
						</Typography>
						<Typography variant="p" size="sm" className="text-white-600">
							{todayPagesCompleted[0]}/{todayPagesCompleted[1]} 페이지 완료
						</Typography>
					</CardContent>
				</Card>
			</div>

			<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
				<div className="space-y-4">
					<Typography
						variant="h2"
						size="lg"
						weight="semibold"
						className="text-gray-800"
					>
						나의 책들
					</Typography>
					<LibraryView />
				</div>

				<div className="space-y-4">
					<Typography
						variant="h2"
						size="lg"
						weight="semibold"
						className="text-gray-800"
					>
						최근 받은 칭찬 🌟
					</Typography>
					<div className="flex flex-col gap-4 max-h-[400px] overflow-y-auto">
						{recentPraises.map((praise) => (
							<Card
								key={praise.id}
								className="bg-yellow-50 rounded-2xl p-4 hover:shadow-lg transition transform hover:scale-[1.02] cursor-pointer"
								onClick={() => {
									//여긴 아직...
								}}
							>
								<CardContent className="p-0">
									<div className="flex items-start justify-between mb-2">
										<div className="flex items-center space-x-1">
											{Array.from(
												{ length: praise.stickers },
												(_, i) => `${praise.id}-star-${i}`,
											).map((starId) => (
												<Star
													key={starId}
													className="w-5 h-5 text-yellow-400"
												/>
											))}
										</div>
										<span className="text-xs text-gray-500">{praise.date}</span>
									</div>
									<Typography
										variant="p"
										size="sm"
										className="text-gray-700 mb-2 line-clamp-2"
									>
										{praise.content}
									</Typography>
									<div className="flex items-center justify-between">
										<span className="text-xs text-gray-600 bg-white px-2 py-1 rounded-full">
											{praise.guardian}
										</span>
										<Typography variant="p" size="sm" className="text-primary">
											자세히 보기 →
										</Typography>
									</div>
								</CardContent>
							</Card>
						))}
					</div>
				</div>
			</div>

			<section className="space-y-4">
				<Typography
					variant="h2"
					size="lg"
					weight="semibold"
					className="text-gray-800"
				>
					이번 주 성취
				</Typography>
				<Typography variant="p" size="sm" className="text-gray-500">
					열심히 노력한 결과를 확인해보세요
				</Typography>
				<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
					<Card className="bg-yellow-50 rounded-2xl p-6 flex flex-col items-center shadow-sm hover:shadow-md transition-shadow">
						<Book className="w-8 h-8 text-yellow-500 mb-2" />
						<Typography variant="p" size="sm" className="text-yellow-600">
							완료한 페이지
						</Typography>
						<Typography
							variant="h3"
							size="xl"
							weight="bold"
							className="text-yellow-600"
						>
							15페이지
						</Typography>
					</Card>
					<Card className="bg-green-50 rounded-2xl p-6 flex flex-col items-center shadow-sm hover:shadow-md transition-shadow">
						<Clock className="w-8 h-8 text-green-500 mb-2" />
						<Typography variant="p" size="sm" className="text-green-600">
							읽은 시간
						</Typography>
						<Typography
							variant="h3"
							size="xl"
							weight="bold"
							className="text-green-600"
						>
							2시간 30분
						</Typography>
					</Card>
					<Card className="bg-blue-50 rounded-2xl p-6 flex flex-col items-center shadow-sm hover:shadow-md transition-shadow">
						<Award className="w-8 h-8 text-blue-500 mb-2" />
						<Typography variant="p" size="sm" className="text-blue-600">
							받은 스티커
						</Typography>
						<Typography
							variant="h3"
							size="xl"
							weight="bold"
							className="text-blue-600"
						>
							12개
						</Typography>
					</Card>
				</div>
			</section>
		</div>
	);
}
