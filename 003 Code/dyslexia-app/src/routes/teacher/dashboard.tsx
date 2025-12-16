import { TeacherDashboardPage } from '@/page/teacher';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/teacher/dashboard')({
	component: RouteComponent,
});

function RouteComponent() {
	return (
		<div>
			<TeacherDashboardPage />
		</div>
	);
}
