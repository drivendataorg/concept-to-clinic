<template>
  <div class="offset-top">
    <nodule-list annotate="true"></nodule-list>
  </div>
</template>

<script>
import NoduleList from '../components/NoduleList'

export default {
  components: {
    NoduleList
  }
}
</script>

<style media="screen">
.offset-top {
  margin-top: 5em;
}

@media screen and (max-width: 990px) {
  .offset-top {
    margin-top: 10em;
  }
}

</style>
