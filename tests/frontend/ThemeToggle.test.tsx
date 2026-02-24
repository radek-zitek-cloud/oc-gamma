/**
 * Tests for ThemeToggle component.
 */

import "@testing-library/jest-dom";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ThemeToggle } from "@/components/ThemeToggle";
import { ThemeProvider } from "@/components/ThemeProvider";

// Mock window.matchMedia
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // Deprecated
    removeListener: vi.fn(), // Deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock the API
vi.mock("@/lib/api", () => ({
  api: {
    patch: vi.fn().mockResolvedValue({ data: {} }),
  },
}));

// Mock the auth store
vi.mock("@/store/authStore", () => ({
  useAuthStore: vi.fn((selector) =>
    selector({
      isAuthenticated: false,
      user: null,
    })
  ),
}));

// Mock TanStack Query
vi.mock("@tanstack/react-query", () => ({
  useMutation: vi.fn(() => ({
    mutate: vi.fn(),
    isPending: false,
  })),
  useQueryClient: vi.fn(() => ({
    setQueryData: vi.fn(),
  })),
}));

describe("ThemeToggle", () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Reset document class
    document.documentElement.classList.remove("dark");
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders the theme toggle button", () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    expect(screen.getByTestId("theme-toggle-button")).toBeInTheDocument();
  });

  it("opens dropdown menu when clicked", async () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const toggleButton = screen.getByTestId("theme-toggle-button");
    await userEvent.click(toggleButton);

    // Check that theme options are displayed
    expect(screen.getByTestId("theme-option-light")).toBeInTheDocument();
    expect(screen.getByTestId("theme-option-dark")).toBeInTheDocument();
    expect(screen.getByTestId("theme-option-system")).toBeInTheDocument();
  });

  it("shows checkmark for current theme selection", async () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const toggleButton = screen.getByTestId("theme-toggle-button");
    await userEvent.click(toggleButton);

    // By default, system theme should be selected
    await waitFor(() => {
      expect(screen.getByTestId("theme-check-system")).toBeInTheDocument();
    });
  });

  it("changes theme when option is clicked", async () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    // Open dropdown
    const toggleButton = screen.getByTestId("theme-toggle-button");
    await userEvent.click(toggleButton);

    // Click dark theme option
    const darkOption = screen.getByTestId("theme-option-dark");
    await userEvent.click(darkOption);

    // Verify localStorage was updated
    await waitFor(() => {
      expect(localStorage.getItem("theme-preference")).toBe("dark");
    });
  });

  it("applies dark class to document when dark theme is selected", async () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    // Open dropdown
    const toggleButton = screen.getByTestId("theme-toggle-button");
    await userEvent.click(toggleButton);

    // Click dark theme option
    const darkOption = screen.getByTestId("theme-option-dark");
    await userEvent.click(darkOption);

    // Verify dark class is applied
    await waitFor(() => {
      expect(document.documentElement.classList.contains("dark")).toBe(true);
    });
  });

  it("removes dark class when light theme is selected", async () => {
    // Start with dark theme
    document.documentElement.classList.add("dark");
    localStorage.setItem("theme-preference", "dark");

    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    // Open dropdown
    const toggleButton = screen.getByTestId("theme-toggle-button");
    await userEvent.click(toggleButton);

    // Click light theme option
    const lightOption = screen.getByTestId("theme-option-light");
    await userEvent.click(lightOption);

    // Verify dark class is removed
    await waitFor(() => {
      expect(document.documentElement.classList.contains("dark")).toBe(false);
    });
  });
});
