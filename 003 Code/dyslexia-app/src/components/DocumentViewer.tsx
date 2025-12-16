import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
	Popover,
	PopoverContent,
	PopoverTrigger,
} from '@/components/ui/popover';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { useToast } from '@/hooks/use-toast';
import {
	Bookmark,
	ChevronLeft,
	ChevronRight,
	Eye,
	Settings,
	Star,
	Type,
	Volume2,
	VolumeX,
} from 'lucide-react';
import { useEffect, useState } from 'react';

interface DocumentViewerProps {
	documentId: string;
	initialPage?: number;
	isPreviewMode?: boolean;
	onPageChange?: (page: number) => void;
	showStudentFeatures?: boolean;
	userType?: 'student' | 'guardian';
}

const DocumentViewer = ({
	documentId,
	initialPage = 1,
	isPreviewMode = false,
	onPageChange,
	showStudentFeatures = true,
	userType = 'student',
}: DocumentViewerProps) => {
	const { toast } = useToast();

	// Viewer settings state
	const [fontSize, setFontSize] = useState([18]);
	const [lineSpacing, setLineSpacing] = useState([1.6]);
	const [letterSpacing, setLetterSpacing] = useState([0.05]);
	const [fontFamily, setFontFamily] = useState('dyslexic');
	const [backgroundColor, setBackgroundColor] = useState('white');
	const [isVocabHighlightOn, setIsVocabHighlightOn] = useState(true);
	const [isReading, setIsReading] = useState(false);
	const [showPageList, setShowPageList] = useState(false);
	const [readingFocusMode, setReadingFocusMode] = useState(false);

	// Document state
	const [currentPage, setCurrentPage] = useState(initialPage);
	const [totalPages] = useState(20);
	const [bookTitle] = useState('우리 동네 동물들');

	const mockContent = `우리 동네에는 많은 동물 친구들이 살고 있어요. 

공원에서는 귀여운 다람쥐들이 나무를 오르내리며 놀고 있어요. 다람쥐들은 겨울에 먹을 도토리를 열심히 모으고 있답니다.

연못에서는 오리 가족이 평화롭게 헤엄치고 있어요. 아기 오리들이 엄마 오리를 따라 일렬로 헤엄치는 모습이 정말 사랑스러워요.

길에서는 길고양이들을 만날 수 있어요. 이 고양이들은 사람들이 주는 음식을 먹으며 살아가고 있어요. 우리가 따뜻한 마음으로 돌봐주면 좋겠어요.`;

	// Text-to-Speech function
	const handleTTS = () => {
		if (isReading) {
			speechSynthesis.cancel();
			setIsReading(false);
			return;
		}

		const utterance = new SpeechSynthesisUtterance(mockContent);
		utterance.rate = 0.8;
		utterance.pitch = 1.1;
		utterance.lang = 'ko-KR';

		utterance.onstart = () => setIsReading(true);
		utterance.onend = () => setIsReading(false);
		utterance.onerror = () => setIsReading(false);

		speechSynthesis.speak(utterance);
	};

	const handlePageChange = (direction: 'prev' | 'next') => {
		const newPage = direction === 'next' ? currentPage + 1 : currentPage - 1;

		if (newPage >= 1 && newPage <= totalPages) {
			setCurrentPage(newPage);
			onPageChange?.(newPage);

			if (direction === 'next' && showStudentFeatures) {
				toast({
					title: '잘했어요! ⭐',
					description: '페이지를 완료했어요!',
				});
			}
		}
	};

	const handleJumpToPage = (page: number) => {
		setCurrentPage(page);
		onPageChange?.(page);
		setShowPageList(false);
	};

	const fontFamilies = {
		dyslexic: 'font-dyslexic',
		sans: 'font-sans',
		serif: 'font-serif',
	};

	const backgroundColors = {
		white: 'bg-white',
		cream: 'bg-orange-50',
		light: 'bg-blue-50',
		dark: 'bg-gray-800 text-white',
	};

	useEffect(() => {
		return () => {
			speechSynthesis.cancel();
		};
	}, []);

	return (
		<div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50 font-dyslexic flex flex-col">
			{/* Header - Settings Bar */}
			<header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-sm">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
					<div className="flex items-center justify-between">
						{/* Left: Page Navigator */}
						<div className="flex items-center space-x-4">
							<Popover open={showPageList} onOpenChange={setShowPageList}>
								<PopoverTrigger asChild>
									<Button
										variant="outline"
										size="sm"
										className="flex items-center space-x-2"
									>
										<span className="font-medium">
											{currentPage} / {totalPages}
										</span>
										<span className="text-xs text-gray-500">페이지</span>
									</Button>
								</PopoverTrigger>
								<PopoverContent className="w-80 p-4">
									<h4 className="font-medium mb-3">페이지 이동</h4>
									<ScrollArea className="h-40">
										<div className="grid grid-cols-5 gap-2">
											{Array.from({ length: totalPages }, (_, i) => i + 1).map(
												(page) => (
													<Button
														key={page}
														variant={
															page === currentPage ? 'default' : 'outline'
														}
														size="sm"
														onClick={() => handleJumpToPage(page)}
														className="w-full"
													>
														{page}
													</Button>
												),
											)}
										</div>
									</ScrollArea>
								</PopoverContent>
							</Popover>

							<div className="text-sm text-gray-600">{bookTitle}</div>
						</div>

						{/* Right: Viewer Settings */}
						<div className="flex items-center space-x-2">
							{/* Font Size */}
							<Button
								variant="outline"
								size="sm"
								onClick={() =>
									setFontSize((prev) => [Math.max(14, prev[0] - 2)])
								}
								disabled={fontSize[0] <= 14}
							>
								A-
							</Button>
							<Button
								variant="outline"
								size="sm"
								onClick={() =>
									setFontSize((prev) => [Math.min(28, prev[0] + 2)])
								}
								disabled={fontSize[0] >= 28}
							>
								A+
							</Button>

							{/* Font Family */}
							<Select value={fontFamily} onValueChange={setFontFamily}>
								<SelectTrigger className="w-20">
									<Type className="w-4 h-4" />
								</SelectTrigger>
								<SelectContent>
									<SelectItem value="dyslexic">난독증 친화</SelectItem>
									<SelectItem value="sans">고딕체</SelectItem>
									<SelectItem value="serif">명조체</SelectItem>
								</SelectContent>
							</Select>

							{/* Vocabulary Highlight Toggle */}
							<Button
								variant={isVocabHighlightOn ? 'default' : 'outline'}
								size="sm"
								onClick={() => setIsVocabHighlightOn(!isVocabHighlightOn)}
							>
								<Bookmark className="w-4 h-4" />
							</Button>

							{/* Reading Focus Mode */}
							<Button
								variant={readingFocusMode ? 'default' : 'outline'}
								size="sm"
								onClick={() => setReadingFocusMode(!readingFocusMode)}
							>
								<Eye className="w-4 h-4" />
							</Button>

							{/* TTS */}
							{showStudentFeatures && (
								<Button
									variant={isReading ? 'destructive' : 'outline'}
									size="sm"
									onClick={handleTTS}
								>
									{isReading ? (
										<VolumeX className="w-4 h-4" />
									) : (
										<Volume2 className="w-4 h-4" />
									)}
								</Button>
							)}

							{/* Advanced Settings */}
							<Popover>
								<PopoverTrigger asChild>
									<Button variant="outline" size="sm">
										<Settings className="w-4 h-4" />
									</Button>
								</PopoverTrigger>
								<PopoverContent className="w-80 p-4">
									<div className="space-y-4">
										<h4 className="font-medium">상세 설정</h4>

										{/* Line Spacing */}
										<div className="space-y-2">
											<label className="text-sm font-medium">줄 간격</label>
											<Slider
												value={lineSpacing}
												onValueChange={setLineSpacing}
												min={1.2}
												max={2.4}
												step={0.2}
												className="w-full"
											/>
											<p className="text-xs text-gray-600">
												{lineSpacing[0].toFixed(1)}
											</p>
										</div>

										{/* Letter Spacing */}
										<div className="space-y-2">
											<label className="text-sm font-medium">자간</label>
											<Slider
												value={letterSpacing}
												onValueChange={setLetterSpacing}
												min={0}
												max={0.15}
												step={0.01}
												className="w-full"
											/>
											<p className="text-xs text-gray-600">
												{(letterSpacing[0] * 100).toFixed(0)}%
											</p>
										</div>

										{/* Background Color */}
										<div className="space-y-2">
											<label className="text-sm font-medium">배경색</label>
											<Select
												value={backgroundColor}
												onValueChange={setBackgroundColor}
											>
												<SelectTrigger>
													<SelectValue />
												</SelectTrigger>
												<SelectContent>
													<SelectItem value="white">밝은 테마</SelectItem>
													<SelectItem value="cream">세피아 테마</SelectItem>
													<SelectItem value="light">연한 파란색</SelectItem>
													<SelectItem value="dark">어두운 테마</SelectItem>
												</SelectContent>
											</Select>
										</div>
									</div>
								</PopoverContent>
							</Popover>
						</div>
					</div>
				</div>
			</header>

			{/* Body - Content Area */}
			<main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
				<Card
					className={`border-gray-200 shadow-lg ${backgroundColors[backgroundColor as keyof typeof backgroundColors]} ${readingFocusMode ? 'reading-focus' : ''}`}
				>
					<CardContent className="p-8">
						{/* Achievement Sticker */}
						{showStudentFeatures && (
							<div className="absolute top-4 right-4">
								<Star className="w-8 h-8 text-yellow-400 fill-current animate-pulse" />
							</div>
						)}

						{/* Two-column layout for better readability */}
						<div className="grid md:grid-cols-2 gap-8">
							<div
								className={`${fontFamilies[fontFamily as keyof typeof fontFamilies]} text-gray-800 leading-relaxed space-y-4`}
								style={{
									fontSize: `${fontSize[0]}px`,
									lineHeight: lineSpacing[0],
									letterSpacing: `${letterSpacing[0]}em`,
								}}
							>
								{mockContent
									.split('\n\n')
									.slice(0, 2)
									.map((paragraph, index) => (
										<p key={index} className="mb-4">
											{paragraph
												.trim()
												.split(' ')
												.map((word, wordIndex) => (
													<span
														key={wordIndex}
														className={`${isVocabHighlightOn && ['동물', '다람쥐', '오리'].includes(word) ? 'bg-yellow-200 px-1 rounded' : ''} cursor-pointer hover:bg-blue-100 transition-colors`}
														onClick={() => {
															if (showStudentFeatures) {
																const utterance = new SpeechSynthesisUtterance(
																	word,
																);
																utterance.lang = 'ko-KR';
																speechSynthesis.speak(utterance);
															}
														}}
													>
														{word}{' '}
													</span>
												))}
										</p>
									))}
							</div>

							<div
								className={`${fontFamilies[fontFamily as keyof typeof fontFamilies]} text-gray-800 leading-relaxed space-y-4`}
								style={{
									fontSize: `${fontSize[0]}px`,
									lineHeight: lineSpacing[0],
									letterSpacing: `${letterSpacing[0]}em`,
								}}
							>
								{mockContent
									.split('\n\n')
									.slice(2)
									.map((paragraph, index) => (
										<p key={index + 2} className="mb-4">
											{paragraph
												.trim()
												.split(' ')
												.map((word, wordIndex) => (
													<span
														key={wordIndex}
														className={`${isVocabHighlightOn && ['고양이', '음식', '마음'].includes(word) ? 'bg-yellow-200 px-1 rounded' : ''} cursor-pointer hover:bg-blue-100 transition-colors`}
														onClick={() => {
															if (showStudentFeatures) {
																const utterance = new SpeechSynthesisUtterance(
																	word,
																);
																utterance.lang = 'ko-KR';
																speechSynthesis.speak(utterance);
															}
														}}
													>
														{word}{' '}
													</span>
												))}
										</p>
									))}
							</div>
						</div>

						{/* Generated Image Placeholder */}
						<div className="my-8 flex justify-center">
							<div className="w-64 h-40 bg-gradient-to-r from-green-100 to-blue-100 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-300">
								<span className="text-gray-500 text-sm">AI 생성 이미지</span>
							</div>
						</div>
					</CardContent>
				</Card>
			</main>

			{/* Footer - Navigation Bar */}
			<footer className="sticky bottom-0 z-50 bg-white/95 backdrop-blur-sm border-t border-gray-200 shadow-sm">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
					<div className="flex items-center justify-between">
						<Button
							variant="outline"
							onClick={() => handlePageChange('prev')}
							disabled={currentPage === 1}
							className="flex items-center space-x-2"
						>
							<ChevronLeft className="w-4 h-4" />
							<span>이전 페이지</span>
						</Button>

						{/* Progress Bar */}
						<div className="flex-1 mx-8">
							<div className="flex items-center justify-between mb-2">
								<span className="text-sm text-gray-600">읽기 진행률</span>
								<span className="text-sm font-medium text-primary">
									{Math.round((currentPage / totalPages) * 100)}%
								</span>
							</div>
							<div className="w-full bg-gray-200 rounded-full h-3 relative overflow-hidden">
								<div
									className="bg-gradient-to-r from-primary to-primary/80 rounded-full h-3 transition-all duration-500 relative"
									style={{ width: `${(currentPage / totalPages) * 100}%` }}
								>
									{showStudentFeatures && (
										<div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
									)}
								</div>
							</div>
						</div>

						<Button
							onClick={() => handlePageChange('next')}
							disabled={currentPage === totalPages}
							className="flex items-center space-x-2 bg-primary hover:bg-primary/90"
						>
							<span>다음 페이지</span>
							<ChevronRight className="w-4 h-4" />
						</Button>
					</div>
				</div>
			</footer>
		</div>
	);
};

export default DocumentViewer;
