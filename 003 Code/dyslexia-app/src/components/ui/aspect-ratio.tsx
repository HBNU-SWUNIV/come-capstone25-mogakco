import { cn } from '@/lib/utils';
import * as React from 'react';

type AspectRatioProps = React.HTMLAttributes<HTMLDivElement> & {
	ratio?: number;
};

const AspectRatio = React.forwardRef<HTMLDivElement, AspectRatioProps>(
	({ ratio = 1, className, style, children, ...props }, ref) => {
		return (
			<div
				ref={ref}
				className={cn('relative', className)}
				style={{ aspectRatio: `${ratio}`, ...style }}
				{...props}
			>
				{children}
			</div>
		);
	},
);
AspectRatio.displayName = 'AspectRatio';

export { AspectRatio };
