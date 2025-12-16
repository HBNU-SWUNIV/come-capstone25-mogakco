import { Button } from '@/shared/ui/button';
import { Typography } from '@/shared/ui/typography';
import { useRouter } from '@tanstack/react-router';
import Footer from './footer';
import KeyFeatures from './key-features';
import Mission from './mission';
import News from './news';

type CardProps = {
	icon?: string;
	title: string;
	description: string;
};

export default function LandingPage() {
	const router = useRouter();

	return (
		<div className="flex flex-col items-center w-full bg-white">
			<main className="flex flex-col items-center w-full px-4 pt-12 pb-20">
				<Typography
					variant="h2"
					className="text-center text-[#007AFF] font-bold mb-2 text-3xl md:text-4xl"
				>
					리딩브릿지
				</Typography>
				<Typography
					variant="p"
					className="text-center text-gray-500 mb-6 text-sm md:text-base max-w-xl"
				>
					난독증 학생들을 위한 맞춤형 학습 경험
					<br />
					보호자가 업로드한 PDF 고안물을 AI로 변환하여 모든 학생이 쉽게 배울 수
					있도록 지원합니다
				</Typography>
				<div className="flex gap-2 mb-10">
					<Button variant="outline" size="lg">
						체험해보기
					</Button>
					<Button size="lg">무료로 시작하기</Button>
				</div>

				<div className="w-full max-w-3xl rounded-2xl border overflow-hidden mb-16">
					<img
						src="/images/readingbridge_preview.JPG"
						alt="리딩브릿지 미리보기"
						className="w-full h-auto"
					/>
				</div>

				<div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-5xl mb-20">
					<FeatureCard
						icon="🗣️"
						title="TTS 음성 지원"
						description="텍스트를 음성으로 학습"
					/>
					<FeatureCard
						icon="🔤"
						title="폰트 조절"
						description="읽기 편한 글씨체로 변경"
					/>
					<FeatureCard
						icon="🔍"
						title="어휘 분석"
						description="어려운 단어를 쉽게 설명"
					/>
					<FeatureCard
						icon="📖"
						title="책처럼 읽기"
						description="자연스러운 읽기 연습 제공"
					/>
				</div>

				<KeyFeatures />
				<Mission />
				<News />

				<section className="w-full bg-[#007AFF] text-white py-12 text-center">
					<Typography
						variant="h3"
						className="font-semibold mb-3 text-white text-center"
					>
						지금 시작해서 아이의 읽기 자신감을 키워보세요
					</Typography>
					<Typography variant="p" className="mb-6 text-white text-center">
						첫 고안 입력부터 AI 분석까지, 모든 기능을 무료로 체험해보세요
					</Typography>
					<Button
						variant="outline"
						size="lg"
						className="bg-white text-[#007AFF] hover:bg-gray-100"
						onClick={() => router.navigate({ to: '/signup' })}
					>
						무료 체험 시작하기
					</Button>
				</section>
				<Footer />
			</main>
		</div>
	);
}

function FeatureCard({ icon, title, description }: CardProps) {
	return (
		<div className="flex flex-col items-center text-center p-4 bg-white rounded-lg border">
			<div className="text-2xl mb-1">{icon}</div>
			<Typography variant="p" className="font-medium mb-0.5">
				{title}
			</Typography>
			<Typography variant="p" className="text-gray-500 text-xs">
				{description}
			</Typography>
		</div>
	);
}
