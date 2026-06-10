import { OrderConfirmation } from './commerce';

export interface Message {
    id?: string;
    type: 'user' | 'assistant';
    text: string;
    products?: Product[];
    orderConfirmation?: OrderConfirmation;
    timestamp?: number;
}

export interface ChatRequest {
    query: string;
    session_id?: string | null;
}

export interface Product {
    name: string;
    sku: string;
    description: string;
    price: string;
    image_url?: string;
}

export interface ChatResponse {
    answer: string;
    productsSuggestions: Product[];
    orderConfirmation?: OrderConfirmation;
    session_id?: string;
}

export interface ChatSession {
    id: string;
    title?: string | null;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface BackendMessage {
    id: string;
    role: 'user' | 'assistant' | 'system' | 'tool';
    content: string;
    message_metadata?: {
        products?: Product[];
        orderConfirmation?: OrderConfirmation;
    } | null;
    token_count?: number | null;
    created_at: string;
}

export interface ChatState {
    messages: Message[];
    isLoading: boolean;
    error: string | null;
    pendingQuery: string;
    sessionId: string | null;
    sessions: ChatSession[];
}
