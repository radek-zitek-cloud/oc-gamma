/**
 * Theme Toggle component.
 * Dropdown menu for selecting light/dark/system theme.
 */

import { Check, Monitor, Moon, Sun } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useThemeStore } from "@/store/themeStore";
import { THEME_OPTIONS, type ThemePreference } from "@/types/theme";
import { useUpdateThemePreference } from "@/hooks/useTheme";
import { useAuthStore } from "@/store/authStore";

const themeIcons = {
  light: Sun,
  dark: Moon,
  system: Monitor,
};

export function ThemeToggle() {
  const theme = useThemeStore((state) => state.theme);
  const setTheme = useThemeStore((state) => state.setTheme);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const updateThemeMutation = useUpdateThemePreference();

  const handleThemeChange = (newTheme: ThemePreference) => {
    // Update local state immediately for responsiveness
    setTheme(newTheme);

    // Sync with server if authenticated
    if (isAuthenticated) {
      updateThemeMutation.mutate(newTheme);
    }
  };

  const CurrentIcon = themeIcons[theme];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9"
          aria-label="Toggle theme"
          data-testid="theme-toggle-button"
        >
          <CurrentIcon className="h-4 w-4" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        {THEME_OPTIONS.map((option, index) => {
          const Icon = themeIcons[option.value];
          const isActive = theme === option.value;

          return (
            <div key={option.value}>
              {index > 0 && <DropdownMenuSeparator />}
              <DropdownMenuItem
                onClick={() => handleThemeChange(option.value)}
                className="flex items-center justify-between cursor-pointer"
                data-testid={`theme-option-${option.value}`}
              >
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4" />
                  <span>{option.label}</span>
                </div>
                {isActive && (
                  <Check className="h-4 w-4 text-primary" data-testid={`theme-check-${option.value}`} />
                )}
              </DropdownMenuItem>
            </div>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
