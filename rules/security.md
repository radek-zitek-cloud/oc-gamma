---
title: Security & Compliance Rules
description: Guidelines for HttpOnly JWTs, CORS, RBAC, and multi-agent security audits.
version: 2.1.0
date: 2026-02-23
---

# Security & Compliance Rules

## 1. The Multi-Agent Workflow
* **Coding Agent:** Your job is to implement features securely following these rules.
* **Security Agent:** Your job is to audit the coding agent's work. Be deeply cynical. Look for injection flaws, broken access control (IDOR), and XSS vulnerabilities. Generate a strict markdown checklist of flaws for the coding agent to fix. Do not write the code yourself; only audit and critique.

## 2. Authentication & Token Management (Strict)
* **Storage:** JWTs must NEVER be stored in the browser's `localStorage` or `sessionStorage`. 
* **HttpOnly Cookies:** The FastAPI backend must issue the JWT via a `Set-Cookie` header. The cookie must be configured with `HttpOnly=True`, `Secure=True` (in production), and `SameSite="lax"` (or `"strict"`).
* **Frontend Execution:** The React frontend (whether using `fetch` or Axios) must be configured to send credentials with every request (e.g., `credentials: 'include'`).
* **Password Hashing:** Use `bcrypt` exclusively.

## 3. Authorization & RBAC
* **Role-Based Access Control:** The system must anticipate RBAC. Define a basic `Role` enum (e.g., `USER`, `ADMIN`).
* **Enforcement:** Use FastAPI's Dependency Injection to enforce roles on endpoints (e.g., `Depends(require_role(Role.ADMIN))`).
* **IDOR Prevention (Insecure Direct Object Reference):** Do not assume a user has access to a resource just because they have a valid token. Every protected endpoint must verify that the authenticated user actually owns the specific database row they are trying to read, modify, or delete.

## 4. API Protection (CORS & Rate Limiting)
* **CORS Middleware:** * NEVER use `allow_origins=["*"]`. 
  * Allowed origins must be loaded dynamically via `pydantic-settings` from the `.env` file.
  * `allow_credentials=True` MUST be set so the frontend can send the HttpOnly cookie.
* **Rate Limiting:** Protect all endpoints, especially authentication routes, using a rate limiter (e.g., `slowapi` or a custom Redis-based middleware) to prevent brute-force attacks.

## 5. Data Security (Backend & Frontend)
* **SQL Injection Prevention:** Rely entirely on SQLAlchemy 2.0 parameterized queries and ORM methods. Never construct raw SQL strings.
* **Input Validation:** All incoming API payloads must be strictly validated using Pydantic V2 schemas. Reject unknown fields.
* **XSS Prevention:** In React, strictly avoid `dangerouslySetInnerHTML`. If unavoidable, sanitize the input with `DOMPurify` first.
* **Secrets:** Never hardcode API keys or secrets. Do not log the application configuration object if it contains secrets.

## 6. Container Security
* **Principle of Least Privilege:** Docker containers must NOT run as the `root` user. The `Dockerfile` must create a dedicated `appuser` and use the `USER` directive before the `CMD` or `ENTRYPOINT`.