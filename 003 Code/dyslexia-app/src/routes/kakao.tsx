import { axiosClient } from '@/shared/api/axios';
import { useToken } from '@/shared/hooks/use-token';
import { Spinner } from '@/shared/ui';
import { storage } from '@/shared/utils/storage';
import {
	createFileRoute,
	useNavigate,
	useSearch,
} from '@tanstack/react-router';
import { useEffect, useRef, useState } from 'react';

interface KakaoSearch {
	code?: string;
}

interface AuthResult {
	registered: boolean;
	clientId: string;
	nickname: string;
	userType: 'STUDENT' | 'TEACHER' | 'GUARDIAN' | 'UNREGISTERED';
	accessToken?: string;
	refreshToken?: string;
}

interface AuthResponse {
	timestamp: string;
	code: number;
	message: string;
	result: AuthResult;
}

export const Route = createFileRoute('/kakao')({
	component: KakaoCallback,
	validateSearch: (search: Record<string, unknown>): KakaoSearch => {
		return {
			code: search.code as string | undefined,
		};
	},
});

function KakaoCallback() {
	const [isLoading, setIsLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const navigate = useNavigate();
	const { code } = useSearch({ from: '/kakao' });
	const { setTokens } = useToken();
	const isProcessed = useRef(false);

	useEffect(() => {
		const handleCallback = async () => {
			if (isProcessed.current) return;
			isProcessed.current = true;

			try {
				if (!code) {
					throw new Error('인증 코드가 없습니다.');
				}

				const response = (await axiosClient.get('/kakao/callback', {
					params: {
						code,
					},
				})) as unknown as AuthResponse;

				console.log('카카오 콜백 전체 응답:', response);

				const data = response.result;
				console.log('카카오 콜백 결과:', data);

				if (data.registered) {
					// 이미 가입된 사용자
					if (data.accessToken && data.refreshToken) {
						setTokens(data.accessToken, data.refreshToken);

						// userType에 따라 적절한 대시보드로 리다이렉트
						if (data.userType === 'TEACHER' || data.userType === 'GUARDIAN') {
							navigate({ to: '/teacher/dashboard' });
						} else if (data.userType === 'STUDENT') {
							navigate({ to: '/' }); // 학생은 홈 페이지로
						} else {
							navigate({ to: '/' });
						}
					} else {
						console.error('토큰이 없습니다:', data);
						navigate({ to: '/' });
					}
				} else {
					// 미가입 사용자 - 바로 해당 역할의 회원가입 페이지로 이동
					storage.setClientId(data.clientId);

					if (data.userType === 'STUDENT') {
						navigate({ to: '/signup/student' });
					} else if (data.userType === 'GUARDIAN') {
						navigate({ to: '/signup/teacher' }); // GUARDIAN은 teacher 회원가입 사용
					} else {
						// 알 수 없는 userType인 경우 역할 선택 페이지로
						navigate({
							to: '/signup',
							search: {
								nickname: data.nickname,
								userType: data.userType,
							},
						});
					}
				}
			} catch (err) {
				console.error('카카오 로그인 처리 중 오류:', err);
				setError(
					err instanceof Error
						? err.message
						: '알 수 없는 오류가 발생했습니다.',
				);
			} finally {
				setIsLoading(false);
			}
		};

		handleCallback();
	}, [code, navigate, setTokens]);

	if (isLoading) {
		return (
			<div className="flex min-h-screen items-center justify-center">
				<div className="text-center">
					<div className="w-full flex justify-center">
						<Spinner className="mb-4 h-12 w-12" />
					</div>
					<h1 className="mb-2 text-2xl font-bold">카카오 로그인 처리 중</h1>
					<p className="text-gray-600">잠시만 기다려주세요...</p>
				</div>
			</div>
		);
	}

	if (error) {
		return (
			<div className="flex min-h-screen items-center justify-center">
				<div className="text-center">
					<h1 className="mb-4 text-2xl font-bold text-red-600">오류 발생</h1>
					<p className="text-gray-600">{error}</p>
					<button
						onClick={() => navigate({ to: '/' })}
						className="mt-4 rounded-md bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
						type="button"
					>
						홈으로 돌아가기
					</button>
				</div>
			</div>
		);
	}

	return null;
}
