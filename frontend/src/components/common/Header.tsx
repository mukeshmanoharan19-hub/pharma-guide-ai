'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks';
import { Button } from '@/components/ui';

export const Header: React.FC = () => {
    const router = useRouter();
    const { user, logout } = useAuth();

    const handleLogout = () => {
        logout();
        router.push('/');
    };

    return (
        <header className="bg-white border-b border-gray-200 shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <h1 className="text-2xl font-bold text-blue-600">💊 Pharma Guide AI</h1>
                </div>

                {user && (
                    <div className="flex items-center gap-4">
                        <span className="text-gray-700">{user.email}</span>
                        <Button variant="secondary" size="sm" onClick={handleLogout}>
                            Logout
                        </Button>
                    </div>
                )}
            </div>
        </header>
    );
};
