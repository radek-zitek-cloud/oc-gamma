# Documentation Report: Split Profile and Password Pages

## Feature Overview

The **Split Profile and Password Pages** feature refactors the user account management experience by separating profile editing and password changing into two distinct, focused pages. This improves user experience by reducing cognitive load and enables better organization of security-related settings.

### Key Components

1. **Profile Page** (`/profile`) - Edit user profile information (email, full name)
2. **Password Page** (`/password`) - Change password with confirmation validation
3. **Toast Notification System** - Real-time feedback for user actions
4. **Enhanced Validation** - Dual-layer validation (frontend + backend)

### What This Feature Does

- Separates profile management from password management into two distinct pages
- Implements a reusable toast notification system with 4 types (success, error, warning, info)
- Adds password confirmation validation with matching checks
- Provides real-time feedback for all user actions via toast notifications
- Implements rate limiting on password change endpoint (3 attempts per minute)
- Maintains consistent navigation patterns (back/cancel buttons return to dashboard)

---

## User Guide

### Accessing the Profile Page

1. Log in to the application
2. Click your username in the header or navigate to `/profile`
3. The Profile page displays two sections:
   - **Edit Profile** - Update your email and full name
   - **Security** - Navigate to password change

### Updating Your Profile

1. Navigate to `/profile`
2. Edit your **Email** and/or **Full Name** in the form fields
3. Click **Save Changes**
4. A success toast notification will appear confirming the update

### Changing Your Password

1. Navigate to `/profile` and click **Change Password** in the Security card
   - Or navigate directly to `/password`
2. Enter your **Current Password**
3. Enter your **New Password** (minimum 8 characters)
4. Enter the same password in **Confirm New Password**
5. Click **Change Password**
6. A success toast notification will appear confirming the change

**Navigation Options:**
- **Back Button** (arrow icon) - Returns to the dashboard
- **Cancel Button** - Returns to the dashboard without saving

### Understanding Toast Notifications

Toast notifications appear in the top-right corner and automatically dismiss after 5 seconds:

| Type | Color | Use Case |
|------|-------|----------|
| **Success** | Green | Operation completed successfully |
| **Error** | Red | Operation failed |
| **Warning** | Amber | Non-critical issue or partial success |
| **Info** | Blue | General information |

**Toast Actions:**
- Click the X button to dismiss manually
- Hover to pause auto-dismiss
- Multiple toasts stack vertically

---

## API Documentation

### Change Password Endpoint

**Endpoint:** `PUT /api/v1/auth/me/password`

**Authentication:** Required (HttpOnly JWT Cookie)

**Rate Limiting:** 3 attempts per minute per IP address

#### Request Body

```json
{
  "current_password": "string (required)",
  "new_password": "string (required, min 8, max 255)",
  "confirm_password": "string (required, min 8, max 255)"
}
```

#### Response

**Success (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Validation Error (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "confirm_password"],
      "msg": "Passwords do not match",
      "type": "value_error"
    }
  ]
}
```

**Authentication Error (401 Unauthorized):**
```json
{
  "detail": "Not authenticated"
}
```

**Current Password Incorrect (400 Bad Request):**
```json
{
  "detail": "Incorrect current password"
}
```

**Rate Limit Exceeded (429 Too Many Requests):**
```json
{
  "detail": "Too many requests"
}
```

### Update Profile Endpoint

**Endpoint:** `PUT /api/v1/auth/me`

**Authentication:** Required

#### Request Body

```json
{
  "email": "user@example.com (optional)",
  "full_name": "John Doe (optional)"
}
```

#### Response

**Success (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "role": "user",
  "theme_preference": "system"
}
```

---

## Architecture Notes

### Frontend Architecture

#### State Management

The feature follows the project's frontend architecture patterns:

- **Zustand** for client-side state (notification store)
- **TanStack Query** for server state (auth mutations)
- **No useEffect for data fetching** - all server interactions use mutations

#### Toast Notification System

```
User Action → TanStack Query Mutation → API Call
    ↓
On Success/Error → notificationStore.addToast()
    ↓
Toaster component renders → Auto-dismiss after 5s
```

**Key Design Decisions:**
1. **CSS Transitions over framer-motion** - Avoided adding new dependencies
2. **Zustand for toast state** - Simple, predictable state management
3. **Auto-dismiss with manual override** - Users can dismiss early
4. **Fixed position top-right** - Non-intrusive, follows common patterns

#### Component Hierarchy

```
App.tsx
├── ProtectedRoute
│   └── AppShell
│       └── Profile.tsx or ChangePassword.tsx
│
Toaster (fixed position, global)
├── Toast (individual notification)
```

### Backend Architecture

#### Pydantic V2 Validation

The `PasswordChange` schema uses Pydantic V2's `field_validator` with `mode="after"` for cross-field validation:

```python
@field_validator("confirm_password", mode="after")
@classmethod
def check_passwords_match(cls, v: str, info) -> str:
    """Validate that confirm_password matches new_password."""
    data = info.data
    if "new_password" in data and v != data["new_password"]:
        raise ValueError("Passwords do not match")
    return v
```

**Validation Strategy:**
- Individual field validation runs first (min_length, max_length)
- Cross-field validator runs after individual validation
- Error messages are included in the 422 response

#### Rate Limiting

Password change endpoint implements IP-based rate limiting:

```python
check_rate_limit(request, max_requests=3, window_seconds=60, endpoint="password_change")
```

This prevents brute-force attacks on the current password field.

### Security Design Patterns

1. **Dual-Layer Validation** - Frontend provides UX feedback, backend enforces rules
2. **Rate Limiting** - Prevents brute-force attacks
3. **IDOR Prevention** - Uses `current_user` dependency to ensure users can only modify their own data
4. **No Password Logging** - Passwords are never logged (structured logging excludes sensitive fields)
5. **HttpOnly Cookies** - JWT tokens stored in HttpOnly cookies, not localStorage

---

## Configuration

### Frontend Configuration

No environment variables required for this feature. The toast system uses default values:

| Setting | Default | Description |
|---------|---------|-------------|
| `duration` | 5000ms | Default toast display time |
| `position` | top-right | Toast container position |

### Backend Configuration

Rate limiting is configured in the endpoint directly:

```python
check_rate_limit(request, max_requests=3, window_seconds=60, endpoint="password_change")
```

To modify rate limits, update the `change_password` function in `src/backend/api/v1/auth.py`.

### Password Validation Rules

| Rule | Value | Enforced By |
|------|-------|-------------|
| Minimum length | 8 characters | Frontend + Backend |
| Maximum length | 255 characters | Backend (Pydantic) |
| Confirmation match | Required | Frontend + Backend |

---

## Testing

### Test Coverage Summary

| Component | Tests | Status |
|-----------|-------|--------|
| `notificationStore.ts` | 6 | ✅ Passing |
| `useToast.ts` | 6 | ✅ Passing |
| `Profile.tsx` | 7 | ✅ Passing |
| `ChangePassword.tsx` | 7 | ✅ Passing |
| `test_auth_api.py` | 17 | ✅ Passing |
| **Total** | **43** | ✅ **All Passing** |

### Frontend Tests

**Notification Store Tests** (`src/frontend/src/store/notificationStore.test.ts`):
- Adding notifications
- Removing notifications by ID
- Auto-removal after duration
- Clearing all notifications

**Toast Hook Tests** (`src/frontend/src/hooks/useToast.test.ts`):
- Success toast display
- Error toast display
- Warning toast display
- Info toast display
- Custom duration override

**Profile Page Tests** (`src/frontend/src/pages/Profile.test.tsx`):
- Form rendering
- User data display
- Loading state
- Form field updates
- Form submission
- Button disabled state during submission
- Security card and navigation link

**Change Password Tests** (`src/frontend/src/pages/ChangePassword.test.tsx`):
- Form rendering
- Password mismatch validation
- Password length validation
- Form submission with valid data
- Form clearing on success
- Password visibility toggle
- Cancel navigation

### Backend Tests

**Password Change API Tests** (`tests/backend/test_auth_api.py`):
- Successful password change
- Password confirmation mismatch (422)
- Incorrect current password (400)
- Rate limiting (429 after 3 attempts)
- Unauthenticated access (401)

### Running Tests

```bash
# Frontend tests
npm test -- --run

# Backend tests
pytest tests/backend/test_auth_api.py -v
```

### E2E Tests

E2E tests are out of scope for this feature but the implementation includes all necessary `data-testid` attributes for Playwright testing.

---

## Known Limitations

### Current Limitations

1. **No Password Strength Meter** - The password change form validates minimum length but doesn't show a visual strength indicator
2. **No Password History** - Users can reuse their previous passwords; no history check is implemented
3. **No Email Confirmation** - Password changes don't trigger confirmation emails
4. **Fixed Toast Duration** - Toast auto-dismiss time is fixed at 5 seconds (can be overridden per-toast)

### Security Recommendations

Per the security review, the following improvements are recommended for production hardening:

1. **Rate Limiting** - ✅ Implemented (3 attempts per minute)
2. **SECRET_KEY Validation** - Consider adding startup check for production deployments
3. **Max Length on Current Password** - Could add `max_length=255` for consistency

### Future Enhancements

Potential improvements for future iterations:

1. Add password strength meter with visual feedback
2. Implement password history to prevent reuse
3. Add email confirmation for password changes
4. Support for 2FA/MFA during password change
5. Session invalidation on password change (force re-login on other devices)
6. Configurable toast positions (user preference)
7. Toast action buttons (e.g., "Undo" for destructive actions)

---

## Files Changed

### Frontend - Modified
- `src/frontend/src/App.tsx` - Added `/password` route and Toaster component
- `src/frontend/src/hooks/useAuth.ts` - Added toast notifications to all mutations
- `src/frontend/src/types/user.ts` - Updated `PasswordChange` interface

### Frontend - Created
- `src/frontend/src/types/notification.ts` - Notification type definitions
- `src/frontend/src/pages/Profile.tsx` - Refactored profile-only page
- `src/frontend/src/pages/ChangePassword.tsx` - New password change page
- `src/frontend/src/store/notificationStore.ts` - Zustand toast store
- `src/frontend/src/components/ui/toast.tsx` - Toast component
- `src/frontend/src/components/ui/toaster.tsx` - Toast container
- `src/frontend/src/components/ui/alert.tsx` - Alert component for validation errors
- `src/frontend/src/hooks/useToast.ts` - Toast convenience hook

### Frontend - Tests Created
- `src/frontend/src/pages/Profile.test.tsx` - Profile page tests
- `src/frontend/src/pages/ChangePassword.test.tsx` - Password page tests
- `src/frontend/src/store/notificationStore.test.ts` - Store tests
- `src/frontend/src/hooks/useToast.test.ts` - Hook tests

### Backend - Modified
- `src/backend/schemas/user.py` - Updated `PasswordChange` schema with confirmation
- `src/backend/api/v1/auth.py` - Added rate limiting to password change endpoint

### Backend - Tests Updated
- `tests/backend/test_auth_api.py` - Added password confirmation tests

---

## Related Documentation

- [Feature Plan](./plan.md) - Original implementation plan
- [Code Review Report](./code-review.md) - Code quality assessment
- [Security Review Report](./security-review.md) - Security audit findings
- [Status](./STATUS.md) - Feature state tracking

## Project Rules Compliance

This implementation follows all project rules:

- ✅ `@rules/frontend_arch_design.md` - TanStack Query, Zustand, shadcn/ui
- ✅ `@rules/backend_arch_design.md` - Pydantic V2, async/await, repository pattern
- ✅ `@rules/security.md` - HttpOnly cookies, bcrypt, rate limiting
- ✅ `@rules/development_testing.md` - TDD, Vitest, pytest, data-testid

---

*Documentation generated: 2026-02-24*
*Feature version: Backend 0.3.0, Frontend 0.2.0*
