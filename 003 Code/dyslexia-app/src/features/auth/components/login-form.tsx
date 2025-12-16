import { Button } from '@/components/ui/button';
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { useNavigate } from '@tanstack/react-router';
import { ArrowLeft, Book } from 'lucide-react';

const Login = () => {
	const navigate = useNavigate();
	const { toast } = useToast();

	const handleKakaoLogin = () => {
		const REST_API_KEY = import.meta.env.VITE_KAKAO_CLIENT_ID;
		const REDIRECT_URI = import.meta.env.VITE_KAKAO_REDIRECT_URI;
		const kakaoAuthUrl = `https://kauth.kakao.com/oauth/authorize?client_id=${REST_API_KEY}&redirect_uri=${REDIRECT_URI}&response_type=code`;
		window.location.href = kakaoAuthUrl;
	};

	return (
		<div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50 font-dyslexic flex items-center justify-center p-4">
			<div className="w-full max-w-md">
				<div className="text-center mb-8">
					<button
						onClick={() => navigate({ to: '/' })}
						className="inline-flex items-center space-x-2 text-gray-600 hover:text-primary mb-6 transition-colors"
					>
						<ArrowLeft className="w-4 h-4" />
						<span>홈으로 돌아가기</span>
					</button>

					<div className="flex items-center justify-center space-x-3 mb-4">
						<div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
							<Book className="w-7 h-7 text-white" />
						</div>
						<h1 className="text-3xl font-bold text-gray-800">리딩브릿지</h1>
					</div>
					<p className="text-gray-600 leading-dyslexic tracking-dyslexic">
						다시 만나서 반가워요!
					</p>
				</div>

				<Card className="border-gray-200 shadow-lg">
					<CardHeader className="text-center pb-4">
						<CardTitle className="text-2xl font-bold text-gray-800">
							로그인
						</CardTitle>
						<CardDescription className="text-gray-600 leading-dyslexic tracking-dyslexic">
							카카오 계정으로 간편하게 로그인하세요
						</CardDescription>
					</CardHeader>

					<CardContent className="space-y-6">
						<Button
							onClick={handleKakaoLogin}
							className="w-full h-12 bg-yellow-400 hover:bg-yellow-500 text-yellow-900 text-base font-medium"
						>
							카카오로 로그인
						</Button>

						<div className="text-center">
							<p className="text-gray-600 leading-dyslexic tracking-dyslexic">
								아직 계정이 없으신가요?{' '}
								<button
									onClick={() => navigate({ to: '/signup' })}
									className="text-primary hover:underline font-medium"
								>
									회원가입하기
								</button>
							</p>
						</div>
					</CardContent>
				</Card>
			</div>
		</div>
	);
};

export default Login;
