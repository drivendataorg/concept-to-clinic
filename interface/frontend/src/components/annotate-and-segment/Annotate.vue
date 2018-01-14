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
        <radio-input v-model="lungOrientation" name="lung" :value="LUNG_ORIENTATION.LEFT" label="Left lung"></radio-input>
        <radio-input v-model="lungOrientation" name="lung" :value="LUNG_ORIENTATION.RIGHT" label="Right lung"></radio-input>
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
        <radio-input v-model="condition" name="condition" value="unchanged" label="Unchanged"></radio-input>
        <radio-input v-model="condition" name="condition" value="increased" label="Increased"></radio-input>
        <radio-input v-model="condition" name="condition" value="decreased" label="Decreased"></radio-input>
        <radio-input v-model="condition" name="condition" value="new" label="New"></radio-input>
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
    return {
      LUNG_ORIENTATION: this.$constants.LUNG_ORIENTATION,
      densityEnum: this.$constants.DENSITY,
      density: this.nodule.density_feature,
      condition: 'unchanged',
      lungOrientation: this.nodule.lung_orientation,
      concerning: 50,
      note: ''
    }
  },
  created () {
    // console.log(this.nodule)
  },
  methods: {
    update (nodule) {
      this.$axios.patch(nodule.url, {
        lung_orientation: this.lungOrientation,
        concerning: this.concerning,
        condition: this.condition,
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
