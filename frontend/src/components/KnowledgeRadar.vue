<template>
  <div class="knowledge-radar">
    <div class="radar-header">
      <h2>知识掌握度分析</h2>
      <p class="subtitle">基于IRT模型的知识状态评估</p>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在分析知识状态...</p>
    </div>

    <div v-else-if="!knowledgeState || Object.keys(knowledgeState).length === 0" class="empty-state">
      <p>暂无知识状态数据</p>
      <p class="hint">请先输入课程成绩进行分析</p>
    </div>

    <div v-else class="radar-content">
      <div class="overall-score">
        <div class="score-circle" :style="{ background: getScoreColor(overallLevel) }">
          <div class="score-value">{{ (overallLevel * 100).toFixed(0) }}</div>
          <div class="score-label">综合水平</div>
        </div>
      </div>

      <div ref="radarChart" class="radar-chart"></div>

      <div class="knowledge-details">
        <div class="details-section">
          <h3 class="section-title">
            <span class="icon">💪</span>
            优势领域
          </h3>
          <div v-if="strengths.length > 0" class="tag-list">
            <span v-for="strength in strengths" :key="strength" class="tag strength-tag">
              {{ strength }}
            </span>
          </div>
          <p v-else class="empty-message">暂无明显优势</p>
        </div>

        <div class="details-section">
          <h3 class="section-title">
            <span class="icon">📚</span>
            薄弱环节
          </h3>
          <div v-if="weaknesses.length > 0" class="tag-list">
            <span v-for="weakness in weaknesses" :key="weakness" class="tag weakness-tag">
              {{ weakness }}
            </span>
          </div>
          <p v-else class="empty-message">无明显薄弱环节</p>
        </div>
      </div>

      <div class="knowledge-list">
        <h3>详细分析</h3>
        <div v-for="(value, domain) in sortedKnowledgeState" :key="domain" class="knowledge-item">
          <div class="knowledge-name">{{ domain }}</div>
          <div class="knowledge-bar">
            <div
              class="knowledge-progress"
              :style="{
                width: (value * 100) + '%',
                background: getProgressColor(value)
              }"
            ></div>
          </div>
          <div class="knowledge-value">{{ (value * 100).toFixed(0) }}%</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue'

export default {
  name: 'KnowledgeRadar',
  props: {
    knowledgeState: {
      type: Object,
      default: () => ({})
    },
    overallLevel: {
      type: Number,
      default: 0
    },
    strengths: {
      type: Array,
      default: () => []
    },
    weaknesses: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const radarChart = ref(null)
    let chartInstance = null

    const sortedKnowledgeState = computed(() => {
      const entries = Object.entries(props.knowledgeState)
      entries.sort((a, b) => b[1] - a[1])
      return Object.fromEntries(entries)
    })

    const getScoreColor = (score) => {
      if (score >= 0.8) return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      if (score >= 0.6) return 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
      if (score >= 0.4) return 'linear-gradient(135deg, #fccb90 0%, #d57eeb 100%)'
      return 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)'
    }

    const getProgressColor = (value) => {
      if (value >= 0.7) return '#4ade80'
      if (value >= 0.4) return '#fbbf24'
      return '#f87171'
    }

    const loadECharts = () => {
      return new Promise((resolve, reject) => {
        if (window.echarts) {
          resolve(window.echarts)
          return
        }

        const script = document.createElement('script')
        script.src = 'https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js'
        script.onload = () => resolve(window.echarts)
        script.onerror = reject
        document.head.appendChild(script)
      })
    }

    const initRadarChart = async () => {
      if (!radarChart.value || Object.keys(props.knowledgeState).length === 0) return

      try {
        const echarts = await loadECharts()

        if (chartInstance) {
          chartInstance.dispose()
        }

        chartInstance = echarts.init(radarChart.value)

        const indicators = Object.keys(props.knowledgeState).map(domain => ({
          name: domain,
          max: 1
        }))

        const values = Object.values(props.knowledgeState)

        const option = {
          tooltip: {
            trigger: 'item',
            formatter: (params) => {
              const data = params.data.value
              let result = '<div style="padding: 10px;">'
              indicators.forEach((ind, idx) => {
                result += `${ind.name}: ${(data[idx] * 100).toFixed(0)}%<br/>`
              })
              result += '</div>'
              return result
            }
          },
          radar: {
            indicator: indicators,
            shape: 'polygon',
            splitNumber: 4,
            name: {
              textStyle: {
                color: '#fff',
                fontSize: 12
              }
            },
            splitLine: {
              lineStyle: {
                color: 'rgba(255, 255, 255, 0.2)'
              }
            },
            splitArea: {
              show: true,
              areaStyle: {
                color: [
                  'rgba(255, 255, 255, 0.05)',
                  'rgba(255, 255, 255, 0.1)'
                ]
              }
            },
            axisLine: {
              lineStyle: {
                color: 'rgba(255, 255, 255, 0.3)'
              }
            }
          },
          series: [
            {
              name: '知识掌握度',
              type: 'radar',
              data: [
                {
                  value: values,
                  name: '当前水平',
                  areaStyle: {
                    color: 'rgba(102, 126, 234, 0.4)'
                  },
                  lineStyle: {
                    color: '#667eea',
                    width: 2
                  },
                  itemStyle: {
                    color: '#667eea'
                  }
                }
              ]
            }
          ]
        }

        chartInstance.setOption(option)

        // Handle window resize
        const resizeHandler = () => {
          if (chartInstance) {
            chartInstance.resize()
          }
        }
        window.addEventListener('resize', resizeHandler)

      } catch (error) {
        console.error('Failed to load ECharts:', error)
      }
    }

    onMounted(() => {
      nextTick(() => {
        initRadarChart()
      })
    })

    watch(() => props.knowledgeState, () => {
      nextTick(() => {
        initRadarChart()
      })
    }, { deep: true })

    return {
      radarChart,
      sortedKnowledgeState,
      getScoreColor,
      getProgressColor
    }
  }
}
</script>

<style scoped>
.knowledge-radar {
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
}

.radar-header {
  text-align: center;
  margin-bottom: 30px;
}

.radar-header h2 {
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

.radar-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.overall-score {
  display: flex;
  justify-content: center;
}

.score-circle {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.score-value {
  font-size: 48px;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  font-size: 14px;
  margin-top: 8px;
  opacity: 0.9;
}

.radar-chart {
  width: 100%;
  height: 400px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.knowledge-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.details-section {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 20px;
  backdrop-filter: blur(10px);
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon {
  font-size: 20px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.strength-tag {
  background: #4ade80;
  color: #064e3b;
}

.weakness-tag {
  background: #f87171;
  color: #7f1d1d;
}

.empty-message {
  font-size: 14px;
  opacity: 0.7;
}

.knowledge-list {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 20px;
  backdrop-filter: blur(10px);
}

.knowledge-list h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
}

.knowledge-item {
  display: grid;
  grid-template-columns: 120px 1fr 60px;
  gap: 16px;
  align-items: center;
  margin-bottom: 16px;
}

.knowledge-item:last-child {
  margin-bottom: 0;
}

.knowledge-name {
  font-size: 14px;
  font-weight: 500;
}

.knowledge-bar {
  height: 24px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  overflow: hidden;
}

.knowledge-progress {
  height: 100%;
  border-radius: 12px;
  transition: width 0.6s ease;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
}

.knowledge-value {
  font-size: 14px;
  font-weight: 600;
  text-align: right;
}

@media (max-width: 768px) {
  .knowledge-details {
    grid-template-columns: 1fr;
  }

  .knowledge-item {
    grid-template-columns: 100px 1fr 50px;
    gap: 12px;
  }
}
</style>
