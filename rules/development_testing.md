---
title: Development & Testing & TDD Rules
description: Enforces strict Red-Green-Refactor loop, local execution, and Playwright E2E boundaries.
version: 2.1.0
date: 2026-02-23
---

# Testing & TDD Rules

## 1. The Agentic TDD Loop (Strict Requirement)
All new features, bug fixes, and utility functions must be built using strict Test-Driven Development (TDD). 
**CRITICAL:** You must NOT write implementation code at the same time as the test. You must follow this exact sequence:

1. **RED:** Write a single test for the specific behavior requested. Be explicit that you are doing TDD to avoid creating mock implementations for functionality that doesn't exist yet.
2. **VERIFY:** Run the test runner locally and verify that the test fails for the *correct* reason (not due to syntax errors or missing imports).
3. **GREEN:** Write the absolute minimum implementation code required to make that specific test pass.
4. **REFACTOR:** Clean up the implementation and the test code, ensuring the test remains green.
5. **REPEAT:** Move on to the next test/behavior. Do not write multiple tests at once.

## 2. Execution Strategy: Local First
* **Primary Loop:** All tests must be executed locally on the bare-metal environment during development. Do not rely on Docker Compose or GitHub Actions for the primary TDD feedback loop.
* **Commands:** * Backend: Execute tests using `uv run pytest`.
  * Frontend: Execute tests using `npm run test` (Vitest).
* **CI/CD:** GitHub Actions is strictly a secondary validation stage to prevent regressions on merged pull requests.

## 3. Frontend Testing Stack (React/Vite/TypeScript)
* **Framework:** Use `Vitest` as the test runner. Do not use Jest.
* **Component Testing:** Use `React Testing Library` (RTL).
* **Best Practices:** * Uninstall JSDOM and prefer Vitest Browser Mode for integration testing where possible.
  * Test user behavior (e.g., clicking buttons, finding text by role) rather than implementation details (like internal state variables).
  * Ensure all mocked API calls return data structures that strictly match the TypeScript interfaces.

## 4. Backend Testing Stack (FastAPI/Python/Async)
* **Framework:** Use `pytest` combined with `pytest-asyncio`.
* **API Testing:** Use `httpx.AsyncClient` alongside FastAPI's `ASGITestClient` to properly test asynchronous endpoints.
* **Database Testing:** * Tests must run against a separate, isolated SQLite in-memory database (`sqlite+aiosqlite:///:memory:`) to ensure speed and prevent state leakage.
  * Use Pytest async fixtures extensively to handle database setup/teardown and to yield clean database sessions for each test.
* **Mocking:** Avoid mocking the database when possible; use the isolated SQLite test DB instead. Only mock external 3rd-party network calls.

## 5. Integration Testing Boundaries
* **Backend Integration:** Use FastAPI's `TestClient` and `httpx.AsyncClient`. You MUST hit the actual FastAPI router and execute real SQLAlchemy queries against the isolated SQLite test database. Only external 3rd-party services (like payment gateways or email providers) should be mocked.
* **Frontend Integration:** Use Vitest with React Testing Library. You MUST intercept and mock all outbound API requests (using MSW or Vitest network mocks) to ensure frontend tests do not depend on the backend running.

## 6. End-to-End (E2E) Testing (Playwright)
* **Framework:** Use `Playwright` for all E2E testing.
* **Environment:** E2E tests must be configured to run against the Stage 2 containerized environment (Docker Compose) at `http://localhost:<port>`. Do not run E2E tests against the bare-metal dev servers.
* **Resilient Selectors (CRITICAL):** * You MUST NEVER select elements by CSS classes, nested DOM hierarchies, or dynamic text content.
  * You MUST add `data-testid="descriptive-name"` attributes to all interactive UI elements (buttons, inputs, forms, critical containers) in the React components.
  * Your Playwright tests MUST exclusively use `page.getByTestId('descriptive-name')` or standard accessibility roles (`page.getByRole()`) to interact with the page.
* **Scope:** E2E tests should only cover Critical User Journeys (CUJs) (e.g., User Login, Creating a Record, Completing a Checkout). Exhaustive edge-case testing belongs in Unit/Integration tests.

## 7. The Agentic E2E Workflow
Do not attempt Test-Driven Development (TDD) for E2E tests. TDD is for Unit/Integration only.
For E2E:
1. Ensure the frontend and backend implementations are fully built and unit-tested.
2. Ensure the UI components have appropriate `data-testid` attributes.
3. Write the Playwright E2E test to verify the complete user journey across the stack.