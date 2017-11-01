<template>
<p>
  <label>{{label}}  :</label>
  <span v-if="constantKey">{{ constantValue }}</span>
  <span v-else>{{ value }}</span>
</p>
</template>

<script>
export default {
  props: [ 'label', 'value', 'constant-key' ],
  computed: {
    constantValue: function () {
      return this.$constants[this.constantKey][this.value]
    }
  }
}
</script>

<style lang="scss" scoped>
p label {
  font-weight: bold;
}
</style>
