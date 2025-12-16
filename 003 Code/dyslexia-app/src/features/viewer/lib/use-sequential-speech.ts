import { useRef, useState, useCallback } from 'react';
import { toast } from 'sonner';
import { fetchSpeechAudio } from '../api/speech-api';

interface TextBlock {
	id?: string;
	text: string;
}

export function useSequentialSpeech() {
	const [isReading, setIsReading] = useState(false);
	const [currentBlockIndex, setCurrentBlockIndex] = useState<number>(-1);
	const [totalBlocks, setTotalBlocks] = useState<number>(0);
	const audioRef = useRef<HTMLAudioElement | null>(null);
	const blocksRef = useRef<TextBlock[]>([]);
	const isStoppedRef = useRef<boolean>(false);

	const cleanup = useCallback(() => {
		if (audioRef.current) {
			audioRef.current.onended = null;
			audioRef.current.onerror = null;
			audioRef.current.pause();
			audioRef.current = null;
		}
	}, []);

	const playNextBlock = useCallback(async (blockIndex: number) => {
		if (isStoppedRef.current || blockIndex >= blocksRef.current.length) {
			// 모든 블록 읽기 완료 또는 중지됨
			setIsReading(false);
			setCurrentBlockIndex(-1);
			cleanup();
			return;
		}

		const block = blocksRef.current[blockIndex];
		if (!block?.text) {
			// 빈 텍스트면 다음 블록으로
			setCurrentBlockIndex(blockIndex);
			setTimeout(() => playNextBlock(blockIndex + 1), 100);
			return;
		}

		setCurrentBlockIndex(blockIndex);

		try {
			const blob = await fetchSpeechAudio({
				text: block.text,
				voice: 'alloy',
				model: 'tts-1',
			});

			if (isStoppedRef.current) return;

			const url = URL.createObjectURL(blob);
			const audio = new Audio(url);
			audioRef.current = audio;

			audio.onended = () => {
				URL.revokeObjectURL(url);
				if (!isStoppedRef.current) {
					// 다음 블록으로 자동 진행
					setTimeout(() => playNextBlock(blockIndex + 1), 500);
				}
			};

			audio.onerror = () => {
				URL.revokeObjectURL(url);
				console.error('오디오 재생 오류:', block.text);
				if (!isStoppedRef.current) {
					// 오류 시에도 다음 블록으로 진행
					setTimeout(() => playNextBlock(blockIndex + 1), 100);
				}
			};

			await audio.play();
		} catch (error) {
			console.error('TTS API 오류:', error);
			if (!isStoppedRef.current) {
				// API 오류 시에도 다음 블록으로 진행
				setTimeout(() => playNextBlock(blockIndex + 1), 100);
			}
		}
	}, [cleanup]);

	const startSequentialReading = useCallback(
		(blocks: TextBlock[]) => {
			if (isReading) {
				// 이미 읽고 있으면 중지
				stop();
				return;
			}

			const textBlocks = blocks.filter((block) => block.text && block.text.trim().length > 0);

			if (textBlocks.length === 0) {
				toast.error('읽을 텍스트가 없습니다');
				return;
			}

			blocksRef.current = textBlocks;
			setTotalBlocks(textBlocks.length);
			setIsReading(true);
			setCurrentBlockIndex(0);
			isStoppedRef.current = false;

			toast.success(`${textBlocks.length}개 블록 순차 낭독을 시작합니다`);
			playNextBlock(0);
		},
		[isReading, playNextBlock],
	);

	const stop = useCallback(() => {
		isStoppedRef.current = true;
		setIsReading(false);
		setCurrentBlockIndex(-1);
		cleanup();
		toast.info('낭독을 중지했습니다');
	}, [cleanup]);

	const getCurrentBlockId = useCallback(() => {
		if (currentBlockIndex >= 0 && currentBlockIndex < blocksRef.current.length) {
			return blocksRef.current[currentBlockIndex].id;
		}
		return null;
	}, [currentBlockIndex]);

	return {
		isReading,
		currentBlockIndex,
		totalBlocks,
		currentBlockId: getCurrentBlockId(),
		startSequentialReading,
		stop,
	};
}