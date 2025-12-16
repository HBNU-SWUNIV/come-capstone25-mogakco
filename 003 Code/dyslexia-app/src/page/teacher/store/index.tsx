import { Badge } from '@/shared/ui/badge';
import { Button } from '@/shared/ui/button';
import { Card, CardContent } from '@/shared/ui/card';
import { Typography } from '@/shared/ui/typography';

export default function StorePage() {
	const lessons = [
		{
			id: '1',
			title: '우리 동네 동물들',
			desc: '우리 주변의 동물들을 관찰하며 알아가는 교안입니다.',
			grade: '1-2학년',
			subject: '과학',
			price: '무료',
			rating: 4.8,
			reviews: 124,
			isNew: false,
			isPopular: true,
		},
		{
			id: '2',
			title: '우주 탐험 이야기',
			desc: '신비로운 우주를 탐험하며 과학적 호기심을 길러보는 교안입니다.',
			grade: '3-4학년',
			subject: '과학',
			price: '5,000원',
			rating: 4.9,
			reviews: 892,
			isNew: true,
			isPopular: true,
		},
		{
			id: '3',
			title: '마법의 숲 모험',
			desc: '다양한 동화 속 모험 이야기를 통해 상상력과 창의력을 기르는 교안입니다.',
			grade: '2-3학년',
			subject: '국어',
			price: '500원/14일',
			rating: 4.7,
			reviews: 567,
			isNew: false,
			isPopular: false,
		},
		{
			id: '4',
			title: '세계 여러 나라 이야기',
			desc: '다양한 문화를 배우며 글로벌 마인드를 기르는 교안입니다.',
			grade: '3-4학년',
			subject: '사회',
			price: '800원/14일',
			rating: 4.8,
			reviews: 345,
			isNew: true,
			isPopular: false,
		},
	];

	return (
		<div className="max-w-6xl mx-auto p-6 space-y-6">
			<div>
				<Typography variant="h3" className="font-semibold">
					교안 스토어
				</Typography>
				<Typography variant="p" className="text-muted-foreground">
					전문가가 제작한 검증된 교안을 찾아보세요
				</Typography>
			</div>

			<div className="flex flex-col sm:flex-row items-center gap-2">
				<input
					type="text"
					placeholder="교안 제목이나 내용으로 검색..."
					className="flex-1 border rounded px-3 py-2 text-sm"
				/>
				<select className="border rounded px-3 py-2 text-sm">
					<option>전체 학년</option>
					<option>1학년</option>
					<option>2학년</option>
				</select>
				<select className="border rounded px-3 py-2 text-sm">
					<option>전체 과목</option>
					<option>국어</option>
					<option>과학</option>
					<option>사회</option>
				</select>
			</div>

			<div className="space-y-2">
				<Typography variant="h4" className="font-semibold">
					인기 교안
				</Typography>
				<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
					{lessons
						.filter((l) => l.isPopular)
						.map((lesson) => (
							<Card
								key={lesson.id}
								className="bg-gradient-to-r from-blue-100 to-blue-200"
							>
								<CardContent className="p-4 space-y-2">
									<div className="flex justify-between items-center">
										<Typography variant="p" className="font-medium">
											{lesson.title}
										</Typography>
										{lesson.isNew && <Badge variant="blue">NEW</Badge>}
									</div>
									<Typography
										variant="p"
										className="text-sm text-muted-foreground"
									>
										{lesson.desc}
									</Typography>
									<div className="flex justify-between items-center text-sm text-gray-700">
										<span>{lesson.grade}</span>
										<span>{lesson.subject}</span>
									</div>
									<div className="flex justify-between items-center">
										<span>
											⭐ {lesson.rating} ({lesson.reviews})
										</span>
										<span>{lesson.price}</span>
									</div>
									<Button size="sm" className="w-full mt-2">
										{lesson.price === '무료' ? '내 보관함에 추가' : '구매하기'}
									</Button>
								</CardContent>
							</Card>
						))}
				</div>
			</div>

			<div className="space-y-2">
				<Typography variant="h4" className="font-semibold">
					새로 출시된 교안
				</Typography>
				<div className="grid grid-cols-1 sm:grid-cols-3 md:grid-cols-4 gap-4">
					{lessons
						.filter((l) => l.isNew)
						.map((lesson) => (
							<Card
								key={lesson.id}
								className="bg-gradient-to-r from-purple-100 to-pink-100"
							>
								<CardContent className="p-4 space-y-2">
									<Typography variant="p" className="font-medium">
										{lesson.title}
									</Typography>
									<Typography
										variant="p"
										className="text-sm text-muted-foreground"
									>
										{lesson.desc}
									</Typography>
									<div className="flex justify-between items-center text-sm text-gray-700">
										<span>{lesson.grade}</span>
										<span>{lesson.subject}</span>
									</div>
									<div className="flex justify-between items-center">
										<span>
											⭐ {lesson.rating} ({lesson.reviews})
										</span>
										<span>{lesson.price}</span>
									</div>
									<Button size="sm" className="w-full mt-2">
										{lesson.price === '무료' ? '내 보관함에 추가' : '구매하기'}
									</Button>
								</CardContent>
							</Card>
						))}
				</div>
			</div>

			<div className="space-y-2">
				<Typography variant="h4" className="font-semibold">
					전체 교안
				</Typography>
				<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
					{lessons.map((lesson) => (
						<Card key={lesson.id}>
							<CardContent className="p-4 space-y-2">
								<Typography variant="p" className="font-medium">
									{lesson.title}
								</Typography>
								<Typography
									variant="p"
									className="text-sm text-muted-foreground"
								>
									{lesson.desc}
								</Typography>
								<div className="flex justify-between items-center text-sm text-gray-700">
									<span>{lesson.grade}</span>
									<span>{lesson.subject}</span>
								</div>
								<div className="flex justify-between items-center">
									<span>
										⭐ {lesson.rating} ({lesson.reviews})
									</span>
									<span>{lesson.price}</span>
								</div>
								<Button size="sm" className="w-full mt-2">
									{lesson.price === '무료' ? '내 보관함에 추가' : '구매하기'}
								</Button>
							</CardContent>
						</Card>
					))}
				</div>
			</div>
		</div>
	);
}
