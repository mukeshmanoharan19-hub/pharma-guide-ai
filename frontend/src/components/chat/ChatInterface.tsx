'use client';

import React, { useState } from 'react';
import { useChat } from '@/hooks';
import { Button } from '@/components/ui';
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
    const { messages, isLoading, error, clearError, stream } = useChat();
    const [showSettings, setShowSettings] = useState(false);
    const [customBackendUrl, setCustomBackendUrl] = useState(backendUrl || 'http://localhost:8000');

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

    return (
        <div className="flex flex-col h-full bg-white">
            {/* Header */}
            <div className="border-b border-gray-200 p-4 bg-gradient-to-r from-blue-600 to-cyan-500">
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-2xl font-bold text-white">Pharma Guide AI</h1>
                        <p className="text-blue-100">Hi, {userEmail || 'pharma explorer'} 👋</p>
                    </div>
                    <div className="flex gap-2">
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
    );
};
