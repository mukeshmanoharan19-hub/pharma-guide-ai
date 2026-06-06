import { create } from 'zustand';
import { ChatState, Message } from '@/types';
import { chatService } from '@/services';

interface ChatStore extends ChatState {
    addMessage: (message: Message) => void;
    clearMessages: () => void;
    setLoading: (isLoading: boolean) => void;
    setError: (error: string | null) => void;
    clearError: () => void;
    setPendingQuery: (query: string) => void;
    askQuestion: (query: string, backendUrl?: string) => Promise<void>;
    streamQuestion: (query: string, backendUrl?: string) => AsyncGenerator<string>;
}

export const useChatStore = create<ChatStore>((set, get) => ({
    messages: [],
    isLoading: false,
    error: null,
    pendingQuery: '',

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

    askQuestion: async (query: string, backendUrl?: string) => {
        set({ isLoading: true, error: null });
        try {
            const response = await chatService.ask({ query });
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
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Chat failed';
            set({ error: errorMessage, isLoading: false });
            throw error;
        }
    },

    streamQuestion: async function* (query: string, backendUrl?: string) {
        set({ isLoading: true, error: null, pendingQuery: query });
        try {
            // Add user message
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

            // Stream assistant response
            let fullResponse = '';
            for await (const chunk of chatService.askStream({ query })) {
                fullResponse += chunk;
                yield chunk;
            }

            // Parse and add assistant message
            try {
                const parsed = JSON.parse(fullResponse);
                set({
                    messages: [
                        ...get().messages,
                        {
                            type: 'assistant',
                            text: parsed.answer || fullResponse,
                            products: parsed.productsSuggestions || [],
                            timestamp: Date.now(),
                        },
                    ],
                    isLoading: false,
                    pendingQuery: '',
                });
            } catch {
                set({
                    messages: [
                        ...get().messages,
                        {
                            type: 'assistant',
                            text: fullResponse,
                            timestamp: Date.now(),
                        },
                    ],
                    isLoading: false,
                    pendingQuery: '',
                });
            }
        } catch (error: any) {
            const errorMessage = error.message || 'Chat streaming failed';
            set({ error: errorMessage, isLoading: false, pendingQuery: '' });
            throw error;
        }
    },
}));
