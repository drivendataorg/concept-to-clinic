<template>
  <div class="container">

    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            Open imagery
          </div>
          <div class="card-block">
            <template v-if="availableSeries.length">
              <ul>
                <li v-for="series in availableSeries" :key="series.series_instance_uid">
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
          <div class="card-block left">
            <tree-view class="item left" :model="directories"></tree-view>
            <open-dicom class="right" :view="preview"></open-dicom>
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
  import { EventBus } from '../../main.js'
  import TreeView from './TreeView'
  import OpenDicom from './OpenDICOM'

  export default {
    components: {
      TreeView,
      OpenDicom
    },
    data () {
      return {
        availableSeries: [],
        directories: {
          name: 'root',
          children: []
        },
        preview: {
          type: 'DICOM',
          prefixCS: '://',
          prefixUrl: '/api/images/metadata?dicom_location=/',
          paths: []
        },
        selected: null,
        showImport: false
      }
    },
    created () {
      this.fetchData()
      this.fetchAvailableImages()
    },
    mounted: function () {
      EventBus.$on('dicom-selection', (path) => {
        this.preview.paths = path
        console.log(this.preview)
      })
    },
    methods: {
      fetchData () {
        this.$http.get('/api/images/')
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
        this.$http.get('/api/images/available')
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
  .left {
    float: left;
  }
  .right {
    float: right;
  }
</style>
