'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
    variant?: 'default' | 'secondary' | 'outline' | 'success';
}

const variantClasses: Record<NonNullable<BadgeProps['variant']>, string> = {
    default: 'bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900',
    secondary: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200',
    outline:
        'border border-slate-200 text-slate-700 dark:border-slate-700 dark:text-slate-200',
    success: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300',
};

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
    ({ className, variant = 'default', ...props }, ref) => (
        <span
            ref={ref}
            className={cn(
                'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
                variantClasses[variant],
                className
            )}
            {...props}
        />
    )
);

Badge.displayName = 'Badge';
