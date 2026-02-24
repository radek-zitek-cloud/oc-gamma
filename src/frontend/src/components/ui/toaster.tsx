/**
 * Toast container component that renders all active notifications.
 * Positioned fixed at top-right of viewport.
 * Uses CSS transitions since framer-motion is not available.
 */

import { useEffect, useState } from "react";

import { useNotificationStore } from "@/store/notificationStore";
import { Toast } from "@/components/ui/toast";

export function Toaster() {
  const { notifications, removeNotification } = useNotificationStore();
  const [mounted, setMounted] = useState<Set<string>>(new Set());

  // Trigger enter animation
  useEffect(() => {
    const newMounted = new Set(mounted);
    notifications.forEach((n) => {
      if (!newMounted.has(n.id)) {
        // Small delay to allow DOM to mount before animation
        setTimeout(() => {
          setMounted((prev) => new Set([...prev, n.id]));
        }, 10);
      }
    });
  }, [notifications, mounted]);

  const handleDismiss = (id: string) => {
    setMounted((prev) => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
    // Wait for exit animation before removing
    setTimeout(() => {
      removeNotification(id);
    }, 200);
  };

  if (notifications.length === 0) {
    return null;
  }

  return (
    <div
      className="fixed right-4 top-4 z-[100] flex flex-col gap-2"
      data-testid="toast-container"
    >
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`
            transform transition-all duration-200 ease-out
            ${mounted.has(notification.id) 
              ? "translate-x-0 opacity-100" 
              : "translate-x-full opacity-0"
            }
          `}
        >
          <Toast
            type={notification.type}
            title={notification.title}
            message={notification.message}
            onDismiss={() => handleDismiss(notification.id)}
          />
        </div>
      ))}
    </div>
  );
}
