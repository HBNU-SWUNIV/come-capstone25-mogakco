import { Button } from '@/shared/ui/button';
import { Typography } from '@/shared/ui/typography';
import { useRouter } from '@tanstack/react-router';
import { useState } from 'react';

export default function Hero() {
	const router = useRouter();
	const [showDemo, setShowDemo] = useState(false);

	return (
		<section className="bg-white py-24 px-4 sm:px-8 w-full">
			<div className="max-w-6xl mx-auto text-center">
				<Typography
					as="h1"
					variant="h1"
					weight="bold"
					className="text-4xl sm:text-5xl text-primary mb-6 leading-tight"
				>
					리딩브릿지
				</Typography>

				<Typography
					as="h2"
					variant="h2"
					className="text-xl sm:text-2xl text-gray-700 mb-4 leading-relaxed"
				>
					난독증 학생들을 위한 맞춤형 학습 경험
				</Typography>

				<Typography
					variant="p"
					className="text-base sm:text-lg text-gray-600 mb-10 leading-relaxed max-w-2xl mx-auto"
				>
					보호자가 업로드한 PDF 교안을 AI로 변환하여 모든 학생이 쉽게 배울 수
					있도록 지원합니다
				</Typography>

				<div className="flex justify-center gap-4 mb-16 flex-wrap">
					<Button
						size="lg"
						variant="outline"
						className="text-base px-6 sm:px-8 py-3 border-primary text-primary hover:bg-primary hover:text-white rounded-lg"
						onClick={() => setShowDemo(true)}
					>
						체험해보기
					</Button>
					<Button
						size="lg"
						className="bg-primary hover:bg-primary/90 text-white text-base px-6 sm:px-8 py-3 rounded-lg"
						onClick={() => router.navigate({ to: '/signup' })}
					>
						무료로 시작하기
					</Button>
				</div>

				{!showDemo && (
					<div className="w-full flex justify-center">
						<div className="relative bg-gray-800 rounded-3xl p-4 shadow-2xl w-full max-w-4xl">
							<div className="bg-black rounded-2xl p-2">
								<div className="bg-white rounded-xl overflow-hidden aspect-[4/3]">
									<img
										src="/images/reading-preview.png"
										alt="리딩 예시 미리보기"
										className="w-full h-full object-cover"
									/>
								</div>
							</div>
						</div>
					</div>
				)}
			</div>
		</section>
	);
}
