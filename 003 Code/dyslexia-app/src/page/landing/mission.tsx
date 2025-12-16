import { Card, CardContent } from '@/shared/ui/card';
import { Type as FileText, Heart, Star, Users } from 'lucide-react';

export default function Mission() {
	const features = [
		{
			icon: <FileText className="w-6 h-6 text-primary" />,
			title: 'AI 맞춤 변환',
			description: 'PDF를 난독증 친화적인 디지털 교안으로 자동 변환해요',
		},
		{
			icon: <Heart className="w-6 h-6 text-warm-500" />,
			title: '읽기 자신감',
			description: 'TTS, 폰트 조절 등으로 아이만의 속도로 학습할 수 있어요',
		},
		{
			icon: <Star className="w-6 h-6 text-yellow-500" />,
			title: 'AI 학습 친구',
			description: '그림을 그리면 AI 친구가 살아 움직이며 반응해요',
		},
		{
			icon: <Users className="w-6 h-6 text-soft-500" />,
			title: '학습 관리',
			description: '보호자에게 상세한 학습 분석 리포트를 제공해요',
		},
	];

	return (
		<section className="py-16 px-4 sm:px-8 bg-gray-50">
			<div className="max-w-6xl mx-auto">
				<h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
					모든 학생은 배울 권리가 있습니다.
				</h3>
				<div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
					{features.map((feature, index) => (
						<Card
							key={index}
							className="border-gray-200 hover:shadow-md transition-shadow"
						>
							<CardContent className="p-6 text-center">
								<div className="flex justify-center mb-4">{feature.icon}</div>
								<h4 className="font-semibold text-gray-800 mb-2">
									{feature.title}
								</h4>
								<p className="text-sm text-gray-600 leading-relaxed">
									{feature.description}
								</p>
							</CardContent>
						</Card>
					))}
				</div>
			</div>
		</section>
	);
}
