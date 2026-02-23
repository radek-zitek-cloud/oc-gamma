/**
 * Centralized logging utility.
 * Never use bare console.log - always use this logger.
 */

interface LogMeta {
  [key: string]: unknown;
}

const isDevelopment = import.meta.env.DEV;

export const logger = {
  debug: (message: string, meta?: LogMeta) => {
    if (isDevelopment) {
      console.debug(`[DEBUG] ${message}`, meta || "");
    }
  },

  info: (message: string, meta?: LogMeta) => {
    console.info(`[INFO] ${message}`, meta || "");
  },

  warn: (message: string, meta?: LogMeta) => {
    console.warn(`[WARN] ${message}`, meta || "");
  },

  error: (message: string, meta?: LogMeta) => {
    console.error(`[ERROR] ${message}`, meta || "");
  },
};
