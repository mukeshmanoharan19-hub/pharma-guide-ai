export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    full_name: string;
    email: string;
    password: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    user?: {
        id: string;
        email: string;
        full_name: string;
    };
}

export interface User {
    id: string;
    email: string;
    full_name: string;
}

export interface AuthState {
    token: string | null;
    user: User | null;
    isLoading: boolean;
    error: string | null;
}
