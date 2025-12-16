import { Button } from '@/shared/ui/button';
import { Card, CardContent, CardHeader } from '@/shared/ui/card';
import { Typography } from '@/shared/ui/typography';
import { CheckCircle, Copy, Mail, MessageCircle, Share2 } from 'lucide-react';
import { type KeyboardEvent, useEffect, useState } from 'react';
import ReactDOM from 'react-dom';

interface StudentInviteModalProps {
	isOpen: boolean;
	onClose: () => void;
}

export default function StudentInviteModal({
	isOpen,
	onClose,
}: StudentInviteModalProps) {
	const [copied, setCopied] = useState(false);
	const [matchCode, setMatchCode] = useState<string | null>(null);
	const [loading, setLoading] = useState(false);

	useEffect(() => {
		if (!isOpen) return;
		const clientId = localStorage.getItem('clientId');
		const accessToken = localStorage.getItem('accessToken');

		if (!clientId) {
			console.error('clientId not found in localStorage');
			return;
		}

		if (!accessToken) {
			console.error('accessToken not found in localStorage');
			return;
		}

		setLoading(true);
		(async () => {
			try {
				const resp2 = await fetch(
					`${import.meta.env.VITE_API_BASE_URL}/guardian/code`,
					{
						method: 'GET',
						headers: {
							'Content-Type': 'application/json',
							Authorization: `Bearer ${accessToken}`,
						},
					},
				);

				if (!resp2.ok) throw new Error('Failed to fetch invitation code');

				const data2 = await resp2.json();
				setMatchCode(data2.result.matchCode);
			} catch (error) {
				console.error(error);
			} finally {
				setLoading(false);
			}
		})();
	}, [isOpen]);

	if (!isOpen) return null;

	const inviteLink = matchCode ? `${matchCode}` : '';
	const displayLink = loading ? '생성 중...' : inviteLink || '코드 없음';

	const handleCopyLink = async () => {
		if (!inviteLink) return;
		try {
			await navigator.clipboard.writeText(inviteLink);
			setCopied(true);
			setTimeout(() => setCopied(false), 3000);
		} catch (e) {
			console.error(e);
		}
	};

	const handleBackdropKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
		if (e.key === 'Enter' || e.key === ' ') onClose();
	};

	return ReactDOM.createPortal(
		<div className="fixed inset-0 z-50 flex items-center justify-center">
			<div
				className="absolute inset-0 bg-black bg-opacity-30"
				onClick={onClose}
				role="button"
				tabIndex={0}
				onKeyDown={handleBackdropKeyDown}
				aria-label="Close modal"
			/>

			<Card className="relative w-full max-w-lg rounded-xl bg-white shadow-lg z-10">
				<CardHeader className="flex items-center justify-between px-6 py-4 border-b">
					<div className="flex items-center space-x-2">
						<Share2 className="w-5 h-5 text-blue-600" />
						<Typography variant="h4" className="font-semibold">
							학생 초대 코드
						</Typography>
					</div>
					<button
						type="button"
						onClick={onClose}
						className="text-gray-500 hover:text-gray-700"
						aria-label="Close"
					>
						×
					</button>
				</CardHeader>

				<CardContent className="px-6 py-4 space-y-6">
					<div className="text-center">
						<Typography variant="p" className="text-gray-600 mb-4">
							아래 코드를 복사하여 학생에게 전달하세요
						</Typography>
						<div className="flex items-center space-x-2 bg-blue-50 border border-blue-200 rounded-lg overflow-hidden">
							<Typography
								variant="p"
								className="flex-1 bg-white px-4 py-2 text-sm text-gray-700 break-all"
							>
								{displayLink}
							</Typography>
							<Button
								type="button"
								size="sm"
								onClick={handleCopyLink}
								disabled={!inviteLink}
								className={copied ? 'bg-green-600 hover:bg-green-700' : ''}
							>
								{copied ? (
									<CheckCircle className="w-4 h-4" />
								) : (
									<Copy className="w-4 h-4" />
								)}
							</Button>
						</div>
					</div>

					<div className="space-y-4">
						<Typography
							variant="p"
							className="text-center text-gray-700 font-medium"
						>
							코드 전달 방법
						</Typography>
						<div className="space-y-3">
							<div className="flex items-start space-x-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
								<MessageCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
								<div>
									<Typography
										variant="p"
										className="text-yellow-800 font-medium"
									>
										카카오톡으로 전달
									</Typography>
									<Typography
										variant="p"
										className="text-yellow-700 text-sm mt-1"
									>
										1. 카톡 열고 학생 채팅방 이동
										<br />
										2. 복사한 코드 붙여넣기 후 전송
									</Typography>
								</div>
							</div>
							<div className="flex items-start space-x-3 p-4 bg-green-50 border border-green-200 rounded-lg">
								<Mail className="w-5 h-5 text-green-600 mt-0.5" />
								<div>
									<Typography
										variant="p"
										className="text-green-800 font-medium"
									>
										문자 메시지로 전달
									</Typography>
									<Typography
										variant="p"
										className="text-green-700 text-sm mt-1"
									>
										1. 문자 앱 열고 학생 선택
										<br />
										2. 복사한 코드 붙여넣기 후 전송
									</Typography>
								</div>
							</div>
						</div>
					</div>

					<div className="flex items-start p-4 bg-amber-50 border border-amber-200 rounded-lg">
						<span className="text-amber-600 text-xl mr-3">💡</span>
						<Typography variant="p" className="text-amber-800 text-sm">
							<strong>안내:</strong> 이 링크로 가입한 학생은 자동으로
							연결됩니다.
						</Typography>
					</div>

					<div className="flex justify-end">
						<Button type="button" variant="outline" size="sm" onClick={onClose}>
							닫기
						</Button>
					</div>
				</CardContent>
			</Card>
		</div>,
		document.body,
	);
}
