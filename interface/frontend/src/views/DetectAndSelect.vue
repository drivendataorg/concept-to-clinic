<template>
  <div class="container">
    <candidate-list></candidate-list>
  </div>
</template>

<script>
import CandidateList from '../components/detect-and-select/CandidateList'

export default {
  name: 'detect-and-select',
  components: {
    CandidateList
  }
}
</script>
