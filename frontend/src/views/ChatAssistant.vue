<template>
  <div class="app-container">
    <!-- 侧边栏 -->
    <nav class="sidebar">
      <div class="logo-section">
        <h2>智能导学小助手</h2>
      </div>
      <ul class="nav-menu">
        <li 
          class="nav-item" 
          :class="{active: activeNav === 0}"
          @click="handleNavClick(0)"
        >
          <span>🆕</span> 新的聊天
        </li>
        <li 
          class="nav-item" 
          :class="{active: activeNav === 1}"
          @click="handleNavClick(1)"
        >
          <span>🔍</span> 搜索会话
        </li>
        <li 
          class="nav-item" 
          :class="{active: activeNav === 2}"
          @click="handleNavClick(2)"
        >
          <span>📚</span> 对话历史
        </li>
      </ul>
      <div class="sidebar-image">
        <img :src="require('@/assets/ls.jpg')" alt="华师标志" style="width: 100%;">
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 搜索框 -->
      <div id="searchBox" v-show="showSearch">
        <input 
          type="text" 
          id="searchInput" 
          placeholder="输入关键词搜索历史会话..."
          v-model="searchKeyword"
          @input="handleSearch"
        >
        <div id="searchResults">
          <div 
            v-for="(entry, index) in searchResults" 
            :key="index" 
            class="search-item"
            :data-session="entry.session"
          >
            <div class="search-header">
              <span class="time">{{ formatDate(entry.timestamp) }}</span>
              <button @click="restoreConversation(entry.session)">恢复此会话</button>
            </div>
            <div class="search-content">
              <p class="query"><strong>问题：</strong><span v-html="highlightKeywords(entry.query, searchKeyword)"></span></p>
              <p class="response"><strong>回答：</strong><span v-html="highlightKeywords(entry.response, searchKeyword)"></span></p>
            </div>
          </div>
          <div v-if="searchResults.length === 0 && searchKeyword" class="no-results">
            未找到相关对话记录
          </div>
        </div>
      </div>

      <!-- 聊天主界面 -->
      <div class="chat-layout" v-show="showChat">
        <div class="chat-container" :class="{ 'with-recommendations': showRecommendations }">
          <div id="chatHistory">
            <div
              v-for="(message, index) in chatMessages"
              :key="index"
              :class="`message ${message.role}`"
            >
              <div class="message-bubble" v-html="message.content"></div>
            </div>
          </div>
          <div class="input-section">
            <div class="input-group">
              <input
                type="text"
                id="userInput"
                placeholder="输入消息（Enter发送，Shift+Enter换行）"
                v-model="userMessage"
                @keydown.enter.exact.prevent="sendMessage"
              >
              <button id="sendBtn" @click="sendMessage">发送</button>
            </div>
          </div>
        </div>

        <!-- 推荐结果展示区域 -->
        <div v-if="showRecommendations" class="recommendations-panel">
          <div class="panel-header">
            <h3>📚 课程推荐</h3>
            <button class="close-btn" @click="showRecommendations = false">✕</button>
          </div>
          <div class="recommendations-content">
            <div v-if="recommendedCourses.length === 0" class="empty-recommendations">
              <p>暂无推荐课程</p>
              <p class="hint">询问AI助手获取个性化课程推荐</p>
            </div>
            <div v-else class="course-cards">
              <div
                v-for="(course, index) in recommendedCourses"
                :key="index"
                class="course-card"
              >
                <div class="course-rank">{{ index + 1 }}</div>
                <div class="course-info">
                  <h4 class="course-name">{{ course.label || course.name }}</h4>
                  <div class="course-meta">
                    <span class="meta-tag">{{ course.difficulty || '中等' }}</span>
                    <span class="meta-tag">{{ course.credits || 3 }}学分</span>
                    <span class="meta-tag">{{ course.course_type || '必修' }}</span>
                  </div>
                  <p v-if="course.reason" class="course-reason">{{ course.reason }}</p>
                  <div v-if="course.prerequisites && course.prerequisites.length > 0" class="prerequisites">
                    <span class="prereq-label">先修:</span>
                    <span class="prereq-items">{{ course.prerequisites.join(', ') }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 历史记录容器 -->
      <div id="historyContainer" v-show="showHistory">
        <div 
          v-for="(entry, index) in chatHistory" 
          :key="index" 
          class="history-item"
        >
          <div class="time">{{ formatDate(entry.timestamp) }}</div>
          <div class="query">问：{{ entry.query }}</div>
          <div class="response">答：{{ entry.response }}</div>
          <div class="item-actions">
            <button @click="restoreConversation(entry.session)">恢复对话</button>
            <button @click="deleteHistoryItem(entry.timestamp)" class="delete-btn">删除</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github-dark.css';

// Configure marked to use highlight.js for code syntax highlighting
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value;
      } catch (err) {
        console.error('Highlight error:', err);
      }
    }
    return hljs.highlightAuto(code).value;
  },
  breaks: true, // Convert \n to <br>
  gfm: true // Enable GitHub flavored markdown
});

export default {
  name: 'ChatAssistant',
  data() {
    return {
      activeNav: 0,
      showChat: true,
      showHistory: false,
      showSearch: false,
      userMessage: '',
      isWaitingForResponse: false,
      chatMessages: [],
      chatHistory: [],
      chatDatabase: [],
      searchKeyword: '',
      searchResults: [],
      currentSession: Date.now().toString(),
      MAX_HISTORY: 50,
      recommendedCourses: [], // Store recommended courses
      showRecommendations: false, // Control recommendation panel visibility
      // 知识图谱数据（保持不变）
      nodes: [
      {"id": "数学分析"},
        {"id": "并行计算"},
        {"id": "数值计算及其计算机实现"},
        {"id": "自然语言处理导论"},
        {"id": "操作系统实践(进阶)"},
        {"id": "现代CAD技术(A)"},
        {"id": "计算机视觉"},
        {"id": "游戏项目实践"},
        {"id": "数据挖掘"},
        {"id": "多智能体系统与实践"},
        {"id": "计算机网络工程"},
        {"id": "网络安全基础"},
        {"id": "存储技术基础"},
        {"id": "模式识别与机器学习"},
        {"id": "服务器维护及网站建设"},
        {"id": "问题求解与程序设计"},
        {"id": "计算机图形学"},
        {"id": "云计算实践"},
        {"id": "创新创业基础与实践"},
        {"id": "多媒体技术"},
        {"id": "算法分析与设计"},
        {"id": "数字图像处理"},
        {"id": "人机交互技术"},
        {"id": "数学建模"},
        {"id": "数据可视化"},
        {"id": "最优化方法"},
        {"id": "计算机新技术前沿"},
        {"id": "信息系统安全概论"},
        {"id": "编程思维与实践"},
        {"id": "程序设计原理与C语言"},
        {"id": "大学物理B(一)：力学，热学"},
        {"id": "大学物理B（二）：电磁学、波动与光学部分"},
        {"id": "概率论与数理统计"},
        {"id": "计算机导论"},
        {"id": "离散数学"},
        {"id": "人工智能"},
        {"id": "数据结构"},
        {"id": "数字逻辑电路"},
        {"id": "线性代数"},
        {"id": "操作系统"},
        {"id": "计算机网络"},
        {"id": "嵌入式系统原理与实践"},
        {"id": "计算机系统结构"},
        {"id": "数据库系统原理与实践"},
        {"id": "编译原理与实践"},
        {"id": "信息工程伦理"},
        {"id": "线性代数进阶"},
        {"id": "计算机基础实践"},
        {"id": "面向对象程序设计（基于Java）"},
        {"id": "面向对象程序设计（基于C++）"},
        {"id": "专业英语"},
        {"id": "信号与系统"},
        {"id": "计算机组成与实践"},
        {"id": "生物信息学"},
        {"id": "大数据系统"},
        {"id": "智能推荐系统"},
        {"id": "视觉感知与前沿技术"},
        {"id": "统计学习算法导论"},
        {"id": "现代CAD技术（B）"},
        {"id": "可信机器学习"},
        {"id": "计算机动画"},
        {"id": "深度学习基础与导论"},
        {"id": "强化学习基础"},
        {"id": "AIoT系统设计与实践"},
        {"id": "写作与表达"},
        {"id": "python程序设计"},
        {"id": "大学英语"}
        // ... 保持原有的节点数据不变
      ],
      edges: [
      {"source": "计算机导论", "target": "问题求解与程序设计"},
        {"source": "程序设计原理与C语言", "target": "问题求解与程序设计"},
        {"source": "数学分析", "target": "问题求解与程序设计"},
        {"source": "数学分析", "target": "大学物理B(一)：力学，热学"},
        {"source": "数学分析", "target": "大学物理B（二）：电磁学、波动与光学部分"},
        {"source": "数学分析", "target": "计算机图形学"},
        {"source": "线性代数", "target": "计算机图形学"},
        {"source": "面向对象程序设计（基于C++）", "target": "计算机图形学"},
        {"source": "数据结构", "target": "计算机图形学"},
        {"source": "计算机网络工程", "target": "云计算实践"},
        {"source": "程序设计原理与C语言", "target": "算法分析与设计"},
        {"source": "数据结构", "target": "算法分析与设计"},
        {"source": "python程序设计", "target": "数字图像处理"},
        {"source": "程序设计原理与C语言", "target": "人机交互技术"},
        {"source": "数学分析", "target": "数学建模"},
        {"source": "线性代数", "target": "数学建模"},
        {"source": "概率论与数理统计", "target": "数学建模"},
        {"source": "编程思维与实践", "target": "数学建模"},
        {"source": "数据结构", "target": "数据可视化"},
        {"source": "程序设计原理与C语言", "target": "数据可视化"},
        {"source": "线性代数", "target": "最优化方法"},
        {"source": "计算机导论", "target": "信息系统安全概论"},
        {"source": "计算机网络工程", "target": "信息系统安全概论"},
        {"source": "数据库系统原理与实践", "target": "信息系统安全概论"},
        {"source": "操作系统", "target": "信息系统安全概论"},
        {"source": "编程思维与实践", "target": "人工智能"},
        {"source": "程序设计原理与C语言", "target": "数据结构"},
        {"source": "概率论与数理统计", "target": "人工智能"},
        {"source": "计算机导论", "target": "人工智能"},
        {"source": "离散数学", "target": "人工智能"},
        {"source": "数据结构", "target": "人工智能"},
        {"source": "数学分析", "target": "人工智能"},
        {"source": "线性代数", "target": "离散数学"},
        {"source": "线性代数", "target": "人工智能"},
        {"source": "操作系统", "target": "并行计算"},
        {"source": "计算机组成与实践", "target": "并行计算"},
        {"source": "数学分析", "target": "数值计算及其计算机实现"},
        {"source": "离散数学", "target": "数值计算及其计算机实现"},
        {"source": "程序设计原理与C语言", "target": "数值计算及其计算机实现"},
        {"source": "概率论与数理统计", "target": "自然语言处理导论"},
        {"source": "人工智能", "target": "自然语言处理导论"},
        {"source": "操作系统", "target": "操作系统实践(进阶)"},
        {"source": "面向对象程序设计（基于C++）", "target": "现代CAD技术(A)"},
        {"source": "python程序设计", "target": "现代CAD技术(A)"},
        {"source": "数字图像处理", "target": "计算机视觉"},
        {"source": "数据结构", "target": "游戏项目实践"},
        {"source": "面向对象程序设计（基于Java）", "target": "游戏项目实践"},
        {"source": "面向对象程序设计（基于C++）", "target": "游戏项目实践"},
        {"source": "面向对象程序设计（基于Java）", "target": "数据挖掘"},
        {"source": "面向对象程序设计（基于C++）", "target": "数据挖掘"},
        {"source": "数学分析", "target": "数据挖掘"},
        {"source": "线性代数", "target": "数据挖掘"},
        {"source": "概率论与数理统计", "target": "数据挖掘"},
        {"source": "程序设计原理与C语言", "target": "数据挖掘"},
        {"source": "数学分析", "target": "多智能体系统与实践"},
        {"source": "概率论与数理统计", "target": "多智能体系统与实践"},
        {"source": "线性代数", "target": "多智能体系统与实践"},
        {"source": "人工智能", "target": "多智能体系统与实践"},
        {"source": "计算机网络", "target": "计算机网络工程"},
        {"source": "操作系统", "target": "计算机网络工程"},
        {"source": "操作系统", "target": "网络安全基础"},
        {"source": "计算机网络", "target": "网络安全基础"},
        {"source": "计算机网络", "target": "存储技术基础"},
        {"source": "数学分析", "target": "模式识别与机器学习"},
        {"source": "概率论与数理统计", "target": "模式识别与机器学习"},
        {"source": "人工智能", "target": "模式识别与机器学习"},
        {"source": "线性代数", "target": "模式识别与机器学习"},
        {"source": "程序设计原理与C语言", "target": "操作系统"},
        {"source": "数据结构", "target": "操作系统"},
        {"source": "计算机组成与实践", "target": "操作系统"},
        {"source": "操作系统", "target": "计算机网络"},
        {"source": "计算机系统结构", "target": "计算机网络"},
        {"source": "程序设计原理与C语言", "target": "嵌入式系统原理与实践"},
        {"source": "计算机组成与实践", "target": "嵌入式系统原理与实践"},
        {"source": "数字逻辑电路", "target": "嵌入式系统原理与实践"},
        {"source": "数据结构", "target": "嵌入式系统原理与实践"},
        {"source": "操作系统", "target": "计算机系统结构"},
        {"source": "计算机组成与实践", "target": "计算机系统结构"},
        {"source": "程序设计原理与C语言", "target": "计算机系统结构"},
        {"source": "数据结构", "target": "数据库系统原理与实践"},
        {"source": "操作系统", "target": "数据库系统原理与实践"},
        {"source": "程序设计原理与C语言", "target": "编译原理与实践"},
        {"source": "离散数学", "target": "编译原理与实践"},
        {"source": "数据结构", "target": "编译原理与实践"},
        {"source": "操作系统", "target": "编译原理与实践"},
        {"source": "计算机网络", "target": "信息工程伦理"},
        {"source": "计算机导论", "target": "信息工程伦理"},
        {"source": "人工智能", "target": "信息工程伦理"},
        {"source": "线性代数", "target": "线性代数进阶"},
        {"source": "程序设计原理与C语言", "target": "面向对象程序设计（基于Java）"},
        {"source": "程序设计原理与C语言", "target": "面向对象程序设计（基于C++）"},
        {"source": "计算机导论", "target": "专业英语"},
        {"source": "大学英语", "target": "专业英语"},
        {"source": "数学分析", "target": "信号与系统"},
        {"source": "人工智能", "target": "生物信息学"},
        {"source": "操作系统", "target": "大数据系统"},
        {"source": "线性代数", "target": "大数据系统"},
        {"source": "离散数学", "target": "大数据系统"},
        {"source": "数据结构", "target": "大数据系统"},
        {"source": "数据库系统原理与实践", "target": "大数据系统"},
        {"source": "编程思维与实践", "target": "大数据系统"},
        {"source": "人工智能", "target": "智能推荐系统"},
        {"source": "数据结构", "target": "智能推荐系统"},
        {"source": "人工智能", "target": "视觉感知与前沿技术"},
        {"source": "数据结构", "target": "视觉感知与前沿技术"},
        {"source": "线性代数", "target": "视觉感知与前沿技术"},
        {"source": "计算机视觉", "target": "视觉感知与前沿技术"},
        {"source": "数学分析", "target": "统计学习算法导论"},
        {"source": "概率论与数理统计", "target": "统计学习算法导论"},
        {"source": "数学分析", "target": "现代CAD技术（B）"},
        {"source": "人工智能", "target": "可信机器学习"},
        {"source": "面向对象程序设计（基于Java）", "target": "计算机动画"},
        {"source": "数字图像处理", "target": "深度学习基础与导论"},
        {"source": "模式识别与机器学习", "target": "深度学习基础与导论"},
        {"source": "人工智能", "target": "强化学习基础"},
        {"source": "嵌入式系统原理与实践", "target": "AIoT系统设计与实践"},
        {"source": "自然语言处理导论", "target": "AIoT系统设计与实践"},
        {"source": "模式识别与机器学习", "target": "AIoT系统设计与实践"},
        {"source": "数字图像处理", "target": "AIoT系统设计与实践"}
        // ... 保持原有的边数据不变
      ]
    }
  },
  created() {
    this.loadHistory();
    this.initializeSystemMessage();
  },
  methods: {
    initializeSystemMessage() {
      const knowledgeGraphPrompt = this.generateKnowledgeGraphPrompt(this.nodes, this.edges);
      this.chatMessages.push({
        role: "assistant",
        content: "你好！我是智能导学小助手，可以帮助你进行学业规划和课程咨询。"
      });
      localStorage.setItem('systemPrompt', knowledgeGraphPrompt);
    },
    generateKnowledgeGraphPrompt(nodes, edges) {
      // 实现与之前相同的知识图谱生成逻辑
      const nodeNames = new Set(nodes.map(node => node.id));
      
      const sourceToTargets = {};
      for (const edge of edges) {
        const source = edge.source;
        const target = edge.target;
        if (!sourceToTargets[source]) {
          sourceToTargets[source] = [];
        }
        sourceToTargets[source].push(target);
      }

      const promptLines = [];
      for (const [source, targets] of Object.entries(sourceToTargets)) {
        if (targets && targets.length > 0) {
          const targetsList = targets.join('、');
          promptLines.push(`${source}是${targetsList}的前置或基础课程。`);
        } else {
          promptLines.push(`${source}是一门独立课程。`);
        }
      }
      
      const connectedNodes = new Set();
      edges.forEach(edge => {
        connectedNodes.add(edge.source);
        connectedNodes.add(edge.target);
      });
      
      const isolatedNodes = [...nodeNames].filter(node => !connectedNodes.has(node));
      for (const node of isolatedNodes) {
        promptLines.push(`${node}是一门独立课程。`);
      }

      return "你将扮演一个智能导学项目的AI助手，名字叫智能导学小助手，服务计算机科学与技术专业的学生。回答时结合下列知识图谱参考课程关系，帮助学生学业规划、问题解答。推荐学习资源.不要绘制任何流程图,可以把想绘制的流程图用语言叙述。\n你有以下知识图谱，描述了课程之间的关系：\n" + 
             promptLines.map(line => `- ${line}`).join('\n') + 
             "\n请根据上面的知识图谱，结合学生的问题，优先参考已有的课程内容、课程关系来回答。";
    },
    handleNavClick(index) {
      this.activeNav = index;
      this.showChat = index === 0;
      this.showSearch = index === 1;
      this.showHistory = index === 2;
      
      if (index === 0) {
        this.createNewChat();
      }
    },
    createNewChat() {
      this.currentSession = Date.now().toString();
      this.chatMessages = [];
    },
    async sendMessage() {
      const message = this.userMessage.trim();
      if (!message || this.isWaitingForResponse) return;

      this.isWaitingForResponse = true;
      this.addMessage('user', message);
      this.userMessage = '';

      try {
        const response = await axios.post('https://api.deepseek.com/v1/chat/completions', {
          model: 'deepseek-chat',
          messages: [
            { role: 'system', content: localStorage.getItem('systemPrompt') },
            { role: 'user', content: message }
          ]
        }, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${process.env.VUE_APP_DEEPSEEK_API_KEY || ''}`
          }
        });

        const reply = response.data.choices[0].message.content;

        // Extract course recommendations if present
        this.extractRecommendations(reply, message);

        const formattedReply = this.formatResponse(reply);
        this.addMessage('assistant', formattedReply);
        this.saveToHistory(message, formattedReply);

      } catch (error) {
        console.error('API请求失败:', error);
        this.addMessage('assistant', '抱歉，暂时无法处理您的请求，请稍后再试。');
      } finally {
        this.isWaitingForResponse = false;
      }
    },
    extractRecommendations(reply, userQuery) {
      // Check if the reply contains course recommendations
      const recommendKeywords = ['推荐', '建议', '学习路径', '课程'];
      const hasRecommendation = recommendKeywords.some(keyword =>
        userQuery.includes(keyword) || reply.includes(keyword)
      );

      if (hasRecommendation) {
        // Extract course names from reply and match with nodes
        const extractedCourses = [];
        this.nodes.forEach(node => {
          if (reply.includes(node.id)) {
            // Find course details
            const courseInfo = {
              label: node.id,
              difficulty: this.getCourseProperty(node.id, 'difficulty'),
              credits: this.getCourseProperty(node.id, 'credits'),
              course_type: this.getCourseProperty(node.id, 'course_type'),
              prerequisites: this.getPrerequisites(node.id)
            };
            extractedCourses.push(courseInfo);
          }
        });

        if (extractedCourses.length > 0) {
          this.recommendedCourses = extractedCourses.slice(0, 10); // Limit to 10
          this.showRecommendations = true;
        }
      }
    },
    getCourseProperty(courseId, property) {
      // This would ideally fetch from course_data.json or backend API
      // For now, return default values
      const defaults = {
        difficulty: '中等',
        credits: 3,
        course_type: '必修'
      };
      return defaults[property];
    },
    getPrerequisites(courseId) {
      // Find all courses that are prerequisites for this course
      const prerequisites = [];
      this.edges.forEach(edge => {
        if (edge.target === courseId) {
          prerequisites.push(edge.source);
        }
      });
      return prerequisites;
    },
    formatResponse(text) {
      // Clean up AI-specific phrases
      text = text.replace(/根据知识图谱(推荐|可知|显示)/g, '');

      // Use marked to render markdown to HTML
      try {
        const html = marked.parse(text);
        return html.trim();
      } catch (err) {
        console.error('Markdown parse error:', err);
        // Fallback: convert newlines to <br>
        return text.replace(/\n/g, '<br>').trim();
      }
    },
    addMessage(role, content) {
      this.chatMessages.push({ role, content });
      this.$nextTick(() => {
        const historyEl = document.getElementById('chatHistory');
        if (historyEl) historyEl.scrollTop = historyEl.scrollHeight;
      });
    },
    saveToHistory(query, response) {
      const record = {
        session: this.currentSession,
        timestamp: Date.now(),
        query: query,
        response: response
      };
      
      this.chatHistory.unshift(record);
      this.chatDatabase.unshift(record);
      
      // 保持历史记录不超过最大值
      if (this.chatHistory.length > this.MAX_HISTORY) {
        this.chatHistory = this.chatHistory.slice(0, this.MAX_HISTORY);
      }
      
      localStorage.setItem('chatHistory', JSON.stringify(this.chatHistory));
    },
    loadHistory() {
      const savedHistory = localStorage.getItem('chatHistory');
      this.chatHistory = savedHistory ? JSON.parse(savedHistory) : [];
      this.chatDatabase = [...this.chatHistory];
    },
    async handleSearch() {
      if (!this.searchKeyword) {
        this.searchResults = [];
        return;
      }
      
      // 模拟异步搜索
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const keyword = this.searchKeyword.toLowerCase();
      this.searchResults = this.chatDatabase.filter(entry =>
        entry.query.toLowerCase().includes(keyword) ||
        entry.response.toLowerCase().includes(keyword)
      ).sort((a, b) => b.timestamp - a.timestamp);
    },
    formatDate(timestamp) {
      return new Date(timestamp).toLocaleString();
    },
    highlightKeywords(text, keyword) {
      if (!keyword || !text) return text;
      
      const escapedText = this.escapeHtml(text);
      const escapedKeyword = this.escapeHtml(keyword);
      
      const regex = new RegExp(this.escapeRegExp(escapedKeyword), 'gi');
      
      return escapedText.replace(regex, match => 
        `<span class="highlight">${match}</span>`
      );
    },
    escapeHtml(text) {
      if (!text) return text;
      return text.toString()
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    },
    escapeRegExp(string) {
      return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    },
    restoreConversation(sessionId) {
      // 1. 切换到聊天界面
      this.activeNav = 0;
      this.showChat = true;
      this.showSearch = false;
      this.showHistory = false;
      
      // 2. 设置当前会话ID
      this.currentSession = sessionId;
      
      // 3. 加载该会话的历史消息
      const sessionMessages = this.chatDatabase
        .filter(item => item.session === sessionId)
        .sort((a, b) => a.timestamp - b.timestamp);
      
      // 4. 重建聊天消息
      this.chatMessages = [];
      sessionMessages.forEach(entry => {
        this.chatMessages.push({ role: 'user', content: entry.query });
        this.chatMessages.push({ role: 'assistant', content: entry.response });
      });
      
      // 5. 滚动到底部
      this.$nextTick(() => {
        const historyEl = document.getElementById('chatHistory');
        if (historyEl) historyEl.scrollTop = historyEl.scrollHeight;
      });
    },
    deleteHistoryItem(timestamp) {
      this.chatHistory = this.chatHistory.filter(item => item.timestamp !== timestamp);
      this.chatDatabase = this.chatDatabase.filter(item => item.timestamp !== timestamp);
      localStorage.setItem('chatHistory', JSON.stringify(this.chatHistory));
      
      // 如果是当前会话的消息被删除，可能需要更新聊天界面
      if (this.chatMessages.some(msg => msg.timestamp === timestamp)) {
        this.chatMessages = this.chatMessages.filter(msg => msg.timestamp !== timestamp);
      }
    }
  }
}
</script>

<style scoped>
:root {
  --sidebar-width: 260px;
  --primary-color: #2c3e50;
  --accent-color: #3498db;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "PingFang SC", "Microsoft YaHei", "Segoe UI", system-ui, sans-serif;
  display: flex;
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e2e 0%, #2c3548 100%);
}

/* 侧边栏样式 */
.sidebar {
  width: var(--sidebar-width);
  background: linear-gradient(180deg, #2c3e50 0%, #1a252f 100%);
  color: white;
  padding: 20px;
  position: fixed;
  height: 100%;
  border-right: 1px solid rgba(102, 126, 234, 0.3);
  z-index: 100;
  box-shadow: 4px 0 16px rgba(0, 0, 0, 0.3);
}

.logo-section {
  padding: 20px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.3);
  margin-bottom: 30px;
  text-align: center;
}

.logo-section h2 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0;
}

.nav-menu {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nav-item {
  padding: 14px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transform: translateX(4px);
}

.nav-item:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: translateX(2px);
}

/* 主内容区 */
.main-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  padding: 40px;
  min-height: 100vh;
}

/* 聊天布局 - 支持推荐面板 */
.chat-layout {
  display: flex;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 聊天容器 */
.chat-container {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(102, 126, 234, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  text-align: left;
  transition: all 0.3s ease;
}

.chat-container.with-recommendations {
  max-width: 800px;
}

#chatHistory {
  height: 500px;
  padding: 24px;
  overflow-y: auto;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(5px);
}

.message {
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}

.message.user {
  text-align: right;
}

.message-bubble {
  display: inline-block;
  padding: 12px 20px;
  border-radius: 20px;
  max-width: 70%;
  line-height: 1.6;
  text-align: left;
}

.user .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.assistant .message-bubble {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #f0f0f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* Markdown 样式 */
.message-bubble :deep(h1),
.message-bubble :deep(h2),
.message-bubble :deep(h3) {
  margin: 16px 0 12px 0;
  font-weight: 600;
}

.message-bubble :deep(h1) { font-size: 1.5em; }
.message-bubble :deep(h2) { font-size: 1.3em; }
.message-bubble :deep(h3) { font-size: 1.1em; }

.message-bubble :deep(p) {
  margin: 8px 0;
  line-height: 1.6;
}

.message-bubble :deep(ul),
.message-bubble :deep(ol) {
  margin: 12px 0;
  padding-left: 24px;
}

.message-bubble :deep(li) {
  margin: 6px 0;
}

.message-bubble :deep(code) {
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.9em;
}

.message-bubble :deep(pre) {
  background: #1e1e1e;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
}

.message-bubble :deep(pre code) {
  background: transparent;
  padding: 0;
  color: #d4d4d4;
}

.message-bubble :deep(blockquote) {
  border-left: 4px solid var(--accent-color);
  padding-left: 16px;
  margin: 12px 0;
  color: #666;
  font-style: italic;
}

.message-bubble :deep(table) {
  border-collapse: collapse;
  margin: 12px 0;
  width: 100%;
}

.message-bubble :deep(th),
.message-bubble :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.message-bubble :deep(th) {
  background: #f5f5f5;
  font-weight: 600;
}

.message-bubble :deep(strong) {
  font-weight: 600;
}

.message-bubble :deep(em) {
  font-style: italic;
}

.message-bubble :deep(a) {
  color: var(--accent-color);
  text-decoration: none;
}

.message-bubble :deep(a:hover) {
  text-decoration: underline;
}

/* 推荐面板样式 */
.recommendations-panel {
  width: 400px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  overflow: hidden;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.panel-header {
  background: linear-gradient(135deg, var(--accent-color) 0%, #2980b9 100%);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.recommendations-content {
  padding: 20px;
  max-height: 500px;
  overflow-y: auto;
}

.empty-recommendations {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.empty-recommendations .hint {
  font-size: 14px;
  margin-top: 10px;
  opacity: 0.7;
}

.course-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.course-card {
  background: #f8fafb;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  gap: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.course-card:hover {
  background: #e8eef3;
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.course-rank {
  background: var(--accent-color);
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.course-info {
  flex: 1;
}

.course-name {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.course-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.meta-tag {
  background: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  color: #666;
  border: 1px solid #e0e0e0;
}

.course-reason {
  font-size: 13px;
  color: #555;
  margin: 8px 0;
  line-height: 1.5;
}

.prerequisites {
  font-size: 12px;
  color: #666;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #ddd;
}

.prereq-label {
  font-weight: 600;
  margin-right: 4px;
}

.prereq-items {
  opacity: 0.8;
}

/* 输入区域 */
.input-section {
  padding: 24px;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(102, 126, 234, 0.2);
}

.input-group {
  display: flex;
  gap: 12px;
}

#userInput {
  flex: 1;
  padding: 14px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 30px;
  font-size: 16px;
  color: white;
  transition: all 0.2s;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

#userInput::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

#userInput:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

button:active {
  transform: translateY(0);
}

/* 历史记录样式 */
.history-item {
  padding: 15px;
  margin: 10px 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

/* 搜索框样式 */
#searchBox {
  max-width: 800px;
  margin: 0 auto 30px;
}

#searchInput {
  width: 100%;
  padding: 14px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 30px;
  margin-bottom: 15px;
  font-size: 16px;
  color: white;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

#searchInput::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

#searchInput:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

#searchResults {
  max-height: 500px;
  overflow-y: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.search-item {
  padding: 15px;
  margin: 10px 0;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #eee;
  transition: all 0.2s;
}

.search-item:hover {
  background-color: #f8f9fa;
  transform: translateY(-2px);
}

.search-item .time {
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.search-item .query,
.search-item .response {
  margin-bottom: 8px;
  line-height: 1.5;
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.search-header button {
  padding: 6px 12px;
  font-size: 12px;
}

.no-results {
  padding: 20px;
  text-align: center;
  color: #666;
}

.sidebar-image {
  padding: 0 15px;
  margin-top: auto;
}

.sidebar-image img {
  display: block;
  max-width: 200px;
  margin: 20px auto;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}

.sidebar-image img:hover {
  transform: scale(1.05);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.highlight {
  background-color: yellow;
  font-weight: bold;
}

.app-container {
  display: flex;
  min-height: 100vh;
}

.item-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #eee;
}

.item-actions button {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 4px;
  background: #f0f0f0;
  color: #333;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.item-actions button:hover {
  background: #e0e0e0;
}

.item-actions .delete-btn {
  background: #ffebee;
  color: #c62828;
}

.item-actions .delete-btn:hover {
  background: #ffcdd2;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .chat-layout {
    flex-direction: column;
  }

  .recommendations-panel {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
  }

  .chat-container.with-recommendations {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    padding: 20px;
  }

  .sidebar {
    display: none; /* 或实现移动端侧边栏菜单 */
  }

  #chatHistory {
    height: 400px;
  }

  .message-bubble {
    max-width: 85%;
  }

  .course-card {
    padding: 12px;
  }

  .recommendations-content {
    padding: 16px;
  }

  .input-group {
    flex-wrap: wrap;
  }

  #userInput {
    min-width: 100%;
    margin-bottom: 8px;
  }
}

/* 滚动条美化 */
#chatHistory::-webkit-scrollbar,
.recommendations-content::-webkit-scrollbar {
  width: 8px;
}

#chatHistory::-webkit-scrollbar-track,
.recommendations-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

#chatHistory::-webkit-scrollbar-thumb,
.recommendations-content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

#chatHistory::-webkit-scrollbar-thumb:hover,
.recommendations-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 加载状态 */
.input-section button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>