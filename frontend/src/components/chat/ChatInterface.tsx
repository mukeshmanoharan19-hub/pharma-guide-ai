'use client';

import React, { useEffect, useState } from 'react';
import { useChat } from '@/hooks';
import { Button } from '@/components/ui';
import { useCartStore } from '@/store';
import { CartDrawer } from '@/components/commerce/CartDrawer';
import {
    LogOut,
    Menu,
    Moon,
    Plus,
    Settings,
    ShoppingCart,
    Sparkles,
    Sun,
    Trash2,
} from 'lucide-react';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';

interface ChatInterfaceProps {
    userEmail?: string;
    backendUrl?: string;
    onLogout?: () => void;
}

const QUICK_PROMPTS = [
    'Compare alternatives for crocin advance',
    'Add PARA-500 to my cart',
    'Prepare checkout for my cart',
    'What is your cancellation policy?',
];
const THEME_STORAGE_KEY = 'pharma_guide_theme';

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
    const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
    const [customBackendUrl, setCustomBackendUrl] = useState(backendUrl || 'http://localhost:8000');
    const [theme, setTheme] = useState<'light' | 'dark'>('light');
    const cartCount = useCartStore((s) => s.cart?.item_count ?? 0);
    const openCart = useCartStore((s) => s.openDrawer);
    const fetchCart = useCartStore((s) => s.fetchCart);

    useEffect(() => {
        restoreActiveSession();
    }, [restoreActiveSession]);

    useEffect(() => {
        fetchCart();
    }, [fetchCart]);

    useEffect(() => {
        if (typeof window === 'undefined') return;
        const stored = localStorage.getItem(THEME_STORAGE_KEY);
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const resolved = stored === 'dark' || stored === 'light' ? stored : (systemDark ? 'dark' : 'light');
        setTheme(resolved);
        document.documentElement.classList.toggle('dark', resolved === 'dark');
    }, []);

    useEffect(() => {
        if (typeof window === 'undefined') return;
        document.documentElement.classList.toggle('dark', theme === 'dark');
        localStorage.setItem(THEME_STORAGE_KEY, theme);
    }, [theme]);

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

    const SessionsSidebar = ({ mobile = false }: { mobile?: boolean }) => (
        <aside
            className={`${mobile ? 'flex w-[88vw] max-w-xs shadow-2xl' : 'hidden md:flex w-72'
                } md:flex md:flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950`}
        >
            <div className="p-5 border-b border-slate-200 dark:border-slate-800">
                <div className="mb-4 flex items-start justify-between">
                    <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                            Pharma Guide
                        </p>
                        <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
                            AI Assistant
                        </h2>
                    </div>
                    {mobile && (
                        <button
                            className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
                            onClick={() => setMobileSidebarOpen(false)}
                            aria-label="Close sidebar"
                        >
                            ✕
                        </button>
                    )}
                </div>
                <Button
                    className="w-full"
                    size="sm"
                    onClick={() => {
                        newChat();
                        setMobileSidebarOpen(false);
                    }}
                >
                    <Plus className="h-4 w-4" />
                    New chat
                </Button>
            </div>
            <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
                {sessions.length === 0 && (
                    <p className="text-xs text-slate-400 px-2 py-3">
                        No conversations yet.
                    </p>
                )}
                {sessions.map((session) => (
                    <div
                        key={session.id}
                        className={`group flex items-center justify-between rounded-lg px-3 py-2 cursor-pointer transition-all ${session.id === sessionId
                            ? 'bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900'
                            : 'hover:bg-slate-100 text-slate-700 dark:hover:bg-slate-900 dark:text-slate-200'
                            }`}
                        onClick={() => {
                            loadSession(session.id);
                            setMobileSidebarOpen(false);
                        }}
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
                            className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-red-500 ml-2"
                            aria-label="Delete conversation"
                        >
                            <Trash2 className="h-4 w-4" />
                        </button>
                    </div>
                ))}
            </div>
            <div className="border-t border-slate-200 dark:border-slate-800 p-4 text-xs text-slate-500 dark:text-slate-400">
                <p className="flex items-center gap-1.5 font-medium">
                    <Sparkles className="h-3.5 w-3.5" />
                    Suggested actions
                </p>
                <ul className="mt-2 space-y-1">
                    <li>• Search and compare medicines</li>
                    <li>• Manage cart and checkout review</li>
                    <li>• Track and support orders</li>
                </ul>
            </div>
        </aside>
    );

    return (
        <div className="flex h-full bg-slate-100 dark:bg-slate-950">
            <SessionsSidebar />

            {mobileSidebarOpen && (
                <div className="md:hidden fixed inset-0 z-50 flex">
                    <div
                        className="absolute inset-0 bg-black/40"
                        onClick={() => setMobileSidebarOpen(false)}
                    />
                    <div className="relative transition-transform duration-300 ease-out">
                        <SessionsSidebar mobile />
                    </div>
                </div>
            )}

            {/* Main Chat Column */}
            <div className="flex flex-col flex-1 bg-slate-50 dark:bg-slate-900">
            {/* Header */}
            <div className="border-b border-slate-200 px-6 py-4 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
                <div className="flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <button
                            className="md:hidden rounded-xl border border-slate-200 p-2 text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
                            onClick={() => setMobileSidebarOpen(true)}
                            aria-label="Open sidebar"
                        >
                            <Menu className="h-4 w-4" />
                        </button>
                        <div>
                        <h1 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">Pharma Guide AI</h1>
                        <p className="text-slate-500 dark:text-slate-400">Welcome, {userEmail || 'pharma explorer'}</p>
                        </div>
                    </div>
                    <div className="flex gap-2 items-center flex-wrap justify-end">
                        <button
                            type="button"
                            onClick={() => openCart('cart')}
                            className="relative bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl px-3 py-2 text-sm font-medium transition-colors dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
                            aria-label="Open cart"
                        >
                            <span className="inline-flex items-center gap-1.5">
                                <ShoppingCart className="h-4 w-4" />
                                Cart
                            </span>
                            {cartCount > 0 && (
                                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                                    {cartCount}
                                </span>
                            )}
                        </button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setShowSettings(!showSettings)}
                        >
                            <Settings className="h-4 w-4" />
                            Settings
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() =>
                                setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'))
                            }
                            aria-label="Toggle theme"
                        >
                            {theme === 'dark' ? (
                                <Sun className="h-4 w-4" />
                            ) : (
                                <Moon className="h-4 w-4" />
                            )}
                            {theme === 'dark' ? 'Light' : 'Dark'}
                        </Button>
                        {onLogout && (
                            <Button variant="danger" size="sm" onClick={onLogout}>
                                <LogOut className="h-4 w-4" />
                                Logout
                            </Button>
                        )}
                    </div>
                </div>
            </div>

            {/* Settings Panel */}
            {showSettings && (
                <div className="border-b border-slate-200 p-4 bg-white dark:border-slate-800 dark:bg-slate-950">
                    <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-3">Conversation Settings</h3>
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={customBackendUrl}
                            onChange={(e) => setCustomBackendUrl(e.target.value)}
                            placeholder="Backend URL"
                            className="flex-1 px-3 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-slate-300 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
                        />
                        <Button size="sm" variant="outline" onClick={handleUpdateBackendUrl}>
                            Update
                        </Button>
                    </div>
                    <p className="text-sm text-slate-500 mt-2">Current backend: {customBackendUrl}</p>
                </div>
            )}

            {/* Error Display */}
            {error && (
                <div className="p-4 bg-red-50 border-b border-red-200 dark:bg-red-950/20 dark:border-red-900/40">
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
                <MessageList
                    messages={messages}
                    isLoading={isLoading}
                    onPromptSelect={(query) => void handleSendMessage(query)}
                />
            </div>

                {/* Input Area */}
                <ChatInput
                    onSend={handleSendMessage}
                    isLoading={isLoading}
                    quickPrompts={QUICK_PROMPTS}
                    onPromptSelect={(query) => void handleSendMessage(query)}
                />
            </div>

            {/* Cart & Orders Drawer */}
            <CartDrawer />
        </div>
    );
};
