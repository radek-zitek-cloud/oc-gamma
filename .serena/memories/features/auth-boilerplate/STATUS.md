# Feature: Auth Boilerplate

## State: coding

## Plan
- **Location:** `/docs/features/auth-boilerplate/plan.md`
- **Description:** Full-stack user authentication system with JWT HttpOnly cookies, registration, login, logout, profile management, and password change functionality.

## Current Phase: Phases 1-5 Complete - Full Stack Implementation Done

## Changed Files (Completed)

### Phase 1: Backend Foundation (COMPLETE)
- [x] `src/backend/pyproject.toml` - Added dependencies
- [x] `src/backend/core/config.py` - Settings configuration with pydantic-settings
- [x] `src/backend/core/database.py` - Async DB setup with SQLAlchemy 2.0
- [x] `src/backend/core/logging.py` - Structured JSON logging
- [x] `src/backend/core/security.py` - JWT and bcrypt (NOT passlib)
- [x] `src/backend/core/__init__.py`
- [x] `src/backend/models/__init__.py`
- [x] `src/backend/models/base.py` - SQLAlchemy 2.0 DeclarativeBase
- [x] `src/backend/models/user.py` - User SQLAlchemy model
- [x] `src/backend/schemas/__init__.py`
- [x] `src/backend/schemas/user.py` - User Pydantic schemas
- [x] `src/backend/schemas/auth.py` - Auth Pydantic schemas
- [x] `tests/backend/conftest.py` - Pytest fixtures with async support
- [x] `tests/backend/test_security.py` - Security tests (11 tests)
- [x] `tests/backend/test_database.py` - Database tests (5 tests)

### Phase 2: Backend API (COMPLETE)
- [x] `src/backend/repositories/__init__.py`
- [x] `src/backend/repositories/base.py` - Generic BaseRepository[T]
- [x] `src/backend/repositories/user.py` - UserRepository with user-specific operations
- [x] `src/backend/services/__init__.py`
- [x] `src/backend/services/auth_service.py` - Auth business logic
- [x] `src/backend/api/__init__.py`
- [x] `src/backend/api/v1/__init__.py` - API router aggregation
- [x] `src/backend/api/v1/auth.py` - Auth endpoints (register, login, logout, me, update, password)
- [x] `src/backend/api/deps.py` - FastAPI dependencies (get_db, get_current_user)
- [x] `src/backend/main.py` - Updated with CORS, lifespan, routers
- [x] `tests/backend/test_user_repo.py` - Repository tests (7 tests)
- [x] `tests/backend/test_auth_service.py` - Service tests (10 tests)
- [x] `tests/backend/test_auth_api.py` - API endpoint tests (8 tests)

### Phase 3: Frontend Foundation (COMPLETE)
- [x] `src/frontend/package.json` - Added all dependencies
- [x] `src/frontend/tailwind.config.js` - Tailwind with Trinity Bank theme
- [x] `src/frontend/postcss.config.js` - PostCSS configuration
- [x] `src/frontend/src/globals.css` - CSS variables (Gold #E7CA64, Thunder Grey #231F20)
- [x] `src/frontend/src/lib/logger.ts` - Centralized logging utility
- [x] `src/frontend/src/lib/api.ts` - Axios client with interceptors
- [x] `src/frontend/src/lib/utils.ts` - cn(), formatDate(), generateCorrelationId()
- [x] `src/frontend/src/types/user.ts` - TypeScript interfaces
- [x] `src/frontend/src/store/authStore.ts` - Zustand auth store
- [x] `src/frontend/vite.config.ts` - Path alias configuration
- [x] `src/frontend/tsconfig.app.json` - TypeScript path mapping

### Phase 4: Frontend Layout (COMPLETE)
- [x] `src/frontend/src/components/layout/AppShell.tsx` - Main layout wrapper
- [x] `src/frontend/src/components/layout/Header.tsx` - Fixed top navigation
- [x] `src/frontend/src/components/layout/Sidebar.tsx` - Left sidebar navigation
- [x] `src/frontend/src/components/layout/StatusBar.tsx` - Bottom status bar
- [x] `src/frontend/src/components/ui/button.tsx` - shadcn Button component
- [x] `src/frontend/src/components/ui/input.tsx` - shadcn Input component
- [x] `src/frontend/src/components/ui/label.tsx` - shadcn Label component
- [x] `src/frontend/src/components/ui/card.tsx` - shadcn Card component

### Phase 5: Frontend Auth (COMPLETE)
- [x] `src/frontend/src/hooks/useAuth.ts` - TanStack Query auth hooks
- [x] `src/frontend/src/pages/Login.tsx` - Login page with form
- [x] `src/frontend/src/pages/Register.tsx` - Registration page
- [x] `src/frontend/src/pages/Dashboard.tsx` - Dashboard page (protected)
- [x] `src/frontend/src/pages/Profile.tsx` - Profile management page
- [x] `src/frontend/src/App.tsx` - React Router with protected routes
- [x] `src/frontend/src/main.tsx` - Updated entry point

### Configuration Files (COMPLETE)
- [x] `.env` - Environment variables
- [x] `.env.example` - Environment template

### Test Results
- **Total Backend Tests:** 41 tests passing
  - Security: 11 tests
  - Database: 5 tests
  - User Repository: 7 tests
  - Auth Service: 10 tests
  - Auth API: 8 tests

### Backend Features Implemented
- User registration with email/username validation
- Login with JWT HttpOnly cookie (Secure, SameSite, Max-Age)
- Logout with cookie clearing
- Get current user profile
- Update profile (email, full_name)
- Change password (requires current password)
- Proper error handling with HTTP status codes
- Structured JSON logging
- CORS middleware with environment-based origins

### Frontend Features Implemented
- App Shell layout (Header, Sidebar, Status Bar, Main Content)
- Login form with validation
- Registration form with validation
- Dashboard (protected route)
- Profile page with update/change password
- TanStack Query for server state
- Zustand for client state
- Axios with interceptors (X-Correlation-ID)
- JWT stored in HttpOnly cookies (not localStorage)
- Protected route guards
- Trinity Bank theme (Gold, Thunder Grey)

### Technical Compliance
- **Backend:**
  - SQLAlchemy 2.0 syntax (Mapped, mapped_column, select())
  - Repository pattern with dependency injection
  - Pydantic V2 schemas separate from SQLAlchemy models
  - bcrypt for password hashing (NOT passlib)
  - Async/await throughout
  - JWT in HttpOnly cookies

- **Frontend:**
  - TanStack Query for server state (no useEffect for data fetching)
  - Zustand for client state
  - shadcn/ui components
  - data-testid attributes on interactive elements
  - App Shell layout with fixed elements
  - Trinity Bank HSL color system
  - Centralized logger (no console.log)
  - X-Correlation-ID header on API requests

## Reports
- [x] Plan: `/docs/features/auth-boilerplate/plan.md`
- [ ] Code Review: `/docs/features/auth-boilerplate/code-review.md`
- [ ] Security Review: `/docs/features/auth-boilerplate/security-review.md`
- [ ] Documentation: `/docs/features/auth-boilerplate/docs-report.md`

## Approval Log
- 2026-02-23 - Plan created by Planning Agent
- 2026-02-23 - Plan approved by human
- [ ] Pending - Code review passed
- [ ] Pending - Security review passed
- [ ] Pending - Final approval by human

## Implementation Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Backend Foundation | **COMPLETE** |
| 2 | Backend API | **COMPLETE** |
| 3 | Frontend Foundation | **COMPLETE** |
| 4 | Frontend Layout | **COMPLETE** |
| 5 | Frontend Auth | **COMPLETE** |
| 6 | Testing (Vitest + E2E) | Partial (Backend complete) |
| 7 | Integration & Documentation | Partial |

## TDD Status
- **Backend:** 41 tests passing (100% TDD compliance)
- **Frontend:** Build succeeds, Vitest setup ready
- **E2E:** Playwright config ready

## Notes
- **Branch:** `feat/auth-boilerplate`
- **Backend Version Impact:** 0.1.0 → 0.2.0 (minor)
- **Frontend Version Impact:** 0.0.0 → 0.1.0 (minor)
- **Test Coverage:** All backend functionality covered with unit/integration tests
- **Build Status:** Frontend builds successfully without errors

## Running the Application

### Backend
```bash
cd src/backend
uv run uvicorn main:app --reload
```

### Frontend
```bash
cd src/frontend
npm run dev
```

### Tests
```bash
# Backend tests
cd src/backend
PYTHONPATH=/home/radek/Code/oc-gamma/src uv run pytest tests/backend/

# Frontend build
cd src/frontend
npm run build
```
