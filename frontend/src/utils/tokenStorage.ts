export const TOKEN_KEY = 'pharma_guide_token';
export const EMAIL_KEY = 'pharma_guide_email';

export const tokenStorage = {
    save: (token: string, email: string) => {
        if (typeof window !== 'undefined') {
            localStorage.setItem(TOKEN_KEY, token);
            localStorage.setItem(EMAIL_KEY, email);
        }
    },

    load: (): { token: string | null; email: string | null } => {
        if (typeof window === 'undefined') {
            return { token: null, email: null };
        }
        return {
            token: localStorage.getItem(TOKEN_KEY),
            email: localStorage.getItem(EMAIL_KEY),
        };
    },

    delete: () => {
        if (typeof window !== 'undefined') {
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(EMAIL_KEY);
        }
    },

    getToken: (): string | null => {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem(TOKEN_KEY);
    },
};
