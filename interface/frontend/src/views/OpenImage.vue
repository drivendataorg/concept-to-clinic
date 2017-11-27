<template>
  <div class="container">
    <div class="row">
      <div class="col-md-12">
        <image-series v-on:series-selected='updateStore'></image-series>
      </div>
    </div>
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
