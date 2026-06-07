'use client';

import { useChatStore } from '@/store';
import { useCallback } from 'react';

export const useChat = () => {
    const {
        messages,
        isLoading,
        error,
        pendingQuery,
        sessionId,
        sessions,
        addMessage,
        clearMessages,
        setLoading,
        setError,
        clearError,
        setPendingQuery,
        fetchSessions,
        newChat,
        loadSession,
        deleteSession,
        restoreActiveSession,
        askQuestion,
        streamQuestion,
    } = useChatStore();

    const ask = useCallback(
        async (query: string, backendUrl?: string) => {
            try {
                await askQuestion(query, backendUrl);
            } catch (err) {
                // Error is handled in store
            }
        },
        [askQuestion]
    );

    const stream = useCallback(
        async function* (query: string, backendUrl?: string) {
            try {
                yield* streamQuestion(query, backendUrl);
            } catch (err) {
                // Error is handled in store
            }
        },
        [streamQuestion]
    );

    return {
        messages,
        isLoading,
        error,
        pendingQuery,
        sessionId,
        sessions,
        addMessage,
        clearMessages,
        setLoading,
        setError,
        clearError,
        setPendingQuery,
        fetchSessions,
        newChat,
        loadSession,
        deleteSession,
        restoreActiveSession,
        ask,
        stream,
    };
};
