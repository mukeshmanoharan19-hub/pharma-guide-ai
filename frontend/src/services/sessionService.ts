import { apiClient } from './api';
import { API_ENDPOINTS } from '@/utils/constants';
import { BackendMessage, ChatSession } from '@/types';

export const sessionService = {
    async list(): Promise<ChatSession[]> {
        const response = await apiClient.get<ChatSession[]>(
            API_ENDPOINTS.SESSIONS.BASE
        );
        return response.data;
    },

    async create(title?: string): Promise<ChatSession> {
        const response = await apiClient.post<ChatSession>(
            API_ENDPOINTS.SESSIONS.BASE,
            { title }
        );
        return response.data;
    },

    async getMessages(sessionId: string): Promise<BackendMessage[]> {
        const response = await apiClient.get<BackendMessage[]>(
            API_ENDPOINTS.SESSIONS.MESSAGES(sessionId)
        );
        return response.data;
    },

    async remove(sessionId: string): Promise<void> {
        await apiClient.delete(API_ENDPOINTS.SESSIONS.DELETE(sessionId));
    },
};
