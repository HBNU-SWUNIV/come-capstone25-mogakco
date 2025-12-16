import { Card, CardContent } from '@/shared/ui/card';

export default function News() {
	const testimonials = [
		{
			title: "난독·경계선 학생 10배 늘었는데...예산 '빈토막'",
			subtitle: '전지역 예산 30-50% 삭감, 난독협회등록 치료사 부족',
			period: '25년 국내기사',
		},
		{
			title:
				'난독증 학생 서울시만 3년 새 8배 늘어..."예산 늘려 영유아기부터 치료해야"',
			subtitle: '난독학생이 2020년부터 2023년까지 958명으로 약 8.5배 ↑',
			period: '23년 국내기사',
		},
		{
			title: '늘어나는 난독·경계선 지능학생...조기 발견해야 치료 수월',
			subtitle: '아이들이 어른들의 게이를 못 받는 시간 증가',
			period: '23년 국내기사',
		},
	];

	return (
		<section className="py-16 px-4 sm:px-8">
			<div className="max-w-4xl mx-auto">
				<div className="space-y-6">
					{testimonials.map((t, idx) => (
						<Card key={idx} className="border-gray-200">
							<CardContent className="p-6">
								<div className="flex justify-between items-start">
									<div className="flex-1">
										<h4 className="font-semibold text-gray-900 mb-2 leading-relaxed">
											{t.title}
										</h4>
										<p className="text-primary text-sm mb-2 leading-relaxed">
											{t.subtitle}
										</p>
									</div>
									<span className="text-sm text-gray-500 ml-4">{t.period}</span>
								</div>
							</CardContent>
						</Card>
					))}
				</div>
			</div>
		</section>
	);
}
