#!/bin/bash
# SmartPath - Neo4j Setup Script
# 设置和初始化 Neo4j 数据库

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
echo "  SmartPath - Neo4j Setup"
echo "=========================================="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    log_error "Docker not found"
    echo ""
    echo "Neo4j 需要 Docker 运行。请选择："
    echo "  1. 安装 Docker: https://docs.docker.com/get-docker/"
    echo "  2. 使用演示模式（无需数据库）"
    echo ""
    exit 1
fi

log_success "Docker found"

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^neo4j$"; then
    log_warning "Neo4j container already exists"

    # Check if running
    if docker ps --format '{{.Names}}' | grep -q "^neo4j$"; then
        log_info "Neo4j is already running"
        echo ""
        echo "访问 Neo4j Browser: http://localhost:7474"
        echo "用户名: neo4j"
        echo "密码: password"
        echo ""

        read -p "是否重新初始化数据？(y/n): " reinit
        if [ "$reinit" = "y" ] || [ "$reinit" = "Y" ]; then
            log_info "Initializing Neo4j data..."
            cd "$(dirname "$0")/../backend"
            python scripts/init_neo4j.py
            log_success "Data initialized"
        fi
        exit 0
    else
        log_info "Starting existing container..."
        docker start neo4j
        sleep 5
        log_success "Neo4j started"
        echo ""
        echo "访问 Neo4j Browser: http://localhost:7474"
        echo "用户名: neo4j"
        echo "密码: password"
        exit 0
    fi
fi

# Create new container
log_info "Creating Neo4j container..."

docker run --name neo4j \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    -d neo4j:latest

if [ $? -ne 0 ]; then
    log_error "Failed to create Neo4j container"
    echo ""
    echo "可能的原因："
    echo "  1. Docker 代理问题（检查网络连接）"
    echo "  2. 端口 7474 或 7687 已被占用"
    echo ""
    echo "建议："
    echo "  - 使用演示模式（无需数据库）"
    echo "  - 检查 Docker 配置"
    exit 1
fi

log_success "Container created"
log_info "Waiting for Neo4j to start (30 seconds)..."
sleep 30

# Check if Neo4j is ready
if ! docker ps | grep -q neo4j; then
    log_error "Neo4j failed to start"
    echo ""
    echo "查看日志："
    echo "  docker logs neo4j"
    exit 1
fi

log_success "Neo4j is running"

# Initialize data
log_info "Initializing course data..."

# Check if smart_path environment exists
if ! micromamba env list | grep -qw "smart_path"; then
    log_error "Environment 'smart_path' not found"
    echo ""
    echo "请先运行: scripts/setup.sh"
    exit 1
fi

# Activate environment and run init script
eval "$(micromamba shell hook --shell bash)"
micromamba activate smart_path

cd "$(dirname "$0")/../backend"
python scripts/init_neo4j.py

if [ $? -eq 0 ]; then
    log_success "Data initialized successfully"
    echo ""
    echo "=========================================="
    echo "  Neo4j Setup Complete!"
    echo "=========================================="
    echo ""
    echo "访问信息："
    echo "  Neo4j Browser: http://localhost:7474"
    echo "  Bolt 端口: 7687"
    echo ""
    echo "登录凭证："
    echo "  用户名: neo4j"
    echo "  密码: password"
    echo ""
    echo "管理命令："
    echo "  启动: docker start neo4j"
    echo "  停止: docker stop neo4j"
    echo "  删除: docker rm neo4j"
    echo "  查看日志: docker logs neo4j"
    echo ""
    echo "后端会自动使用 Neo4j 数据库"
    echo "=========================================="
else
    log_error "Failed to initialize data"
    echo ""
    echo "检查 Neo4j 是否正常运行："
    echo "  docker logs neo4j"
    echo ""
    echo "或继续使用演示模式（无需数据库）"
    exit 1
fi
