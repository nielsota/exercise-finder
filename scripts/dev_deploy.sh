#!/bin/bash
set -e

echo "🚀 Starting local development environment with hot-reload..."
echo ""

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
    echo "⚠️  Warning: .env.prod not found. Create it from .env.example"
    echo ""
fi

# Option to rebuild the image
if [ "$1" == "--rebuild" ] || [ "$1" == "-r" ]; then
    echo "🔨 Rebuilding Docker image..."
    docker compose build --no-cache
    echo ""
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker compose down
echo ""

# Start the container in detached mode
echo "🐳 Starting container with hot-reload..."
docker compose up -d
echo ""

# Wait a moment for the container to start
sleep 2

# Show the status
echo "✅ Container is running!"
echo ""
echo "📍 Access the app at: http://localhost:8000"
echo "🔄 Hot-reload is enabled - changes to src/ will auto-restart"
echo "📋 View logs with: docker compose logs -f"
echo "🛑 Stop with: docker compose down"
echo ""

# Follow logs (Ctrl+C to exit, container keeps running)
echo "📋 Following logs (Ctrl+C to exit)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker compose logs -f

