export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
    AUTH: {
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
    },
    CHAT: {
        ASK: '/api/chat/ask',
        ASK_STREAM: '/api/chat/ask/stream',
    },
    HEALTH: '/health',
};

export const APP_CONFIG = {
    DEFAULT_BACKEND_URL: API_BASE_URL,
    REQUEST_TIMEOUT: 60000,
    STREAM_TIMEOUT: 120000,
};
