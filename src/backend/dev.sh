#!/bin/bash
# Run the FastAPI backend server from the backend directory with hot reload
# Usage: ./dev.sh [port]

PORT=${1:-8000}
cd "$(dirname "$0")" || exit 1

# Get the project root (parent of src)
PROJECT_ROOT="$(cd ../.. && pwd)"

echo "Starting backend server on port $PORT..."
echo "Project root: $PROJECT_ROOT"
echo "Working directory: $(pwd)"
echo ""

# Set PYTHONPATH to include the src directory for proper package imports
export PYTHONPATH="${PROJECT_ROOT}/src:${PYTHONPATH}"

# Run uvicorn using module path with reload enabled
exec uv run uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --reload \
    --reload-dir . \
    --log-level info