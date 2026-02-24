# Run the FastAPI backend server from the backend directory with hot reload
# Usage: ./dev.ps1 [port]

param (
    [int]$Port = 8000
)

# Change to the script directory
Set-Location -Path $PSScriptRoot

# Get the project root (parent of src)
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "../..")

Write-Host "Starting backend server on port $Port..."
Write-Host "Project root: $ProjectRoot"
Write-Host "Working directory: $(Get-Location)"
Write-Host ""

# Set PYTHONPATH to include the src directory for proper package imports
$env:PYTHONPATH = "$ProjectRoot/src" + `
    $(if ($env:PYTHONPATH) { ";$env:PYTHONPATH" } else { "" })

# Run uvicorn using module path with reload enabled
uv run uvicorn backend.main:app `
    --host 0.0.0.0 `
    --port $Port `
    --reload `
    --reload-dir . `
    --log-level info