.PHONY: backend frontend dev dev-nextjs install-frontend migrate migration help

# Start FastAPI backend
backend:
	python3 -m uvicorn app.main:app --reload --host localhost --port 8000

# Apply all database migrations
migrate:
	alembic upgrade head
# Inside the container
# docker compose exec api make migrate

# Autogenerate a new migration: make migration m="add chat tables"
migration:
	alembic revision --autogenerate -m "$(m)"
# Inside the container
# docker compose exec api make migration m="add chat tables"

# Start Next.js frontend
frontend:
	cd frontend && npm run dev

# Install frontend dependencies
install-frontend:
	cd frontend && npm install

# Development server with API only
dev:
	@echo "Starting FastAPI backend..."
	python3 -m uvicorn app.main:app --reload --host localhost --port 8000

# Development with Next.js frontend
dev-nextjs:
	@echo "Starting API (port 8000) and Next.js frontend (port 3000)..."
	@echo "Make sure both terminals are running:"
	@echo "  Terminal 1: make backend"
	@echo "  Terminal 2: make frontend"

# Show help
help:
	@echo "Available commands:"
	@echo "  make backend       - Start FastAPI backend (port 8000)"
	@echo "  make frontend      - Start Next.js frontend (port 3000)"
	@echo "  make migrate       - Apply DB migrations (alembic upgrade head)"
	@echo "  make migration m=\"msg\" - Autogenerate a new migration"
	@echo "  make dev           - Start API only"
	@echo "  make dev-nextjs    - Display instructions for running both servers"
	@echo "  make install-frontend - Install frontend dependencies"
