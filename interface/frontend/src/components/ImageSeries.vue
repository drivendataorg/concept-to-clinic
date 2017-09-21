<template>
<div class="container">
  <div class="row">
    <div class="col-md-4">
      <div class="card">
        <div class="card-block">
          <h3 class="card-title">Available directories</h3>
          <template v-if="directories.length">
            <ul>
              <li v-for="dir in directories">
                {{ dir }}
              </li>
            </ul>
          </template>
        </div>
      </div><!-- left side -->
    </div>

    <div class="col-md-8">

      <div class="row">
        <div class="col-md-12">
          <div class="card">
            <div class="card-block">
              <h3 class="card-title">Available image series</h3>
              <template v-if="availableSeries.length">
                <ul>
                  <li v-for="series in availableSeries">
                    <a href="#" @click="selectSeries(series)">{{ series.series_instance_uid }}</a>
                    <span v-if="series == selected">&larr;</span>
                  </li>
                </ul>
              </template>
              <template v-else>
                <p class="card-text">No images available.</p>
              </template>
            </div>
          </div>
        </div>
      </div>

      <div class="row" v-if="selected">
        <div class="col-md-12">
          <div class="card">
            <div class="card-block">
              <h3 class="card-title">{{ selected.patient_id }}</h3>

              <table class="table table-bordered table-condensed">
                <thead></thead>
                <tr>
                  <th>key</th>
                  <th>value</th>
                </tr>
                <tbody>
                <tr v-for="(item, key) in selected">
                  <td>{{ key }}</td>
                  <td>{{ item }}</td>
                </tr>
                </tbody>
              </table>

              <a class="btn btn-primary">Start case</a>
            </div>
          </div>
        </div>
      </div>

    </div><!-- right side -->

  </div><!-- row -->
</div><!-- container -->
</template>

<script>
export default {
  data () {
    return {
      availableSeries: [],
      directories: [],
      selected: null
    }
  },
  created () {
    this.fetchImages()
    this.fetchDirectories()
  },
  methods: {
    fetchImages () {
      this.$axios.get('/api/images/').then(
        (response) => {
          this.availableSeries = response.data
        },
        () => {
          // error callback
        })
    },
    selectSeries (series) {
      this.selected = series
    },
    fetchDirectories () {
      this.$axios.get('/api/images/available').then(
        (response) => {
          this.directories = response.data.directories
        },
        () => {
          // error callback
        }
      )
    }
  }
}
</script>

<style>
</style>
