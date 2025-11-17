# SmartPath Backend API

Knowledge Tracking-Enhanced Agentic Search for Personalized Learning (KTAS)

## 快速开始

### 1. 设置 Python 环境

#### 使用 micromamba（推荐）

```bash
# 返回项目根目录
cd ..

# 运行环境设置脚本
./setup-environment.sh

# 激活环境
micromamba activate smart_path
```

#### 或使用传统方式

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置 Neo4j 数据库连接信息：

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### 3. 启动 Neo4j 数据库

使用 Docker 快速启动（推荐）：

```bash
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    -d neo4j:latest
```

或者使用本地安装的 Neo4j：

- 访问 https://neo4j.com/download/
- 下载并安装 Neo4j Desktop
- 创建新数据库，设置密码

### 4. 初始化数据库

运行初始化脚本导入课程数据：

```bash
python scripts/init_neo4j.py
```

### 5. 启动后端服务

```bash
# 确保环境已激活
micromamba activate smart_path

# 进入后端目录
cd backend

# 开发模式（自动重载）
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口

### 课程管理 (`/api/courses`)

- `GET /api/courses/` - 获取所有课程
- `GET /api/courses/{course_id}` - 获取课程详情
- `POST /api/courses/search` - 搜索课程
- `POST /api/courses/prerequisites` - 查询先修课程路径
- `POST /api/courses/learning-path` - 生成学习路径
- `GET /api/courses/stats/summary` - 知识图谱统计

### 知识追踪 (`/api/knowledge`)

- `POST /api/knowledge/state` - 计算知识状态
- `POST /api/knowledge/recommend` - 课程推荐
- `GET /api/knowledge/domains` - 获取知识领域列表

## 核心功能

### 1. IRT 知识追踪模型

基于 Item Response Theory 的知识状态估计：

```python
# 请求示例
POST /api/knowledge/state
{
  "student_id": "student123",
  "course_scores": {
    "高等数学": 85,
    "线性代数": 78,
    "程序设计基础": 92,
    "数据结构": 88
  }
}

# 响应示例
{
  "student_id": "student123",
  "knowledge_vector": {
    "数学基础": 0.72,
    "编程基础": 0.85,
    "算法基础": 0.78
  },
  "overall_level": 0.78,
  "strengths": ["编程基础", "算法基础"],
  "weaknesses": []
}
```

### 2. 智能课程推荐

基于知识状态的个性化推荐：

```python
# 请求示例
POST /api/knowledge/recommend
{
  "student_id": "student123",
  "knowledge_state": {
    "数学基础": 0.72,
    "编程基础": 0.85
  },
  "completed_courses": [1, 2, 3],
  "max_recommendations": 5
}

# 响应示例
{
  "recommendations": [
    {
      "course_id": 15,
      "course_name": "算法设计与分析",
      "reason": "满足先修要求，知识储备充分，难度适中",
      "match_score": 0.85,
      "difficulty_match": "中等",
      "prerequisites_met": true
    }
  ]
}
```

### 3. 学习路径规划

```python
POST /api/courses/learning-path
{
  "target_course_id": 50,
  "completed_courses": [1, 2, 3, 5],
  "knowledge_state": {...}
}
```

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── database/            # 数据库连接
│   │   ├── __init__.py
│   │   └── neo4j_driver.py
│   ├── routers/             # API 路由
│   │   ├── __init__.py
│   │   ├── courses.py
│   │   └── knowledge.py
│   ├── schemas/             # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── course.py
│   │   └── knowledge.py
│   └── services/            # 业务逻辑
│       ├── __init__.py
│       ├── course_service.py
│       └── knowledge_tracking.py
├── scripts/
│   └── init_neo4j.py        # 数据库初始化脚本
├── tests/                   # 测试
├── requirements.txt         # 依赖包
├── .env.example            # 环境变量示例
└── README.md
```

## 技术栈

- **FastAPI**: 现代、高性能的 Python Web 框架
- **Neo4j**: 图数据库，存储课程知识图谱
- **Pydantic**: 数据验证和设置管理
- **NumPy/SciPy**: 科学计算，用于 IRT 模型
- **Uvicorn**: ASGI 服务器

## 开发指南

### 添加新的 API 端点

1. 在 `app/schemas/` 中定义请求/响应模型
2. 在 `app/services/` 中实现业务逻辑
3. 在 `app/routers/` 中创建路由
4. 在 `app/main.py` 中注册路由

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black app/
isort app/
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t smartpath-backend .

# 运行容器
docker run -d \
  --name smartpath-api \
  -p 8000:8000 \
  --env-file .env \
  smartpath-backend
```

### 生产环境配置

1. 修改 `.env` 中的 `SECRET_KEY`
2. 配置 HTTPS
3. 设置防火墙规则
4. 配置日志记录
5. 启用速率限制

## 许可证

MIT License
