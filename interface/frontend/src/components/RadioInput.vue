<template>
  <label class="radio">
    <input type="radio" :name="name" :value="value" @change="update" :checked='checked === value'>
    <span class="outer"><span class="inner"></span></span>
    {{label}}
  </label>
</template>

<script>
export default {
  model: {
    prop: 'checked',
    event: 'change'
  },
  props: ['name', 'label', 'value', 'checked'],
  methods: {
    update () {
      this.$emit('change', this.value)
    }
  }
}
</script>

<style scoped>
/* Radio button style inspired by https://codepen.io/jchristianhall/pen/cvFrm */
.radio {
  display: inline-block;
  padding-right: 20px;
  line-height: 50px;
  font-size: 1em;
  cursor: pointer;
}

.radio:hover .inner {
  transform: scale(0.5);
  opacity: .5;
}

.radio input {
  height: 1px;
  width: 1px;
  opacity: 0;
}

.radio input:checked + .outer .inner {
  transform: scale(1);
  opacity: 1;
}

.radio input:checked + .outer {
  border-color: #f08b3b;
}

.radio input:focus + .outer .inner {
  transform: scale(1);
  opacity: 1;
  background-color: #e67012;
}

.radio .outer {
  display: block;
  float: left;
  margin: 10px 9px 10px 10px;
  border: 3px solid #0c70b4;
  border-radius: 50%;
  background-color: #fff;
}
.radio .inner {

  transition: all 0.25s ease-in-out;
  height: 16px;
  width: 16px;

  transform: scale(0);
  display: block;
  margin: 2px;
  border-radius: 50%;
  background-color: #f08b3b;
  opacity: 0;
}

</style>
