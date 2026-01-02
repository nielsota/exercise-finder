#!/bin/bash
set -e
set -u

# Run the web app locally without Docker for fast iteration
# Usage: ./scripts/dev-local.sh

cd "$(dirname "$0")/.."

echo "Starting local development server..."
echo "URL: http://localhost:8000"
echo ""

uv run uvicorn exercise_finder.web.app:app_factory --factory --reload --host 0.0.0.0 --port 8000

