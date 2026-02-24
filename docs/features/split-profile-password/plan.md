# Implementation Plan: Split Profile and Password Pages

## 1. Feature Overview

### Goals
1. **Split the monolithic Profile page** into two focused pages:
   - `/profile` - Edit profile information (email, full_name)
   - `/profile/password` - Change password with confirmation
2. **Implement toast notification system** for success, warning, and error states
3. **Add password confirmation** validation (frontend and backend)
4. **Apply visual styling** with primary background color for editable fields

### Success Criteria
- [ ] Two separate pages accessible via distinct routes
- [ ] Profile page only shows email and full_name fields
- [ ] Password page requires current_password, new_password, and confirm_password
- [ ] Passwords are validated to match on both frontend and backend
- [ ] Toast notifications appear for all mutation success/error states
- [ ] All interactive elements have `data-testid` attributes
- [ ] All tests pass (unit, integration, E2E)

### Project Rules Reference
This implementation MUST follow:
- `@rules/frontend_arch_design.md` - Frontend architecture, TanStack Query, Zustand, shadcn/ui
- `@rules/backend_arch_design.md` - FastAPI, Pydantic V2, SQLAlchemy 2.0, repository pattern
- `@rules/security.md` - Password validation, input sanitization
- `@rules/development_testing.md` - TDD (Red-Green-Refactor), data-testid attributes, Playwright

---

## 2. Technical Approach

### 2.1 Architecture Decisions

#### Toast Notification System
- **State Management:** Zustand store (`notificationStore.ts`)
- **UI Component:** Custom toast using shadcn/ui design patterns (no external toast library)
- **Position:** Top-right corner, auto-dismiss after 5 seconds
- **Types:** Success (green), Error (red), Warning (amber), Info (blue)
- **Animation:** Fade in/out with slide transition

#### Password Validation Strategy
- **Frontend:** Real-time validation using React state
- **Backend:** Pydantic V2 field_validator with cross-field validation
- **Security:** Never log passwords, validate before hashing

#### Page Splitting Strategy
- Use React Router nested routes for organization
- Extract shared layout patterns into components
- Maintain consistent Card-based form layout

### 2.2 Component Hierarchy

```
App.tsx (routes)
├── /profile → Profile.tsx
│   └── ProfileForm (editable fields with bg-primary/10)
├── /profile/password → ChangePassword.tsx
│   └── PasswordForm (current + new + confirm fields)
│
Toast System:
├── Toaster (container, fixed position)
│   └── Toast (individual notification)
│
State:
├── notificationStore.ts (Zustand - toast queue)
```

### 2.3 Data Flow

```
User Action → TanStack Query Mutation → API Call
    ↓
On Success/Error → notificationStore.addToast()
    ↓
Toaster component renders → Auto-dismiss after 5s
```

---

## 3. File-by-File Implementation Guide

### Phase 1: Backend Schema Updates

#### File: `src/backend/schemas/user.py`

**Changes:** Update `PasswordChange` schema to include `confirm_password` with validation

**Current Code:**
```python
class PasswordChange(BaseModel):
    """Schema for password change requests."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=255)
```

**New Code:**
```python
class PasswordChange(BaseModel):
    """Schema for password change requests with confirmation."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=255)
    confirm_password: str = Field(..., min_length=8, max_length=255)

    @field_validator("confirm_password", mode="after")
    @classmethod
    def check_passwords_match(cls, v: str, info) -> str:
        """Validate that confirm_password matches new_password."""
        # Access other fields from validation context
        data = info.data
        if "new_password" in data and v != data["new_password"]:
            raise ValueError("Passwords do not match")
        return v
```

**Notes:**
- Use Pydantic V2's `field_validator` with `mode="after"` for cross-field validation
- The validator runs after individual field validation
- Error message will be included in the validation error response

---

#### File: `src/backend/api/v1/auth.py`

**Changes:** Update `change_password` endpoint error handling for validation errors

**Current Code:**
```python
@router.put(
    "/me/password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
)
async def change_password(
    password_data: PasswordChange,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> dict:
    """Change the current user's password."""
    # Verify current password
    if not verify_password(
        password_data.current_password, current_user.hashed_password
    ):
        logger.warning(
            f"Password change failed: incorrect current password",
            {"user_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    # Hash and update new password
    new_hashed = hash_password(password_data.new_password)
    await repo.change_password(current_user, new_hashed)

    logger.info(
        f"Password changed for user: {current_user.username}",
        {"user_id": current_user.id},
    )
    return {"message": "Password changed successfully"}
```

**No changes needed** - Pydantic validation will automatically handle the confirm_password validation before the endpoint is called. FastAPI returns 422 Unprocessable Entity for validation errors.

---

### Phase 2: Frontend Types

#### File: `src/frontend/src/types/user.ts`

**Changes:** Update `PasswordChange` interface to include `confirm_password`

**Current Code:**
```typescript
export interface PasswordChange {
  current_password: string;
  new_password: string;
}
```

**New Code:**
```typescript
export interface PasswordChange {
  current_password: string;
  new_password: string;
  confirm_password: string;
}
```

---

#### File: `src/frontend/src/types/notification.ts` (CREATE)

**New File:** Define notification types

```typescript
/**
 * Notification/Toast type definitions.
 */

export type NotificationType = "success" | "error" | "warning" | "info";

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  duration?: number; // in milliseconds, default 5000
}

export interface NotificationState {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, "id">) => void;
  removeNotification: (id: string) => void;
  clearAll: () => void;
}
```

---

### Phase 3: Toast Notification System

#### File: `src/frontend/src/store/notificationStore.ts` (CREATE)

**New File:** Zustand store for notification state

```typescript
/**
 * Notification store using Zustand.
 * Manages toast notification queue.
 */

import { create } from "zustand";
import type { Notification, NotificationState } from "@/types/notification";

// Generate unique ID for notifications
const generateId = (): string =>
  `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],

  addNotification: (notification) => {
    const id = generateId();
    const newNotification: Notification = {
      ...notification,
      id,
      duration: notification.duration ?? 5000,
    };

    set((state) => ({
      notifications: [...state.notifications, newNotification],
    }));

    // Auto-remove after duration
    if (newNotification.duration > 0) {
      setTimeout(() => {
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        }));
      }, newNotification.duration);
    }
  },

  removeNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    }));
  },

  clearAll: () => {
    set({ notifications: [] });
  },
}));
```

---

#### File: `src/frontend/src/components/ui/toast.tsx` (CREATE)

**New File:** Individual toast component

```typescript
/**
 * Toast notification component using shadcn/ui patterns.
 */

import * as React from "react";
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import type { NotificationType } from "@/types/notification";

export interface ToastProps extends React.HTMLAttributes<HTMLDivElement> {
  type: NotificationType;
  title: string;
  message?: string;
  onDismiss?: () => void;
}

const iconMap = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
};

const typeStyles = {
  success: "border-success/30 bg-success/10 text-success",
  error: "border-destructive/30 bg-destructive/10 text-destructive",
  warning: "border-warning/30 bg-warning/10 text-warning",
  info: "border-info/30 bg-info/10 text-info",
};

export const Toast = React.forwardRef<HTMLDivElement, ToastProps>(
  ({ className, type, title, message, onDismiss, ...props }, ref) => {
    const Icon = iconMap[type];

    return (
      <div
        ref={ref}
        className={cn(
          "pointer-events-auto relative flex w-full max-w-sm items-start gap-3 rounded-lg border p-4 shadow-lg transition-all",
          typeStyles[type],
          className
        )}
        role="alert"
        data-testid={`toast-${type}`}
        {...props}
      >
        <Icon className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
        <div className="flex-1">
          <h4 className="text-sm font-semibold">{title}</h4>
          {message && (
            <p className="mt-1 text-sm opacity-90">{message}</p>
          )}
        </div>
        {onDismiss && (
          <Button
            variant="ghost"
            size="icon"
            className="-mr-2 -mt-2 h-6 w-6 shrink-0 opacity-70 hover:opacity-100"
            onClick={onDismiss}
            data-testid="toast-dismiss-button"
          >
            <X className="h-4 w-4" />
            <span className="sr-only">Dismiss</span>
          </Button>
        )}
      </div>
    );
  }
);
Toast.displayName = "Toast";
```

**Note:** Need to add lucide-react icons. Check if already installed.

---

#### File: `src/frontend/src/components/ui/toaster.tsx` (CREATE)

**New File:** Toast container component

```typescript
/**
 * Toast container component that renders all active notifications.
 * Positioned fixed at top-right of viewport.
 */

import { AnimatePresence, motion } from "framer-motion";

import { useNotificationStore } from "@/store/notificationStore";
import { Toast } from "@/components/ui/toast";

export function Toaster() {
  const { notifications, removeNotification } = useNotificationStore();

  return (
    <div
      className="fixed right-4 top-4 z-[100] flex flex-col gap-2"
      data-testid="toast-container"
    >
      <AnimatePresence mode="popLayout">
        {notifications.map((notification) => (
          <motion.div
            key={notification.id}
            layout
            initial={{ opacity: 0, x: 50, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 50, scale: 0.9 }}
            transition={{ duration: 0.2 }}
          >
            <Toast
              type={notification.type}
              title={notification.title}
              message={notification.message}
              onDismiss={() => removeNotification(notification.id)}
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
```

**Note:** Requires `framer-motion` for animations. If not available, use CSS transitions instead.

---

#### File: `src/frontend/src/hooks/useToast.ts` (CREATE)

**New File:** Convenience hook for showing toast notifications

```typescript
/**
 * Convenience hook for showing toast notifications.
 * Wraps the notification store with common use cases.
 */

import { useCallback } from "react";

import { useNotificationStore } from "@/store/notificationStore";
import type { NotificationType } from "@/types/notification";

interface ToastOptions {
  title: string;
  message?: string;
  duration?: number;
}

export function useToast() {
  const addNotification = useNotificationStore(
    (state) => state.addNotification
  );

  const show = useCallback(
    (type: NotificationType, options: ToastOptions) => {
      addNotification({
        type,
        title: options.title,
        message: options.message,
        duration: options.duration,
      });
    },
    [addNotification]
  );

  const success = useCallback(
    (options: ToastOptions) => show("success", options),
    [show]
  );

  const error = useCallback(
    (options: ToastOptions) => show("error", options),
    [show]
  );

  const warning = useCallback(
    (options: ToastOptions) => show("warning", options),
    [show]
  );

  const info = useCallback(
    (options: ToastOptions) => show("info", options),
    [show]
  );

  return { show, success, error, warning, info };
}
```

---

### Phase 4: Update Auth Hooks

#### File: `src/frontend/src/hooks/useAuth.ts`

**Changes:** Add toast notifications to all mutations

**Add import:**
```typescript
import { useToast } from "@/hooks/useToast";
```

**Update `useUpdateProfile`:**
```typescript
export function useUpdateProfile() {
  const setUser = useAuthStore((state) => state.setUser);
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: async (data: UserUpdate): Promise<User> => {
      const response = await api.put("/api/v1/auth/me", data);
      return response.data;
    },
    onSuccess: (data) => {
      setUser(data);
      queryClient.setQueryData(authKeys.user(), data);
      toast.success({
        title: "Profile updated",
        message: "Your profile has been updated successfully.",
      });
      logger.info("Profile updated successfully");
    },
    onError: (error: AxiosError<{ detail: string }>) => {
      const message = error.response?.data?.detail || "Failed to update profile";
      toast.error({
        title: "Update failed",
        message,
      });
      logger.error("Profile update failed", { error });
    },
  });
}
```

**Update `useChangePassword`:**
```typescript
export function useChangePassword() {
  const toast = useToast();

  return useMutation({
    mutationFn: async (data: PasswordChange): Promise<void> => {
      await api.put("/api/v1/auth/me/password", data);
    },
    onSuccess: () => {
      toast.success({
        title: "Password changed",
        message: "Your password has been changed successfully.",
      });
      logger.info("Password changed successfully");
    },
    onError: (error: AxiosError<{ detail: string }>) => {
      const message = error.response?.data?.detail || "Failed to change password";
      toast.error({
        title: "Password change failed",
        message,
      });
      logger.error("Password change failed", { error });
    },
  });
}
```

**Also update other mutations (useLogin, useLogout, useRegister)** with appropriate toast notifications following the same pattern.

---

### Phase 5: Refactor Profile Page

#### File: `src/frontend/src/pages/Profile.tsx`

**Changes:** Remove password change section, add navigation to password page, style editable fields

**New Code:**
```typescript
import { useState } from "react";
import { Link } from "react-router-dom";
import { Key, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCurrentUser, useUpdateProfile } from "@/hooks/useAuth";
import { useAuthStore } from "@/store/authStore";

export function Profile() {
  const user = useAuthStore((state) => state.user);
  const { isLoading } = useCurrentUser();
  const updateProfile = useUpdateProfile();

  const [profileData, setProfileData] = useState({
    email: user?.email || "",
    full_name: user?.full_name || "",
  });

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await updateProfile.mutateAsync(profileData);
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Profile</h1>
      </div>

      <Card data-testid="profile-form">
        <CardHeader>
          <CardTitle>Edit Profile</CardTitle>
          <CardDescription>
            Update your email address and display name.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleProfileSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={profileData.email}
                onChange={(e) =>
                  setProfileData({ ...profileData, email: e.target.value })
                }
                className="bg-primary/10"
                data-testid="profile-email-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="full_name">Full Name</Label>
              <Input
                id="full_name"
                type="text"
                value={profileData.full_name}
                onChange={(e) =>
                  setProfileData({ ...profileData, full_name: e.target.value })
                }
                className="bg-primary/10"
                data-testid="profile-fullname-input"
              />
            </div>
            <Button
              type="submit"
              disabled={updateProfile.isPending}
              data-testid="profile-save-button"
            >
              {updateProfile.isPending ? "Saving..." : "Save Changes"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Security</CardTitle>
          <CardDescription>
            Manage your password and account security.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Link
            to="/profile/password"
            className="flex items-center justify-between rounded-lg border p-4 transition-colors hover:bg-muted"
            data-testid="profile-change-password-link"
          >
            <div className="flex items-center gap-3">
              <Key className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="font-medium">Change Password</p>
                <p className="text-sm text-muted-foreground">
                  Update your password to keep your account secure
                </p>
              </div>
            </div>
            <ChevronRight className="h-5 w-5 text-muted-foreground" />
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
```

**Notes:**
- Uses `bg-primary/10` for editable input fields (Trinity Gold with 10% opacity)
- Adds CardDescription for better UX
- Includes navigation card to password change page
- All interactive elements have `data-testid` attributes

---

### Phase 6: Create Password Change Page

#### File: `src/frontend/src/pages/ChangePassword.tsx` (CREATE)

**New File:** Password change page with confirmation validation

```typescript
import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Eye, EyeOff } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useChangePassword } from "@/hooks/useAuth";
import { logger } from "@/lib/logger";

export function ChangePassword() {
  const changePassword = useChangePassword();
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [passwordData, setPasswordData] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  const [validationError, setValidationError] = useState<string | null>(null);

  const validatePasswords = (): boolean => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      setValidationError("New passwords do not match");
      return false;
    }
    if (passwordData.new_password.length < 8) {
      setValidationError("New password must be at least 8 characters");
      return false;
    }
    setValidationError(null);
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validatePasswords()) {
      return;
    }

    try {
      await changePassword.mutateAsync(passwordData);
      // Clear form on success
      setPasswordData({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });
    } catch (error) {
      // Error is handled by the mutation's onError callback (toast)
      logger.error("Password change form submission failed", { error });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/profile" data-testid="password-back-button">
            <ArrowLeft className="h-5 w-5" />
            <span className="sr-only">Back to Profile</span>
          </Link>
        </Button>
        <h1 className="text-3xl font-bold">Change Password</h1>
      </div>

      <Card data-testid="password-change-form">
        <CardHeader>
          <CardTitle>Update Password</CardTitle>
          <CardDescription>
            Enter your current password and choose a new one.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {validationError && (
              <Alert variant="destructive" data-testid="password-validation-error">
                <AlertDescription>{validationError}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="current_password">Current Password</Label>
              <div className="relative">
                <Input
                  id="current_password"
                  type={showCurrentPassword ? "text" : "password"}
                  value={passwordData.current_password}
                  onChange={(e) =>
                    setPasswordData({
                      ...passwordData,
                      current_password: e.target.value,
                    })
                  }
                  className="bg-primary/10 pr-10"
                  data-testid="password-current-input"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full px-3"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  data-testid="password-current-toggle"
                >
                  {showCurrentPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                  <span className="sr-only">
                    {showCurrentPassword ? "Hide password" : "Show password"}
                  </span>
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="new_password">New Password</Label>
              <div className="relative">
                <Input
                  id="new_password"
                  type={showNewPassword ? "text" : "password"}
                  value={passwordData.new_password}
                  onChange={(e) =>
                    setPasswordData({
                      ...passwordData,
                      new_password: e.target.value,
                    })
                  }
                  className="bg-primary/10 pr-10"
                  data-testid="password-new-input"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full px-3"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  data-testid="password-new-toggle"
                >
                  {showNewPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                  <span className="sr-only">
                    {showNewPassword ? "Hide password" : "Show password"}
                  </span>
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm_password">Confirm New Password</Label>
              <div className="relative">
                <Input
                  id="confirm_password"
                  type={showConfirmPassword ? "text" : "password"}
                  value={passwordData.confirm_password}
                  onChange={(e) =>
                    setPasswordData({
                      ...passwordData,
                      confirm_password: e.target.value,
                    })
                  }
                  className="bg-primary/10 pr-10"
                  data-testid="password-confirm-input"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full px-3"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  data-testid="password-confirm-toggle"
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                  <span className="sr-only">
                    {showConfirmPassword ? "Hide password" : "Show password"}
                  </span>
                </Button>
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <Button
                type="button"
                variant="outline"
                asChild
                data-testid="password-cancel-button"
              >
                <Link to="/profile">Cancel</Link>
              </Button>
              <Button
                type="submit"
                disabled={changePassword.isPending}
                data-testid="password-submit-button"
              >
                {changePassword.isPending ? "Changing..." : "Change Password"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
```

**Notes:**
- Includes password visibility toggle for all fields
- Real-time validation before submission
- Shows validation errors inline with Alert component
- Uses `bg-primary/10` for editable fields
- Back button returns to profile page
- Form clears on successful submission

---

### Phase 7: Update App Routes

#### File: `src/frontend/src/App.tsx`

**Changes:** Add new route for password change page and include Toaster

**Add imports:**
```typescript
import { ChangePassword } from "@/pages/ChangePassword";
import { Toaster } from "@/components/ui/toaster";
```

**Add route (after /profile route):**
```typescript
<Route
  path="/profile/password"
  element={
    <ProtectedRoute>
      <ChangePassword />
    </ProtectedRoute>
  }
/>
```

**Add Toaster component (inside ThemeProvider, after AuthChecker):**
```typescript
<ThemeProvider>
  <AuthChecker>
    <Routes>
      {/* ... routes ... */}
    </Routes>
    <Toaster />
  </AuthChecker>
</ThemeProvider>
```

---

### Phase 8: Add UI Components

The implementation requires an Alert component for showing validation errors. Check if it exists, otherwise create it.

#### File: `src/frontend/src/components/ui/alert.tsx` (CREATE if not exists)

```typescript
/**
 * Alert component using shadcn/ui patterns.
 */

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const alertVariants = cva(
  "relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground",
  {
    variants: {
      variant: {
        default: "bg-background text-foreground",
        destructive:
          "border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

const Alert = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & VariantProps<typeof alertVariants>
>(({ className, variant, ...props }, ref) => (
  <div
    ref={ref}
    role="alert"
    className={cn(alertVariants({ variant }), className)}
    {...props}
  />
));
Alert.displayName = "Alert";

const AlertDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm [&_p]:leading-relaxed", className)}
    {...props}
  />
));
AlertDescription.displayName = "AlertDescription";

export { Alert, AlertDescription };
```

---

## 4. Testing Strategy

### 4.1 Unit Tests (Vitest)

#### Test: `tests/frontend/store/notificationStore.test.ts`

```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";
import { useNotificationStore } from "@/store/notificationStore";

describe("notificationStore", () => {
  beforeEach(() => {
    // Reset store state
    useNotificationStore.setState({ notifications: [] });
  });

  it("should add a notification", () => {
    const { addNotification } = useNotificationStore.getState();
    
    addNotification({
      type: "success",
      title: "Test",
      message: "Test message",
    });

    const { notifications } = useNotificationStore.getState();
    expect(notifications).toHaveLength(1);
    expect(notifications[0].type).toBe("success");
    expect(notifications[0].title).toBe("Test");
  });

  it("should remove a notification by id", () => {
    const { addNotification, removeNotification } = useNotificationStore.getState();
    
    addNotification({ type: "info", title: "Test" });
    const { notifications } = useNotificationStore.getState();
    const id = notifications[0].id;

    removeNotification(id);
    
    expect(useNotificationStore.getState().notifications).toHaveLength(0);
  });

  it("should auto-remove notification after duration", async () => {
    vi.useFakeTimers();
    const { addNotification } = useNotificationStore.getState();
    
    addNotification({
      type: "info",
      title: "Test",
      duration: 1000,
    });

    expect(useNotificationStore.getState().notifications).toHaveLength(1);
    
    vi.advanceTimersByTime(1000);
    
    expect(useNotificationStore.getState().notifications).toHaveLength(0);
    vi.useRealTimers();
  });
});
```

#### Test: `tests/frontend/hooks/useToast.test.ts`

```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook } from "@testing-library/react";
import { useToast } from "@/hooks/useToast";
import { useNotificationStore } from "@/store/notificationStore";

describe("useToast", () => {
  beforeEach(() => {
    useNotificationStore.setState({ notifications: [] });
  });

  it("should show success toast", () => {
    const { result } = renderHook(() => useToast());
    
    result.current.success({
      title: "Success!",
      message: "Operation completed",
    });

    const { notifications } = useNotificationStore.getState();
    expect(notifications).toHaveLength(1);
    expect(notifications[0].type).toBe("success");
    expect(notifications[0].title).toBe("Success!");
  });

  it("should show error toast", () => {
    const { result } = renderHook(() => useToast());
    
    result.current.error({
      title: "Error!",
      message: "Something went wrong",
    });

    const { notifications } = useNotificationStore.getState();
    expect(notifications[0].type).toBe("error");
  });
});
```

#### Test: `tests/frontend/pages/ChangePassword.test.tsx`

```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ChangePassword } from "@/pages/ChangePassword";

// Mock the auth hooks
vi.mock("@/hooks/useAuth", () => ({
  useChangePassword: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}));

describe("ChangePassword", () => {
  const queryClient = new QueryClient();

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ChangePassword />
        </BrowserRouter>
      </QueryClientProvider>
    );

  it("should render password change form", () => {
    renderComponent();
    
    expect(screen.getByTestId("password-change-form")).toBeInTheDocument();
    expect(screen.getByTestId("password-current-input")).toBeInTheDocument();
    expect(screen.getByTestId("password-new-input")).toBeInTheDocument();
    expect(screen.getByTestId("password-confirm-input")).toBeInTheDocument();
  });

  it("should show validation error when passwords do not match", async () => {
    renderComponent();
    
    const newPasswordInput = screen.getByTestId("password-new-input");
    const confirmPasswordInput = screen.getByTestId("password-confirm-input");
    const submitButton = screen.getByTestId("password-submit-button");

    fireEvent.change(newPasswordInput, { target: { value: "newpassword123" } });
    fireEvent.change(confirmPasswordInput, { target: { value: "different123" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByTestId("password-validation-error")).toBeInTheDocument();
    });
  });
});
```

### 4.2 Backend Tests

#### Test: Update `tests/backend/test_auth_api.py`

Add tests for password confirmation validation:

```python
async def test_change_password_with_confirmation_mismatch(
    async_client: AsyncClient, auth_headers: dict
):
    """Test that password change fails when confirmation doesn't match."""
    response = await async_client.put(
        "/api/v1/auth/me/password",
        headers=auth_headers,
        json={
            "current_password": "testpassword123",
            "new_password": "newpassword123",
            "confirm_password": "differentpassword123",
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert "Passwords do not match" in str(data)
```

### 4.3 E2E Tests (Playwright)

#### Test: `tests/e2e/password-change.spec.ts`

```typescript
import { test, expect } from "@playwright/test";

test.describe("Password Change", () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto("/login");
    await page.getByTestId("login-username-input").fill("testuser");
    await page.getByTestId("login-password-input").fill("testpassword123");
    await page.getByTestId("login-submit-button").click();
    await page.waitForURL("/");
    
    // Navigate to profile
    await page.goto("/profile");
  });

  test("should navigate to password change page", async ({ page }) => {
    await page.getByTestId("profile-change-password-link").click();
    await expect(page).toHaveURL("/profile/password");
    await expect(page.getByTestId("password-change-form")).toBeVisible();
  });

  test("should show error when passwords do not match", async ({ page }) => {
    await page.goto("/profile/password");
    
    await page.getByTestId("password-current-input").fill("testpassword123");
    await page.getByTestId("password-new-input").fill("newpassword123");
    await page.getByTestId("password-confirm-input").fill("different123");
    await page.getByTestId("password-submit-button").click();
    
    await expect(page.getByTestId("password-validation-error")).toBeVisible();
    await expect(page.getByText("New passwords do not match")).toBeVisible();
  });

  test("should successfully change password with matching passwords", async ({ page }) => {
    await page.goto("/profile/password");
    
    await page.getByTestId("password-current-input").fill("testpassword123");
    await page.getByTestId("password-new-input").fill("newpassword123");
    await page.getByTestId("password-confirm-input").fill("newpassword123");
    await page.getByTestId("password-submit-button").click();
    
    // Wait for success toast
    await expect(page.getByTestId("toast-success")).toBeVisible();
    await expect(page.getByText("Password changed")).toBeVisible();
  });

  test("should navigate back to profile", async ({ page }) => {
    await page.goto("/profile/password");
    await page.getByTestId("password-back-button").click();
    await expect(page).toHaveURL("/profile");
  });
});
```

---

## 5. Schema Summary

### Backend Schema Changes

| Schema | Field | Type | Constraints |
|--------|-------|------|-------------|
| PasswordChange | current_password | str | Required |
| PasswordChange | new_password | str | Required, min_length=8, max_length=255 |
| PasswordChange | confirm_password | str | Required, min_length=8, max_length=255 |

**Validation:** Cross-field validator ensures `confirm_password == new_password`

### Frontend Type Changes

| Interface | Field | Type | Description |
|-----------|-------|------|-------------|
| PasswordChange | current_password | string | Current password |
| PasswordChange | new_password | string | New password (min 8 chars) |
| PasswordChange | confirm_password | string | Password confirmation |

---

## 6. Route Structure

| Route | Component | Access |
|-------|-----------|--------|
| `/profile` | Profile.tsx | Protected |
| `/profile/password` | ChangePassword.tsx | Protected |

---

## 7. Dependencies

### Check/Install

1. **lucide-react** - Icons (ArrowLeft, Key, Eye, EyeOff, etc.)
   ```bash
   cd src/frontend && npm install lucide-react
   ```

2. **framer-motion** - Toast animations (optional, can use CSS instead)
   ```bash
   cd src/frontend && npm install framer-motion
   ```

### Verify Existing
- zustand (state management)
- @tanstack/react-query (server state)
- axios (API client)
- tailwindcss (styling)
- class-variance-authority (component variants)

---

## 8. Migration Notes

### Breaking Changes
None - this is an additive feature that doesn't remove existing functionality.

### Database Migrations
None required - only API schema changes.

### API Compatibility
- Old requests without `confirm_password` will fail with 422 validation error
- Frontend must be deployed simultaneously with backend update

---

## 9. Commit Strategy

Follow Conventional Commits:

```
feat(backend): add confirm_password validation to PasswordChange schema

feat(frontend): create notification store and toast system

feat(frontend): create Toast and Toaster components

feat(frontend): add useToast hook for notifications

refactor(frontend): split Profile page, add password change navigation

feat(frontend): create ChangePassword page with confirmation

feat(frontend): update App.tsx with new routes and Toaster

test(frontend): add tests for notification store and toast system

test(backend): add password confirmation validation tests

test(e2e): add password change E2E tests
```

---

## 10. Checklist

### Before Implementation
- [ ] Review this plan with team
- [ ] Approve plan (human checkpoint)
- [ ] Create branch `feat/split-profile-password`

### During Implementation
- [ ] Phase 1: Backend schema updates
- [ ] Phase 2: Toast notification system
- [ ] Phase 3: Frontend types & store
- [ ] Phase 4: Profile page refactor
- [ ] Phase 5: Password change page
- [ ] Phase 6: Route updates
- [ ] Phase 7: Testing (Unit/Integration/E2E)

### After Implementation
- [ ] Run all tests (backend + frontend + E2E)
- [ ] Security review
- [ ] Code review
- [ ] Documentation update
- [ ] Human final approval
- [ ] Merge to main

---

## 11. References

### Project Rules
- `@AGENTS.md` - Master agent instructions
- `@rules/frontend_arch_design.md` - Frontend architecture
- `@rules/backend_arch_design.md` - Backend architecture
- `@rules/security.md` - Security guidelines
- `@rules/development_testing.md` - Testing & TDD

### Related Files
- `src/frontend/src/pages/Profile.tsx` - Current profile page
- `src/frontend/src/hooks/useAuth.ts` - Auth hooks
- `src/frontend/src/types/user.ts` - User types
- `src/backend/schemas/user.py` - User schemas
- `src/backend/api/v1/auth.py` - Auth endpoints
