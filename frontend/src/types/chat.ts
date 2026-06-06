export interface Message {
    id?: string;
    type: 'user' | 'assistant';
    text: string;
    products?: Product[];
    timestamp?: number;
}

export interface ChatRequest {
    query: string;
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
}

export interface ChatState {
    messages: Message[];
    isLoading: boolean;
    error: string | null;
    pendingQuery: string;
}
