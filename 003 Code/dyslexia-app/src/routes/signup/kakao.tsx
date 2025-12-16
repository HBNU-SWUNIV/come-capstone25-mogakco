import { KakaoAuthPage } from '@page/signup/kakao';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/signup/kakao')({
	component: KakaoAuthPage,
});
