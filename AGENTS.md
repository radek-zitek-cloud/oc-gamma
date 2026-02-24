---
title: Master Agent Instructions
description: Global configuration and progressive disclosure router for AI coding agents.
version: 2.1.0
date: 2026-02-23
---

# ⚠️ CRITICAL RULES - READ FIRST

## 🚫 NEVER Commit to main/master Branch
**ALWAYS create a feature branch before making any changes.**

Before starting ANY work:
1. Check current branch: `git branch`
2. If on main/master: `git checkout -b feature/descriptive-name`
3. Only then begin implementing changes

**This is a hard requirement. Violations must be immediately corrected.**

---

# Full Stack Project

This is a modern full-stack application using a React/Vite frontend and a FastAPI/PostgreSQL backend. To optimize context limits and keep instructions relevant, we use progressive disclosure.

## MCP Servers

Use the available MCP servers.

### Workflow Overview

```
[Feature Request] → [Planning] → [Plan Approved] → [Coding] → [Code Review] → 
[Security Review] → [Documentation] → [Human Final Approval] → [Complete]
```

### Feature State Tracking

Every feature MUST have a tracking document at `/docs/features/{feature-slug}/STATUS.md`. This is the shared memory across agent invocations. Each agent reads this file at the start and updates it before finishing.

**STATUS.md Template:**

```markdown
# Feature: {Feature Name}
## State: {current_state}
## Plan: [link to plan document]
## Changed Files:
- path/to/file1.py
- path/to/file2.tsx
## Reports:
- [ ] Plan: /docs/features/{slug}/plan.md
- [ ] Code Review: /docs/features/{slug}/code-review.md
- [ ] Security Review: /docs/features/{slug}/security-review.md
- [ ] Documentation: /docs/features/{slug}/docs-report.md
## Approval Log:
- {date} - Plan approved by {human}
- {date} - Code review passed
- {date} - Security review passed
- {date} - Final approval by {human}
```

### Manual Agent Invocation Guide

**Starting a Feature:**
1. Human describes the feature request
2. **Invoke:** `planning-agent` - "Create implementation plan for [feature]"

**State Transitions:**

| Current State | Next State | Agent to Invoke | Human Action Required |
|---------------|------------|-----------------|----------------------|
| Feature Request | Planning | planning-agent | Submit feature description |
| Planning | Plan Approved | - | **Approve/reject the plan** |
| Plan Approved | Coding | code-implementer | - |
| Coding | Code Review | code-reviewer | Implementation complete |
| Code Review | Security Review | security-reviewer | Code review passed |
| Security Review | Documentation | documentation-agent | Security audit passed |
| Documentation | Human Final Approval | - | **Final review & merge approval** |

**Loopbacks (when reviews fail):**
- Code Review → Coding: Fix code quality issues
- Security Review → Coding: Fix security vulnerabilities

### Agent Mapping

- **planning-agent** → Planning phase
- **code-implementer** → Coding phase  
- **code-reviewer** → Code Review phase
- **security-reviewer** → Security Review phase
- **documentation-agent** → Documentation phase

### Mandatory Human Checkpoints

🚫 **CRITICAL:** These transitions require explicit human approval:
1. **Planning → Plan Approved** - Review and approve the implementation plan
2. **Documentation → Human Final Approval** - Review implementation, tests, docs before merge

### Governance Rules

- **No coding without approved plan** - Never start implementation before plan approval
- **No merge without dual review** - Both code review AND security review must pass
- **Documentation always follows security** - Update docs only after security approval
- **Human is final authority** - All merges require human final approval

### Error Recovery Protocol

If an agent invocation is interrupted or produces incomplete output:
1. The agent MUST write partial findings to the feature tracking document with `STATUS: INCOMPLETE`
2. The next invocation of the same agent MUST read the tracking document and resume from the last checkpoint
3. Maximum loopback iterations: **3** per review stage (code review ↔ coding, security review ↔ coding). After 3 iterations, escalate to human intervention.

### Example Session

```
User: "I need to add user authentication"
→ Invoke: planning-agent
→ Review plan, approve it
→ Invoke: code-implementer (follows approved plan)
→ Invoke: code-reviewer (after tests pass)
→ Invoke: security-reviewer (after code review passes)
→ Invoke: documentation-agent (after security passes)
→ Human: Review everything, approve merge
```

## External Rule Loading
CRITICAL: When you encounter a file reference (e.g., `@rules/frontend_arch_design.md`), you must use your Read tool to load it immediately on a need-to-know basis.

**Instructions for the Agent:**
- Do NOT preemptively load all references. Load them only when the specific task requires it.
- When loaded, treat the content as strict, mandatory instructions that override your default behaviors.
- Ask clarifying questions if the rules conflict with your internal logic before writing any code.

## Domain-Specific Architecture Guidelines

### Frontend Tasks
**Read immediately:** @rules/frontend_arch_design.md
- **Tech:** React 18+, Vite, Tailwind CSS, shadcn/ui, TanStack Query, Zustand
- **Constraints:** Fixed App Shell layout, HSL color variables, structured logging
- **Testing:** Vitest + React Testing Library (NO Jest)

### Backend Tasks
**Read immediately:** @rules/backend_arch_design.md
- **Tech:** FastAPI, SQLAlchemy 2.0, Pydantic V2, Alembic, asyncpg/aiosqlite
- **Constraints:** Strict separation SQLAlchemy/Pydantic, repository pattern, async only
- **Testing:** pytest + pytest-asyncio with SQLite in-memory DB

### Deployment Tasks
**Read immediately:** @rules/deployment.md
- **Stage 1:** Local bare-metal with `uv` and `npm`
- **Stage 2:** Docker Compose with hot-reload
- **Volumes:** Mount only `./src`, `./data`, `./logs` (NEVER mount `.venv` or `node_modules`)

### Development and Testing Tasks
**Read immediately:** @rules/development_testing.md
- **Unit/Integration:** Strict Red-Green-Refactor TDD loop
- **E2E:** Playwright with `data-testid` selectors only
- **Database:** Isolated SQLite for tests, never mock DB

### Security Tasks
**Read immediately:** @rules/security.md
- **Auth:** HttpOnly cookies, bcrypt (not passlib), JWT tokens
- **CORS:** Never use `allow_origins=["*"]`
- **Protection:** Rate limiting, IDOR prevention, parameterized queries

## Standard Output Paths

All agent artifacts MUST follow this directory convention:

```
/docs/
├── features/                  # Feature tracking (one dir per feature)
│   └── {feature-slug}/
│       ├── STATUS.md          # State tracking document (shared memory)
│       ├── plan.md            # Planning agent output
│       ├── code-review.md     # Code reviewer output
│       ├── security-review.md # Security reviewer output
│       └── docs-report.md     # Documentation agent output
├── api/                       # API documentation
├── architecture/              # Architecture documentation
└── guides/                    # User and developer guides
```

## Project Structure

```
your-project-root/
├── .env                       # Global environment variables & secrets
├── .gitignore                 # Standard exclusions (node_modules, .venv, data/, logs/)
├── AGENTS.md                  # Master Agent Instructions (The Router)
├── compose.yaml               # Docker Compose for Stage 2 development
├── data/                      # Persistent data (SQLite, etc.) - Host-mounted
├── docs/                      # All documentation and agent artifacts
├── logs/                      # Structured JSON log files - Host-mounted
├── rules/                     # The Agentic Rulebook (Domain-specific rules)
│   ├── backend_arch_design.md
│   ├── deployment.md
│   ├── frontend_arch_design.md
│   ├── security.md
│   └── development_testing.md
├── src/
│   ├── backend/               # Python/FastAPI Root
│   │   ├── .python-version    # Managed by uv
│   │   ├── .venv/             # Local backend environment
│   │   ├── pyproject.toml     # Backend dependencies (uv)
│   │   ├── alembic/           # Async database migrations
│   │   ├── api/               # FastAPI routers & endpoints
│   │   ├── core/              # Config, Security, DB session setup
│   │   ├── models/            # SQLAlchemy 2.0 Declarative Models
│   │   ├── repositories/      # Data Access Layer (CRUD)
│   │   ├── schemas/           # Pydantic V2 Models
│   │   └── services/          # Complex cross-repository business logic
│   └── frontend/              # React/Vite/TypeScript Root
│       ├── .eslintrc.json     # Linting rules
│       ├── node_modules/      # Local frontend environment
│       ├── package.json       # Frontend dependencies (npm)
│       ├── tsconfig.json      # TypeScript configuration
│       ├── vite.config.ts     # Vite configuration
│       └── src/
│           ├── components/    # UI (shadcn) & Layout components
│           ├── hooks/         # TanStack Query & logic hooks
│           ├── lib/           # Centralized logger.ts & utils
│           ├── store/         # Zustand state management
│           └── types/         # Global TypeScript interfaces/enums
└── tests/
    ├── backend/               # Pytest (Unit & Integration)
    ├── frontend/              # Vitest (Component & Logic)
    └── e2e/                   # Playwright (Full User Journeys)
```

## Code Style Guidelines

### Git Commits
- **Format:** Strictly use Conventional Commits: `type(scope): description`
- **Types:** `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `perf:`
- **Example:** `feat(auth): add JWT token refresh endpoint`
- **Branches:** Never work in master or main branch, always create working branch.

### Backend (Python)

#### Imports (Strict Order)
```python
1. Standard library imports
2. Third-party imports (FastAPI, SQLAlchemy, Pydantic)
3. Local application imports (absolute imports preferred)
```

#### Naming Conventions
- **Modules/Files:** `snake_case.py`
- **Classes:** `PascalCase` (e.g., `UserRepository`)
- **Functions/Variables:** `snake_case` (e.g., `get_user_by_id`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- **Private:** `_leading_underscore` for internal use
- **Async:** Prefix with verb indicating async (e.g., `async def fetch_users()`)

#### Type Hints (Mandatory)
```python
# Always use type hints
async def get_user(user_id: int) -> UserSchema | None:
    ...

# Use | instead of Optional/Union (Python 3.10+)
def process(data: str | None) -> list[int]:
    ...
```

#### Error Handling
- Use structured error responses: `{"detail": "message", "code": "ERROR_CODE"}`
- Raise `HTTPException` with appropriate status codes
- Never expose internal error details to clients
- Log full stack traces server-side only

#### Async Programming
- **ALL** database, file I/O, and network calls must be async
- Never run blocking code in async endpoints
- Use `await` consistently; never mix sync/async without `run_in_executor`

### Frontend (TypeScript)

#### Imports (Strict Order)
```typescript
1. React and framework imports
2. Third-party libraries (TanStack Query, Zustand)
3. Absolute imports (@/components, @/lib)
4. Relative imports (./Component)
```

#### Naming Conventions
- **Components:** `PascalCase.tsx` (e.g., `UserProfile.tsx`)
- **Hooks:** `usePascalCase.ts` (e.g., `useAuth.ts`)
- **Utilities:** `camelCase.ts` (e.g., `formatDate.ts`)
- **Types/Interfaces:** `PascalCase` (e.g., `interface UserProps`)
- **Constants:** `UPPER_SNAKE_CASE`
- **Styled Components:** Suffix with `Styled` or use descriptive names

#### Type Safety (Mandatory)
```typescript
// Always define explicit types
interface UserProps {
  id: string;
  name: string;
}

// Use strict TypeScript config - no implicit any
const UserCard: React.FC<UserProps> = ({ id, name }) => { ... }

// Prefer interface over type for object shapes
// Use type for unions, tuples, and utility types
```

#### Error Handling
- Use React Error Boundaries (`react-error-boundary`)
- Never use bare `console.log/warn/error` - use `lib/logger.ts`
- Always handle async errors in try/catch
- Provide fallback UIs for error states

#### React Patterns
- Use functional components only (no class components)
- Use hooks for state and side effects
- Use TanStack Query for server state (NEVER useEffect for data fetching)
- Use Zustand for global client state only when necessary
- Always use `data-testid` attributes for E2E selectors