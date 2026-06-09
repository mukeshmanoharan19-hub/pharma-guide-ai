# Pharma Guide AI - Next.js Migration Complete ✅

A comprehensive AI-powered pharmaceutical guidance system with a modern Next.js frontend and FastAPI backend.

## 🎯 What's New

The project has been successfully migrated from **Streamlit to Next.js 14+**:

### Previous Stack (Streamlit)
- ❌ Streamlit UI (limited customization)
- ❌ Python client library
- ❌ Session-based state management

### Current Stack (Next.js)
- ✅ **Next.js 14+** with TypeScript
- ✅ **Zustand** state management
- ✅ **Tailwind CSS** for styling
- ✅ **Axios** for HTTP requests
- ✅ **Real-time streaming** chat responses
- ✅ **Responsive design** (mobile-friendly)
- ✅ **Modern authentication** with JWT tokens

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL (for backend)

### Installation

#### 1. Backend Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.db.init_db import init_db; init_db()"
```

#### 2. Frontend Setup

```bash
cd frontend
npm install
```

### Running the Application

Open two terminal windows:

**Terminal 1 - Start Backend**
```bash
make api
# or
python3 -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Start Frontend**
```bash
make frontend
# or
cd frontend && npm run dev
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
pharma-guide-ai/
├── app/                    # FastAPI backend
│   ├── api/               # API routes
│   ├── services/          # Business logic
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   └── main.py            # FastAPI app
├── frontend/              # Next.js frontend (NEW)
│   ├── src/
│   │   ├── app/          # Pages and layouts
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # API client
│   │   ├── store/        # Zustand stores
│   │   ├── types/        # TypeScript types
│   │   └── utils/        # Utilities
│   └── package.json
├── data/                  # Data files
├── alembic/              # Database migrations
└── Makefile              # Build commands
```

## 🎨 Frontend Features

### Authentication
- Secure login/signup with email and password
- JWT token-based authentication
- Token persistence in localStorage
- Automatic redirect on token expiration

### Chat Interface
- Real-time streaming responses
- Message history
- Product recommendations display
- Configurable backend URL
- Error handling with retry options

### UI Components
- Beautiful Tailwind CSS design
- Responsive mobile-first layout
- Loading states and spinners
- Error boundaries for safety
- Form validation

## 🔧 Make Commands

```bash
make api            # Start FastAPI backend (port 8000)
make frontend       # Start Next.js frontend (port 3000)
make streamlit      # Start Streamlit (legacy)
make dev            # Start API only
make help           # Show all available commands
```

## 📚 Documentation

- [Frontend README](./frontend/README_FRONTEND.md) - Detailed frontend documentation
- [Integration Guide](./frontend/INTEGRATION_GUIDE.md) - Backend-frontend integration
- [Backend API Docs](./app) - FastAPI documentation at http://localhost:8000/docs

### Phase Documentation (Completed Phases 0–5)
- [PHASE 0 — Foundation](./phases/PHASE0_FOUNDATION.md)
- [PHASE 1 — Chat Memory](./phases/PHASE1_MEMORY.md)
- [PHASE 2 — Tool Layer](./phases/PHASE2_TOOLS.md)
- [PHASE 3 — LangGraph](./phases/PHASE3_LANGGRAPH.md)
- [PHASE 4 — Supervisor Agent](./phases/PHASE4_SUPERVISOR.md)
- [PHASE 5 — Specialist Agents](./phases/PHASE5_SPECIALISTS.md)

## 🔐 Security

### Authentication Flow
1. User provides email and password
2. Backend validates and returns JWT token
3. Token stored in browser localStorage
4. Token sent in `Authorization: Bearer <token>` header
5. Backend validates token for protected routes

### CORS Configuration
The backend is configured to accept requests from:
- `http://localhost:3000` (development frontend)
- `http://localhost:8000` (direct API access)
- Production frontend URL (set via environment variable)

## 📊 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration

### Chat
- `POST /api/chat/ask` - Send message and get response
- `POST /api/chat/ask/stream` - Stream chat response (SSE)

### Health
- `GET /health` - Health check endpoint

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy
- **Auth**: JWT tokens with python-jose
- **AI/ML**: LangChain, Cohere, Sentence Transformers
- **Search**: FAISS, BM25
- **PDF Processing**: PyMuPDF

### Frontend
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: Zustand
- **HTTP**: Axios
- **Validation**: Zod

## 🚢 Deployment

### Frontend Deployment
Options:
- **Vercel** (recommended for Next.js): `vercel deploy`
- **Netlify**: Connect GitHub repo
- **Docker**: Build Docker image
- **Self-hosted**: Any Node.js hosting

### Backend Deployment
Options:
- **Docker**: Use provided Dockerfile
- **Railway**: Deploy FastAPI directly
- **Render**: Deploy with gunicorn
- **PythonAnywhere**: Python hosting platform

## 🐛 Troubleshooting

### Frontend Won't Connect to Backend
1. Ensure backend is running on http://localhost:8000
2. Check CORS configuration in backend
3. Verify `NEXT_PUBLIC_API_URL` in `.env.local`

### Chat Streaming Not Working
1. Verify backend `/api/chat/ask/stream` endpoint returns SSE format
2. Check network tab in browser DevTools
3. Ensure response has correct content-type header

### Authentication Issues
1. Check localStorage for `pharma_guide_token`
2. Verify token format in Authorization header
3. Check backend token validation logic

## 📈 Performance

- **Frontend**: Optimized Next.js with code splitting and lazy loading
- **Backend**: Async database queries and caching
- **Streaming**: Real-time responses with Server-Sent Events
- **Search**: Hybrid BM25 + vector search for fast retrieval

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

This project is proprietary.

## 📞 Support

For issues and feature requests, contact the development team.

## 🎓 Learning Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Zustand](https://zustand.pmnd.rs/)

---

**Migration Status**: ✅ Complete - Streamlit replaced with modern Next.js frontend
**Last Updated**: June 6, 2026
