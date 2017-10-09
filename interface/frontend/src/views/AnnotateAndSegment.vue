<template>
  <div>
    <nodule-list></nodule-list>
    <annotate></annotate>
  </div>
</template>

<script>
import NoduleList from '../components/NoduleList'
import Annotate from '../components/Annotate'

export default {
  components: {
    NoduleList,
    Annotate
  }
}
</script>
