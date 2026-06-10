'use client';

import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'danger' | 'outline' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    isLoading?: boolean;
    children: React.ReactNode;
}

const variantClasses = {
    primary:
        'bg-slate-900 text-white shadow-sm hover:bg-slate-800 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-slate-200',
    secondary:
        'bg-slate-100 text-slate-900 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700',
    danger: 'bg-red-600 text-white hover:bg-red-700',
    outline:
        'border border-slate-200 bg-white text-slate-900 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800',
    ghost:
        'bg-transparent text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800',
};

const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ variant = 'primary', size = 'md', isLoading = false, className = '', disabled, ...props }, ref) => {
        return (
            <button
                ref={ref}
                disabled={disabled || isLoading}
                className={`
          inline-flex items-center justify-center gap-2 whitespace-nowrap
          font-medium rounded-xl transition-colors duration-200
          disabled:opacity-50 disabled:cursor-not-allowed
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400
          ${variantClasses[variant]}
          ${sizeClasses[size]}
          ${className}
        `}
                {...props}
            >
                {isLoading ? (
                    <span className="flex items-center gap-2">
                        <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                        Loading...
                    </span>
                ) : (
                    props.children
                )}
            </button>
        );
    }
);

Button.displayName = 'Button';
