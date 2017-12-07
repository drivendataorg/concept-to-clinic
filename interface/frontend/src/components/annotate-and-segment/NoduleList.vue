<template>
<div class='container'>
  <div class='row'>
    <div class='col-md-4'>
      <div v-if="nodules && nodules.length">
        <div id="accordion" role="tablist" aria-multiselectable="true">
          <template v-for="(nodule, index) in nodules">
            <nodule :nodule="nodule" :index="index" :key="index">
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
    <div class='col-md-8'>
      <open-dicom :view="viewerData"></open-dicom>
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
  computed: {
    nodules () {
      return this.$store.getters.nodules
    },
    viewerData () {
      return {
        type: 'DICOM',
        prefixCS: ':/',
        prefixUrl: '/api/images/preview?dicom_location=',
        paths: this.$store.getters.imagePaths,
        sliceIndex: 0
      }
    }
  }
}
</script>
