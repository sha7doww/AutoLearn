<template>
  <div class="learning-path-timeline">
    <div class="timeline-header">
      <h2>学习路径规划</h2>
      <p class="subtitle">根据您的学习目标智能生成个性化课程序列</p>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在生成学习路径...</p>
    </div>

    <div v-else-if="!path || path.length === 0" class="empty-state">
      <p>暂无学习路径数据</p>
      <p class="hint">请先选择目标课程或输入成绩数据</p>
    </div>

    <div v-else class="timeline-container">
      <div class="timeline-summary">
        <div class="summary-item">
          <span class="label">总课程数:</span>
          <span class="value">{{ path.length }}</span>
        </div>
        <div class="summary-item">
          <span class="label">总学分:</span>
          <span class="value">{{ totalCredits }}</span>
        </div>
        <div class="summary-item">
          <span class="label">预计学期:</span>
          <span class="value">{{ estimatedSemesters }}</span>
        </div>
      </div>

      <div class="timeline">
        <div
          v-for="(course, index) in path"
          :key="course.id"
          class="timeline-item"
          :class="{ 'completed': course.completed, 'current': index === currentIndex }"
          @click="selectCourse(course, index)"
        >
          <div class="timeline-marker">
            <div class="marker-dot"></div>
            <div v-if="index < path.length - 1" class="marker-line"></div>
          </div>

          <div class="timeline-content">
            <div class="course-header">
              <div class="course-number">第 {{ index + 1 }} 门</div>
              <div class="course-status">
                <span v-if="course.completed" class="badge completed">已完成</span>
                <span v-else-if="index === currentIndex" class="badge current">进行中</span>
                <span v-else class="badge pending">待学习</span>
              </div>
            </div>

            <div class="course-title">{{ course.label }}</div>

            <div class="course-meta">
              <span class="meta-item">
                <i class="icon-difficulty"></i>
                难度: {{ course.difficulty || '中等' }}
              </span>
              <span class="meta-item">
                <i class="icon-credit"></i>
                学分: {{ course.credits || 3 }}
              </span>
              <span class="meta-item">
                <i class="icon-type"></i>
                {{ course.course_type || '必修' }}
              </span>
            </div>

            <div v-if="course.prerequisites && course.prerequisites.length > 0" class="prerequisites">
              <span class="prereq-label">先修课程:</span>
              <span class="prereq-list">
                {{ getPrerequisiteNames(course.prerequisites).join(', ') }}
              </span>
            </div>

            <div v-if="course.reason" class="recommendation-reason">
              <i class="icon-info"></i>
              {{ course.reason }}
            </div>
          </div>
        </div>
      </div>

      <div class="timeline-actions">
        <button @click="exportPath" class="btn btn-primary">导出学习计划</button>
        <button @click="adjustPath" class="btn btn-secondary">调整路径</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'LearningPathTimeline',
  props: {
    path: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['course-selected', 'export-path', 'adjust-path'],
  setup(props, { emit }) {
    const currentIndex = ref(0)

    const totalCredits = computed(() => {
      return props.path.reduce((sum, course) => sum + (course.credits || 3), 0)
    })

    const estimatedSemesters = computed(() => {
      return Math.ceil(totalCredits.value / 20)
    })

    const selectCourse = (course, index) => {
      currentIndex.value = index
      emit('course-selected', course)
    }

    const getPrerequisiteNames = (prerequisiteIds) => {
      // This should fetch actual course names from the full course list
      // For now, return IDs
      return prerequisiteIds.map(id => `课程${id}`)
    }

    const exportPath = () => {
      emit('export-path', props.path)
    }

    const adjustPath = () => {
      emit('adjust-path')
    }

    return {
      currentIndex,
      totalCredits,
      estimatedSemesters,
      selectCourse,
      getPrerequisiteNames,
      exportPath,
      adjustPath
    }
  }
}
</script>

<style scoped>
.learning-path-timeline {
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
}

.timeline-header {
  text-align: center;
  margin-bottom: 30px;
}

.timeline-header h2 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  opacity: 0.9;
}

.loading-container {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  opacity: 0.8;
}

.hint {
  font-size: 14px;
  margin-top: 10px;
  opacity: 0.7;
}

.timeline-summary {
  display: flex;
  justify-content: space-around;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  backdrop-filter: blur(10px);
}

.summary-item {
  text-align: center;
}

.summary-item .label {
  display: block;
  font-size: 14px;
  opacity: 0.8;
  margin-bottom: 8px;
}

.summary-item .value {
  display: block;
  font-size: 24px;
  font-weight: 600;
}

.timeline {
  max-height: 600px;
  overflow-y: auto;
  padding: 20px 0;
}

.timeline-item {
  display: flex;
  margin-bottom: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.timeline-item:hover {
  transform: translateX(5px);
}

.timeline-item.current .timeline-content {
  background: rgba(255, 255, 255, 0.25);
  border-left: 4px solid #4ade80;
}

.timeline-item.completed .marker-dot {
  background: #4ade80;
}

.timeline-marker {
  position: relative;
  margin-right: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.marker-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  border: 3px solid white;
  z-index: 2;
  transition: all 0.3s ease;
}

.timeline-item:hover .marker-dot {
  transform: scale(1.3);
}

.marker-line {
  width: 2px;
  flex: 1;
  background: rgba(255, 255, 255, 0.3);
  margin-top: 4px;
  min-height: 40px;
}

.timeline-content {
  flex: 1;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 20px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.course-number {
  font-size: 12px;
  opacity: 0.8;
  font-weight: 500;
}

.badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.badge.completed {
  background: #4ade80;
  color: #064e3b;
}

.badge.current {
  background: #fbbf24;
  color: #78350f;
}

.badge.pending {
  background: rgba(255, 255, 255, 0.3);
  color: white;
}

.course-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
}

.course-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 13px;
  opacity: 0.9;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.prerequisites {
  font-size: 13px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.prereq-label {
  font-weight: 500;
  margin-right: 8px;
}

.prereq-list {
  opacity: 0.9;
}

.recommendation-reason {
  margin-top: 12px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  font-size: 13px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.timeline-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 30px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: white;
  color: #667eea;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid white;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Scrollbar styling */
.timeline::-webkit-scrollbar {
  width: 8px;
}

.timeline::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.timeline::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.timeline::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>
