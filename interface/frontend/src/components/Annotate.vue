<template>
  <div id="annotate">
    <a @click="update(nodule)">
      <button type="button" class="btn btn-block btn-success">Accept</button>
    </a>
    <hr/>

    <concern-slider v-model="concernValue" predictedValue="98"></concern-slider>

    <hr/>

    <div class="lung-select-container">
      <form>
        <radio-input v-model="lungSide" name="lung" value="left" label="Left lung"></radio-input>
        <radio-input v-model="lungSide" name="lung" value="right" label="Right lung"></radio-input>
      </form>
    </div>

    <hr>

    <div class="solidity-radio-container">
      <form>
        <radio-input v-model="solidity" name="solidity" value="solid" label="Solid"></radio-input>
        <radio-input v-model="solidity" name="solidity" value="semi-solid" label="Semi-solid"></radio-input>
        <radio-input v-model="solidity" name="solidity" value="ground-glass" label="Ground glass"></radio-input>
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
      <textarea class="form-control"  name="name" rows="3" style="width:100%;" placeholder="Add notes">
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
      solidity: 'solid',
      condition: 'unchanged',
      lungSide: 'left',
      concernValue: 50
    }
  }
}
</script>

<style scoped>

</style>
