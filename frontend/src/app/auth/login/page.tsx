'use client';

import React, { useState } from 'react';
import { LoginForm, SignupForm } from '@/components/auth';

export default function AuthPage() {
    const [isLogin, setIsLogin] = useState(true);
    const [backendUrl, setBackendUrl] = useState('http://localhost:8000');

    return (
        <div className="space-y-6">
            {/* Tab Buttons */}
            <div className="flex gap-2 border-b border-gray-200">
                <button
                    onClick={() => setIsLogin(true)}
                    className={`px-4 py-2 font-medium transition-colors ${isLogin
                            ? 'text-blue-600 border-b-2 border-blue-600'
                            : 'text-gray-600 hover:text-gray-900'
                        }`}
                >
                    Login
                </button>
                <button
                    onClick={() => setIsLogin(false)}
                    className={`px-4 py-2 font-medium transition-colors ${!isLogin
                            ? 'text-blue-600 border-b-2 border-blue-600'
                            : 'text-gray-600 hover:text-gray-900'
                        }`}
                >
                    Sign Up
                </button>
            </div>

            {/* Forms */}
            {isLogin ? (
                <LoginForm backendUrl={backendUrl} />
            ) : (
                <SignupForm backendUrl={backendUrl} />
            )}

            {/* Backend URL Input */}
            <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                    Backend URL
                </label>
                <input
                    type="text"
                    value={backendUrl}
                    onChange={(e) => setBackendUrl(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="http://localhost:8000"
                />
                <p className="text-xs text-gray-500">
                    Configure your FastAPI backend URL
                </p>
            </div>
        </div>
    );
}
