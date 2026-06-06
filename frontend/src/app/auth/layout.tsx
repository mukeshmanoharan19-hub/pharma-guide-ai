import React from 'react';

export default function AuthLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-cyan-50 flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                {/* Logo/Header */}
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-blue-600 mb-2">💊</h1>
                    <h2 className="text-3xl font-bold text-gray-900">Pharma Guide AI</h2>
                    <p className="text-gray-600 mt-2">Your secure medicine assistant</p>
                </div>

                {/* Content */}
                <div className="bg-white rounded-lg shadow-lg p-8">
                    {children}
                </div>

                {/* Footer */}
                <div className="text-center mt-8">
                    <p className="text-sm text-gray-500">
                        Need your backend on http://localhost:8000? Run it before accessing this app.
                    </p>
                </div>
            </div>
        </div>
    );
}
