<template>
  <header class="header">
    <!-- 左侧 Logo 和标题 -->
    <div class="left-section">
      <img src="@/assets/pics/logo.png" alt="Logo" class="logo">
      <h1 class="title">智能导学</h1>
    </div>

    <!-- 右侧 5 个带图片的圆形按钮 -->
    <div class="right-section">
      <button class="circle-btn" @click="toggleTheme">
        <img src="@/assets/pics/lightness.png" alt="Icon 4" style="width: 33px; height: 33px; object-fit: cover;">
      </button>
      <button class="circle-btn">
        <img src="@/assets/pics/search.png" alt="Icon 1">
      </button>
      <button class="circle-btn">
        <img src="@/assets/pics/translate.png" alt="Icon 2" style="width: 33px; height: 33px; object-fit: cover;">
      </button>
      <button class="circle-btn">
        <img src="@/assets/pics/homepage.png" alt="Icon 3" style="width: 33px; height: 33px; object-fit: cover;">
      </button>
      <button class="circle-btn">
        <img src="@/assets/pics/dog.jpg" alt="Icon 5" style="width: 50px; height: 50px; object-fit: cover;">
      </button>
    </div>
  </header>
</template>

<script>
export default {
  name: 'NavBar',
  methods: {
    // 触发父组件切换主题的方法
    toggleTheme() {
      this.$emit('toggle-theme');
    }
  }
}
</script>

<style scoped>
/* 顶部导航栏 */
.header {
  width: 100vw;
  height: 70px;
  background-color: #f8f8f8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid #e0e0e0;
}

.left-section {
  display: flex;
  align-items: center;
}

.logo {
  width: 40px;
  height: 40px;
  margin-right: 1rem;
}

.title {
  color: #333;
  font-size: 2rem;
  font-weight: 600;
  font-family: 'Helvetica Neue', sans-serif;
}

/* 右侧按钮区域 */
.right-section {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  align-items: center;
  margin-right: 70px;
}

.circle-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #ffffff;
  border: 1px solid #dcdcdc;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  padding: 0;
  flex-shrink: 0;
}

.circle-btn img {
  width: 80%;
  height: 80%;
  object-fit: contain;
}

.circle-btn:hover {
  background-color: #f5f5f5;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* 深色主题样式 */
.dark-mode {
  background-color: #121212;  /* 深色背景 */
  color: #ffffff;  /* 白色文字 */
}

/* 响应式调整：小屏幕下的按钮大小 */
@media (max-width: 768px) {
  .title {
    font-size: 1.6rem;
  }
  .circle-btn {
    width: 45px;
    height: 45px;
  }
  .circle-btn img {
    width: 70%;
    height: 70%;
  }
}
</style>
