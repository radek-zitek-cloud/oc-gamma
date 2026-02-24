# Security Review: Theme Switching Feature

## Executive Summary

**Overall Security Posture:** SECURE

**Total Findings:** 2 (Critical: 0, High: 0, Medium: 1, Low: 1)

**Project Rule Violations:** 0

**Verdict:** PASS with minor recommendations

The theme switching feature implementation demonstrates strong security practices with proper authentication, authorization, input validation, and secure data handling. The code follows project security rules comprehensively with no violations. The two findings are minor improvements that enhance defense-in-depth but do not represent exploitable vulnerabilities.

---

## Project Rule Compliance ✅

| Rule | Status | Location | Notes |
|------|--------|----------|-------|
| HttpOnly JWT cookies | ✅ PASS | `auth.py:185-192` | Proper `HttpOnly=True`, `Secure` (conditional), `SameSite="lax"` |
| No localStorage for tokens | ✅ PASS | All files | Uses HttpOnly cookies exclusively |
| bcrypt only (no passlib) | ✅ PASS | `security.py:26-27` | Uses `bcrypt.hashpw` and `bcrypt.checkpw` |
| CORS - no `allow_origins=["*"]` | ✅ PASS | `main.py:78` | Uses `settings.cors_origins_list` from environment |
| CORS - `allow_credentials=True` | ✅ PASS | `main.py:79` | Properly configured for HttpOnly cookies |
| RBAC enforcement | ✅ PASS | `auth.py:327` | Uses `Depends(get_current_user)` |
| IDOR prevention | ✅ PASS | `auth.py:327-342` | Users can only update their own theme |
| Rate limiting (auth routes) | ✅ PASS | `auth.py:128,169` | Custom rate limiter on login/register |
| Parameterized queries | ✅ PASS | `repositories/base.py:30-55` | SQLAlchemy ORM only |
| Input validation | ✅ PASS | `schemas/user.py:39-42` | Pydantic V2 with `ThemePreference` Literal |
| No XSS (dangerouslySetInnerHTML) | ✅ PASS | All files | No occurrences found |
| No hardcoded secrets | ✅ PASS | All files | Config loaded from environment |
| No secrets in logs | ✅ PASS | `logging.py:22-43` | Structured JSON logging, no secret exposure |
| Container non-root user | N/A | - | Dockerfile not in scope |
| Frontend `credentials: 'include'` | ✅ PASS | `api.ts:17` | `withCredentials: true` configured |
| Frontend `X-Correlation-ID` | ✅ PASS | `api.ts:24` | Header added to all requests |
| No bare `console.log` | ✅ PASS | `logger.ts` | Centralized logger used throughout |

---

## OWASP Top 10 Analysis

### A01: Broken Access Control
**Status:** SECURE

The theme update endpoint (`PATCH /api/v1/auth/me/theme`) properly enforces authentication and authorization:
- Uses `Depends(get_current_user)` to ensure only authenticated users can access
- The user object from the dependency is used directly for the update, preventing IDOR attacks
- Users can only modify their own theme preference

**Evidence:**
```python
# auth.py:325-329
async def update_theme_preference(
    theme_data: ThemePreferenceUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],  # Auth enforced
    repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> UserResponse:
```

### A02: Cryptographic Failures
**Status:** SECURE

- JWT tokens use HS256 with configurable secret key
- Password hashing uses bcrypt exclusively
- HttpOnly cookies prevent XSS from stealing tokens
- Secure flag on cookies in production

### A03: Injection
**Status:** SECURE

- SQL Injection: Mitigated through SQLAlchemy 2.0 ORM with parameterized queries
- NoSQL Injection: N/A (PostgreSQL/SQLite only)
- Command Injection: N/A (no shell execution)
- LDAP Injection: N/A (no LDAP integration)

**Evidence:**
```python
# repositories/base.py:30-33
result = await self.session.execute(
    select(self.model_class).where(self.model_class.id == id)
)
```

### A04: Insecure Design
**Status:** SECURE

- Repository pattern properly abstracts data access
- Clear separation between schemas and models
- Pydantic validation prevents malformed input

### A05: Security Misconfiguration
**Status:** SECURE

- CORS origins loaded from environment variables
- No debug mode exposed in production
- Proper error handling without information leakage

### A06: Vulnerable and Outdated Components
**Status:** NOT ASSESSED

Dependency vulnerability scanning not in scope of this review. Recommend periodic `pip audit` and `npm audit` runs.

### A07: Identification and Authentication Failures
**Status:** SECURE

- Proper session management via HttpOnly cookies
- Rate limiting on authentication endpoints
- No session fixation vulnerabilities (new token on login)

### A08: Software and Data Integrity Failures
**Status:** SECURE

- Theme preference validated against allowed values only
- No deserialization of untrusted data
- SQLAlchemy ORM prevents direct data manipulation

### A09: Security Logging and Monitoring Failures
**Status:** SECURE

- Structured JSON logging with correlation IDs
- Security events logged (theme updates, auth events)
- No sensitive data in logs

### A10: Server-Side Request Forgery (SSRF)
**Status:** N/A

No server-side requests to external URLs based on user input.

---

## Findings

### [MEDIUM] Missing Rate Limiting on Theme Update Endpoint

**OWASP Category:** A07 - Identification and Authentication Failures (CWE-770)

**Location:** `src/backend/api/v1/auth.py:320-348`

**Description:**
The `PATCH /api/v1/auth/me/theme` endpoint does not implement rate limiting. While theme updates are relatively low-risk, an attacker with valid credentials could potentially:
1. Automate rapid theme changes to generate excessive database writes
2. Pollute audit logs with noise
3. Contribute to resource exhaustion in a broader DoS attack

**Exploitation Scenario:**
An attacker with a valid session token could script rapid theme updates:
```bash
while true; do
  curl -X PATCH /api/v1/auth/me/theme \
    -H "Cookie: access_token=<token>" \
    -d '{"theme_preference": "dark"}'
  curl -X PATCH /api/v1/auth/me/theme \
    -H "Cookie: access_token=<token>" \
    -d '{"theme_preference": "light"}'
done
```

This would generate continuous database writes and log entries.

**Remediation:**
Add rate limiting to the theme endpoint using the existing rate limiter infrastructure:

```python
@router.patch("/me/theme", response_model=UserResponse)
async def update_theme_preference(
    theme_data: ThemePreferenceUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    repo: Annotated[UserRepository, Depends(get_user_repo)],
    request: Request,  # Add this parameter
) -> UserResponse:
    # Rate limit: 10 theme changes per minute per user
    check_rate_limit(
        request, 
        max_requests=10, 
        window_seconds=60
    )
    # ... rest of function
```

Alternatively, apply the slowapi limiter decorator:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

@router.patch("/me/theme", response_model=UserResponse)
@limiter.limit("10/minute")
async def update_theme_preference(...)
```

---

### [LOW] localStorage Theme Preference Could Be Manipulated

**OWASP Category:** A04 - Insecure Design (CWE-602)

**Location:** `src/frontend/src/store/themeStore.ts:34-42, 85-88`

**Description:**
The theme preference is stored in localStorage for caching purposes. While this is acceptable for non-sensitive UI state, the implementation reads from localStorage and trusts the value without additional validation:

```typescript
function getInitialTheme(): ThemePreference {
  if (typeof window === "undefined") return "system";
  
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "light" || stored === "dark" || stored === "system") {
    return stored;
  }
  return "system";
}
```

An attacker with XSS (in a different part of the application) could manipulate the theme preference in localStorage. While this is a low-impact issue (only affects UI appearance), it could be used for:
1. UI redressing attacks
2. Social engineering (making the app look different)
3. Cache poisoning if theme affects content loading

**Exploitation Scenario:**
If an XSS vulnerability exists elsewhere in the application:
```javascript
// Attacker injects malicious theme value
localStorage.setItem('theme-preference', '<img src=x onerror=alert(1)>');
```

However, the current code validates against allowed values, so this would fall back to "system".

**Remediation:**
The current implementation already has validation, which is good. Consider also syncing from server on mount to ensure consistency:

```typescript
// In themeStore.ts initializeTheme function
// Always prefer server value if authenticated
const serverTheme = authStore.getState().user?.theme_preference;
if (serverTheme) {
  theme = serverTheme;
} else {
  theme = getInitialTheme();
}
```

This ensures that even if localStorage is manipulated, the server value takes precedence for authenticated users.

---

## Positive Security Practices ✅

### 1. Proper Input Validation
The `ThemePreferenceUpdate` schema uses Pydantic V2 with a `Literal` type to restrict values:
```python
ThemePreference = Literal["light", "dark", "system"]

class ThemePreferenceUpdate(BaseModel):
    theme_preference: ThemePreference
```
This prevents injection of invalid or malicious values.

### 2. Secure Authentication Flow
- JWT tokens stored in HttpOnly cookies (not localStorage)
- `SameSite="lax"` prevents CSRF in most scenarios
- `Secure` flag in production ensures HTTPS-only transmission

### 3. No Information Disclosure
Error responses do not leak internal implementation details:
```python
# Returns generic message, not database errors
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
)
```

### 4. Proper Authorization
The theme endpoint correctly uses dependency injection to ensure users can only modify their own data:
```python
current_user: Annotated[UserResponse, Depends(get_current_user)]
```

### 5. Structured Logging
All security-relevant events are logged with correlation IDs for audit trails:
```python
logger.info(
    f"Theme preference updated: {theme_data.theme_preference}",
    {"user_id": updated.id}
)
```

### 6. No XSS Vectors
- No use of `dangerouslySetInnerHTML`
- Theme values are used only for CSS class manipulation
- Proper escaping via React's built-in protections

### 7. Safe DOM Manipulation
Theme changes use safe `classList` API:
```typescript
if (theme === "dark") {
  root.classList.add("dark");
} else {
  root.classList.remove("dark");
}
```

### 8. Repository Pattern
Data access is properly abstracted, preventing direct SQL injection risks and ensuring consistent security controls.

---

## Remediation Checklist

- [ ] **Add rate limiting to theme endpoint** — `src/backend/api/v1/auth.py:320-348` — MEDIUM
  - Consider 10 requests per minute limit per user
  - Use existing `check_rate_limit` function or slowapi decorator

- [ ] **Prioritize server theme value over localStorage** — `src/frontend/src/store/themeStore.ts:124-157` — LOW
  - For authenticated users, use `user.theme_preference` from auth store
  - Fallback to localStorage only for unauthenticated users

---

## Verdict

**PASS**

The theme switching feature implementation is **secure** and ready for production deployment. The code follows all project security rules and OWASP guidelines. The two identified findings are defense-in-depth improvements rather than exploitable vulnerabilities.

### Risk Summary

| Risk | Level | Justification |
|------|-------|---------------|
| Authentication Bypass | None | Proper JWT validation with HttpOnly cookies |
| Authorization Bypass | None | Correct use of dependency injection |
| Data Injection | None | Pydantic validation and SQLAlchemy ORM |
| XSS | None | No dangerous HTML rendering |
| Information Disclosure | None | Proper error handling |
| DoS via Theme Updates | Low | No rate limiting, but impact is minimal |

### Recommendations

1. **Immediate (Pre-deployment):** None required
2. **Short-term:** Add rate limiting to theme endpoint for defense-in-depth
3. **Long-term:** Consider periodic security audits of dependencies

---

*Security Review conducted by: security-reviewer*  
*Date: 2026-02-24*  
*Files Reviewed: 16*  
*Rules Checked: 17*  
*Findings: 2 (0 Critical, 0 High, 1 Medium, 1 Low)*
