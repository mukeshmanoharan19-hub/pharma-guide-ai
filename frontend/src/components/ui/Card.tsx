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
          rounded-lg border border-gray-200 bg-white 
          shadow-sm hover:shadow-md transition-shadow
          ${className}
        `}
                {...props}
            />
        );
    }
);

Card.displayName = 'Card';
