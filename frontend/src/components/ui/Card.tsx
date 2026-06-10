'use client';

import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
    ({ className = '', ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={`
          rounded-2xl border border-slate-200 bg-white
          shadow-sm transition-shadow
          dark:bg-slate-900 dark:border-slate-700
          ${className}
        `}
                {...props}
            />
        );
    }
);

Card.displayName = 'Card';
