#!/bin/bash
# SmartPath 环境激活脚本
# 用法: source scripts/activate.sh
# 注意: 必须使用 source 命令，不能直接执行

ENV_NAME="smart_path"

# 检查是否被 source 调用
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "❌ 错误: 请使用 source 命令运行此脚本"
    echo ""
    echo "正确用法:"
    echo "  source scripts/activate.sh"
    echo ""
    echo "或:"
    echo "  . scripts/activate.sh"
    exit 1
fi

echo "=========================================="
echo "SmartPath 环境激活"
echo "=========================================="
echo ""

# 检查 micromamba 是否安装
if ! command -v micromamba &> /dev/null; then
    echo "❌ 错误: micromamba 未安装"
    echo ""
    echo "请先运行安装脚本:"
    echo "  scripts/setup.sh"
    return 1
fi

# 检查环境是否存在
if ! micromamba env list | grep -qw "${ENV_NAME}"; then
    echo "❌ 错误: 环境 '${ENV_NAME}' 不存在"
    echo ""
    echo "请先运行安装脚本:"
    echo "  scripts/setup.sh"
    return 1
fi

# 初始化 micromamba
eval "$(micromamba shell hook --shell bash)"

# 激活环境
micromamba activate ${ENV_NAME}

if [ $? -eq 0 ]; then
    echo "✅ 环境已激活: ${ENV_NAME}"
    echo ""
    echo "Python 版本:"
    python --version
    echo ""
    echo "现在可以:"
    echo "  - 启动服务: scripts/start.sh"
    echo "  - 运行测试: cd backend && python scripts/test_api.py"
    echo "  - 手动启动后端: cd backend && python -m app.main"
    echo "  - 手动启动前端: cd frontend && npm run serve"
    echo ""
    echo "=========================================="
else
    echo "❌ 环境激活失败"
    return 1
fi
