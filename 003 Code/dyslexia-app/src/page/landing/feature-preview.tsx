import { Card } from '@/shared/ui/card';
import { Typography } from '@/shared/ui/typography';

export default function FeaturePreview() {
	return (
		<section className="py-20 px-4 bg-[#F9FAFB]">
			<div className="max-w-6xl mx-auto">
				<div className="text-center mb-12">
					<Typography
						variant="h2"
						size="2xl"
						weight="bold"
						className="text-gray-900 mb-4"
					>
						리딩브릿지 체험 미리보기
					</Typography>
					<Typography variant="p" className="text-gray-600">
						실제 학생들이 보는 화면을 그대로 체험해보세요. <br />
						폰트 조절, TTS, 어휘 강조 등 다양한 기능이 지원됩니다.
					</Typography>
				</div>

				{/* 콘텐츠 프리뷰 */}
				<div className="relative bg-gray-800 rounded-3xl p-4 shadow-2xl w-full max-w-5xl mx-auto">
					<div className="bg-black rounded-2xl p-2">
						<div className="bg-white rounded-xl overflow-hidden aspect-[4/3]">
							<div className="h-full flex flex-col">
								{/* 상단 바 */}
								<div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex items-center justify-between">
									<div className="flex items-center gap-2">
										<img src="/icons/book.svg" className="w-5 h-5" alt="Book" />
										<span className="text-gray-800 font-bold text-lg">
											우리 동네 동물들
										</span>
									</div>
									<div className="flex items-center gap-4 text-sm text-gray-500">
										<span>1 / 20 페이지</span>
										<button className="text-xs px-3 py-1 border rounded border-gray-300 flex items-center gap-1 hover:bg-gray-100">
											<img
												src="/icons/tts.svg"
												className="w-3 h-3"
												alt="듣기"
											/>
											듣기
										</button>
									</div>
								</div>

								{/* 본문 */}
								<div className="flex-1 flex">
									{/* 좌측 툴바 */}
									<div className="w-16 bg-gray-50 border-r border-gray-200 flex flex-col items-center gap-3 p-3">
										{[
											{ icon: '/icons/tts.svg', bg: 'bg-primary', alt: 'TTS' },
											{
												icon: '/icons/font.svg',
												bg: 'bg-orange-400',
												alt: 'Font',
											},
											{
												icon: '/icons/word.svg',
												bg: 'bg-yellow-400',
												alt: 'Word',
											},
											{
												icon: '/icons/book.svg',
												bg: 'bg-sky-500',
												alt: '읽기',
											},
										].map((tool, i) => (
											<div
												key={i}
												className={`w-10 h-10 ${tool.bg} rounded-lg flex items-center justify-center`}
											>
												<img
													src={tool.icon}
													alt={tool.alt}
													className="w-5 h-5 text-white"
												/>
											</div>
										))}
									</div>

									{/* 본문 내용 */}
									<div className="flex-1 p-8 bg-gradient-to-b from-white to-gray-50">
										<div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8">
											<div className="space-y-4 text-left">
												<p className="text-lg text-gray-800 leading-relaxed font-dyslexic">
													우리 동네에는 많은{' '}
													<span className="bg-yellow-200 px-1 rounded">
														동물
													</span>{' '}
													친구들이 살고 있어요.
												</p>
												<p className="text-lg text-gray-800 leading-relaxed font-dyslexic">
													공원에서는 귀여운{' '}
													<span className="bg-yellow-200 px-1 rounded">
														다람쥐
													</span>
													들이 나무를 오르내리며 놀고 있어요.
												</p>
											</div>
											<div className="space-y-4 text-left">
												<p className="text-lg text-gray-800 leading-relaxed font-dyslexic">
													연못에서는{' '}
													<span className="bg-yellow-200 px-1 rounded">
														오리
													</span>{' '}
													가족이 평화롭게 헤엄치고 있어요.
												</p>
												<div className="w-32 h-20 bg-gradient-to-r from-green-100 to-blue-100 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-300">
													<span className="text-gray-500 text-xs">
														AI 생성 이미지
													</span>
												</div>
											</div>
										</div>
									</div>
								</div>

								{/* 하단 바 */}
								<div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex items-center justify-between">
									<button
										className="text-sm text-gray-400 flex items-center gap-1"
										disabled
									>
										<img src="/icons/left.svg" className="w-4 h-4" />
										이전 페이지
									</button>
									<div className="flex-1 mx-8">
										<div className="w-full bg-gray-200 h-2 rounded-full">
											<div
												className="bg-primary h-2 rounded-full"
												style={{ width: '5%' }}
											/>
										</div>
									</div>
									<button className="text-sm text-white bg-primary rounded px-4 py-1 flex items-center gap-1">
										다음 페이지
										<img src="/icons/right.svg" className="w-4 h-4" />
									</button>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>
	);
}
