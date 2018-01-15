<template>
  <div class="annotate-container">
    <a @click="update(nodule)">
      <button type="button" class="btn btn-block btn-success">Accept</button>
    </a>
    <hr/>

    <concern-slider v-model="concerning" :predictedValue="(nodule.candidate.probability_concerning * 100).toFixed(1)"></concern-slider>

    <hr/>

    <div class="lung-select-container">
      <form>
        <radio-input v-model="lungOrientation" name="lung" :value="lungOrientationEnum.LEFT" label="Left lung"></radio-input>
        <radio-input v-model="lungOrientation" name="lung" :value="lungOrientationEnum.RIGHT" label="Right lung"></radio-input>
      </form>
    </div>

    <hr>

    <div class="density-radio-container">
      <form>
        <radio-input v-model="density" name="density" :value="densityEnum.SOLID" label="Solid"></radio-input>
        <radio-input v-model="density" name="density" :value="densityEnum.SEMI_SOLID" label="Semi-solid"></radio-input>
        <radio-input v-model="density" name="density" :value="densityEnum.GROUND_GLASS" label="Ground glass"></radio-input>
      </form>
    </div>

    <hr>

    <div class="severity-radio-container">
      <form>
        <radio-input v-model="sizeChange" name="sizeChange" :value="sizeChangeEnum.UNCHANGED" label="Unchanged"></radio-input>
        <radio-input v-model="sizeChange" name="sizeChange" :value="sizeChangeEnum.INCREASED" label="Increased"></radio-input>
        <radio-input v-model="sizeChange" name="sizeChange" :value="sizeChangeEnum.DECREASED" label="Decreased"></radio-input>
        <radio-input v-model="sizeChange" name="sizeChange" :value="sizeChangeEnum.NEW" label="New"></radio-input>
      </form>
    </div>

    <hr>

    <div class="note-container">
      <textarea class="form-control" v-model="note" rows="3" style="width:100%;" placeholder="Add notes">
      </textarea>
    </div>

  </div>
</template>

<script>
import RadioInput from './RadioInput'

import ConcernSlider from './ConcernSlider'

export default {
  components: { RadioInput, ConcernSlider },
  props: ['nodule', 'index'],
  data () {
    const probabilityConcerning = this.nodule.probability_concerning || this.nodule.candidate.probability_concerning

    return {
      lungOrientationEnum: this.$constants.LUNG_ORIENTATION,
      densityEnum: this.$constants.DENSITY,
      sizeChangeEnum: this.$constants.SIZE_CHANGE,
      density: this.nodule.density_feature,
      sizeChange: this.nodule.size_change,
      lungOrientation: this.nodule.lung_orientation,
      concerning: Math.round(probabilityConcerning * 100),
      note: this.nodule.note
    }
  },
  created () {
    // console.log(this.nodule)
  },
  methods: {
    update (nodule) {
      this.$store.dispatch('updateNodule', {
        url: nodule.url,
        lung_orientation: this.lungOrientation,
        probability_concerning: this.concerning * 0.01,
        size_change: this.sizeChange,
        density_feature: this.density,
        note: this.note
      })
      .then((response) => {
        console.log(response)
      }, console.error)
    }
  }
}
</script>

<style scoped>

</style>
