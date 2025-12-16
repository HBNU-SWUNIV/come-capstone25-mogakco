import { Button } from '@/shared/ui/button';
import { Card } from '@/shared/ui/card';
import { ProgressBar } from '@/shared/ui/progress-bar';
import { Typography } from '@/shared/ui/typography';
import { useNavigate } from '@tanstack/react-router';
import { Book as BookIcon, CalendarDays } from 'lucide-react';

type BookItem = {
	id: string;
	title: string;
	progress: number;
	current: number;
	total: number;
	lastActive: string;
	coverColor: string;
};

const BOOKS: BookItem[] = [
	{
		id: 'b1',
		title: '우리 동네 동물들',
		progress: 65,
		current: 13,
		total: 20,
		lastActive: '어제',
		coverColor: 'bg-gradient-to-br from-orange-400 to-orange-500',
	},
	{
		id: 'b2',
		title: '우주 탐험 이야기',
		progress: 30,
		current: 8,
		total: 25,
		lastActive: '3일 전',
		coverColor: 'bg-gradient-to-br from-blue-400 to-blue-500',
	},
	{
		id: 'b3',
		title: '마법의 숲 모험',
		progress: 0,
		current: 1, //미시작: 1페이지부터
		total: 18,
		lastActive: '아직 읽지 않음',
		coverColor: 'bg-gradient-to-br from-green-400 to-green-500',
	},
];

export default function LibraryView() {
	const navigate = useNavigate();

	const handleRead = (bookId: string, currentPage: number) => {
		navigate({ to: `/student/reader/${bookId}/${currentPage}` });
	};

	return (
		<div className="grid gap-4">
			{BOOKS.map((book) => {
				const isNotStarted = book.progress === 0;
				const buttonText = isNotStarted ? '시작' : '계속';

				return (
					<Card
						key={book.id}
						className="border-0 shadow-md hover:shadow-xl transition-all duration-300 cursor-pointer group rounded-2xl overflow-hidden"
					>
						<div className="p-6">
							<div className="flex items-center space-x-4">
								<div
									className={`${book.coverColor} w-16 h-20 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform duration-300 flex-shrink-0`}
								>
									<BookIcon className="w-6 h-6 text-white opacity-80" />
								</div>

								<div className="flex-1 min-w-0">
									<Typography
										variant="p"
										weight="bold"
										className="text-lg text-gray-800 mb-2 truncate"
									>
										{book.title}
									</Typography>

									<div className="space-y-2">
										<div className="flex items-center justify-between text-sm">
											<span className="text-gray-600">진행률</span>
											<span className="font-medium text-primary">
												{book.progress}%
											</span>
										</div>

										<ProgressBar progress={book.progress} className="h-2" />

										<div className="flex items-center justify-between text-xs text-gray-500">
											<div className="flex items-center space-x-1">
												<CalendarDays className="w-3 h-3" />
												<span>{book.lastActive}</span>
											</div>
											<span>
												{book.current}/{book.total} 페이지
											</span>
										</div>
									</div>
								</div>

								<Button
									onClick={(e) => {
										e.stopPropagation();
										handleRead(book.id, book.current);
									}}
									//variant={isNotStarted ? "outline" : "default"} //시작/계속 구분할 때
									variant="default"
									size="sm"
									className="rounded-xl flex-shrink-0"
								>
									{buttonText}
								</Button>
							</div>
						</div>
					</Card>
				);
			})}
		</div>
	);
}
