# Neo4j 数据库设置指南

## 📋 概述

SmartPath 支持两种运行模式：

1. **演示模式**（默认）：使用本地 JSON 数据，无需数据库
2. **Neo4j 模式**：使用图数据库，支持更复杂的查询和关系分析

## 🚀 快速设置 Neo4j

### 一键安装

```bash
scripts/setup-neo4j.sh
```

这个脚本会自动完成：
- ✅ 检查 Docker 是否安装
- ✅ 创建 Neo4j 容器
- ✅ 等待服务启动
- ✅ 初始化 67 门课程数据
- ✅ 配置数据库连接

### 前提条件

- **Docker** 已安装并运行
- 端口 **7474** (HTTP) 和 **7687** (Bolt) 未被占用
- 网络连接正常（需要拉取 Neo4j 镜像）

## 🔧 手动安装步骤

如果自动脚本失败，可以手动操作：

### 1. 启动 Neo4j 容器

```bash
docker run --name neo4j \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    -d neo4j:latest
```

### 2. 等待启动

```bash
# 等待约 30 秒
sleep 30

# 检查状态
docker ps | grep neo4j
```

### 3. 初始化数据

```bash
# 激活环境
source scripts/activate.sh

# 运行初始化脚本
cd backend
python scripts/init_neo4j.py
```

## 🌐 访问 Neo4j

### Neo4j Browser

访问：http://localhost:7474

**登录凭证**：
- 用户名：`neo4j`
- 密码：`password`

### 常用查询

```cypher
// 查看所有课程
MATCH (c:Course) RETURN c LIMIT 25

// 查看课程关系
MATCH (c1:Course)-[:PREREQUISITE]->(c2:Course)
RETURN c1.label, c2.label
LIMIT 50

// 查找某门课程的所有先修课程
MATCH path = (start:Course {label: "人工智能"})-[:PREREQUISITE*]->(prereq)
RETURN path

// 统计课程数量
MATCH (c:Course) RETURN count(c)

// 查看知识点
MATCH (c:Course)-[:CONTAINS]->(k:KnowledgePoint)
RETURN c.label, k.name
LIMIT 20
```

## 🔄 管理 Neo4j

### 启动容器

```bash
docker start neo4j
```

### 停止容器

```bash
docker stop neo4j
```

### 重启容器

```bash
docker restart neo4j
```

### 查看日志

```bash
docker logs neo4j
```

### 删除容器

```bash
docker stop neo4j
docker rm neo4j
```

### 完全重置

```bash
# 删除容器和数据
docker stop neo4j
docker rm neo4j

# 重新运行设置脚本
scripts/setup-neo4j.sh
```

## 📊 数据结构

### 节点类型

1. **Course** - 课程节点
   - `id`: 课程ID
   - `label`: 课程名称
   - `difficulty`: 难度等级
   - `credits`: 学分
   - `course_type`: 课程类型

2. **KnowledgePoint** - 知识点节点（可选）
   - `name`: 知识点名称

### 关系类型

1. **PREREQUISITE** - 先修关系
   - 方向：先修课程 → 目标课程
   - 例如：`(高等数学)-[:PREREQUISITE]->(概率论)`

2. **CONTAINS** - 包含知识点（可选）
   - 方向：课程 → 知识点

## ⚙️ 后端配置

### 环境变量

创建 `backend/.env` 文件：

```env
# Neo4j 连接配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# API 配置
API_HOST=0.0.0.0
API_PORT=8000
```

### 连接检查

后端会自动检测 Neo4j 连接：
- ✅ **连接成功**：使用 Neo4j 数据
- ❌ **连接失败**：自动切换到演示模式

## 🐛 故障排除

### 问题 1: Docker 镜像拉取失败

**错误**：
```
Error response from daemon: failed to resolve reference
```

**解决方案**：
1. 检查网络连接
2. 配置 Docker 代理
3. 或使用演示模式（无需数据库）

### 问题 2: 端口已被占用

**错误**：
```
Bind for 0.0.0.0:7474 failed: port is already allocated
```

**解决方案**：
```bash
# 查找占用端口的进程
lsof -i :7474
lsof -i :7687

# 停止旧容器
docker stop neo4j
docker rm neo4j

# 重新启动
scripts/setup-neo4j.sh
```

### 问题 3: 初始化失败

**错误**：
```
Failed to connect to Neo4j
```

**解决方案**：
1. 确保容器正在运行：`docker ps | grep neo4j`
2. 检查日志：`docker logs neo4j`
3. 等待容器完全启动（约 30 秒）
4. 重试初始化：`cd backend && python scripts/init_neo4j.py`

### 问题 4: 连接被拒绝

**解决方案**：
```bash
# 重启容器
docker restart neo4j

# 等待启动
sleep 10

# 测试连接
curl http://localhost:7474
```

## 🔄 演示模式 vs Neo4j 模式

| 特性 | 演示模式 | Neo4j 模式 |
|------|---------|-----------|
| 安装难度 | ⭐ 简单 | ⭐⭐⭐ 中等 |
| 启动速度 | ⚡ 快速 | 🐢 较慢 |
| 数据查询 | 基于 JSON | 图查询 |
| 复杂关系查询 | 有限 | 完整支持 |
| 适用场景 | 演示、开发 | 生产、研究 |

## 💡 推荐使用场景

### 使用演示模式

- ✅ 快速演示系统功能
- ✅ 日常开发测试
- ✅ 没有 Docker 环境
- ✅ 不需要复杂图查询

### 使用 Neo4j 模式

- ✅ 生产环境部署
- ✅ 研究课程关系网络
- ✅ 需要复杂路径查询
- ✅ 大规模数据分析
- ✅ 多用户并发访问

## 📚 相关文档

- [安装指南](docs/installation.md) - 详细安装步骤
- [API 文档](docs/api.md) - 后端 API 接口
- [Neo4j 官方文档](https://neo4j.com/docs/) - 深入学习

---

**提示**：系统默认使用演示模式，所有功能都可以正常使用。只有在需要图数据库特性时才需要安装 Neo4j。
