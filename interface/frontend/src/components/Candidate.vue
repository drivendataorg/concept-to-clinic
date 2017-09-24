<template>
<div class="card">
  <div class="card-header" @click="toggleShow(candidate)">
    <p class="mb-0">
      <b>Candidate {{ index + 1 }}</b> (p={{ candidate.probability_concerning }})
    </p>
  </div>

  <div class="collapse" :class="{ show: isOpen }">
    <div class="card-block">
      <table>
        <tbody>
          <tr>
            <td>lidc_max_sensitiv:</td>
            <td>TBI</td>
          </tr>
          <tr>
            <td>convnet_vgg:</td>
            <td>TBI</td>
          </tr>
          <tr>
            <td>convnett_vgg_lidc:</td>
            <td>TBI</td>
          </tr>
        </tbody>
      </table><br>
      Centroid (predicted):<br>
      <table style="margin-left:10px">
        <tbody>
          <tr>
            <td>Slice:</td>
            <td>TBI</td>
          </tr>
          <tr>
            <td>X:</td>
            <td>{{ candidate.centroid.x }}</td>
          </tr>
          <tr>
            <td>Y:</td>
            <td>{{ candidate.centroid.y }}</td>
          </tr>
        </tbody>
      </table>
      <a @click="dismiss(candidate)">
        <button type="button" class="btn btn-sm btn-secondary">Dismiss</button>
      </a>
      <a @click="mark(candidate)">
        <button type="button" class="btn btn-sm btn-danger">Mark concerning</button>
      </a>
    </div>
  </div>
</div>
</template>

<script>
export default {
  props: ['candidate', 'index'],
  data () {
    return {
      isOpen: false
    }
  },
  created () {
    if (this.index === 0) { this.isOpen = true }
  },
  methods: {
    toggleShow (candidate) {
      this.isOpen = !this.isOpen
    },
    mark (candidate) {
      this.$axios.get(candidate.url + 'mark').then(
        (response) => {
          console.log(response)
        },
        () => {
          // error callback
        }
      )
    },
    dismiss (candidate) {
      this.$axios.get(candidate.url + 'dismiss').then(
        (response) => {
          console.log(response)
        },
        () => {
          // error callback
        }
      )
    }
  }
}
</script>