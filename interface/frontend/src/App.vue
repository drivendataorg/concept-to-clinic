<template>
<div id="app">
  <app-nav></app-nav>
  <image-series></image-series>
</div>
</template>

<script>
import AppNav from './components/AppNav'
import ImageSeries from './components/ImageSeries'

export default {
  components: {
    AppNav, ImageSeries
  }
}
</script>

<style scoped>
.container {
  margin-top: 72px;
}
</style>
