import { apiClient } from './api';
import { API_ENDPOINTS, APP_CONFIG } from '@/utils/constants';
import { ChatRequest, ChatResponse } from '@/types';

export const chatService = {
    async ask(request: ChatRequest): Promise<ChatResponse> {
        const response = await apiClient.post<ChatResponse>(
            API_ENDPOINTS.CHAT.ASK,
            request
        );
        return response.data;
    },

    async *askStream(
        request: ChatRequest,
        onSessionId?: (sessionId: string) => void
    ): AsyncGenerator<string> {
        const token = localStorage.getItem('pharma_guide_token');
        const baseURL = localStorage.getItem('pharma_guide_base_url') ||
            (typeof window !== 'undefined' ? window.location.origin : '');
        const apiUrl = baseURL.includes('localhost')
            ? 'http://localhost:8000'
            : baseURL;

        const headers: HeadersInit = {
            'Content-Type': 'application/json',
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), APP_CONFIG.STREAM_TIMEOUT);

        try {
            const response = await fetch(`${apiUrl}${API_ENDPOINTS.CHAT.ASK_STREAM}`, {
                method: 'POST',
                headers,
                body: JSON.stringify(request),
                signal: controller.signal,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Stream failed');
            }

            const sessionId = response.headers.get('X-Session-Id');
            if (sessionId && onSessionId) {
                onSessionId(sessionId);
            }

            const reader = response.body?.getReader();
            if (!reader) {
                throw new Error('No response body');
            }

            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const chunk = line.slice(6)
                        if (chunk && !chunk.startsWith('[ERROR]')) {
                            yield chunk;
                        }
                    }
                }
            }

            if (buffer) {
                if (buffer.startsWith('data: ')) {
                    const chunk = buffer.slice(6)
                    if (chunk) yield chunk;
                }
            }
        } finally {
            clearTimeout(timeoutId);
        }
    },
};
