import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
	Dialog,
	DialogContent,
	DialogHeader,
	DialogTitle,
} from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { CheckCircle, Copy, Mail, MessageCircle, Share2 } from 'lucide-react';
import { useState } from 'react';

interface StudentInviteModalProps {
	isOpen: boolean;
	onClose: () => void;
}

const StudentInviteModal = ({ isOpen, onClose }: StudentInviteModalProps) => {
	const { toast } = useToast();
	const [copied, setCopied] = useState(false);

	const inviteLink = 'https://reading-bridge.app/signup/student?code=ABC123';

	const handleCopyLink = async () => {
		try {
			await navigator.clipboard.writeText(inviteLink);
			setCopied(true);
			toast({
				title: '링크가 복사되었습니다! 📋',
				description: '카카오톡이나 메시지로 학생에게 전달해주세요.',
			});

			// Reset copied state after 3 seconds
			setTimeout(() => {
				setCopied(false);
			}, 3000);
		} catch (err) {
			console.error('Failed to copy link:', err);
			toast({
				title: '복사 실패',
				description: '링크를 수동으로 복사해주세요.',
				variant: 'destructive',
			});
		}
	};

	return (
		<Dialog open={isOpen} onOpenChange={onClose}>
			<DialogContent className="sm:max-w-lg">
				<DialogHeader>
					<DialogTitle className="flex items-center space-x-2">
						<Share2 className="w-5 h-5 text-blue-600" />
						<span>학생 초대 링크</span>
					</DialogTitle>
				</DialogHeader>

				<div className="space-y-6">
					<div className="text-center">
						<p className="text-gray-600 mb-4">
							아래 링크를 복사하여 학생에게 전달해주세요
						</p>

						<Card className="bg-blue-50 border-blue-200">
							<CardContent className="p-4">
								<div className="flex items-center space-x-2">
									<div className="flex-1 text-sm text-gray-700 bg-white p-3 rounded border break-all">
										{inviteLink}
									</div>
									<Button
										size="sm"
										onClick={handleCopyLink}
										className={`${copied ? 'bg-green-600 hover:bg-green-700' : ''}`}
									>
										{copied ? (
											<CheckCircle className="w-4 h-4" />
										) : (
											<Copy className="w-4 h-4" />
										)}
									</Button>
								</div>
							</CardContent>
						</Card>
					</div>

					<div className="space-y-4">
						<p className="text-sm font-medium text-gray-700 text-center">
							링크 전달 방법:
						</p>

						<div className="space-y-3">
							<div className="flex items-start space-x-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
								<MessageCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
								<div>
									<h4 className="font-medium text-yellow-800">
										카카오톡으로 전달
									</h4>
									<p className="text-sm text-yellow-700 mt-1">
										1. 카카오톡을 열고 학생과의 채팅방으로 이동하세요
										<br />
										2. 복사한 링크를 붙여넣기하여 전송하세요
									</p>
								</div>
							</div>

							<div className="flex items-start space-x-3 p-4 bg-green-50 border border-green-200 rounded-lg">
								<Mail className="w-5 h-5 text-green-600 mt-0.5" />
								<div>
									<h4 className="font-medium text-green-800">
										문자 메시지로 전달
									</h4>
									<p className="text-sm text-green-700 mt-1">
										1. 문자 메시지 앱을 열고 학생의 연락처를 선택하세요
										<br />
										2. 복사한 링크를 붙여넣기하여 전송하세요
									</p>
								</div>
							</div>
						</div>
					</div>

					<div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
						<div className="flex">
							<div className="flex-shrink-0">
								<span className="text-amber-600 text-sm">💡</span>
							</div>
							<div className="ml-3">
								<p className="text-sm text-amber-800">
									<strong>안내:</strong> 학생이 이 링크를 통해 회원가입하면
									자동으로 연결됩니다.
								</p>
							</div>
						</div>
					</div>

					<div className="flex justify-end">
						<Button variant="outline" onClick={onClose}>
							닫기
						</Button>
					</div>
				</div>
			</DialogContent>
		</Dialog>
	);
};

export default StudentInviteModal;
