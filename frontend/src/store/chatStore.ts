import { create } from 'zustand';
import { BackendMessage, ChatSession, ChatState, Message, Product } from '@/types';
import { chatService, sessionService } from '@/services';
import { SESSION_STORAGE_KEY } from '@/utils/constants';

interface ChatStore extends ChatState {
    addMessage: (message: Message) => void;
    clearMessages: () => void;
    setLoading: (isLoading: boolean) => void;
    setError: (error: string | null) => void;
    clearError: () => void;
    setPendingQuery: (query: string) => void;
    setSessionId: (sessionId: string | null) => void;
    fetchSessions: () => Promise<void>;
    newChat: () => void;
    loadSession: (sessionId: string) => Promise<void>;
    deleteSession: (sessionId: string) => Promise<void>;
    restoreActiveSession: () => Promise<void>;
    askQuestion: (query: string, backendUrl?: string) => Promise<void>;
    streamQuestion: (query: string, backendUrl?: string) => AsyncGenerator<string>;
}

const persistSessionId = (sessionId: string | null) => {
    if (typeof window === 'undefined') return;
    if (sessionId) {
        localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
    } else {
        localStorage.removeItem(SESSION_STORAGE_KEY);
    }
};

const mapBackendMessage = (message: BackendMessage): Message => {
    const products: Product[] | undefined = message.message_metadata?.products?.map(
        (p) => ({ ...p, price: String((p as Product).price) })
    );
    return {
        id: message.id,
        type: message.role === 'user' ? 'user' : 'assistant',
        text: message.content,
        products: products && products.length > 0 ? products : undefined,
        timestamp: message.created_at ? new Date(message.created_at).getTime() : Date.now(),
    };
};

export const useChatStore = create<ChatStore>((set, get) => ({
    messages: [],
    isLoading: false,
    error: null,
    pendingQuery: '',
    sessionId: null,
    sessions: [],

    addMessage: (message: Message) => {
        set({ messages: [...get().messages, { ...message, id: Date.now().toString() }] });
    },

    clearMessages: () => {
        set({ messages: [] });
    },

    setLoading: (isLoading: boolean) => {
        set({ isLoading });
    },

    setError: (error: string | null) => {
        set({ error });
    },

    clearError: () => {
        set({ error: null });
    },

    setPendingQuery: (query: string) => {
        set({ pendingQuery: query });
    },

    setSessionId: (sessionId: string | null) => {
        persistSessionId(sessionId);
        set({ sessionId });
    },

    fetchSessions: async () => {
        try {
            const sessions = await sessionService.list();
            set({ sessions });
        } catch {
            // Non-fatal: sidebar simply stays empty.
        }
    },

    newChat: () => {
        persistSessionId(null);
        set({ sessionId: null, messages: [], error: null });
    },

    loadSession: async (sessionId: string) => {
        set({ isLoading: true, error: null });
        try {
            const backendMessages = await sessionService.getMessages(sessionId);
            persistSessionId(sessionId);
            set({
                sessionId,
                messages: backendMessages.map(mapBackendMessage),
                isLoading: false,
            });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to load conversation';
            set({ error: errorMessage, isLoading: false });
        }
    },

    deleteSession: async (sessionId: string) => {
        try {
            await sessionService.remove(sessionId);
            if (get().sessionId === sessionId) {
                get().newChat();
            }
            await get().fetchSessions();
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to delete conversation';
            set({ error: errorMessage });
        }
    },

    restoreActiveSession: async () => {
        if (typeof window === 'undefined') return;
        const stored = localStorage.getItem(SESSION_STORAGE_KEY);
        await get().fetchSessions();
        if (stored) {
            await get().loadSession(stored);
        }
    },

    askQuestion: async (query: string, backendUrl?: string) => {
        set({ isLoading: true, error: null });
        try {
            const response = await chatService.ask({ query, session_id: get().sessionId });
            if (response.session_id) {
                get().setSessionId(response.session_id);
            }
            set({
                messages: [
                    ...get().messages,
                    {
                        type: 'user',
                        text: query,
                        timestamp: Date.now(),
                    },
                    {
                        type: 'assistant',
                        text: response.answer,
                        products: response.productsSuggestions,
                        timestamp: Date.now(),
                    },
                ],
                isLoading: false,
            });
            await get().fetchSessions();
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Chat failed';
            set({ error: errorMessage, isLoading: false });
            throw error;
        }
    },

    streamQuestion: async function* (query: string, backendUrl?: string) {
        set({ isLoading: true, error: null, pendingQuery: query });
        try {
            // Add user message immediately.
            set({
                messages: [
                    ...get().messages,
                    {
                        type: 'user',
                        text: query,
                        timestamp: Date.now(),
                    },
                ],
            });

            // The backend streams the full structured object on each chunk, so
            // the last chunk holds the complete answer.
            let lastChunk = '';
            const stream = chatService.askStream(
                { query, session_id: get().sessionId },
                (sessionId) => get().setSessionId(sessionId)
            );

            for await (const chunk of stream) {
                lastChunk = chunk;
                yield chunk;
            }

            let answer = lastChunk;
            let products: Product[] | undefined;
            try {
                const parsed = JSON.parse(lastChunk);
                answer = parsed.answer ?? lastChunk;
                products = parsed.productsSuggestions || [];
            } catch {
                // Fall back to raw text.
            }

            set({
                messages: [
                    ...get().messages,
                    {
                        type: 'assistant',
                        text: answer,
                        products,
                        timestamp: Date.now(),
                    },
                ],
                isLoading: false,
                pendingQuery: '',
            });

            await get().fetchSessions();
        } catch (error: any) {
            const errorMessage = error.message || 'Chat streaming failed';
            set({ error: errorMessage, isLoading: false, pendingQuery: '' });
            throw error;
        }
    },
}));
