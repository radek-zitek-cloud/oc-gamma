# Authentication Developer Guide

## Quick Start

This guide shows you how to use the authentication system in your OC Gamma application.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Frontend Usage](#frontend-usage)
3. [Backend Usage](#backend-usage)
4. [Common Patterns](#common-patterns)
5. [Security Best Practices](#security-best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:5173`
- `.env` file configured with proper `CORS_ORIGINS`

### Environment Setup

```bash
# .env
CORS_ORIGINS=http://localhost:5173,http://localhost:4173
SECRET_KEY=your-secret-key-change-in-production
```

---

## Frontend Usage

### 1. Import Auth Hooks

```typescript
import { 
  useLogin, 
  useRegister, 
  useLogout, 
  useCurrentUser,
  useUpdateProfile,
  useChangePassword 
} from "@/hooks/useAuth";
```

### 2. Login Implementation

```typescript
import { useState } from "react";
import { useLogin } from "@/hooks/useAuth";
import { useNavigate } from "react-router-dom";

function LoginForm() {
  const navigate = useNavigate();
  const login = useLogin();
  const [credentials, setCredentials] = useState({
    username: "",
    password: ""
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await login.mutateAsync(credentials);
      navigate("/"); // Redirect to dashboard
    } catch (error) {
      // Error is handled by the hook, but you can show UI feedback
      console.error("Login failed:", error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={credentials.username}
        onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
        placeholder="Username"
      />
      <input
        type="password"
        value={credentials.password}
        onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
        placeholder="Password"
      />
      <button type="submit" disabled={login.isPending}>
        {login.isPending ? "Logging in..." : "Login"}
      </button>
      {login.isError && (
        <p className="error">Invalid username or password</p>
      )}
    </form>
  );
}
```

### 3. Registration Implementation

```typescript
import { useRegister } from "@/hooks/useAuth";
import { useNavigate } from "react-router-dom";

function RegisterForm() {
  const navigate = useNavigate();
  const register = useRegister();
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
    full_name: ""
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await register.mutateAsync(formData);
      navigate("/login"); // Redirect to login after registration
    } catch (error: any) {
      if (error.response?.status === 409) {
        alert("Email or username already exists");
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
}
```

### 4. Protected Routes

```typescript
// components/ProtectedRoute.tsx
import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuthStore();
  
  if (isLoading) {
    return <div>Loading...</div>; // Or a spinner component
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <Outlet />;
}

// App.tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { Login } from "@/pages/Login";
import { Dashboard } from "@/pages/Dashboard";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

### 5. User Dropdown / Logout

```typescript
import { useLogout } from "@/hooks/useAuth";
import { useAuthStore } from "@/store/authStore";

function UserMenu() {
  const logout = useLogout();
  const user = useAuthStore((state) => state.user);

  const handleLogout = () => {
    logout.mutate();
    // No need to redirect - logout clears the store,
    // and ProtectedRoute will handle the redirect
  };

  return (
    <div className="user-menu">
      <span>Welcome, {user?.full_name || user?.username}</span>
      <button onClick={handleLogout} disabled={logout.isPending}>
        Logout
      </button>
    </div>
  );
}
```

### 6. Profile Management

```typescript
import { useCurrentUser, useUpdateProfile, useChangePassword } from "@/hooks/useAuth";

function ProfilePage() {
  const { data: user, isLoading } = useCurrentUser();
  const updateProfile = useUpdateProfile();
  const changePassword = useChangePassword();

  const handleUpdateProfile = async (data: UserUpdate) => {
    await updateProfile.mutateAsync(data);
    // Success - profile updated
  };

  const handleChangePassword = async (currentPassword: string, newPassword: string) => {
    await changePassword.mutateAsync({
      current_password: currentPassword,
      new_password: newPassword
    });
    // Success - password changed
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Profile</h1>
      <ProfileForm 
        user={user} 
        onSubmit={handleUpdateProfile}
        isPending={updateProfile.isPending}
      />
      <PasswordForm 
        onSubmit={handleChangePassword}
        isPending={changePassword.isPending}
      />
    </div>
  );
}
```

### 7. Making Authenticated API Calls

The `api` instance automatically handles authentication:

```typescript
import { api } from "@/lib/api";

// This request automatically includes the HttpOnly cookie
async function fetchUserData() {
  const response = await api.get("/api/v1/auth/me");
  return response.data;
}

// POST request
async function createItem(data: CreateItemData) {
  const response = await api.post("/api/v1/items", data);
  return response.data;
}
```

---

## Backend Usage

### 1. Protecting Endpoints

Use FastAPI dependencies to protect routes:

```python
from fastapi import APIRouter, Depends
from typing import Annotated

from backend.api.deps import get_current_user
from backend.schemas.user import UserResponse

router = APIRouter()

@router.get("/protected-resource")
async def get_protected_resource(
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> dict:
    """Only authenticated users can access this."""
    return {
        "message": f"Hello, {current_user.username}!",
        "user_id": current_user.id
    }
```

### 2. Using the Repository Pattern

```python
from typing import Annotated
from fastapi import APIRouter, Depends

from backend.api.deps import get_current_user, get_user_repo
from backend.repositories.user import UserRepository
from backend.schemas.user import UserResponse

router = APIRouter()

@router.get("/users/search")
async def search_users(
    query: str,
    repo: Annotated[UserRepository, Depends(get_user_repo)],
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> list[UserResponse]:
    """Search users (admin only example)."""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = await repo.search(query)
    return [UserResponse.model_validate(u) for u in users]
```

### 3. Admin-Only Endpoints

```python
from fastapi import HTTPException, status

async def require_admin(
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> UserResponse:
    """Dependency that requires ADMIN role."""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: Annotated[UserResponse, Depends(require_admin)],
    repo: Annotated[UserRepository, Depends(get_user_repo)]
) -> dict:
    """Delete a user (admin only)."""
    await repo.delete(user_id)
    return {"message": "User deleted"}
```

### 4. Custom Auth Logic

```python
from backend.core.security import decode_access_token
from backend.core.logging import get_logger

logger = get_logger(__name__)

@router.post("/webhook")
async def webhook_handler(request: Request) -> dict:
    """Custom auth logic example."""
    # Get token from custom header
    token = request.headers.get("X-Webhook-Token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = int(payload["sub"])
    logger.info(f"Webhook called by user {user_id}")
    
    return {"status": "ok"}
```

---

## Common Patterns

### Pattern 1: Auto-Redirect on 401

Create an Axios interceptor to handle auth errors:

```typescript
// lib/api.ts
import axios from "axios";
import { useAuthStore } from "@/store/authStore";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth state
      useAuthStore.getState().logout();
      // Redirect to login
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);
```

### Pattern 2: Auth Loading State

Handle the initial auth check loading state:

```typescript
function App() {
  const { isLoading } = useAuthStore();
  
  if (isLoading) {
    return <LoadingScreen />;
  }
  
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          {/* Routes */}
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}
```

### Pattern 3: Optimistic Updates

Update UI before API confirms:

```typescript
const updateProfile = useUpdateProfile({
  onMutate: async (newData) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: authKeys.user() });
    
    // Snapshot previous value
    const previousUser = queryClient.getQueryData(authKeys.user());
    
    // Optimistically update
    queryClient.setQueryData(authKeys.user(), (old) => ({
      ...old,
      ...newData
    }));
    
    return { previousUser };
  },
  onError: (err, newData, context) => {
    // Rollback on error
    queryClient.setQueryData(authKeys.user(), context?.previousUser);
  },
});
```

### Pattern 4: Form Validation

Combine Zod with auth hooks:

```typescript
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

const loginSchema = z.object({
  username: z.string().min(3, "Username must be at least 3 characters"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

type LoginFormData = z.infer<typeof loginSchema>;

function LoginForm() {
  const login = useLogin();
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema)
  });

  return (
    <form onSubmit={handleSubmit((data) => login.mutate(data))}>
      <input {...register("username")} />
      {errors.username && <span>{errors.username.message}</span>}
      
      <input type="password" {...register("password")} />
      {errors.password && <span>{errors.password.message}</span>}
      
      <button type="submit">Login</button>
    </form>
  );
}
```

---

## Security Best Practices

### 1. Never Store Tokens in localStorage

The auth system uses HttpOnly cookies. Never extract and store the JWT in:
- localStorage
- sessionStorage
- React state
- Redux/Zustand

**Correct:**
```typescript
// Cookie is sent automatically
fetch('/api/v1/protected', { credentials: 'include' });
```

**Incorrect:**
```typescript
// Never do this
localStorage.setItem('token', jwt);
```

### 2. Always Use HTTPS in Production

```bash
# .env (production)
ENVIRONMENT=production
CORS_ORIGINS=https://app.yourdomain.com
```

In production, the `Secure` flag is automatically set on cookies.

### 3. Validate All Inputs

Always use Pydantic schemas on the backend:

```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
```

### 4. Use Generic Error Messages

Don't reveal whether a username or email exists:

```python
# Correct - generic message
raise HTTPException(
    status_code=401,
    detail="Incorrect username or password"  # Same message for both
)

# Incorrect - reveals information
raise HTTPException(status_code=401, detail="User not found")
```

### 5. Implement Rate Limiting

Rate limits are already implemented on auth endpoints. When adding new sensitive endpoints:

```python
from backend.api.v1.auth import check_rate_limit

@router.post("/sensitive-action")
async def sensitive_action(
    request: Request,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
):
    # Apply rate limiting
    check_rate_limit(request, max_requests=10, window_seconds=60)
    # ... rest of the endpoint
```

### 6. Use Parameterized Queries

Always use the repository pattern or SQLAlchemy ORM:

```python
# Correct - parameterized query
stmt = select(User).where(User.id == user_id)
result = await session.execute(stmt)

# Incorrect - vulnerable to SQL injection
result = await session.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

---

## Troubleshooting

### Issue: Cookie Not Being Set

**Symptoms:** Login succeeds but subsequent requests return 401.

**Check:**
1. Frontend and backend on same domain? (CORS issue)
2. `withCredentials: true` set in API client?
3. `CORS_ORIGINS` includes frontend URL?
4. `allow_credentials=True` in FastAPI CORS config?

**Debug:**
```typescript
// Check if cookie is being received
api.interceptors.response.use((response) => {
  console.log("Set-Cookie header:", response.headers["set-cookie"]);
  return response;
});
```

### Issue: 401 on Every Request

**Symptoms:** All authenticated requests return 401.

**Check:**
1. Cookie is being sent? (Check browser DevTools → Network → Request Headers)
2. Token is not expired? (Check cookie expiry)
3. User is active? (`is_active` flag in database)

**Debug:**
```python
# Add to endpoint for debugging
@router.get("/debug-auth")
async def debug_auth(request: Request):
    return {
        "cookies": request.cookies,
        "headers": dict(request.headers)
    }
```

### Issue: Rate Limit Errors

**Symptoms:** Getting 429 errors unexpectedly.

**Cause:** The rate limiter uses in-memory storage and resets on server restart. In development with auto-reload, this can cause issues.

**Solution:**
```bash
# Disable rate limiting in development (not for production)
# Or increase limits for testing
```

### Issue: CORS Errors

**Symptoms:** Browser blocks requests with CORS errors.

**Check:**
```python
# backend/core/config.py
CORS_ORIGINS="http://localhost:5173"  # No trailing slash!

# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,  # Required for cookies
)
```

### Issue: Password Validation Fails

**Symptoms:** Registration fails with validation error.

**Requirements:**
- Minimum 8 characters
- Maximum 255 characters
- No complexity requirements (you can add them)

**Custom Validation:**
```python
from pydantic import field_validator

class UserCreate(UserBase):
    password: str
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        return v
```

---

## Additional Resources

- [Auth Boilerplate Full Docs](../features/auth-boilerplate/docs-report.md)
- [API Reference](../api/README.md)
- [Security Rules](../../rules/security.md)
- [Backend Architecture](../../rules/backend_arch_design.md)
- [Frontend Architecture](../../rules/frontend_arch_design.md)
