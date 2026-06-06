import { NextRequest, NextResponse } from 'next/server';
import { TOKEN_KEY } from './utils/tokenStorage';

export function middleware(request: NextRequest) {
    const token = request.cookies.get(TOKEN_KEY)?.value;
    const { pathname } = request.nextUrl;

    // If accessing protected routes without token, redirect to auth
    if (pathname.startsWith('/chat') && !token) {
        // Note: Token might be in localStorage instead, so this is optional
        // The actual auth check happens in the component
        return NextResponse.next();
    }

    // If accessing auth routes with token, redirect to chat
    if (pathname.startsWith('/auth') && token) {
        return NextResponse.redirect(new URL('/chat', request.url));
    }

    return NextResponse.next();
}

export const config = {
    matcher: [
        /*
         * Match all request paths except for the ones starting with:
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico (favicon file)
         */
        '/((?!_next/static|_next/image|favicon.ico).*)',
    ],
};
