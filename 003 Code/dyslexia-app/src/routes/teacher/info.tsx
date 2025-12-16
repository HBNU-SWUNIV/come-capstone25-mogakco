import InfoPage from '@/page/teacher/info';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/teacher/info')({
	component: RouteComponent,
});

function RouteComponent() {
	return (
		<div>
			<InfoPage />
		</div>
	);
}
