<template>
  <div class="login-page">
    <!-- 粒子背景 -->
    <div id="particles-js"></div>

    <!-- 登录表单 -->
    <div class="login-form-wrapper">
      <el-form :model="loginRuleForm" :rules="loginRules" ref="loginRules" label-width="0px" class="login-form">
        <!-- 项目名字标题 -->
        <h2 class="login-title">智能导学</h2>
        <el-form-item prop="username">
          <el-input v-model="loginRuleForm.username" placeholder="请输入您的账号" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginRuleForm.password" type="password" placeholder="请输入您的密码" @keyup.enter="login" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="rememberMe">我同意「智能导学用户使用协议」</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="login" :loading="loading">登录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
// eslint-disable-next-line
/* global particlesJS */
import "particles.js";

export default {
  name: 'LoginView',
  data() {
    return {
      loading: false,
      rememberMe: false,
      loginRuleForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [
          { required: true, message: "请输入用户名", trigger: "blur" },
          { min: 3, max: 18, message: "长度在 3 到 18 个字符", trigger: "blur" }
        ],
        password: [
          { required: true, message: "请输入密码", trigger: "blur" },
          { min: 3, max: 18, message: "长度在 3 到 18 个字符", trigger: "blur" }
        ]
      }
    }
  },
  mounted() {
    this.initParticles();
    document.title = "智能导学 - 登录"; // 页签标题也改
  },
  methods: {
    initParticles() {
      particlesJS('particles-js', {
        "particles": {
          "number": {
            "value": 80,
            "density": {
              "enable": true,
              "value_area": 800
            }
          },
          "color": { "value": "#ffffff" },
          "shape": {
            "type": "circle",
            "stroke": { "width": 0, "color": "#000000" },
          },
          "opacity": {
            "value": 0.5,
            "random": true,
          },
          "size": {
            "value": 3,
            "random": true,
          },
          "move": {
            "enable": true,
            "speed": 2,
            "direction": "none",
            "random": false,
            "straight": false,
            "out_mode": "out",
          }
        },
        "interactivity": {
          "detect_on": "canvas",
          "events": {
            "onhover": {
              "enable": true,
              "mode": "repulse"
            },
            "onclick": {
              "enable": true,
              "mode": "push"
            }
          },
          "modes": {
            "repulse": {
              "distance": 100,
              "duration": 0.4
            },
            "push": {
              "particles_nb": 4
            }
          }
        },
        "retina_detect": true
      });
    },
    login() {
      if (!this.rememberMe) {
        this.$message({
          message: '请先同意【智能导学用户使用协议】',
          type: "warning"
        });
        return;
      }
      this.$refs.loginRules.validate(valid => {
        if (valid) {
          this.loading = true;
          setTimeout(() => {
            this.loading = false;
            this.$router.push({ name: 'Home' });
          }, 1000);
        } else {
          console.log('error submit!');
          return false;
        }
      });
    }
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #74ebd5 0%, #acb6e5 100%);
  overflow: hidden;
}

/* 粒子背景容器 */
#particles-js {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 0;
}

/* 登录表单容器 */
.login-form-wrapper {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

/* 表单本体 */
.login-form {
  background: rgba(255, 255, 255, 0.9);
  padding: 40px 30px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  width: 320px;
}

/* 项目名字标题 */
.login-title {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  color: #333;
}

.login-form .el-form-item {
  margin-bottom: 20px;
}

.login-form .el-button {
  width: 100%;
}
</style>
