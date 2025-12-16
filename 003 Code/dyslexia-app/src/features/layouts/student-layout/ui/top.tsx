import { useAuth } from '@/shared/hooks/use-auth';
import { Button } from '@/shared/ui/button';
import { Typography } from '@/shared/ui/typography';
import { useNavigate } from '@tanstack/react-router';
import { Book as BookIcon, Palette, User as UserIcon } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

export function TopHeader() {
	const navigate = useNavigate();
	const { my, logout } = useAuth();
	const [menuOpen, setMenuOpen] = useState(false);
	const menuRef = useRef<HTMLDivElement | null>(null);

	useEffect(() => {
		const onClick = (e: MouseEvent) => {
			if (!menuRef.current) return;
			if (!menuRef.current.contains(e.target as Node)) setMenuOpen(false);
		};
		document.addEventListener('mousedown', onClick);
		return () => {
			document.removeEventListener('mousedown', onClick);
		};
	}, []);

	return (
		<header className="bg-white/80 backdrop-blur-sm border-b border-gray-200/50 shadow-sm sticky top-0 z-10">
			<div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
				<button
					type="button"
					onClick={() => navigate({ to: '/student/library' })}
					className="flex items-center gap-3 focus:outline-none"
				>
					<div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary shadow-md">
						<BookIcon className="h-6 w-6 text-white" />
					</div>
					<div className="text-left">
						<Typography
							variant="h4"
							className="text-2xl font-bold text-gray-800"
						>
							리딩브릿지
						</Typography>
						<Typography variant="p" size="sm" className="text-gray-600">
							나의 책장
						</Typography>
					</div>
				</button>

				<div className="relative flex items-center gap-4" ref={menuRef}>
					<Button
						type="button"
						variant="outline"
						onClick={() => navigate({})}
						className="rounded-xl border-warm-400 text-warm-600 hover:bg-warm-50"
						size="sm"
					>
						<Palette className="mr-2 h-4 w-4" />
						AI 친구
					</Button>

					<button
						type="button"
						aria-haspopup="menu"
						aria-expanded={menuOpen}
						onClick={() => setMenuOpen((v) => !v)}
						className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-warm-400 to-warm-500 shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-warm-300"
					>
						<UserIcon className="h-6 w-6 text-white" />
					</button>

					{menuOpen && (
						<ul
							role="menu"
							className="absolute right-0 top-12 mt-2 w-48 overflow-hidden rounded-xl border border-gray-200 bg-white text-sm shadow-lg"
						>
							<li role="none">
								<button
									role="menuitem"
									type="button"
									className="block w-full px-4 py-2 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none"
									onClick={() => {
										navigate({});
										setMenuOpen(false);
									}}
								>
									회원정보 수정
								</button>
							</li>
							<li role="none">
								<button
									role="menuitem"
									type="button"
									className="block w-full px-4 py-2 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none"
									onClick={() => {
										logout();
										setMenuOpen(false);
										navigate({ to: '/' });
									}}
								>
									로그아웃
								</button>
							</li>
						</ul>
					)}
				</div>
			</div>
		</header>
	);
}
