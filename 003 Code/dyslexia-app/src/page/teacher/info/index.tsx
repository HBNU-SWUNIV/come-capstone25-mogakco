import { Button } from '@/shared/ui/button';
import { Card, CardContent } from '@/shared/ui/card';
import { Typography } from '@/shared/ui/typography';
import { Bell, Calendar, LogOut, User } from 'lucide-react';
import { useEffect, useState } from 'react';

type MeResponse = {
	id: number;
	clientId: string;
	name: string;
	organization: string;
	profileImageUrl: string;
};

export default function InfoPage() {
	const [userInfo, setUserInfo] = useState({
		name: '',
		organization: '',
		joinDate: '2024-01-01',
		connectedStudents: 2,
	});

	const [notifications, setNotifications] = useState({
		learningProgress: true,
		weeklyReport: true,
		aiInsights: true,
	});

	const [loading, setLoading] = useState(true);
	const [errorMsg, setErrorMsg] = useState<string | null>(null);

	const handleSaveNotifications = () => {
		alert('알림 설정이 저장되었습니다');
	};

	const handleLogout = () => {
		alert('로그아웃합니다');
	};

	useEffect(() => {
		const controller = new AbortController();
		const API_BASE = import.meta.env.VITE_API_BASE_URL;

		async function fetchMe() {
			try {
				setLoading(true);
				setErrorMsg(null);

				const res = await fetch(`${API_BASE}/guardian/me`, {
					method: 'GET',
					headers: {
						'Content-Type': 'application/json',
					},
					signal: controller.signal,
				});

				if (!res.ok) {
					throw new Error(`요청 실패 (${res.status})`);
				}

				const data: MeResponse = await res.json();

				setUserInfo((prev) => ({
					...prev,
					name: data.name ?? '',
					organization: data.organization ?? '',
				}));
			} catch (err: unknown) {
				const message =
					err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다';
				setErrorMsg(message);
			} finally {
				setLoading(false);
			}
		}

		fetchMe();

		return () => controller.abort();
	}, []);

	return (
		<div className="min-h-screen bg-gradient-to-br from-soft-50 via-white to-warm-50">
			<div className="mx-auto w-full max-w-4xl md:max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
				<div className="mb-8">
					<h2 className="text-3xl font-bold text-gray-800">내 정보</h2>
					<p className="text-gray-600 mt-2">
						프로필 정보와 설정을 관리해보세요
					</p>
				</div>

				{errorMsg && (
					<div className="mb-6 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
						프로필 정보를 불러오지 못했습니다. ({errorMsg})
					</div>
				)}

				<div className="grid gap-8 lg:grid-cols-[2fr_1fr]">
					<div className="space-y-6">
						<Card className="border-gray-200 shadow-sm">
							<CardContent className="p-6 space-y-4">
								<div className="flex items-center space-x-2">
									<User className="w-5 h-5" />
									<Typography as="h3" variant="h4" className="font-semibold">
										기본 정보
									</Typography>
								</div>
								<Typography variant="p" className="text-sm text-gray-600">
									회원가입으로 연결된 정보입니다
								</Typography>

								<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
									<div className="space-y-2">
										<label htmlFor="name" className="text-sm text-gray-700">
											이름
										</label>
										<input
											id="name"
											value={loading ? '불러오는 중...' : userInfo.name || '-'}
											readOnly
											className="w-full border rounded px-3 py-2 text-sm bg-gray-50 cursor-not-allowed"
										/>
									</div>
									<div className="space-y-2">
										<label
											htmlFor="organization"
											className="text-sm text-gray-700"
										>
											소속
										</label>
										<input
											id="organization"
											value={
												loading
													? '불러오는 중...'
													: userInfo.organization || '-'
											}
											readOnly
											className="w-full border rounded px-3 py-2 text-sm bg-gray-50 cursor-not-allowed"
										/>
									</div>
								</div>
							</CardContent>
						</Card>

						<Card className="border-gray-200 shadow-sm">
							<CardContent className="p-6 space-y-5">
								<div className="flex items-center space-x-2">
									<Bell className="w-5 h-5" />
									<Typography as="h3" variant="h4" className="font-semibold">
										알림 설정
									</Typography>
								</div>
								<Typography variant="p" className="text-sm text-gray-600">
									받고 싶은 알림을 설정해보세요
								</Typography>

								<div className="space-y-4">
									<div className="flex items-center justify-between">
										<div>
											<h4 className="font-medium">학습 진행 알림</h4>
											<p className="text-sm text-gray-600">
												학생의 학습 활동을 실시간으로 알려드립니다
											</p>
										</div>
										<input
											type="checkbox"
											checked={notifications.learningProgress}
											onChange={(e) =>
												setNotifications({
													...notifications,
													learningProgress: e.target.checked,
												})
											}
											className="w-4 h-4"
										/>
									</div>

									<div className="flex items-center justify-between">
										<div>
											<h4 className="font-medium">주간 리포트</h4>
											<p className="text-sm text-gray-600">
												매주 학습 현황 요약을 보내드립니다
											</p>
										</div>
										<input
											type="checkbox"
											checked={notifications.weeklyReport}
											onChange={(e) =>
												setNotifications({
													...notifications,
													weeklyReport: e.target.checked,
												})
											}
											className="w-4 h-4"
										/>
									</div>

									<div className="flex items-center justify-between">
										<div>
											<h4 className="font-medium">AI 분석 인사이트</h4>
											<p className="text-sm text-gray-600">
												AI가 분석한 학습 개선 제안을 알려드립니다
											</p>
										</div>
										<input
											type="checkbox"
											checked={notifications.aiInsights}
											onChange={(e) =>
												setNotifications({
													...notifications,
													aiInsights: e.target.checked,
												})
											}
											className="w-4 h-4"
										/>
									</div>
								</div>

								<div className="flex justify-end">
									<Button onClick={handleSaveNotifications} variant="outline">
										알림 설정 저장
									</Button>
								</div>
							</CardContent>
						</Card>
					</div>

					<div className="space-y-6">
						<Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-primary/10">
							<CardContent className="p-6 space-y-4">
								<Typography as="h3" variant="h4" className="text-lg">
									계정 현황
								</Typography>

								<div className="space-y-3 text-sm">
									<div className="flex items-center justify-between">
										<div className="flex items-center space-x-2">
											<Calendar className="w-4 h-4 text-primary" />
											<span>가입일</span>
										</div>
										<span className="font-medium">{userInfo.joinDate}</span>
									</div>

									<div className="flex items-center justify-between">
										<div className="flex items-center space-x-2">
											<User className="w-4 h-4 text-primary" />
											<span>연결된 학생</span>
										</div>
										<span className="font-medium">
											{userInfo.connectedStudents}명
										</span>
									</div>
								</div>
							</CardContent>
						</Card>

						<Card className="border-gray-200 shadow-sm">
							<CardContent className="p-6">
								<div className="flex items-center space-x-2 mb-4">
									<LogOut className="w-5 h-5" />
									<Typography as="h3" variant="h4" className="font-semibold">
										계정
									</Typography>
								</div>

								<Button
									onClick={handleLogout}
									variant="outline"
									className="w-full justify-start text-red-600 border-red-200 hover:bg-red-50"
								>
									<LogOut className="w-4 h-4 mr-2" />
									로그아웃
								</Button>
							</CardContent>
						</Card>
					</div>
				</div>
			</div>
		</div>
	);
}
