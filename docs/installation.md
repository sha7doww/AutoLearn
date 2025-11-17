# SmartPath 安装指南

完整的系统安装和配置步骤。

---

## 📋 前提条件

### 必需

- **micromamba** 或 conda/virtualenv
- **Node.js** >= 14.x
- **npm** >= 6.x
- **Git** (用于克隆项目)

### 可选

- **Neo4j** >= 4.x (用于生产环境，开发可跳过)
- **Docker** (用于运行Neo4j容器)

---

## 🔧 安装 micromamba

### Linux/macOS

```bash
curl -Ls https://micro.mamba.pm/install.sh | bash
```

### Windows (WSL)

```bash
curl -Ls https://micro.mamba.pm/install.sh | bash
```

重启终端使其生效。

---

## 📥 获取项目

```bash
# 克隆项目
git clone <repository-url>
cd AutoLearn

# 或直接解压项目包
unzip SmartPath.zip
cd SmartPath
```

---

## ⚙️ 环境设置

### 一键设置（推荐）

```bash
scripts/setup.sh
```

这会自动：
1. 创建 `smart_path` Python 3.11 环境
2. 安装所有后端依赖
3. 生成激活脚本

### 手动设置

```bash
# 创建环境
micromamba create -n smart_path python=3.11 -y -c conda-forge

# 激活环境
micromamba activate smart_path

# 安装后端依赖
cd backend
pip install -r requirements.txt
cd ..

# 安装前端依赖
cd frontend
npm install
cd ..
```

---

## 🗄️ 数据库配置（可选）

系统支持**演示模式**（无需数据库），也可以配置Neo4j获得完整功能。

### 方式1：跳过数据库（演示模式）

直接启动系统即可，会自动使用本地数据。

### 方式2：Docker安装Neo4j

```bash
# 启动Neo4j容器
docker run --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -d neo4j:latest

# 等待启动（约30秒）
sleep 30

# 初始化数据
source scripts/activate.sh
cd backend
python scripts/init_neo4j.py
```

### 方式3：本地安装Neo4j

1. 访问 https://neo4j.com/download/
2. 下载 Neo4j Community Edition
3. 安装并启动
4. 设置密码为 `password`
5. 运行初始化脚本

---

## ✅ 验证安装

### 检查环境

```bash
# 激活环境
source scripts/activate.sh

# 检查Python
python --version  # 应显示 3.11.x

# 检查已安装的包
pip list | grep fastapi
pip list | grep uvicorn
```

### 测试后端

```bash
cd backend
python scripts/test_api.py
```

应该看到所有测试通过（7/7 PASSED）。

### 测试前端

```bash
cd frontend
npm run serve
```

应该能在 http://localhost:8080 访问。

---

## 🚀 首次启动

```bash
# 确保在项目根目录
cd /path/to/AutoLearn

# 激活环境
source scripts/activate.sh

# 启动系统
scripts/start.sh
```

访问 http://localhost:8080/dashboard

---

## 🔍 故障排除

### 问题1: micromamba 命令未找到

```bash
# 重新安装
curl -Ls https://micro.mamba.pm/install.sh | bash

# 重启终端
exec bash
```

### 问题2: 脚本权限错误

```bash
chmod +x scripts/*.sh
```

### 问题3: 换行符问题

```bash
# 修复所有脚本
find scripts -name "*.sh" -exec sed -i 's/\r$//' {} \;
```

### 问题4: 端口被占用

```bash
# 查看占用的进程
lsof -i :8000  # 后端
lsof -i :8080  # 前端

# 停止进程
kill -9 <PID>
```

### 问题5: Neo4j连接失败

这是正常的！系统会自动进入演示模式。如果需要Neo4j：

```bash
# 检查Neo4j状态
docker ps | grep neo4j

# 重启Neo4j
docker restart neo4j
```

---

## 📊 安装验证清单

- [ ] micromamba 已安装
- [ ] Python 环境已创建 (`smart_path`)
- [ ] 后端依赖已安装
- [ ] 前端依赖已安装
- [ ] 可以激活环境
- [ ] 脚本可以执行
- [ ] 测试通过

---

## 🔄 更新系统

```bash
# 激活环境
source scripts/activate.sh

# 更新后端
cd backend
pip install -r requirements.txt --upgrade

# 更新前端
cd ../frontend
npm update

# 重启服务
cd ..
scripts/stop.sh
scripts/start.sh
```

---

## 🗑️ 完全卸载

```bash
# 停止服务
scripts/stop.sh

# 删除环境
micromamba env remove -n smart_path -y

# 删除Neo4j（如果使用Docker）
docker stop neo4j
docker rm neo4j

# 删除项目文件
cd ..
rm -rf AutoLearn
```

---

## ⏭️ 下一步

安装完成后，查看：
- [使用手册](usage.md) - 学习如何使用系统
- [演示指南](demo.md) - 准备中期汇报演示
