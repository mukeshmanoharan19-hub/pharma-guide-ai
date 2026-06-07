'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks';
import { ChatInterface } from '@/components/chat';
import { LoadingSpinner } from '@/components/common';
import { TOKEN_KEY } from '@/utils/tokenStorage';

export default function ChatPage() {
    const router = useRouter();
    const { isAuthenticated, user, logout } = useAuth();

    useEffect(() => {
        const token =
            typeof window !== 'undefined'
                ? localStorage.getItem(TOKEN_KEY)
                : null;

        if (!isAuthenticated && !token) {
            router.push('/auth/login');
        }
    }, [isAuthenticated, router]);

    if (!isAuthenticated) {
        return (
            <div className="flex items-center justify-center h-screen">
                <LoadingSpinner size="lg" />
            </div>
        );
    }

    const handleLogout = () => {
        logout();
        router.push('/auth/login');
    };

    const backendUrl =
        (typeof window !== 'undefined' &&
            localStorage.getItem('pharma_guide_base_url')) ||
        'http://localhost:8000';

    return (
        <div className="h-screen flex flex-col">
            <ChatInterface
                userEmail={user?.email}
                backendUrl={backendUrl}
                onLogout={handleLogout}
            />
        </div>
    );
}
