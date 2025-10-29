#!/bin/bash
set -e

echo "🚀 Starting Trippy Backend..."
echo "📍 Current directory: $(pwd)"
echo "🔍 Checking environment variables..."

# Debug: Show all env vars
echo "Environment variables starting with OPENAI:"
env | grep OPENAI || echo "No OPENAI env vars found"

echo "Environment variables starting with ARIZE:"
env | grep ARIZE || echo "No ARIZE env vars found"

# Navigate to backend directory
cd backend

# Start uvicorn
echo "🎯 Starting uvicorn server..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT
