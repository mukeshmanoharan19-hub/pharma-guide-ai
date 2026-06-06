# Next.js Frontend Integration Guide

This guide explains how to configure your FastAPI backend to work with the new Next.js frontend.

## CORS Configuration

Add CORS middleware to your FastAPI backend to allow requests from the Next.js frontend:

```python
# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title=os.getenv("APP_NAME", "Pharma Guide API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Development
    "http://localhost:8000",  # Local backend
    os.getenv("FRONTEND_URL", ""),  # Production URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in origins if o],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... rest of your routes
```

## API Response Format

The frontend expects the following JSON formats:

### Authentication Responses

**Login Response** (`POST /auth/login`):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

**Register Response** (`POST /auth/register`):
Same as login response.

### Chat Responses

**Non-Streaming Response** (`POST /api/chat/ask`):
```json
{
  "answer": "Based on your symptoms...",
  "productsSuggestions": [
    {
      "name": "Medicine Name",
      "sku": "MED-123",
      "description": "Medicine description",
      "price": "₹299",
      "image_url": "https://..."
    }
  ]
}
```

**Streaming Response** (`POST /api/chat/ask/stream`):
Send Server-Sent Events (SSE) with newline-delimited JSON:

```
data: {"answer": "chunk1", "productsSuggestions": []}
data: {"answer": "chunk2", "productsSuggestions": []}
data: {"answer": "chunk3", "productsSuggestions": [{"name": "..."}]}
```

## Running Both Backend and Frontend

### Terminal 1 - Start FastAPI Backend

```bash
cd /Users/mukeshmanoharan/work/pharma-guide-ai
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Start Next.js Frontend

```bash
cd /Users/mukeshmanoharan/work/pharma-guide-ai/frontend
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Environment Variables

### Backend (.env)

```env
APP_NAME=Pharma Guide API
APP_VERSION=1.0.0
DATABASE_URL=postgresql://...
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Pharma Guide AI
```

## Migration from Streamlit

The original Streamlit app used:
- `POST /auth/login` for authentication
- `POST /auth/register` for user registration
- `POST /api/chat/ask` for chat requests
- `POST /api/chat/ask/stream` for streaming responses

All these endpoints remain unchanged. The frontend now:
1. Uses a modern Next.js App Router instead of Streamlit
2. Manages state with Zustand instead of Streamlit session_state
3. Uses Axios for HTTP requests instead of urllib
4. Stores tokens in localStorage instead of local files

## Token Management

### Storage Options

#### Option 1: localStorage (Current Implementation)
```typescript
localStorage.setItem('pharma_guide_token', token);
```

#### Option 2: HTTP-Only Cookies (More Secure)
```typescript
// In backend response:
response.set_cookie(
    key="auth_token",
    value=token,
    httponly=True,
    secure=True,  # For HTTPS in production
    samesite="lax"
)

// Frontend automatically sends with requests
```

To upgrade to HTTP-only cookies:
1. Update backend to set cookie
2. Update frontend's `tokenStorage.ts` to use cookies

## Debugging

### Check Frontend Requests

1. Open browser DevTools (F12)
2. Go to Network tab
3. Send a login request
4. Verify:
   - Status code is 200
   - Response has `access_token`
   - Authorization header is sent in subsequent requests

### Check Backend Logs

```bash
# Terminal with backend running
# Should see:
# INFO:     Started server process [...]
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Common Issues

1. **CORS Error**
   - Add frontend URL to CORS origins
   - Verify backend is running

2. **401 Unauthorized**
   - Check token is being sent
   - Verify token format: `Bearer <token>`
   - Check token expiration

3. **Chat Streaming Not Working**
   - Verify response is SSE format
   - Check network tab for streaming status
   - Verify content-type includes `text/event-stream`

## Production Deployment

### Backend (Python)

1. Use production database
2. Set `DEBUG=False`
3. Configure proper CORS origins
4. Use production ASGI server (Gunicorn + Uvicorn)

### Frontend (Next.js)

1. Build: `npm run build`
2. Deploy to Vercel, Netlify, or your server
3. Set production environment variables
4. Use production backend URL

## Performance Optimization

### Backend
- Add caching for frequently accessed data
- Implement connection pooling for database
- Use async database queries

### Frontend
- Code splitting happens automatically with Next.js
- Images are optimized with next/image
- API calls are cached where appropriate

## Monitoring

### Backend Health Check

```bash
curl http://localhost:8000/health
```

### Frontend Health

- Check browser console for errors
- Monitor API response times in DevTools
- Check Vercel/deployment logs

## Security Considerations

1. **HTTPS in Production**: Use secure cookies and HTTPS
2. **Token Expiration**: Implement refresh tokens
3. **Input Validation**: Both frontend and backend
4. **Rate Limiting**: Add rate limiting to backend
5. **CORS**: Only allow trusted origins

## Next Steps

1. Test full authentication flow
2. Test chat functionality with streaming
3. Verify product suggestions display
4. Test error handling
5. Load testing with multiple users
6. Deploy to production
