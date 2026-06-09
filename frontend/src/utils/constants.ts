export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
    AUTH: {
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
    },
    CHAT: {
        ASK: '/api/agent/chat',
        ASK_STREAM: '/api/agent/chat',
    },
    SESSIONS: {
        BASE: '/api/sessions',
        MESSAGES: (id: string) => `/api/sessions/${id}/messages`,
        DELETE: (id: string) => `/api/sessions/${id}`,
    },
    HEALTH: '/health',
};

export const SESSION_STORAGE_KEY = 'pharma_guide_session_id';

export const APP_CONFIG = {
    DEFAULT_BACKEND_URL: API_BASE_URL,
    REQUEST_TIMEOUT: 60000,
    STREAM_TIMEOUT: 120000,
};
