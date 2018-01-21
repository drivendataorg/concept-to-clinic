<template>
<div class='container'>
  <div class='row'>
    <div class='col-md-4'>
      <div v-if="nodules && nodules.length">
        <div id="accordion" role="tablist" aria-multiselectable="true">
          <template v-for="(nodule, index) in nodules">
            <nodule :nodule="nodule"
                    :index="index"
                    :selectedIndex="selectedIndex"
                    v-on:selected="selected"
                    :key="index">
              <annotate v-if="annotate" :nodule="nodule" :areaCoordinates="areaCoordinates" 
                        :index="index" slot="add-on-editor">
              </annotate>
            </nodule>
          </template>
        </div>
      </div>
      <div v-else>
        <p class="card-text">No nodules available.</p>
      </div>
    </div><!-- left side-->
    <div class='col-md-8'>
      <open-dicom :view="viewerData" :showAreaSelect="true" :areaCoordinates="areaCoordinates"></open-dicom>
    </div><!-- right side-->
  </div>
</div>
</template>

<script>
import Nodule from './Nodule'
import Annotate from './Annotate'
import OpenDicom from '../common/OpenDICOM'

export default {
  props: ['annotate'],
  components: { Nodule, Annotate, OpenDicom },
  data () {
    return {
      selectedIndex: 0
    }
  },
  computed: {
    nodules () {
      return this.$store.getters.nodules
    },
    selectedNodule () {
      return this.nodules[this.selectedIndex]
    },
    areaCoordinates () {
      // needs to be implemented, for now draw a 40 x 40 square at the centroid
      var x = this.selectedNodule.candidate.centroid.x
      var y = this.selectedNodule.candidate.centroid.y

      return [
        [x - 10, y - 10],
        [x - 10, y + 10],
        [x + 10, y + 10],
        [x + 10, y - 10]
      ]
    },
    viewerData () {
      return {
        type: 'DICOM',
        prefixCS: ':/',
        prefixUrl: '/api/images/preview?dicom_location=',
        paths: this.$store.getters.imagePaths,
        sliceIndex: this.nodules[this.selectedIndex].candidate.centroid.z || 0
      }
    }
  },
  methods: {
    selected (ix) {
      this.selectedIndex = ix
    }
  }
}
</script>
