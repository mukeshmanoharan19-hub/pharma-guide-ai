'use client';

import React, { useState } from 'react';
import { Button, Input } from '@/components/ui';
import { ArrowUp, Sparkles } from 'lucide-react';

interface ChatInputProps {
    onSend: (message: string) => Promise<void>;
    isLoading?: boolean;
    disabled?: boolean;
    onPromptSelect?: (query: string) => void;
    quickPrompts?: string[];
}

export const ChatInput: React.FC<ChatInputProps> = ({
    onSend,
    isLoading = false,
    disabled = false,
    onPromptSelect,
    quickPrompts = [],
}) => {
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
        <form
            onSubmit={handleSubmit}
            className="border-t border-slate-200 bg-white/90 backdrop-blur p-4 dark:border-slate-800 dark:bg-slate-950/90"
        >
            {error && <p className="text-sm text-red-600 mb-2">{error}</p>}
            {quickPrompts.length > 0 && onPromptSelect && (
                <div className="mb-3 flex flex-wrap gap-2">
                    {quickPrompts.map((prompt) => (
                        <button
                            key={prompt}
                            type="button"
                            onClick={() => onPromptSelect(prompt)}
                            className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 inline-flex items-center gap-1"
                        >
                            <Sparkles className="h-3 w-3" />
                            {prompt}
                        </button>
                    ))}
                </div>
            )}
            <div className="flex gap-2">
                <Input
                    type="text"
                    placeholder="Ask anything about medicines, orders, or policies..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={isLoading || disabled}
                    className="flex-1"
                />
                <Button
                    type="submit"
                    isLoading={isLoading}
                    disabled={disabled}
                    size="md"
                    className="min-w-24"
                >
                    <ArrowUp className="h-4 w-4" />
                    Send
                </Button>
            </div>
            <p className="mt-2 text-[11px] text-slate-400 dark:text-slate-500">
                Press Enter to send. Use quick prompts to start faster.
            </p>
        </form>
    );
};
