export * from './vocabulary';

export interface PhonemeComponent {
	consonant: string;
	pronunciation: string;
	sound: string;
	difficulty: string;
}

export interface SyllableComponents {
	initial: PhonemeComponent;
	medial: {
		vowel: string;
		pronunciation: string;
		sound: string;
		difficulty: string;
	};
	final?: PhonemeComponent;
}

export interface SyllableInfo {
	syllable: string;
	combinedSound: string;
	writingTips: string;
	components: SyllableComponents;
}

export interface WritingStep {
	step: number;
	syllable: string;
	phoneme: string;
	description: string;
}

export interface LearningTips {
	commonMistakes: string[];
	practiceWords: string[];
	rhymingWords: string[];
}

export interface PhonemeAnalysis {
	syllables: SyllableInfo[];
	writingOrder: WritingStep[];
	learningTips: LearningTips;
}

export interface StudentSignUpRequestDto {
	clientId: string;
	name: string;
	grade: string; // "GRADE_1" 형태
	interests: number[];
}

export interface GuardianSignUpRequestDto {
	clientId: string;
	name: string;
	email: string;
	guardianRole: 'PARENT' | 'TEACHER';
	organization: string;
}

export interface SignUpResponseDto {
	id: number;
	name: string;
	userType: 'STUDENT' | 'GUARDIAN';
	accessToken: string;
	refreshToken: string;
}
