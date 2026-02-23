---
title: Deployment & Infrastructure Rules
description: Guidelines for two-stage development, Docker Compose, and strict volume mounting.
version: 2.1.0
date: 2026-02-23
---

# Deployment & Infrastructure Rules

## 1. Production & Testing Environments
* **Production:** The application is strictly deployed as containerized microservices managed by Kubernetes (or standard Docker environments).
* **Testing:** The testing environment must be an exact mirror of production. Tests must run against the compiled/built production container images to guarantee parity.

## 2. Two-Stage Development Workflow
Development is split into two distinct stages to balance speed and accuracy. 

### Stage 1: Local Bare-Metal Development (Dual-Root)
To prevent dependency conflicts, the project uses a Dual-Root monorepo structure.
* **Backend Execution:**
  - **Working Directory:** All Python/uv commands MUST be run within `src/backend/`.
  - **Tooling:** Use `uv`. The `pyproject.toml` and `.venv` must reside in `src/backend/`.
  - **Command:** Execute via `uv run` (e.g., `uv run fastapi dev`).
* **Frontend Execution:**
  - **Working Directory:** All Node/npm commands MUST be run within `src/frontend/`.
  - **Tooling:** Use `npm`. The `package.json` and `node_modules/` must reside in `src/frontend/`.
  - **Command:** Execute via `npm run dev`.
* **Database:** Connects to a local SQLite database file in the project root `/data` directory for simplicity.

### Stage 2: Containerized Hot-Loading (`docker compose`)
Used to verify integration, networking, and environment parity before pushing to CI/CD or production.
* **Tooling:** Uses the modern `docker compose` CLI standard and a `compose.yaml` file (do not use the legacy `docker-compose.yml` naming convention).
* **Behavior:** Services must hot-reload code changes automatically (e.g., Vite HMR for frontend, Uvicorn `--reload` for backend).

## 3. Strict Docker Volume Mounting Constraints
CRITICAL: When generating `compose.yaml` for Stage 2 development, you must strictly control volume bind mounts. Cross-OS binary clashes are a known issue, so host-managed environments must NEVER overwrite container environments.

* **Project Root Structure:** The application must write all runtime data and logs to a `data/` and `logs/` directory located directly in the project root.
* **Allowed Mounts:** You may ONLY bind-mount the following directories from the host to the container:
  * Application source code: `./src:/app/src` 
  * Root data directory: `./data:/data` 
  * Root log directory: `./logs:/logs`
* **Forbidden Mounts:** You must ABSOLUTELY AVOID mounting the host's `node_modules` or `.venv` directories into the container.
* **Implementation Rule:** If mounting the entire project root (`.:/app`) is unavoidable, you MUST use anonymous volumes to block the host's dependency folders from bleeding into the container (e.g., adding `- /app/node_modules` and `- /app/.venv` under the service's `volumes` block).
* **Environment Injection:** 
  - **Stage 1:** The backend loads variables from the root `.env` via the relative path fallback defined in the config.
  - **Stage 2 (Compose):** The `compose.yaml` must use the `env_file: .env` directive at the service level. This injects the variables directly into the container's ENV, which Pydantic will prioritize over any physical file.

## 4. Versioning & Container Tags
* **Separation:** The Frontend and Backend codebases maintain separate, independent Semantic Versions (SemVer).
* **Container Tagging:** When building Docker images for deployment, images MUST be explicitly tagged with their exact SemVer version (e.g., `myapp-frontend:1.2.0`, `myapp-backend:1.1.4`).
* **Rule:** Do not rely on the `latest` tag for production deployments.
