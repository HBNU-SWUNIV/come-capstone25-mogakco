import { useAuth } from '@/shared/hooks/use-auth';
import { Button } from '@/shared/ui/button';
import { Typography } from '@/shared/ui/typography';
import { Link, useMatchRoute } from '@tanstack/react-router';
import clsx from 'clsx';
import { BarChart3, Book, FolderOpen, User, Users } from 'lucide-react';

const navItems = [
	{ name: '대시보드', href: '/teacher/dashboard', icon: BarChart3 },
	{ name: '학생 관리', href: '/teacher/student', icon: Users },
	{ name: '교안 보관함', href: '/teacher/content', icon: FolderOpen },
	{ name: '내 정보', href: '/teacher/info', icon: User },
];

export function TopHeader() {
	const { my } = useAuth();
	const matchRoute = useMatchRoute();

	return (
		<header className="bg-white border-b border-gray-200 shadow-sm">
			<div className="max-w-7xl mx-auto flex items-center justify-between px-4 sm:px-6 lg:px-8 py-4">
				<div className="flex items-center space-x-6">
					<Link to="/" className="flex items-center space-x-3">
						<div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
							<Book className="w-6 h-6 text-white" />
						</div>
						<div className="flex flex-col">
							<Typography variant="h4" className="font-semibold text-gray-800">
								리딩브릿지
							</Typography>
							<Typography variant="p" className="text-xs text-gray-500">
								보호자 대시보드
							</Typography>
						</div>
					</Link>

					<nav className="hidden md:flex items-center space-x-8">
						{navItems.map(({ name, href, icon: Icon }) => {
							const params = matchRoute({ to: href, fuzzy: true });
							const isActive = params !== false;

							return (
								<Link
									key={href}
									to={href}
									className={clsx(
										'flex items-center space-x-2 px-3 py-2 rounded-full text-sm font-medium transition-colors',
										isActive
											? 'bg-blue-50 text-blue-600'
											: 'text-gray-600 hover:text-gray-800 hover:bg-gray-50',
									)}
								>
									<Icon
										className={clsx(
											'w-4 h-4',
											isActive ? 'text-blue-600' : 'text-gray-400',
										)}
									/>
									<span>{name}</span>
								</Link>
							);
						})}
					</nav>
				</div>

				<div className="flex items-center space-x-4">
					<Typography variant="p" size="sm" className="text-gray-700">
						{my ? my.name : '로그인 필요'}
					</Typography>
					<Button size="sm" variant="outline">
						{my ? '로그아웃' : '로그인'}
					</Button>
				</div>
			</div>
		</header>
	);
}
