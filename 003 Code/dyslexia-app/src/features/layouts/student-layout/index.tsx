import { useState } from 'react';
import { TopHeader } from './ui/top';

interface StudentLayoutProps {
	children?: React.ReactNode;
}

export function StudentLayout({ children }: StudentLayoutProps) {
	const [open, setOpen] = useState(true);

	return (
		<div className="flex min-h-screen bg-gray-50">
			<div className="flex flex-1 flex-col">
				<TopHeader />
				<main className="flex-1 p-6">{children}</main>
			</div>
		</div>
	);
}
