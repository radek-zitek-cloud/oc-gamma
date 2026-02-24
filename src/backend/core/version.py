"""
Version management for backend.
Reads version from pyproject.toml for single source of truth.
"""

from pathlib import Path

def get_version() -> str:
    """Read version from pyproject.toml."""
    # Path to pyproject.toml (backend root)
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    
    try:
        with open(pyproject_path, "r") as f:
            for line in f:
                if line.strip().startswith("version"):
                    # Extract version from line like: version = "0.1.2"
                    return line.split("=")[1].strip().strip('"').strip("'")
    except (FileNotFoundError, IndexError):
        pass
    
    return "0.0.0"  # Fallback


__version__ = get_version()
