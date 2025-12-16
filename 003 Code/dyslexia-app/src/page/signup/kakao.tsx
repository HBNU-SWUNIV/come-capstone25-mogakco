import { Button } from '@/shared/ui/button';
import { createFileRoute } from '@tanstack/react-router';
import { useEffect, useState } from 'react';
import { z } from 'zod';

const searchSchema = z.object({
	userType: z.enum(['STUDENT', 'GUARDIAN']),
});

type SearchType = z.infer<typeof searchSchema>;

export const Route = createFileRoute('/signup/kakao')({
	validateSearch: (search) => searchSchema.parse(search),
	component: KakaoAuthPage,
});

export function KakaoAuthPage() {
	const search = Route.useSearch() as SearchType;
	const { userType } = search;
	const [loading, setLoading] = useState(false);
	const navigate = Route.useNavigate();

	const handleKakaoAuth = () => {
		const redirectUri = import.meta.env.VITE_KAKAO_REDIRECT_URI;
		const kakaoAuthUrl = `https://kauth.kakao.com/oauth/authorize?client_id=${import.meta.env.VITE_KAKAO_CLIENT_ID}&redirect_uri=${redirectUri}&response_type=code`;
		window.location.href = kakaoAuthUrl;
	};

	useEffect(() => {
		const urlParams = new URLSearchParams(window.location.search);
		const code = urlParams.get('code');
		const alreadyFetched = sessionStorage.getItem('kakaoTokenFetched');

		if (!code || alreadyFetched) return;
		sessionStorage.setItem('kakaoTokenFetched', 'true');

		const fetchKakaoTokenAndUserInfo = async () => {
			setLoading(true);
			try {
				const data = new URLSearchParams();
				data.append('grant_type', 'authorization_code');
				data.append('client_id', import.meta.env.VITE_KAKAO_CLIENT_ID);
				data.append(
					'redirect_uri',
					`${window.location.origin}/signup/kakao?userType=${userType}`,
				);
				data.append('code', code);
				data.append('client_secret', import.meta.env.VITE_KAKAO_CLIENT_SECRET);

				const response = await fetch('https://kauth.kakao.com/oauth/token', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
					},
					body: data,
				});

				const tokenData = await response.json();
				console.log('카카오 tokenData:', tokenData);

				if (!tokenData.access_token) {
					alert(
						`카카오 인증 실패: ${tokenData.error_description || JSON.stringify(tokenData)}`,
					);
					return;
				}

				const userInfoRes = await fetch('https://kapi.kakao.com/v2/user/me', {
					method: 'GET',
					headers: {
						Authorization: `Bearer ${tokenData.access_token}`,
						'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
					},
				});

				const userInfo = await userInfoRes.json();
				console.log('카카오 userInfo:', userInfo);

				if (userInfo.id) {
					localStorage.setItem('clientId', userInfo.id.toString());
					localStorage.setItem('userType', userType);

					navigate({
						to: userType === 'STUDENT' ? '/signup/student' : '/signup/teacher',
						replace: true,
					});
				} else {
					alert('카카오 사용자 정보 조회 실패: 사용자 ID가 없습니다.');
				}
			} catch (error) {
				console.error('카카오 인증 오류:', error);
				alert('카카오 인증 처리 중 오류가 발생했습니다.');
			} finally {
				setLoading(false);
			}
		};

		fetchKakaoTokenAndUserInfo();
	}, [userType, navigate]);

	return (
		<div className="min-h-screen flex flex-col items-center justify-center space-y-4">
			<h2 className="text-xl font-semibold">카카오 인증</h2>
			<p className="text-gray-600 text-sm">카카오톡으로 인증을 진행해주세요.</p>
			<Button
				type="button"
				onClick={handleKakaoAuth}
				disabled={loading}
				className="bg-yellow-400 hover:bg-yellow-500 text-black"
			>
				{loading ? '인증 중...' : '카카오톡으로 인증하기'}
			</Button>
		</div>
	);
}
