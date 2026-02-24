# Theme Development Guide

A technical guide for developers working with the theme switching system.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Theme Store](#theme-store)
- [Using Themes in Components](#using-themes-in-components)
- [Adding New Theme Modes](#adding-new-theme-modes)
- [Testing Theme Functionality](#testing-theme-functionality)
- [API Integration](#api-integration)

## Architecture Overview

The theme system uses a layered architecture separating concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                      UI Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ ThemeToggle  │  │   Header     │  │  Components  │      │
│  │  (React)     │  │   (Layout)   │  │   (Pages)    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                 State Management Layer                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │              themeStore (Zustand)                  │    │
│  │  • LocalStorage persistence                        │    │
│  │  • System preference detection                     │    │
│  │  • DOM class management                            │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │           useTheme Hook (TanStack Query)           │    │
│  │  • Server synchronization                          │    │
│  │  • API communication                               │    │
│  └────────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   API Layer (FastAPI)                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │         PATCH /api/v1/auth/me/theme                │    │
│  │  • Authentication via HttpOnly cookies             │    │
│  │  • Rate limiting (10 req/min)                      │    │
│  │  • Database persistence                            │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `ThemeProvider` | Initializes theme on app mount, handles side effects | `components/ThemeProvider.tsx` |
| `ThemeToggle` | UI dropdown for theme selection | `components/ThemeToggle.tsx` |
| `themeStore` | Client state, localStorage, system detection | `store/themeStore.ts` |
| `useUpdateThemePreference` | Server sync via TanStack Query | `hooks/useTheme.ts` |
| Theme endpoint | Persist theme to database | `api/v1/auth.py` |

## Theme Store

The theme store is the central state management for themes using Zustand.

### State Interface

```typescript
// types/theme.ts
export type ThemePreference = 'light' | 'dark' | 'system';
export type ResolvedTheme = 'light' | 'dark';

interface ThemeState {
  // User's preferred theme setting
  theme: ThemePreference;
  
  // Computed actual theme (resolves 'system' to light/dark)
  resolvedTheme: ResolvedTheme;
  
  // Media query for system preference detection
  systemMediaQuery: MediaQueryList | null;
  
  // Event handler reference (for cleanup)
  systemHandler: ((e: MediaQueryListEvent) => void) | null;
  
  // Actions
  setTheme: (theme: ThemePreference, skipSync?: boolean) => void;
  initializeTheme: () => void;
  cleanup: () => void;
}
```

### Store Implementation

```typescript
// store/themeStore.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

const STORAGE_KEY = 'theme-preference';

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'system',
      resolvedTheme: 'light',
      systemMediaQuery: null,
      systemHandler: null,

      setTheme: (theme, skipSync = false) => {
        // Update state
        set({ theme });
        
        // Apply to DOM
        const resolved = resolveTheme(theme);
        applyThemeToDOM(resolved);
        set({ resolvedTheme: resolved });
        
        // Sync with server if authenticated
        if (!skipSync) {
          syncWithServer(theme);
        }
      },

      initializeTheme: () => {
        const { theme } = get();
        const resolved = resolveTheme(theme);
        applyThemeToDOM(resolved);
        
        // Set up system preference listener if needed
        if (theme === 'system') {
          setupSystemListener();
        }
      },

      cleanup: () => {
        const { systemMediaQuery, systemHandler } = get();
        if (systemMediaQuery && systemHandler) {
          systemMediaQuery.removeEventListener('change', systemHandler);
        }
        set({ systemMediaQuery: null, systemHandler: null });
      },
    }),
    {
      name: STORAGE_KEY,
      storage: createJSONStorage(() => localStorage),
    }
  )
);
```

### System Preference Detection

```typescript
function resolveTheme(theme: ThemePreference): ResolvedTheme {
  if (theme === 'system') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
  }
  return theme;
}

function setupSystemListener() {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  
  const handler = (e: MediaQueryListEvent) => {
    const resolved = e.matches ? 'dark' : 'light';
    applyThemeToDOM(resolved);
    useThemeStore.setState({ resolvedTheme: resolved });
  };
  
  mediaQuery.addEventListener('change', handler);
  
  useThemeStore.setState({
    systemMediaQuery: mediaQuery,
    systemHandler: handler,
  });
}

function applyThemeToDOM(theme: ResolvedTheme) {
  const root = document.documentElement;
  if (theme === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
}
```

### Server Sync Priority

**Important:** For authenticated users, the server theme always takes precedence over localStorage. This is a security measure to prevent localStorage manipulation from affecting the UI for logged-in users.

```typescript
// In auth initialization or user fetch
const serverTheme = authStore.getState().user?.theme_preference;
if (serverTheme) {
  // Server value takes precedence
  themeStore.setTheme(serverTheme, true); // skipSync = true
} else {
  // Use localStorage value for unauthenticated users
  themeStore.initializeTheme();
}
```

## Using Themes in Components

### Basic Theme Access

```typescript
import { useThemeStore } from '@/store/themeStore';

function MyComponent() {
  // Get current theme
  const theme = useThemeStore((state) => state.theme);
  const resolvedTheme = useThemeStore((state) => state.resolvedTheme);
  
  // Get action
  const setTheme = useThemeStore((state) => state.setTheme);
  
  return (
    <div className={resolvedTheme === 'dark' ? 'bg-gray-900' : 'bg-white'}>
      Current theme: {theme}
    </div>
  );
}
```

### Theme-Aware Styling with Tailwind

Use Tailwind's `dark:` modifier for conditional styling:

```tsx
// ❌ Don't manually check theme
<div className={resolvedTheme === 'dark' ? 'text-white' : 'text-black'}>

// ✅ Use Tailwind dark: modifier
<div className="text-black dark:text-white">
```

The `dark` class is automatically applied to `<html>` by the theme store.

### Theme Toggle Component Pattern

```tsx
// components/ThemeToggle.tsx
import { useThemeStore } from '@/store/themeStore';
import { useUpdateThemePreference } from '@/hooks/useTheme';
import { Sun, Moon, Monitor, Check } from 'lucide-react';

const THEME_OPTIONS = [
  { value: 'light', label: 'Light', icon: Sun },
  { value: 'dark', label: 'Dark', icon: Moon },
  { value: 'system', label: 'System', icon: Monitor },
] as const;

export function ThemeToggle() {
  const theme = useThemeStore((state) => state.theme);
  const setTheme = useThemeStore((state) => state.setTheme);
  const updateServerTheme = useUpdateThemePreference();
  
  const handleThemeChange = (newTheme: ThemePreference) => {
    // Update local state immediately for responsiveness
    setTheme(newTheme);
    
    // Sync with server
    updateServerTheme.mutate(newTheme);
  };
  
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Toggle theme">
          {theme === 'light' && <Sun className="h-5 w-5" />}
          {theme === 'dark' && <Moon className="h-5 w-5" />}
          {theme === 'system' && <Monitor className="h-5 w-5" />}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {THEME_OPTIONS.map(({ value, label, icon: Icon }) => (
          <DropdownMenuItem
            key={value}
            onClick={() => handleThemeChange(value)}
            data-testid={`theme-option-${value}`}
          >
            <Icon className="mr-2 h-4 w-4" />
            <span>{label}</span>
            {theme === value && <Check className="ml-auto h-4 w-4" />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

## Adding New Theme Modes

To add a new theme (e.g., "high-contrast" or "sepia"):

### 1. Update Type Definitions

```typescript
// types/theme.ts
export type ThemePreference = 'light' | 'dark' | 'system' | 'high-contrast';
```

### 2. Update Backend Schema

```python
# schemas/user.py
ThemePreference = Literal["light", "dark", "system", "high-contrast"]
```

### 3. Add CSS Variables

```css
/* globals.css */
[data-theme="high-contrast"] {
  --background: 0 0% 0%;
  --foreground: 0 0% 100%;
  /* High contrast colors */
}
```

### 4. Update Store Logic

```typescript
// store/themeStore.ts
function applyThemeToDOM(theme: ResolvedTheme | 'high-contrast') {
  const root = document.documentElement;
  
  // Remove all theme classes
  root.classList.remove('dark');
  root.removeAttribute('data-theme');
  
  // Apply new theme
  if (theme === 'dark') {
    root.classList.add('dark');
  } else if (theme === 'high-contrast') {
    root.setAttribute('data-theme', 'high-contrast');
  }
  // light is the default, no class needed
}
```

### 5. Update UI Components

```typescript
const THEME_OPTIONS = [
  { value: 'light', label: 'Light', icon: Sun },
  { value: 'dark', label: 'Dark', icon: Moon },
  { value: 'system', label: 'System', icon: Monitor },
  { value: 'high-contrast', label: 'High Contrast', icon: Eye },
] as const;
```

### 6. Update Theme Toggle Icons

```tsx
{theme === 'high-contrast' && <Eye className="h-5 w-5" />}
```

### 7. Add Migration (Database)

```python
# alembic migration
from alembic import op

# Update existing check constraint or validation
```

## Testing Theme Functionality

### Unit Tests for Store

```typescript
// store/themeStore.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useThemeStore } from './themeStore';

describe('themeStore', () => {
  beforeEach(() => {
    // Reset store
    useThemeStore.setState({
      theme: 'system',
      resolvedTheme: 'light',
      systemMediaQuery: null,
      systemHandler: null,
    });
    
    // Clear localStorage
    localStorage.clear();
    
    // Mock matchMedia
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      })),
    });
  });

  it('should initialize with system theme', () => {
    const theme = useThemeStore.getState().theme;
    expect(theme).toBe('system');
  });

  it('should persist theme to localStorage', () => {
    useThemeStore.getState().setTheme('dark');
    
    const stored = localStorage.getItem('theme-preference');
    expect(stored).toContain('dark');
  });

  it('should resolve system theme based on matchMedia', () => {
    // Mock dark mode preference
    window.matchMedia = vi.fn().mockImplementation(query => ({
      matches: query === '(prefers-color-scheme: dark)',
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }));
    
    useThemeStore.getState().initializeTheme();
    
    expect(useThemeStore.getState().resolvedTheme).toBe('dark');
  });
});
```

### Component Tests

```typescript
// components/ThemeToggle.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeToggle } from './ThemeToggle';

// Mock the store
vi.mock('@/store/themeStore', () => ({
  useThemeStore: vi.fn((selector) => selector({
    theme: 'light',
    setTheme: vi.fn(),
  })),
}));

describe('ThemeToggle', () => {
  it('renders theme options', async () => {
    render(<ThemeToggle />);
    
    // Open dropdown
    fireEvent.click(screen.getByLabelText('Toggle theme'));
    
    // Check options are present
    expect(screen.getByTestId('theme-option-light')).toBeInTheDocument();
    expect(screen.getByTestId('theme-option-dark')).toBeInTheDocument();
    expect(screen.getByTestId('theme-option-system')).toBeInTheDocument();
  });

  it('shows checkmark for current theme', () => {
    render(<ThemeToggle />);
    fireEvent.click(screen.getByLabelText('Toggle theme'));
    
    // Light theme should have checkmark (current in mock)
    const lightOption = screen.getByTestId('theme-option-light');
    expect(lightOption.querySelector('svg')).toHaveClass('check');
  });
});
```

### E2E Tests (Playwright)

```typescript
// e2e/theme.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Theme Switching', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await login(page, 'test@example.com', 'password');
  });

  test('user can switch between themes', async ({ page }) => {
    // Open theme toggle
    await page.getByTestId('theme-toggle-button').click();
    
    // Select dark mode
    await page.getByTestId('theme-option-dark').click();
    
    // Verify dark class on html
    const html = page.locator('html');
    await expect(html).toHaveClass(/dark/);
    
    // Reopen and select light
    await page.getByTestId('theme-toggle-button').click();
    await page.getByTestId('theme-option-light').click();
    
    // Verify dark class removed
    await expect(html).not.toHaveClass(/dark/);
  });

  test('theme persists after page reload', async ({ page }) => {
    // Set dark theme
    await page.getByTestId('theme-toggle-button').click();
    await page.getByTestId('theme-option-dark').click();
    
    // Reload
    await page.reload();
    
    // Verify theme persisted
    const html = page.locator('html');
    await expect(html).toHaveClass(/dark/);
  });

  test('system theme follows OS preference', async ({ page }) => {
    // Emulate dark mode preference
    await page.emulateMedia({ colorScheme: 'dark' });
    
    // Select system theme
    await page.getByTestId('theme-toggle-button').click();
    await page.getByTestId('theme-option-system').click();
    
    // Verify dark class applied
    const html = page.locator('html');
    await expect(html).toHaveClass(/dark/);
  });
});
```

## API Integration

### Theme Hook Pattern

```typescript
// hooks/useTheme.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { logger } from '@/lib/logger';
import { useAuthStore } from '@/store/authStore';
import type { ThemePreference, User } from '@/types';

const THEME_API_ENDPOINT = '/api/v1/auth/me/theme';

export function useUpdateThemePreference() {
  const queryClient = useQueryClient();
  const setUser = useAuthStore((state) => state.setUser);
  
  return useMutation({
    mutationFn: async (theme: ThemePreference): Promise<User> => {
      const response = await api.patch(THEME_API_ENDPOINT, {
        theme_preference: theme,
      });
      return response.data;
    },
    
    onSuccess: (data) => {
      // Update auth store with new user data
      setUser(data);
      
      // Invalidate and refetch user query
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      
      logger.info('Theme preference synced with server', {
        theme: data.theme_preference,
        userId: data.id,
      });
    },
    
    onError: (error: AxiosError) => {
      logger.error('Failed to sync theme preference', {
        error: error.message,
        status: error.response?.status,
      });
      
      // Optionally show toast notification
      if (error.response?.status === 429) {
        toast.error('Please wait before changing theme again');
      }
    },
  });
}

export function useThemeSync() {
  const setTheme = useThemeStore((state) => state.setTheme);
  const user = useAuthStore((state) => state.user);
  
  // Sync theme when user data changes
  useEffect(() => {
    if (user?.theme_preference) {
      // Server theme takes precedence
      setTheme(user.theme_preference, true); // skipSync = true
    }
  }, [user?.theme_preference, setTheme]);
}
```

### Rate Limit Handling

```typescript
// hooks/useTheme.ts (continued)

export function useUpdateThemePreference() {
  const [isRateLimited, setIsRateLimited] = useState(false);
  
  const mutation = useMutation({
    mutationFn: async (theme: ThemePreference) => {
      if (isRateLimited) {
        throw new Error('Rate limited');
      }
      return api.patch(THEME_API_ENDPOINT, { theme_preference: theme });
    },
    
    onError: (error: AxiosError) => {
      if (error.response?.status === 429) {
        setIsRateLimited(true);
        
        // Reset after 60 seconds
        setTimeout(() => setIsRateLimited(false), 60000);
        
        toast.error('Theme change rate limit reached. Please wait.');
      }
    },
  });
  
  return {
    ...mutation,
    isRateLimited,
  };
}
```

## Best Practices

### DO

- ✅ Use Tailwind's `dark:` modifier for conditional styling
- ✅ Test theme changes in both light and dark modes
- ✅ Provide keyboard navigation for theme toggle
- ✅ Use `data-testid` attributes for E2E tests
- ✅ Respect `prefers-reduced-motion` for theme transitions
- ✅ Log theme-related actions for debugging

### DON'T

- ❌ Use `useEffect` for data fetching (use TanStack Query)
- ❌ Store JWT tokens in localStorage alongside theme
- ❌ Use bare `console.log` (use centralized logger)
- ❌ Manually manipulate DOM classes outside ThemeProvider
- ❌ Ignore system preference when theme is set to "system"

## Related Documentation

- [Theme Switching User Guide](./theme-switching.md) - End-user documentation
- [Theme API Documentation](../api/theme.md) - Backend API reference
- [Frontend Architecture](../../rules/frontend_arch_design.md) - Project architecture rules
- [Backend Architecture](../../rules/backend_arch_design.md) - API layer rules
