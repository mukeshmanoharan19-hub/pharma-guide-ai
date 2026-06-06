'use client';

import React, { useState } from 'react';
import { Button, Input } from '@/components/ui';

interface ChatInputProps {
    onSend: (message: string) => Promise<void>;
    isLoading?: boolean;
    disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, isLoading = false, disabled = false }) => {
    const [input, setInput] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        const trimmedInput = input.trim();
        if (!trimmedInput) {
            setError('Please enter a message');
            return;
        }

        try {
            await onSend(trimmedInput);
            setInput('');
        } catch (err: any) {
            setError(err.message || 'Failed to send message');
        }
    };

    return (
        <form onSubmit={handleSubmit} className="border-t border-gray-200 bg-white p-4">
            {error && <p className="text-sm text-red-600 mb-2">{error}</p>}
            <div className="flex gap-2">
                <Input
                    type="text"
                    placeholder="Type your question about medicines..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={isLoading || disabled}
                    className="flex-1 text-black"
                />
                <Button
                    type="submit"
                    isLoading={isLoading}
                    disabled={disabled}
                    size="md"
                >
                    Send
                </Button>
            </div>
        </form>
    );
};
