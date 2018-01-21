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
      const savedArea = this.selectedNodule.selected_area
      const currentArea = savedArea || new Array(this.$store.getters.imagePaths.length)

      if (!savedArea) {
        const centroid = this.selectedNodule.candidate.centroid
        const x = centroid.x
        const y = centroid.y

        // by default creating an area around current centroid
        // but actually it should be predicted by backend
        currentArea[centroid.z] = [
          [x - 10, y - 10],
          [x - 10, y + 10],
          [x + 10, y + 10],
          [x + 10, y - 10]
        ]
      }

      // create a new detached object, user has to click Apply to save changes
      return JSON.parse(JSON.stringify(currentArea))
    },
    viewerData () {
      // preselect first slice with selected area
      let firstSliceWithArea = 0

      for (let [i, sliceArea] of this.areaCoordinates.entries()) {
        if (sliceArea && sliceArea.length) {
          firstSliceWithArea = i
          break
        }
      }

      return {
        type: 'DICOM',
        prefixCS: ':/',
        prefixUrl: '/api/images/preview?dicom_location=',
        paths: this.$store.getters.imagePaths,
        sliceIndex: firstSliceWithArea
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
