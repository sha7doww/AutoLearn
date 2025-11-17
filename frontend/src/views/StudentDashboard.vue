<template>
  <div class="student-dashboard">
    <div class="dashboard-header">
      <h1>SmartPath 智能导学系统</h1>
      <p class="header-subtitle">基于知识追踪的个性化学习路径规划</p>
    </div>

    <div class="dashboard-content">
      <!-- 成绩输入区域 -->
      <div class="input-section">
        <div class="section-card">
          <h3 class="section-title">📊 输入您的课程成绩</h3>
          <div class="score-input-grid">
            <div v-for="course in sampleCourses" :key="course.name" class="score-input-item">
              <label>{{ course.name }}</label>
              <input
                type="number"
                v-model.number="courseScores[course.name]"
                min="0"
                max="100"
                placeholder="0-100"
                class="score-input"
              />
            </div>
          </div>
          <button @click="analyzeKnowledge" class="btn btn-primary" :disabled="isAnalyzing">
            {{ isAnalyzing ? '分析中...' : '分析知识状态' }}
          </button>
        </div>

        <!-- 目标课程选择 -->
        <div class="section-card">
          <h3 class="section-title">🎯 选择目标课程</h3>
          <select v-model="targetCourseId" class="course-select">
            <option value="">请选择目标课程</option>
            <option v-for="course in availableCourses" :key="course.id" :value="course.id">
              {{ course.label }} ({{ course.difficulty }})
            </option>
          </select>
          <button @click="generatePath" class="btn btn-primary" :disabled="isGeneratingPath || !targetCourseId">
            {{ isGeneratingPath ? '生成中...' : '生成学习路径' }}
          </button>
        </div>
      </div>

      <!-- 知识状态可视化 -->
      <div v-if="knowledgeStateData" class="visualization-section">
        <KnowledgeRadar
          :knowledge-state="knowledgeStateData.knowledge_vector"
          :overall-level="knowledgeStateData.overall_level"
          :strengths="knowledgeStateData.strengths"
          :weaknesses="knowledgeStateData.weaknesses"
          :loading="isAnalyzing"
        />
      </div>

      <!-- 学习路径可视化 -->
      <div v-if="learningPath && learningPath.length > 0" class="visualization-section">
        <LearningPathTimeline
          :path="learningPath"
          :loading="isGeneratingPath"
          @course-selected="onCourseSelected"
          @export-path="exportLearningPath"
          @adjust-path="adjustLearningPath"
        />
      </div>

      <!-- 课程推荐 -->
      <div v-if="recommendations.length > 0" class="recommendations-section">
        <div class="section-card">
          <h3 class="section-title">💡 智能推荐课程</h3>
          <div class="recommendation-list">
            <div
              v-for="rec in recommendations"
              :key="rec.course_id"
              class="recommendation-card"
              :class="{ 'prerequisites-met': rec.prerequisites_met }"
            >
              <div class="rec-header">
                <h4>{{ rec.course_name }}</h4>
                <span class="match-score">匹配度: {{ (rec.match_score * 100).toFixed(0) }}%</span>
              </div>
              <p class="rec-reason">{{ rec.reason }}</p>
              <div class="rec-meta">
                <span class="difficulty-badge" :class="getDifficultyClass(rec.difficulty_match)">
                  {{ rec.difficulty_match }}
                </span>
                <span v-if="!rec.prerequisites_met" class="warning">
                  需要先修 {{ rec.missing_prerequisites.length }} 门课程
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import KnowledgeRadar from '../components/KnowledgeRadar.vue'
import LearningPathTimeline from '../components/LearningPathTimeline.vue'

export default {
  name: 'StudentDashboard',
  components: {
    KnowledgeRadar,
    LearningPathTimeline
  },
  setup() {
    const API_BASE_URL = 'http://localhost:8000'

    // 数据状态
    const courseScores = ref({})
    const knowledgeStateData = ref(null)
    const learningPath = ref([])
    const recommendations = ref([])
    const availableCourses = ref([])
    const targetCourseId = ref('')

    // 加载状态
    const isAnalyzing = ref(false)
    const isGeneratingPath = ref(false)

    // 示例课程列表（用于成绩输入）
    const sampleCourses = [
      { name: '高等数学', defaultScore: 85 },
      { name: '线性代数', defaultScore: 78 },
      { name: '概率论与数理统计', defaultScore: 82 },
      { name: '程序设计原理与C语言', defaultScore: 90 },
      { name: '数据结构', defaultScore: 88 },
      { name: '离散数学', defaultScore: 75 },
      { name: '计算机组成与实践', defaultScore: 80 },
      { name: '操作系统', defaultScore: 85 }
    ]

    // 初始化示例成绩
    sampleCourses.forEach(course => {
      courseScores.value[course.name] = course.defaultScore
    })

    // 加载可用课程列表
    const loadAvailableCourses = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/courses/`)
        availableCourses.value = response.data
      } catch (error) {
        console.error('Failed to load courses:', error)
        // 使用本地数据作为备份
        availableCourses.value = [
          { id: 36, label: '人工智能', difficulty: '较难' },
          { id: 14, label: '模式识别与机器学习', difficulty: '较难' },
          { id: 62, label: '深度学习基础与导论', difficulty: '较难' },
          { id: 55, label: '大数据系统', difficulty: '较难' }
        ]
      }
    }

    // 分析知识状态
    const analyzeKnowledge = async () => {
      isAnalyzing.value = true
      try {
        const response = await axios.post(`${API_BASE_URL}/api/knowledge/state`, {
          student_id: 'demo_student',
          course_scores: courseScores.value
        })
        knowledgeStateData.value = response.data

        // 自动获取推荐
        if (response.data.knowledge_vector) {
          await getRecommendations(response.data.knowledge_vector)
        }
      } catch (error) {
        console.error('Failed to analyze knowledge:', error)
        // 使用模拟数据
        knowledgeStateData.value = {
          knowledge_vector: {
            '数学基础': 0.75,
            '编程基础': 0.85,
            '算法基础': 0.78,
            '计算机系统': 0.72,
            '人工智能': 0.45
          },
          overall_level: 0.71,
          strengths: ['编程基础', '算法基础'],
          weaknesses: ['人工智能']
        }
      } finally {
        isAnalyzing.value = false
      }
    }

    // 获取推荐课程
    const getRecommendations = async (knowledgeVector) => {
      try {
        const completedCourses = Object.keys(courseScores.value)
          .filter(name => courseScores.value[name] >= 60)
          .map(name => {
            // 简化映射，实际应该从完整课程列表中查找
            const courseMap = {
              '高等数学': 1,
              '线性代数': 39,
              '概率论与数理统计': 33,
              '程序设计原理与C语言': 30,
              '数据结构': 37,
              '离散数学': 35,
              '计算机组成与实践': 53,
              '操作系统': 40
            }
            return courseMap[name]
          })
          .filter(id => id !== undefined)

        const response = await axios.post(`${API_BASE_URL}/api/knowledge/recommend`, {
          student_id: 'demo_student',
          knowledge_state: knowledgeVector,
          completed_courses: completedCourses,
          max_recommendations: 6
        })
        recommendations.value = response.data.recommendations
      } catch (error) {
        console.error('Failed to get recommendations:', error)
      }
    }

    // 生成学习路径
    const generatePath = async () => {
      if (!targetCourseId.value) return

      isGeneratingPath.value = true
      try {
        const completedCourses = Object.keys(courseScores.value)
          .filter(name => courseScores.value[name] >= 60)
          .map(name => {
            const courseMap = {
              '高等数学': 1,
              '线性代数': 39,
              '概率论与数理统计': 33,
              '程序设计原理与C语言': 30,
              '数据结构': 37,
              '离散数学': 35,
              '计算机组成与实践': 53,
              '操作系统': 40
            }
            return courseMap[name]
          })
          .filter(id => id !== undefined)

        const response = await axios.post(`${API_BASE_URL}/api/courses/learning-path`, {
          target_course_id: parseInt(targetCourseId.value),
          completed_courses: completedCourses,
          knowledge_state: knowledgeStateData.value?.knowledge_vector
        })
        learningPath.value = response.data.course_details
      } catch (error) {
        console.error('Failed to generate path:', error)
      } finally {
        isGeneratingPath.value = false
      }
    }

    // 课程选中回调
    const onCourseSelected = (course) => {
      console.log('Selected course:', course)
    }

    // 导出学习路径
    const exportLearningPath = (path) => {
      const data = JSON.stringify(path, null, 2)
      const blob = new Blob([data], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'learning-path.json'
      a.click()
      URL.revokeObjectURL(url)
    }

    // 调整学习路径
    const adjustLearningPath = () => {
      console.log('Adjust learning path')
      // TODO: 实现路径调整逻辑
    }

    // 难度等级样式
    const getDifficultyClass = (difficulty) => {
      const map = {
        '简单': 'easy',
        '中等': 'medium',
        '较难': 'hard',
        '困难': 'very-hard'
      }
      return map[difficulty] || 'medium'
    }

    onMounted(() => {
      loadAvailableCourses()
    })

    return {
      courseScores,
      knowledgeStateData,
      learningPath,
      recommendations,
      availableCourses,
      targetCourseId,
      isAnalyzing,
      isGeneratingPath,
      sampleCourses,
      analyzeKnowledge,
      generatePath,
      onCourseSelected,
      exportLearningPath,
      adjustLearningPath,
      getDifficultyClass
    }
  }
}
</script>

<style scoped>
.student-dashboard {
  min-height: 100vh;
  background: linear-gradient(to bottom, #1a1a2e 0%, #16213e 100%);
  padding: 40px 20px;
}

.dashboard-header {
  text-align: center;
  color: white;
  margin-bottom: 50px;
}

.dashboard-header h1 {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-subtitle {
  font-size: 16px;
  opacity: 0.8;
}

.dashboard-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.input-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.section-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 30px;
  backdrop-filter: blur(10px);
  color: white;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
}

.score-input-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.score-input-item label {
  display: block;
  font-size: 14px;
  margin-bottom: 6px;
  opacity: 0.9;
}

.score-input {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;
  transition: all 0.3s ease;
}

.score-input:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.15);
}

.course-select {
  width: 100%;
  padding: 12px 14px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;
  margin-bottom: 16px;
  cursor: pointer;
}

.course-select option {
  background: #1a1a2e;
  color: white;
}

.btn {
  width: 100%;
  padding: 14px 24px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.visualization-section {
  animation: fadeIn 0.6s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.recommendations-section {
  animation: fadeIn 0.6s ease;
}

.recommendation-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.recommendation-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
  cursor: pointer;
}

.recommendation-card:hover {
  transform: translateY(-4px);
  border-color: #667eea;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.recommendation-card.prerequisites-met {
  border-left: 4px solid #4ade80;
}

.rec-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 12px;
}

.rec-header h4 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.match-score {
  font-size: 12px;
  font-weight: 600;
  color: #4ade80;
}

.rec-reason {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 12px;
  line-height: 1.6;
}

.rec-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.difficulty-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.difficulty-badge.easy {
  background: #4ade80;
  color: #064e3b;
}

.difficulty-badge.medium {
  background: #fbbf24;
  color: #78350f;
}

.difficulty-badge.hard {
  background: #f97316;
  color: #7c2d12;
}

.difficulty-badge.very-hard {
  background: #ef4444;
  color: #7f1d1d;
}

.warning {
  font-size: 12px;
  color: #fbbf24;
}

@media (max-width: 1024px) {
  .input-section {
    grid-template-columns: 1fr;
  }

  .score-input-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>
