<template>
  <div class="container" style="margin-top: 5em;">

    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            Open imagery
          </div>
          <div class="card-block">
            <template v-if="availableSeries.length">
              <ul>
                <li v-for="series in availableSeries">
                  <a href="#" @click="selectSeries(series)">{{ series.series_instance_uid }}</a>
                  <span v-if="series == selected">&larr;</span>
                </li>
              </ul>
            </template>
            <template v-else>
              <p class="card-text">No images imported.</p>
            </template>
            <button class="btn btn-warning float-right"
                    @click="showImport = !showImport"
            >
              Import
            </button>
          </div>
        </div>
      </div>
    </div><!-- /row1 -->

    <div class="row" v-show="showImport">
      <div class="col-md-12">
        <div class="card card-outline-warning">
          <div class="card-header">
            Import image series
          </div>
          <div class="card-block">
            <tree-view class="item" :model="directories"></tree-view>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-md-12">
        <div class="card" v-if="selected">
          <div class="card-header">
            Selected image series
          </div>
          <div class="card-block">
            <h3 class="card-title">{{ selected.patient_id }}</h3>

            <table class="table table-bordered table-condensed">
              <thead>
              <tr>
                <th>key</th>
                <th>value</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="(item, key, index) in selected">
                <td>{{ key }}</td>
                <td><small>{{ item }}</small></td>
              </tr>
              </tbody>
            </table>

            <a href="#" class="btn btn-primary float-right">Start case</a>
          </div>
        </div>
      </div>
    </div><!-- /row2 -->

  </div><!-- /container -->
</template>

<script>
  import TreeView from './TreeView'

  export default {
    components: {
      TreeView
    },
    data () {
      return {
        availableSeries: [],
        directories: {
          name: 'root',
          children: []
        },
        selected: null,
        showImport: false
      }
    },
    created () {
      this.fetchData()
      this.fetchAvailableImages()
    },
    methods: {
      fetchData () {
        this.$axios.get('/api/images/')
          .then((response) => {
            this.availableSeries = response.body
          })
          .catch(() => {
            // TODO: handle error
          })
      },
      selectSeries (series) {
        console.log(series.uri)
        this.selected = series
      },
      fetchAvailableImages () {
        this.$axios.get('/api/images/available')
          .then((response) => {
            this.directories = response.body.directories
          })
          .catch(() => {
            // TODO: handle error
          })
      }
    }
  }
</script>

<style lang="scss" scoped>
</style>
