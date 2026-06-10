'use client';

import React, { useEffect, useRef } from 'react';
import { Message, Product } from '@/types';
import { formatTime } from '@/utils/formatting';
import { useCartStore } from '@/store';
import { OrderConfirmationCard } from '@/components/commerce/OrderConfirmationCard';
import { ArrowUpRight, Bot, Pill, UserRound } from 'lucide-react';

const ProductCard: React.FC<{ product: Product }> = ({ product }) => {
    const addItem = useCartStore((s) => s.addItem);
    const isLoading = useCartStore((s) => s.isLoading);
    // Agent tool results may use `title` instead of `name`.
    const displayName = product.name || (product as any).title || product.sku;

    return (
        <div className="flex gap-4 p-3 bg-slate-50 rounded-xl border border-slate-200 hover:border-slate-300 transition-colors">
            {product.image_url && (
                <img
                    src={product.image_url}
                    alt={displayName}
                    className="w-24 h-24 object-cover rounded-lg"
                />
            )}
            <div className="flex-1">
                <h4 className="font-semibold text-slate-900 flex items-center gap-1.5">
                    <Pill className="h-4 w-4 text-slate-500" />
                    {displayName}
                </h4>
                {product.description && (
                    <p className="text-sm text-slate-600 mt-1">{product.description}</p>
                )}
                <div className="flex justify-between items-center mt-2">
                    <span className="text-sm text-slate-500">SKU: {product.sku}</span>
                    <span className="font-semibold text-slate-900">₹{product.price}</span>
                </div>
                {product.sku && (
                    <button
                        type="button"
                        onClick={() => addItem(product.sku)}
                        disabled={isLoading}
                        className="mt-2 w-full bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white text-sm font-medium py-1.5 rounded-lg transition-colors inline-flex items-center justify-center gap-1.5"
                    >
                        Add to cart
                        <ArrowUpRight className="h-3.5 w-3.5" />
                    </button>
                )}
            </div>
        </div>
    );
};

interface MessageListProps {
    messages: Message[];
    isLoading?: boolean;
    onPromptSelect?: (query: string) => void;
}

const RECOMMENDED_QUERIES = [
    'Find alternatives for Dolo 650',
    'Show my cart and total',
    'What is your refund policy timeline?',
    'Track my recent order',
];

export const MessageList: React.FC<MessageListProps> = ({
    messages,
    isLoading = false,
    onPromptSelect,
}) => {
    const endRef = useRef<HTMLDivElement>(null);
    const lastAssistant = [...messages].reverse().find((m) => m.type === 'assistant');

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <div className="flex flex-col gap-5 h-full overflow-y-auto p-5 bg-gradient-to-b from-slate-50/95 to-slate-100/80 dark:from-slate-950 dark:to-slate-900">
            {messages.length === 0 && !isLoading && (
                <div className="flex items-center justify-center h-full">
                    <div className="max-w-2xl text-center">
                        <div className="inline-flex items-center rounded-full border border-slate-200 bg-white px-3 py-1 text-xs text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">
                            AI Pharmacare Assistant
                        </div>
                        <h3 className="mt-4 text-3xl font-semibold text-slate-900 dark:text-slate-100">
                            How can I help you today?
                        </h3>
                        <p className="mt-2 text-slate-500 dark:text-slate-400">
                            Ask about medicines, orders, cart operations, refunds, and support policies.
                        </p>
                        <div className="mt-6 grid gap-2 sm:grid-cols-2">
                            {RECOMMENDED_QUERIES.map((query) => (
                                <button
                                    key={query}
                                    type="button"
                                    onClick={() => onPromptSelect?.(query)}
                                    className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-left text-sm text-slate-700 hover:border-slate-300 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
                                >
                                    {query}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {messages.map((message) => (
                <div
                    key={message.id || `${message.type}-${message.timestamp}`}
                    className={`flex items-end gap-2 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                    {message.type === 'assistant' && (
                        <div className="h-8 w-8 rounded-full bg-white border border-slate-200 dark:bg-slate-900 dark:border-slate-700 flex items-center justify-center text-slate-500">
                            <Bot className="h-4 w-4" />
                        </div>
                    )}
                    <div
                        className={`max-w-xs lg:max-w-md xl:max-w-xl ${message.type === 'user'
                            ? 'bg-slate-900 text-white rounded-2xl rounded-br-md dark:bg-slate-100 dark:text-slate-900'
                            : 'bg-white text-slate-900 rounded-2xl rounded-bl-md border border-slate-200 dark:bg-slate-900 dark:text-slate-100 dark:border-slate-700'
                            } px-4 py-3 shadow-sm`}
                    >
                        <p className="text-sm">{message.text}</p>
                        {message.timestamp && (
                            <p className={`text-xs mt-2 ${message.type === 'user' ? 'text-slate-200 dark:text-slate-700' : 'text-slate-500 dark:text-slate-400'}`}>
                                {formatTime(message.timestamp)}
                            </p>
                        )}
                    </div>
                    {message.type === 'user' && (
                        <div className="h-8 w-8 rounded-full bg-slate-900 dark:bg-slate-100 flex items-center justify-center text-white dark:text-slate-900">
                            <UserRound className="h-4 w-4" />
                        </div>
                    )}
                </div>
            ))}

            {lastAssistant &&
                lastAssistant.products &&
                lastAssistant.products.length > 0 && (
                    <div className="bg-white p-4 rounded-2xl border border-slate-200 max-w-xs lg:max-w-md xl:max-w-xl dark:bg-slate-900 dark:border-slate-700">
                        <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-3">Suggested Products</h3>
                        <div className="space-y-3">
                            {lastAssistant.products.map((product) => (
                                <ProductCard key={product.sku} product={product} />
                            ))}
                        </div>
                    </div>
                )}

            {lastAssistant?.orderConfirmation && (
                <div className="max-w-xs lg:max-w-md xl:max-w-xl">
                    <OrderConfirmationCard confirmation={lastAssistant.orderConfirmation} />
                </div>
            )}

            {isLoading && (
                <div className="flex justify-start">
                    <div className="bg-white text-slate-900 px-4 py-3 rounded-2xl rounded-bl-md border border-slate-200 dark:bg-slate-900 dark:text-slate-100 dark:border-slate-700">
                        <div className="flex gap-2">
                            <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" />
                            <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                            <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                        </div>
                    </div>
                </div>
            )}

            <div ref={endRef} />
        </div>
    );
};
