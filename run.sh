#!/bin/bash
trap "kill 0" EXIT

# Start Backend
if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
else
    echo "Virtual environment not found. Please setup backend."
    exit 1
fi

echo "Starting Backend..."
uvicorn app.main:app --app-dir backend --reload --port 8000 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Start Frontend (Electron)
echo "Starting Electron..."
cd frontend
npm run electron:dev
