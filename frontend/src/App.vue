<template>
  <div id="app">
    <router-view></router-view> <!-- 这里会显示匹配到的组件 -->
  </div>
</template>

<script>
export default {
  name: 'App'
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  /* Removed global color - let components control their own text colors */
  height: 100%;
  width: 100%;
}
</style>