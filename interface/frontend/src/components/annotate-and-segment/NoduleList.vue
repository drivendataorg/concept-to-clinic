<template>
<div class='container'>
  <div class='row'>
    <div class='col-md-4'>
      <div v-if="nodules.length">
        <div id="accordion" role="tablist" aria-multiselectable="true">
          <template v-for="(nodule, index) in nodules">
            <nodule :nodule="nodule" :index="index">
              <annotate v-if="annotate" :nodule="nodule" :index="index" slot="add-on-editor">
              </annotate>
            </nodule>
          </template>
        </div>
      </div>
      <div v-else>
        <p class="card-text">No nodules available.</p>
      </div>
    </div><!-- left side-->
    <div class='col-md-8'></div><!-- right side-->
  </div>
</div>
</template>

<script>
import Nodule from './Nodule'
import Annotate from './Annotate'

export default {
  props: ['annotate'],
  components: { Nodule, Annotate },
  data () {
    return {
      nodules: []
    }
  },
  created () {
    this.fetchNodules()
  },
  methods: {
    fetchNodules () {
      this.$axios.get('/api/nodules.json')
        .then((response) => {
          this.nodules = response.data
        })
        .catch(() => {
          // TODO: error callback
        })
    }
  }
}
</script>
