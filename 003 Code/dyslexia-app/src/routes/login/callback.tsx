import { createFileRoute } from '@tanstack/react-router';
import { KakaoCallback } from '../../features/auth/components/kakao-callback';

export const Route = createFileRoute('/login/callback')({
	component: RouteComponent,
});

function RouteComponent() {
	return <KakaoCallback />;
}
