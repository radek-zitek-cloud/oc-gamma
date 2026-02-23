# Auth Boilerplate Implementation Plan

## Overview

This plan describes the implementation of a full-stack user authentication boilerplate that will serve as the foundation for the OC Gamma application. The system provides secure user registration, login, logout, profile management, and password change functionality using JWT tokens stored in HttpOnly cookies.

### Success Criteria
- Users can register with email, username, and password
- Users can log in and receive a JWT token via HttpOnly cookie
- Users can log out (cookie cleared)
- Users can view and edit their profile
- Users can change their password
- Authenticated users see a mock dashboard
- All endpoints protected with proper authentication
- Full test coverage (unit, integration, E2E)

---

## 1. Database Schema

### User Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    role VARCHAR(50) DEFAULT 'USER',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
- `idx_users_email` on `email` (for login lookups)
- `idx_users_username` on `username` (for profile lookups)

---

## 2. Backend Implementation

### 2.1 Dependencies to Add (pyproject.toml)

```toml
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "aiosqlite>=0.20.0",
    "alembic>=1.14.0",
    "pydantic-settings>=2.6.0",
    "python-jose[cryptography]>=3.3.0",
    "bcrypt>=4.2.0",
    "python-multipart>=0.0.17",
    "email-validator>=2.2.0",
    "slowapi>=0.1.9",
]

[dependency-groups]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
    "pytest-cov>=6.0.0",
]
```

### 2.2 Core Layer (`/core`)

#### 2.2.1 Configuration (`src/backend/core/config.py`)

**Purpose:** Centralized application settings loaded from environment variables.

**Key Settings:**
- `SECRET_KEY`: For JWT signing (load from .env)
- `ALGORITHM`: "HS256" for JWT
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 30 minutes default
- `DATABASE_URL`: SQLite async URL
- `CORS_ORIGINS`: List of allowed frontend origins
- `ENVIRONMENT`: "development" | "production"

**Rules Reference:** @rules/backend_arch_design.md Section 10 (Environment Loading)

#### 2.2.2 Database Setup (`src/backend/core/database.py`)

**Purpose:** Async SQLAlchemy engine and session management.

**Components:**
- `create_async_engine` with aiosqlite
- `async_sessionmaker` for AsyncSession
- `get_db()` dependency for FastAPI injection
- `init_db()` function for creating tables

**Rules Reference:** @rules/backend_arch_design.md Section 3 (Async Engine)

#### 2.2.3 Security (`src/backend/core/security.py`)

**Purpose:** Password hashing and JWT token operations.

**Functions:**
- `hash_password(password: str) -> str`: Use bcrypt directly (NOT passlib)
- `verify_password(plain: str, hashed: str) -> bool`: bcrypt verification
- `create_access_token(data: dict, expires_delta: timedelta | None) -> str`: JWT encoding
- `decode_access_token(token: str) -> dict | None`: JWT decoding with error handling

**Rules Reference:** 
- @rules/backend_arch_design.md Section 5 (bcrypt only)
- @rules/security.md Section 2 (JWT, HttpOnly cookies)

#### 2.2.4 Logging (`src/backend/core/logging.py`)

**Purpose:** Structured JSON logging with correlation IDs.

**Components:**
- `get_logger(name: str) -> logging.Logger`: Factory function
- `CorrelationIdMiddleware`: Extract X-Correlation-ID header, inject into logs
- JSON formatter with fields: timestamp, level, module, message, correlation_id

**Rules Reference:** @rules/backend_arch_design.md Section 7 (Structured Logging)

### 2.3 Models Layer (`/models`)

#### 2.3.1 User Model (`src/backend/models/user.py`)

**Purpose:** SQLAlchemy 2.0 declarative model for users table.

**Structure:**
```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    role: Mapped[str] = mapped_column(String(50), default="USER")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
```

**Rules Reference:** @rules/backend_arch_design.md Section 3 (SQLAlchemy 2.0 Syntax)

### 2.4 Schemas Layer (`/schemas`)

**Purpose:** Pydantic V2 models for request/response validation. Strictly separate from SQLAlchemy models.

#### 2.4.1 User Schemas (`src/backend/schemas/user.py`)

**Schemas:**
- `UserBase`: Base fields (email, username, full_name)
- `UserCreate`: Registration (extends UserBase + password)
- `UserUpdate`: Profile update (optional fields)
- `UserResponse`: API response (all fields except hashed_password)
- `UserInDB`: Internal use (includes hashed_password)
- `PasswordChange`: Password change request (current_password, new_password)

**Rules Reference:** @rules/backend_arch_design.md Section 3 (Separation of Concerns)

#### 2.4.2 Auth Schemas (`src/backend/schemas/auth.py`)

**Schemas:**
- `Token`: JWT token response (access_token, token_type)
- `TokenPayload`: Decoded JWT payload (sub: user_id, exp: expiration)
- `LoginRequest`: Login credentials (username/email, password)

### 2.5 Repositories Layer (`/repositories`)

#### 2.5.1 Base Repository (`src/backend/repositories/base.py`)

**Purpose:** Generic CRUD operations using SQLAlchemy 2.0 async syntax.

**Generic Class:**
```python
class BaseRepository[T]:
    def __init__(self, session: AsyncSession, model_class: type[T])
    async def get_by_id(self, id: int) -> T | None
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[T]
    async def create(self, obj_in: dict) -> T
    async def update(self, db_obj: T, obj_in: dict) -> T
    async def delete(self, id: int) -> bool
```

#### 2.5.2 User Repository (`src/backend/repositories/user.py`)

**Purpose:** User-specific data access operations.

**Class:** `UserRepository(BaseRepository[User])`

**Methods:**
- `get_by_email(email: str) -> User | None`
- `get_by_username(username: str) -> User | None`
- `create_user(user_data: dict) -> User`: Hash password before saving
- `update_user(user: User, update_data: dict) -> User`
- `change_password(user: User, new_hashed: str) -> User`

**Rules Reference:** @rules/backend_arch_design.md Section 4 (Repository Pattern)

### 2.6 Services Layer (`/services`)

#### 2.6.1 Auth Service (`src/backend/services/auth_service.py`)

**Purpose:** Cross-repository business logic for authentication.

**Functions:**
- `authenticate_user(db: AsyncSession, username: str, password: str) -> User | None`
- `register_user(db: AsyncSession, user_data: UserCreate) -> User`
- `get_current_user(db: AsyncSession, token: str) -> User`

### 2.7 API Layer (`/api`)

#### 2.7.1 Dependencies (`src/backend/api/deps.py`)

**Purpose:** FastAPI dependency injection.

**Dependencies:**
- `get_db() -> AsyncSession`: Database session
- `get_user_repo(db: AsyncSession) -> UserRepository`
- `get_current_user_id(token: str = Cookie(...)) -> int`: Extract user from JWT cookie
- `get_current_user(..., db: AsyncSession, user_id: int) -> User`: Get full user object
- `require_active_user(user: User) -> User`: Verify user is active

**Rules Reference:** @rules/backend_arch_design.md Section 4 (Dependency Injection)

#### 2.7.2 Auth Router (`src/backend/api/v1/auth.py`)

**Purpose:** Authentication endpoints.

**Endpoints:**

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | `/api/v1/auth/register` | User registration | No |
| POST | `/api/v1/auth/login` | User login | No |
| POST | `/api/v1/auth/logout` | User logout | Yes |
| GET | `/api/v1/auth/me` | Get current user | Yes |
| PUT | `/api/v1/auth/me` | Update profile | Yes |
| PUT | `/api/v1/auth/me/password` | Change password | Yes |

**Cookie Handling:**
- Login: Set `access_token` HttpOnly cookie
- Logout: Clear `access_token` cookie
- Cookie settings: `HttpOnly=True`, `Secure=False` (dev), `SameSite="lax"`, `Max-Age=1800`

**Rules Reference:** 
- @rules/security.md Section 2 (HttpOnly Cookies)
- @rules/security.md Section 4 (Rate Limiting on auth endpoints)

#### 2.7.3 API Router Aggregation (`src/backend/api/v1/__init__.py`)

Include auth router with prefix `/api/v1`.

### 2.8 Main Application (`src/backend/main.py`)

**Updates Required:**
- Add CORS middleware (dynamic origins from config)
- Add CorrelationIdMiddleware
- Add RateLimitMiddleware (slowapi)
- Include API routers
- Add lifespan context manager for DB initialization

**Rules Reference:** 
- @rules/security.md Section 4 (CORS)
- @rules/backend_arch_design.md Section 7 (Correlation IDs)

### 2.9 Alembic Migrations

**Initialize:**
```bash
cd src/backend
alembic init alembic
```

**Configure `alembic/env.py`:**
- Use async URL from config
- Import User model for autogenerate
- Use `run_async` for async operations

**Create Initial Migration:**
```bash
alembic revision --autogenerate -m "create_users_table"
```

**Rules Reference:** @rules/backend_arch_design.md Section 3.1 (Migration Safety)

---

## 3. Frontend Implementation

### 3.1 Dependencies to Add (package.json)

```json
{
  "dependencies": {
    "@tanstack/react-query": "^5.62.0",
    "axios": "^1.7.9",
    "zustand": "^5.0.2",
    "react-router-dom": "^7.0.0",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.6.0",
    "lucide-react": "^0.468.0",
    "@radix-ui/react-slot": "^1.1.1",
    "@radix-ui/react-dialog": "^1.1.4",
    "@radix-ui/react-dropdown-menu": "^2.1.4",
    "@radix-ui/react-label": "^2.1.1",
    "@radix-ui/react-separator": "^1.1.1",
    "@radix-ui/react-tooltip": "^1.1.6",
    "react-error-boundary": "^4.1.2"
  },
  "devDependencies": {
    "vitest": "^2.1.8",
    "@testing-library/react": "^16.1.0",
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/user-event": "^14.5.2",
    "jsdom": "^25.0.1",
    "playwright": "^1.49.1",
    "@playwright/test": "^1.49.1",
    "@types/uuid": "^10.0.0",
    "uuid": "^11.0.3",
    "tailwindcss": "^3.4.17",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.49"
  }
}
```

### 3.2 Tailwind & CSS Setup

#### 3.2.1 Tailwind Config (`src/frontend/tailwind.config.js`)

**Purpose:** Configure Tailwind with shadcn/ui theme.

**Content:**
- Add paths for component files
- Extend theme with custom colors matching the Trinity Bank theme
- Add dark mode support

#### 3.2.2 Global CSS (`src/frontend/src/globals.css`)

**Purpose:** CSS variables for shadcn/ui theming.

**Variables to Add:**
```css
:root {
  --background: 0 0% 100%;
  --foreground: 345 6% 13%;
  --primary: 45 73% 65%;
  --primary-foreground: 345 6% 13%;
  --secondary: 0 0% 96%;
  --secondary-foreground: 345 6% 13%;
  --muted: 0 0% 96%;
  --muted-foreground: 0 0% 45%;
  --info: 214 95% 40%;
  --success: 142 71% 29%;
  --warning: 38 92% 50%;
  --destructive: 0 84% 60%;
  --border: 0 0% 90%;
  --input: 0 0% 90%;
  --ring: 45 73% 65%;
  --radius: 0.5rem;
}

.dark {
  --background: 345 6% 7%;
  --foreground: 0 0% 98%;
  --primary: 45 73% 65%;
  --primary-foreground: 345 6% 7%;
  --secondary: 345 6% 13%;
  --secondary-foreground: 0 0% 98%;
  --muted: 345 5% 15%;
  --muted-foreground: 0 0% 64%;
  --border: 345 5% 20%;
  --input: 345 5% 20%;
  --ring: 45 73% 65%;
}
```

**Rules Reference:** @rules/frontend_arch_design.md Section 2 (Design Tokens)

### 3.3 Utility Layer (`/lib`)

#### 3.3.1 Logger (`src/frontend/src/lib/logger.ts`)

**Purpose:** Centralized logging utility (no bare console.log).

**Functions:**
```typescript
export const logger = {
  debug: (message: string, meta?: object) => { ... },
  info: (message: string, meta?: object) => { ... },
  warn: (message: string, meta?: object) => { ... },
  error: (message: string, meta?: object) => { ... },
}
```

**Rules Reference:** @rules/frontend_arch_design.md Section 4 (Logging)

#### 3.3.2 API Client (`src/frontend/src/lib/api.ts`)

**Purpose:** Axios instance with interceptors.

**Configuration:**
- Base URL from environment variable
- `withCredentials: true` (for HttpOnly cookies)
- Request interceptor: Add X-Correlation-ID header (UUID)
- Response interceptor: Handle 401 errors, redirect to login

#### 3.3.3 Utils (`src/frontend/src/lib/utils.ts`)

**Purpose:** Utility functions.

**Functions:**
- `cn(...inputs: ClassValue[]): string`: Tailwind class merging
- `formatDate(date: string): string`: Date formatting
- `generateCorrelationId(): string`: UUID generation

### 3.4 Types Layer (`/types`)

#### 3.4.1 User Types (`src/frontend/src/types/user.ts`)

```typescript
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  role: 'USER' | 'ADMIN';
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface PasswordChange {
  current_password: string;
  new_password: string;
}
```

### 3.5 Store Layer (`/store`)

#### 3.5.1 Auth Store (`src/frontend/src/store/authStore.ts`)

**Purpose:** Zustand store for authentication state.

**State:**
```typescript
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setAuthenticated: (value: boolean) => void;
  logout: () => void;
}
```

**Rules Reference:** @rules/frontend_arch_design.md Section 1 (Zustand)

### 3.6 Hooks Layer (`/hooks`)

#### 3.6.1 Auth Hooks (`src/frontend/src/hooks/useAuth.ts`)

**Purpose:** TanStack Query hooks for authentication API calls.

**Hooks:**
- `useLogin()`: Mutation for login
- `useRegister()`: Mutation for registration
- `useLogout()`: Mutation for logout
- `useCurrentUser()`: Query for fetching current user
- `useUpdateProfile()`: Mutation for profile update
- `useChangePassword()`: Mutation for password change

**Rules Reference:** @rules/frontend_arch_design.md Section 1 (TanStack Query)

### 3.7 shadcn/ui Components (`/components/ui`)

**Components to Install:**
```bash
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add label
npx shadcn@latest add card
npx shadcn@latest add form
npx shadcn@latest add alert
npx shadcn@latest add dropdown-menu
npx shadcn@latest add separator
npx shadcn@latest add sheet
npx shadcn@latest add tooltip
npx shadcn@latest add avatar
```

### 3.8 Layout Components (`/components/layout`)

#### 3.8.1 App Shell (`src/frontend/src/components/layout/AppShell.tsx`)

**Purpose:** Main layout wrapper following the App Shell pattern.

**Structure:**
```
<div className="h-screen w-screen overflow-hidden">
  <Header />
  <Sidebar />
  <main className="absolute top-14 bottom-8 right-0 left-64 overflow-y-auto">
    {children}
  </main>
  <StatusBar />
</div>
```

**Rules Reference:** @rules/frontend_arch_design.md Section 3 (App Shell)

#### 3.8.2 Header (`src/frontend/src/components/layout/Header.tsx`)

**Purpose:** Fixed top navigation bar.

**Content:**
- Left: App logo/name, hamburger menu (mobile)
- Right: Theme toggle, user dropdown menu

**Tailwind:** `fixed top-0 left-0 w-full h-14 z-50 border-b bg-background`

#### 3.8.3 Sidebar (`src/frontend/src/components/layout/Sidebar.tsx`)

**Purpose:** Left navigation sidebar.

**Content:**
- Navigation links (Dashboard, Profile, Settings)
- Collapsible state (expanded/collapsed)
- Mobile sheet drawer

**Tailwind:** `fixed left-0 top-14 bottom-8 z-40 border-r bg-background`

#### 3.8.4 Status Bar (`src/frontend/src/components/layout/StatusBar.tsx`)

**Purpose:** Fixed bottom status bar.

**Content:**
- Frontend version (from `import.meta.env.VITE_APP_VERSION`)
- Backend version (fetched from `/health`)
- API status indicator (green/red dot)
- Current username

**Tailwind:** `fixed bottom-0 left-0 w-full h-8 z-50 border-t bg-secondary`

### 3.9 Page Components (`/pages`)

#### 3.9.1 Login Page (`src/frontend/src/pages/Login.tsx`)

**Purpose:** User login form.

**Form Fields:**
- Username/email input
- Password input
- Submit button
- Link to register

**data-testid attributes:**
- `login-form`
- `login-username-input`
- `login-password-input`
- `login-submit-button`
- `login-register-link`

#### 3.9.2 Register Page (`src/frontend/src/pages/Register.tsx`)

**Purpose:** User registration form.

**Form Fields:**
- Email input
- Username input
- Full name input (optional)
- Password input
- Confirm password input
- Submit button
- Link to login

**data-testid attributes:**
- `register-form`
- `register-email-input`
- `register-username-input`
- `register-fullname-input`
- `register-password-input`
- `register-confirm-password-input`
- `register-submit-button`
- `register-login-link`

#### 3.9.3 Dashboard Page (`src/frontend/src/pages/Dashboard.tsx`)

**Purpose:** Mock dashboard (post-login landing).

**Content:**
- Welcome message with user's name
- Placeholder cards for future features

**data-testid attributes:**
- `dashboard-container`
- `dashboard-welcome-message`

#### 3.9.4 Profile Page (`src/frontend/src/pages/Profile.tsx`)

**Purpose:** View and edit user profile.

**Content:**
- Display current info
- Edit form for: full_name, email
- Change password section

**data-testid attributes:**
- `profile-form`
- `profile-email-input`
- `profile-fullname-input`
- `profile-save-button`
- `profile-change-password-button`

### 3.10 Routing (`src/frontend/src/App.tsx`)

**Purpose:** React Router setup with protected routes.

**Routes:**
| Path | Component | Auth Required |
|------|-----------|---------------|
| `/login` | Login | No |
| `/register` | Register | No |
| `/` | Dashboard | Yes |
| `/profile` | Profile | Yes |

**Protected Route Logic:** Check auth store, redirect to /login if not authenticated.

### 3.11 Error Boundaries

#### 3.11.1 Global Error Boundary (`src/frontend/src/components/ErrorBoundary.tsx`)

**Purpose:** Catch all unhandled errors.

**Implementation:** Use `react-error-boundary` with `onError` callback to logger.

**Rules Reference:** @rules/frontend_arch_design.md Section 6 (Error Boundaries)

---

## 4. Authentication Flow

### 4.1 Registration Flow

```
1. User fills registration form → Frontend
2. Frontend POST /api/v1/auth/register → Backend
3. Backend validates input (Pydantic)
4. Backend hashes password (bcrypt)
5. Backend creates User record (SQLAlchemy)
6. Backend returns UserResponse (no password)
7. Frontend redirects to /login
```

### 4.2 Login Flow

```
1. User fills login form → Frontend
2. Frontend POST /api/v1/auth/login → Backend
3. Backend verifies credentials (bcrypt verify)
4. Backend creates JWT token (expires in 30 min)
5. Backend sets HttpOnly cookie: access_token=<jwt>
6. Frontend receives 200 OK, updates auth store
7. Frontend redirects to /
```

### 4.3 Authenticated Request Flow

```
1. Frontend makes API call with withCredentials: true
2. Browser automatically sends access_token cookie
3. Backend extracts cookie, decodes JWT
4. Backend validates token (signature, expiration)
5. Backend fetches User from database
6. Backend checks user.is_active
7. Backend processes request
8. Backend returns response
```

### 4.4 Logout Flow

```
1. User clicks logout → Frontend
2. Frontend POST /api/v1/auth/logout → Backend
3. Backend clears access_token cookie (set empty, expired)
4. Frontend clears auth store
5. Frontend redirects to /login
```

---

## 5. File Structure

### Backend Files

```
src/backend/
├── alembic/
│   ├── env.py              # Async Alembic configuration
│   ├── script.py.mako
│   └── versions/
│       └── 001_create_users_table.py
├── api/
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py     # Router aggregation
│   │   ├── auth.py         # Auth endpoints
│   │   └── deps.py         # Dependencies
├── core/
│   ├── __init__.py
│   ├── config.py           # Settings
│   ├── database.py         # Async DB setup
│   ├── logging.py          # Structured logging
│   └── security.py         # JWT & bcrypt
├── models/
│   ├── __init__.py
│   └── user.py             # SQLAlchemy User model
├── repositories/
│   ├── __init__.py
│   ├── base.py             # Generic repository
│   └── user.py             # User repository
├── schemas/
│   ├── __init__.py
│   ├── user.py             # Pydantic user schemas
│   └── auth.py             # Pydantic auth schemas
├── services/
│   ├── __init__.py
│   └── auth_service.py     # Auth business logic
├── main.py                 # Updated app entry
└── pyproject.toml          # Updated dependencies
```

### Frontend Files

```
src/frontend/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppShell.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── StatusBar.tsx
│   │   ├── ui/             # shadcn/ui components
│   │   └── ErrorBoundary.tsx
│   ├── hooks/
│   │   └── useAuth.ts
│   ├── lib/
│   │   ├── api.ts
│   │   ├── logger.ts
│   │   └── utils.ts
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   └── Profile.tsx
│   ├── store/
│   │   └── authStore.ts
│   ├── types/
│   │   └── user.ts
│   ├── globals.css         # Updated with CSS variables
│   ├── App.tsx             # Updated with routing
│   └── main.tsx
├── tailwind.config.js      # New
├── postcss.config.js       # New
├── vitest.config.ts        # New
├── playwright.config.ts    # New
└── package.json            # Updated
```

### Test Files

```
tests/
├── backend/
│   ├── conftest.py         # Pytest fixtures
│   ├── test_security.py    # Security utils tests
│   ├── test_auth_api.py    # Auth endpoint tests
│   └── test_user_repo.py   # Repository tests
├── frontend/
│   ├── setup.ts            # Vitest setup
│   ├── components/
│   │   └── Login.test.tsx
│   └── hooks/
│       └── useAuth.test.ts
└── e2e/
    ├── auth.spec.ts        # Authentication flows
    └── fixtures/
        └── user.json
```

### Configuration Files

```
.env                      # Environment variables
.env.example              # Template for .env
docs/features/auth-boilerplate/
├── STATUS.md
└── plan.md               # This file
```

---

## 6. Testing Strategy

### 6.1 Backend Tests (pytest)

#### Test Configuration (`tests/backend/conftest.py`)

**Fixtures:**
- `event_loop`: Async event loop
- `db_engine`: In-memory SQLite async engine
- `db_session`: AsyncSession for tests
- `client`: Async HTTP test client
- `test_user`: Pre-created user for auth tests

**Rules Reference:** @rules/development_testing.md Section 4 (Backend Testing)

#### Test Files

**`tests/backend/test_security.py`:**
- Test password hashing with bcrypt
- Test password verification
- Test JWT creation and decoding
- Test expired token handling
- Test invalid token handling

**`tests/backend/test_auth_api.py`:**
- Test registration success (201)
- Test registration duplicate email (409)
- Test registration invalid email (422)
- Test login success (200 + cookie set)
- Test login invalid credentials (401)
- Test logout clears cookie (200)
- Test get current user (200)
- Test get current user unauthorized (401)
- Test update profile (200)
- Test change password (200)
- Test change password wrong current (400)

**`tests/backend/test_user_repo.py`:**
- Test create user
- Test get by email
- Test get by username
- Test update user
- Test change password

### 6.2 Frontend Tests (Vitest + React Testing Library)

#### Test Configuration (`tests/frontend/setup.ts`)

- Configure Vitest with jsdom
- Mock API calls
- Setup React Testing Library

**Rules Reference:** @rules/development_testing.md Section 3 (Frontend Testing)

#### Test Files

**`tests/frontend/components/Login.test.tsx`:**
- Test renders login form
- Test username input updates
- Test password input updates
- Test submit calls login mutation
- Test displays error on failed login

**`tests/frontend/hooks/useAuth.test.ts`:**
- Test useLogin mutation
- Test useRegister mutation
- Test useCurrentUser query

### 6.3 E2E Tests (Playwright)

#### Test Configuration (`playwright.config.ts`)

- Target Docker Compose environment
- Use data-testid selectors only

**Rules Reference:** @rules/development_testing.md Section 6 (E2E Testing)

#### Test File (`tests/e2e/auth.spec.ts`)

**Test Cases:**
1. **User Registration Journey:**
   - Navigate to /register
   - Fill registration form
   - Submit form
   - Verify redirect to /login

2. **User Login Journey:**
   - Navigate to /login
   - Fill credentials
   - Submit form
   - Verify redirect to /dashboard
   - Verify user info displayed

3. **Profile Update Journey:**
   - Login as test user
   - Navigate to /profile
   - Update full name
   - Save changes
   - Verify success message

4. **Password Change Journey:**
   - Login as test user
   - Navigate to /profile
   - Change password
   - Logout
   - Login with new password
   - Verify success

5. **Protected Route Guard:**
   - Try to access / without login
   - Verify redirect to /login

---

## 7. Implementation Order

### Phase 1: Backend Foundation (Days 1-2)

**Goal:** Core backend infrastructure

1. **Setup Dependencies**
   - Update `pyproject.toml` with all dependencies
   - Run `uv sync` to install

2. **Core Layer**
   - Create `src/backend/core/config.py`
   - Create `src/backend/core/database.py`
   - Create `src/backend/core/logging.py`
   - Create `src/backend/core/security.py`
   - **TDD:** Write tests first, then implementation

3. **Database Model**
   - Create `src/backend/models/user.py`
   - Create Alembic migration
   - Run migration

4. **Schemas**
   - Create `src/backend/schemas/user.py`
   - Create `src/backend/schemas/auth.py`

**Acceptance Criteria:**
- All core tests pass
- Database migrations run successfully
- Security functions work correctly

### Phase 2: Backend API (Days 3-4)

**Goal:** Complete authentication API

1. **Repository Layer**
   - Create `src/backend/repositories/base.py`
   - Create `src/backend/repositories/user.py`
   - **TDD:** Write tests first

2. **Service Layer**
   - Create `src/backend/services/auth_service.py`
   - **TDD:** Write tests first

3. **API Layer**
   - Create `src/backend/api/deps.py`
   - Create `src/backend/api/v1/auth.py`
   - Update `src/backend/main.py`
   - **TDD:** Write tests first

**Acceptance Criteria:**
- All API tests pass
- Manual test with curl/httpie works:
  ```bash
  curl -X POST http://localhost:8000/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","username":"testuser","password":"testpass123"}'
  ```

### Phase 3: Frontend Foundation (Days 5-6)

**Goal:** Frontend infrastructure and layout

1. **Setup Dependencies**
   - Update `package.json`
   - Run `npm install`

2. **Tailwind & CSS**
   - Create `tailwind.config.js`
   - Create `postcss.config.js`
   - Update `src/globals.css`

3. **Core Utilities**
   - Create `src/lib/logger.ts`
   - Create `src/lib/api.ts`
   - Create `src/lib/utils.ts`

4. **Types & Store**
   - Create `src/types/user.ts`
   - Create `src/store/authStore.ts`

5. **shadcn/ui Setup**
   - Initialize shadcn: `npx shadcn@latest init`
   - Install required components

**Acceptance Criteria:**
- Frontend builds successfully
- No console errors
- Theme CSS variables applied

### Phase 4: Frontend Layout (Days 7-8)

**Goal:** App Shell implementation

1. **Layout Components**
   - Create `src/components/layout/Header.tsx`
   - Create `src/components/layout/Sidebar.tsx`
   - Create `src/components/layout/StatusBar.tsx`
   - Create `src/components/layout/AppShell.tsx`

2. **Error Handling**
   - Create `src/components/ErrorBoundary.tsx`
   - Wrap App with boundary

**Acceptance Criteria:**
- App Shell renders correctly
- Responsive layout works
- Status Bar displays version info

### Phase 5: Frontend Auth (Days 9-10)

**Goal:** Authentication UI and logic

1. **Auth Hooks**
   - Create `src/hooks/useAuth.ts`

2. **Auth Pages**
   - Create `src/pages/Login.tsx`
   - Create `src/pages/Register.tsx`
   - Create `src/pages/Dashboard.tsx`
   - Create `src/pages/Profile.tsx`

3. **Routing**
   - Update `src/App.tsx` with Router
   - Implement ProtectedRoute component

**Acceptance Criteria:**
- Login/Register forms work
- Protected routes redirect to login
- Authenticated users see dashboard

### Phase 6: Testing (Days 11-12)

**Goal:** Comprehensive test coverage

1. **Backend Tests**
   - Write remaining test files
   - Achieve >80% coverage

2. **Frontend Tests**
   - Configure Vitest
   - Write component tests
   - Write hook tests

3. **E2E Tests**
   - Configure Playwright
   - Write auth flow tests

**Acceptance Criteria:**
- All tests pass
- Coverage meets targets
- E2E tests run against Docker Compose

### Phase 7: Integration & Documentation (Day 13)

**Goal:** Final integration and documentation

1. **Integration Testing**
   - Full stack test
   - Cookie handling verified
   - CORS configuration verified

2. **Environment Setup**
   - Create `.env.example`
   - Document setup instructions

3. **Update Feature Status**
   - Update `STATUS.md`
   - Mark implementation complete

**Acceptance Criteria:**
- Full user journey works end-to-end
- Documentation is complete
- All rules compliance verified

---

## 8. Dependencies

### Backend Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | >=0.115.0 | Web framework |
| uvicorn[standard] | >=0.32.0 | ASGI server |
| sqlalchemy[asyncio] | >=2.0.0 | Async ORM |
| aiosqlite | >=0.20.0 | Async SQLite driver |
| alembic | >=1.14.0 | Database migrations |
| pydantic-settings | >=2.6.0 | Environment config |
| python-jose[cryptography] | >=3.3.0 | JWT handling |
| bcrypt | >=4.2.0 | Password hashing |
| python-multipart | >=0.0.17 | Form parsing |
| email-validator | >=2.2.0 | Email validation |
| slowapi | >=0.1.9 | Rate limiting |

### Backend Dev Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >=8.3.0 | Testing framework |
| pytest-asyncio | >=0.24.0 | Async test support |
| httpx | >=0.27.0 | HTTP client for tests |
| pytest-cov | >=6.0.0 | Coverage reporting |

### Frontend Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| @tanstack/react-query | ^5.62.0 | Server state management |
| axios | ^1.7.9 | HTTP client |
| zustand | ^5.0.2 | Client state management |
| react-router-dom | ^7.0.0 | Routing |
| class-variance-authority | ^0.7.1 | Component variants |
| clsx | ^2.1.1 | Class name utilities |
| tailwind-merge | ^2.6.0 | Tailwind class merging |
| lucide-react | ^0.468.0 | Icons |
| @radix-ui/* | ^1.1.x | Headless UI primitives |
| react-error-boundary | ^4.1.2 | Error handling |

### Frontend Dev Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| vitest | ^2.1.8 | Test runner |
| @testing-library/react | ^16.1.0 | Component testing |
| @testing-library/jest-dom | ^6.6.3 | DOM matchers |
| @testing-library/user-event | ^14.5.2 | User interactions |
| jsdom | ^25.0.1 | DOM environment |
| @playwright/test | ^1.49.1 | E2E testing |
| tailwindcss | ^3.4.17 | CSS framework |
| autoprefixer | ^10.4.20 | CSS processing |
| postcss | ^8.4.49 | CSS processing |

---

## 9. Environment Variables

### .env.example

```bash
# Backend
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
CORS_ORIGINS=http://localhost:5173,http://localhost:4173
ENVIRONMENT=development

# Frontend
VITE_API_URL=http://localhost:8000
VITE_APP_VERSION=0.1.0
```

---

## 10. Git Branching Strategy

**Working Branch:** `feat/auth-boilerplate`

**Commit Messages (Conventional Commits):**
```
feat(backend): add user authentication endpoints
feat(frontend): implement login and register pages
feat(core): add JWT security utilities
test(backend): add auth API tests
test(frontend): add Login component tests
chore(deps): add bcrypt and python-jose
docs: add auth implementation plan
```

---

## 11. Version Impact

- **Backend:** Minor version bump (0.1.0 → 0.2.0) - New features, backward compatible
- **Frontend:** Minor version bump (0.0.0 → 0.1.0) - Initial feature set

---

## 12. Security Checklist

Per @rules/security.md:

- [ ] JWT stored in HttpOnly cookie (not localStorage)
- [ ] Cookie settings: HttpOnly=True, Secure=False (dev), SameSite="lax"
- [ ] Passwords hashed with bcrypt (not passlib)
- [ ] CORS origins loaded from environment (not "*")
- [ ] Rate limiting on auth endpoints (/login, /register)
- [ ] IDOR prevention: Users can only access their own data
- [ ] Input validation with Pydantic
- [ ] Parameterized queries only (SQLAlchemy ORM)
- [ ] No secrets in code

---

## 13. Rule Compliance Summary

| Rule File | Sections Applied |
|-----------|-----------------|
| @rules/backend_arch_design.md | 1, 3, 3.1, 4, 5, 6, 7, 8, 9, 10 |
| @rules/frontend_arch_design.md | 1, 2, 3, 4, 5, 6 |
| @rules/security.md | 2, 3, 4, 5 |
| @rules/development_testing.md | 1, 2, 3, 4, 6 |

---

## 14. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Async/await issues | Medium | High | Follow SQLAlchemy 2.0 async patterns strictly |
| JWT secret exposure | Low | Critical | Use .env, never commit secrets |
| CORS misconfiguration | Medium | Medium | Test with frontend origin explicitly |
| Cookie not persisting | Medium | Medium | Verify withCredentials and SameSite settings |
| Test flakiness | Medium | Medium | Use isolated test DB, proper fixtures |

---

## 15. Acceptance Criteria Summary

### Functional Requirements
- [ ] Users can register with unique email/username
- [ ] Users can log in with valid credentials
- [ ] JWT token stored in HttpOnly cookie
- [ ] Users can view their profile
- [ ] Users can update profile information
- [ ] Users can change their password
- [ ] Users can log out
- [ ] Unauthenticated users redirected to login
- [ ] Dashboard accessible only when authenticated

### Technical Requirements
- [ ] All backend tests pass (>80% coverage)
- [ ] All frontend tests pass
- [ ] All E2E tests pass
- [ ] No TypeScript errors
- [ ] No ESLint errors
- [ ] App Shell layout matches spec
- [ ] Status Bar displays versions

### Security Requirements
- [ ] HttpOnly cookies implemented
- [ ] bcrypt password hashing
- [ ] Input validation on all endpoints
- [ ] Rate limiting on auth endpoints
- [ ] IDOR prevention implemented
- [ ] CORS properly configured

---

*Plan created by: Planning Agent*
*Date: 2026-02-23*
*Version: 1.0.0*
