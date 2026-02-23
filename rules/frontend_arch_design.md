---
title: Frontend Architecture & Design Rules
description: Strict constraints for React, Vite, Tailwind CSS, and shadcn/ui development.
version: 2.1.0
date: 2026-02-23
---

# Frontend Architecture & Design Rules

## 1. Tech Stack & Methodology
* **Framework:** React (Vite).
* **Styling:** Tailwind CSS.
* **Component Library:** shadcn/ui. 
* **Data Fetching:** Use `TanStack Query` (React Query) for all server state and API requests. Do NOT use `useEffect` for data fetching.
* **Client State:** Use `Zustand` for global client state if passing props becomes too deeply nested. Do not use Redux.
* **Rule:** Do not install heavy external component libraries. Generate UI using Tailwind primitives or standard shadcn/ui component patterns (Radix UI under the hood).

## 2. Design Tokens: Trinity Bank Theme
### Typography
* **Primary Font:** Inter (or standard sans-serif system font). Use for all standard UI text.
* **Monospace Font:** JetBrains Mono (or standard mono). Use EXCLUSIVELY in the Status Bar for version numbers and technical data.

### Information Density
* **Density Level:** High (Compact).
* **Spacing Rules:** Favor tight padding (`p-2`, `p-3`, max `p-4` for containers). 
* **Text Sizing:** Use `text-sm` for standard UI elements and `text-xs` for the Status Bar and secondary metadata.

### Semantic Color System (shadcn/ui HSL format)
The color system is derived from Trinity Bank's brand identity: Gold (`#E7CA64`), Thunder Grey (`#231F20`), and White. All colors must be implemented via CSS variables in `globals.css` using HSL values.

**Light Theme:**
* `--background`: `0 0% 100%` (White)
* `--foreground`: `345 6% 13%` (Thunder Grey - `#231F20`)
* `--primary`: `45 73% 65%` (Trinity Gold - `#E7CA64`)
* `--primary-foreground`: `345 6% 13%` (Contrast text for gold buttons)
* `--secondary`: `0 0% 96%` (Very light grey for surfaces)
* `--secondary-foreground`: `345 6% 13%`
* `--muted`: `0 0% 96%`
* `--muted-foreground`: `0 0% 45%`
* `--info`: `214 95% 40%` (Standard clear blue for neutral info)
* `--success`: `142 71% 29%` (Emerald/Green for positive balance/status)
* `--warning`: `38 92% 50%` (Amber for non-blocking alerts)
* `--destructive`: `0 84% 60%` (Red/Rose for errors/delete actions)
* `--border` / `--input` / `--ring`: `0 0% 90%` (Light grey borders)

**Dark Theme (Complementary):**
* `--background`: `345 6% 7%` (Very dark grey/black, darker than Thunder)
* `--foreground`: `0 0% 98%` (Off-white for readability)
* `--primary`: `45 73% 65%` (Trinity Gold - stays consistent for brand identity)
* `--primary-foreground`: `345 6% 7%` (Dark text on gold buttons)
* `--secondary`: `345 6% 13%` (Thunder Grey for elevated surfaces)
* `--secondary-foreground`: `0 0% 98%`
* `--muted`: `345 5% 15%`
* `--muted-foreground`: `0 0% 64%`
* `--info`: `214 95% 60%` (Lighter blue for dark mode contrast)
* `--success`: `142 71% 45%`
* `--warning`: `38 92% 55%`
* `--destructive`: `0 84% 65%`
* `--border` / `--input`: `345 5% 20%` (Subtle dark borders)
* `--ring`: `45 73% 65%` (Gold focus rings)

## 3. Global Layout: The App Shell
The application uses a strict App Shell layout. The viewport (`h-screen` and `w-screen`) is locked (`overflow-hidden` on the `<body>`). **Only the Main Content area is allowed to scroll.**

### Header (Top)
* **Tailwind Constraints:** `fixed top-0 left-0 w-full h-14 z-50 border-b bg-background`.
* **Desktop Content:** * Left: Application Icon + Name.
  * Right: User Profile Menu + Theme Toggle (Light/Dark).
* **Mobile Behavior:** Displays a hamburger menu on the left to toggle the Sidebar Drawer.

### Sidebar (Left)
* **Tailwind Constraints:** `fixed left-0 top-14 bottom-8 z-40 border-r bg-background transition-all duration-300`.
* **State 1 (Expanded):** Fixed width (e.g., `w-64`). Displays full navigation. Active menu items should use a subtle `--primary` (Gold) left-border or background highlight.
* **State 2 (Collapsed):** Narrow width (e.g., `w-16`). Displays only tooltips/icons.
* **Mobile Behavior:** Hidden by default (`hidden md:flex`). Toggled via a shadcn `Sheet` component on small screens.

### Status Bar (Bottom)
* **Tailwind Constraints:** `fixed bottom-0 left-0 w-full h-8 z-50 border-t bg-secondary flex items-center px-4 text-xs font-mono`.
* **Visibility:** Always visible on all screen sizes.
* **Content:** Frontend Version | Backend Version | API Status Indicator (colored dot using `--success` or `--destructive`) | Current Username.

### Main Content Area
* **Tailwind Constraints:** `absolute top-14 bottom-8 right-0 overflow-y-auto bg-background`.
* **Dynamic Width:** Must dynamically calculate width based on the Sidebar's state (`left-64` when expanded, `left-16` when collapsed).

## 4. Logging & Observability (Tool Agnostic)
* **No Bare Logs:** DO NOT use bare `console.log()`, `console.warn()`, or `console.error()` directly in components or business logic.
* **Centralized Logger:** Create a centralized logging utility (e.g., `lib/logger.ts`) that wraps console methods. This allows logs to be easily redirected to external observability tools (like Sentry or Datadog) in the future.
* **Structured Context:** The logger must accept structured metadata (objects) alongside the main message.
* **Correlation IDs:** Every API request made from the frontend (via `fetch` or Axios) must generate and attach a unique UUID as an `X-Correlation-ID` header to allow full-stack tracing.

## 5. Versioning
* **Standard:** Use strict Semantic Versioning (SemVer). The frontend version is completely decoupled from the backend version.
* **Storage:** Track the version in `package.json`.
* **Injection:** Expose the version to the application at build time using Vite's environment variables (e.g., `import.meta.env.VITE_APP_VERSION`).
* **Visibility:** Display this version dynamically in the left side of the App Shell's Status Bar.

## 6. Error Handling & Boundaries
* **React Error Boundaries:** The application must gracefully handle UI crashes using the `react-error-boundary` package. Do not write custom class-based error boundaries.
* **Granularity Pattern:**
  * **Global Boundary:** Wrap the main layout in a Global Error Boundary to catch catastrophic routing or layout failures, displaying a full-page, user-friendly fallback UI.
  * **Local Boundaries:** Wrap isolated, complex features (e.g., data tables, charts, forms) in Local Error Boundaries. If a widget crashes, it must isolate the failure and display a local error state without unmounting the rest of the App Shell.
* **Logging Integration:** Every Error Boundary MUST use the `onError` callback to pass the exact error object and React component stack directly to `lib/logger.ts` for tracing.
* **Fallback UI:** Fallback components must be styled using standard `shadcn/ui` components (e.g., `Alert` or an empty state card) and provide a user-facing "Try Again" reset action where applicable.

## 7. Accessibility (Future)
* Follow WCAG 2.1 AA guidelines for all interactive elements.
* Specific constraints to be defined before first customer-facing release.

## 8. Internationalization (Future)
* i18n framework and locale strategy to be defined before multi-language support is required.