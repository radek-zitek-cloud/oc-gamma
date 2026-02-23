# OC Gamma - Project Overview

## Purpose
OC Gamma is a modern full-stack application using React/Vite frontend and FastAPI/PostgreSQL backend with progressive disclosure routing and multi-agent development workflow.

## Tech Stack

### Backend (Python)
- **Framework:** FastAPI (async)
- **Databases:** SQLite (aiosqlite) for dev, PostgreSQL (asyncpg) for production
- **ORM:** SQLAlchemy 2.0 (async) - NOT SQLModel
- **Validation:** Pydantic V2
- **Migrations:** Alembic (async)
- **Config:** pydantic-settings from .env
- **Package Manager:** uv

### Frontend (TypeScript/React)
- **Framework:** React 18+ with Vite
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui
- **Data Fetching:** TanStack Query (no useEffect for data fetching)
- **State Management:** Zustand (client state only)
- **Testing:** Vitest + React Testing Library
- **Package Manager:** npm

### Testing
- **Backend:** pytest + pytest-asyncio with SQLite in-memory
- **Frontend:** Vitest + React Testing Library (NO Jest)
- **E2E:** Playwright with data-testid selectors only

## Design System
**Trinity Bank Theme:**
- Gold (#E7CA64) as primary color
- Thunder Grey (#231F20) for dark backgrounds
- High information density (compact spacing)
- Strict App Shell layout (fixed header, sidebar, status bar, scrollable content)

## Architecture Patterns
- **Backend:** Repository pattern with dependency injection
- **Frontend:** App Shell layout with fixed positioning
- **Auth:** HttpOnly cookies with JWT, bcrypt for hashing (NOT passlib)
- **Logging:** Structured JSON format with correlation IDs

## Workflow
Feature development follows multi-agent workflow:
1. Planning Agent → creates plan
2. Code Implementer → writes code
3. Code Reviewer → reviews quality
4. Security Reviewer → security audit
5. Documentation Agent → updates docs
6. Human Final Approval → merge

## Project Structure
```
src/
  backend/          # Python FastAPI
    api/            # Routers & endpoints
    models/         # SQLAlchemy models
    schemas/        # Pydantic schemas
    repositories/   # Data access layer
    core/           # Config, security, DB
    services/       # Business logic
  frontend/         # React/Vite
    src/
      components/   # UI components
      hooks/        # TanStack Query hooks
      lib/          # Logger & utils
      store/        # Zustand state
      types/        # TypeScript types
tests/
  backend/          # pytest
  frontend/         # Vitest
  e2e/              # Playwright
docs/features/      # Feature tracking
rules/              # Architecture rules
