'use client';

import React, { useEffect, useState } from 'react';
import { useChat } from '@/hooks';
import { Button } from '@/components/ui';
import { useCartStore } from '@/store';
import { CartDrawer } from '@/components/commerce/CartDrawer';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';

interface ChatInterfaceProps {
    userEmail?: string;
    backendUrl?: string;
    onLogout?: () => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
    userEmail,
    backendUrl,
    onLogout,
}) => {
    const {
        messages,
        isLoading,
        error,
        clearError,
        stream,
        sessions,
        sessionId,
        newChat,
        loadSession,
        deleteSession,
        restoreActiveSession,
    } = useChat();
    const [showSettings, setShowSettings] = useState(false);
    const [customBackendUrl, setCustomBackendUrl] = useState(backendUrl || 'http://localhost:8000');
    const cartCount = useCartStore((s) => s.cart?.item_count ?? 0);
    const openCart = useCartStore((s) => s.openDrawer);
    const fetchCart = useCartStore((s) => s.fetchCart);

    useEffect(() => {
        restoreActiveSession();
    }, [restoreActiveSession]);

    useEffect(() => {
        fetchCart();
    }, [fetchCart]);

    const handleSendMessage = async (query: string) => {
        try {
            // Stream the response
            let fullResponse = '';
            for await (const chunk of stream(query, customBackendUrl)) {
                fullResponse += chunk;
            }
        } catch (err) {
            console.error('Error sending message:', err);
        }
    };

    const handleUpdateBackendUrl = () => {
        localStorage.setItem('pharma_guide_base_url', customBackendUrl);
        setShowSettings(false);
    };

    const formatSessionTitle = (title?: string | null) =>
        title && title.trim().length > 0 ? title : 'New conversation';

    return (
        <div className="flex h-full bg-white">
            {/* Sessions Sidebar */}
            <aside className="hidden md:flex md:flex-col w-64 border-r border-gray-200 bg-gray-50">
                <div className="p-4 border-b border-gray-200">
                    <Button className="w-full" size="sm" onClick={newChat}>
                        + New chat
                    </Button>
                </div>
                <div className="flex-1 overflow-y-auto p-2 space-y-1">
                    {sessions.length === 0 && (
                        <p className="text-xs text-gray-400 px-2 py-3">
                            No conversations yet.
                        </p>
                    )}
                    {sessions.map((session) => (
                        <div
                            key={session.id}
                            className={`group flex items-center justify-between rounded-lg px-3 py-2 cursor-pointer transition-colors ${session.id === sessionId
                                ? 'bg-blue-100 text-blue-700'
                                : 'hover:bg-gray-200 text-gray-700'
                                }`}
                            onClick={() => loadSession(session.id)}
                        >
                            <span className="truncate text-sm">
                                {formatSessionTitle(session.title)}
                            </span>
                            <button
                                type="button"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    deleteSession(session.id);
                                }}
                                className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 ml-2"
                                aria-label="Delete conversation"
                            >
                                ✕
                            </button>
                        </div>
                    ))}
                </div>
            </aside>

            {/* Main Chat Column */}
            <div className="flex flex-col flex-1 bg-white">
            {/* Header */}
            <div className="border-b border-gray-200 p-4 bg-gradient-to-r from-blue-600 to-cyan-500">
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-2xl font-bold text-white">Pharma Guide AI</h1>
                        <p className="text-blue-100">Hi, {userEmail || 'pharma explorer'} 👋</p>
                    </div>
                    <div className="flex gap-2 items-center">
                        <button
                            type="button"
                            onClick={() => openCart('cart')}
                            className="relative bg-white/20 hover:bg-white/30 text-white rounded-lg px-3 py-1.5 text-sm font-medium transition-colors"
                            aria-label="Open cart"
                        >
                            🛒 Cart
                            {cartCount > 0 && (
                                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                                    {cartCount}
                                </span>
                            )}
                        </button>
                        <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => setShowSettings(!showSettings)}
                        >
                            Settings ⚙️
                        </Button>
                        {onLogout && (
                            <Button variant="danger" size="sm" onClick={onLogout}>
                                Logout
                            </Button>
                        )}
                    </div>
                </div>
            </div>

            {/* Settings Panel */}
            {showSettings && (
                <div className="border-b border-gray-200 p-4 bg-gray-50">
                    <h3 className="font-semibold text-gray-900 mb-3">Conversation Settings</h3>
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={customBackendUrl}
                            onChange={(e) => setCustomBackendUrl(e.target.value)}
                            placeholder="Backend URL"
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <Button size="sm" onClick={handleUpdateBackendUrl}>
                            Update
                        </Button>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">Current backend: {customBackendUrl}</p>
                </div>
            )}

            {/* Error Display */}
            {error && (
                <div className="p-4 bg-red-50 border-b border-red-200">
                    <div className="flex justify-between items-start">
                        <p className="text-sm text-red-600">{error}</p>
                        <button
                            onClick={clearError}
                            className="text-red-500 hover:text-red-700 font-semibold"
                        >
                            ✕
                        </button>
                    </div>
                </div>
            )}

            {/* Messages Area */}
            <div className="flex-1 overflow-hidden">
                <MessageList messages={messages} isLoading={isLoading} />
            </div>

                {/* Input Area */}
                <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
            </div>

            {/* Cart & Orders Drawer */}
            <CartDrawer />
        </div>
    );
};
