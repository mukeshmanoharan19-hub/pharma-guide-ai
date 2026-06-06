import { create } from 'zustand';
import { AuthState, User } from '@/types';
import { authService } from '@/services';
import { tokenStorage } from '@/utils/tokenStorage';

interface AuthStore extends AuthState {
    login: (email: string, password: string, backendUrl?: string) => Promise<void>;
    register: (fullName: string, email: string, password: string, backendUrl?: string) => Promise<void>;
    logout: () => void;
    setToken: (token: string, user?: User) => void;
    setError: (error: string | null) => void;
    clearError: () => void;
    loadStoredAuth: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
    token: null,
    user: null,
    isLoading: false,
    error: null,

    login: async (email: string, password: string, backendUrl?: string) => {
        set({ isLoading: true, error: null });
        try {
            const response = await authService.login({ email, password });
            tokenStorage.save(response.access_token, email);
            if (backendUrl) {
                localStorage.setItem('pharma_guide_base_url', backendUrl);
            }
            set({
                token: response.access_token,
                user: response.user || { id: '', email, full_name: '' },
                isLoading: false,
            });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Login failed';
            set({ error: errorMessage, isLoading: false });
            throw error;
        }
    },

    register: async (fullName: string, email: string, password: string, backendUrl?: string) => {
        set({ isLoading: true, error: null });
        try {
            const response = await authService.register({
                full_name: fullName,
                email,
                password,
            });
            tokenStorage.save(response.access_token, email);
            if (backendUrl) {
                localStorage.setItem('pharma_guide_base_url', backendUrl);
            }
            set({
                token: response.access_token,
                user: response.user || { id: '', email, full_name: fullName },
                isLoading: false,
            });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Registration failed';
            set({ error: errorMessage, isLoading: false });
            throw error;
        }
    },

    logout: () => {
        tokenStorage.delete();
        localStorage.removeItem('pharma_guide_base_url');
        set({ token: null, user: null, error: null });
    },

    setToken: (token: string, user?: User) => {
        set({ token, user: user || null });
    },

    setError: (error: string | null) => {
        set({ error });
    },

    clearError: () => {
        set({ error: null });
    },

    loadStoredAuth: () => {
        const { token, email } = tokenStorage.load();
        if (token && email) {
            set({ token, user: { id: '', email, full_name: '' } });
        }
    },
}));
