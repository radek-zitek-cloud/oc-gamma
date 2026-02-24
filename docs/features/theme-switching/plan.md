# Theme Switching Feature Implementation Plan

## Overview
Implement a comprehensive theme switching system that allows users to toggle between light and dark modes, follow system preferences, and persist their choice in the database. The backend User model already has a `theme_preference` field (default: "system"), so we need to expose it via API and implement the frontend theme management.

## Feature Requirements

### Functional Requirements
1. **Theme Modes**: Support three modes - `light`, `dark`, `system`
2. **System Preference**: When set to `system`, automatically follow OS-level theme preference
3. **Persistence**: Store user's theme preference in the database and restore on login
4. **UI Toggle**: Add a dropdown or button in the Header to switch themes
5. **Visual Feedback**: Real-time theme switching without page reload

### Technical Constraints
- Use Tailwind CSS dark mode (`.dark` class on `<html>`)
- Store theme in database as `light`, `dark`, or `system`
- Use Zustand for client-side theme state
- Follow repository pattern for backend
- Support SSR-safe theme detection

---

## Implementation Tasks

### Phase 1: Backend API (Priority: High)

#### 1.1 Update User Schemas
**File**: `src/backend/schemas/user.py`

**Changes**:
- Add `theme_preference` field to `UserResponse` schema
- Create `ThemePreferenceUpdate` schema for PATCH requests
- Validate theme values are one of: `light`, `dark`, `system`

**Rationale**: The User model already has the field; we need to expose it in API responses and allow updates.

#### 1.2 Add Theme Update Endpoint
**File**: `src/backend/api/v1/auth.py`

**Add Endpoint**:
```python
@router.patch("/me/theme", response_model=UserResponse)
async def update_theme_preference(
    theme_data: ThemePreferenceUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> UserResponse:
    """Update user's theme preference."""
    updated = await repo.update_user(current_user, {"theme_preference": theme_data.theme_preference})
    logger.info(f"Theme preference updated: {theme_data.theme_preference}", {"user_id": current_user.id})
    return UserResponse.model_validate(updated)
```

**Rationale**: Separate endpoint for theme updates keeps concerns clean and allows for future theme-related logic.

#### 1.3 Repository Method (if needed)
**File**: `src/backend/repositories/user.py`

The existing `update_user` method should work, but verify it handles partial updates correctly.

---

### Phase 2: Frontend State Management (Priority: High)

#### 2.1 Create Theme Store
**File**: `src/frontend/src/store/themeStore.ts` (new)

**Implementation**:
```typescript
interface ThemeState {
  theme: 'light' | 'dark' | 'system';
  resolvedTheme: 'light' | 'dark'; // Computed actual theme
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  initializeTheme: () => void;
}

// Store handles:
// 1. Persisting to localStorage for immediate UI
// 2. Syncing with system preference when theme='system'
// 3. Applying/removing .dark class on document.documentElement
```

**Rationale**: Zustand store manages theme state globally and handles the complex logic of system preference detection.

#### 2.2 Create Theme Provider/Hydration
**File**: `src/frontend/src/components/ThemeProvider.tsx` (new)

**Implementation**:
- Component that initializes theme on mount
- Watches for system preference changes via `matchMedia`
- Applies/removes `.dark` class on `<html>` element
- Syncs with user's saved preference from API on login

**Rationale**: Provider component handles side effects (DOM manipulation, event listeners) separately from store logic.

---

### Phase 3: UI Components (Priority: High)

#### 3.1 Theme Toggle Component
**File**: `src/frontend/src/components/ThemeToggle.tsx` (new)

**Implementation**:
- Dropdown menu with three options: Light, Dark, System
- Shows checkmark next to current selection
- Uses Sun, Moon, and Monitor icons from lucide-react
- Accessible (ARIA labels, keyboard navigation)

**Placement**: In Header component (next to user menu)

#### 3.2 Update Header Component
**File**: `src/frontend/src/components/layout/Header.tsx`

**Changes**:
- Import and add `<ThemeToggle />` component
- Place between app title and user menu (or in user menu)

---

### Phase 4: API Integration (Priority: Medium)

#### 4.1 Update User Types
**File**: `src/frontend/src/types/user.ts`

**Changes**:
- Add `theme_preference` to `User` interface
- Add `ThemePreference` type: `'light' | 'dark' | 'system'`

#### 4.2 Create Theme API Hook
**File**: `src/frontend/src/hooks/useTheme.ts` (new)

**Implementation**:
```typescript
export function useUpdateThemePreference() {
  return useMutation({
    mutationFn: async (theme: ThemePreference): Promise<User> => {
      const response = await api.patch("/api/v1/auth/me/theme", { theme_preference: theme });
      return response.data;
    },
    onSuccess: (data) => {
      // Update auth store with new user data
      useAuthStore.getState().setUser(data);
      logger.info("Theme preference saved", { theme: data.theme_preference });
    },
  });
}
```

#### 4.3 Sync Theme on Auth
**File**: `src/frontend/src/hooks/useAuth.ts`

**Changes**:
- In `useCurrentUser` hook, when user data is received, sync theme_preference to theme store
- Call `themeStore.setTheme(user.theme_preference)` on successful auth

---

### Phase 5: App Integration (Priority: Medium)

#### 5.1 Update App Entry Point
**File**: `src/frontend/src/App.tsx`

**Changes**:
- Wrap app with `<ThemeProvider />`
- Import and add ThemeProvider as a wrapper component

**Rationale**: Ensures theme is initialized before any UI renders to prevent flash of wrong theme.

#### 5.2 Update globals.css (verify)
**File**: `src/frontend/src/globals.css`

**Current Status**: Dark theme CSS variables already defined ✓

**Verify**: Ensure `.dark` class selector works correctly with Tailwind

---

### Phase 6: Testing (Priority: Medium)

#### 6.1 Backend Tests
**Files**: `tests/backend/test_theme.py` (new)

**Test Cases**:
1. GET /me returns theme_preference
2. PATCH /me/theme updates preference
3. Invalid theme value returns 422
4. Unauthenticated request returns 401

#### 6.2 Frontend Tests
**Files**: `tests/frontend/ThemeToggle.test.tsx` (new)

**Test Cases**:
1. ThemeToggle renders correctly
2. Clicking option updates theme
3. System preference detection works
4. Theme persists after refresh

#### 6.3 E2E Tests
**Files**: `tests/e2e/theme.spec.ts` (new)

**Test Cases**:
1. User can switch themes
2. Theme persists across sessions
3. System preference is respected
4. Visual appearance changes correctly

---

## File Summary

### New Files
1. `src/backend/schemas/theme.py` - Theme-related schemas
2. `src/frontend/src/store/themeStore.ts` - Theme state management
3. `src/frontend/src/components/ThemeProvider.tsx` - Theme initialization
4. `src/frontend/src/components/ThemeToggle.tsx` - Theme UI component
5. `src/frontend/src/hooks/useTheme.ts` - Theme API hooks
6. `src/frontend/src/types/theme.ts` - Theme type definitions
7. `tests/backend/test_theme.py` - Backend tests
8. `tests/frontend/ThemeToggle.test.tsx` - Frontend tests
9. `tests/e2e/theme.spec.ts` - E2E tests

### Modified Files
1. `src/backend/schemas/user.py` - Add theme_preference to schemas
2. `src/backend/api/v1/auth.py` - Add theme update endpoint
3. `src/frontend/src/types/user.ts` - Add theme_preference to User
4. `src/frontend/src/store/authStore.ts` - Sync theme on login
5. `src/frontend/src/hooks/useAuth.ts` - Initialize theme from user data
6. `src/frontend/src/components/layout/Header.tsx` - Add ThemeToggle
7. `src/frontend/src/App.tsx` - Add ThemeProvider

---

## Success Criteria

1. **Functional**: User can switch between light/dark/system modes
2. **Persistence**: Theme choice is saved to database and restored on login
3. **System Preference**: When set to "system", UI matches OS theme
4. **Performance**: No layout shift or flash of wrong theme on load
5. **Accessibility**: Theme toggle is keyboard accessible and has ARIA labels
6. **Testing**: All test suites pass (>80% coverage)

---

## Open Questions

1. **Q**: Should theme apply to login/register pages or only after auth?  
   **A**: Apply globally - use localStorage before auth, sync with DB after login.

2. **Q**: What happens if user changes system theme while app is open?  
   **A**: App should reactively update when theme is set to "system".

3. **Q**: Should we support server-side rendering (SSR) for theme?  
   **A**: Not required for MVP; implement client-side only using localStorage.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Flash of unstyled theme (FOUC) | Medium | Medium | Initialize theme in `<head>` or use inline script |
| System preference API not supported | Low | Low | Graceful fallback to light mode |
| Race condition between theme init and render | Low | High | Use blocking initialization in ThemeProvider |
| Database migration issues | Low | Medium | Field already exists; no migration needed |

---

## Next Steps

1. **Awaiting Approval**: This plan needs human review before proceeding
2. **Post-Approval**: Create feature branch and begin Phase 1 implementation
3. **Iterate**: Follow workflow: Planning → Implementation → Code Review → Security Review → Documentation → Final Approval

---

*Plan created by: planning-agent*  
*Date: 2026-02-23*  
*Status: Pending Approval*
