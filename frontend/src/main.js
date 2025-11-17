import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

// 导入 axios
import axios from 'axios';
import qs from 'qs';

// 创建 Vue 应用实例
const app = createApp(App);

// 使用路由
app.use(router);

// 使用 Element Plus
app.use(ElementPlus);

// 全局注册 axios 和 qs
app.config.globalProperties.$axios = axios;
app.config.globalProperties.qs = qs;

// 挂载应用
app.mount('#app');