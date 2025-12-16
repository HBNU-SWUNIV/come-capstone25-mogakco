import { useNavigate } from '@tanstack/react-router';
import { useEffect, useRef } from 'react';

type KakaoCallbackResponse = {
	registered: boolean;
	clientId: string;
	nickname: string;
	userType: 'GUARDIAN' | 'STUDENT' | string;
	accessToken: string | null;
	refreshToken: string | null;
};

type ServerResponse = {
	code: number;
	message: string;
	timestamp: string;
	result: KakaoCallbackResponse;
};

export function KakaoCallback() {
	const navigate = useNavigate();
	const hasRequested = useRef(false);

	useEffect(() => {
		if (hasRequested.current) {
			return;
		}
		hasRequested.current = true;

		const params = new URLSearchParams(window.location.search);
		const code = params.get('code');
		const callbackUri = import.meta.env.VITE_KAKAO_REDIRECT_URI;

		if (!code || !callbackUri) {
			console.error('Missing code or callback URI', { code, callbackUri });
			alert(
				'로그인 코드 또는 설정된 콜백 URI가 없습니다. 로그인 페이지로 이동합니다.',
			);
			navigate({ to: '/login' });
			return;
		}

		const requestUrl = `${import.meta.env.VITE_API_BASE_URL}/kakao/callback?code=${encodeURIComponent(code)}`;
		console.debug('Requesting Kakao callback:', requestUrl);

		fetch(requestUrl, { method: 'GET' })
			.then(async (res) => {
				const text = await res.text();
				let parsed: ServerResponse;

				try {
					parsed = JSON.parse(text);
				} catch {
					throw new Error(`응답 파싱 실패: ${text || res.statusText}`);
				}

				if (!res.ok) {
					const message = parsed?.message || `HTTP ${res.status}`;
					throw new Error(message);
				}

				return parsed.result;
			})
			.then((data: KakaoCallbackResponse) => {
				console.debug('Callback response data:', data);
				alert(
					`Callback Response: registered: ${data.registered}\n` +
						`clientId: ${data.clientId}\n` +
						`nickname: ${data.nickname}\n` +
						`userType: ${data.userType}\n` +
						`accessToken: ${data.accessToken}\n` +
						`refreshToken: ${data.refreshToken}`,
				);

				if (data.registered && data.accessToken && data.refreshToken) {
					localStorage.setItem('accessToken', data.accessToken);
					localStorage.setItem('refreshToken', data.refreshToken);
					localStorage.setItem('clientId', data.clientId);
					localStorage.setItem('userType', data.userType);

					switch (data.userType) {
						case 'GUARDIAN':
							navigate({ to: '/teacher/dashboard' });
							break;
						case 'STUDENT':
							navigate({ to: '/student/library' });
							break;
						default:
							navigate({ to: '/' });
					}
				} else {
					alert('등록되지 않은 사용자입니다. 회원가입 페이지로 이동합니다.');
					navigate({ to: '/signup' });
				}
			})
			.catch((error: unknown) => {
				const msg = error instanceof Error ? error.message : String(error);
				console.error('Unhandled error in KakaoCallback:', msg);
				alert(`오류 발생: ${msg}\n홈으로 이동합니다.`);
				navigate({ to: '/' });
			});
	}, [navigate]);

	return (
		<div className="flex items-center justify-center min-h-screen text-gray-500">
			<p>로그인 처리 중입니다…</p>
		</div>
	);
}
