<template>
<div id="app">
  <app-nav></app-nav>
  <router-view></router-view>
</div>
</template>

<script>
import AppNav from './components/AppNav'

export default {
  components: {
    AppNav
  }
}
</script>

<style scoped>
.container {
  margin-top: 72px;
}
</style>
