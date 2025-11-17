#!/bin/bash
# SmartPath - Environment Setup Script
# Creates Python environment and installs dependencies

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;94m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}ℹ $1${NC}"; }
log_success() { echo -e "${GREEN}✓ $1${NC}"; }
log_error() { echo -e "${RED}✗ $1${NC}"; }
log_warning() { echo -e "${YELLOW}! $1${NC}"; }

echo "=========================================="
echo "  SmartPath - Environment Setup"
echo "=========================================="
echo ""

ENV_NAME="smart_path"

# Check micromamba
if ! command -v micromamba &> /dev/null; then
    log_error "micromamba not found"
    echo ""
    echo "Please install micromamba first:"
    echo "  curl -Ls https://micro.mamba.pm/install.sh | bash"
    echo ""
    exit 1
fi

log_success "micromamba found"

# Check if environment exists
if micromamba env list | grep -qw "${ENV_NAME}"; then
    log_warning "Environment '${ENV_NAME}' already exists"
    read -p "Recreate? (y/n): " recreate

    if [ "$recreate" != "y" ] && [ "$recreate" != "Y" ]; then
        log_info "Using existing environment"
        log_success "Setup complete! Run: source scripts/activate.sh"
        exit 0
    fi

    log_info "Removing old environment..."
    micromamba env remove -n ${ENV_NAME} -y
    log_success "Old environment removed"
fi

# Create environment
log_info "Creating environment '${ENV_NAME}' with Python 3.11..."
micromamba create -n ${ENV_NAME} python=3.11 -y -c conda-forge

if [ $? -ne 0 ]; then
    log_error "Failed to create environment"
    exit 1
fi

log_success "Environment created"

# Activate environment
log_info "Activating environment..."
eval "$(micromamba shell hook --shell bash)"
micromamba activate ${ENV_NAME}

# Install dependencies
log_info "Installing Python dependencies..."
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    log_error "Failed to install dependencies"
    exit 1
fi

log_success "Dependencies installed"
cd ..

# Create activation script
cat > scripts/activate.sh << 'EOF'
#!/bin/bash
# Quick activation script for SmartPath environment

eval "$(micromamba shell hook --shell bash)"
micromamba activate smart_path

echo "✓ SmartPath environment activated"
echo "Python: $(python --version)"
EOF

chmod +x scripts/activate.sh

# Summary
echo ""
log_success "Setup complete!"
echo ""
echo "Environment: ${ENV_NAME}"
echo "Python: $(python --version)"
echo ""
echo "Next steps:"
printf "  1. Activate environment: ${GREEN}source scripts/activate.sh${NC}\n"
printf "  2. Start system:         ${GREEN}scripts/start.sh${NC}\n"
echo ""
