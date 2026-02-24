/**
 * Theme state management using Zustand.
 * Handles theme preference, system detection, and DOM updates.
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";

import { logger } from "@/lib/logger";
import type { ResolvedTheme, ThemePreference } from "@/types/theme";

interface ThemeState {
  /** User's theme preference (may be 'system') */
  theme: ThemePreference;
  /** Actual applied theme (never 'system') */
  resolvedTheme: ResolvedTheme;
  /** System preference media query */
  systemMediaQuery: MediaQueryList | null;
  /** Handler reference for cleanup */
  systemChangeHandler: ((e: MediaQueryListEvent) => void) | null;
  /** Set theme preference */
  setTheme: (theme: ThemePreference) => void;
  /** Initialize theme from storage/system */
  initializeTheme: () => void;
  /** Cleanup system preference listener */
  cleanup: () => void;
}

const STORAGE_KEY = "theme-preference";

/**
 * Get the initial theme from localStorage or default to 'system'.
 */
function getInitialTheme(): ThemePreference {
  if (typeof window === "undefined") return "system";
  
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "light" || stored === "dark" || stored === "system") {
    return stored;
  }
  return "system";
}

/**
 * Get the current system theme preference.
 */
function getSystemTheme(): ResolvedTheme {
  if (typeof window === "undefined") return "light";
  
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

/**
 * Resolve the actual theme to apply based on preference.
 */
function resolveTheme(preference: ThemePreference): ResolvedTheme {
  if (preference === "system") {
    return getSystemTheme();
  }
  return preference;
}

/**
 * Apply the theme to the DOM.
 */
function applyThemeToDOM(theme: ResolvedTheme): void {
  if (typeof document === "undefined") return;
  
  const root = document.documentElement;
  
  if (theme === "dark") {
    root.classList.add("dark");
  } else {
    root.classList.remove("dark");
  }
  
  logger.debug("Theme applied to DOM", { theme });
}

/**
 * Store theme preference in localStorage.
 */
function storeThemePreference(theme: ThemePreference): void {
  if (typeof localStorage === "undefined") return;
  localStorage.setItem(STORAGE_KEY, theme);
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: "system",
      resolvedTheme: "light",
      systemMediaQuery: null,
      systemChangeHandler: null,

      setTheme: (theme) => {
        const resolved = resolveTheme(theme);
        
        // Update state
        set({
          theme,
          resolvedTheme: resolved,
        });
        
        // Apply to DOM
        applyThemeToDOM(resolved);
        
        // Store preference
        storeThemePreference(theme);
        
        // Setup or cleanup system preference listener
        const state = get();
        if (theme === "system") {
          state.initializeTheme();
        } else {
          state.cleanup();
        }
        
        logger.info("Theme preference changed", { theme, resolved });
      },

      initializeTheme: () => {
        if (typeof window === "undefined") return;
        
        const theme = getInitialTheme();
        const resolved = resolveTheme(theme);
        
        // Apply initial theme
        applyThemeToDOM(resolved);
        
        // Setup system preference listener if needed
        if (theme === "system") {
          const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
          
          const handleChange = (e: MediaQueryListEvent) => {
            const newResolved: ResolvedTheme = e.matches ? "dark" : "light";
            set({ resolvedTheme: newResolved });
            applyThemeToDOM(newResolved);
            logger.debug("System theme preference changed", { theme: newResolved });
          };
          
          mediaQuery.addEventListener("change", handleChange);
          set({ 
            systemMediaQuery: mediaQuery,
            systemChangeHandler: handleChange,
          });
        }
        
        set({
          theme,
          resolvedTheme: resolved,
        });
        
        logger.debug("Theme initialized", { theme, resolved });
      },

      cleanup: () => {
        const { systemMediaQuery, systemChangeHandler } = get();
        if (systemMediaQuery && systemChangeHandler) {
          // Properly remove the event listener using the stored handler reference
          systemMediaQuery.removeEventListener("change", systemChangeHandler);
          set({ 
            systemMediaQuery: null,
            systemChangeHandler: null,
          });
          logger.debug("System preference listener removed");
        }
      },
    }),
    {
      name: "theme-storage",
      partialize: (state) => ({ theme: state.theme }),
    }
  )
);
