import SignupPage from '@page/signup';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/signup/')({
	component: RouteComponent,
});

function RouteComponent() {
	return <SignupPage />;
}
