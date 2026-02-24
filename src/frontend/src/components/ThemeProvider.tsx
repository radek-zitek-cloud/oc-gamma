/**
 * Theme Provider component.
 * Initializes theme on mount and handles system preference changes.
 */

import { useEffect } from "react";

import { useThemeStore } from "@/store/themeStore";
import { logger } from "@/lib/logger";

interface ThemeProviderProps {
  children: React.ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const initializeTheme = useThemeStore((state) => state.initializeTheme);
  const cleanup = useThemeStore((state) => state.cleanup);
  const theme = useThemeStore((state) => state.theme);

  // Initialize theme on mount
  useEffect(() => {
    initializeTheme();
    logger.debug("ThemeProvider mounted, theme initialized");
    
    // Cleanup on unmount
    return () => {
      cleanup();
    };
  }, [initializeTheme, cleanup]);

  // Re-initialize when theme changes to/from system
  useEffect(() => {
    if (theme === "system") {
      initializeTheme();
    }
  }, [theme, initializeTheme]);

  return <>{children}</>;
}
