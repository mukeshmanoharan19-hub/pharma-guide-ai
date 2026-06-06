# Pharma Guide AI Frontend

A modern Next.js frontend for the Pharma Guide AI application - your AI-powered medicine assistant.

## Features

- 🔐 **Secure Authentication**: Login/signup with JWT token management
- 💬 **Real-time Chat**: Streaming responses from the AI backend
- 🎯 **Product Suggestions**: Get relevant medicine recommendations
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- ⚡ **Fast Performance**: Built with Next.js 14+ and optimized for speed
- 🎨 **Beautiful UI**: Modern Tailwind CSS design with smooth animations

## Project Structure

```
src/
├── app/                  # Next.js App Router
│   ├── auth/            # Authentication pages
│   ├── chat/            # Chat interface
│   └── page.tsx         # Landing page
├── components/          # React components
│   ├── auth/            # LoginForm, SignupForm
│   ├── chat/            # ChatInterface, MessageList, ChatInput
│   ├── common/          # Header, ErrorBoundary, LoadingSpinner
│   └── ui/              # Button, Input, Card components
├── hooks/               # Custom React hooks
│   ├── useAuth.ts       # Authentication hook
│   ├── useChat.ts       # Chat hook
│   └── useLocalStorage.ts
├── services/            # API client services
│   ├── api.ts           # Axios client with interceptors
│   ├── authService.ts   # Auth API calls
│   └── chatService.ts   # Chat API calls
├── store/               # Zustand state management
│   ├── authStore.ts     # Auth state
│   └── chatStore.ts     # Chat state
├── types/               # TypeScript type definitions
│   ├── auth.ts
│   ├── chat.ts
│   └── api.ts
└── utils/               # Utility functions
    ├── constants.ts
    ├── formatting.ts
    ├── tokenStorage.ts
    └── validators.ts
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- FastAPI backend running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Configuration

1. Create a `.env.local` file:

```bash
cp .env.example .env.local
```

2. Update environment variables:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Pharma Guide AI
```

### Running the Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### Building for Production

```bash
npm run build
npm start
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | FastAPI backend URL | `http://localhost:8000` |
| `NEXT_PUBLIC_APP_NAME` | Application name | `Pharma Guide AI` |

## Technology Stack

- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Validation**: Zod
- **Linting**: ESLint

## Authentication Flow

1. User navigates to `/auth`
2. User logs in or creates an account
3. Backend returns JWT token
4. Token stored in localStorage (can be upgraded to HTTP-only cookies)
5. Token sent in `Authorization: Bearer <token>` header for all API requests
6. On token expiration, user is redirected to login

## Chat Features

- **Real-time Streaming**: Messages stream as they're generated
- **Message History**: Chat history persists during session
- **Product Suggestions**: Display relevant medicine recommendations
- **Configurable Backend**: Change backend URL in chat settings
- **Error Handling**: Graceful error display with retry options

## API Integration

The frontend communicates with the FastAPI backend at:

- **Auth Endpoints**:
  - `POST /auth/login` - User login
  - `POST /auth/register` - User registration

- **Chat Endpoints**:
  - `POST /api/chat/ask` - Send chat message
  - `POST /api/chat/ask/stream` - Stream chat response

## State Management with Zustand

### Auth Store

```typescript
const { token, user, login, register, logout } = useAuthStore();
```

### Chat Store

```typescript
const { messages, ask, stream, clearMessages } = useChatStore();
```

## Custom Hooks

### useAuth

```typescript
const { isAuthenticated, user, login, register, logout } = useAuth();
```

### useChat

```typescript
const { messages, isLoading, ask, stream } = useChat();
```

### useLocalStorage

```typescript
const [value, setValue, isLoaded] = useLocalStorage('key', defaultValue);
```

## Components

### Authentication Components

- `LoginForm` - User login with email and password
- `SignupForm` - User registration with validation

### Chat Components

- `ChatInterface` - Main chat layout
- `MessageList` - Display messages and products
- `ChatInput` - User input form

### Common Components

- `Header` - Navigation header
- `LoadingSpinner` - Loading indicator
- `ErrorBoundary` - Error handling

### UI Components

- `Button` - Customizable button
- `Input` - Form input with validation
- `Card` - Container component

## Deployment

### Vercel (Recommended)

```bash
npm i -g vercel
vercel
```

### Docker

Create a `Dockerfile`:

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install && npm run build
CMD ["npm", "start"]
```

### Environment Setup for Production

Set environment variables in your hosting platform:
- `NEXT_PUBLIC_API_URL` - Your production FastAPI URL
- `NEXT_PUBLIC_APP_NAME` - Your app name

## Development

### Code Generation

- Types are generated from backend API responses
- Use TypeScript strict mode for type safety

### Testing

```bash
npm run test
```

### Linting

```bash
npm run lint
```

## Troubleshooting

### Backend Connection Issues

1. Ensure backend is running on the correct URL
2. Check CORS configuration in FastAPI backend
3. Verify `NEXT_PUBLIC_API_URL` in environment variables

### Authentication Issues

1. Check browser localStorage for tokens
2. Verify backend token validation
3. Check API response format matches types

### Chat Streaming Issues

1. Verify backend supports SSE (Server-Sent Events)
2. Check network tab in browser DevTools
3. Verify request format matches `/api/chat/ask/stream`

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is part of Pharma Guide AI.

## Support

For issues and feature requests, please contact the development team or create an issue in the repository.
