<template>
  <div id="app">
    <NavBar />
    <div class="main-container">
      <div class="content-container">
        <div class="content">
          <div class="course-info">
            <div class="course-image-container">
              <img :src="courseImage" alt="Course Image" class="course-image" />
            </div>
            <div class="course-details-container">
              <div class="course-details-content">
                <h1 class="course-title">概率论与数理统计</h1>
                <div class="course-details">
                  <div class="detail-group">
                    <div class="detail"><strong>开课老师:</strong> 赵静</div>
                    <div class="detail"><strong>课程性质:</strong> 学科必修</div>
                  </div>
                  <div class="detail-group">
                    <div class="detail"><strong>先修课程:</strong> 数学分析</div>
                    <div class="detail"><strong>学时/学分:</strong> 54/3</div>
                  </div>
                </div>
                <div class="learning-advices">
                  <span>1. 夯实数学基础：确保先修课程中的数学知识扎实，特别是微积分和线性代数，这对理解概率论和数理统计中的概念和计算非常重要。<br>2. 系统学习基本概念：注重理解每个章节的基本概念和原理，确保对随机事件、概率、一维和多维随机变量、参数估计和假设检验等基础知识有全面了解。<br>3. 多做习题：通过大量习题练习巩固所学知识，尤其是涉及概率计算、随机变量分布、参数估计和假设检验等内容的题目。<br>4. 积极参与课堂讨论：通过课堂讨论和提问，深化对课程内容的理解，与同学和老师交流学习经验和难点问题。<br>5. 理论结合实际：尝试将所学理论知识应用于实际问题的解决，通过案例分析和项目实践来验证和巩固所学知识。<br>6. 参考多种教材：除了推荐教材外，广泛阅读其他相关书籍和文献，拓展知识面，增强理解深度。<br>7. 定期复习总结：每周复习课程内容，整理笔记和习题答案，形成系统的知识框架，为考试做好充分准备。<br>8. 注重应用：了解概率论与数理统计在社会、经济、生产中的应用实例，增强对理论知识的兴趣和理解。</span>
                </div>
              </div>
            </div>
          </div>
          <div class="course-outline">
            <h2>课程大纲内容</h2>
            <ol>
              <li>《概率论与数理统计》课程是一门研究随机现象及其统计规律性的基础课程。主要内容包括随机事件与概率、一维和多维随机变量、参数估计和假设检验等。课程旨在培养学生利用数学思想设计解决实际应用问题的能力，为后续需要概率论等数学知识的课程打下基础，并为从事算法等相关工作和研究的学生储备数学知识和锻炼数学思维。</li>
            </ol>
          </div>
        </div>
      </div>
      <SideBar />
    </div>
  </div>
</template>

<script>
import NavBar from '../components/NavBar.vue';
import SideBar from '../components/SideBar.vue';

export default {
  components: {
    NavBar,
    SideBar,
  },
  data() {
    return {
      courseImage: require('@/assets/STAT0031121004.png'),
    };
  },
};
</script>

<style scoped>
#app {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  background-color: #f5f5f5;
  color: #333;
}

.main-container {
  display: flex;
  padding-top: 80px;
  justify-content: center;
}

.content-container {
  width: 60%;
  background-color: #ffffff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-right: 200px;
}

.content {
  display: flex;
  flex-direction: column;
}

.course-info {
  display: flex;
  margin-bottom: 30px;
}

.course-image-container {
  width: 35%;
  margin-right: 20px;
}

.course-image {
  width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.course-details-container {
  width: 65%;
  display: flex;
  flex-direction: column;
}

.course-details-content {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.course-title {
  font-size: 26px;
  font-weight: 700;
  color: #333;
  margin-bottom: 20px;
}

.course-details {
  margin-bottom: 20px;
}

.detail-group {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.detail {
  flex: 1;
  font-size: 16px;
  color: #555;
}

.learning-advices {
  margin-top: 20px;
  font-size: 16px;
  line-height: 1.8;
  color: #555;
}

.course-outline {
  margin-top: 30px;
}

.course-outline h2 {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #333;
}

.course-outline ol {
  margin-left: 20px;
}

.course-outline li {
  font-size: 16px;
  color: #555;
  margin-bottom: 10px;
}

@media (max-width: 768px) {
  .main-container {
    padding-top: 70px;
    flex-direction: column;
    justify-content: flex-start;
  }

  .content-container {
    width: 90%;
    margin-right: 0;
  }

  .course-title {
    font-size: 22px;
  }

  .course-details-container {
    width: 100%;
  }

  .course-info {
    flex-direction: column;
    align-items: center;
  }

  .course-image-container {
    width: 80%;
    margin-right: 0;
    margin-bottom: 20px;
  }
}
</style>
