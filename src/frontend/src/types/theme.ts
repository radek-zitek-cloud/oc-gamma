/**
 * Theme type definitions.
 */

/** Valid theme preference values */
export type ThemePreference = "light" | "dark" | "system";

/** Resolved theme (actual applied theme, never 'system') */
export type ResolvedTheme = "light" | "dark";

/** Theme option with metadata for UI */
export interface ThemeOption {
  value: ThemePreference;
  label: string;
  description: string;
}

/** All available theme options */
export const THEME_OPTIONS: ThemeOption[] = [
  {
    value: "light",
    label: "Light",
    description: "Always use light mode",
  },
  {
    value: "dark",
    label: "Dark",
    description: "Always use dark mode",
  },
  {
    value: "system",
    label: "System",
    description: "Follow system preference",
  },
];
