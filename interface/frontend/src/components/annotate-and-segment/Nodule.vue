<template>
<div class="card">
  <div class="card-header" @click="toggleShow(nodule)">
    <h1>Nodule {{ index + 1 }}</h1>
    <span class="fa" :class="{
        'fa-chevron-up' : isOpen,
        'fa-chevron-down' : !isOpen
      }"></span>
  </div>

  <div class="collapse" :class="{ show: isOpen }">
    <div class="card-block">
      <!-- L: With the add-on-editor slot, this component can be
              extended with a variety of foreign editor.
            Check NoduleList for example usage
          -->
      <slot name="add-on-editor"></slot>
    </div>
  </div>
</div>
</template>

<script>
export default {
  props: ['nodule', 'index'],
  data () {
    return {
      isOpen: false,
      selected: this.nodule.lung_orientation
    }
  },
  created () {
    if (this.index === 0) { this.isOpen = true }
  },
  methods: {
    toggleShow (nodule) {
      this.isOpen = !this.isOpen
    },
    update (nodule) {
      this.$axios.put(nodule.url, { lung_orientation: this.selected })
        .then((response) => {
          console.log(response)
        })
        .catch(() => {
          // TODO: error callback
        })
    }
  }
}
</script>

<style lang="scss" scoped media="screen">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 45px;
  padding: 1em;

  h1 {
    margin: 0;
    font-size: 1em;
    font-weight: bold;
  }
}
</style>
