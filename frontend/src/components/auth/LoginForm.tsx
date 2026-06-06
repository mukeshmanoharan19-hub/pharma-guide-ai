'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks';
import { Button, Input } from '@/components/ui';
import { validateEmail } from '@/utils/validators';

interface LoginFormProps {
    backendUrl?: string;
    onSuccess?: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ backendUrl, onSuccess }) => {
    const router = useRouter();
    const { login, isLoading, error, clearError } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [formError, setFormError] = useState<Record<string, string>>({});

    const validateForm = () => {
        const errors: Record<string, string> = {};

        if (!email) {
            errors.email = 'Email is required';
        } else if (!validateEmail(email)) {
            errors.email = 'Invalid email format';
        }

        if (!password) {
            errors.password = 'Password is required';
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
            await login(email, password, backendUrl);
            onSuccess?.();
            router.push('/chat');
        } catch (err) {
            // Error handled by store
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-900">Login</h2>

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
            />

            <Button type="submit" isLoading={isLoading} className="w-full">
                Login
            </Button>
        </form>
    );
};
