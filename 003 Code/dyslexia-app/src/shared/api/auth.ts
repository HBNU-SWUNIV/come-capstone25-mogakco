import { axiosClient } from './axios';
import type {
	GuardianSignUpRequestDto,
	SignUpResponseDto,
	StudentSignUpRequestDto,
} from './types/';

export const studentSignUp = async (
	data: StudentSignUpRequestDto,
): Promise<SignUpResponseDto> => {
	const response = await axiosClient.post('/users/signup/student', data);
	return response.data;
};

export const guardianSignUp = async (
	data: GuardianSignUpRequestDto,
): Promise<SignUpResponseDto> => {
	const response = await axiosClient.post('/users/signup/guardian', data);
	return response.data;
};
