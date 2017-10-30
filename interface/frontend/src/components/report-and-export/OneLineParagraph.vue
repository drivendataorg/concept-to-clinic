<template>
<p>
  <label>{{label}}  :</label> <span>{{ value }}</span>
</p>
</template>

<script>
export default {
  props: [ 'label', 'value' ]
}
</script>

<style lang="scss" scoped>
p label {
  font-weight: bold;
}
</style>
