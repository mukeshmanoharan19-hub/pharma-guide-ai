'use client';

import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    helperText?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
    ({ label, error, helperText, className = '', ...props }, ref) => {
        return (
            <div className="w-full">
                {label && (
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        {label}
                    </label>
                )}
                <input
                    ref={ref}
                    className={`
            w-full h-11 px-4 border border-slate-200 rounded-xl
            bg-white text-slate-900 placeholder:text-slate-400
            focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-transparent
            dark:bg-slate-900 dark:text-slate-100 dark:border-slate-700 dark:focus:ring-slate-600
            disabled:bg-slate-100 disabled:cursor-not-allowed disabled:text-slate-400
            ${error ? 'border-red-500 focus:ring-red-400 dark:border-red-500 dark:focus:ring-red-500' : ''}
            ${className}
          `}
                    {...props}
                />
                {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
                {helperText && !error && (
                    <p className="mt-1 text-sm text-gray-500">{helperText}</p>
                )}
            </div>
        );
    }
);

Input.displayName = 'Input';
