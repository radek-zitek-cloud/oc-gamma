/**
 * Tests for Profile page.
 * Following TDD: Red-Green-Refactor
 */

import "@testing-library/jest-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Profile } from "./Profile";

// Mock the auth store
const mockUser = {
  id: 1,
  email: "test@example.com",
  username: "testuser",
  full_name: "Test User",
};

const mockSetUser = vi.fn();

vi.mock("@/store/authStore", () => ({
  useAuthStore: vi.fn((selector) =>
    selector({
      user: mockUser,
      setUser: mockSetUser,
    })
  ),
}));

// Mock the auth hooks
const mockMutateAsync = vi.fn();
let mockIsLoading = false;
let mockIsPending = false;

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => ({
    isLoading: mockIsLoading,
  }),
  useUpdateProfile: () => ({
    mutateAsync: mockMutateAsync,
    isPending: mockIsPending,
  }),
}));

describe("Profile", () => {
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
          <Profile />
        </BrowserRouter>
      </QueryClientProvider>
    );

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
    mockIsLoading = false;
    mockIsPending = false;
  });

  it("should render profile form", () => {
    renderComponent();

    expect(screen.getByTestId("profile-heading")).toBeInTheDocument();
    expect(screen.getByTestId("profile-form")).toBeInTheDocument();
    expect(screen.getByTestId("profile-email-input")).toBeInTheDocument();
    expect(screen.getByTestId("profile-fullname-input")).toBeInTheDocument();
    expect(screen.getByTestId("profile-save-button")).toBeInTheDocument();
  });

  it("should display user data in form fields", () => {
    renderComponent();

    const emailInput = screen.getByTestId("profile-email-input");
    const fullNameInput = screen.getByTestId("profile-fullname-input");

    expect(emailInput).toHaveValue("test@example.com");
    expect(fullNameInput).toHaveValue("Test User");
  });

  it("should show loading state", () => {
    mockIsLoading = true;
    renderComponent();

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("should update form fields on user input", () => {
    renderComponent();

    const emailInput = screen.getByTestId("profile-email-input");
    const fullNameInput = screen.getByTestId("profile-fullname-input");

    fireEvent.change(emailInput, { target: { value: "newemail@example.com" } });
    fireEvent.change(fullNameInput, { target: { value: "New Name" } });

    expect(emailInput).toHaveValue("newemail@example.com");
    expect(fullNameInput).toHaveValue("New Name");
  });

  it("should submit form with updated data", async () => {
    mockMutateAsync.mockResolvedValueOnce({
      email: "newemail@example.com",
      full_name: "New Name",
    });

    renderComponent();

    const emailInput = screen.getByTestId("profile-email-input");
    const fullNameInput = screen.getByTestId("profile-fullname-input");
    const saveButton = screen.getByTestId("profile-save-button");

    fireEvent.change(emailInput, { target: { value: "newemail@example.com" } });
    fireEvent.change(fullNameInput, { target: { value: "New Name" } });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledWith({
        email: "newemail@example.com",
        full_name: "New Name",
      });
    });
  });

  it("should disable save button when pending", () => {
    mockIsPending = true;
    renderComponent();

    const saveButton = screen.getByTestId("profile-save-button");
    expect(saveButton).toBeDisabled();
    expect(saveButton).toHaveTextContent("Saving...");
  });

  it("should render security card with change password link", () => {
    renderComponent();

    expect(screen.getByText("Security")).toBeInTheDocument();
    expect(screen.getByText("Manage your password and account security.")).toBeInTheDocument();
    expect(screen.getByText("Change Password")).toBeInTheDocument();
    
    const changePasswordLink = screen.getByTestId("profile-change-password-link");
    expect(changePasswordLink).toBeInTheDocument();
    expect(changePasswordLink).toHaveAttribute("href", "/password");
  });

});
