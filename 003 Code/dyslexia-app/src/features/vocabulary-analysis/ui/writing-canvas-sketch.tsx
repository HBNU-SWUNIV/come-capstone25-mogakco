import { cn } from '@/lib/utils';
import { Button } from '@/shared/ui/button';
import { Eraser } from 'lucide-react';
import React, { useRef } from 'react';
import {
	ReactSketchCanvas,
	type ReactSketchCanvasRef,
} from 'react-sketch-canvas';

interface WritingCanvasSketchProps {
	height?: number;
	width?: number;
	onSave?: (pngData: string) => void;
	onClear?: () => void;
	guideText?: string;
	guideTextScale?: number;
	initialImage?: string;
	className?: string;
}

export const WritingCanvasSketch = React.forwardRef<
	ReactSketchCanvasRef,
	WritingCanvasSketchProps
>(
	(
		{
			height = 300,
			width,
			onSave,
			onClear,
			guideText,
			guideTextScale = 1,
			initialImage,
			className,
		},
		ref,
	) => {
		const canvasRef = useRef<ReactSketchCanvasRef>(null);
		const [backgroundImage, setBackgroundImage] = React.useState<
			string | undefined
		>(undefined);

		const handleClear = () => {
			canvasRef.current?.clearCanvas();
			if (onClear) onClear();
		};

		const handleSave = async () => {
			const data = await canvasRef.current?.exportImage('png');
			if (data && onSave) onSave(data);
		};

		React.useImperativeHandle(
			ref,
			() => canvasRef.current as ReactSketchCanvasRef,
		);

		React.useEffect(() => {
			if (!initialImage) return;
			if (initialImage.startsWith('data:image')) {
				setBackgroundImage(initialImage);
			} else {
				try {
					canvasRef.current?.loadPaths(JSON.parse(initialImage));
				} catch (e) {
					// 무시: 잘못된 JSON이거나 base64가 아님
				}
			}
		}, [initialImage]);

		return (
			<div
				className={cn('flex flex-col gap-4', className)}
				style={width ? { width: `${width}px` } : undefined}
			>
				<div
					className="relative rounded-lg border-2 border-dyslexia-blue shadow-sm w-full overflow-hidden"
					style={{ height: `${height}px` }}
				>
					<ReactSketchCanvas
						ref={canvasRef}
						style={{
							position: 'absolute',
							top: 0,
							left: 0,
							width: '100%',
							height: '100%',
							background: 'transparent',
							zIndex: 10,
						}}
						width={width ? String(width) : undefined}
						height={String(height)}
						strokeWidth={4}
						strokeColor="#000"
						backgroundImage={backgroundImage}
						withTimestamp={false}
						onStroke={handleSave}
					/>
					{guideText && (
						<div
							className="absolute top-0 left-0 w-full h-full flex items-center justify-center pointer-events-none select-none"
							style={{
								fontSize: `min(${height * 0.8 * guideTextScale}px, 7vw)`,
								color: '#64748b',
								opacity: 0.4,
								zIndex: 11,
								textAlign: 'center',
								wordBreak: 'keep-all',
								whiteSpace: 'pre-line',
								lineHeight: 1.1,
								padding: '0 8px',
								fontWeight: 600,
								textShadow: '0 1px 2px #fff, 0 0 8px #fff',
							}}
						>
							{guideText}
						</div>
					)}
				</div>
				<Button
					variant="outline"
					size="sm"
					onClick={handleClear}
					className="w-fit"
				>
					<Eraser className="mr-2 h-4 w-4" />
					다시 쓰기
				</Button>
			</div>
		);
	},
);
