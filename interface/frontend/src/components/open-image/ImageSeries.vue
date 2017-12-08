<template>
  <div class="container">

    <template v-if="!readyToProceed">
      <div class="row">
        <div class="col-md-12" v-if="!caseInProgressIsValid">
          <div class="alert alert-info" >
            <strong>Note:</strong> select an existing case or import imagery and create a new case to begin.
          </div>
        </div>

        <div class="col-md-12" v-else-if="!candidatesExist">
          <div class="alert alert-warning">
            <strong>Warning:</strong> selected case has no predicted candidates.
          </div>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="row">
        <div class="col-md-12">
          <div class="alert alert-success">
            Case <strong>{{ displayName(caseInProgress) }}</strong> selected.

            <router-link to="/detect-and-select" tag="span" class="float-right">
              <a class="btn btn-sm btn-outline-success">
                Start identifying nodules
                <i class="fa fa-arrow-right"></i>
              </a>
            </router-link>
            <div class="clearfix"></div>
          </div>
        </div>
      </div>
    </template>

    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            <h5 class="card-title">Available Cases</h5>
          </div>
          <div class="card-block">
            <template v-if="availableCases.length">
              <div id="accordion" role="tablist" aria-multiselectable="true">
                <div class="card card-outline-primary" v-for="case_ in availableCases" :key="case_.url">
                  <div class="card-block" role="tab">
                    <h5 class="mb-0">
                      <a data-toggle="collapse" data-parent="#accordion" href="#" @click="toggleSelect(case_)">
                        {{ displayName(case_) }}
                      </a>
                      <span class="float-right">
                        <i class="fa fa-check success" v-show="isSelectedCase(case_)"></i>
                      </span>
                    </h5>
                  </div>

                  <div class="collapse" role="tabpanel" v-bind:class="{'show': isSelectedCase(case_) }">
                    <div class="card-block">
                      <table class="table table-bordered table-condensed">
                        <thead>
                        <tr>
                          <th>key</th>
                          <th>value</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr v-for="(item, key, index) in case_">
                          <td>{{ key }}</td>
                          <td><small><pre><code>{{ item | json }}</code></pre></small></td>
                        </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </template>
            <template v-else>
              <p class="card-text">No cases available. Click Import to find images and start a case.</p>
            </template>
          </div>
        </div>
      </div>
    </div><!-- /row1 -->

    <div class="row mt-3">
      <div class="col-md-12">
        <div class="card card-outline-warning">
          <div class="card-header">
            <h5 class="card-title">
              <span class="float-right">
              <i class="fa fa-expand warning" @click="showImport = !showImport"></i>
              </span>
              Import image series for new case
            </h5>
          </div>
          <div class="card-block" v-show="showImport">
            <p class="card-text">Select available DICOM images to start case</p>

            <!-- navigation and preview -->
            <div class="row">
              <div class="col-md-8">
              <tree-view class="item left"
                 :model="directories"
                 :parent="directories.name"
                 :selectedSeries="selectedUri"
                 v-on:selectSeries="selectSeries">
              </tree-view>
              </div>
              <div class="col-md-4">
                <open-dicom class="right" :view="preview"></open-dicom>
              </div>
            </div>

            <div class="float-right">
              <button class="btn btn-success" :disabled="!selectedUri" @click="startNewCase()">
                Start New Case
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

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
      readyToProceed () {
        return (this.candidatesExist)
      },
      ...mapGetters({
        endpoints: 'endpoints',
        caseInProgress: 'caseInProgress',
        caseInProgressIsValid: 'caseInProgressIsValid',
        candidatesExist: 'candidatesExist'
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
      this.refreshAvailableCases()
      this.fetchAvailableImages()
      EventBus.$on('dicom-selection', (context) => {
        this.preview.paths = context.paths
        this.preview.state = context.state
      })
    },
    filters: {
      json (value) { return JSON.stringify(value, null, 2) }
    },
    methods: {
      refreshAvailableCases () {
        console.log('refresh called')
        this.$axios.get(this.$store.getters.endpoints.cases)
          .then((response) => { this.availableCases = response.data })
          .catch((error) => { console.log(error) })
      },
      selectCase (case_) {
        // Get the available data for the case that we have selected
        if (case_) this.$store.dispatch('loadCase', {'url': case_.url})
        this.selectedCase = case_
      },
      unselectCase () {
        this.selectedCase = null
        this.$store.dispatch('unloadCase')
      },
      isSelectedCase (otherCase) {
        if (otherCase && this.selectedCase) {
          return otherCase.url === this.selectedCase.url
        }
        return false
      },
      toggleSelect (case_) {
        if (this.selectedCase) {
          this.unselectCase()
        } else {
          this.selectCase(case_)
        }
      },
      selectSeries (seriesId) {
        console.log('selecting ', seriesId)
        this.selectedUri = seriesId
      },
      async startNewCase () {
        await this.$store.dispatch('startNewCase', {'uri': this.selectedUri})
        setTimeout(() => { this.refreshAvailableCases() }, 1000)
      },
      displayName (case_) {
        if (case_) {
          return case_.series.patient_id + ' (created at ' + case_.created.split('.')[0].replace('T', ' ') + ')'
        }
      },
      fetchAvailableImages () {
        this.$http.get('/api/images/available')
          .then((response) => { this.directories = response.body.directories })
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
