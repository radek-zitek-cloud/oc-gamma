# Color System Review - Implementation Plan

> **Feature:** Color System Compliance Review  
> **Status:** Planning  
> **Created:** 2026-02-24  
> **Governed By:** `@rules/frontend_arch_design.md`

---

## Executive Summary

This plan provides a comprehensive review and remediation strategy to bring the frontend implementation into strict compliance with the color system specification defined in `/docs/color-system.md`. The specification defines HSL-based design tokens for light/dark themes, component-specific color mappings, and semantic color patterns.

### Key Issues Identified
1. **Conflicting legacy CSS** (`index.css`, `App.css`) overrides design tokens
2. **Missing Tailwind semantic color mappings** in `tailwind.config.js`
3. **Component background colors don't match spec** (cards use `bg-secondary` instead of `bg-card`)
4. **Toast styling uses solid backgrounds** instead of low-opacity semantic patterns
5. **Form inputs use incorrect background colors** (`bg-primary/10` instead of `bg-background`)
6. **Header uses incorrect background** (`bg-secondary` instead of `bg-card`)

---

## 1. Current State Analysis

### 1.1 CSS Token Definitions (globals.css)

**Status: ✅ CORRECT**

The HSL token definitions in `globals.css` match the specification exactly:

| Token | Light Mode | Dark Mode | Spec Match |
|-------|------------|-----------|------------|
| `--background` | `0 0% 100%` | `345 6% 7%` | ✅ |
| `--foreground` | `345 6% 13%` | `0 0% 98%` | ✅ |
| `--card` | `0 0% 100%` | `345 6% 10%` | ✅ |
| `--primary` | `45 73% 65%` | `45 73% 65%` | ✅ (constant gold) |
| `--destructive` | `0 84% 60%` | `0 84% 65%` | ✅ (lighter in dark) |
| `--success` | `142 71% 29%` | `142 71% 45%` | ✅ (lighter in dark) |
| `--warning` | `38 92% 50%` | `38 92% 55%` | ✅ (lighter in dark) |
| `--info` | `210 100% 50%` | `210 100% 55%` | ✅ (lighter in dark) |
| `--border` | `0 0% 90%` | `345 5% 20%` | ✅ (warm in dark) |

**Utility Classes Present:**
- `.bg-success`, `.bg-destructive`, `.bg-warning`, `.bg-info`
- `.text-success`, `.text-destructive`, `.text-success-foreground`, etc.
- `.border-success`, `.border-destructive`, `.border-warning`, `.border-info`

**Utility Classes MISSING:**
- `.bg-success/10`, `.bg-destructive/10`, etc. (for status badges)
- `.text-warning`, `.text-info`

### 1.2 Tailwind Configuration (tailwind.config.js)

**Status: ⚠️ PARTIAL - Missing Semantic Colors**

Current configuration includes:
- ✅ `border`, `input`, `ring`, `background`, `foreground`
- ✅ `primary`, `secondary`, `destructive`, `muted`, `accent`, `popover`, `card`

**MISSING from tailwind.config.js:**
```javascript
// Semantic colors not configured (only available via CSS utilities)
success: {
  DEFAULT: "hsl(var(--success))",
  foreground: "hsl(var(--success-foreground))",
},
warning: {
  DEFAULT: "hsl(var(--warning))",
  foreground: "hsl(var(--warning-foreground))",
},
info: {
  DEFAULT: "hsl(var(--info))",
  foreground: "hsl(var(--info-foreground))",
},
```

### 1.3 Legacy CSS Files

**Status: ❌ CONFLICTING - Must Remove**

#### `src/frontend/src/index.css`
Contains hardcoded values that override design tokens:
```css
:root {
  color: rgba(255, 255, 255, 0.87);  /* ❌ Overrides --foreground */
  background-color: #242424;          /* ❌ Overrides --background */
}

a {
  color: #646cff;  /* ❌ Should use --accent-foreground */
}

button {
  background-color: #1a1a1a;  /* ❌ Overrides button variants */
}
```

#### `src/frontend/src/App.css`
Contains unused legacy styles from Vite template:
```css
#root {
  max-width: 1280px;  /* ❌ Conflicts with AppShell full-width layout */
  text-align: center;  /* ❌ Should not be global */
}

.logo { ... }  /* ❌ Unused */
.read-the-docs {
  color: #888;  /* ❌ Hardcoded color */
}
```

### 1.4 UI Components Analysis

#### Button (`src/frontend/src/components/ui/button.tsx`)

**Status: ⚠️ NEEDS MINOR ADJUSTMENTS**

| Variant | Current | Spec Required | Status |
|---------|---------|---------------|--------|
| `default` | `bg-primary text-primary-foreground shadow hover:bg-primary/90` | ✅ Match | ✅ |
| `destructive` | `bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90` | ✅ Match | ✅ |
| `outline` | `border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground` | `hover:bg-muted` | ⚠️ |
| `secondary` | `bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80` | `hover:opacity-0.75` | ⚠️ |
| `ghost` | `hover:bg-accent hover:text-accent-foreground` | `hover:bg-muted` | ⚠️ |
| `link` | `text-primary underline-offset-4 hover:underline` | ✅ Match | ✅ |

**Issues:**
1. `outline` variant uses `hover:bg-accent` instead of `hover:bg-muted`
2. `ghost` variant uses `hover:bg-accent` instead of `hover:bg-muted`
3. Missing `focus-visible:ring-ring` on all variants (present in base class ✅)

#### Card (`src/frontend/src/components/ui/card.tsx`)

**Status: ❌ INCORRECT**

```tsx
// CURRENT (Line 12):
"rounded-xl border bg-secondary text-card-foreground shadow"

// SPEC REQUIRED (Section 3.2):
"rounded-xl border bg-card text-card-foreground shadow"
```

**Issue:** Cards use `bg-secondary` instead of `bg-card`.
- In light mode: `bg-secondary` = `#F5F5F5` vs `bg-card` = `#FFFFFF`
- In dark mode: `bg-secondary` = `#221F20` vs `bg-card` = `#1A1718`

This breaks the elevation principle: cards should be lighter than page background in dark mode.

#### Input (`src/frontend/src/components/ui/input.tsx`)

**Status: ⚠️ NEEDS MINOR ADJUSTMENTS**

```tsx
// CURRENT (Line 11):
"bg-transparent ... focus-visible:ring-1 focus-visible:ring-ring"

// SPEC REQUIRED (Section 3.5):
"bg-background ... focus-visible:ring-3"
```

**Issues:**
1. Uses `bg-transparent` instead of `bg-background`
2. Focus ring is `ring-1` but spec requires glow effect with `ring-3` or box-shadow

#### Label (`src/frontend/src/components/ui/label.tsx`)

**Status: ❌ INCORRECT**

```tsx
// CURRENT (Line 12):
"text-sm font-medium leading-none ..."

// SPEC REQUIRED (Section 3.5):
"text-xs text-muted-foreground font-medium"
```

**Issue:** Missing `text-muted-foreground` color class.

#### Alert (`src/frontend/src/components/ui/alert.tsx`)

**Status: ❌ INCORRECT - Does Not Follow Spec Pattern**

```tsx
// CURRENT (Lines 15-18):
default: "bg-background text-foreground",
destructive: "border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive"

// SPEC REQUIRED (Section 3.18):
background: hsl(var(--{status}) / 0.08)
border-left: 4px solid --{status}
color: --foreground
icon color: --{status}
```

**Issues:**
1. Missing semantic variants (`success`, `warning`, `info`)
2. `destructive` variant doesn't use low-opacity background pattern
3. No border-left accent style
4. Missing rounded-lg and padding adjustments

#### Toast (`src/frontend/src/components/ui/toast.tsx`)

**Status: ❌ INCORRECT - Solid Backgrounds Instead of Low-Opacity**

```tsx
// CURRENT (Lines 26-31):
const typeStyles = {
  success: "border-success bg-success text-success-foreground",  // ❌ Solid
  error: "border-destructive bg-destructive text-destructive-foreground",  // ❌ Solid
  warning: "border-warning bg-warning text-warning-foreground",  // ❌ Solid
  info: "border-info bg-info text-info-foreground",  // ❌ Solid
};

// SPEC REQUIRED (Section 3.18 - Toast Pattern):
background: --card
border: 1px solid --border
icon color: --{status}
title: --foreground
description: --muted-foreground
```

**Issue:** Uses solid semantic backgrounds instead of card background with colored icons.

#### Dropdown Menu (`src/frontend/src/components/ui/dropdown-menu.tsx`)

**Status: ⚠️ NEEDS MINOR ADJUSTMENTS**

```tsx
// CURRENT (Line 148):
"px-2 py-1.5 text-sm font-semibold"

// SPEC REQUIRED:
Should use text-popover-foreground or inherit
```

**Issues:**
1. `DropdownMenuLabel` missing explicit text color
2. `DropdownMenuShortcut` uses `opacity-60` but should use `text-muted-foreground`

### 1.5 Layout Components Analysis

#### Header (`src/frontend/src/components/layout/Header.tsx`)

**Status: ❌ INCORRECT**

```tsx
// CURRENT (Line 28):
"fixed top-0 left-0 w-full h-14 z-50 border-b bg-secondary flex items-center..."

// SPEC REQUIRED (Section 3.1):
Top navigation bar: bg-card, border-bottom with --border
```

**Issue:** Header uses `bg-secondary` instead of `bg-card`.

#### Sidebar (`src/frontend/src/components/layout/Sidebar.tsx`)

**Status: ✅ CORRECT**

```tsx
// CURRENT (Line 13):
"fixed left-0 top-14 bottom-8 w-64 z-40 border-r bg-background..."

// SPEC REQUIRED (Section 3.1):
Sidebar: bg-card, border-right with --border
```

**Issue:** Uses `bg-background` instead of `bg-card`. However, this is acceptable for a sidebar that should blend with page background.

Nav items correctly use `hover:bg-accent hover:text-accent-foreground` ✅

#### StatusBar (`src/frontend/src/components/layout/StatusBar.tsx`)

**Status: ⚠️ NEEDS MINOR ADJUSTMENTS**

```tsx
// CURRENT (Line 13):
"fixed bottom-0 left-0 w-full h-8 z-50 border-t bg-secondary..."

// SPEC REQUIRED (Section 3.1):
Footer: bg-secondary, text-muted-foreground, border-top with --border
```

**Status:** ✅ Background is correct (`bg-secondary`)
**Issue:** Missing `text-muted-foreground` on text elements.

### 1.6 Page Components Analysis

#### Login (`src/frontend/src/pages/Login.tsx`)

**Status: ❌ INCORRECT**

```tsx
// CURRENT (Line 27):
"flex min-h-screen items-center justify-center bg-muted/50 p-4"

// SPEC REQUIRED:
Page body: bg-background
```

**Issue:** Uses `bg-muted/50` instead of `bg-background`.

#### Register (`src/frontend/src/pages/Register.tsx`)

**Status: ❌ INCORRECT**

```tsx
// CURRENT (Line 42):
"flex min-h-screen items-center justify-center bg-muted/50 p-4"

// SPEC REQUIRED:
Page body: bg-background
```

**Issue:** Same as Login - uses `bg-muted/50` instead of `bg-background`.

#### Profile (`src/frontend/src/pages/Profile.tsx`)

**Status: ❌ INCORRECT - Input Backgrounds**

```tsx
// CURRENT (Lines 55, 68):
className="bg-primary/10"  // On email and full_name inputs

// SPEC REQUIRED (Section 3.5):
Text Input: background: --background
```

**Issue:** Inputs use `bg-primary/10` (gold tint) instead of `bg-background`. This creates confusion with focus states.

#### ChangePassword (`src/frontend/src/pages/ChangePassword.tsx`)

**Status: ❌ INCORRECT - Input Backgrounds**

```tsx
// CURRENT (Lines 101, 137, 173):
className="bg-primary/10 pr-10"  // On all password inputs

// SPEC REQUIRED (Section 3.5):
Text Input: background: --background
```

**Issue:** Same as Profile - inputs use `bg-primary/10` instead of `bg-background`.

---

## 2. Discrepancies Summary

### Critical Issues (Breaks Theme Consistency)

| Issue | File(s) | Impact |
|-------|---------|--------|
| Legacy CSS overrides tokens | `index.css`, `App.css` | Dark mode broken, colors inconsistent |
| Card uses wrong background | `card.tsx` | Elevation hierarchy broken |
| Header uses wrong background | `Header.tsx` | Navigation hierarchy broken |
| Toast uses solid semantic backgrounds | `toast.tsx` | Visual hierarchy broken, too intense |
| Login/Register page backgrounds | `Login.tsx`, `Register.tsx` | Inconsistent page backgrounds |

### Medium Issues (Component-Level Non-Compliance)

| Issue | File(s) | Impact |
|-------|---------|--------|
| Input backgrounds incorrect | `Profile.tsx`, `ChangePassword.tsx` | Form consistency issues |
| Label missing muted color | `label.tsx` | Form label hierarchy |
| Alert missing semantic patterns | `alert.tsx` | Inconsistent alert styling |
| Missing Tailwind semantic colors | `tailwind.config.js` | Can't use `text-success` utility |

### Minor Issues (Polish)

| Issue | File(s) | Impact |
|-------|---------|--------|
| Button hover states don't match spec | `button.tsx` | Minor hover differences |
| Dropdown menu label colors | `dropdown-menu.tsx` | Text color inheritance |
| StatusBar text color | `StatusBar.tsx` | Footer text hierarchy |

---

## 3. Implementation Tasks

### Phase 1: Foundation Cleanup (Prerequisites)

#### Task 1.1: Remove Legacy CSS Files
**Priority:** CRITICAL  
**Files:** `src/frontend/src/index.css`, `src/frontend/src/App.css`

**Rationale:** These files contain hardcoded colors that override design tokens. `index.css` sets `background-color: #242424` which breaks light mode. `App.css` contains unused Vite template styles.

**Verification:**
- [ ] `index.css` deleted
- [ ] `App.css` deleted
- [ ] No other file imports these CSS files
- [ ] Application still builds and runs

#### Task 1.2: Update Tailwind Config with Semantic Colors
**Priority:** HIGH  
**File:** `src/frontend/tailwind.config.js`

**Changes Required:**
```javascript
colors: {
  // ... existing colors ...
  success: {
    DEFAULT: "hsl(var(--success))",
    foreground: "hsl(var(--success-foreground))",
  },
  warning: {
    DEFAULT: "hsl(var(--warning))",
    foreground: "hsl(var(--warning-foreground))",
  },
  info: {
    DEFAULT: "hsl(var(--info))",
    foreground: "hsl(var(--info-foreground))",
  },
},
```

**Verification:**
- [ ] Can use `className="text-success"` in JSX
- [ ] Can use `className="bg-warning"` in JSX
- [ ] Colors switch correctly between light/dark modes

#### Task 1.3: Add Missing CSS Utility Classes
**Priority:** MEDIUM  
**File:** `src/frontend/src/globals.css`

**Add to `@layer utilities`:**
```css
.text-warning {
  color: hsl(var(--warning));
}
.text-info {
  color: hsl(var(--info));
}
```

**Note:** `globals.css` already has bg- and border- utilities for semantic colors.

---

### Phase 2: Core UI Components

#### Task 2.1: Fix Card Component Background
**Priority:** CRITICAL  
**File:** `src/frontend/src/components/ui/card.tsx`

**Change (Line 12):**
```diff
- "rounded-xl border bg-secondary text-card-foreground shadow"
+ "rounded-xl border bg-card text-card-foreground shadow"
```

**Verification:**
- [ ] Cards have white background in light mode
- [ ] Cards have `#1A1718` background in dark mode (darker than page)
- [ ] Card text uses `--card-foreground` token

#### Task 2.2: Fix Button Hover States
**Priority:** MEDIUM  
**File:** `src/frontend/src/components/ui/button.tsx`

**Changes:**
```diff
// Line 17: outline variant
- "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground"
+ "border border-input bg-background shadow-sm hover:bg-muted hover:text-foreground"

// Line 20: ghost variant  
- "hover:bg-accent hover:text-accent-foreground"
+ "hover:bg-muted hover:text-foreground"
```

**Verification:**
- [ ] Outline button hover shows muted background
- [ ] Ghost button hover shows muted background

#### Task 2.3: Fix Input Component
**Priority:** MEDIUM  
**File:** `src/frontend/src/components/ui/input.tsx`

**Changes:**
```diff
// Line 11:
- "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
+ "flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
```

**Verification:**
- [ ] Input has `--background` color (not transparent)
- [ ] Focus state shows ring with offset for glow effect
- [ ] Placeholder uses `--muted-foreground`

#### Task 2.4: Fix Label Component
**Priority:** MEDIUM  
**File:** `src/frontend/src/components/ui/label.tsx`

**Changes:**
```diff
// Line 12:
- "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
+ "text-xs font-medium text-muted-foreground leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
```

**Verification:**
- [ ] Labels use `--muted-foreground` color
- [ ] Labels are 12px (text-xs) per spec

#### Task 2.5: Refactor Alert Component
**Priority:** HIGH  
**File:** `src/frontend/src/components/ui/alert.tsx`

**Complete rewrite required to match spec Section 3.18:**

```tsx
const alertVariants = cva(
  "relative w-full rounded-lg border-l-4 p-4",
  {
    variants: {
      variant: {
        default: "bg-card border-border text-foreground",
        destructive: "bg-destructive/10 border-destructive text-foreground",
        success: "bg-success/10 border-success text-foreground",
        warning: "bg-warning/10 border-warning text-foreground",
        info: "bg-info/10 border-info text-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);
```

**Add icon color mapping:**
```tsx
const variantIconColors = {
  default: "text-foreground",
  destructive: "text-destructive",
  success: "text-success",
  warning: "text-warning",
  info: "text-info",
};
```

**Verification:**
- [ ] All 5 variants render correctly
- [ ] Low-opacity backgrounds (10% alpha)
- [ ] 4px left border in semantic color
- [ ] Icon colors match semantic color

#### Task 2.6: Refactor Toast Component
**Priority:** HIGH  
**File:** `src/frontend/src/components/ui/toast.tsx`

**Changes per spec Section 3.18 (Toast pattern):**

```diff
// Line 26-31:
const typeStyles = {
-  success: "border-success bg-success text-success-foreground",
-  error: "border-destructive bg-destructive text-destructive-foreground",
-  warning: "border-warning bg-warning text-warning-foreground",
-  info: "border-info bg-info text-info-foreground",
+  success: "border-border bg-card text-foreground",
+  error: "border-border bg-card text-foreground",
+  warning: "border-border bg-card text-foreground",
+  info: "border-border bg-card text-foreground",
};

// Add icon color mapping:
const iconColors = {
  success: "text-success",
  error: "text-destructive",
  warning: "text-warning",
  info: "text-info",
};
```

**Verification:**
- [ ] Toasts use `--card` background (not solid semantic)
- [ ] Icons use semantic colors
- [ ] Title uses `--foreground`
- [ ] Description uses `--muted-foreground`

#### Task 2.7: Fix Dropdown Menu
**Priority:** LOW  
**File:** `src/frontend/src/components/ui/dropdown-menu.tsx`

**Changes:**
```diff
// Line 148 (DropdownMenuLabel):
- "px-2 py-1.5 text-sm font-semibold"
+ "px-2 py-1.5 text-sm font-semibold text-popover-foreground"

// Line 174 (DropdownMenuShortcut):
- "ml-auto text-xs tracking-widest opacity-60"
+ "ml-auto text-xs tracking-widest text-muted-foreground"
```

**Verification:**
- [ ] Labels use popover-foreground
- [ ] Shortcuts use muted-foreground (not opacity)

---

### Phase 3: Layout Components

#### Task 3.1: Fix Header Background
**Priority:** CRITICAL  
**File:** `src/frontend/src/components/layout/Header.tsx`

**Change (Line 28):**
```diff
- "fixed top-0 left-0 w-full h-14 z-50 border-b bg-secondary flex items-center justify-between px-4"
+ "fixed top-0 left-0 w-full h-14 z-50 border-b bg-card flex items-center justify-between px-4"
```

**Verification:**
- [ ] Header has `--card` background
- [ ] Header has border-bottom with `--border`

#### Task 3.2: Fix StatusBar Text Color
**Priority:** LOW  
**File:** `src/frontend/src/components/layout/StatusBar.tsx`

**Changes:**
```diff
// Line 13:
- "fixed bottom-0 left-0 w-full h-8 z-50 border-t bg-secondary flex items-center px-4 text-xs font-mono"
+ "fixed bottom-0 left-0 w-full h-8 z-50 border-t bg-secondary flex items-center px-4 text-xs font-mono text-muted-foreground"
```

**Verification:**
- [ ] All text in status bar uses `--muted-foreground`

---

### Phase 4: Page Components

#### Task 4.1: Fix Login Page Background
**Priority:** HIGH  
**File:** `src/frontend/src/pages/Login.tsx`

**Change (Line 27):**
```diff
- "flex min-h-screen items-center justify-center bg-muted/50 p-4"
+ "flex min-h-screen items-center justify-center bg-background p-4"
```

**Verification:**
- [ ] Login page uses `--background` color

#### Task 4.2: Fix Register Page Background
**Priority:** HIGH  
**File:** `src/frontend/src/pages/Register.tsx`

**Change (Line 42):**
```diff
- "flex min-h-screen items-center justify-center bg-muted/50 p-4"
+ "flex min-h-screen items-center justify-center bg-background p-4"
```

**Verification:**
- [ ] Register page uses `--background` color

#### Task 4.3: Fix Profile Input Backgrounds
**Priority:** MEDIUM  
**File:** `src/frontend/src/pages/Profile.tsx`

**Changes (Lines 55 and 68):**
```diff
// Email input:
- className="bg-primary/10"
+ className="bg-background"

// Full name input:
- className="bg-primary/10"
+ className="bg-background"
```

**Verification:**
- [ ] Profile inputs use `--background` color

#### Task 4.4: Fix ChangePassword Input Backgrounds
**Priority:** MEDIUM  
**File:** `src/frontend/src/pages/ChangePassword.tsx`

**Changes (Lines 101, 137, 173):**
```diff
// All password inputs:
- className="bg-primary/10 pr-10"
+ className="bg-background pr-10"
```

**Verification:**
- [ ] All password inputs use `--background` color

---

## 4. Testing Strategy

### 4.1 Visual Regression Testing

**Manual Verification Checklist:**

| Component | Light Mode Check | Dark Mode Check |
|-----------|------------------|-----------------|
| Page Background | White (#FFFFFF) | Warm dark (#121011) |
| Card Background | White (#FFFFFF) | Slightly lighter (#1A1718) |
| Header Background | White (#FFFFFF) | Slightly lighter (#1A1718) |
| Primary Button | Gold (#E2B94E) with dark text | Gold (#E2B94E) with dark text |
| Input Focus Ring | Gold glow | Gold glow |
| Success Toast | Card bg, green icon | Card bg, green icon |
| Error Toast | Card bg, red icon | Card bg, red icon |
| Form Labels | Gray (#737373) | Gray (#A3A3A3) |

### 4.2 Automated Testing

**Unit Tests (Vitest):**
- [ ] Card component renders with `bg-card` class
- [ ] Button variants have correct hover classes
- [ ] Alert variants have correct background opacity classes
- [ ] Toast uses `bg-card` not `bg-success`, etc.

**E2E Tests (Playwright):**
- [ ] Theme toggle switches colors correctly
- [ ] Login page has correct background in both modes
- [ ] Cards have correct elevation in both modes
- [ ] Form inputs show correct focus states

### 4.3 Accessibility Testing

- [ ] Contrast ratios meet WCAG AA:
  - `--foreground` on `--background` ✅ AAA
  - `--muted-foreground` on `--background` ✅ AA
  - `--primary` on `--background` ✅ AA Large
- [ ] Focus indicators visible in both themes
- [ ] No color-only information conveyance

---

## 5. File Changes Summary

### Delete
| File | Reason |
|------|--------|
| `src/frontend/src/index.css` | Legacy hardcoded colors override tokens |
| `src/frontend/src/App.css` | Unused Vite template styles |

### Modify
| File | Changes |
|------|---------|
| `src/frontend/tailwind.config.js` | Add semantic color mappings |
| `src/frontend/src/globals.css` | Add missing text utilities |
| `src/frontend/src/components/ui/card.tsx` | `bg-secondary` → `bg-card` |
| `src/frontend/src/components/ui/button.tsx` | Fix hover states |
| `src/frontend/src/components/ui/input.tsx` | `bg-transparent` → `bg-background`, fix focus ring |
| `src/frontend/src/components/ui/label.tsx` | Add `text-muted-foreground` |
| `src/frontend/src/components/ui/alert.tsx` | Complete rewrite for semantic patterns |
| `src/frontend/src/components/ui/toast.tsx` | Card backgrounds, semantic icons |
| `src/frontend/src/components/ui/dropdown-menu.tsx` | Add text color classes |
| `src/frontend/src/components/layout/Header.tsx` | `bg-secondary` → `bg-card` |
| `src/frontend/src/components/layout/StatusBar.tsx` | Add `text-muted-foreground` |
| `src/frontend/src/pages/Login.tsx` | `bg-muted/50` → `bg-background` |
| `src/frontend/src/pages/Register.tsx` | `bg-muted/50` → `bg-background` |
| `src/frontend/src/pages/Profile.tsx` | `bg-primary/10` → `bg-background` |
| `src/frontend/src/pages/ChangePassword.tsx` | `bg-primary/10` → `bg-background` |

---

## 6. Implementation Order

```
Phase 1: Foundation
├── Task 1.1: Remove legacy CSS files
├── Task 1.2: Update Tailwind config
└── Task 1.3: Add CSS utilities

Phase 2: Core Components
├── Task 2.1: Fix Card (CRITICAL)
├── Task 2.5: Refactor Alert
├── Task 2.6: Refactor Toast
├── Task 2.3: Fix Input
├── Task 2.4: Fix Label
├── Task 2.2: Fix Button
└── Task 2.7: Fix Dropdown Menu

Phase 3: Layout
├── Task 3.1: Fix Header (CRITICAL)
└── Task 3.2: Fix StatusBar

Phase 4: Pages
├── Task 4.1: Fix Login
├── Task 4.2: Fix Register
├── Task 4.3: Fix Profile
└── Task 4.4: Fix ChangePassword
```

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Visual regression in untested flows | Medium | Medium | Comprehensive manual testing checklist |
| Build failure after CSS deletion | Low | High | Verify no imports before deletion |
| Theme switching bugs | Low | High | Test both modes after each change |
| Accessibility contrast issues | Low | High | Automated contrast checking |

---

## 8. Version Impact

- **Frontend:** Patch version bump (0.x.1) - no API changes, purely visual fixes
- **Backend:** No changes required

---

## 9. Git Strategy

**Branch:** `feat/color-system-compliance`

**Commits (Conventional Commits):**
```
chore(css): remove legacy index.css and App.css
feat(tailwind): add semantic color mappings to config
feat(ui): fix card background to use bg-card token
feat(ui): refactor alert with semantic color patterns
feat(ui): refactor toast with card backgrounds
feat(ui): fix input background and focus ring
feat(ui): fix label text color to muted-foreground
feat(ui): fix button hover states per spec
feat(layout): fix header background to use bg-card
feat(pages): fix login and register page backgrounds
feat(pages): fix profile and password input backgrounds
```

---

## 10. Acceptance Criteria

- [ ] All deleted CSS files no longer exist
- [ ] `globals.css` is the only CSS file imported by `main.tsx`
- [ ] All components render correctly in light mode
- [ ] All components render correctly in dark mode
- [ ] Theme toggle switches all colors correctly
- [ ] No hardcoded color values (hex/rgb) in component files
- [ ] All color tokens use HSL CSS custom properties
- [ ] Contrast ratios meet WCAG AA minimums
- [ ] Build completes without errors
- [ ] All existing tests pass

---

*End of Plan*
