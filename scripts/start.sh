#!/bin/bash
# SmartPath - Start Script
# Starts backend and frontend services

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;94m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ $1${NC}"; }
log_success() { echo -e "${GREEN}✓ $1${NC}"; }
log_error() { echo -e "${RED}✗ $1${NC}"; }
log_warning() { echo -e "${YELLOW}! $1${NC}"; }

echo "=========================================="
echo "  SmartPath - Starting Services"
echo "=========================================="
echo ""

# Check environment
if ! command -v micromamba &> /dev/null; then
    log_error "micromamba not found. Run: scripts/setup.sh"
    exit 1
fi

if ! micromamba env list | grep -qw "smart_path"; then
    log_error "Environment 'smart_path' not found"
    log_info "Run: scripts/setup.sh"
    exit 1
fi

# Activate environment
eval "$(micromamba shell hook --shell bash)"
micromamba activate smart_path

# Create logs directory
mkdir -p logs

# Start backend
log_info "[1/2] Starting backend..."
cd backend

if [ ! -f ".env" ]; then
    log_warning ".env not found, using defaults"
fi

nohup python -m app.main > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid

sleep 3

if ! ps -p $BACKEND_PID > /dev/null; then
    log_error "Backend failed to start"
    cat ../logs/backend.log
    exit 1
fi

log_success "Backend started (PID: $BACKEND_PID)"
cd ..

# Start frontend
log_info "[2/2] Starting frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    log_warning "node_modules not found, installing..."
    npm install
fi

nohup npm run serve > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid

sleep 5

if ! ps -p $FRONTEND_PID > /dev/null; then
    log_error "Frontend failed to start"
    cat ../logs/frontend.log
    exit 1
fi

log_success "Frontend started (PID: $FRONTEND_PID)"
cd ..

# Summary
echo ""
echo "=========================================="
log_success "Services started successfully!"
echo "=========================================="
echo ""
echo "Access:"
printf "  🎯 Dashboard:  ${GREEN}http://localhost:8080/dashboard${NC}\n"
printf "  🏠 Home:       ${GREEN}http://localhost:8080${NC}\n"
printf "  📡 API Docs:   ${GREEN}http://localhost:8000/docs${NC}\n"
echo ""
echo "Logs:"
echo "  Backend:  tail -f logs/backend.log"
echo "  Frontend: tail -f logs/frontend.log"
echo ""
printf "Stop services: ${YELLOW}scripts/stop.sh${NC}\n"
echo ""
