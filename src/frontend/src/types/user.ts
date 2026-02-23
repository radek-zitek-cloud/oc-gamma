/**
 * User type definitions.
 */

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  role: "USER" | "ADMIN";
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface PasswordChange {
  current_password: string;
  new_password: string;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
}
