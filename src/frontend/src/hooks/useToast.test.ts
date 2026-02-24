/**
 * Tests for useToast hook.
 * Following TDD: Red-Green-Refactor
 */

import { describe, it, expect, beforeEach } from "vitest";
import { renderHook } from "@testing-library/react";
import { useToast } from "@/hooks/useToast";
import { useNotificationStore } from "@/store/notificationStore";

describe("useToast", () => {
  beforeEach(() => {
    useNotificationStore.setState({ notifications: [] });
  });

  it("should show success toast", () => {
    const { result } = renderHook(() => useToast());

    result.current.success({
      title: "Success!",
      message: "Operation completed successfully",
    });

    const { notifications } = useNotificationStore.getState();
    expect(notifications).toHaveLength(1);
    expect(notifications[0].type).toBe("success");
    expect(notifications[0].title).toBe("Success!");
    expect(notifications[0].message).toBe("Operation completed successfully");
  });

  it("should show error toast", () => {
    const { result } = renderHook(() => useToast());

    result.current.error({
      title: "Error!",
      message: "Something went wrong",
    });

    const { notifications } = useNotificationStore.getState();
    expect(notifications).toHaveLength(1);
    expect(notifications[0].type).toBe("error");
    expect(notifications[0].title).toBe("Error!");
  });

  it("should show warning toast", () => {
    const { result } = renderHook(() => useToast());

    result.current.warning({
      title: "Warning",
      message: "Please check your input",
    });

    const { notifications } = useNotificationStore.getState();
    expect(notifications).toHaveLength(1);
    expect(notifications[0].type).toBe("warning");
  });

  it("should show info toast", () => {
    const { result } = renderHook(() => useToast());

    result.current.info({
      title: "Information",
      message: "Just so you know",
    });

    const { notifications } = useNotificationStore.getState();
    expect(notifications).toHaveLength(1);
    expect(notifications[0].type).toBe("info");
  });

  it("should use custom duration", () => {
    const { result } = renderHook(() => useToast());

    result.current.success({
      title: "Quick",
      duration: 2000,
    });

    const { notifications } = useNotificationStore.getState();
    expect(notifications[0].duration).toBe(2000);
  });

  it("should show generic toast with custom type", () => {
    const { result } = renderHook(() => useToast());

    result.current.show("error", {
      title: "Custom Error",
      message: "Custom error message",
    });

    const { notifications } = useNotificationStore.getState();
    expect(notifications).toHaveLength(1);
    expect(notifications[0].type).toBe("error");
    expect(notifications[0].title).toBe("Custom Error");
  });
});
