<template>
  <div class="container">
    <button id="openimage-mock" type="button" class="btn btn-block btn-success" @click="updateStore()">
      Test Validating Open Image route (/)
    </button>
    <image-series v-on:series-selected='updateStore'></image-series>
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
