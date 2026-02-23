# Auth Boilerplate Documentation Report

**Feature:** Authentication Boilerplate  
**Status:** ✅ Documentation Complete  
**Date:** 2026-02-23  
**Version:** 1.0.0  

---

## Table of Contents

1. [Feature Overview](#1-feature-overview)
2. [Architecture](#2-architecture)
3. [API Documentation](#3-api-documentation)
4. [Frontend Components](#4-frontend-components)
5. [Authentication Flow](#5-authentication-flow)
6. [Security Considerations](#6-security-considerations)
7. [Testing](#7-testing)
8. [Setup/Configuration](#8-setupconfiguration)
9. [Usage Examples](#9-usage-examples)
10. [File Reference](#10-file-reference)

---

## 1. Feature Overview

The Authentication Boilerplate provides a complete, production-ready authentication system for the OC Gamma application. It implements secure user registration, login, logout, profile management, and password change functionality using industry best practices.

### Key Features

| Feature | Description |
|---------|-------------|
| **User Registration** | Create accounts with email, username, and password validation |
| **Secure Login** | JWT-based authentication with HttpOnly cookies |
| **Profile Management** | View and update user profile information |
| **Password Change** | Secure password change with current password verification |
| **Rate Limiting** | Brute-force protection on auth endpoints |
| **Role-Based Access** | Foundation for USER/ADMIN role system |

### Technology Stack

| Layer | Technology |
|-------|------------|
| Backend Framework | FastAPI (async) |
| Database ORM | SQLAlchemy 2.0 |
| Password Hashing | bcrypt |
| Token Format | JWT (HS256) |
| Frontend Framework | React 18+ |
| State Management | Zustand (client), TanStack Query (server) |
| UI Components | shadcn/ui |
| Styling | Tailwind CSS |

---

## 2. Architecture

### 2.1 High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client (Browser)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Login Page  │  │  Dashboard  │  │     Profile Page        │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
│         │                │                      │                │
│  ┌──────▼────────────────▼──────────────────────▼────────────┐  │
│  │              React Frontend (Vite)                        │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐   │  │
│  │  │  useAuth    │  │ authStore   │  │   api client     │   │  │
│  │  │   hooks     │  │  (Zustand)  │  │   (Axios)        │   │  │
│  │  └─────────────┘  └─────────────┘  └────────┬─────────┘   │  │
│  └─────────────────────────────────────────────┼─────────────┘  │
│                                                │                 │
│                       withCredentials: true   │                 │
└────────────────────────────────────────────────┼────────────────┘
                                                 │
                       ┌─────────────────────────▼─────────────────┐
                       │         HTTP/HTTPS + Cookies              │
                       └─────────────────────────┬─────────────────┘
                                                 │
┌────────────────────────────────────────────────┼─────────────────┐
│              Backend (FastAPI)                 │                 │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────▼──────────┐      │
│  │   API Layer │  │ Repository  │  │   Security Layer    │      │
│  │  (/api/v1)  │  │   Pattern   │  │  (JWT, bcrypt)      │      │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────┘      │
│         │                │                                       │
│  ┌──────▼────────────────▼──────────────┐                       │
│  │     Database (SQLite/PostgreSQL)     │                       │
│  │         SQLAlchemy 2.0 ORM           │                       │
│  └──────────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Backend Layer Architecture

The backend follows a strict layer-based architecture as defined in `@rules/backend_arch_design.md`:

```
┌─────────────────────────────────────────────────────────────┐
│  API Layer (/api)                                           │
│  ├── v1/auth.py         - Auth endpoints                    │
│  ├── v1/deps.py         - FastAPI dependencies              │
│  └── Exception handlers - HTTP error responses              │
├─────────────────────────────────────────────────────────────┤
│  Service Layer (/services)                                  │
│  └── auth_service.py    - Cross-repository business logic   │
├─────────────────────────────────────────────────────────────┤
│  Repository Layer (/repositories)                           │
│  ├── base.py            - Generic CRUD operations           │
│  └── user.py            - User-specific queries             │
├─────────────────────────────────────────────────────────────┤
│  Schema Layer (/schemas)                                    │
│  ├── user.py            - Pydantic User models              │
│  └── auth.py            - Pydantic Auth models              │
├─────────────────────────────────────────────────────────────┤
│  Model Layer (/models)                                      │
│  ├── base.py            - SQLAlchemy base                   │
│  └── user.py            - User table definition             │
├─────────────────────────────────────────────────────────────┤
│  Core Layer (/core)                                         │
│  ├── config.py          - Pydantic settings                 │
│  ├── database.py        - Async engine/session              │
│  ├── security.py        - JWT & bcrypt                      │
│  └── logging.py         - Structured JSON logging           │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Frontend Architecture

The frontend follows the App Shell pattern with strict separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│  App Shell (Fixed Layout)                                   │
│  ├── Header (top, h-14)        - Logo, user menu           │
│  ├── Sidebar (left)            - Navigation                 │
│  ├── Main Content (scrollable) - Page content               │
│  └── Status Bar (bottom, h-8)  - Versions, API status      │
├─────────────────────────────────────────────────────────────┤
│  State Management                                           │
│  ├── authStore.ts (Zustand)    - Auth state                │
│  └── useAuth.ts (TanStack)     - Server state + mutations  │
├─────────────────────────────────────────────────────────────┤
│  API Layer                                                  │
│  ├── api.ts (Axios)            - HTTP client               │
│  └── logger.ts                 - Structured logging        │
├─────────────────────────────────────────────────────────────┤
│  Pages                                                      │
│  ├── Login.tsx                 - Authentication            │
│  ├── Register.tsx              - User creation             │
│  ├── Dashboard.tsx             - Post-login landing        │
│  └── Profile.tsx               - User settings             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. API Documentation

### 3.1 Base URL

```
Development: http://localhost:8000/api/v1
Production:  https://api.yourdomain.com/api/v1
```

### 3.2 Authentication Endpoints

All authenticated endpoints require the `access_token` HttpOnly cookie to be present.

#### POST /auth/register

Register a new user account.

**Request:**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "role": "USER",
  "created_at": "2026-02-23T10:00:00",
  "updated_at": "2026-02-23T10:00:00"
}
```

**Error Responses:**
- `409 Conflict` - Email or username already exists
- `422 Unprocessable Entity` - Invalid input (e.g., invalid email format)
- `429 Too Many Requests` - Rate limit exceeded (3 requests/minute)

---

#### POST /auth/login

Authenticate and receive JWT cookie.

**Request:**
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=securepassword123
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Response Headers:**
```http
Set-Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...; 
            HttpOnly; Max-Age=1800; Path=/; SameSite=lax
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials (generic message)
- `429 Too Many Requests` - Rate limit exceeded (5 requests/minute)

---

#### POST /auth/logout

Clear authentication cookie.

**Request:**
```http
POST /api/v1/auth/logout
Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

**Response Headers:**
```http
Set-Cookie: access_token=""; expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/
```

---

#### GET /auth/me

Get current authenticated user's profile.

**Request:**
```http
GET /api/v1/auth/me
Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "role": "USER",
  "created_at": "2026-02-23T10:00:00",
  "updated_at": "2026-02-23T10:00:00"
}
```

**Error Responses:**
- `401 Unauthorized` - Not authenticated or invalid token

---

#### PUT /auth/me

Update current user's profile.

**Request:**
```http
PUT /api/v1/auth/me
Content-Type: application/json
Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "email": "newemail@example.com",
  "full_name": "Johnathan Doe"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "newemail@example.com",
  "username": "johndoe",
  "full_name": "Johnathan Doe",
  "is_active": true,
  "role": "USER",
  "created_at": "2026-02-23T10:00:00",
  "updated_at": "2026-02-23T10:30:00"
}
```

---

#### PUT /auth/me/password

Change current user's password.

**Request:**
```http
PUT /api/v1/auth/me/password
Content-Type: application/json
Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "current_password": "securepassword123",
  "new_password": "newsecurepassword456"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Responses:**
- `400 Bad Request` - Current password is incorrect

---

### 3.3 Schema Reference

#### UserCreate (Registration)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| email | string | Valid email format | User's email address |
| username | string | 3-100 chars | Unique username |
| password | string | 8-255 chars | User's password |
| full_name | string | Optional, max 255 | Display name |

#### UserResponse

| Field | Type | Description |
|-------|------|-------------|
| id | integer | User ID |
| email | string | User's email |
| username | string | Unique username |
| full_name | string | Display name (nullable) |
| is_active | boolean | Account status |
| role | string | "USER" or "ADMIN" |
| created_at | ISO datetime | Account creation time |
| updated_at | ISO datetime | Last update time |

#### PasswordChange

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| current_password | string | Required | Current password for verification |
| new_password | string | 8-255 chars | New password to set |

---

## 4. Frontend Components

### 4.1 Component Hierarchy

```
App.tsx
├── ErrorBoundary (Global)
├── QueryClientProvider
└── AppShell
    ├── Header
    │   └── UserDropdown
    ├── Sidebar
    │   └── NavLinks
    ├── Main Content (Outlet)
    │   ├── Login
    │   ├── Register
    │   ├── Dashboard
    │   └── Profile
    └── StatusBar
```

### 4.2 Key Components

#### AppShell

The main layout wrapper implementing the fixed App Shell pattern.

**Location:** `src/frontend/src/components/layout/AppShell.tsx`

**Structure:**
- Fixed header (56px height)
- Collapsible sidebar (256px expanded, 64px collapsed)
- Scrollable main content area
- Fixed status bar (32px height)

#### ProtectedRoute

Higher-order component that redirects unauthenticated users to login.

**Usage:**
```typescript
<Route element={<ProtectedRoute />}>
  <Route path="/" element={<Dashboard />} />
  <Route path="/profile" element={<Profile />} />
</Route>
```

#### Auth Pages

| Page | Route | Purpose |
|------|-------|---------|
| Login | `/login` | User authentication form |
| Register | `/register` | New account creation |
| Dashboard | `/` | Post-login landing page |
| Profile | `/profile` | View/edit user profile |

### 4.3 State Management

#### Auth Store (Zustand)

```typescript
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  logout: () => void;
}
```

**Key Points:**
- Synchronous state updates for immediate UI feedback
- `isLoading` starts true until auth check completes
- `logout()` clears state without API call (for immediate UI update)

#### Auth Hooks (TanStack Query)

```typescript
// Query for current user
const { data: user, isLoading } = useCurrentUser();

// Mutations for auth actions
const login = useLogin();
const register = useRegister();
const logout = useLogout();
const updateProfile = useUpdateProfile();
const changePassword = useChangePassword();
```

**Key Points:**
- `useCurrentUser()` automatically syncs with authStore
- Mutations invalidate queries on success
- Error handling integrated with logger

---

## 5. Authentication Flow

### 5.1 Registration Flow

```
┌──────────┐     ┌──────────────┐     ┌─────────────────┐
│   User   │────▶│  Frontend    │────▶│     Backend     │
└──────────┘     └──────────────┘     └─────────────────┘
                      │                        │
                      │ 1. Fill registration    │
                      │    form                │
                      ▼                        │
               ┌──────────────┐               │
               │   Register   │               │
               │    Page      │               │
               └──────┬───────┘               │
                      │ 2. POST /register      │
                      │    (JSON payload)      │
                      └───────────────────────▶│
                                               │
                                               │ 3. Validate input
                                               │    (Pydantic)
                                               │
                                               │ 4. Hash password
                                               │    (bcrypt)
                                               │
                                               │ 5. Create user
                                               │    (SQLAlchemy)
                                               │
                                               │ 6. Return UserResponse
                      │                        │
                      │ 7. 201 Created         │
                      │    (user data)         │
                      │◀───────────────────────┘
                      │
                      │ 8. Redirect to /login
                      ▼
```

### 5.2 Login Flow

```
┌──────────┐     ┌──────────────┐     ┌─────────────────┐
│   User   │────▶│  Frontend    │────▶│     Backend     │
└──────────┘     └──────────────┘     └─────────────────┘
                      │                        │
                      │ 1. Enter credentials    │
                      ▼                        │
               ┌──────────────┐               │
               │    Login     │               │
               │    Page      │               │
               └──────┬───────┘               │
                      │ 2. POST /login         │
                      │    (form-urlencoded)   │
                      └───────────────────────▶│
                                               │
                                               │ 3. Verify credentials
                                               │    (bcrypt verify)
                                               │
                                               │ 4. Create JWT
                                               │    (30 min expiry)
                                               │
                                               │ 5. Set HttpOnly cookie
                                               │    (access_token)
                                               │
                                               │ 6. Return Token
                      │                        │
                      │ 7. 200 OK + Cookie     │
                      │◀───────────────────────┘
                      │
                      │ 8. Fetch /me
                      │ 9. Update authStore
                      │ 10. Redirect to /
                      ▼
```

### 5.3 Authenticated Request Flow

```
┌──────────────┐                    ┌─────────────────┐
│  Frontend    │────────────────────│     Backend     │
└──────────────┘                    └─────────────────┘
       │                                     │
       │ 1. API call with                    │
       │    withCredentials: true            │
       └─────────────────────────────────────▶│
                                              │
                                              │ 2. Browser sends
                                              │    access_token cookie
                                              │    automatically
                                              │
                                              │ 3. Extract token
                                              │    from Cookie header
                                              │
                                              │ 4. Decode & verify JWT
                                              │
                                              │ 5. Extract user_id
                                              │    from "sub" claim
                                              │
                                              │ 6. Fetch user from DB
                                              │
                                              │ 7. Check is_active
                                              │
                                              │ 8. Process request
       │                                     │
       │ 9. Return response                  │
       │◀────────────────────────────────────┘
       │
       │ 10. Update TanStack cache
       ▼
```

### 5.4 Logout Flow

```
┌──────────────┐     ┌─────────────────┐
│  Frontend    │────▶│     Backend     │
└──────────────┘     └─────────────────┘
       │                     │
       │ 1. User clicks       │
       │    logout           │
       │                     │
       │ 2. POST /logout      │
       │    (with cookie)    │
       └─────────────────────▶│
                             │
                             │ 3. Delete cookie
                             │    (set expired)
                             │
       │ 4. 200 OK            │
       │◀─────────────────────┘
       │
       │ 5. Clear authStore
       │ 6. Clear query cache
       │ 7. Redirect /login
       ▼
```

---

## 6. Security Considerations

### 6.1 HttpOnly Cookie Storage

JWT tokens are stored in HttpOnly cookies, not localStorage:

```python
# Backend: Setting the cookie
response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,        # Prevents JavaScript access
    secure=is_production, # HTTPS only in production
    samesite="lax",       # CSRF protection
    max_age=1800,         # 30 minutes
)
```

```typescript
// Frontend: Sending credentials
const api = axios.create({
  withCredentials: true,  // Sends cookies with requests
});
```

**Benefits:**
- XSS attacks cannot steal the token
- Browser handles cookie transmission automatically
- CSRF protection via SameSite attribute

### 6.2 Password Security

Using bcrypt (not passlib) for password hashing:

```python
# Hashing (backend/core/security.py)
def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")

# Verification
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )
```

**Key Features:**
- Automatic salt generation
- Adaptive cost factor
- Constant-time comparison

### 6.3 Rate Limiting

IP-based rate limiting on auth endpoints:

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /auth/register | 3 requests | 60 seconds |
| POST /auth/login | 5 requests | 60 seconds |

```python
def check_rate_limit(request: Request, max_requests: int = 5, window_seconds: int = 60):
    key = _get_client_ip(request)
    if _check_rate_limit(key, max_requests, window_seconds):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
        )
```

### 6.4 CORS Configuration

Dynamic CORS origins from environment:

```python
# backend/core/config.py
CORS_ORIGINS: str = "http://localhost:5173,http://localhost:4173"

# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # No wildcards
    allow_credentials=True,                     # For cookies
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Security Rule:** Never use `allow_origins=["*"]` with `allow_credentials=True`.

### 6.5 IDOR Prevention

All user data endpoints use `/me` pattern:

```python
# backend/api/v1/auth.py
@router.get("/me")
async def get_me(
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> UserResponse:
    # User can only access their own data
    return current_user
```

No endpoints accept user IDs as parameters, eliminating IDOR vectors.

### 6.6 Input Validation

Strict Pydantic validation on all inputs:

```python
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=255)

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(None, max_length=255)
    
    model_config = ConfigDict(extra="ignore")  # Reject unknown fields
```

### 6.7 Security Checklist

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| HttpOnly cookies | ✅ | Cookie set with `httponly=True` |
| Secure flag | ✅ | Enabled in production |
| SameSite | ✅ | Set to "lax" |
| bcrypt hashing | ✅ | Using `bcrypt` package |
| Rate limiting | ✅ | IP-based sliding window |
| CORS origins | ✅ | Loaded from environment |
| Input validation | ✅ | Pydantic V2 schemas |
| SQL injection prevention | ✅ | SQLAlchemy ORM |
| IDOR prevention | ✅ | `/me` endpoints only |
| Error handling | ✅ | Generic auth error messages |

---

## 7. Testing

### 7.1 Test Coverage Overview

| Test Suite | Count | Framework |
|------------|-------|-----------|
| Backend Unit Tests | 43 | pytest + pytest-asyncio |
| Frontend Tests | 6 | Vitest + React Testing Library |
| E2E Tests | 5 | Playwright |

### 7.2 Backend Tests

**Run Tests:**
```bash
cd /home/radek/Code/oc-gamma
uv run pytest tests/backend/ -v
```

**Test Files:**

| File | Tests | Coverage |
|------|-------|----------|
| `test_security.py` | 7 | Password hashing, JWT encode/decode |
| `test_auth_api.py` | 27 | All auth endpoints |
| `test_user_repo.py` | 9 | Repository CRUD operations |

**Key Test Cases:**

```python
# Registration tests
test_register_success              # 201 Created
test_register_duplicate_email      # 409 Conflict
test_register_invalid_email        # 422 Validation error

# Login tests
test_login_success                 # 200 OK + cookie set
test_login_invalid_credentials     # 401 Unauthorized (generic message)
test_login_rate_limit              # 429 Too Many Requests

# Authenticated endpoint tests
test_get_me_success                # 200 OK
test_get_me_unauthorized           # 401 Unauthorized
test_update_profile                # 200 OK
test_change_password               # 200 OK
test_change_password_wrong_current # 400 Bad Request
```

### 7.3 Frontend Tests

**Run Tests:**
```bash
cd /home/radek/Code/oc-gamma/src/frontend
npm run test
```

**Test Files:**

| File | Tests |
|------|-------|
| `Login.test.tsx` | 5 tests for login form |
| `useAuth.test.ts` | 1 test for auth hooks |

### 7.4 E2E Tests

**Run Tests:**
```bash
cd /home/radek/Code/oc-gamma
docker compose up -d
npx playwright test tests/e2e/
```

**Test Scenarios:**

1. **User Registration Journey**
   - Navigate to /register
   - Fill registration form
   - Submit form
   - Verify redirect to /login

2. **User Login Journey**
   - Navigate to /login
   - Fill credentials
   - Submit form
   - Verify redirect to /dashboard
   - Verify user info displayed

3. **Profile Update Journey**
   - Login as test user
   - Navigate to /profile
   - Update full name
   - Save changes
   - Verify success message

4. **Password Change Journey**
   - Login as test user
   - Navigate to /profile
   - Change password
   - Logout
   - Login with new password
   - Verify success

5. **Protected Route Guard**
   - Try to access / without login
   - Verify redirect to /login

---

## 8. Setup/Configuration

### 8.1 Environment Variables

Create `.env` file in project root:

```bash
# Backend Settings
SECRET_KEY=your-super-secret-key-min-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
CORS_ORIGINS=http://localhost:5173,http://localhost:4173
ENVIRONMENT=development

# Frontend Settings
VITE_API_URL=http://localhost:8000
VITE_APP_VERSION=0.1.0
```

**Important:** Change `SECRET_KEY` in production! Use a cryptographically secure random string of at least 32 characters.

### 8.2 Installation

**Backend Setup:**
```bash
cd src/backend
uv sync
uv run alembic upgrade head
```

**Frontend Setup:**
```bash
cd src/frontend
npm install
```

### 8.3 Running the Application

**Development Mode:**
```bash
# Terminal 1 - Backend
cd src/backend
uv run uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd src/frontend
npm run dev
```

**Docker Compose:**
```bash
docker compose up -d
```

Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 9. Usage Examples

### 9.1 Using the Auth Hooks

```typescript
import { useLogin, useRegister, useLogout, useCurrentUser } from "@/hooks/useAuth";

// Login
function LoginForm() {
  const login = useLogin();
  
  const handleSubmit = async (credentials) => {
    try {
      await login.mutateAsync(credentials);
      // Redirect to dashboard
    } catch (error) {
      // Show error message
    }
  };
}

// Register
function RegisterForm() {
  const register = useRegister();
  
  const handleSubmit = async (data) => {
    await register.mutateAsync(data);
    // Redirect to login
  };
}

// Logout
function UserMenu() {
  const logout = useLogout();
  
  const handleLogout = () => {
    logout.mutate();
  };
}

// Current User
function Dashboard() {
  const { data: user, isLoading } = useCurrentUser();
  
  if (isLoading) return <Loading />;
  return <h1>Welcome, {user?.full_name}</h1>;
}
```

### 9.2 Protected Route Component

```typescript
import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuthStore();
  
  if (isLoading) return <Loading />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  
  return <Outlet />;
}
```

### 9.3 Making Authenticated API Calls

```typescript
import { api } from "@/lib/api";

// The api instance automatically:
// 1. Sends credentials (cookies)
// 2. Adds correlation ID header
// 3. Handles 401 responses

async function fetchData() {
  const response = await api.get("/api/v1/some-endpoint");
  return response.data;
}
```

### 9.4 Backend Dependency Injection

```python
from fastapi import Depends, APIRouter
from typing import Annotated

from backend.api.deps import get_current_user, get_user_repo
from backend.repositories.user import UserRepository
from backend.schemas.user import UserResponse

router = APIRouter()

@router.get("/protected-endpoint")
async def protected_endpoint(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> dict:
    # current_user is the authenticated user
    # repo is ready to use for database operations
    return {"message": f"Hello, {current_user.username}"}
```

### 9.5 Custom Auth Decorator

```python
from functools import wraps
from fastapi import HTTPException, status

from backend.api.deps import require_active_user

@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: Annotated[User, Depends(require_active_user)],
    repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> dict:
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    await repo.delete(user_id)
    return {"message": "User deleted"}
```

---

## 10. File Reference

### 10.1 Backend Files

| File | Purpose | Lines |
|------|---------|-------|
| `main.py` | FastAPI app setup, middleware, routers | ~100 |
| `api/v1/auth.py` | Authentication endpoints | 316 |
| `api/v1/deps.py` | FastAPI dependencies (auth, DB) | 117 |
| `core/config.py` | Pydantic settings | 43 |
| `core/database.py` | Async SQLAlchemy setup | ~50 |
| `core/security.py` | JWT & bcrypt utilities | 92 |
| `core/logging.py` | Structured JSON logging | ~80 |
| `models/user.py` | User SQLAlchemy model | 39 |
| `models/base.py` | SQLAlchemy declarative base | ~20 |
| `schemas/user.py` | User Pydantic schemas | 80 |
| `schemas/auth.py` | Auth Pydantic schemas | 26 |
| `repositories/base.py` | Generic CRUD repository | ~80 |
| `repositories/user.py` | User repository | ~60 |
| `services/auth_service.py` | Auth business logic | ~40 |

### 10.2 Frontend Files

| File | Purpose |
|------|---------|
| `lib/api.ts` | Axios instance with interceptors |
| `lib/logger.ts` | Centralized logging utility |
| `lib/utils.ts` | Helper functions (cn, uuid) |
| `types/user.ts` | TypeScript user interfaces |
| `store/authStore.ts` | Zustand auth state |
| `hooks/useAuth.ts` | TanStack Query auth hooks |
| `components/layout/AppShell.tsx` | Main layout wrapper |
| `components/layout/Header.tsx` | Top navigation bar |
| `components/layout/Sidebar.tsx` | Left navigation |
| `components/layout/StatusBar.tsx` | Bottom status bar |
| `components/ErrorBoundary.tsx` | Global error boundary |
| `pages/Login.tsx` | Login page |
| `pages/Register.tsx` | Registration page |
| `pages/Dashboard.tsx` | Dashboard page |
| `pages/Profile.tsx` | Profile management page |

### 10.3 Test Files

| File | Purpose |
|------|---------|
| `tests/backend/conftest.py` | Pytest fixtures |
| `tests/backend/test_security.py` | Security utility tests |
| `tests/backend/test_auth_api.py` | Auth endpoint tests |
| `tests/backend/test_user_repo.py` | Repository tests |
| `tests/frontend/setup.ts` | Vitest configuration |
| `tests/frontend/components/Login.test.tsx` | Login component tests |
| `tests/frontend/hooks/useAuth.test.ts` | Auth hook tests |
| `tests/e2e/auth.spec.ts` | E2E auth flow tests |

---

## Related Documentation

- [Project Rules: Security](../../rules/security.md)
- [Project Rules: Backend Architecture](../../rules/backend_arch_design.md)
- [Project Rules: Frontend Architecture](../../rules/frontend_arch_design.md)
- [API Overview](../../api/README.md)
- [Authentication Guide](../../guides/authentication.md)
- [Feature Plan](./plan.md)
- [Security Review](./security-review.md)
- [Code Review](./code-review.md)

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-23 | 1.0.0 | Initial documentation |

---

*Documentation created by Documentation Agent*  
*Last updated: 2026-02-23*
