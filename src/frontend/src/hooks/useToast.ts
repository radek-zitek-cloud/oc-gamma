/**
 * Convenience hook for showing toast notifications.
 * Wraps the notification store with common use cases.
 */

import { useCallback } from "react";

import { useNotificationStore } from "@/store/notificationStore";
import type { NotificationType } from "@/types/notification";

interface ToastOptions {
  title: string;
  message?: string;
  duration?: number;
}

export function useToast() {
  const addNotification = useNotificationStore(
    (state) => state.addNotification
  );

  const show = useCallback(
    (type: NotificationType, options: ToastOptions) => {
      addNotification({
        type,
        title: options.title,
        message: options.message,
        duration: options.duration,
      });
    },
    [addNotification]
  );

  const success = useCallback(
    (options: ToastOptions) => show("success", options),
    [show]
  );

  const error = useCallback(
    (options: ToastOptions) => show("error", options),
    [show]
  );

  const warning = useCallback(
    (options: ToastOptions) => show("warning", options),
    [show]
  );

  const info = useCallback(
    (options: ToastOptions) => show("info", options),
    [show]
  );

  return { show, success, error, warning, info };
}
