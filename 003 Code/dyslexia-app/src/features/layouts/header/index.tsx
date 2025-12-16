import { Button } from '@/shared/ui/button';
import { Typography } from '@/shared/ui/typography';
import { Link } from '@tanstack/react-router';

export default function Header() {
	return (
		<header className="w-full px-4 py-4 border-b border-gray-200 bg-white sticky top-0 z-50">
			<div className="max-w-7xl mx-auto flex justify-between items-center">
				<Link to="/">
					<Typography
						as="h1"
						variant="h3"
						weight="bold"
						className="text-[#007AFF] text-lg sm:text-xl"
					>
						리딩브릿지
					</Typography>
				</Link>

				<div className="flex gap-2 sm:gap-3 items-center">
					<Link to="/login">
						<Button
							variant="ghost"
							className="text-sm sm:text-base text-gray-700 border border-gray-200 hover:bg-gray-100 rounded-md px-4 sm:px-6 py-1.5"
						>
							로그인
						</Button>
					</Link>
					<Link to="/signup">
						<Button className="bg-[#007AFF] hover:bg-[#0066d6] text-white text-sm sm:text-base rounded-md px-4 sm:px-6 py-1.5">
							회원가입
						</Button>
					</Link>
				</div>
			</div>
		</header>
	);
}
