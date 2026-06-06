'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/store';

export const useAuth = () => {
    const { token, user, isLoading, error, login, register, logout, loadStoredAuth, clearError } =
        useAuthStore();

    useEffect(() => {
        // Load stored authentication on mount
        loadStoredAuth();
    }, [loadStoredAuth]);

    const isAuthenticated = !!token;

    return {
        token,
        user,
        isAuthenticated,
        isLoading,
        error,
        login,
        register,
        logout,
        clearError,
    };
};
