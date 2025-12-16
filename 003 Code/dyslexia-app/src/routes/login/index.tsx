import LoginPage from '@page/login';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/login/')({
	component: RouteComponent,
});

function RouteComponent() {
	return <LoginPage />;
}
