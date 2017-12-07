<template>
  <div class="container">

    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            Available Cases
          </div>
          <div class="card-block">
            <template v-if="availableCases.length">
              <ul>
                <li v-for="case_ in availableCases" :key="case_.url">
                  <p>Created on: {{ case_.created }} <a href="#" @click="selectCase(case_)">{{ case_.url }}</a></p>
                </li>
              </ul>
            </template>
            <template v-else>
              <p class="card-text">No cases available. Click Import to find images and start a case.</p>
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
      <div class="col-md-8">
        <div class="card card-outline-warning">
          <div class="card-header">
            Select available DICOM images to start case
            <button class="btn btn-success pull-right"
                    :disabled="!selectedUri"
                    @click="startNewCase()">
              Start New Case
            </button>
          </div>
          <div class="card-block">
            <tree-view class="item left"
                       :model="directories"
                       :parent="directories.name"
                       :selectedSeries="selectedUri"
                       v-on:selectSeries="selectSeries">
              </tree-view>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card card-outline-warning">
          <div class="card-header">
            Preview
          </div>
          <div class="card-block">
            <open-dicom class="right" :view="preview"></open-dicom>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-md-12">
        <div class="card" v-if="selectedCase">
          <div class="card-header">
            Selected Case
          </div>
          <div class="card-block">
            <h3 class="card-title">{{ selectedCase.patient_id }}</h3>

            <table class="table table-bordered table-condensed">
              <thead>
              <tr>
                <th>key</th>
                <th>value</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="(item, key, index) in selectedCase">
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
  import OpenDicom from '../common/OpenDICOM'

  import { mapGetters } from 'vuex'

  export default {
    components: {
      TreeView,
      OpenDicom
    },
    data () {
      return {
        availableCases: [],
        selectedCase: null,
        directories: {
          name: 'root',
          children: []
        },
        preview: {
          type: 'DICOM',
          prefixCS: '://',
          prefixUrl: '/api/images/preview?dicom_location=',
          paths: [],
          state: ''
        },
        selectedUri: null,
        showImport: false
      }
    },
    computed: {
      ...mapGetters({
        endpoints: 'endpoints'
      })
    },
    watch: {
      // when the store gets the endpoints, pull the available cases.
      endpoints (val, oldVal) {
        this.$axios.get(this.$store.getters.endpoints.cases)
          .then((response) => {
            this.availableCases = response.data
          })
          .catch((error) => {
            console.log(error)

            // TODO: handle error
          })
      }
    },
    created () {
      // Try to hit the root API endpoint when this component
      // is created to get available routes in the store
      this.$store.dispatch('populateEndpoints')
    },
    mounted () {
      this.fetchAvailableImages()
      EventBus.$on('dicom-selection', (context) => {
        this.preview.paths = context.paths
        this.preview.state = context.state
      })
    },
    methods: {
      selectCase (case_) {
        // Get the available data for the case that we have selected
        this.$store.dispatch('loadCase', {'url': case_.url})
        this.selectedCase = case_
      },
      selectSeries (seriesId) {
        console.log('selecting ', seriesId)
        this.selectedUri = seriesId
      },
      startNewCase () {
        this.$store.dispatch('startNewCase', {'uri': this.selectedUri})
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
