import { Card } from '@/shared/ui/card';
import { Typography } from '@/shared/ui/typography';
import { Globe, Monitor, Zap } from 'lucide-react';

export default function KeyFeatures() {
	const keyFeatures = [
		{
			icon: <Globe className="w-12 h-12 text-blue-500" />,
			title: '해외 자료의 한국형 재생성',
			description:
				'공개 저작권의 해외 교육 자료를 한국 난독증 학생들에게 맞게 AI로 재생성합니다',
			details:
				'원문의 핵심 내용을 유지하면서 한국어 특성과 난독증 학습자의 특성을 고려하여 최적화된 콘텐츠로 변환해요',
		},
		{
			icon: <Monitor className="w-12 h-12 text-green-500" />,
			title: '언제 어디서나 원격 지도',
			description:
				'보호자와 아동 간 실시간 모니터링으로 원격에서도 효과적인 학습 지도가 가능합니다',
			details:
				'학습 진도, 이해도, 집중도를 실시간으로 확인하고 필요한 순간에 즉시 도움을 제공할 수 있어요',
		},
		{
			icon: <Zap className="w-12 h-12 text-purple-500" />,
			title: '난독증 맞춤 솔루션',
			description:
				'난독 아동의 개별적인 학습 특성을 분석하여 맞춤형 학습 환경을 제공합니다',
			details:
				'읽기 속도, 이해도, 선호하는 학습 방식을 분석하여 각 아이에게 최적화된 학습 경험을 설계해요',
		},
	];

	return (
		<section className="py-16 px-4 sm:px-8 bg-gradient-to-b from-blue-50 to-white">
			<div className="max-w-6xl mx-auto">
				<div className="text-center mb-12">
					<h3 className="text-3xl font-bold text-gray-900 mb-4">
						리딩브릿지의 핵심 기능
					</h3>
					<p className="text-lg text-gray-600">
						난독증 학생들을 위한 혁신적인 학습 솔루션을 제공합니다
					</p>
				</div>

				<div className="space-y-16">
					{keyFeatures.map((feature, index) => (
						<div
							key={index}
							className={`flex flex-col ${index % 2 === 0 ? 'lg:flex-row' : 'lg:flex-row-reverse'} items-center gap-12`}
						>
							<div className="flex-1">
								<div className="flex items-center mb-6">
									<div className="mr-4 p-3 bg-white rounded-xl shadow-lg">
										{feature.icon}
									</div>
									<h4 className="text-2xl font-bold text-gray-900">
										{feature.title}
									</h4>
								</div>
								<p className="text-lg text-gray-700 mb-4 leading-relaxed">
									{feature.description}
								</p>
								<p className="text-gray-600 leading-relaxed">
									{feature.details}
								</p>
							</div>
							<div className="flex-1">
								<div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
									{index === 0 && (
										<div className="space-y-6">
											<div className="text-center">
												<h5 className="font-semibold text-gray-800 mb-4">
													콘텐츠 변환 예시
												</h5>
											</div>
											<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
												<div className="bg-gray-50 p-4 rounded-lg">
													<h6 className="text-sm font-medium text-gray-600 mb-2">
														원문 (영어)
													</h6>
													<p className="text-sm text-gray-800">
														"The quick brown fox jumps over the lazy dog."
													</p>
												</div>
												<div className="bg-primary/5 p-4 rounded-lg">
													<h6 className="text-sm font-medium text-primary mb-2">
														변환된 내용
													</h6>
													<p className="text-sm text-gray-800 font-dyslexic leading-relaxed">
														빠른{' '}
														<span className="bg-yellow-200 px-1 rounded">
															갈색
														</span>{' '}
														여우가 게으른 개 위로 뛰어넘어요.
													</p>
												</div>
											</div>
											<div className="flex justify-center">
												<div className="w-24 h-16 bg-gradient-to-r from-orange-100 to-yellow-100 rounded-lg flex items-center justify-center border-2 border-dashed border-orange-300">
													<span className="text-orange-600 text-xs">
														AI 생성
													</span>
												</div>
											</div>
										</div>
									)}
									{index === 1 && (
										<div className="space-y-6">
											<div className="text-center">
												<h5 className="font-semibold text-gray-800 mb-4">
													실시간 모니터링 대시보드
												</h5>
											</div>
											<div className="space-y-4">
												<div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-400">
													<div className="flex justify-between items-center">
														<span className="text-sm font-medium text-green-800">
															민지의 학습 상태
														</span>
														<span className="text-xs text-green-600">
															활발히 학습 중
														</span>
													</div>
													<div className="mt-2 bg-green-200 rounded-full h-2">
														<div
															className="bg-green-500 h-2 rounded-full"
															style={{ width: '75%' }}
														/>
													</div>
												</div>
												<div className="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-400">
													<div className="flex justify-between items-center">
														<span className="text-sm font-medium text-yellow-800">
															준호의 학습 상태
														</span>
														<span className="text-xs text-yellow-600">
															도움 필요
														</span>
													</div>
													<div className="mt-2 bg-yellow-200 rounded-full h-2">
														<div
															className="bg-yellow-500 h-2 rounded-full"
															style={{ width: '45%' }}
														/>
													</div>
												</div>
											</div>
										</div>
									)}
									{index === 2 && (
										<div className="space-y-6">
											<div className="text-center">
												<h5 className="font-semibold text-gray-800 mb-4">
													개인 맞춤 학습 분석
												</h5>
											</div>
											<div className="space-y-4">
												<div className="bg-blue-50 p-4 rounded-lg">
													<h6 className="text-sm font-medium text-blue-800 mb-2">
														읽기 선호도
													</h6>
													<div className="flex space-x-2">
														<span className="px-2 py-1 bg-blue-200 text-blue-800 text-xs rounded">
															큰 글씨
														</span>
														<span className="px-2 py-1 bg-blue-200 text-blue-800 text-xs rounded">
															음성 지원
														</span>
													</div>
												</div>
												<div className="bg-purple-50 p-4 rounded-lg">
													<h6 className="text-sm font-medium text-purple-800 mb-2">
														학습 패턴
													</h6>
													<div className="flex space-x-2">
														<span className="px-2 py-1 bg-purple-200 text-purple-800 text-xs rounded">
															시각적 학습
														</span>
														<span className="px-2 py-1 bg-purple-200 text-purple-800 text-xs rounded">
															반복 학습
														</span>
													</div>
												</div>
											</div>
										</div>
									)}
								</div>
							</div>
						</div>
					))}
				</div>
			</div>
		</section>
	);
}
