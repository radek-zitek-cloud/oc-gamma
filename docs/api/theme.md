# Theme API Documentation

API endpoint documentation for theme preference management.

## Overview

The Theme API allows authenticated users to manage their theme preference (light, dark, or system). Theme preferences are persisted to the database and synchronized across devices on login.

## Base URL

```
/api/v1/auth/me/theme
```

## Authentication

All theme endpoints require authentication via HttpOnly JWT cookie. Include credentials with all requests:

```typescript
fetch('/api/v1/auth/me/theme', {
  credentials: 'include',  // Required for cookie transmission
  headers: {
    'X-Correlation-ID': correlationId,  // Recommended for tracing
  },
});
```

## Endpoints

### Update Theme Preference

Update the authenticated user's theme preference.

**Endpoint:** `PATCH /api/v1/auth/me/theme`

**Rate Limiting:** 10 requests per minute per IP address

#### Request

**Headers:**
| Header | Value | Required |
|--------|-------|----------|
| Content-Type | `application/json` | Yes |
| Cookie | `access_token=<jwt>` | Yes (automatic) |

**Request Body:**
```json
{
  "theme_preference": "dark"
}
```

**Valid Values:**
| Value | Description |
|-------|-------------|
| `light` | Always use light theme |
| `dark` | Always use dark theme |
| `system` | Follow operating system preference |

#### Response

**Success (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "theme_preference": "dark",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 401 | `NOT_AUTHENTICATED` | Missing or invalid authentication token |
| 422 | `VALIDATION_ERROR` | Invalid theme_preference value |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests (10/min limit) |

**Validation Error Example (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "theme_preference"],
      "msg": "unexpected value; permitted: 'light', 'dark', 'system'",
      "type": "value_error.const",
      "input": "invalid_theme"
    }
  ]
}
```

**Rate Limit Error Example (429):**
```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

## Schemas

### ThemePreference

Type definition for valid theme values.

```python
ThemePreference = Literal["light", "dark", "system"]
```

### ThemePreferenceUpdate (Request)

```python
class ThemePreferenceUpdate(BaseModel):
    theme_preference: ThemePreference
```

**Validation Rules:**
- Required field
- Must be one of: `"light"`, `"dark"`, `"system"`
- Unknown fields are rejected (Pydantic `extra="forbid"`)

### UserResponse (Response)

The user object returned includes the current theme preference:

```python
class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    theme_preference: ThemePreference  # <-- Included in response
    created_at: datetime
```

## Rate Limiting

The theme update endpoint is rate-limited to prevent abuse:

| Limit | Window | Scope |
|-------|--------|-------|
| 10 requests | 60 seconds | Per IP address |

When the rate limit is exceeded:
- HTTP 429 status code is returned
- Response includes `Retry-After` header (when applicable)
- Rate limit counter resets after the window expires

## Integration Examples

### React with TanStack Query

```typescript
// hooks/useTheme.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { logger } from '@/lib/logger';
import type { ThemePreference, User } from '@/types';

export function useUpdateThemePreference() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (theme: ThemePreference): Promise<User> => {
      const response = await api.patch('/api/v1/auth/me/theme', {
        theme_preference: theme,
      });
      return response.data;
    },
    onSuccess: (data) => {
      // Update cached user data
      queryClient.setQueryData(['currentUser'], data);
      logger.info('Theme preference saved to server', { 
        theme: data.theme_preference 
      });
    },
    onError: (error) => {
      logger.error('Failed to save theme preference', { error });
    },
  });
}
```

### cURL Example

```bash
# Update theme to dark
curl -X PATCH http://localhost:8000/api/v1/auth/me/theme \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=<your-jwt-token>" \
  -H "X-Correlation-ID: $(uuidgen)" \
  -d '{"theme_preference": "dark"}'
```

### Python (httpx)

```python
import httpx

async def update_theme(client: httpx.AsyncClient, theme: str) -> dict:
    response = await client.patch(
        "/api/v1/auth/me/theme",
        json={"theme_preference": theme},
    )
    response.raise_for_status()
    return response.json()
```

## Error Handling Best Practices

1. **Always handle 401 errors:** Redirect to login page
2. **Handle 422 errors:** Show validation message to user
3. **Handle 429 errors:** Display cooldown message, disable rapid toggling
4. **Network failures:** Implement retry with exponential backoff

```typescript
try {
  await updateTheme(theme);
} catch (error) {
  if (error.response?.status === 429) {
    toast.error('Please wait before changing theme again');
  } else if (error.response?.status === 401) {
    redirectToLogin();
  } else {
    toast.error('Failed to save theme preference');
  }
}
```

## Related Documentation

- [Theme Switching User Guide](../guides/theme-switching.md)
- [Theme Development Guide](../guides/theme-development.md)
- [Authentication API](auth.md)
- [Frontend Architecture](../../rules/frontend_arch_design.md)

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-24 | Initial API documentation |
