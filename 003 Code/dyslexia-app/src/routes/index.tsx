import { BaseLayout } from '@/features/layouts/base-layout';
import LandingPage from '@/page/landing';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/')({
	component: Landing,
});

export function Landing() {
	return (
		<BaseLayout>
			<LandingPage />
		</BaseLayout>
	);
}
