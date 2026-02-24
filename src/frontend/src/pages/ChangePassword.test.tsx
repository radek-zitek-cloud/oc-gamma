/**
 * Tests for ChangePassword page.
 * Following TDD: Red-Green-Refactor
 */

import "@testing-library/jest-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ChangePassword } from "./ChangePassword";

// Mock the logger
vi.mock("@/lib/logger", () => ({
  logger: {
    error: vi.fn(),
    info: vi.fn(),
  },
}));

// Mock the auth hooks
const mockMutateAsync = vi.fn();
vi.mock("@/hooks/useAuth", () => ({
  useChangePassword: () => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  }),
}));

describe("ChangePassword", () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ChangePassword />
        </BrowserRouter>
      </QueryClientProvider>
    );

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
  });

  it("should render password change form", () => {
    renderComponent();

    expect(screen.getByTestId("password-change-form")).toBeInTheDocument();
    expect(screen.getByTestId("password-current-input")).toBeInTheDocument();
    expect(screen.getByTestId("password-new-input")).toBeInTheDocument();
    expect(screen.getByTestId("password-confirm-input")).toBeInTheDocument();
    expect(screen.getByTestId("password-submit-button")).toBeInTheDocument();
    expect(screen.getByTestId("password-cancel-button")).toBeInTheDocument();
    expect(screen.getByTestId("password-back-button")).toBeInTheDocument();
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
      expect(screen.getByText("New passwords do not match")).toBeInTheDocument();
    });

    // Should not call mutate
    expect(mockMutateAsync).not.toHaveBeenCalled();
  });

  it("should show validation error when password is too short", async () => {
    renderComponent();

    const newPasswordInput = screen.getByTestId("password-new-input");
    const confirmPasswordInput = screen.getByTestId("password-confirm-input");
    const submitButton = screen.getByTestId("password-submit-button");

    fireEvent.change(newPasswordInput, { target: { value: "short" } });
    fireEvent.change(confirmPasswordInput, { target: { value: "short" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByTestId("password-validation-error")).toBeInTheDocument();
      expect(screen.getByText("New password must be at least 8 characters")).toBeInTheDocument();
    });

    expect(mockMutateAsync).not.toHaveBeenCalled();
  });

  it("should submit form with valid data", async () => {
    mockMutateAsync.mockResolvedValueOnce(undefined);
    renderComponent();

    const currentPasswordInput = screen.getByTestId("password-current-input");
    const newPasswordInput = screen.getByTestId("password-new-input");
    const confirmPasswordInput = screen.getByTestId("password-confirm-input");
    const submitButton = screen.getByTestId("password-submit-button");

    fireEvent.change(currentPasswordInput, { target: { value: "currentpass123" } });
    fireEvent.change(newPasswordInput, { target: { value: "newpassword123" } });
    fireEvent.change(confirmPasswordInput, { target: { value: "newpassword123" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledWith({
        current_password: "currentpass123",
        new_password: "newpassword123",
        confirm_password: "newpassword123",
      });
    });
  });

  it("should clear form on successful submission", async () => {
    mockMutateAsync.mockResolvedValueOnce(undefined);
    renderComponent();

    const currentPasswordInput = screen.getByTestId("password-current-input");
    const newPasswordInput = screen.getByTestId("password-new-input");
    const confirmPasswordInput = screen.getByTestId("password-confirm-input");
    const submitButton = screen.getByTestId("password-submit-button");

    fireEvent.change(currentPasswordInput, { target: { value: "currentpass123" } });
    fireEvent.change(newPasswordInput, { target: { value: "newpassword123" } });
    fireEvent.change(confirmPasswordInput, { target: { value: "newpassword123" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(currentPasswordInput).toHaveValue("");
      expect(newPasswordInput).toHaveValue("");
      expect(confirmPasswordInput).toHaveValue("");
    });
  });

  it("should toggle password visibility", () => {
    renderComponent();

    const currentPasswordInput = screen.getByTestId("password-current-input");
    const toggleButton = screen.getByTestId("password-current-toggle");

    // Initially password type
    expect(currentPasswordInput).toHaveAttribute("type", "password");

    // Click toggle
    fireEvent.click(toggleButton);

    // Now text type
    expect(currentPasswordInput).toHaveAttribute("type", "text");

    // Click again
    fireEvent.click(toggleButton);

    // Back to password type
    expect(currentPasswordInput).toHaveAttribute("type", "password");
  });

  it("should navigate back to dashboard when cancel clicked", () => {
    renderComponent();

    const cancelButton = screen.getByTestId("password-cancel-button");
    expect(cancelButton.closest("a")).toHaveAttribute("href", "/");
  });
});
