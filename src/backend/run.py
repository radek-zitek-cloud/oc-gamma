#!/usr/bin/env python3
"""
Launcher script for running the FastAPI backend with proper Python path.
This ensures all imports work correctly when running from the backend directory.
"""
import sys
from pathlib import Path

# Add the src directory to Python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

# Now import and run the app
from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)