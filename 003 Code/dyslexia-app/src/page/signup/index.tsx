import { Button } from '@/components/ui/button';
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from '@/components/ui/card';
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { ArrowLeft, Book, User, Users } from 'lucide-react';

export const Route = createFileRoute('/signup/')({
	component: SignupRoleSelect,
});

function SignupRoleSelect() {
	const navigate = useNavigate();

	const handleRoleSelect = (role: 'STUDENT' | 'GUARDIAN') => {
		localStorage.setItem('userType', role);
		navigate({
			to: '/signup/kakao',
			search: { userType: role },
		});
	};

	return (
		<div className="min-h-screen bg-gradient-to-br from-[#f0f9ff] to-[#fffaf4] flex items-center justify-center px-4 py-10">
			<div className="w-full max-w-3xl">
				<div className="text-center mb-8">
					<button
						onClick={() => navigate({ to: '/' })}
						className="inline-flex items-center space-x-2 text-sm text-gray-500 hover:text-primary mb-6 transition-colors"
					>
						<ArrowLeft className="w-4 h-4" />
						<span>홈으로 돌아가기</span>
					</button>

					<div className="flex items-center justify-center space-x-3 mb-4">
						<div className="w-12 h-12 bg-[#0078FF] rounded-full flex items-center justify-center">
							<Book className="w-7 h-7 text-white" />
						</div>
						<h1 className="text-3xl font-bold text-[#1f1f1f]">리딩브릿지</h1>
					</div>
					<p className="text-gray-600 text-sm">
						리딩브릿지와 함께 읽기 자신감을 키워보세요
					</p>
				</div>

				<Card className="bg-white p-8 rounded-xl shadow-md border max-w-3xl mx-auto">
					<CardHeader className="text-center pb-6">
						<CardTitle className="text-2xl font-bold">회원가입</CardTitle>
						<CardDescription className="text-gray-600">
							어떤 역할로 리딩브릿지를 시작하시나요?
						</CardDescription>
					</CardHeader>

					<CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
						<button
							type="button"
							onClick={() => handleRoleSelect('GUARDIAN')}
							className="rounded-lg border hover:shadow-md transition p-6 text-left border-blue-200 hover:border-blue-400"
						>
							<div className="flex items-center gap-3 mb-3">
								<div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
									<Users className="text-blue-500 w-5 h-5" />
								</div>
								<h3 className="text-base font-semibold">보호자</h3>
							</div>
							<p className="text-sm text-gray-600 mb-2">
								부모님 또는 교사로서 아이의 학습을 관리하고 지원해요
							</p>
							<ul className="list-disc list-inside text-sm text-blue-600 space-y-1">
								<li>PDF 교안 업로드 및 변환</li>
								<li>학습 진도 및 분석 리포트</li>
								<li>아동 초대 및 관리</li>
							</ul>
						</button>

						<button
							type="button"
							onClick={() => handleRoleSelect('STUDENT')}
							className="rounded-lg border hover:shadow-md transition p-6 text-left border-orange-200 hover:border-orange-400"
						>
							<div className="flex items-center gap-3 mb-3">
								<div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
									<User className="text-orange-500 w-5 h-5" />
								</div>
								<h3 className="text-base font-semibold">아동(학생)</h3>
							</div>
							<p className="text-sm text-gray-600 mb-2">
								학습의 주인공으로서 나만의 속도로 즐겁게 공부해요
							</p>
							<ul className="list-disc list-inside text-sm text-orange-600 space-y-1">
								<li>맞춤형 인터랙티브 리더</li>
								<li>TTS 및 접근성 도구</li>
								<li>AI 학습 친구와 상호작용</li>
							</ul>
						</button>
					</CardContent>

					<div className="mt-8 text-center text-sm text-gray-600">
						이미 계정이 있으신가요?{' '}
						<button
							onClick={() => navigate({ to: '/login' })}
							className="text-blue-600 font-medium hover:underline"
						>
							로그인하기
						</button>
					</div>
				</Card>
			</div>
		</div>
	);
}

export default SignupRoleSelect;
