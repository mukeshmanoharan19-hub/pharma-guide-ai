'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface SheetProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    children: React.ReactNode;
}

interface SheetContentProps extends React.HTMLAttributes<HTMLDivElement> {
    side?: 'right' | 'left';
}

export const Sheet: React.FC<SheetProps> = ({ open, onOpenChange, children }) => {
    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50">
            <button
                className="absolute inset-0 bg-black/45"
                onClick={() => onOpenChange(false)}
                aria-label="Close panel"
            />
            {children}
        </div>
    );
};

export const SheetContent = React.forwardRef<HTMLDivElement, SheetContentProps>(
    ({ className, side = 'right', children, ...props }, ref) => (
        <div
            ref={ref}
            className={cn(
                'absolute top-0 h-full w-full max-w-md border-l border-slate-200 bg-white shadow-xl dark:border-slate-800 dark:bg-slate-950',
                side === 'right' ? 'right-0' : 'left-0',
                className
            )}
            {...props}
        >
            {children}
        </div>
    )
);

SheetContent.displayName = 'SheetContent';
