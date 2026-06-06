export const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

export const validatePassword = (password: string): string | null => {
    if (password.length < 8) {
        return 'Password must be at least 8 characters long';
    }
    if (!/[A-Z]/.test(password)) {
        return 'Password must contain at least one uppercase letter';
    }
    if (!/[0-9]/.test(password)) {
        return 'Password must contain at least one number';
    }
    return null;
};

export const validateForm = (
    email: string,
    password: string,
    fullName?: string
): { valid: boolean; errors: Record<string, string> } => {
    const errors: Record<string, string> = {};

    if (!email) {
        errors.email = 'Email is required';
    } else if (!validateEmail(email)) {
        errors.email = 'Invalid email format';
    }

    if (!password) {
        errors.password = 'Password is required';
    } else {
        const passwordError = validatePassword(password);
        if (passwordError) {
            errors.password = passwordError;
        }
    }

    if (fullName !== undefined && !fullName.trim()) {
        errors.fullName = 'Full name is required';
    }

    return {
        valid: Object.keys(errors).length === 0,
        errors,
    };
};
