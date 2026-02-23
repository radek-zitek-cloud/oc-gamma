---
title: Backend Architecture & Design Rules
description: Strict constraints for async FastAPI, SQLAlchemy 2.0, and Pydantic V2 architecture.
version: 2.1.0
date: 2026-02-23
---

# Backend Architecture & Design Rules

## 1. Core Tech Stack
* **Framework:** FastAPI (Strictly Asynchronous).
  - Produce OpenAPI / Swagger / ReDocs
* **Databases:** SQLite (`aiosqlite`) for local development, PostgreSQL (`asyncpg`) for production.
* **ORM:** SQLAlchemy 2.0 (Async). DO NOT use SQLModel. 
* **Validation/Serialization:** Pydantic V2.
* **Migrations:** Alembic (Must be configured for async execution in `env.py`).
  - Automated migrations during the backend startup.
* **Configuration:** `pydantic-settings` loaded from `.env` files.

## 2. Project Structure (Strict Layer-Based)
The application must follow a strict layer-based architecture to separate concerns. Code must be organized into the following directories:
* `/api` - FastAPI routers, endpoints, and HTTP exception handling. Maintain API versioning `/api/v1`.
* `/models` - SQLAlchemy 2.0 declarative base classes and database table definitions.
* `/schemas` - Pydantic V2 models for request validation and response serialization.
* `/repositories` - Data access layer encapsulating all SQLAlchemy CRUD operations.
* `/core` - Application configuration, database engine/session setup, and security utilities.
* `/services` - Complex business logic (only if it spans multiple repositories, otherwise keep logic in repositories).

## 3. Database & ORM Rules
* **Separation of Concerns:** SQLAlchemy models (`/models`) and Pydantic schemas (`/schemas`) must remain strictly separate. Do not use SQLAlchemy models as response models in FastAPI routers.
* **SQLAlchemy 2.0 Syntax:** Use modern SQLAlchemy 2.0 constructs. 
  * Use `Mapped` and `mapped_column` for model definitions.
  * Use `select()`, `insert()`, `update()`, and `delete()` constructs executed via `await session.execute()`. 
  * DO NOT use legacy `session.query()` syntax.
* **Async Engine:** The database engine must be instantiated using `create_async_engine`. Sessions must use `AsyncSession` via `async_sessionmaker`.

## 3.1 Migration Safety Rules (Alembic)
* **One Concern Per Migration:** Each migration file must contain either schema changes (add/drop/alter columns, create/drop tables, modify constraints) OR data transformations (backfilling values, converting formats, seeding rows). Never combine both in a single migration. Schema migrations are reversible by definition; data transformations require explicit rollback logic that is harder to reason about when mixed with DDL.
* **Reversibility:** Every migration must implement both `upgrade()` and `downgrade()`. If a `downgrade()` is truly impossible (e.g., dropping a column that discards data), the `downgrade()` body must raise `NotImplementedError("Irreversible migration: {reason}")` rather than being left empty or containing a silent `pass`.
* **No Destructive Operations Without a Two-Phase Approach:** Never drop a column, drop a table, or rename a column in the same release that removes the application code referencing it. Use a two-phase deployment:
  1. **Phase 1 (code release):** Deploy code that no longer reads/writes the target column, but the column still exists in the database.
  2. **Phase 2 (migration release):** Deploy the migration that drops the now-unused column.
  This prevents downtime during rolling deployments where old and new code versions coexist briefly.
* **Additive-First Principle:** Prefer additive changes (add column with default, add table, add index) over destructive changes. If a column needs to be renamed, add the new column, backfill it (in a separate data migration), update the code to use the new column, then drop the old column in a later phase.
* **Index Safety:** Creating indexes on large tables locks the table in PostgreSQL. For production, all `CREATE INDEX` statements must use `CONCURRENTLY` (Alembic: set `op.create_index(..., postgresql_concurrently=True)` and mark the migration with `# non-transactional` since concurrent index creation cannot run inside a transaction).
* **Testing:** Every migration must be tested by running the full `upgrade()` → `downgrade()` → `upgrade()` cycle against the test database before merging. This catches asymmetric migrations where the downgrade leaves the schema in a state the upgrade cannot handle on re-application.

## 4. Repository Pattern & Dependency Injection
* **Router Constraints:** FastAPI routers (`/api`) must NEVER import or interact with the database `AsyncSession` directly.
* **Flow:** 1. Inject the `AsyncSession` into the Repository class.
  2. Inject the Repository class into the FastAPI endpoint using `Depends()`.
* **Standardization:** Create an abstract/base generic repository class that handles standard CRUD operations to reduce boilerplate, then extend it for specific domain models (e.g., `UserRepository(BaseRepository)`).

## 5. Authentication & Security
* **Password Hashing:** DO NOT use the `passlib` library (it is unmaintained and throws deprecation warnings). Use the `bcrypt` package directly to hash and verify passwords.
* **Tokens:** Implement standard JWT (JSON Web Tokens) for stateless user authentication.
* **Protection:** Secure all protected endpoints using FastAPI's `OAuth2PasswordBearer` injected as a dependency.

## 6. Asynchronous Programming Rules
* All database interactions, file I/O, and external network requests must be asynchronous (`await`).
* Never run blocking synchronous code inside an `async def` endpoint.

## 7. Logging & Observability (Tool Agnostic)
* **Structured Logging:** All logs must be output in strict JSON format to ensure compatibility with any log aggregator (e.g., ELK, Datadog, Loki). Avoid plain-text string formatting for production logs.
* **Contextual Data:** Every log entry must include: `timestamp`, `level`, `module`, and a `message`.
* **Correlation IDs:** The backend must extract the `X-Correlation-ID` (or `X-Request-ID`) from incoming HTTP headers and inject it into all subsequent logs for that specific request lifecycle.
* **Output:** Logs should be written to standard output (`stdout`) for container orchestration capture, AND duplicated to the `./logs` file mount for local development inspection.

## 8. Versioning
* **Standard:** Use strict Semantic Versioning (SemVer) (e.g., `1.2.4`).
* **Storage:** Track the version centrally in `pyproject.toml` (or an equivalent single source of truth).
* **Visibility:** Expose a public `/health` or `/info` endpoint that returns the current backend version so the frontend Status Bar can fetch and display it.

## 9. Error Handling
* **Standardized Responses:** All HTTP errors must return a consistent JSON schema. Avoid returning raw strings. Use FastAPI's `HTTPException` with a structured dictionary: `{"detail": "Human readable message", "code": "SPECIFIC_ERROR_CODE"}` so the frontend can reliably parse it.

## 10. Environment Loading
* **Environment Loading:** Use `pydantic-settings`. The `Settings` class must be configured to check multiple potential paths for the `.env` file to support both local bare-metal and containerized environments:
  ```python
  model_config = SettingsConfigDict(
      # 1. Look in backend root, 2. Look in project root (Stage 1)
      env_file=[".env", "../../.env"], 
      env_file_encoding="utf-8",
      extra="ignore"
  )