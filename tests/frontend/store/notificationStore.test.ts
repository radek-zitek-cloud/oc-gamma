/**
 * Tests for notification store (Zustand).
 * Following TDD: Red-Green-Refactor
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { useNotificationStore } from "@/store/notificationStore";

describe("notificationStore", () => {
  beforeEach(() => {
    // Reset store state before each test
    useNotificationStore.setState({ notifications: [] });
  });

  it("should add a notification", () => {
    const { addNotification } = useNotificationStore.getState();

    addNotification({
      type: "success",
      title: "Test Title",
      message: "Test message",
    });

    const { notifications } = useNotificationStore.getState();
    expect(notifications).toHaveLength(1);
    expect(notifications[0].type).toBe("success");
    expect(notifications[0].title).toBe("Test Title");
    expect(notifications[0].message).toBe("Test message");
    expect(notifications[0].id).toBeDefined();
    expect(notifications[0].duration).toBe(5000); // Default duration
  });

  it("should remove a notification by id", () => {
    const { addNotification, removeNotification } = useNotificationStore.getState();

    addNotification({ type: "info", title: "Test" });
    const { notifications } = useNotificationStore.getState();
    const id = notifications[0].id;

    removeNotification(id);

    expect(useNotificationStore.getState().notifications).toHaveLength(0);
  });

  it("should auto-remove notification after duration", async () => {
    vi.useFakeTimers();
    const { addNotification } = useNotificationStore.getState();

    addNotification({
      type: "info",
      title: "Test",
      duration: 1000,
    });

    expect(useNotificationStore.getState().notifications).toHaveLength(1);

    vi.advanceTimersByTime(1000);

    expect(useNotificationStore.getState().notifications).toHaveLength(0);
    vi.useRealTimers();
  });

  it("should clear all notifications", () => {
    const { addNotification, clearAll } = useNotificationStore.getState();

    addNotification({ type: "success", title: "Success 1" });
    addNotification({ type: "error", title: "Error 1" });
    addNotification({ type: "warning", title: "Warning 1" });

    expect(useNotificationStore.getState().notifications).toHaveLength(3);

    clearAll();

    expect(useNotificationStore.getState().notifications).toHaveLength(0);
  });

  it("should generate unique IDs for each notification", () => {
    const { addNotification } = useNotificationStore.getState();

    addNotification({ type: "info", title: "First" });
    addNotification({ type: "info", title: "Second" });
    addNotification({ type: "info", title: "Third" });

    const { notifications } = useNotificationStore.getState();
    const ids = notifications.map((n) => n.id);
    const uniqueIds = new Set(ids);

    expect(ids).toHaveLength(3);
    expect(uniqueIds.size).toBe(3);
  });

  it("should use custom duration when provided", () => {
    const { addNotification } = useNotificationStore.getState();

    addNotification({
      type: "success",
      title: "Quick",
      duration: 1000,
    });

    const { notifications } = useNotificationStore.getState();
    expect(notifications[0].duration).toBe(1000);
  });
});
