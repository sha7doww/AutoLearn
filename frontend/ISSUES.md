# 项目问题与改进建议

本文档记录 ZhiShiTuPu（知识图谱）项目中发现的问题和潜在的改进方向。

---

## 🔴 严重问题

### 1. ChatAssistant 缺少对话历史上下文

**位置**: `src/views/ChatAssistant.vue:406-409`

**问题描述**:
当前实现中，每次调用 DeepSeek API 时只发送当前用户输入，不包含之前的对话历史。这导致 AI 无法进行连续的多轮对话，无法记住上下文。

**当前代码**:
```javascript
messages: [
  { role: 'system', content: localStorage.getItem('systemPrompt') },
  { role: 'user', content: message }  // 只有当前输入
]
```

**影响**:
- AI 无法记住之前说过的内容
- 无法进行需要上下文的连续对话
- 用户体验较差（看起来有历史，但 AI 实际上"失忆"）

**建议修改**:
```javascript
messages: [
  { role: 'system', content: localStorage.getItem('systemPrompt') },
  ...this.chatMessages.map(msg => ({
    role: msg.role,
    content: msg.content.replace(/<br>/g, '\n') // 还原换行符
  })),
  { role: 'user', content: message }
]
```

**注意事项**:
- 需要考虑 token 限制（DeepSeek 的上下文窗口大小）
- 可能需要实现对话历史截断策略（只保留最近 N 轮对话）
- 需要在格式化时保留原始内容，避免信息丢失

---

## ⚠️ 安全问题

### 2. API Key 硬编码在前端代码中

**位置**: `src/views/ChatAssistant.vue:413`

**问题描述**:
DeepSeek API Key (`[REDACTED - 已移除]`) 直接写在前端代码中，任何人都可以通过查看源代码获取。

**风险**:
- API Key 可能被滥用
- 产生意外的 API 费用
- 无法撤销已泄露的 Key（代码已提交到 Git）

**建议解决方案**:

**方案 1: 使用后端代理**（推荐）
```
前端 → 后端 API → DeepSeek API
```
- 在后端服务器中存储 API Key
- 前端只调用自己的后端接口
- 后端负责转发请求到 DeepSeek

**方案 2: 使用环境变量**（仅开发环境）
```javascript
// .env.local (不提交到 Git)
VUE_APP_DEEPSEEK_API_KEY=sk-xxx

// 代码中使用
'Authorization': `Bearer ${process.env.VUE_APP_DEEPSEEK_API_KEY}`
```

**立即行动**:
1. 在 DeepSeek 控制台撤销当前 API Key
2. 生成新的 API Key
3. 实施上述解决方案之一

---

## 🟡 架构问题

### 3. 课程数据重复定义

**位置**:
- `src/views/HomeView.vue:36-148`
- `src/components/myDagre.vue:26-94`
- `src/views/ChatAssistant.vue:135-325`

**问题描述**:
相同的课程数据（67门课程及其关系）在三个不同的组件中重复定义，导致：
- 代码冗余
- 维护困难（修改一处需要同步修改三处）
- 数据不一致风险

**建议解决方案**:

**方案 1: 创建共享数据模块**
```javascript
// src/data/courseData.js
export const courseNodes = [
  { id: 1, label: '数学分析' },
  // ...
];

export const courseEdges = [
  { from: 34, to: 16 },
  // ...
];
```

然后在各组件中导入：
```javascript
import { courseNodes, courseEdges } from '@/data/courseData.js';
```

**方案 2: 使用 Vuex/Pinia 状态管理**
```javascript
// store/courses.js
export const useCourseStore = defineStore('courses', {
  state: () => ({
    nodes: [...],
    edges: [...]
  })
});
```

**方案 3: 从后端 API 获取**（最佳实践）
```javascript
// 在 main.js 或 App.vue 中
async mounted() {
  const response = await axios.get('/api/courses');
  this.courseData = response.data;
}
```

---

## 🟡 功能问题

### 4. CourseOutline 页面内容硬编码

**位置**: `src/views/CourseOutline.vue:13-35`

**问题描述**:
课程详情页面只显示"概率论与数理统计"的固定内容，无法根据用户点击的课程动态显示。

**当前行为**:
- 用户在 3D/2D 图谱中点击任何课程
- 都跳转到 `/course` 路由
- 都显示相同的"概率论与数理统计"内容

**建议修改**:

1. **修改路由传参** (`src/views/HomeView.vue:230`):
```javascript
// 当前
router.push({ name: 'course' });

// 修改为
router.push({
  name: 'course',
  params: { courseId: sphere.userData.id }
});
```

2. **修改路由定义** (`src/router/index.js:23-26`):
```javascript
{
  path: '/course/:courseId',  // 添加动态参数
  name: 'course',
  component: CourseOutline
}
```

3. **CourseOutline 组件动态加载数据**:
```javascript
export default {
  data() {
    return {
      courseData: null
    }
  },
  async mounted() {
    const courseId = this.$route.params.courseId;
    // 从 API 或本地数据获取课程信息
    this.courseData = await this.fetchCourseData(courseId);
  }
}
```

---

## 🟢 优化建议

### 5. DeepSeek API 调用缺少参数配置

**位置**: `src/views/ChatAssistant.vue:404-415`

**问题描述**:
API 调用时没有设置任何可选参数，完全依赖默认值。

**当前缺少的参数**:
- `temperature`: 控制回答的随机性（0-2，默认约1.0）
- `max_tokens`: 限制回答长度
- `top_p`: 核采样参数
- `stream`: 是否使用流式输出

**建议添加**:
```javascript
{
  model: 'deepseek-chat',
  messages: [...],
  temperature: 0.7,        // 较低的温度使回答更确定
  max_tokens: 2000,        // 限制最大输出长度
  top_p: 0.9,              // 核采样
  stream: false            // 或实现流式输出以提升体验
}
```

**流式输出的好处**:
- 用户可以实时看到 AI 的回答过程
- 减少等待时的焦虑感
- 更好的用户体验

---

### 6. 响应格式化过于激进

**位置**: `src/views/ChatAssistant.vue:429-438`

**问题描述**:
`formatResponse` 方法移除了所有 Markdown 格式，包括加粗、标题等，导致回答失去结构化信息。

**当前行为**:
```javascript
text = text.replace(/\*\*(.*?)\*\*/g, '$1'); // 去掉所有加粗
text = text.replace(/#/g, '');                // 去掉所有标题标记
```

**建议改进**:
保留部分格式，转换为 HTML：
```javascript
formatResponse(text) {
  // 保留加粗
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // 转换标题
  text = text.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
  text = text.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
  text = text.replace(/^# (.*?)$/gm, '<h1>$1</h1>');

  // 转换列表
  text = text.replace(/^- (.*?)$/gm, '<li>$1</li>');

  // 转换换行
  text = text.replace(/\n\n/g, '</p><p>');
  text = text.replace(/\n/g, '<br>');

  return `<p>${text}</p>`;
}
```

或者使用现成的 Markdown 解析库：
```bash
npm install marked
```

```javascript
import { marked } from 'marked';

formatResponse(text) {
  return marked(text);
}
```

---

### 7. 缺少错误处理和加载状态

**位置**: `src/views/ChatAssistant.vue:395-428`

**问题描述**:
- 没有显示加载动画（虽然有 `isWaitingForResponse` 状态）
- 错误提示过于简单
- 没有重试机制

**建议改进**:

1. **添加加载动画**:
```vue
<template>
  <div v-if="isWaitingForResponse" class="loading-indicator">
    <div class="spinner"></div>
    <span>AI 正在思考中...</span>
  </div>
</template>
```

2. **详细的错误处理**:
```javascript
catch (error) {
  console.error('API请求失败:', error);

  let errorMessage = '抱歉，暂时无法处理您的请求。';

  if (error.response) {
    // 服务器返回错误
    if (error.response.status === 401) {
      errorMessage = 'API 密钥无效，请联系管理员。';
    } else if (error.response.status === 429) {
      errorMessage = '请求过于频繁，请稍后再试。';
    } else if (error.response.status === 500) {
      errorMessage = '服务器错误，请稍后再试。';
    }
  } else if (error.request) {
    // 网络错误
    errorMessage = '网络连接失败，请检查您的网络。';
  }

  this.addMessage('assistant', errorMessage);
}
```

3. **添加重试按钮**:
```vue
<button @click="retryLastMessage" v-if="lastMessageFailed">
  重试
</button>
```

---

### 8. localStorage 使用可能导致数据丢失

**位置**: `src/views/ChatAssistant.vue:340, 462`

**问题描述**:
- `localStorage` 有大小限制（通常 5-10MB）
- 用户清除浏览器数据会丢失所有历史
- 没有数据备份机制

**建议改进**:

1. **添加导出/导入功能**:
```javascript
exportHistory() {
  const data = JSON.stringify(this.chatHistory);
  const blob = new Blob([data], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `chat-history-${Date.now()}.json`;
  a.click();
}

importHistory(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    const data = JSON.parse(e.target.result);
    this.chatHistory = data;
    localStorage.setItem('chatHistory', JSON.stringify(data));
  };
  reader.readAsText(file);
}
```

2. **使用 IndexedDB**（更大容量）:
```javascript
// 使用 localforage 库
import localforage from 'localforage';

await localforage.setItem('chatHistory', this.chatHistory);
this.chatHistory = await localforage.getItem('chatHistory') || [];
```

---

## 📋 优先级建议

| 优先级 | 问题编号 | 问题 | 影响 |
|--------|---------|------|------|
| 🔴 高 | #2 | API Key 泄露 | 安全风险 |
| 🔴 高 | #1 | 缺少对话历史 | 功能缺陷 |
| 🟡 中 | #3 | 数据重复定义 | 维护困难 |
| 🟡 中 | #4 | 课程详情硬编码 | 功能不完整 |
| 🟢 低 | #5 | API 参数缺失 | 体验优化 |
| 🟢 低 | #6 | 格式化过度 | 显示效果 |
| 🟢 低 | #7 | 错误处理不足 | 用户体验 |
| 🟢 低 | #8 | 数据存储风险 | 数据安全 |

---

---

## 🔴 严重问题（续）

### 9. SideBar 组件泄露另一个 API Key

**位置**: `src/components/SideBar.vue:66`

**问题描述**:
SideBar 组件中实现了另一个聊天功能，使用豆包（Doubao）API，同样将 API Key 硬编码在前端。

**泄露的信息**:
- API Endpoint: `https://ark.cn-beijing.volces.com/api/v3/chat/completions`
- 模型: `doubao-1.5-pro-32k-250115`
- API Key: `[REDACTED - 已移除]`

**代码**:
```javascript
headers: {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${process.env.VUE_APP_DOUBAO_API_KEY}`
}
```

**影响**:
- 与 ChatAssistant 同样的安全风险
- 两个不同服务的 API Key 都已泄露
- 可能产生双倍的滥用风险

**立即行动**:
1. 撤销豆包 API Key
2. 撤销 DeepSeek API Key（问题 #2）
3. 统一使用后端代理方案

---

### 10. 项目中存在两个独立的聊天助手实现

**位置**:
- `src/views/ChatAssistant.vue` - 完整的聊天页面
- `src/components/SideBar.vue:44-78` - 侧边栏简化版聊天

**问题描述**:
项目中有两个完全独立的聊天助手实现，使用不同的 API：
1. **ChatAssistant**: 使用 DeepSeek API，有知识图谱上下文，功能完整
2. **SideBar**: 使用豆包 API，只有简单的 system prompt，功能简化

**问题**:
- 代码重复，维护成本高
- 用户体验不一致（两个聊天界面，不同的 AI 模型）
- 没有会话同步（在两个地方的对话是独立的）
- 资源浪费（两个 API 都在调用）

**建议方案**:

**方案 1: 统一为单一聊天服务**
- 移除 SideBar 中的聊天功能
- SideBar 中的"发送"按钮改为跳转到 ChatAssistant 页面
- 只保留一个 AI 后端（建议 DeepSeek，因为已有知识图谱）

**方案 2: 明确功能分工**
- ChatAssistant: 深度学业规划（完整的知识图谱上下文）
- SideBar: 快速问答（简单问题，不需要知识图谱）
- 但仍需统一 API 和共享会话历史

---

### 11. LoginView 没有真实的认证逻辑

**位置**: `src/views/LoginView.vue:117-137`

**问题描述**:
登录功能只是一个假的 UI，没有真实的用户认证。

**当前逻辑**:
```javascript
login() {
  if (!this.rememberMe) {
    this.$message({ message: '请先同意【智能导学用户使用协议】', type: "warning" });
    return;
  }
  this.$refs.loginRules.validate(valid => {
    if (valid) {
      this.loading = true;
      setTimeout(() => {
        this.loading = false;
        this.$router.push({ name: 'Home' });  // 直接跳转，没有验证
      }, 1000);
    }
  });
}
```

**问题**:
- 任何用户名和密码都能通过（只要长度在 3-18 个字符）
- 没有调用后端 API 验证用户身份
- 没有存储登录状态（token、session 等）
- 没有权限控制

**安全风险**:
- 任何人都能访问系统
- 无法区分不同用户
- 无法实现个性化功能
- 无法保护用户数据

**建议实现**:
```javascript
async login() {
  if (!this.rememberMe) {
    this.$message({ message: '请先同意用户协议', type: "warning" });
    return;
  }

  this.$refs.loginRules.validate(async valid => {
    if (valid) {
      this.loading = true;
      try {
        const response = await axios.post('/api/login', {
          username: this.loginRuleForm.username,
          password: this.loginRuleForm.password
        });

        // 保存 token
        localStorage.setItem('authToken', response.data.token);
        localStorage.setItem('userId', response.data.userId);

        this.$router.push({ name: 'Home' });
      } catch (error) {
        this.$message.error('用户名或密码错误');
      } finally {
        this.loading = false;
      }
    }
  });
}
```

---

## 🟡 架构问题（续）

### 12. 课程数据第四次重复

**位置**:
- `src/views/HomeView.vue:36-148`
- `src/components/myDagre.vue:26-94`
- `src/views/ChatAssistant.vue:135-325`
- `src/components/LsSb.vue:32-102` ⚠️ **新发现**

**问题描述**:
LsSb.vue 中再次重复定义了相同的课程数据，这是第 4 次重复。而且 LsSb 的数据还包含了额外的三个分类节点（学科基础课、专业必修课、专业任意选修课）。

**数据不一致**:
- LsSb 有 67 + 3 = 70 个节点
- 其他组件只有 67 个节点
- 边的关系也完全不同

**影响**:
- 与问题 #3 相同，但更严重（4 处重复）
- 数据不一致导致用户在不同页面看到不同的课程关系

---

### 13. 课程节点包含无效的 URL

**位置**:
- `src/components/myDagre.vue:27-94`
- `src/components/LsSb.vue:33-102`

**问题描述**:
每个课程节点都有一个 `url` 字段，但都指向无效的示例网址：

```javascript
{ id: 1, label: '数学分析', url: 'https://example.com/page1' },
{ id: 2, label: '并行计算', url: 'https://example.com/page2' },
// ...
```

**问题**:
- `example.com` 是示例域名，不是真实的课程页面
- URL 字段存在但从未被使用（点击节点跳转到 `/course` 而不是 URL）
- 代码中有检查 `if (selectedNode.url)` 但实际使用的是路由跳转

**建议**:
1. 如果不需要外部链接，删除 `url` 字段
2. 如果需要，应该指向真实的课程页面
3. 统一跳转逻辑（要么用 URL，要么用路由，不要混用）

---

## 🟢 优化建议（续）

### 14. NavBar 组件的按钮缺少功能

**位置**: `src/components/NavBar.vue:10-26`

**问题描述**:
NavBar 右侧有 5 个图标按钮，但只有第一个"主题切换"按钮有实现，其他 4 个按钮都没有功能。

**当前状态**:
```vue
<!-- ✅ 有功能 -->
<button class="circle-btn" @click="toggleTheme">
  <img src="@/assets/pics/lightness.png" alt="Icon 4">
</button>

<!-- ❌ 没有功能 -->
<button class="circle-btn">
  <img src="@/assets/pics/search.png" alt="Icon 1">
</button>
<button class="circle-btn">
  <img src="@/assets/pics/translate.png" alt="Icon 2">
</button>
<button class="circle-btn">
  <img src="@/assets/pics/homepage.png" alt="Icon 3">
</button>
<button class="circle-btn">
  <img src="@/assets/pics/dog.jpg" alt="Icon 5">
</button>
```

**影响**:
- 用户点击按钮没有任何反应，体验差
- 占用界面空间但没有实际功能
- 图标名称暗示了功能（search、translate、homepage），但未实现

**建议**:
1. **移除未实现的按钮**（如果短期内不打算实现）
2. **实现对应功能**:
   - 搜索：全局课程搜索
   - 翻译：切换中英文界面
   - 主页：返回首页
   - 用户头像：用户中心/退出登录

---

### 15. 主题切换功能未实现

**位置**: `src/components/NavBar.vue:35-37`

**问题描述**:
NavBar 的主题切换按钮只是触发了一个事件 `this.$emit('toggle-theme')`，但没有组件监听这个事件。

**代码**:
```javascript
toggleTheme() {
  this.$emit('toggle-theme');
}
```

**问题**:
- 父组件（App.vue、HomeView.vue、CourseOutline.vue 等）都没有监听 `@toggle-theme` 事件
- NavBar 中定义了 `.dark-mode` 样式（第 116-119 行），但从未被应用
- 按钮可以点击，但没有任何效果

**建议实现**:
```javascript
// App.vue
<template>
  <div id="app" :class="{ 'dark-mode': isDarkMode }">
    <router-view @toggle-theme="toggleTheme"></router-view>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isDarkMode: false
    }
  },
  methods: {
    toggleTheme() {
      this.isDarkMode = !this.isDarkMode;
      localStorage.setItem('theme', this.isDarkMode ? 'dark' : 'light');
    }
  },
  mounted() {
    const savedTheme = localStorage.getItem('theme');
    this.isDarkMode = savedTheme === 'dark';
  }
}
</script>
```

---

### 16. LsSb 组件固定宽度，缺少响应式设计

**位置**: `src/components/LsSb.vue:293-294`

**问题描述**:
LsSb 组件使用固定宽度 1680px，在不同屏幕尺寸下会出现问题。

**代码**:
```css
.background {
  width: 1680px;  /* 固定宽度 */
  height: 100%;
}

#mynetwork {
  width: 1500px;  /* 固定宽度 */
  height: 1000px;
  border: 1px solid lightgray;
}
```

**问题**:
- 小屏幕（笔记本、平板）会出现横向滚动条
- 大屏幕（4K 显示器）会有大量空白
- 图表不能充分利用屏幕空间

**建议修改**:
```css
.background {
  width: 100vw;   /* 视口宽度 */
  height: 100vh;  /* 视口高度 */
  overflow: hidden;
}

#mynetwork {
  width: calc(100vw - 40px);  /* 减去 padding */
  height: calc(100vh - 150px); /* 减去 controls 高度 */
  border: 1px solid lightgray;
}
```

---

### 17. SideBar 聊天功能同样缺少对话历史

**位置**: `src/components/SideBar.vue:54-69`

**问题描述**:
与 ChatAssistant（问题 #1）相同，SideBar 的聊天功能也没有发送对话历史上下文。

**当前代码**:
```javascript
const response = await axios.post(
  'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
  {
    model: 'doubao-1.5-pro-32k-250115',
    messages: [
      { role: 'system', content: '你是一个专业的学业生涯规划指导师，回答与课程相关问题。' },
      { role: 'user', content: userMessage }  // 只有当前消息
    ]
  }
);
```

**影响**:
- 同问题 #1
- 豆包模型无法进行连续对话

---

### 18. particles.js 使用全局变量

**位置**: `src/views/LoginView.vue:30-31`

**问题描述**:
LoginView 使用了全局的 `particlesJS` 对象，通过 eslint-disable 注释来忽略警告。

**代码**:
```javascript
// eslint-disable-next-line
/* global particlesJS */
import "particles.js";
```

**问题**:
- 依赖全局变量，不符合模块化开发规范
- 可能与其他库冲突
- 类型检查困难

**建议替换**:
使用 Vue 生态的粒子库：
```bash
npm install vue-particles
```

```javascript
import Particles from "vue3-particles";

export default {
  components: {
    Particles
  }
}
```

---

## 📋 优先级建议（更新）

| 优先级 | 问题编号 | 问题 | 影响 |
|--------|---------|------|------|
| 🔴 高 | #2 | DeepSeek API Key 泄露 | 安全风险 |
| 🔴 高 | #9 | 豆包 API Key 泄露 | 安全风险 |
| 🔴 高 | #11 | 登录功能是假的 | 安全风险 |
| 🔴 高 | #1 | ChatAssistant 缺少对话历史 | 功能缺陷 |
| 🔴 高 | #10 | 两个独立聊天实现 | 架构混乱 |
| 🟡 中 | #3 | 课程数据重复定义（3次） | 维护困难 |
| 🟡 中 | #12 | 课程数据第4次重复 | 维护困难 |
| 🟡 中 | #4 | 课程详情硬编码 | 功能不完整 |
| 🟡 中 | #13 | 无效的课程 URL | 数据质量 |
| 🟢 低 | #14 | NavBar 按钮无功能 | 用户体验 |
| 🟢 低 | #15 | 主题切换未实现 | 功能缺失 |
| 🟢 低 | #16 | 固定宽度设计 | 响应式问题 |
| 🟢 低 | #17 | SideBar 缺少历史 | 功能缺陷 |
| 🟢 低 | #5 | API 参数缺失 | 体验优化 |
| 🟢 低 | #6 | 格式化过度 | 显示效果 |
| 🟢 低 | #7 | 错误处理不足 | 用户体验 |
| 🟢 低 | #8 | localStorage 风险 | 数据安全 |
| 🟢 低 | #18 | 全局变量使用 | 代码质量 |

---

---

## 🟡 用户体验问题（浏览器测试发现）

### 19. 3D图谱搜索功能缺少视觉反馈

**位置**: `src/views/HomeView.vue:167-218`

**问题描述**:
通过浏览器测试发现，在3D图谱页面搜索课程后，虽然代码中有放大节点和移动相机的逻辑，但从视觉上很难看出搜索结果。

**代码逻辑**:
```javascript
searchNode() {
  // ...找到节点后
  targetSphere.scale.lerpVectors(startScale, new THREE.Vector3(2, 2, 2), progress);
  camera.position.lerpVectors(startCameraPosition, targetCameraPosition, progress);
}
```

**问题**:
- 节点放大到 2 倍，但在密集的球形布局中可能不够明显
- 没有颜色高亮（节点颜色始终是蓝色）
- 没有其他节点的淡化效果（对比不明显）
- 没有搜索结果的文字提示（如"已定位到：人工智能"）

**建议改进**:
```javascript
searchNode() {
  const query = searchQuery.value.trim();
  if (!query) return;

  // 重置所有节点
  nodes.forEach(node => {
    node.scale.set(1, 1, 1);
    node.material.opacity = 0.3; // 其他节点变淡
  });

  const targetIndex = courseData.nodes.findIndex(node => node.label.includes(query));
  if (targetIndex !== -1) {
    const targetSphere = nodes[targetIndex];

    // 高亮目标节点
    targetSphere.material.emissive.setHex(0xff6600); // 橙色高亮
    targetSphere.material.opacity = 1.0;
    targetSphere.scale.set(3, 3, 3); // 更明显的放大

    // 显示提示信息
    showMessage(`已定位到：${courseData.nodes[targetIndex].label}`);

    // 相机动画...
  } else {
    showMessage(`未找到课程：${query}`);
  }
}
```

---

### 20. 2D图谱节点文字过小，难以阅读

**位置**: `src/components/myDagre.vue:207-221`

**问题描述**:
在 myDagre 页面，67 个课程节点全部显示在一个图谱中，导致节点密集、文字过小，几乎无法阅读。

**视觉效果**:
- 节点重叠严重
- 字体太小（font.size: 14）看不清
- 边线交错混乱

**当前配置**:
```javascript
nodes: {
  size: 200,
  font: {
    size: 14,  // 太小
    color: '#000',
  }
}
```

**建议改进**:

**方案 1: 增大字体和节点**
```javascript
nodes: {
  size: 300,  // 增大节点
  font: {
    size: 18,  // 增大字体
    bold: true,
  }
}
```

**方案 2: 分层显示**
- 实现课程分类（如问题#12中的：学科基础课、专业必修课、专业选修课）
- 点击分类才展开具体课程
- 减少单屏显示的节点数量

**方案 3: 缩放和筛选**
- 添加缩放控制（放大后文字才显示）
- 添加课程类别筛选（只显示某一类课程）
- 实现搜索高亮功能

---

### 21. 页面标题不一致

**位置**: 多个组件的 `mounted` 钩子

**问题描述**:
通过浏览器测试发现，除了登录页设置了 `document.title = "智能导学 - 登录"`，其他所有页面的标题都是默认的 "zhishitupu"。

**当前状态**:
- 登录页: ✅ "智能导学 - 登录"
- Home页: ❌ "zhishitupu"
- CourseOutline: ❌ "zhishitupu"
- ChatAssistant: ❌ "zhishitupu"
- myDagre: ❌ "zhishitupu"
- LsSb: ❌ "zhishitupu"

**影响**:
- 浏览器标签页显示不友好
- SEO 不利
- 用户打开多个标签页时无法区分

**建议修改**:

在每个页面的 `mounted` 钩子中添加：

```javascript
// HomeView.vue
mounted() {
  document.title = "智能导学 - 3D课程图谱";
}

// CourseOutline.vue
mounted() {
  document.title = "智能导学 - 课程详情";
}

// ChatAssistant.vue
mounted() {
  document.title = "智能导学 - AI助手";
}

// myDagre.vue
mounted() {
  document.title = "智能导学 - 2D课程图谱";
}

// LsSb.vue
mounted() {
  document.title = "智能导学 - 课程体系";
}
```

或者使用 Vue Router 的 `meta` 字段：
```javascript
// router/index.js
const routes = [
  {
    path: '/home',
    name: 'Home',
    component: HomeView,
    meta: { title: '智能导学 - 3D课程图谱' }
  },
  // ...
];

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '智能导学';
  next();
});
```

---

### 22. LsSb 页面背景图片影响可读性

**位置**: `src/components/LsSb.vue:289-295`

**问题描述**:
LsSb 页面使用了星空背景图片（`@/assets/pics/xingxi.png`），但与前景的网络图重叠，影响节点和文字的可读性。

**代码**:
```css
.background {
  background-image: url('@/assets/pics/xingxi.png');
  background-size: cover;
  background-repeat: no-repeat;
  width: 1680px;
  height: 100%;
}
```

**问题**:
- 背景图案与网络图线条交织，视觉混乱
- 节点标签在背景上对比度不够
- 背景图太抢眼，喧宾夺主

**建议改进**:

**方案 1: 降低背景透明度**
```css
.background {
  background-image: url('@/assets/pics/xingxi.png');
  background-size: cover;
  opacity: 0.3;  /* 降低透明度 */
  position: absolute;
  z-index: -1;
}
```

**方案 2: 添加半透明遮罩**
```vue
<div class="background">
  <div class="overlay"></div>
  <div id="mynetwork"></div>
</div>
```

```css
.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8); /* 白色半透明遮罩 */
  z-index: 1;
}

#mynetwork {
  position: relative;
  z-index: 2;
}
```

**方案 3: 移除背景图**
如果背景图主要是装饰性的，可以考虑移除，使用纯色背景：
```css
.background {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

---

### 23. 图片资源缺失检查

**位置**: 多个组件引用的图片路径

**问题描述**:
代码中引用了多个图片资源，但没有验证这些图片是否存在于项目中。

**引用的图片**:
- `@/assets/pics/logo.png` (NavBar.vue:5)
- `@/assets/pics/lightness.png` (NavBar.vue:12)
- `@/assets/pics/search.png` (NavBar.vue:15)
- `@/assets/pics/translate.png` (NavBar.vue:18)
- `@/assets/pics/homepage.png` (NavBar.vue:21)
- `@/assets/pics/dog.jpg` (NavBar.vue:24)
- `@/assets/STAT0031121004.png` (CourseOutline.vue:54)
- `@/assets/ls.jpg` (ChatAssistant.vue:32)
- `@/assets/pics/xingxi.png` (LsSb.vue:290)

**建议操作**:
1. 检查 `src/assets` 目录，确认所有图片都存在
2. 缺失的图片应该补充或移除引用
3. 添加图片加载错误处理：
```vue
<img
  :src="require('@/assets/pics/logo.png')"
  @error="handleImageError"
  alt="Logo"
>
```

```javascript
handleImageError(e) {
  e.target.src = '/placeholder-image.png'; // 使用占位图
}
```

---

## 📋 优先级建议（最终更新）

| 优先级 | 问题编号 | 问题 | 影响 |
|--------|---------|------|------|
| 🔴 高 | #2 | DeepSeek API Key 泄露 | 安全风险 |
| 🔴 高 | #9 | 豆包 API Key 泄露 | 安全风险 |
| 🔴 高 | #11 | 登录功能是假的 | 安全风险 |
| 🔴 高 | #1 | ChatAssistant 缺少对话历史 | 功能缺陷 |
| 🔴 高 | #10 | 两个独立聊天实现 | 架构混乱 |
| 🟡 中 | #3 | 课程数据重复定义（3次） | 维护困难 |
| 🟡 中 | #12 | 课程数据第4次重复 | 维护困难 |
| 🟡 中 | #4 | 课程详情硬编码 | 功能不完整 |
| 🟡 中 | #13 | 无效的课程 URL | 数据质量 |
| 🟡 中 | #20 | 2D图谱文字过小 | 用户体验 |
| 🟡 中 | #22 | 背景图影响可读性 | 用户体验 |
| 🟢 低 | #14 | NavBar 按钮无功能 | 用户体验 |
| 🟢 低 | #15 | 主题切换未实现 | 功能缺失 |
| 🟢 低 | #16 | 固定宽度设计 | 响应式问题 |
| 🟢 低 | #17 | SideBar 缺少历史 | 功能缺陷 |
| 🟢 低 | #19 | 搜索缺少反馈 | 用户体验 |
| 🟢 低 | #21 | 页面标题不一致 | SEO/UX |
| 🟢 低 | #23 | 图片资源检查 | 资源管理 |
| 🟢 低 | #5 | API 参数缺失 | 体验优化 |
| 🟢 低 | #6 | 格式化过度 | 显示效果 |
| 🟢 低 | #7 | 错误处理不足 | 用户体验 |
| 🟢 低 | #8 | localStorage 风险 | 数据安全 |
| 🟢 低 | #18 | 全局变量使用 | 代码质量 |

---

## 📝 更新日志

- **2025-10-26 14:00**: 初始文档创建，记录 8 个问题
- **2025-10-26 15:30**: 新增 10 个问题（#9-#18），总计 18 个问题
- **2025-10-26 16:00**: 通过 Playwright 浏览器测试，新增 5 个问题（#19-#23），总计 23 个问题
