# Split Profile & Password Feature Plan

## Overview
This feature splits the monolithic Profile page into two separate pages:
1. `/profile` - Profile editing (email, full_name)
2. `/profile/password` - Password change with confirmation

Additionally implements:
- Toast notification system for success/error/warning states
- Password confirmation validation
- Enhanced UI with primary background color for editable fields

## Scope
- Frontend: React + TypeScript + Tailwind + shadcn/ui + TanStack Query
- Backend: FastAPI + Pydantic V2 + SQLAlchemy 2.0
- Testing: Unit, Integration, E2E (Playwright)

## Key Technical Decisions
1. Use Zustand for toast state management (client state)
2. Create reusable Toast component using shadcn/ui patterns
3. PasswordChange schema validation at both frontend and backend
4. Follow TDD: Red-Green-Refactor for all new code
5. Add data-testid attributes for E2E testing

## Version Impact
- Backend: 0.2.0 → 0.3.0 (minor - API schema change)
- Frontend: 0.1.0 → 0.2.0 (minor - new features)

## Branch
`feat/split-profile-password`
