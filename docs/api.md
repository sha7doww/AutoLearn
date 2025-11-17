# SmartPath API 文档

后端RESTful API接口说明。

---

## 🔗 基础信息

- **Base URL**: `http://localhost:8000`
- **API文档**: `http://localhost:8000/docs` (Swagger UI)
- **备用文档**: `http://localhost:8000/redoc` (ReDoc)
- **健康检查**: `http://localhost:8000/health`

---

## 📡 课程管理 API

### 获取所有课程

```http
GET /api/courses/
```

**响应示例**:
```json
[
  {
    "id": 1,
    "label": "数学分析",
    "difficulty": "较难",
    "credits": 6.0,
    "course_type": "必修"
  }
]
```

### 获取课程详情

```http
GET /api/courses/{course_id}
```

**路径参数**:
- `course_id` (integer): 课程ID

**响应示例**:
```json
{
  "id": 36,
  "label": "人工智能",
  "difficulty": "较难",
  "credits": 3.0,
  "course_type": "必修",
  "prerequisites": [29, 30, 33, 34, 35, 37, 1, 39],
  "knowledge_points": [],
  "description": "人工智能"
}
```

### 搜索课程

```http
POST /api/courses/search
```

**请求体**:
```json
{
  "keyword": "算法",
  "search_type": "fuzzy"  // "fuzzy" 或 "exact"
}
```

**响应示例**:
```json
{
  "courses": [...],
  "total": 3
}
```

### 查询先修关系

```http
POST /api/courses/prerequisites
```

**请求体**:
```json
{
  "course_id": 36,
  "max_depth": 5
}
```

**响应示例**:
```json
{
  "course_id": 36,
  "course_name": "人工智能",
  "path": [[29, 36], [30, 36], ...],
  "path_details": [...]
}
```

### 生成学习路径

```http
POST /api/courses/learning-path
```

**请求体**:
```json
{
  "target_course_id": 36,
  "completed_courses": [1, 30, 37, 39],
  "knowledge_state": {
    "数学基础": 0.75,
    "编程基础": 0.85
  }
}
```

**响应示例**:
```json
{
  "target_course_id": 36,
  "target_course_name": "人工智能",
  "recommended_sequence": [33, 34, 35, 29, 36],
  "course_details": [...],
  "total_credits": 15.0,
  "estimated_semesters": 1
}
```

### 获取统计信息

```http
GET /api/courses/stats/summary
```

**响应示例**:
```json
{
  "total_courses": 67,
  "total_relationships": 150
}
```

---

## 🧠 知识追踪 API

### 计算知识状态

```http
POST /api/knowledge/state
```

**请求体**:
```json
{
  "student_id": "student123",
  "course_scores": {
    "高等数学": 85,
    "线性代数": 78,
    "数据结构": 88
  }
}
```

**响应示例**:
```json
{
  "student_id": "student123",
  "knowledge_vector": {
    "数学基础": 0.72,
    "编程基础": 0.85,
    "算法基础": 0.78
  },
  "overall_level": 0.78,
  "strengths": ["编程基础", "算法基础"],
  "weaknesses": [],
  "calculated_at": "2024-11-17T12:00:00"
}
```

### 课程推荐

```http
POST /api/knowledge/recommend
```

**请求体**:
```json
{
  "student_id": "student123",
  "knowledge_state": {
    "数学基础": 0.72,
    "编程基础": 0.85
  },
  "completed_courses": [1, 30, 37],
  "max_recommendations": 5
}
```

**响应示例**:
```json
{
  "student_id": "student123",
  "recommendations": [
    {
      "course_id": 21,
      "course_name": "算法分析与设计",
      "reason": "满足先修要求，知识储备充分，难度适中",
      "match_score": 0.85,
      "difficulty_match": "中等",
      "prerequisites_met": true,
      "missing_prerequisites": []
    }
  ],
  "generated_at": "2024-11-17T12:00:00"
}
```

### 获取知识域列表

```http
GET /api/knowledge/domains
```

**响应示例**:
```json
{
  "domains": [
    "数学基础",
    "编程基础",
    "算法基础",
    "计算机系统",
    "人工智能"
  ],
  "total": 5
}
```

---

## 🔧 系统 API

### 健康检查

```http
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "database": "connected"  // 或 "disconnected" (演示模式)
}
```

### 根路径

```http
GET /
```

**响应示例**:
```json
{
  "name": "SmartPath API - KTAS System",
  "version": "0.1.0",
  "description": "Knowledge Tracking-Enhanced Agentic Search...",
  "endpoints": {
    "courses": "/api/courses",
    "knowledge": "/api/knowledge",
    "docs": "/docs",
    "redoc": "/redoc"
  }
}
```

---

## 📊 数据模型

### CourseBase

```typescript
{
  id: number
  label: string
  difficulty?: string  // "简单"|"中等"|"较难"|"困难"
  credits?: number
  course_type?: string  // "必修"|"选修"
}
```

### CourseDetail

```typescript
{
  ...CourseBase,
  prerequisites: number[]
  knowledge_points: string[]
  description?: string
}
```

### KnowledgeState

```typescript
{
  student_id: string
  knowledge_vector: {
    [domain: string]: number  // 0-1
  }
  overall_level: number  // 0-1
  strengths: string[]
  weaknesses: string[]
  calculated_at: datetime
}
```

### RecommendationItem

```typescript
{
  course_id: number
  course_name: string
  reason: string
  match_score: number  // 0-1
  difficulty_match: string
  prerequisites_met: boolean
  missing_prerequisites: number[]
}
```

---

## 🧪 测试示例

### cURL 示例

```bash
# 计算知识状态
curl -X POST http://localhost:8000/api/knowledge/state \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test",
    "course_scores": {"高等数学": 85, "数据结构": 88}
  }'

# 获取推荐
curl -X POST http://localhost:8000/api/knowledge/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test",
    "knowledge_state": {"数学基础": 0.75},
    "completed_courses": [1],
    "max_recommendations": 3
  }'
```

### Python 示例

```python
import requests

# 计算知识状态
response = requests.post(
    "http://localhost:8000/api/knowledge/state",
    json={
        "student_id": "test",
        "course_scores": {
            "高等数学": 85,
            "数据结构": 88
        }
    }
)
print(response.json())
```

### JavaScript 示例

```javascript
// 使用 axios
const response = await axios.post(
  'http://localhost:8000/api/knowledge/state',
  {
    student_id: 'test',
    course_scores: {
      '高等数学': 85,
      '数据结构': 88
    }
  }
);
console.log(response.data);
```

---

## ⚠️ 错误处理

### HTTP状态码

- **200** - 成功
- **404** - 资源未找到
- **422** - 请求参数验证失败
- **500** - 服务器内部错误

### 错误响应格式

```json
{
  "detail": "Course 999 not found"
}
```

---

## 🔐 认证

当前版本无需认证。未来版本将支持JWT Token认证。

---

## 📈 性能

- 平均响应时间: < 100ms
- 并发支持: 100+ req/s
- 数据库: Neo4j (或演示模式内存数据)

---

## 🔄 版本控制

当前版本: **v0.1.0**

主要功能:
- ✅ 课程查询和搜索
- ✅ IRT知识追踪
- ✅ 智能推荐
- ✅ 学习路径规划

---

## 📞 技术支持

查看 [使用手册](usage.md) 了解更多API使用示例。
