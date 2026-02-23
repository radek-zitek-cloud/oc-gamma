# OC Gamma - Suggested Commands

## System Commands (Linux)
- `ls` - List files
- `cd <dir>` - Change directory
- `find . -name "*.py"` - Find files
- `grep -r "pattern" .` - Search in files
- `git status` - Check git status
- `git add <file>` - Stage files
- `git commit -m "message"` - Commit changes
- `git push` - Push to remote

## Backend Commands (run from src/backend/)

### Development
- `uv run fastapi dev` - Start development server
- `uv run uvicorn main:app --reload` - Alternative dev server

### Testing (TDD)
- `uv run pytest` - Run all tests
- `uv run pytest -v` - Run with verbose output
- `uv run pytest tests/test_file.py` - Run specific test file
- `uv run pytest -k test_name` - Run tests matching pattern

### Database
- `uv run alembic revision --autogenerate -m "description"` - Create migration
- `uv run alembic upgrade head` - Run migrations
- `uv run alembic downgrade -1` - Rollback one migration

### Code Quality
- `uv format <file>` - Format Python file with uv
- `ruff check <file>` - Lint Python file
- `ruff format <file>` - Format with ruff

### Dependencies
- `uv add <package>` - Add dependency
- `uv add --dev <package>` - Add dev dependency
- `uv sync` - Sync dependencies

## Frontend Commands (run from src/frontend/)

### Development
- `npm run dev` - Start Vite dev server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

### Testing (TDD)
- `npm run test` - Run Vitest tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Run tests with coverage

### Code Quality
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues
- `npx prettier --write <file>` - Format file with Prettier

### Dependencies
- `npm install <package>` - Add dependency
- `npm install -D <package>` - Add dev dependency

## E2E Testing (Playwright)
- `npx playwright test` - Run E2E tests
- `npx playwright test --headed` - Run with visible browser
- `npx playwright test --debug` - Debug mode

## Docker Commands
- `docker compose up` - Start all services
- `docker compose up -d` - Start in background
- `docker compose down` - Stop services
- `docker compose logs -f` - Follow logs
- `docker compose build` - Rebuild images

## Git Workflow
- `git checkout -b feature/name` - Create feature branch
- `git commit -m "feat(scope): description"` - Conventional commit
- `git push -u origin feature/name` - Push new branch

### Commit Types
- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `docs:` - Documentation
- `chore:` - Maintenance
