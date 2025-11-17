#!/bin/bash
# SmartPath - Stop Script
# Stops all running services

GREEN='\033[0;32m'
NC='\033[0m'

echo "Stopping SmartPath services..."

# Stop backend
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID
        printf "${GREEN}✓${NC} Backend stopped\n"
    fi
    rm logs/backend.pid
fi

# Stop frontend
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID
        printf "${GREEN}✓${NC} Frontend stopped\n"
    fi
    rm logs/frontend.pid
fi

# Clean up any remaining processes
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "vue-cli-service serve" 2>/dev/null

echo ""
echo "All services stopped"
