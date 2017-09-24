<template>
<div class="card">
  <div class="card-header" @click="toggleShow(nodule)">
    <p class="mb-0">
      <b>Nodule {{ index + 1 }}</b>
    </p>
  </div>

  <div class="collapse" :class="{ show: isOpen }">
    <div class="card-block">
      <table>
        <tbody>
        <tr>
          <td>
            <select v-model="selected">
              <option disabled> -- select an option -- </option>
              <option :value="lungOrientations.left">Left lung</option>
              <option :value="lungOrientations.right">Right lung</option>
            </select>
          </td>
        </tr>
        </tbody>
      </table>
      <br>
      <a @click="update(nodule)">
        <button type="button" class="btn btn-sm btn-secondary">Accept</button>
      </a>
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
      selected: this.nodule.lung_orientation,
      lungOrientations: this.$constants.lungOrientations
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
      this.$axios.put(nodule.url, { lung_orientation: this.selected }).then((response) => {
        console.log(response)
      },
      () => {
        // error callback
      })
    }
  }
}
</script>