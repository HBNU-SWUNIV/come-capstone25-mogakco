import ContentManagePage from '@/page/teacher/content';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/teacher/content')({
	component: RouteComponent,
});

function RouteComponent() {
	return <ContentManagePage />;
}
