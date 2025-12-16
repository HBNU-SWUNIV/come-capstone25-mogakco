import { StorePage } from '@/page/teacher';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/teacher/store')({
	component: RouteComponent,
});

function RouteComponent() {
	return (
		<div>
			<StorePage />
		</div>
	);
}
