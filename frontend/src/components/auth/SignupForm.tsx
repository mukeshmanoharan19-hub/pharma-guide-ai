'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks';
import { Button, Input } from '@/components/ui';
import { validateEmail, validatePassword } from '@/utils/validators';

interface SignupFormProps {
    backendUrl?: string;
    onSuccess?: () => void;
}

export const SignupForm: React.FC<SignupFormProps> = ({ backendUrl, onSuccess }) => {
    const router = useRouter();
    const { register, isLoading, error, clearError } = useAuth();
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [formError, setFormError] = useState<Record<string, string>>({});

    const validateForm = () => {
        const errors: Record<string, string> = {};

        if (!fullName.trim()) {
            errors.fullName = 'Full name is required';
        }

        if (!email) {
            errors.email = 'Email is required';
        } else if (!validateEmail(email)) {
            errors.email = 'Invalid email format';
        }

        if (!password) {
            errors.password = 'Password is required';
        } else {
            const passwordError = validatePassword(password);
            if (passwordError) {
                errors.password = passwordError;
            }
        }

        if (password !== confirmPassword) {
            errors.confirmPassword = 'Passwords do not match';
        }

        setFormError(errors);
        return Object.keys(errors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setFormError({});

        if (!validateForm()) {
            return;
        }

        try {
            await register(fullName, email, password, backendUrl);
            onSuccess?.();
            router.push('/chat');
        } catch (err) {
            // Error handled by store
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-900">Create Account</h2>

            {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-600">{error}</p>
                    <button
                        type="button"
                        onClick={clearError}
                        className="text-xs text-red-500 hover:text-red-700 mt-2"
                    >
                        Dismiss
                    </button>
                </div>
            )}

            <Input
                label="Full Name"
                type="text"
                placeholder="John Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                error={formError.fullName}
            />

            <Input
                label="Email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={formError.email}
            />

            <Input
                label="Password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={formError.password}
                helperText="Min 8 chars, 1 uppercase, 1 number"
            />

            <Input
                label="Confirm Password"
                type="password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                error={formError.confirmPassword}
            />

            <Button type="submit" isLoading={isLoading} className="w-full">
                Sign Up
            </Button>
        </form>
    );
};
