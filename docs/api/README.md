# API Documentation

## Overview

The OC Gamma API is a RESTful API built with FastAPI, providing authentication and user management functionality. The API uses JWT tokens stored in HttpOnly cookies for authentication.

**Base URL:** `http://localhost:8000/api/v1`

## Authentication

The API uses JWT-based authentication with HttpOnly cookies. The authentication flow is:

1. **Register** - Create a new account with `POST /auth/register`
2. **Login** - Authenticate with `POST /auth/login` to receive a cookie
3. **Access Protected Endpoints** - Send the cookie with each request
4. **Logout** - Clear the cookie with `POST /auth/logout`

### Cookie Details

| Attribute | Value | Description |
|-----------|-------|-------------|
| Name | `access_token` | JWT token |
| HttpOnly | `true` | Prevents JavaScript access |
| Secure | `true` (production) | HTTPS only in production |
| SameSite | `lax` | CSRF protection |
| Max-Age | 1800 seconds | 30 minute expiration |

### Making Authenticated Requests

Include credentials with every request:

```bash
# curl
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Content-Type: application/json" \
  -b "access_token=YOUR_JWT_TOKEN"

# JavaScript/TypeScript
fetch('/api/v1/auth/me', {
  credentials: 'include'  // Sends cookies
});
```

## Endpoints

### Authentication

#### POST /auth/register

Register a new user account.

**Request Body:**
```json
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

**Errors:**
- `409 Conflict` - Email or username already exists
- `422 Unprocessable Entity` - Invalid input
- `429 Too Many Requests` - Rate limit exceeded (3/min)

---

#### POST /auth/login

Authenticate and receive JWT cookie.

**Request Body:** (form-urlencoded)
```
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

**Errors:**
- `401 Unauthorized` - Invalid credentials
- `429 Too Many Requests` - Rate limit exceeded (5/min)

---

#### POST /auth/logout

Clear authentication cookie.

**Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

---

#### GET /auth/me

Get current authenticated user's profile.

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

**Errors:**
- `401 Unauthorized` - Not authenticated

---

#### PUT /auth/me

Update current user's profile.

**Request Body:**
```json
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

**Request Body:**
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Errors:**
- `400 Bad Request` - Current password is incorrect

## Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Human-readable error message"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request (e.g., wrong password) |
| 401 | Unauthorized | Authentication required or invalid |
| 403 | Forbidden | Permission denied |
| 409 | Conflict | Resource conflict (e.g., duplicate email) |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

## Rate Limiting

Rate limits are applied per IP address:

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /auth/register | 3 requests | 60 seconds |
| POST /auth/login | 5 requests | 60 seconds |

When rate limit is exceeded:

```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

## Interactive API Documentation

FastAPI automatically generates interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Use these interfaces to explore and test the API interactively.

## Data Models

### User

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| email | string | Email address (unique) |
| username | string | Username (unique) |
| full_name | string | Display name (optional) |
| is_active | boolean | Account status |
| role | string | "USER" or "ADMIN" |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

### Token

| Field | Type | Description |
|-------|------|-------------|
| access_token | string | JWT token |
| token_type | string | Always "bearer" |

## CORS

The API supports CORS for configured origins. Ensure your frontend origin is listed in the `CORS_ORIGINS` environment variable.

Default development origins:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:4173` (Vite preview)

## Additional Resources

- [Authentication Boilerplate Documentation](../features/auth-boilerplate/docs-report.md)
- [Authentication Developer Guide](../guides/authentication.md)
- [Security Review](../features/auth-boilerplate/security-review.md)
