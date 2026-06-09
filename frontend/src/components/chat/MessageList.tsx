'use client';

import React, { useEffect, useRef } from 'react';
import { Message, Product } from '@/types';
import { formatTime } from '@/utils/formatting';
import { useCartStore } from '@/store';

const ProductCard: React.FC<{ product: Product }> = ({ product }) => {
    const addItem = useCartStore((s) => s.addItem);
    const isLoading = useCartStore((s) => s.isLoading);
    // Agent tool results may use `title` instead of `name`.
    const displayName = product.name || (product as any).title || product.sku;

    return (
        <div className="flex gap-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
            {product.image_url && (
                <img
                    src={product.image_url}
                    alt={displayName}
                    className="w-24 h-24 object-cover rounded"
                />
            )}
            <div className="flex-1">
                <h4 className="font-semibold text-gray-900">{displayName}</h4>
                {product.description && (
                    <p className="text-sm text-gray-600 mt-1">{product.description}</p>
                )}
                <div className="flex justify-between items-center mt-2">
                    <span className="text-sm text-gray-500">SKU: {product.sku}</span>
                    <span className="font-semibold text-blue-600">₹{product.price}</span>
                </div>
                {product.sku && (
                    <button
                        type="button"
                        onClick={() => addItem(product.sku)}
                        disabled={isLoading}
                        className="mt-2 w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium py-1.5 rounded-lg transition-colors"
                    >
                        Add to cart
                    </button>
                )}
            </div>
        </div>
    );
};

interface MessageListProps {
    messages: Message[];
    isLoading?: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, isLoading = false }) => {
    const endRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <div className="flex flex-col gap-4 h-full overflow-y-auto p-4">
            {messages.length === 0 && !isLoading && (
                <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            Welcome to Pharma Guide AI
                        </h3>
                        <p className="text-gray-500">Ask anything about medicines and health guidance.</p>
                    </div>
                </div>
            )}

            {messages.map((message) => (
                <div
                    key={message.id || `${message.type}-${message.timestamp}`}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                    <div
                        className={`max-w-xs lg:max-w-md xl:max-w-xl ${message.type === 'user'
                            ? 'bg-blue-600 text-white rounded-tl-lg rounded-bl-lg rounded-tr-lg'
                            : 'bg-gray-200 text-gray-900 rounded-tr-lg rounded-br-lg rounded-tl-lg'
                            } px-4 py-2 rounded-lg`}
                    >
                        <p className="text-sm">{message.text}</p>
                        {message.timestamp && (
                            <p className={`text-xs mt-1 ${message.type === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                                {formatTime(message.timestamp)}
                            </p>
                        )}
                    </div>
                </div>
            ))}

            {messages.length > 0 && messages[messages.length - 1].type === 'assistant' &&
                messages[messages.length - 1].products &&
                messages[messages.length - 1].products!.length > 0 && (
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 max-w-xs lg:max-w-md xl:max-w-xl">
                        <h3 className="font-semibold text-gray-900 mb-3">Suggested Products</h3>
                        <div className="space-y-3">
                            {messages[messages.length - 1].products!.map((product) => (
                                <ProductCard key={product.sku} product={product} />
                            ))}
                        </div>
                    </div>
                )}

            {isLoading && (
                <div className="flex justify-start">
                    <div className="bg-gray-200 text-gray-900 px-4 py-2 rounded-lg">
                        <div className="flex gap-2">
                            <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" />
                            <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                            <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                        </div>
                    </div>
                </div>
            )}

            <div ref={endRef} />
        </div>
    );
};
