<template>
  <div class="offset-top container">
    <button type="button" class="btn btn-block btn-success" @click="updateStore()">
      Test Validating AnnotateAndSegment route
    </button>
    <nodule-list annotate="true"></nodule-list>
  </div>
</template>

<script>
import NoduleList from '../components/annotate-and-segment/NoduleList'

import Store from '../store'

export default {
  name: 'annotate-and-segment',
  components: {
    NoduleList
  },
  methods: {
    updateStore () {
      // Using a true boolean for now, but it can be anything
      Store.setRouteResult(this.$route.path, true)
    }
  }
}
</script>
