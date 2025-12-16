import { useMutation } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { guardianSignUp, studentSignUp } from '../api/auth';
import type {
	GuardianSignUpRequestDto,
	StudentSignUpRequestDto,
} from '../api/types/';

interface UseSignUpParams {
	userType: 'student' | 'teacher';
}

export const useSignUp = ({ userType }: UseSignUpParams) => {
	const navigate = useNavigate();

	return useMutation({
		mutationFn: (data: StudentSignUpRequestDto | GuardianSignUpRequestDto) => {
			if (userType === 'student') {
				return studentSignUp(data as StudentSignUpRequestDto);
			}
			return guardianSignUp(data as GuardianSignUpRequestDto);
		},
		onSuccess: (data) => {
			localStorage.setItem('accessToken', data.accessToken);
			localStorage.setItem('refreshToken', data.refreshToken);
			if (userType === 'student') {
				navigate({ to: '/student' });
			} else {
				navigate({ to: '/teacher' });
			}
		},
		onError: (error) => {
			console.error('회원가입 실패', error);
			alert('회원가입에 실패했습니다. 다시 시도해주세요.');
		},
	});
};
