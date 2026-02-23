import axios, { AxiosError } from "axios";
import type { InternalAxiosRequestConfig } from "axios";

import { generateCorrelationId } from "./utils";
import { logger } from "./logger";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Axios instance with default configuration.
 */
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // Important for HttpOnly cookies
});

// Request interceptor to add correlation ID
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const correlationId = generateCorrelationId();
    config.headers["X-Correlation-ID"] = correlationId;
    
    logger.debug(`API Request: ${config.method?.toUpperCase()} ${config.url}`, {
      correlationId,
    });
    
    return config;
  },
  (error: AxiosError) => {
    logger.error("API Request Error", { error: error.message });
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      logger.warn("Unauthorized request - redirecting to login");
      // Let the application handle the redirect
    }
    
    logger.error("API Response Error", {
      status: error.response?.status,
      message: error.message,
    });
    
    return Promise.reject(error);
  }
);
