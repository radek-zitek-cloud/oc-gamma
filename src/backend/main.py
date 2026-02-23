"""
Main application entry point for the FastAPI backend.
"""
from fastapi import FastAPI

app = FastAPI(
    title="OC Gamma API",
    description="Full-stack application backend",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to OC Gamma API"}
