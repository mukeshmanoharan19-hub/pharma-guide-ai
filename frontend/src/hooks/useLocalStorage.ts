'use client';

import { useEffect, useState } from 'react';

export const useLocalStorage = <T,>(key: string, initialValue: T) => {
    const [storedValue, setStoredValue] = useState<T>(initialValue);
    const [isLoaded, setIsLoaded] = useState(false);

    // Load value from localStorage on mount
    useEffect(() => {
        try {
            if (typeof window === 'undefined') return;
            const item = window.localStorage.getItem(key);
            if (item) {
                setStoredValue(JSON.parse(item));
            }
        } catch (error) {
            console.error(`Error reading from localStorage key "${key}":`, error);
        } finally {
            setIsLoaded(true);
        }
    }, [key]);

    const setValue = (value: T | ((val: T) => T)) => {
        try {
            const valueToStore = value instanceof Function ? value(storedValue) : value;
            setStoredValue(valueToStore);
            if (typeof window !== 'undefined') {
                window.localStorage.setItem(key, JSON.stringify(valueToStore));
            }
        } catch (error) {
            console.error(`Error writing to localStorage key "${key}":`, error);
        }
    };

    return [storedValue, setValue, isLoaded] as const;
};
