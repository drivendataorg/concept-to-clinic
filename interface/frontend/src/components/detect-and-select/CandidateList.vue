<template>
<div class="container">
  <div class="row">
    <div class="col-md-4">
      <template v-if="candidates.length">
        <div id="accordion">
        <template v-for="(candidate, index) in candidates">
          <candidate :candidate="candidate" :index="index" :key="index"></candidate>
        </template>
      </div>
      </template>
      <template v-else>
        <p class="card-text">No candidates available.</p>
      </template>
    </div>
    <div class="col-md-8"></div>
  </div>
</div>
</template>

<script>
import Candidate from './Candidate'

export default {
  components: { Candidate },
  data () {
    return {
      candidates: []
    }
  },
  created () {
    this.fetchCandidates()
  },
  methods: {
    fetchCandidates () {
      this.$axios.get('/api/candidates/')
        .then((response) => {
          this.candidates = response.data
        })
        .catch(() => {
          // TODO: error callback
        })
    }
  }
}
</script>
