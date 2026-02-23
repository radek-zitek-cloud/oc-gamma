# Task Completion Checklist

## Before Submitting Code

### Code Quality
- [ ] Code follows project style guidelines (read @rules/ files)
- [ ] All type hints are present (Python: use `|` not Optional)
- [ ] No bare console.log/warn/error (use lib/logger.ts in frontend)
- [ ] No blocking code in async functions (backend)
- [ ] Proper error handling with structured responses

### Testing (TDD Required)
- [ ] Tests written BEFORE implementation (Red phase)
- [ ] Tests verified to fail correctly
- [ ] Implementation makes tests pass (Green phase)
- [ ] Code refactored (Refactor phase)
- [ ] All tests pass locally
- [ ] Backend: `uv run pytest` passes
- [ ] Frontend: `npm run test` passes

### Backend Specific
- [ ] SQLAlchemy models use 2.0 syntax (Mapped, mapped_column)
- [ ] Repository pattern used (no direct DB access in routers)
- [ ] Pydantic schemas separate from SQLAlchemy models
- [ ] All endpoints async
- [ ] Authentication uses HttpOnly cookies (not localStorage)
- [ ] IDOR prevention (verify ownership of resources)
- [ ] Rate limiting on auth endpoints

### Frontend Specific
- [ ] React functional components only
- [ ] TanStack Query for server state (no useEffect for data fetching)
- [ ] data-testid attributes on interactive elements
- [ ] Error boundaries in place
- [ ] App Shell layout followed (fixed header/sidebar/status bar)

### Security
- [ ] No secrets in code (use .env)
- [ ] CORS not using allow_origins=["*"]
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (no dangerouslySetInnerHTML or sanitized)
- [ ] Password hashing with bcrypt (not passlib)

### Formatting
- [ ] Python files formatted: `uv format <file>`
- [ ] TypeScript files formatted: `npx prettier --write <file>`
- [ ] No lint errors: `npm run lint` or `ruff check`

### Git
- [ ] Commit messages follow Conventional Commits: `type(scope): description`
- [ ] Branch created from main (not working in main)
- [ ] Changes committed (not left uncommitted)

## After Code Completion

### Required Actions
1. Run linting/formatting tools
2. Run all tests
3. Update feature tracking STATUS.md in docs/features/{slug}/
4. Create PR with proper description
5. Do NOT merge without human approval

### Documentation
- [ ] Feature tracking STATUS.md updated
- [ ] API changes documented (if applicable)
- [ ] Component documentation (if new UI components)

## Never Do
- ❌ Work directly in main/master branch
- ❌ Skip tests (strict TDD required)
- ❌ Use allow_origins=["*"] in CORS
- ❌ Store JWTs in localStorage
- ❌ Use passlib for password hashing
- ❌ Use useEffect for data fetching
- ❌ Mix sync and async code without care
- ❌ Merge without human approval
- ❌ Commit without conventional commit format
