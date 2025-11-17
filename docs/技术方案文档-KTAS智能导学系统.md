# SmartPath - 基于知识追踪增强的智能体搜索式学习系统
## Knowledge Tracking-Enhanced Agentic Search for Personalized Learning (KTAS)

**文档日期**: 2025-11-17

---

## 目录

1. [项目背景与现状分析](#1-项目背景与现状分析)
2. [现有工作痛点与创新机会](#2-现有工作痛点与创新机会)
3. [核心创新点设计](#3-核心创新点设计)
4. [系统技术架构](#4-系统技术架构)
5. [详细实现方案](#5-详细实现方案)
6. [数据流程与算法设计](#6-数据流程与算法设计)
7. [实施路线图](#7-实施路线图)
8. [技术风险与应对](#8-技术风险与应对)
9. [预期成果与验证](#9-预期成果与验证)
10. [参考文献](#10-参考文献)

---

## 1. 项目背景与现状分析

### 1.1 原有项目现状

#### 已完成的工作
根据中期汇报和代码分析，原项目已实现：

| 模块 | 实现情况 | 技术栈 | 问题 |
|------|---------|--------|------|
| **3D知识图谱可视化** | ✅ 完成 | Three.js + Vue3 | 只有展示功能，无推荐逻辑 |
| **2D网络图** | ✅ 完成 | vis-network | 与3D图谱数据重复 |
| **课程详情页** | ⚠️ 部分完成 | Vue3 | 只有一个硬编码课程 |
| **AI聊天助手** | ⚠️ 部分完成 | DeepSeek API | 仅调用外部API，无知识集成 |
| **登录系统** | ❌ 假实现 | Vue3 | setTimeout跳转，无认证 |
| **后端系统** | ❌ 不存在 | 无 | 所有数据硬编码在前端 |
| **知识追踪** | ❌ 不存在 | 无 | 中期汇报声称有，实际无 |

#### 核心问题诊断

**技术层面**：
1. **数据管理混乱**：67门课程数据在4个文件中重复定义（HomeView.vue, myDagre.vue, ChatAssistant.vue, LsSb.vue）
2. **安全漏洞**：API密钥明文硬编码（已修复 - 现使用环境变量）
3. **架构缺失**：无后端、无数据库、无状态管理
4. **功能虚假**：声称的"Redis数据库"、"SpringBoot框架"、"个性化推荐"完全不存在

**创新层面**：
1. **无技术深度**：知识图谱只是Excel数据的3D可视化，无算法支撑
2. **无个性化**：所有用户看到同样的内容
3. **无智能性**：AI助手只是套壳ChatGPT，无领域知识整合

### 1.2 学术界与工业界现状

通过调研LLM4Edu和智能推荐系统领域（2024-2025年最新工作），发现：

#### 已有的相关工作

| 系统/方法 | 核心技术 | 局限性 |
|----------|---------|--------|
| **MultiTutor** (PMLR 2025) | 多Agent协作 + 信息检索 | 搜索策略固定，无个性化 |
| **PlanGlow** (L@S 2025) | LLM生成学习计划 + 资源验证 | 知识追踪缺失，规划静态 |
| **LPReKL** (Electronics 2024) | 知识追踪(KT) + LLM推荐 | KT与推荐割裂，无Agent |
| **Embedding+LLM推荐** (arXiv 2024) | 向量检索 + LLM解释 | 单次检索，无多步推理 |
| **Search-o1** (arXiv 2025) | Agentic RAG + 深度推理 | 通用搜索，未针对教育 |

#### 关键空白（我们的机会）

1. **知识追踪与Agentic Search的深度集成**
   - 现有工作：要么做KT，要么做Agent，很少结合
   - 空白：知识状态如何驱动搜索策略？

2. **元认知搜索（Meta-Cognitive Retrieval）**
   - 现有工作：只搜索"学什么"（课程内容）
   - 空白：如何搜索"怎么学"（学习策略）？

3. **同侪案例推理（Peer Case-Based Reasoning）**
   - 现有工作：基于课程相似度推荐
   - 空白：如何从成功学生的案例中学习？

4. **闭环知识追踪（Closed-Loop KT）**
   - 现有工作：推荐后就结束，无反馈
   - 空白：如何让搜索结果更新知识状态？

---

## 2. 现有工作痛点与创新机会

### 2.1 学生使用教育系统的真实痛点

通过调研和访谈（中期汇报提及的用户调研），学生的核心问题是：

| 痛点 | 现有系统的不足 | 我们的机会 |
|------|--------------|-----------|
| **不知道先修要求** | 只显示静态先修关系 | → 根据学生当前知识状态，动态判断是否满足 |
| **不知道课程难度** | 显示统一难度标签 | → 预测"对该学生"的难度（个性化） |
| **不知道怎么学** | 只推荐课程，不推荐方法 | → 检索成功案例的学习策略 |
| **选课后迷茫** | 推荐一次就结束 | → 持续追踪学习进展，动态调整 |
| **信息过载** | 返回大量无关信息 | → 根据知识缺口精准搜索 |

### 2.2 现有技术方案的三大问题

#### 问题1：搜索策略的"一刀切"

**现象**：
```
传统RAG/Agent的搜索逻辑：
  所有用户提问 → 同样的embedding → 同样的top-k检索 → 同样的LLM生成
```

**问题**：
- 基础薄弱的学生需要深度搜索（知识点级 + 学习方法）
- 基础良好的学生需要快速定位（课程级即可）
- 但现有系统不区分，浪费资源或信息不足

#### 问题2：知识追踪与推荐的"割裂"

**现象**：
```
典型流程：
  KT模型预测知识状态 → 传给推荐系统 → 推荐系统基于规则/协同过滤 → 结束
```

**问题**：
- KT结果只用于"初始化"推荐，后续学习数据不反馈
- 推荐系统不理解"为什么这个学生需要这个资源"
- 无法形成"推荐 → 学习 → 更新状态 → 再推荐"的闭环

#### 问题3：检索空间的"单一性"

**现象**：
```
现有RAG的检索来源：
  - 课程库（课程名、简介）
  - 课程资料（教材、PPT）

缺失：
  - 学习策略库（费曼学习法、间隔重复等）
  - 成功案例库（相似学生的学习路径）
  - 诊断性资源（针对特定错误模式的习题）
```

**问题**：
学生问"我数学不好，能学AI吗？"
- 传统系统：检索AI的数学要求 → "需要线性代数"
- 缺失信息：数学薄弱的学生如何成功学AI的案例？有哪些替代路径？

---

## 3. 核心创新点设计

基于上述分析，我们提出**KTAS (Knowledge Tracking-Enhanced Agentic Search)** 架构，包含**4个核心创新点**：

### 创新点1：Knowledge-Aware Search Planning（知识感知的搜索规划）

#### 创新内容
**不同知识状态 → 不同搜索策略**

| 学生类型 | 知识状态特征 | 搜索策略 | 搜索深度 | 搜索来源 |
|---------|------------|---------|---------|---------|
| 基础薄弱型 | k_avg < 0.5 | 深度优先 | 3层（课程→章节→知识点） | 基础资料 + 学习策略 |
| 知识缺口型 | 部分k < 0.4 | 定向深挖 | 2层（课程→缺口知识点） | 诊断性资源 |
| 基础良好型 | k_avg > 0.7 | 广度优先 | 1层（课程级） | 进阶课程 + 项目 |
| 目标明确型 | 有明确终点 | 路径规划 | 全局优化 | 学习路径库 |

#### 技术实现要点

```python
class KnowledgeAwareSearchPlanner:
    def plan_search_strategy(self, query, knowledge_state):
        # 1. 解析查询目标
        target = self.parse_target(query)  # "机器学习"

        # 2. 计算知识缺口
        required_knowledge = self.kg.get_prerequisites(target)
        gap = self.calculate_gap(knowledge_state, required_knowledge)
        # gap = {
        #   "severity": "high",  # 缺口程度
        #   "missing": ["线性代数", "概率论"],
        #   "weak": ["微积分"]  # 掌握但不扎实
        # }

        # 3. 自适应规划
        if gap['severity'] == 'high':
            return SearchPlan(
                depth=3,  # 深度搜索
                tools=['search_kg', 'search_materials', 'search_strategies'],
                max_iterations=6,  # 允许更多搜索步骤
                focus='foundation'
            )
        else:
            return SearchPlan(
                depth=1,
                tools=['search_kg', 'search_courses'],
                max_iterations=3,
                focus='advanced'
            )
```

#### 与现有工作的区别

| 维度 | MultiTutor | PlanGlow | KTAS（我们） |
|------|-----------|---------|-------------|
| 搜索策略 | 固定的多Agent并行 | 固定的规划流程 | 根据知识状态动态调整 |
| 个性化 | 基于用户输入 | 基于用户偏好 | 基于知识掌握度 |
| 搜索深度 | 固定 | 固定 | 自适应（1-3层） |

---

### 创新点2：Meta-Cognitive Retrieval（元认知检索）

#### 创新内容
**不只检索"学什么"，还检索"怎么学"**

传统RAG vs 元认知检索：

```
学生问："我数学基础差，想学机器学习，怎么办？"

【传统RAG】
检索内容：机器学习的数学要求
返回：线性代数、概率论、微积分
回答："建议先学习线性代数和概率论"

【元认知检索（我们的）】
检索内容1：机器学习的数学要求（同传统）
检索内容2：数学薄弱学生成功学ML的案例 🆕
检索内容3：针对数学弱者的学习策略 🆕

返回：
"根据50个相似背景学生的分析：
 - 成功路径（成功率72%）：先学《深度学习的数学》（比传统线代更直观）
 - 关键策略：边做项目边补数学（而非先学完数学再学ML）
 - 学习方法：用代码实现每个数学公式（费曼学习法）
 - 时间分配：每天1小时数学 + 1小时编程实践
 - 风险提示：直接学传统线代课程，类似背景学生挂科率58%"
```

#### 元认知检索的三层架构

```
Layer 1: Content Retrieval（内容检索）
  └─ 检索对象：课程资料、知识点定义
  └─ 回答："是什么"

Layer 2: Strategy Retrieval（策略检索）🆕
  └─ 检索对象：学习策略库（费曼法、间隔重复、刻意练习...）
  └─ 回答："怎么做"

Layer 3: Case Retrieval（案例检索）🆕
  └─ 检索对象：成功/失败学生案例
  └─ 回答："别人怎么成功的"
```

#### 技术实现要点

**策略库构建**：
```python
learning_strategies = {
    "费曼学习法": {
        "description": "用简单语言解释复杂概念",
        "适用场景": ["概念理解", "知识内化"],
        "知识点": ["抽象概念", "原理性内容"],
        "效果数据": {"理解度提升": 0.35, "记忆保持": 0.42}
    },
    "代码实现法": {
        "description": "用编程实现数学公式/算法",
        "适用场景": ["数学薄弱但编程强"],
        "知识点": ["线性代数", "概率论", "优化算法"],
        "效果数据": {"掌握度提升": 0.28, "应用能力": 0.51}
    },
    # ... 20+ 策略
}
```

**案例库schema**：
```python
case_schema = {
    "student_id": "匿名ID",
    "background": {
        "knowledge_state": [0.45, 0.60, ...],  # 初始知识向量
        "major": "计算机科学",
        "gpa": 3.2
    },
    "goal": "学习机器学习",
    "learning_path": [
        {"course": "深度学习的数学", "grade": 85, "time": "2024-03"},
        {"course": "机器学习", "grade": 88, "time": "2024-09"}
    ],
    "strategies_used": ["代码实现法", "项目驱动"],
    "outcome": "success",
    "key_factors": ["每天编程2小时", "参加Kaggle竞赛"]
}
```

#### 与现有工作的区别

**现有工作均未实现元认知检索**，这是完全的创新。

---

### 创新点3：Closed-Loop Knowledge Tracking（闭环知识追踪）

#### 创新内容
**搜索结果反馈到知识追踪，形成持续优化循环**

传统流程 vs 闭环流程：

```
【传统：单向流程】
KT预测知识状态 → Agent搜索推荐 → 展示给用户 → 结束

问题：
- 3个月后学生回来问"下一步学什么"，系统不知道这3个月发生了什么
- 无法利用学习过程中的数据（做题记录、学习时长）

【闭环：持续迭代】
t0: KT状态 K₀ → Agent搜索 → 推荐资源R₁
t1: 学生学习R₁ → 产生数据D₁（做题、测试）
t2: KT更新 K₁ ← D₁ → 检测变化ΔK
t3: 如果ΔK显著 → Agent重新规划 → 推荐R₂
t4: 学生学习R₂ → 产生数据D₂
t5: KT更新 K₂ ← D₂
... 持续循环
```

#### 闭环的三个关键机制

**机制1：知识状态的持续更新**
```python
class ClosedLoopKT:
    def update_from_learning_data(self, student_id, new_data):
        """
        new_data = {
            "exercise_results": [
                {"knowledge": "矩阵乘法", "correct": True, "time": 30},
                {"knowledge": "特征值", "correct": False, "time": 120},
                ...
            ],
            "study_time": {"线性代数": 120},  # 分钟
            "completed_resources": ["视频1", "习题集A"]
        }
        """
        # 1. 从做题结果更新知识掌握度
        for exercise in new_data['exercise_results']:
            self.kt_model.update(
                student_id,
                exercise['knowledge'],
                is_correct=exercise['correct']
            )

        # 2. 考虑学习时长（时间越长，遗忘越少）
        self.kt_model.apply_decay_with_time(student_id, new_data['study_time'])

        # 3. 返回新的知识状态
        return self.kt_model.get_state(student_id)
```

**机制2：变化检测与重规划触发**
```python
def detect_significant_change(K_old, K_new, threshold=0.1):
    """
    检测知识状态是否有显著变化
    """
    delta_K = K_new - K_old

    # 策略1：任一知识点变化超过阈值
    if np.max(np.abs(delta_K)) > threshold:
        return True, delta_K

    # 策略2：平均变化超过阈值
    if np.mean(np.abs(delta_K)) > threshold * 0.5:
        return True, delta_K

    return False, delta_K

# 使用
changed, delta = detect_significant_change(K_old, K_new)
if changed:
    # 触发Agent重新规划
    agent.replan(K_new, reason=f"知识状态显著变化: {delta}")
```

**机制3：元认知状态的更新**
```python
meta_cognitive_state = {
    "learning_style": "visual",  # 学习风格
    "struggle_patterns": ["特征值概念", "抽象证明"],  # 困难模式
    "effective_strategies": ["代码实现法"],  # 有效策略
    "study_pace": "slow_but_steady"  # 学习节奏
}

# 从学习数据中更新元认知状态
def update_meta_cognitive(student_id, learning_data):
    # 如果学生在某类问题上反复出错
    if count_errors(learning_data, pattern="抽象证明") > 5:
        meta_state['struggle_patterns'].append("抽象证明")

    # 如果某策略有效
    if strategy_effectiveness(learning_data, "代码实现法") > 0.8:
        meta_state['effective_strategies'].append("代码实现法")
```

#### 与现有工作的区别

| 系统 | 是否有KT | 是否有反馈 | 反馈频率 | 自动重规划 |
|------|---------|-----------|---------|-----------|
| LPReKL | ✅ | ❌ | - | ❌ |
| PlanGlow | ❌ | ⚠️ (用户手动) | 手动触发 | ❌ |
| KTAS（我们） | ✅ | ✅ | 实时/每次学习后 | ✅ |

---

### 创新点4：Peer Case-Based Reasoning（同侪案例推理）

#### 创新内容
**从"相似背景的成功学生"的学习路径中学习**

核心思想：
```
传统推荐：基于课程相似度
  "你想学A课程 → 学过A的人还学了B → 推荐B"

案例推理（我们）：基于学生相似度
  "你的背景是X → 找到背景相似的学生 → 分析他们的成功/失败路径 → 提取模式"
```

#### 案例推理的四个步骤

**Step 1: 学生相似度计算**
```python
def calculate_student_similarity(student_A, student_B):
    """
    多维度相似度
    """
    # 1. 知识向量相似度（余弦相似度）
    knowledge_sim = cosine_similarity(
        student_A['knowledge_vector'],
        student_B['knowledge_vector']
    )

    # 2. 背景相似度
    background_sim = 0
    if student_A['major'] == student_B['major']:
        background_sim += 0.3
    if abs(student_A['gpa'] - student_B['gpa']) < 0.5:
        background_sim += 0.2

    # 3. 学习风格相似度
    style_sim = jaccard_similarity(
        student_A['learning_style'],
        student_B['learning_style']
    )

    # 加权综合
    total_sim = 0.5 * knowledge_sim + 0.3 * background_sim + 0.2 * style_sim
    return total_sim
```

**Step 2: 案例检索与过滤**
```python
def retrieve_relevant_cases(student_profile, target_goal, top_k=50):
    """
    检索相似案例
    """
    # 1. 从案例库中找相似学生
    all_students = case_database.get_all_students()
    similarities = [
        (s, calculate_student_similarity(student_profile, s))
        for s in all_students
    ]
    similar_students = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]

    # 2. 过滤：只要有相同目标的案例
    relevant_cases = [
        s for s, sim in similar_students
        if target_goal in s['learning_history']
    ]

    return relevant_cases
```

**Step 3: 成功模式提取**
```python
def extract_success_patterns(cases):
    """
    从成功案例中提取共性
    """
    success_cases = [c for c in cases if c['outcome'] == 'success']
    failure_cases = [c for c in cases if c['outcome'] == 'failure']

    # 提取成功者的共同路径
    from collections import Counter

    # 学习路径
    paths = [tuple(c['course_sequence']) for c in success_cases]
    most_common_path = Counter(paths).most_common(1)[0][0]

    # 使用的策略
    strategies = [s for c in success_cases for s in c['strategies_used']]
    common_strategies = Counter(strategies).most_common(3)

    # 学习时长
    avg_study_time = np.mean([c['total_study_time'] for c in success_cases])

    return {
        "recommended_path": most_common_path,
        "key_strategies": [s[0] for s in common_strategies],
        "expected_time": avg_study_time,
        "success_rate": len(success_cases) / len(cases)
    }
```

**Step 4: 对比分析（成功 vs 失败）**
```python
def compare_success_failure(success_cases, failure_cases):
    """
    找出成功者与失败者的关键差异
    """
    differences = {}

    # 差异1: 学习顺序
    success_first_courses = Counter([c['course_sequence'][0] for c in success_cases])
    failure_first_courses = Counter([c['course_sequence'][0] for c in failure_cases])

    # 差异2: 学习时长
    success_avg_time = np.mean([c['total_study_time'] for c in success_cases])
    failure_avg_time = np.mean([c['total_study_time'] for c in failure_cases])

    # 差异3: 使用的资源
    success_resources = set([r for c in success_cases for r in c['resources_used']])
    failure_resources = set([r for c in failure_cases for r in c['resources_used']])
    unique_to_success = success_resources - failure_resources

    return {
        "first_course_impact": (success_first_courses, failure_first_courses),
        "time_difference": success_avg_time - failure_avg_time,
        "critical_resources": unique_to_success
    }
```

#### 输出示例

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 基于同侪案例的学习路径分析

您的背景画像：
- 知识状态：线性代数 0.45 | 概率论 0.60 | 编程 0.80
- 专业：计算机科学
- GPA: 3.2

找到 45 个相似背景学生的案例
├─ 成功者：32人（71%）
└─ 失败者：13人（29%）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 成功路径（基于32个成功案例）

推荐学习顺序：
1️⃣ 《深度学习的数学基础》（28人选择，通过率89%）
   ⚠️ 而非传统《线性代数》（只有4人选择，通过率50%）

2️⃣ 《Python数据分析》（并行学习，25人选择）

3️⃣ 《机器学习入门》（32人最终到达）

关键成功因素：
- 🔑 学习策略：87%使用"代码实现法"学数学
- ⏱️ 时间投入：平均每周12小时（失败者仅6小时）
- 📚 核心资源：3Blue1Brown视频 + 《深度学习》书籍

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 失败案例分析（13人）

常见错误：
- 62% 直接学传统线代课程 → 感觉太抽象 → 放弃
- 54% 只看理论不动手 → 无法理解应用 → 挂科
- 38% 低估时间投入 → 准备不足 → 考试失败

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 个性化建议

根据您的编程优势（0.80），建议采用"代码优先"策略：
- 先学Python实现矩阵运算（巩固编程，顺便学数学）
- 每学一个数学概念，立即用NumPy实现
- 参考案例学生B（相似度94%）的Jupyter笔记

预测成功率：76%（基于历史数据）
预计学习时长：3-4个月（每周10-12小时）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### 与现有工作的区别

**所有调研的工作均未实现同侪案例推理**，这是完全的创新。

---

## 4. 系统技术架构

### 4.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                          前端层 (Vue 3)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │
│  │ 3D知识图谱    │  │ 智能对话界面  │  │ 学习路径规划 │  │ 仪表盘   │ │
│  │ (Three.js)   │  │ (Chat UI)    │  │ (Timeline)   │  │ (Charts) │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                ↓ ↑ (HTTP/WebSocket)
┌─────────────────────────────────────────────────────────────────────┐
│                        API网关层 (FastAPI)                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ RESTful API      WebSocket      JWT Auth      Rate Limiting   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                ↓ ↑
┌─────────────────────────────────────────────────────────────────────┐
│                       核心算法层 (Python)                             │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │              KTAS Agent (LangChain/LangGraph)                  ││
│  │  ┌──────────────────────────────────────────────────────────┐ ││
│  │  │ Knowledge State Encoder (知识状态编码器)                  │ ││
│  │  │  - Input: 成绩、做题记录、学习行为                        │ ││
│  │  │  - Model: IRT / Simplified DKT                           │ ││
│  │  │  - Output: Knowledge Vector K + Meta-Cognitive State M  │ ││
│  │  └──────────────────────────────────────────────────────────┘ ││
│  │  ┌──────────────────────────────────────────────────────────┐ ││
│  │  │ Adaptive Search Planner (自适应搜索规划器)                │ ││
│  │  │  - Input: Query + K + M                                  │ ││
│  │  │  - Logic: 根据知识状态规划搜索策略                       │ ││
│  │  │  - Output: SearchPlan (tools, depth, max_steps)         │ ││
│  │  └──────────────────────────────────────────────────────────┘ ││
│  │  ┌──────────────────────────────────────────────────────────┐ ││
│  │  │ ReAct Agent Loop (推理-行动循环)                          │ ││
│  │  │  - Thought → Action → Observation → Thought ...         │ ││
│  │  │  - Tools: 5-8个专用工具                                  │ ││
│  │  │  - LLM: Qwen-7B (规划) + GPT-4 (生成)                   │ ││
│  │  └──────────────────────────────────────────────────────────┘ ││
│  │  ┌──────────────────────────────────────────────────────────┐ ││
│  │  │ Knowledge Update Loop (知识更新循环)                      │ ││
│  │  │  - 检测学习数据 → 更新KT → 触发重规划                    │ ││
│  │  └──────────────────────────────────────────────────────────┘ ││
│  └────────────────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────────────────┐│
│  │                   Agent工具箱 (Tools)                          ││
│  │  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐    ││
│  │  │ Tool 1:      │ │ Tool 2:      │ │ Tool 3:            │    ││
│  │  │ SearchKG     │ │ RAGSearch    │ │ MetaCognitiveSearch│    ││
│  │  │ (Neo4j)      │ │ (Milvus)     │ │ (自实现)            │    ││
│  │  └──────────────┘ └──────────────┘ └────────────────────┘    ││
│  │  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐    ││
│  │  │ Tool 4:      │ │ Tool 5:      │ │ Tool 6:            │    ││
│  │  │ PeerCase     │ │ GetStudent   │ │ CalcRisk           │    ││
│  │  │ Search       │ │ Profile      │ │ (XGBoost)          │    ││
│  │  └──────────────┘ └──────────────┘ └────────────────────┘    ││
│  └────────────────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────────────────┐│
│  │              辅助算法模块                                       ││
│  │  - 知识追踪 (IRT Model)                                        ││
│  │  - 推荐算法 (LightGCN - 可选)                                  ││
│  │  - 风险预测 (XGBoost Classifier)                               ││
│  │  - 相似度计算 (Cosine + Jaccard)                               ││
│  └────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
                                ↓ ↑
┌─────────────────────────────────────────────────────────────────────┐
│                       数据存储层                                      │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────────┐  │
│  │ Neo4j          │  │ Milvus         │  │ PostgreSQL          │  │
│  │ (知识图谱)      │  │ (向量数据库)    │  │ (业务数据)           │  │
│  │ - 课程节点      │  │ - 课程资料      │  │ - 用户信息           │  │
│  │ - 知识点节点    │  │ - 学习策略      │  │ - 成绩数据           │  │
│  │ - 依赖关系      │  │ - 成功案例      │  │ - 学习行为日志       │  │
│  └────────────────┘  └────────────────┘  └─────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Redis (缓存层)                                              │   │
│  │ - 推理路径缓存  - 知识状态缓存  - Session管理                │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 技术栈选型

#### 前端技术栈

| 模块 | 技术选型 | 理由 | 复用原有代码 |
|------|---------|------|-------------|
| 框架 | Vue 3 (Composition API) | 团队熟悉，生态成熟 | ✅ 100% |
| UI库 | Element Plus | 已在用，组件丰富 | ✅ 100% |
| 3D可视化 | Three.js + OrbitControls | 已实现，效果好 | ✅ 90% (优化交互) |
| 2D图谱 | Cytoscape.js (替换vis-network) | 更强大，支持复杂布局 | ❌ 重写 |
| 图表 | ECharts | 数据可视化标准 | 🆕 新增 |
| 状态管理 | Pinia | Vue 3官方推荐 | 🆕 新增 |
| HTTP | Axios | 已在用 | ✅ 100% |
| 路由 | Vue Router 4 | 已在用 | ✅ 100% |

#### 后端技术栈

| 模块 | 技术选型 | 理由 |
|------|---------|------|
| Web框架 | FastAPI | 异步高性能，类型安全，自动文档 |
| Agent框架 | LangChain + LangGraph | 成熟的Agent工具链，社区活跃 |
| LLM | Qwen-7B (本地) + DeepSeek (云) | 成本控制 + 质量保证 |
| KT模型 | PyKT (IRT实现) | 开源库，快速上手 |
| 深度学习 | PyTorch | 灵活，社区大 |
| 图计算 | NetworkX | Python标准图算法库 |

#### 数据存储技术栈

| 数据类型 | 技术选型 | Schema设计 |
|---------|---------|-----------|
| **知识图谱** | Neo4j 5.x | 节点：Course, Knowledge, Student<br>边：PREREQUISITE, CONTAINS, LEARNED |
| **向量数据** | Milvus 2.x | Collection: course_materials, strategies, cases |
| **关系数据** | PostgreSQL 15 | 表：users, grades, learning_logs, exercises |
| **缓存** | Redis 7.x | Key: reasoning_paths, knowledge_states, sessions |

#### LLM配置策略

```python
llm_config = {
    "规划阶段": {
        "model": "qwen-7b-chat",
        "deployment": "本地vLLM",
        "cost": "免费",
        "latency": "~500ms",
        "用途": "Agent的Thought生成、工具选择"
    },
    "生成阶段": {
        "model": "deepseek-chat",
        "deployment": "API",
        "cost": "~¥0.002/次",
        "latency": "~2s",
        "用途": "最终答案生成、解释性文本"
    },
    "Embedding": {
        "model": "bge-large-zh-v1.5",
        "deployment": "本地",
        "cost": "免费",
        "用途": "向量检索、相似度计算"
    }
}
```

---

## 5. 详细实现方案

### 5.1 知识状态编码器（Knowledge State Encoder）

#### 输入数据

```python
student_data = {
    "student_id": "10225102471",
    "courses_taken": [
        {"name": "高等数学", "grade": 85, "semester": "2023-1"},
        {"name": "线性代数", "grade": 72, "semester": "2023-2"},
        {"name": "概率论", "grade": 78, "semester": "2024-1"}
    ],
    "exercise_logs": [
        {"knowledge": "矩阵运算", "correct": True, "time": 30, "date": "2024-11-01"},
        {"knowledge": "特征值", "correct": False, "time": 120, "date": "2024-11-01"},
        # ... 100+ 条记录
    ],
    "learning_behaviors": {
        "study_time_per_week": 10,  # 小时
        "login_frequency": 5,  # 次/周
        "resource_access": ["video", "textbook", "exercise"]
    }
}
```

#### IRT模型实现

```python
from pykt.models import IRT
import torch

class KnowledgeStateEncoder:
    def __init__(self):
        self.irt_model = IRT(
            n_students=1000,  # 预估学生数
            n_items=500,      # 知识点数量
            n_knowledge=50    # 粗粒度知识概念
        )

    def encode(self, student_data):
        """
        编码学生知识状态

        Returns:
            knowledge_vector: [k1, k2, ..., k50] 每个值在[0,1]
            meta_cognitive_state: dict
        """
        # 1. 从成绩推断初始知识状态
        grade_based_state = self._infer_from_grades(
            student_data['courses_taken']
        )

        # 2. 从做题记录细化知识状态
        if student_data['exercise_logs']:
            exercise_based_state = self._update_from_exercises(
                grade_based_state,
                student_data['exercise_logs']
            )
        else:
            exercise_based_state = grade_based_state

        # 3. 提取元认知状态
        meta_state = self._extract_meta_cognitive(student_data)

        return exercise_based_state, meta_state

    def _infer_from_grades(self, courses):
        """
        从成绩推断知识掌握度
        """
        knowledge_state = np.zeros(50)

        # 课程→知识点映射（预先定义）
        course_knowledge_map = {
            "线性代数": {
                "矩阵运算": 0.4,
                "线性方程组": 0.3,
                "特征值": 0.3
            },
            "概率论": {
                "概率基础": 0.4,
                "随机变量": 0.4,
                "统计推断": 0.2
            }
            # ... 更多课程
        }

        for course in courses:
            normalized_grade = course['grade'] / 100

            # 分配到各知识点
            if course['name'] in course_knowledge_map:
                for knowledge, weight in course_knowledge_map[course['name']].items():
                    idx = self.knowledge_to_idx[knowledge]
                    knowledge_state[idx] = normalized_grade

        return knowledge_state

    def _update_from_exercises(self, initial_state, exercise_logs):
        """
        用IRT模型从做题记录更新知识状态
        """
        # 准备IRT输入
        responses = []
        for log in exercise_logs:
            knowledge_idx = self.knowledge_to_idx[log['knowledge']]
            responses.append({
                'item_id': knowledge_idx,
                'correct': 1 if log['correct'] else 0
            })

        # IRT估计学生能力
        theta = self.irt_model.estimate_ability(responses)

        # 结合初始状态和IRT估计
        updated_state = 0.6 * initial_state + 0.4 * theta

        return updated_state

    def _extract_meta_cognitive(self, student_data):
        """
        提取元认知状态
        """
        # 分析错误模式
        errors = [log for log in student_data['exercise_logs'] if not log['correct']]
        error_knowledge = [e['knowledge'] for e in errors]
        struggle_patterns = [k for k, count in Counter(error_knowledge).items() if count >= 3]

        # 学习风格（基于行为）
        if 'video' in student_data['learning_behaviors']['resource_access']:
            learning_style = 'visual'
        elif student_data['learning_behaviors']['study_time_per_week'] > 15:
            learning_style = 'intensive'
        else:
            learning_style = 'moderate'

        return {
            'struggle_patterns': struggle_patterns,
            'learning_style': learning_style,
            'study_pace': 'fast' if student_data['learning_behaviors']['study_time_per_week'] > 12 else 'normal'
        }
```

### 5.2 自适应搜索规划器（Adaptive Search Planner）

```python
class AdaptiveSearchPlanner:
    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph

    def plan(self, query, knowledge_state, meta_state):
        """
        根据知识状态规划搜索策略

        Returns:
            SearchPlan对象
        """
        # 1. 解析查询意图
        intent = self._parse_intent(query)
        # intent = {
        #   'type': 'course_recommendation',  # 或 'learning_strategy', 'difficulty_inquiry'
        #   'target': '机器学习',
        #   'constraints': ['数学基础薄弱']
        # }

        # 2. 计算知识缺口
        if intent['type'] == 'course_recommendation':
            required_knowledge = self.kg.get_prerequisites(intent['target'])
            gap = self._calculate_gap(knowledge_state, required_knowledge)
        else:
            gap = {'severity': 'low'}

        # 3. 规划搜索策略
        if gap['severity'] == 'high':
            # 基础薄弱 → 深度搜索
            plan = SearchPlan(
                depth=3,
                tools=[
                    'search_knowledge_graph',      # 查依赖关系
                    'search_learning_materials',   # 搜基础资料
                    'meta_cognitive_search',       # 搜学习策略 🔥
                    'peer_case_search'             # 搜成功案例 🔥
                ],
                max_iterations=6,
                focus='foundation',
                granularity='knowledge_point'  # 知识点级
            )
        elif gap['severity'] == 'medium':
            plan = SearchPlan(
                depth=2,
                tools=[
                    'search_knowledge_graph',
                    'search_learning_materials',
                    'calculate_difficulty'
                ],
                max_iterations=4,
                focus='balanced',
                granularity='chapter'  # 章节级
            )
        else:
            # 基础良好 → 浅度快速搜索
            plan = SearchPlan(
                depth=1,
                tools=[
                    'search_knowledge_graph',
                    'search_courses'
                ],
                max_iterations=3,
                focus='advanced',
                granularity='course'  # 课程级
            )

        # 4. 考虑元认知状态
        if 'abstract_proof' in meta_state['struggle_patterns']:
            # 如果学生在抽象证明上有困难，优先推荐应用型资源
            plan.add_constraint('prefer_applied_resources')

        return plan

    def _calculate_gap(self, current_state, required_state):
        """
        计算知识缺口
        """
        gap_vector = required_state - current_state
        gap_vector[gap_vector < 0] = 0  # 已掌握的不算缺口

        severity_score = np.mean(gap_vector)

        if severity_score > 0.4:
            severity = 'high'
        elif severity_score > 0.2:
            severity = 'medium'
        else:
            severity = 'low'

        missing_knowledge = [
            self.idx_to_knowledge[i]
            for i, gap in enumerate(gap_vector)
            if gap > 0.3
        ]

        return {
            'severity': severity,
            'score': severity_score,
            'missing': missing_knowledge
        }
```

### 5.3 Agent工具实现

#### Tool 1: search_knowledge_graph

```python
from langchain.tools import Tool

def search_knowledge_graph_func(query: str, relation: str = "prerequisite"):
    """
    在Neo4j知识图谱中查询

    Args:
        query: 课程名或知识点名
        relation: 关系类型 (prerequisite/followup/contains)

    Returns:
        JSON格式的查询结果
    """
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver("bolt://localhost:7687")

    cypher_query = """
    MATCH (c:Course {name: $course_name})-[:PREREQUISITE]->(prereq:Course)
    RETURN prereq.name AS name, prereq.importance AS importance
    ORDER BY prereq.importance DESC
    """

    with driver.session() as session:
        result = session.run(cypher_query, course_name=query)
        prerequisites = [
            {"course": record["name"], "importance": record["importance"]}
            for record in result
        ]

    return json.dumps(prerequisites, ensure_ascii=False)

# 注册为LangChain工具
search_kg_tool = Tool(
    name="SearchKnowledgeGraph",
    func=search_knowledge_graph_func,
    description="""
    在知识图谱中查询课程关系。
    输入：课程名称（例如："机器学习"）
    输出：先修课程列表及其重要性
    使用场景：当需要了解课程依赖关系时
    """
)
```

#### Tool 2: meta_cognitive_search

```python
def meta_cognitive_search_func(student_profile: str, learning_goal: str):
    """
    元认知检索：搜索学习策略和成功案例

    Args:
        student_profile: 学生画像JSON字符串
        learning_goal: 学习目标

    Returns:
        推荐的学习策略和案例
    """
    profile = json.loads(student_profile)

    # 1. 构建查询向量
    query_text = f"""
    学生背景：知识基础{profile['knowledge_level']}，学习风格{profile['learning_style']}
    学习目标：{learning_goal}
    困难点：{profile.get('struggles', '无')}
    """

    query_embedding = embedding_model.encode(query_text)

    # 2. 在策略库中检索
    strategy_results = milvus_client.search(
        collection_name="learning_strategies",
        data=[query_embedding],
        limit=3,
        output_fields=["strategy_name", "description", "effectiveness"]
    )

    # 3. 在案例库中检索相似学生
    case_results = milvus_client.search(
        collection_name="student_cases",
        data=[query_embedding],
        limit=5,
        output_fields=["background", "path", "outcome", "tips"]
    )

    # 4. 整合结果
    strategies = [
        {
            "name": hit.entity.get("strategy_name"),
            "description": hit.entity.get("description"),
            "effectiveness": hit.entity.get("effectiveness")
        }
        for hit in strategy_results[0]
    ]

    cases = [
        {
            "background": hit.entity.get("background"),
            "success_path": hit.entity.get("path"),
            "key_tips": hit.entity.get("tips")
        }
        for hit in case_results[0]
        if hit.entity.get("outcome") == "success"
    ]

    return json.dumps({
        "recommended_strategies": strategies,
        "peer_success_cases": cases
    }, ensure_ascii=False)

meta_cognitive_tool = Tool(
    name="MetaCognitiveSearch",
    func=meta_cognitive_search_func,
    description="""
    搜索学习策略和成功案例。
    输入：学生画像和学习目标
    输出：推荐的学习方法、相似学生的成功经验
    使用场景：当学生询问"怎么学"或遇到困难时
    """
)
```

#### Tool 3: peer_case_search

```python
def peer_case_search_func(student_id: str, target_course: str):
    """
    同侪案例检索
    """
    # 1. 获取学生知识状态
    student_profile = db.get_student_profile(student_id)
    student_vector = student_profile['knowledge_vector']

    # 2. 检索相似学生
    similar_students = db.query("""
        SELECT s.*,
               cosine_similarity(s.knowledge_vector, $1) AS similarity
        FROM students s
        WHERE s.student_id != $2
          AND EXISTS (
              SELECT 1 FROM course_history ch
              WHERE ch.student_id = s.student_id
                AND ch.course_name = $3
          )
        ORDER BY similarity DESC
        LIMIT 50
    """, student_vector, student_id, target_course)

    # 3. 分析成功/失败案例
    success_cases = [s for s in similar_students if s['course_grade'] >= 70]
    failure_cases = [s for s in similar_students if s['course_grade'] < 60]

    # 4. 提取成功模式
    if success_cases:
        # 提取共同的学习路径
        paths = [s['course_sequence_before_target'] for s in success_cases]
        most_common_path = Counter(paths).most_common(1)[0][0]

        # 提取关键策略
        strategies = [s['strategies_used'] for s in success_cases]
        common_strategies = Counter([s for sublist in strategies for s in sublist]).most_common(3)

        result = {
            "success_rate": len(success_cases) / len(similar_students),
            "sample_size": len(similar_students),
            "recommended_path": most_common_path,
            "key_strategies": [s[0] for s in common_strategies],
            "avg_study_time": np.mean([s['total_study_hours'] for s in success_cases]),
            "typical_case": {
                "similarity": success_cases[0]['similarity'],
                "background": success_cases[0]['background_summary'],
                "grade": success_cases[0]['course_grade'],
                "tips": success_cases[0]['learning_tips']
            }
        }
    else:
        result = {
            "success_rate": 0,
            "message": "未找到足够的成功案例，建议谨慎选择"
        }

    return json.dumps(result, ensure_ascii=False)

peer_case_tool = Tool(
    name="PeerCaseSearch",
    func=peer_case_search_func,
    description="""
    搜索相似背景学生的学习案例。
    输入：学生ID和目标课程
    输出：成功率、推荐路径、关键策略、典型案例
    使用场景：当学生询问"我这样的背景能学这门课吗"
    """
)
```

### 5.4 ReAct Agent主循环

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Agent Prompt模板
react_prompt = PromptTemplate.from_template("""
你是一个专业的学习路径规划助手，帮助学生制定个性化的课程学习计划。

当前学生的知识状态：
{knowledge_state}

元认知状态：
{meta_cognitive_state}

学生提问：
{input}

你可以使用以下工具来回答问题：
{tools}

请按照以下格式思考和行动：

Thought: 我需要分析这个问题，思考需要哪些信息
Action: [工具名称]
Action Input: [工具输入]
Observation: [工具返回结果]

... (重复Thought/Action/Observation多次)

Thought: 我现在有足够的信息可以回答了
Final Answer: [给学生的详细回答，包括学习路径、策略建议、预期效果]

开始！

{agent_scratchpad}
""")

# 创建Agent
llm = ChatOpenAI(model="gpt-4", temperature=0)

tools = [
    search_kg_tool,
    meta_cognitive_tool,
    peer_case_tool,
    # ... 其他工具
]

agent = create_react_agent(llm, tools, react_prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=6,
    handle_parsing_errors=True
)

# 使用Agent
def query_agent(student_id, question):
    # 1. 获取学生知识状态
    knowledge_state, meta_state = knowledge_encoder.encode(
        db.get_student_data(student_id)
    )

    # 2. 规划搜索策略
    search_plan = planner.plan(question, knowledge_state, meta_state)

    # 3. 执行Agent
    response = agent_executor.invoke({
        "input": question,
        "knowledge_state": str(knowledge_state),
        "meta_cognitive_state": str(meta_state)
    })

    # 4. 记录推理路径（用于缓存）
    reasoning_path = response['intermediate_steps']
    cache_reasoning_path(question, knowledge_state, reasoning_path)

    return response['output']
```

### 5.5 闭环知识更新

```python
class ClosedLoopKTAS:
    def __init__(self):
        self.kt_encoder = KnowledgeStateEncoder()
        self.agent = agent_executor
        self.db = PostgreSQLDatabase()

    def handle_learning_event(self, student_id, event_type, event_data):
        """
        处理学习事件，触发知识状态更新和重规划

        event_type:
            - 'exercise_completed': 完成练习
            - 'resource_finished': 完成学习资源
            - 'test_taken': 参加测试
        """
        # 1. 记录事件
        self.db.log_learning_event(student_id, event_type, event_data)

        # 2. 获取当前知识状态
        K_old, M_old = self.get_current_state(student_id)

        # 3. 根据新数据更新知识状态
        student_data = self.db.get_student_data(student_id)
        K_new, M_new = self.kt_encoder.encode(student_data)

        # 4. 检测显著变化
        delta_K = K_new - K_old
        significant_change = np.max(np.abs(delta_K)) > 0.1

        if significant_change:
            # 5. 触发重规划
            self._trigger_replan(student_id, K_new, M_new, delta_K)

        # 6. 保存新状态
        self.db.update_knowledge_state(student_id, K_new, M_new)

    def _trigger_replan(self, student_id, K_new, M_new, delta_K):
        """
        重新规划学习路径
        """
        # 分析变化
        improved_knowledge = [
            self.idx_to_knowledge[i]
            for i, d in enumerate(delta_K)
            if d > 0.1
        ]

        declined_knowledge = [
            self.idx_to_knowledge[i]
            for i, d in enumerate(delta_K)
            if d < -0.1
        ]

        # 生成反馈消息
        if improved_knowledge:
            message = f"检测到你在{improved_knowledge}上有明显进步！系统为你调整了后续学习计划。"

            # 调用Agent生成新推荐
            new_recommendations = self.agent.invoke({
                "input": f"学生在{improved_knowledge}上取得进步，请推荐下一步学习内容",
                "knowledge_state": str(K_new),
                "meta_cognitive_state": str(M_new)
            })

            # 推送给学生
            self.notify_student(student_id, message, new_recommendations)

        if declined_knowledge:
            message = f"注意：你在{declined_knowledge}上的掌握度下降，可能需要复习。"
            self.notify_student(student_id, message)
```

---

## 6. 数据流程与算法设计

### 6.1 完整数据流程图

```
用户提问："我基础薄弱，想学机器学习，怎么办？"
    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 1: 知识状态编码                                     │
│ Input: student_id = "10225102471"                      │
│ ├─ 查询数据库：成绩、做题记录                            │
│ ├─ IRT模型推断：K = [k₁, k₂, ..., k₅₀]               │
│ └─ 提取元认知：M = {struggle_patterns, style, ...}    │
│ Output: K = [0.45, 0.60, 0.80, ...], M = {...}        │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 2: 自适应搜索规划                                   │
│ Input: query + K + M                                    │
│ ├─ 解析意图：course_recommendation                      │
│ ├─ 计算知识缺口：gap_severity = "high"                 │
│ └─ 生成搜索计划：SearchPlan(depth=3, tools=[...])      │
│ Output: 深度搜索策略，包含4个工具                        │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 3: ReAct Agent执行                                 │
│                                                          │
│ Iteration 1:                                             │
│ ├─ Thought: "需要了解机器学习的前置要求"                │
│ ├─ Action: SearchKnowledgeGraph("机器学习")            │
│ └─ Observation: "需要：线性代数(0.8), 概率论(0.7)"      │
│                                                          │
│ Iteration 2:                                             │
│ ├─ Thought: "学生线性代数只有0.45，缺口大，需要了解     │
│             相似背景的学生怎么成功的"                    │
│ ├─ Action: PeerCaseSearch(student_id, "机器学习")      │
│ └─ Observation: "50个相似学生，成功率72%，              │
│                  推荐路径：[深度学习的数学→ML入门]"      │
│                                                          │
│ Iteration 3:                                             │
│ ├─ Thought: "基础薄弱，需要搜索适合的学习策略"          │
│ ├─ Action: MetaCognitiveSearch(profile, "机器学习")    │
│ └─ Observation: "推荐策略：代码实现法、项目驱动"        │
│                                                          │
│ Iteration 4:                                             │
│ ├─ Thought: "信息足够，可以生成答案"                    │
│ └─ Final Answer: [详细的学习路径 + 策略建议]            │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 4: 返回用户 + 记录                                  │
│ ├─ 格式化输出：Markdown格式的学习计划                   │
│ ├─ 缓存推理路径：用于相似问题快速响应                   │
│ └─ 记录交互日志：用于后续分析                           │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 5: 学生学习 (2周后)                                │
│ ├─ 学生完成"深度学习的数学"第1章                        │
│ ├─ 做题：10道题，正确8道                                │
│ └─ 触发学习事件                                          │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 6: 闭环更新                                         │
│ ├─ 更新KT：线性代数 0.45 → 0.55                        │
│ ├─ 检测变化：Δk = +0.10（显著）                        │
│ ├─ 触发重规划：Agent生成新推荐                          │
│ └─ 推送通知："你在线性代数上有进步！推荐下一步..."     │
└─────────────────────────────────────────────────────────┘
    ↓
循环迭代...
```

### 6.2 核心算法伪代码

#### 算法1：知识感知搜索规划

```python
Algorithm: Knowledge-Aware Search Planning

Input:
    query: 用户问题
    K: 知识状态向量 [k₁, k₂, ..., kₙ]
    M: 元认知状态 {struggle_patterns, learning_style, ...}

Output:
    SearchPlan: {tools, depth, max_iterations, focus}

Procedure:
1. intent ← ParseIntent(query)
   // 提取：目标课程、问题类型、约束条件

2. IF intent.type == "course_recommendation" THEN
3.     required_K ← KnowledgeGraph.GetPrerequisites(intent.target)
4.     gap ← CalculateGap(K, required_K)
5.     gap.severity ← ClassifySeverity(gap.score)
6. ELSE
7.     gap.severity ← "low"
8. END IF

9. // 根据知识缺口选择策略
10. IF gap.severity == "high" THEN
11.     depth ← 3
12.     tools ← [SearchKG, SearchMaterials, MetaCognitiveSearch, PeerCaseSearch]
13.     max_iter ← 6
14.     focus ← "foundation"
15.     granularity ← "knowledge_point"
16. ELSE IF gap.severity == "medium" THEN
17.     depth ← 2
18.     tools ← [SearchKG, SearchMaterials, CalculateDifficulty]
19.     max_iter ← 4
20.     focus ← "balanced"
21.     granularity ← "chapter"
22. ELSE
23.     depth ← 1
24.     tools ← [SearchKG, SearchCourses]
25.     max_iter ← 3
26.     focus ← "advanced"
27.     granularity ← "course"
28. END IF

29. // 考虑元认知状态调整
30. IF "abstract_proof" IN M.struggle_patterns THEN
31.     tools.AddConstraint("prefer_applied_resources")
32. END IF

33. RETURN SearchPlan(tools, depth, max_iter, focus, granularity)
```

#### 算法2：同侪案例推理

```python
Algorithm: Peer Case-Based Reasoning

Input:
    student_profile: 目标学生画像 {K, major, gpa, ...}
    target_course: 目标课程
    top_k: 检索相似学生数量

Output:
    recommendation: {success_rate, path, strategies, case_example}

Procedure:
1. // 检索相似学生
2. all_students ← Database.GetAllStudents()
3. similarities ← []
4. FOR each s IN all_students DO
5.     sim ← CalculateStudentSimilarity(student_profile, s)
6.     similarities.APPEND((s, sim))
7. END FOR

8. // 排序并过滤
9. similar_students ← TopK(similarities, k=top_k)
10. relevant_cases ← FILTER(similar_students,
                            WHERE target_course IN s.course_history)

11. // 分析成功/失败案例
12. success_cases ← FILTER(relevant_cases, WHERE s.grade >= 70)
13. failure_cases ← FILTER(relevant_cases, WHERE s.grade < 60)

14. // 提取成功模式
15. IF LENGTH(success_cases) > 0 THEN
16.     paths ← [s.course_sequence_before_target FOR s IN success_cases]
17.     most_common_path ← MostFrequent(paths)

18.     strategies ← FLATTEN([s.strategies_used FOR s IN success_cases])
19.     common_strategies ← TopFrequent(strategies, k=3)

20.     avg_time ← MEAN([s.total_study_hours FOR s IN success_cases])

21.     // 对比分析
22.     critical_factors ← CompareSuccessFailure(success_cases, failure_cases)

23.     recommendation ← {
24.         success_rate: LENGTH(success_cases) / LENGTH(relevant_cases),
25.         recommended_path: most_common_path,
26.         key_strategies: common_strategies,
27.         expected_time: avg_time,
28.         typical_case: success_cases[0],  // 最相似的成功案例
29.         critical_factors: critical_factors
30.     }
31. ELSE
32.     recommendation ← {success_rate: 0, message: "insufficient_data"}
33. END IF

34. RETURN recommendation
```

#### 算法3：闭环知识追踪

```python
Algorithm: Closed-Loop Knowledge Tracking

Input:
    student_id: 学生ID
    learning_event: {type, data, timestamp}

Output:
    updated_state: 新的知识状态
    replan_triggered: 是否触发重规划

Procedure:
1. // 获取当前状态
2. K_old, M_old ← Database.GetKnowledgeState(student_id)

3. // 更新知识状态
4. student_data ← Database.GetStudentData(student_id)
5. K_new, M_new ← KT_Encoder.Encode(student_data)

6. // 计算变化
7. delta_K ← K_new - K_old
8. max_change ← MAX(ABS(delta_K))
9. avg_change ← MEAN(ABS(delta_K))

10. // 判断是否显著变化
11. threshold ← 0.1
12. significant_change ← (max_change > threshold) OR
                         (avg_change > threshold * 0.5)

13. IF significant_change THEN
14.     // 分析变化方向
15.     improved ← [knowledge[i] FOR i WHERE delta_K[i] > 0.1]
16.     declined ← [knowledge[i] FOR i WHERE delta_K[i] < -0.1]

17.     // 触发重规划
18.     IF LENGTH(improved) > 0 THEN
19.         new_query ← GenerateQuery(improved, "next_steps")
20.         new_recommendations ← Agent.Invoke(new_query, K_new, M_new)
21.         NotifyStudent(student_id, "progress_update", new_recommendations)
22.     END IF

23.     IF LENGTH(declined) > 0 THEN
24.         NotifyStudent(student_id, "review_needed", declined)
25.     END IF

26.     replan_triggered ← TRUE
27. ELSE
28.     replan_triggered ← FALSE
29. END IF

30. // 保存新状态
31. Database.UpdateKnowledgeState(student_id, K_new, M_new, timestamp=NOW())

32. RETURN K_new, M_new, replan_triggered
```

---

## 7. 实施路线图

### 7.1 总体时间规划（3个月）

```
月份            核心任务                    里程碑                    人员分配
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
第1月  基础设施 + 核心算法          MVP可运行                后端2人 + 前端2人
(Week 1-4)

第2月  创新功能 + 数据收集          创新点实现                全员
(Week 5-8)

第3月  实验验证 + 论文撰写          系统完成 + 论文初稿       全员
(Week 9-12)
```

### 7.2 详细任务分解

#### 第1个月：基础设施与核心算法

**Week 1: 环境搭建与数据准备**

| 任务 | 负责人 | 输出 | 验收标准 |
|------|--------|------|---------|
| 搭建后端框架（FastAPI） | 后端1 | API服务可启动 | curl测试通过 |
| 部署Neo4j + Milvus + PostgreSQL | 后端2 | 数据库可连接 | 测试数据写入成功 |
| 构建课程知识图谱（100门课程） | 全员 | Neo4j中有100个节点 | Cypher查询返回正确 |
| 收集初始学生数据（50人） | 前端1 | PostgreSQL中有50条记录 | 数据格式校验通过 |

**Week 2: 知识追踪模块**

| 任务 | 负责人 | 输出 |
|------|--------|------|
| 实现IRT模型 | 后端1 | `KnowledgeStateEncoder`类 |
| 课程→知识点映射 | 后端2 | `course_knowledge_map.json` |
| 从成绩推断知识状态 | 后端1 | `_infer_from_grades()`函数 |
| 单元测试 | 后端2 | 测试覆盖率>80% |

**Week 3: Agentic Search框架**

| 任务 | 负责人 | 输出 |
|------|--------|------|
| 集成LangChain | 后端1 | Agent可初始化 |
| 实现Tool 1: SearchKG | 后端2 | Neo4j查询工具 |
| 实现Tool 2: RAGSearch | 后端1 | Milvus检索工具 |
| ReAct主循环 | 后端1 | Agent可执行简单查询 |

**Week 4: 前后端联调**

| 任务 | 负责人 | 输出 |
|------|--------|------|
| API接口设计 | 后端1 | OpenAPI文档 |
| 前端状态管理（Pinia） | 前端1 | Store架构 |
| 聊天界面优化 | 前端2 | 支持流式输出 |
| 3D图谱集成新数据源 | 前端1 | 从API获取数据 |
| 集成测试 | 全员 | E2E测试通过 |

**第1月里程碑**：
- ✅ 能够通过聊天界面问"机器学习需要什么基础？"
- ✅ Agent调用SearchKG工具查询Neo4j
- ✅ 返回先修课程列表
- ✅ 前端展示结果

---

#### 第2个月：创新功能实现

**Week 5: 自适应搜索规划**

| 任务 | 负责人 | 输出 |
|------|--------|------|
| 实现`AdaptiveSearchPlanner` | 后端1 | 根据知识状态调整策略 |
| 知识缺口计算 | 后端2 | `calculate_gap()`函数 |
| 集成到Agent | 后端1 | Agent执行前先规划 |
| A/B测试设计 | 全员 | 对比固定策略vs自适应 |

**Week 6: 元认知检索**

| 任务 | 负责人 | 输出 |
|------|--------|------|
| 构建学习策略库（20个策略） | 全员 | `learning_strategies.json` |
| 实现Tool 3: MetaCognitiveSearch | 后端2 | 元认知检索工具 |
| 策略向量化存入Milvus | 后端2 | Milvus collection创建 |
| 前端展示策略建议 | 前端2 | 策略卡片组件 |

**Week 7: 同侪案例推理**

| 任务 | 负责人 | 输出 |
|------|--------|------|
| 构建案例库（50个真实/模拟案例） | 全员 | `student_cases`表 |
| 学生相似度计算 | 后端1 | `calculate_student_similarity()` |
| 实现Tool 4: PeerCaseSearch | 后端1 | 案例检索工具 |
| 成功模式提取算法 | 后端2 | `extract_success_patterns()` |
| 前端案例展示组件 | 前端1 | 案例卡片 + 对比图表 |

**Week 8: 闭环知识追踪**

| 任务 | 负责人 | 输出 |
|------|--------|------|
| 学习事件监听系统 | 后端2 | `handle_learning_event()` |
| 知识状态变化检测 | 后端1 | `detect_significant_change()` |
| 重规划触发机制 | 后端1 | `_trigger_replan()` |
| WebSocket推送通知 | 后端2 + 前端2 | 实时通知功能 |

**第2月里程碑**：
- ✅ 基础薄弱的学生提问时，Agent自动深度搜索3层
- ✅ 返回学习策略建议（元认知检索）
- ✅ 返回相似学生案例（同侪推理）
- ✅ 学生做题后，系统自动更新知识状态并推送新建议

---

#### 第3个月：验证与产出

**Week 9: 用户研究**

| 任务 | 负责人 | 输出 |
|------|--------|------|
| 招募20-30个学生 | 全员 | 用户列表 |
| 设计问卷和访谈提纲 | 前端1 | 问卷星链接 |
| 收集使用数据 | 后端2 | 行为日志分析 |
| 用户满意度调研 | 全员 | 调研报告 |

**Week 10: 实验与对比**

| 任务 | 负责人 | 输出 |
|------|--------|------|
| 实现Baseline方法（5个） | 后端1 | 对比系统 |
| 运行实验 | 后端2 | 实验数据 |
| 数据分析（准确率、效果） | 后端1 | 实验结果表格 |
| 绘制对比图表 | 前端2 | 可视化图表 |

**Week 11: 论文撰写**

| 任务 | 负责人 | 输出 |
|------|--------|------|
| 论文结构设计 |  | Outline |
| 相关工作调研 | 全员 | Related Work部分 |
| 方法论撰写 | 后端团队 | Method部分 |
| 实验部分撰写 | 全员 | Experiment部分 |
| 绘制架构图 | 前端1 | 论文插图 |

**Week 12: 优化与总结**

| 任务 | 负责人 | 输出 |
|------|--------|------|
| 性能优化（响应时间<5s） | 后端团队 | 优化报告 |
| UI/UX优化 | 前端团队 | 交互优化 |
| 撰写项目总结报告 |  | 结题报告 |
| 准备答辩PPT | 全员 | 答辩材料 |
| 录制Demo视频 | 前端2 | 视频文件 |

**第3月里程碑**：
- ✅ 完整系统上线
- ✅ 用户研究完成
- ✅ 论文初稿完成
- ✅ 答辩材料准备完毕

---

### 7.3 风险缓解计划

| 风险 | 概率 | 影响 | 缓解策略 |
|------|------|------|---------|
| LLM API成本超预算 | 中 | 高 | 使用本地Qwen-7B做规划，只用云API做生成；推理路径缓存 |
| 真实数据收集困难 | 高 | 中 | 先用模拟数据验证算法，后期逐步替换真实数据 |
| Agent推理质量不稳定 | 中 | 高 | 限制max_iterations；设计Prompt模板；做充分测试 |
| Neo4j性能瓶颈 | 低 | 中 | 建立索引；使用缓存；限制图谱规模在1000节点内 |
| 前后端联调困难 | 中 | 中 | 第1月就开始集成；定义清晰的API契约；Mock数据 |
| 知识追踪精度不够 | 中 | 中 | 先用简单IRT，后续可升级DKT；人工校验结果 |

---

## 8. 技术风险与应对

### 8.1 关键技术挑战

#### 挑战1：Agent推理质量控制

**问题**：LLM的推理可能不稳定，生成错误的Action或死循环

**解决方案**：
1. **限制推理步数**：`max_iterations=6`
2. **Action白名单**：只允许调用预定义的工具
3. **输出格式校验**：用正则表达式验证Action格式
4. **Fallback机制**：
```python
try:
    response = agent.invoke(query)
except Exception as e:
    # 降级：使用简单的规则引擎
    response = rule_based_recommendation(query)
```

#### 挑战2：数据质量与冷启动

**问题**：
- 新用户没有历史数据，无法追踪知识状态
- 成绩数据可能不全

**解决方案**：
1. **新用户流程**：
   - 注册时填写问卷（已修课程、自评知识掌握度）
   - 完成10分钟的知识点测试
   - 用测试结果初始化知识状态

2. **数据增强**：
   - 用协同过滤借鉴相似学生数据
   - 用先修关系推断（学过B课，默认掌握A知识）

#### 挑战3：元认知检索的效果

**问题**：学习策略是否真的有效？如何验证？

**解决方案**：
1. **策略标注质量**：
   - 查阅教育学文献（费曼学习法、间隔重复等有实证支持）
   - 咨询教育专家

2. **效果验证**：
   - A/B测试：对比"有策略建议"vs"无策略建议"的学习效果
   - 长期追踪：记录使用策略的学生的成绩变化

### 8.2 工程实施风险

#### 风险1：LLM成本超预算

**估算**：
```
假设1000个用户，每人每月10次查询：
- 本地Qwen-7B：免费
- DeepSeek API：10,000次 × ¥0.002 = ¥20

总成本：¥20/月（可接受）
```

**控制策略**：
1. 推理路径缓存（相似问题复用）
2. 限制每次调用的token数
3. 设置用户每日查询上限

#### 风险2：系统响应时间过长

**目标**：< 5秒返回结果

**优化策略**：
1. **并行工具调用**：多个独立工具同时执行
2. **缓存热点查询**：常见问题直接返回缓存
3. **流式输出**：先返回部分结果，再逐步补充
4. **数据库索引**：Neo4j和PostgreSQL建立索引

**性能测试计划**：
```python
# 压力测试
for i in range(100):
    start = time.time()
    response = agent.invoke(random_query())
    latency = time.time() - start
    assert latency < 5, f"Query {i} too slow: {latency}s"
```

---

## 9. 预期成果与验证

### 9.1 系统功能验收标准

| 功能模块 | 验收标准 | 测试方法 |
|---------|---------|---------|
| 知识追踪 | 预测准确率AUC > 0.75 | 用历史数据交叉验证 |
| Agentic Search | 成功率 > 90%（不出错） | 100个测试问题 |
| 自适应规划 | 基础薄弱学生触发深度搜索100% | 日志分析 |
| 元认知检索 | 召回策略 > 0 | 每次查询都返回策略 |
| 同侪案例 | 找到相似案例的成功率 > 80% | 50个测试用户 |
| 闭环反馈 | 检测变化并重规划的准确率 > 85% | 模拟学习过程 |
| 响应时间 | 平均 < 5秒 | 压力测试 |

### 9.2 实验设计

#### 实验1：推荐准确性

**目标**：验证KTAS比传统方法更准确

**方法**：
- 招募50个学生
- 系统推荐5门课程
- 3个月后统计学生实际选课
- 计算命中率

**对比Baseline**：
1. 协同过滤（选了A的人还选了B）
2. 基于知识图谱的推荐（只看先修关系）
3. LPReKL（KT+LLM，无Agent）
4. 传统RAG（单次检索）
5. KTAS（我们的）

**评估指标**：
- 准确率@5：推荐的5门课中，学生实际选了几门
- NDCG：考虑顺序的推荐质量

#### 实验2：学习效果

**目标**：验证推荐路径的学习效果更好

**方法**：
- A组：使用KTAS推荐的路径学习（25人）
- B组：自行选课（对照组，25人）
- 追踪3个月后的成绩

**评估指标**：
- 平均GPA
- 课程通过率
- 学习时长

**预期结果**：A组平均GPA提升10%，通过率提升15%

#### 实验3：用户满意度

**目标**：验证系统的用户体验

**方法**：
- 问卷调查（System Usability Scale, SUS）
- 半结构化访谈

**问题示例**：
1. 推荐的课程路径是否合理？（1-5分）
2. 学习策略建议是否有用？（1-5分）
3. 相比传统选课方式，你更喜欢这个系统吗？

**预期结果**：SUS分数 > 70（良好）

### 9.3 论文产出计划

#### 主论文：Knowledge-Aware Agentic Search for Personalized Learning

**投稿目标**：
- **首选**：EDM 2025 (Educational Data Mining)
- **备选**：LAK 2026 (Learning Analytics & Knowledge)
- **备选**：AAAI 2026 (AI in Education Track)

**论文结构**：
```
1. Introduction
   - 问题：现有推荐系统的三大问题
   - 贡献：四个创新点

2. Related Work
   - LLM4Edu综述
   - Knowledge Tracing
   - Agentic Search (Search-o1, etc.)
   - 与现有工作的对比（表格）

3. Methodology
   - KTAS整体架构
   - 知识状态编码器（IRT实现细节）
   - 自适应搜索规划（算法伪代码）
   - 元认知检索（策略库构建）
   - 同侪案例推理（相似度计算）
   - 闭环知识追踪（更新机制）

4. Experiments
   - 数据集（华东师范大学数据）
   - Baseline方法（5个）
   - 实验1：推荐准确性
   - 实验2：学习效果
   - 实验3：用户满意度
   - 消融实验（去掉某个创新点后的效果）

5. Discussion
   - 四个创新点各自的贡献
   - 局限性（数据规模、LLM成本）
   - 未来工作（扩展到其他专业、加入强化学习）

6. Conclusion
```

**预期创新点强度**：
- 知识感知搜索规划：⭐⭐⭐⭐ (现有工作未做)
- 元认知检索：⭐⭐⭐⭐⭐ (完全创新)
- 同侪案例推理：⭐⭐⭐⭐⭐ (完全创新)
- 闭环知识追踪：⭐⭐⭐⭐ (现有工作未深度结合)

#### 辅助论文：Meta-Cognitive Retrieval (短文/Workshop)

**投稿目标**：L@S 2025 Work-in-Progress Track

**重点**：深入探讨元认知检索这一个创新点

---

### 9.4 其他成果

| 成果类型 | 具体内容 | 时间节点 |
|---------|---------|---------|
| **软件著作权** | SmartPath智能导学系统V1.0 | 第3个月 |
| **开源代码** | GitHub仓库（部分开源） | 论文接收后 |
| **技术博客** | 3-5篇技术文章（CSDN/知乎） | 开发过程中 |
| **数据集** | 匿名化的学习路径数据集 | 论文接收后 |
| **Demo视频** | 5分钟系统演示 | 第3个月 |

---

## 10. 参考文献

### 核心参考文献（必读）

#### Agentic Search相关
1. **Search-o1**: "Search-o1: Agentic Search-Enhanced Large Reasoning Models" (arXiv 2025)
   - 提出Agentic RAG工作流，在不确定时自动检索

2. **SearchAgent-X**: "Demystifying and Enhancing the Efficiency of Large Language Model Based Search Agents" (arXiv 2025)
   - 优化search agents的效率（调度、检索策略）

#### LLM4Edu相关
3. **LLM Agents for Education**: "LLM Agents for Education: Advances and Applications" (EMNLP 2025 Findings)
   - 教育场景下的LLM agents综述

4. **MultiTutor**: "MultiTutor: Collaborative LLM Agents for Multimodal Student Support" (PMLR 2025)
   - 多Agent教育系统，有明确的search agents

5. **PlanGlow**: "PlanGlow: Personalized Study Planning with an Explainable and Controllable LLM-Driven System" (L@S 2025)
   - 学习计划生成，强调可解释性

6. **LPReKL**: "Learning Path Recommendation Enhanced by Knowledge Tracing and LLM" (Electronics 2024)
   - KT+LLM的结合，但无Agent

#### Knowledge Tracing相关
7. **Deep Knowledge Tracing**: "Deep Knowledge Tracing" (NIPS 2015)
   - DKT的开山之作

8. **PyKT**: "pyKT: A Python Library to Benchmark Deep Learning based Knowledge Tracing Models" (NeurIPS 2021 Datasets Track)
   - 开源KT库，包含IRT实现

#### 推荐系统相关
9. **LightGCN**: "LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation" (SIGIR 2020)
   - 图神经网络推荐算法

### 补充文献

10. "An LLM Approach to Course Recommendations Using Embedding-Based Similarity Search" (arXiv 2024)
11. "LearnMate: Enhancing Online Education with LLM-Powered Personalized Learning Plans" (arXiv 2025)
12. "How Can LLMs Simulate the Real Teacher? Retrieval-Enhanced Learning Path Generation" (EMNLP 2025)

---

## 附录A：技术选型对比表

### A.1 Agent框架对比

| 框架 | 优点 | 缺点 | 选择 |
|------|------|------|------|
| **LangChain** | 生态成熟，工具丰富，文档完善 | 抽象层较重，性能一般 | ✅ 主选 |
| **LangGraph** | 复杂工作流支持，可视化 | 学习曲线陡 | ⚠️ 可选 |
| **AutoGPT** | 自主性强 | 控制性差，成本高 | ❌ 不选 |
| **ReAct手动实现** | 完全可控 | 开发工作量大 | ❌ 不选 |

### A.2 知识追踪模型对比

| 模型 | 数据需求 | 精度 | 实现难度 | 选择 |
|------|---------|------|---------|------|
| **IRT** | 低（只需成绩） | 中 | 低（PyKT现成） | ✅ 第1版 |
| **BKT** | 中（需做题序列） | 中 | 中 | ⚠️ 可选 |
| **DKT** | 高（大量交互数据） | 高 | 高 | ⚠️ 第2版 |
| **AKT** | 高 | 很高 | 很高 | ❌ 不考虑 |

### A.3 LLM选型对比

| 模型 | 部署方式 | 成本 | 质量 | 用途 |
|------|---------|------|------|------|
| **Qwen-7B-Chat** | 本地vLLM | 免费 | 中 | Agent规划 |
| **GPT-4** | API | ¥0.03/1K tokens | 很高 | 最终生成 |
| **DeepSeek-Chat** | API | ¥0.002/1K tokens | 高 | 最终生成（性价比） |
| **GLM-4** | API | ¥0.01/1K tokens | 高 | 备选 |

---

## 附录B：数据库Schema设计

### B.1 PostgreSQL表结构

```sql
-- 用户表
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(50),
    major VARCHAR(50),
    enrollment_year INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 成绩表
CREATE TABLE grades (
    grade_id SERIAL PRIMARY KEY,
    student_id VARCHAR(20) REFERENCES users(student_id),
    course_name VARCHAR(100),
    grade DECIMAL(5,2),
    semester VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 知识状态表
CREATE TABLE knowledge_states (
    state_id SERIAL PRIMARY KEY,
    student_id VARCHAR(20) REFERENCES users(student_id),
    knowledge_vector FLOAT[],  -- PostgreSQL数组
    meta_cognitive_state JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 学习日志表
CREATE TABLE learning_logs (
    log_id SERIAL PRIMARY KEY,
    student_id VARCHAR(20) REFERENCES users(student_id),
    event_type VARCHAR(50),  -- 'exercise_completed', 'resource_viewed', etc.
    event_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 做题记录表
CREATE TABLE exercise_logs (
    exercise_id SERIAL PRIMARY KEY,
    student_id VARCHAR(20) REFERENCES users(student_id),
    knowledge_point VARCHAR(100),
    is_correct BOOLEAN,
    time_spent INT,  -- 秒
    difficulty VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 推荐历史表
CREATE TABLE recommendation_history (
    rec_id SERIAL PRIMARY KEY,
    student_id VARCHAR(20) REFERENCES users(student_id),
    query TEXT,
    recommended_courses JSONB,
    reasoning_path JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### B.2 Neo4j图谱Schema

```cypher
// 课程节点
CREATE (c:Course {
    id: "CS101",
    name: "计算机导论",
    credits: 3,
    difficulty: 0.6,
    description: "..."
})

// 知识点节点
CREATE (k:Knowledge {
    id: "matrix_multiplication",
    name: "矩阵乘法",
    domain: "线性代数"
})

// 学生节点
CREATE (s:Student {
    student_id: "10225102471",
    major: "计算机科学"
})

// 关系：先修关系
CREATE (c1:Course)-[:PREREQUISITE {importance: 0.8}]->(c2:Course)

// 关系：包含知识点
CREATE (c:Course)-[:CONTAINS {weight: 0.4}]->(k:Knowledge)

// 关系：学生已修课程
CREATE (s:Student)-[:LEARNED {grade: 85, semester: "2024-1"}]->(c:Course)

// 关系：知识点依赖
CREATE (k1:Knowledge)-[:DEPENDS_ON {strength: 0.7}]->(k2:Knowledge)
```

### B.3 Milvus集合Schema

```python
# 课程资料集合
course_materials_schema = {
    "collection_name": "course_materials",
    "fields": [
        {"name": "id", "type": DataType.INT64, "is_primary": True, "auto_id": True},
        {"name": "course_name", "type": DataType.VARCHAR, "max_length": 100},
        {"name": "material_type", "type": DataType.VARCHAR, "max_length": 50},  # "textbook", "video", "exercise"
        {"name": "content", "type": DataType.VARCHAR, "max_length": 5000},
        {"name": "embedding", "type": DataType.FLOAT_VECTOR, "dim": 1024}
    ]
}

# 学习策略集合
learning_strategies_schema = {
    "collection_name": "learning_strategies",
    "fields": [
        {"name": "id", "type": DataType.INT64, "is_primary": True, "auto_id": True},
        {"name": "strategy_name", "type": DataType.VARCHAR, "max_length": 100},
        {"name": "description", "type": DataType.VARCHAR, "max_length": 1000},
        {"name": "applicable_knowledge", "type": DataType.VARCHAR, "max_length": 200},
        {"name": "effectiveness", "type": DataType.FLOAT},
        {"name": "embedding", "type": DataType.FLOAT_VECTOR, "dim": 1024}
    ]
}

# 学生案例集合
student_cases_schema = {
    "collection_name": "student_cases",
    "fields": [
        {"name": "id", "type": DataType.INT64, "is_primary": True, "auto_id": True},
        {"name": "background_summary", "type": DataType.VARCHAR, "max_length": 500},
        {"name": "learning_path", "type": DataType.VARCHAR, "max_length": 1000},
        {"name": "outcome", "type": DataType.VARCHAR, "max_length": 20},  # "success" or "failure"
        {"name": "tips", "type": DataType.VARCHAR, "max_length": 1000},
        {"name": "embedding", "type": DataType.FLOAT_VECTOR, "dim": 1024}
    ]
}
```

---

## 附录C：API接口文档

### C.1 核心接口列表

```yaml
# 1. 获取学生知识状态
GET /api/v1/students/{student_id}/knowledge-state
Response:
  {
    "knowledge_vector": [0.45, 0.60, 0.80, ...],
    "meta_cognitive_state": {
      "struggle_patterns": ["abstract_proof"],
      "learning_style": "visual"
    },
    "updated_at": "2025-01-17T10:30:00Z"
  }

# 2. Agent查询接口
POST /api/v1/agent/query
Request:
  {
    "student_id": "10225102471",
    "query": "我想学机器学习，应该怎么规划？",
    "stream": true  # 流式输出
  }
Response (Stream):
  data: {"type": "thought", "content": "需要了解机器学习的前置要求"}
  data: {"type": "action", "tool": "SearchKnowledgeGraph", "input": "机器学习"}
  data: {"type": "observation", "content": "..."}
  ...
  data: {"type": "final_answer", "content": "根据分析..."}

# 3. 学习事件上报
POST /api/v1/learning-events
Request:
  {
    "student_id": "10225102471",
    "event_type": "exercise_completed",
    "event_data": {
      "knowledge": "矩阵乘法",
      "correct": true,
      "time_spent": 30
    }
  }
Response:
  {
    "status": "success",
    "knowledge_updated": true,
    "replan_triggered": true,
    "new_recommendations": [...]
  }

# 4. 获取课程详情
GET /api/v1/courses/{course_name}
Response:
  {
    "name": "机器学习",
    "prerequisites": [...],
    "difficulty": 0.75,
    "description": "...",
    "knowledge_points": [...]
  }

# 5. 同侪案例查询
GET /api/v1/peer-cases?student_id={student_id}&target_course={course_name}
Response:
  {
    "success_rate": 0.72,
    "sample_size": 50,
    "recommended_path": [...],
    "typical_case": {...}
  }
```

---

## 结语

本技术方案基于对原有项目的深度分析和学术界最新进展的调研，提出了**KTAS (Knowledge Tracking-Enhanced Agentic Search)** 架构，通过**四个核心创新点**：

1. **知识感知的搜索规划** - 根据学生知识状态动态调整搜索策略
2. **元认知检索** - 不只搜索"学什么"，还搜索"怎么学"
3. **同侪案例推理** - 从成功学生的学习路径中学习
4. **闭环知识追踪** - 搜索结果反馈到知识状态，持续优化

实现了真正**有技术深度、有实用价值、有创新性**的智能导学系统。

相比原有项目，本方案：
- ✅ 解决了"只有可视化，无推荐算法"的问题
- ✅ 修复了"数据硬编码、无后端"的架构缺陷
- ✅ 实现了中期汇报声称但未实现的功能（知识追踪、个性化推荐）
- ✅ 在现有学术工作基础上，提出了**4个首创性的技术创新**

预期产出：
- 📄 1-2篇会议论文（EDM/LAK/AAAI）
- 💻 完整可用的智能导学系统
- 🏆 创新创业项目优秀结题
- 🎓 对学生真正有价值的学习工具

**实施建议**：
按照3个月路线图，第1个月实现基础框架，第2个月实现创新功能，第3个月验证和产出。

如有任何技术问题或需要进一步细化某个模块，欢迎随时讨论！
