<template>
  <div class="container">
    <button type="button" class="btn btn-block btn-success" @click="updateStore()">
      Test Validating Open Image route (/)
    </button>
    <image-series></image-series>
  </div>
</template>

<script>
import ImageSeries from '../components/open-image/ImageSeries'

import Store from '../store'

export default {
  name: 'open-image',
  components: {
    ImageSeries
  },
  methods: {
    updateStore () {
      Store.setRouteResult('/', true)
    }
  }
}
</script>

<style lang="scss" scoped>
</style>
