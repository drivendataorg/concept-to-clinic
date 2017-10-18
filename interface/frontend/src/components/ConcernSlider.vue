<template>
  <div class="concern-slider-container">
    <div class="concern-labels row-space-between">
      <span class="text-success">Not concerning</span>
      <span class="text-danger">Concerning</span>
    </div>

    <div class="concern-slider">
      <input type="range" v-model="stateValue" @input="update"
        :class="{
            'green-thumb' : value <= 36,
            'blue-thumb' : value > 36 && value < 72,
            'red-thumb' : value >= 72
          }" />
    </div>
    <div class="concern-value row-space-between">
      <span class="predicted">
        <span class="label">Predicted</span>
        <span class="value">{{predictedValue}}%</span>
      </span>
      <span class="labeled">
        <span class="label">Labeled</span>
        <span class="value">{{stateValue}}%</span>
      </span>
    </div>
  </div>
</template>

<script>
export default {
  props: ['value', 'predictedValue'],
  data () {
    return {
      stateValue: this.value
    }
  },
  methods: {
    update () {
      // Emit the number value through the input event
      this.$emit('input', this.stateValue)
    }
  }
}
</script>

<style lang="scss" scoped>
.row-space-between {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.concern-labels {

}

.concern-slider {
  display: flex;
  justify-content: center;
  input[type=range] {
    width: 100%;
    height: 1.8em;
    padding: 0 1em;
    -webkit-appearance: none;
  }
}

/*Range input inspired by https://codepen.io/egrucza/pen/LEoOQZ*/
input[type=range]::-webkit-slider-runnable-track {
  background: rgba(59,173,227,1);
  background: linear-gradient(45deg, white 0%, #5cb85c 4.5%, rgba(87,111,230,1) 51%, #d9534f 95.4%, white 100%);
  height: 2px;
}

input[type=range]::-webkit-slider-thumb {
  -webkit-appearance: none;

  border: 4.5px solid;
  border-radius: 50%;
  height: 25px;
  width: 25px;
  max-width: 80px;
  position: relative;
  bottom: 11px;

  background-color: white;
  cursor: -webkit-grab;

  transition: border 1000ms ease;
}

input[type=range].green-thumb::-webkit-slider-thumb {
   border-color: #5cb85c;
}

input[type=range].blue-thumb::-webkit-slider-thumb {
   border-color: rgb(59,173,227);
}

input[type=range].red-thumb::-webkit-slider-thumb {
   border-color: #d9534f;
}

input[type=range]:focus {
  outline: none;
}

input[type=range]::-webkit-slider-thumb:active {
  cursor: -webkit-grabbing;
}
</style>
