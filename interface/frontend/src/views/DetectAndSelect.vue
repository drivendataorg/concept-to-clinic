<template>
  <div class="container">
    <button type="button" class="btn btn-block btn-success" @click="updateStore()">
      Test Validating DetectAndSelect route (/detect-and-select)
    </button>
    <candidate-list></candidate-list>
  </div>
</template>

<script>
import CandidateList from '../components/detect-and-select/CandidateList'

import Store from '../store'

export default {
  name: 'detect-and-select',
  components: {
    CandidateList
  },
  methods: {
    updateStore () {
      // Using a true boolean for now, but it can be anything
      Store.setRouteResult(this.$route.path, true)
    }
  }
}
</script>
