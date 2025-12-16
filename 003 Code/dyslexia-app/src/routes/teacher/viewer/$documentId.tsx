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
import { guardianTextbookApi } from '@/features/textbooks/api/guardian-textbook-api';
import { viewerApi } from '@/features/viewer/api/viewer-api';
import { DocumentRenderer } from '@/features/viewer/ui/document-renderer';
import { PageTips } from '@/features/viewer/ui/page-tips';
import { useSequentialSpeech } from '@/features/viewer/lib/use-sequential-speech';
import { useQuery } from '@tanstack/react-query';
import { createFileRoute } from '@tanstack/react-router';
import {
	Bookmark,
	ChevronLeft,
	ChevronRight,
	Eye,
	Settings,
	Type,
	Volume2,
	VolumeX,
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

export const Route = createFileRoute('/teacher/viewer/$documentId')({
	component: DocumentViewerPage,
});

const fontMap = {
	dyslexic: 'font-dyslexic',
	sans: 'font-sans',
	serif: 'font-serif',
} as const;

const bgMap = {
	white: 'bg-white',
	cream: 'bg-orange-50',
	light: 'bg-blue-50',
	dark: 'bg-gray-800 text-white',
} as const;

export default function DocumentViewerPage() {
	const { documentId } = Route.useParams();
	const docId = Number.parseInt(documentId ?? '', 10);

	const [currentPage, setCurrentPage] = useState(1);
	const [fontSize, setFontSize] = useState([18]);
	const [lineSpacing, setLineSpacing] = useState([1.6]);
	const [letterSpacing, setLetterSpacing] = useState([0.05]);
	const [fontFamily, setFontFamily] = useState<'dyslexic' | 'sans' | 'serif'>(
		'dyslexic',
	);
	const [backgroundColor, setBackgroundColor] = useState<
		'white' | 'cream' | 'light' | 'dark'
	>('white');
	const [isVocabHighlightOn, setIsVocabHighlightOn] = useState(true);
	const [readingFocusMode, setReadingFocusMode] = useState(false);
	const [showPageList, setShowPageList] = useState(false);

	// 순차적 낭독 훅
	const sequentialSpeech = useSequentialSpeech();
	const stageContainerRef = useRef<HTMLDivElement | null>(null);
	const headerRef = useRef<HTMLElement | null>(null);
	const footerRef = useRef<HTMLElement | null>(null);
	// CSS var-based sizing; no local height state

	// textbook detail (title, total pages, etc.)
	const { data: detail, isLoading: isLoadingDetail } = useQuery({
		queryKey: ['guardian', 'textbooks', docId, 'detail'],
		queryFn: () => guardianTextbookApi.getTextbookDetail(docId),
		enabled: !!docId,
		staleTime: 2_000,
		refetchInterval: (data) => {
			const status =
				(data as any)?.analysis_status ?? (data as any)?.convert_status;
			if (!status) return false as const;
			return status === 'COMPLETED' || status === 'FAILED' ? false : 10_000;
		},
	});
	const activeTextbookId = detail?.textbook_id ?? docId;
	if (detail && detail.textbook_id !== docId) {
		console.warn('Route param documentId differs from backend textbook_id', {
			routeDocumentId: docId,
			backendTextbookId: detail.textbook_id,
		});
	}

	// Current page content (use normalized active id when available)
	const { data: pages = [], isLoading: isLoadingPage } = useQuery({
		queryKey: ['document', activeTextbookId, 'page-content', currentPage],
		queryFn: () => viewerApi.getPageContent(activeTextbookId, currentPage),
		enabled: !!activeTextbookId,
	});

	const page = pages[0];

	// Page tips for current page
	const { data: tips = [], isLoading: isLoadingTips } = useQuery({
		queryKey: ['document', activeTextbookId, 'page', page?.id, 'tips'],
		queryFn: () => viewerApi.getPageTips(page!.id),
		enabled: !!activeTextbookId && !!page?.id,
		staleTime: 60_000,
	});

	const totalPages = detail?.total_pages ?? 0;

	const handleTTS = () => {
		if (!page?.processedContent?.blocks) return;
		if (sequentialSpeech.isReading) {
			sequentialSpeech.stop();
			return;
		}
		const textBlocks = page.processedContent.blocks
			.filter((b) => 'text' in b)
			.map((b: any) => ({ id: b.id, text: b.text })) as { id?: string; text: string }[];
		sequentialSpeech.startSequentialReading(textBlocks);
	};

	const handlePageChange = (direction: 'prev' | 'next') => {
		const newPage = direction === 'next' ? currentPage + 1 : currentPage - 1;
		if (newPage >= 1 && newPage <= totalPages) setCurrentPage(newPage);
	};

	const handleJumpToPage = (page: number) => {
		setCurrentPage(page);
		setShowPageList(false);
	};

	useEffect(() => {
		return () => {
			sequentialSpeech.stop();
		};
	// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	const minFs = 14;
	const maxFs = 28;
	const textColorClass =
		backgroundColor === 'dark' ? 'text-white' : 'text-gray-800';

	// Measure header/footer and expose CSS vars for layout sizing
	useEffect(() => {
		const update = () => {
			const footerH = footerRef.current?.offsetHeight ?? 0;
			const headerH = headerRef.current?.offsetHeight ?? 0;
			document.documentElement.style.setProperty(
				'--viewer-header-h',
				`${headerH}px`,
			);
			document.documentElement.style.setProperty(
				'--viewer-footer-h',
				`${footerH}px`,
			);
		};
		const ro = new ResizeObserver(update);
		if (footerRef.current) ro.observe(footerRef.current);
		if (headerRef.current) ro.observe(headerRef.current);
		window.addEventListener('resize', update);
		setTimeout(update, 0);
		return () => {
			ro.disconnect();
			window.removeEventListener('resize', update);
		};
	}, []);

	// When page changes, scroll the stage into view and reset internal scroll
	useEffect(() => {
		const headerH = headerRef.current?.offsetHeight ?? 0;
		const el = stageContainerRef.current;
		if (!el) return;
		const top = el.getBoundingClientRect().top + window.scrollY - headerH - 8;
		window.scrollTo({ top, behavior: 'smooth' });
	}, [currentPage]);

	// Stop reading when page changes
	useEffect(() => {
		if (sequentialSpeech.isReading) {
			sequentialSpeech.stop();
		}
	// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [currentPage]);

	return (
		<div
			className={[
				'min-h-screen',
				'flex',
				'flex-col',
				readingFocusMode ? 'reading-focus' : '',
			].join(' ')}
		>
			{/* Scoped typography override to force styles into nested content */}
			<style>{`
        .rb-typo {
          --rb-fs: ${fontSize[0]}px;
          --rb-lh: ${lineSpacing[0]};
          --rb-ls: ${letterSpacing[0]}em;
        }
        .rb-typo * {
          font-size: var(--rb-fs) !important;
          line-height: var(--rb-lh) !important;
          letter-spacing: var(--rb-ls) !important;
        }
      `}</style>

			<header
				ref={headerRef}
				className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-sm"
			>
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center gap-3">
					{/* Left: Page jump */}
					<Popover open={showPageList} onOpenChange={setShowPageList}>
						<PopoverTrigger asChild>
							<Button variant="outline" size="sm">
								{currentPage} / {totalPages} 페이지
							</Button>
						</PopoverTrigger>
						<PopoverContent className="w-80 p-4">
							<h4 className="font-medium mb-3" id="page-jump-label">
								페이지 이동
							</h4>
							<ScrollArea className="h-40" aria-labelledby="page-jump-label">
								<div className="grid grid-cols-5 gap-2">
									{Array.from({ length: totalPages }, (_, i) => i + 1).map(
										(p) => (
											<Button
												key={p}
												variant={p === currentPage ? 'default' : 'outline'}
												size="sm"
												onClick={() => handleJumpToPage(p)}
											>
												{p}
											</Button>
										),
									)}
								</div>
							</ScrollArea>
						</PopoverContent>
					</Popover>

					{/* Center: Document title in navbar */}
					{(detail?.inferred_title || detail?.textbook_name) && (
						<div className="flex-1 text-center font-semibold truncate px-2">
							{detail?.inferred_title || detail?.textbook_name}
						</div>
					)}

					{/* Right: Controls */}
					<div className="flex items-center gap-2">
						<Button
							variant="outline"
							size="sm"
							onClick={() =>
								setFontSize((prev) => [Math.max(minFs, prev[0] - 2)])
							}
							disabled={fontSize[0] <= minFs}
							aria-label="글자 크기 축소"
							title="글자 크기 축소"
						>
							A-
						</Button>
						<Button
							variant="outline"
							size="sm"
							onClick={() =>
								setFontSize((prev) => [Math.min(maxFs, prev[0] + 2)])
							}
							disabled={fontSize[0] >= maxFs}
							aria-label="글자 크기 확대"
							title="글자 크기 확대"
						>
							A+
						</Button>

						<Select
							value={fontFamily}
							onValueChange={(value: 'dyslexic' | 'sans' | 'serif') =>
								setFontFamily(value)
							}
						>
							<SelectTrigger className="w-28">
								<Type className="w-4 h-4 mr-2" />
								<SelectValue placeholder="글꼴" />
							</SelectTrigger>
							<SelectContent>
								<SelectItem value="dyslexic">난독증</SelectItem>
								<SelectItem value="sans">고딕</SelectItem>
								<SelectItem value="serif">명조</SelectItem>
							</SelectContent>
						</Select>

						<Button
							variant={isVocabHighlightOn ? 'default' : 'outline'}
							size="sm"
							onClick={() => setIsVocabHighlightOn(!isVocabHighlightOn)}
							aria-pressed={isVocabHighlightOn}
							title="어휘 하이라이트"
						>
							<Bookmark className="w-4 h-4" />
						</Button>

						<Button
							variant={readingFocusMode ? 'default' : 'outline'}
							size="sm"
							onClick={() => setReadingFocusMode(!readingFocusMode)}
							aria-pressed={readingFocusMode}
							title="집중 모드"
						>
							<Eye className="w-4 h-4" />
						</Button>

						<Button
							variant={sequentialSpeech.isReading ? 'destructive' : 'outline'}
							size="sm"
							onClick={handleTTS}
							title={sequentialSpeech.isReading ? '낭독 중지' : '낭독 시작'}
						>
							{sequentialSpeech.isReading ? (
								<VolumeX className="w-4 h-4" />
							) : (
								<Volume2 className="w-4 h-4" />
							)}
						</Button>

						<Popover>
							<PopoverTrigger asChild>
								<Button variant="outline" size="sm">
									<Settings className="w-4 h-4" />
								</Button>
							</PopoverTrigger>
							<PopoverContent className="w-80 p-4">
								<div className="space-y-4">
									<div className="space-y-2">
										<label
											className="text-sm font-medium"
											htmlFor="line-spacing-slider"
										>
											줄 간격 ({lineSpacing[0].toFixed(1)})
										</label>
										<Slider
											id="line-spacing-slider"
											value={lineSpacing}
											onValueChange={setLineSpacing}
											min={1.2}
											max={2.4}
											step={0.2}
										/>
									</div>
									<div className="space-y-2">
										<label
											className="text-sm font-medium"
											htmlFor="letter-spacing-slider"
										>
											자간 ({(letterSpacing[0] * 100).toFixed(0)}%)
										</label>
										<Slider
											id="letter-spacing-slider"
											value={letterSpacing}
											onValueChange={setLetterSpacing}
											min={0}
											max={0.15}
											step={0.01}
										/>
									</div>
									<div className="space-y-2">
										<label
											className="text-sm font-medium"
											htmlFor="background-color-select"
										>
											배경색
										</label>
										<Select
											value={backgroundColor}
											onValueChange={(
												value: 'white' | 'cream' | 'light' | 'dark',
											) => setBackgroundColor(value)}
										>
											<SelectTrigger id="background-color-select">
												<SelectValue placeholder="배경" />
											</SelectTrigger>
											<SelectContent>
												<SelectItem value="white">밝은 테마</SelectItem>
												<SelectItem value="cream">세피아</SelectItem>
												<SelectItem value="light">연한 파랑</SelectItem>
												<SelectItem value="dark">어두운 테마</SelectItem>
											</SelectContent>
										</Select>
									</div>
								</div>
							</PopoverContent>
						</Popover>
					</div>
				</div>
			</header>

			<main
				className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6"
				style={{ paddingBottom: 'calc(var(--viewer-footer-h, 64px) + 16px)' }}
			>
				{isLoadingPage || isLoadingDetail ? (
					<Card className="relative shadow-lg">
						<CardContent className="p-8">
							<div className="text-center text-gray-400 py-10">
								불러오는 중...
							</div>
						</CardContent>
					</Card>
				) : (
					<div className="grid grid-cols-12 gap-6">
						{/* Center: 문서 본문 패널만 유지 (가로 비율) */}
						<div
							className={`col-span-12 ${!isLoadingTips && tips?.length > 0 ? 'lg:col-span-9' : 'lg:col-span-12'}`}
						>
							<Card className={`relative shadow-lg ${bgMap[backgroundColor]}`}>
								<CardContent className="p-6">
									{page ? (
										<div ref={stageContainerRef} className="w-full">
											<div
												className="w-full mx-auto overflow-hidden rounded-md"
												style={{
													height:
														'calc(100svh - var(--viewer-header-h, 60px) - var(--viewer-footer-h, 88px) - 16px)',
												}}
											>
												<ScrollArea key={currentPage} className="h-full w-full">
													<div
														className={`p-4 rb-typo ${fontMap[fontFamily]} ${textColorClass} ${readingFocusMode ? 'reading-focus' : ''}`}
													>
														<DocumentRenderer
															blocks={page.processedContent?.blocks ?? []}
															fontSize={fontSize[0]}
															fontFamily={fontFamily}
															lineSpacing={lineSpacing[0]}
															documentId={activeTextbookId}
															pageNumber={currentPage}
															activeBlockId={sequentialSpeech.currentBlockId ?? null}
														/>
													</div>
												</ScrollArea>
											</div>
										</div>
									) : (
										<div className="text-center text-gray-400 py-10">
											페이지를 불러올 수 없습니다.
										</div>
									)}
								</CardContent>
							</Card>
						</div>

						{/* Right: 학습 팁 패널 */}
						{!isLoadingTips && tips?.length > 0 && (
							<div className="col-span-12 lg:col-span-3">
								<Card className="relative shadow-lg">
									<CardContent className="p-6">
										<PageTips tips={tips} fontSize={fontSize[0]} />
									</CardContent>
								</Card>
							</div>
						)}
					</div>
				)}
			</main>

			<footer
				ref={footerRef}
				className="sticky bottom-0 z-50 bg-white/95 backdrop-blur-sm border-t border-gray-200 shadow-sm"
			>
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
					<Button
						variant="outline"
						size="lg"
						onClick={() => handlePageChange('prev')}
						disabled={currentPage <= 1}
					>
						<ChevronLeft className="w-5 h-5 mr-2" /> 이전
					</Button>

					<div className="flex-1 mx-8">
						<div className="flex items-center justify-between mb-2">
							<span className="text-sm text-gray-600">읽기 진행률</span>
							<span className="text-sm font-medium text-primary">
								{totalPages > 0
									? Math.round((currentPage / totalPages) * 100)
									: 0}
								%
							</span>
						</div>
						<div className="w-full bg-gray-200 rounded-full h-3 relative overflow-hidden">
							<div
								className="bg-gradient-to-r from-primary to-primary/80 rounded-full h-3 transition-all duration-500 relative"
								style={{
									width: `${totalPages > 0 ? (currentPage / totalPages) * 100 : 0}%`,
								}}
							>
								<div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
							</div>
						</div>
					</div>

					<Button
						variant="outline"
						size="lg"
						onClick={() => handlePageChange('next')}
						disabled={totalPages === 0 || currentPage >= totalPages}
					>
						다음 <ChevronRight className="w-5 h-5 ml-2" />
					</Button>
				</div>
			</footer>
		</div>
	);
}
