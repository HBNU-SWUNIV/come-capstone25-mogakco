import { SignUpForm } from '@/features/auth/components/signup-form';
import { createFileRoute, useSearch } from '@tanstack/react-router';

export const Route = createFileRoute('/signup/teacher')({
	component: TeacherSignUpPage,
});

function TeacherSignUpPage() {
	const { nickname } = useSearch({ from: '/signup/teacher' });

	return (
		<div className="min-h-screen bg-gray-50 py-12">
			<div className="container mx-auto px-4">
				<div className="max-w-md mx-auto">
					<SignUpForm userType="TEACHER" defaultNickname={nickname} />
				</div>
			</div>
		</div>
	);
}
