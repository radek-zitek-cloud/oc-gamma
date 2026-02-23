/**
 * Global Error Boundary component using react-error-boundary.
 * Catches all unhandled errors in the React component tree.
 */

import type { FallbackProps } from "react-error-boundary";

import { Button } from "@/components/ui/button";

/**
 * Fallback component displayed when an error is caught.
 */
export function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-background">
      <div className="w-full max-w-md p-6 border border-destructive/50 rounded-lg bg-destructive/10">
        <h1 className="text-lg font-semibold text-destructive mb-2">
          Something went wrong
        </h1>
        
        <p className="text-sm text-muted-foreground mb-4">
          An unexpected error occurred. Please try again or contact support if the problem persists.
        </p>
        
        {error.message && (
          <pre className="text-xs bg-background p-2 rounded mb-4 overflow-auto max-h-32 border">
            {error.message}
          </pre>
        )}
        
        <Button onClick={resetErrorBoundary} className="w-full">
          Try Again
        </Button>
      </div>
    </div>
  );
}
