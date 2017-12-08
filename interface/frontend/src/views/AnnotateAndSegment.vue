<template>
  <div id="annotate-and-segment" class="offset-top container">
    <nodule-list annotate="true"></nodule-list>
  </div>
</template>

<script>
import NoduleList from '../components/annotate-and-segment/NoduleList'

export default {
  name: 'annotate-and-segment',
  components: {
    NoduleList
  }
}
</script>
