import { Button } from '@/shared/ui/button';
import { Card } from '@/shared/ui/card';
import { Input } from '@/shared/ui/input';
import { Select } from '@/shared/ui/select';
import { Typography } from '@/shared/ui/typography';
import { useNavigate } from '@tanstack/react-router';
import { useEffect, useMemo, useState } from 'react';
import { useForm } from 'react-hook-form';

const interestOptions = [
	'동물',
	'우주',
	'과학',
	'음악',
	'미술',
	'운동',
	'요리',
	'게임',
	'만화',
	'영화',
];

interface StudentForm {
	name: string;
	grade: string;
	guardianCode: string;
}

interface GuardianForm {
	name: string;
	email: string;
	guardianRole: 'PARENT' | 'TEACHER';
	organization: string;
}

interface StudentPayload {
	clientId: string;
	name: string;
	grade: string;
	interests: number[];
}

interface GuardianPayload {
	clientId: string;
	name: string;
	email: string;
	guardianRole: 'PARENT' | 'TEACHER';
	organization: string;
}

export const SignUpForm = ({
	defaultNickname = '',
}: { defaultNickname?: string }) => {
	const navigate = useNavigate();
	const clientId = localStorage.getItem('clientId');
	const userType = useMemo(
		() => localStorage.getItem('userType') as 'STUDENT' | 'GUARDIAN' | null,
		[],
	);
	const [selectedInterests, setSelectedInterests] = useState<number[]>([]);
	const { register, handleSubmit } = useForm<StudentForm | GuardianForm>();

	useEffect(() => {
		if (!clientId || !userType) {
			navigate({
				to: '/signup/kakao',
				search: { userType: userType ?? 'STUDENT' },
				replace: true,
			});
		}
	}, [clientId, userType, navigate]);

	const toggleInterest = (index: number) => {
		setSelectedInterests((prev) => {
			if (prev.includes(index)) {
				return prev.filter((i) => i !== index);
			}
			if (prev.length >= 3) return prev;
			return [...prev, index];
		});
	};

	const onSubmit = async (data: StudentForm | GuardianForm) => {
		if (!clientId) {
			alert('카카오 인증을 먼저 진행해주세요.');
			return;
		}

		try {
			let endpoint: string;
			let payload: StudentPayload | GuardianPayload;

			if (userType === 'STUDENT') {
				const studentData = data as StudentForm;
				const guardianCode = studentData.guardianCode.trim();
				endpoint = `/users/signup/student${guardianCode ? `?code=${encodeURIComponent(guardianCode)}` : ''}`;
				payload = {
					clientId,
					name: studentData.name,
					grade: studentData.grade,
					interests: selectedInterests.map((i) => i + 1),
				};
			} else {
				const guardianData = data as GuardianForm;
				endpoint = '/users/signup/guardian';
				payload = {
					clientId,
					name: guardianData.name,
					email: guardianData.email,
					guardianRole: guardianData.guardianRole,
					organization: guardianData.organization,
				};
			}

			const response = await fetch(
				`${import.meta.env.VITE_API_BASE_URL}${endpoint}`,
				{
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(payload),
				},
			);

			const result = await response.json();
			console.log('회원가입 완료:', result);

			if (response.ok) {
				localStorage.setItem('accessToken', result.accessToken);
				localStorage.setItem('refreshToken', result.refreshToken);
				alert('회원가입이 완료되었습니다!');
				navigate({ to: '/' });
			} else {
				alert(`회원가입 실패: ${result.message || JSON.stringify(result)}`);
			}
		} catch (error) {
			console.error('회원가입 오류:', error);
			alert('회원가입 처리 중 오류가 발생했습니다.');
		}
	};

	if (!userType) {
		return (
			<div className="text-center mt-10">
				<p>유저 신분 정보가 없습니다. 다시 시도해주세요.</p>
				<Button
					onClick={() =>
						navigate({ to: '/signup/kakao', search: { userType: 'STUDENT' } })
					}
				>
					카카오 인증 페이지로 이동
				</Button>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-gradient-to-br from-[#f0f9ff] to-[#fffaf4] flex justify-center items-center p-4">
			<Card className="w-full max-w-md p-6 space-y-6">
				<div className="text-center space-y-1">
					<Typography variant="h4" className="font-bold">
						{userType === 'STUDENT' ? '학생 정보 입력' : '보호자 회원가입'}
					</Typography>
					<Typography variant="p" className="text-gray-600 text-sm">
						{userType === 'STUDENT'
							? '나만의 속도로 즐겁게 학습해요'
							: '아이의 학습을 지원하고 관리하세요'}
					</Typography>
				</div>

				<form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
					<div>
						<label
							htmlFor="name"
							className="block text-sm font-medium text-gray-700"
						>
							이름
						</label>
						<Input
							id="name"
							{...register('name', { required: true })}
							defaultValue={defaultNickname}
						/>
					</div>

					{userType === 'STUDENT' ? (
						<>
							<div>
								<label
									htmlFor="grade"
									className="block text-sm font-medium text-gray-700"
								>
									학년
								</label>
								<Select
									id="grade"
									{...register('grade', { required: true })}
									defaultValue=""
								>
									<option value="" disabled>
										학년을 선택하세요
									</option>
									{Array.from({ length: 6 }).map((_, i) => (
										<option
											key={`grade_${i + 1}`}
											value={`GRADE_${i + 1}`}
										>{`${i + 1}학년`}</option>
									))}
								</Select>
							</div>
							<div>
								<label
									htmlFor="guardianCode"
									className="block text-sm font-medium text-gray-700"
								>
									보호자 코드
								</label>
								<Input
									id="guardianCode"
									{...register('guardianCode', { required: true })}
									placeholder="보호자에게 받은 초대 코드를 입력하세요"
								/>
							</div>
							<div>
								<p className="block text-sm font-medium text-gray-700">
									좋아하는 것들 (3개까지 선택)
								</p>
								<div className="grid grid-cols-2 gap-2 mt-1">
									{interestOptions.map((interest, index) => (
										<button
											type="button"
											key={interest}
											onClick={() => toggleInterest(index)}
											className={`border rounded p-2 text-sm ${
												selectedInterests.includes(index)
													? 'bg-blue-500 text-white'
													: 'bg-white text-gray-700'
											}`}
										>
											{interest}
										</button>
									))}
								</div>
								<p className="text-xs text-gray-500 mt-1">
									선택한 관심사: {selectedInterests.length}/3
								</p>
							</div>
						</>
					) : (
						<>
							<div>
								<label
									htmlFor="email"
									className="block text-sm font-medium text-gray-700"
								>
									이메일
								</label>
								<Input id="email" {...register('email', { required: true })} />
							</div>
							<div>
								<label
									htmlFor="guardianRole"
									className="block text-sm font-medium text-gray-700"
								>
									역할
								</label>
								<Select
									id="guardianRole"
									{...register('guardianRole', { required: true })}
									defaultValue=""
								>
									<option value="" disabled>
										역할을 선택하세요
									</option>
									<option value="PARENT">부모</option>
									<option value="TEACHER">교사</option>
								</Select>
							</div>
							<div>
								<label
									htmlFor="organization"
									className="block text-sm font-medium text-gray-700"
								>
									소속 (선택사항)
								</label>
								<Input
									id="organization"
									{...register('organization')}
									placeholder="학교명 또는 기관명"
								/>
							</div>
						</>
					)}

					<Button type="submit" className="w-full">
						{userType === 'STUDENT' ? '읽기 모험 시작하기! 🚀' : '계정 만들기'}
					</Button>
				</form>
			</Card>
		</div>
	);
};
