'use client';

import React from 'react';

interface LoadingSpinnerProps {
    size?: 'sm' | 'md' | 'lg';
    fullScreen?: boolean;
}

const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-10 w-10',
    lg: 'h-16 w-16',
};

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
    size = 'md',
    fullScreen = false,
}) => {
    const spinner = (
        <div className={`inline-block animate-spin rounded-full border-4 border-current border-t-transparent ${sizeClasses[size]}`} />
    );

    if (fullScreen) {
        return (
            <div className="flex items-center justify-center h-screen w-screen">
                <div className="text-center">
                    {spinner}
                    <p className="mt-4 text-gray-600">Loading...</p>
                </div>
            </div>
        );
    }

    return spinner;
};
