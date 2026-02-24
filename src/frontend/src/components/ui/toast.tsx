/**
 * Toast notification component using shadcn/ui patterns.
 */

import * as React from "react";
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import type { NotificationType } from "@/types/notification";

export interface ToastProps extends React.HTMLAttributes<HTMLDivElement> {
  type: NotificationType;
  title: string;
  message?: string;
  onDismiss?: () => void;
}

const iconMap = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
};

const typeStyles = {
  success: "border-success bg-success text-success-foreground",
  error: "border-destructive bg-destructive text-destructive-foreground",
  warning: "border-warning bg-warning text-warning-foreground",
  info: "border-info bg-info text-info-foreground",
};

export const Toast = React.forwardRef<HTMLDivElement, ToastProps>(
  ({ className, type, title, message, onDismiss, ...props }, ref) => {
    const Icon = iconMap[type];

    return (
      <div
        ref={ref}
        className={cn(
          "pointer-events-auto relative flex w-full max-w-sm items-start gap-3 rounded-lg border p-4 shadow-lg transition-all",
          typeStyles[type],
          className
        )}
        role="alert"
        data-testid={`toast-${type}`}
        {...props}
      >
        <Icon className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
        <div className="flex-1">
          <h4 className="text-sm font-semibold">{title}</h4>
          {message && (
            <p className="mt-1 text-sm opacity-90">{message}</p>
          )}
        </div>
        {onDismiss && (
          <Button
            variant="ghost"
            size="icon"
            className="-mr-2 -mt-2 h-6 w-6 shrink-0 opacity-70 hover:opacity-100"
            onClick={onDismiss}
            data-testid="toast-dismiss-button"
          >
            <X className="h-4 w-4" />
            <span className="sr-only">Dismiss</span>
          </Button>
        )}
      </div>
    );
  }
);
Toast.displayName = "Toast";
