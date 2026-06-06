'use client';

import Link from 'next/link';
import { useAuth } from '@/hooks';
import { Button } from '@/components/ui';

export default function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600">💊 Pharma Guide AI</h1>
          <div>
            {isAuthenticated ? (
              <Link href="/chat">
                <Button>Go to Chat</Button>
              </Link>
            ) : (
              <Link href="/auth/login">
                <Button>Login / Sign Up</Button>
              </Link>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-16">
        <div className="text-center max-w-3xl mx-auto">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            Your AI-Powered Medicine Assistant
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Get instant, secure guidance on medicines, prescriptions, and health-related questions.
            Powered by advanced AI and backed by your own FastAPI server.
          </p>

          {isAuthenticated ? (
            <Link href="/chat">
              <Button size="lg">Start Chatting Now</Button>
            </Link>
          ) : (
            <Link href="/auth/login">
              <Button size="lg">Get Started</Button>
            </Link>
          )}
        </div>
      </main>

      {/* Features Section */}
      <section className="bg-white py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Why Choose Pharma Guide AI?
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="p-6 bg-blue-50 rounded-lg border border-blue-200">
              <div className="text-4xl mb-4">🔒</div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">Secure & Private</h4>
              <p className="text-gray-600">
                Your data stays on your own server. Login-backed chat ensures complete privacy.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="p-6 bg-cyan-50 rounded-lg border border-cyan-200">
              <div className="text-4xl mb-4">⚡</div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">Fast & Reliable</h4>
              <p className="text-gray-600">
                Get instant responses with streaming chat and advanced retrieval-augmented generation.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="p-6 bg-indigo-50 rounded-lg border border-indigo-200">
              <div className="text-4xl mb-4">💊</div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">Product Suggestions</h4>
              <p className="text-gray-600">
                Get relevant medicine recommendations based on your queries and symptoms.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white text-center py-8 px-4">
        <p>
          Made with ❤️ | Pharma Guide AI v1.0 | Built with Next.js & FastAPI
        </p>
      </footer>
    </div>
  );
}
