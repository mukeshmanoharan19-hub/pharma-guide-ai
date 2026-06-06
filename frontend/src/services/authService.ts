import { apiClient } from './api';
import { API_ENDPOINTS } from '@/utils/constants';
import { LoginRequest, RegisterRequest, AuthResponse } from '@/types';

export const authService = {
    async login(credentials: LoginRequest): Promise<AuthResponse> {
        const response = await apiClient.post<AuthResponse>(
            API_ENDPOINTS.AUTH.LOGIN,
            credentials
        );
        return response.data;
    },

    async register(data: RegisterRequest): Promise<AuthResponse> {
        const response = await apiClient.post<AuthResponse>(
            API_ENDPOINTS.AUTH.REGISTER,
            data
        );
        return response.data;
    },

    async logout() {
        // Optional: Call backend logout endpoint if needed
        // await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    },
};
