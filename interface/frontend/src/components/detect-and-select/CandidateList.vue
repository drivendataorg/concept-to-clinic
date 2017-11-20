<template>
  <div class="container">
    <template v-if="candidates.length">

      <div class="row">
        <div class="col-md-4">
          <div id="accordion">
            <template v-for="(candidate, index) in candidates">
              <div class="card">
                <div class="card-header cursor-pointer" @click="toggleShow(index)">
                  <p class="mb-0">
                    <b>Candidate {{ index + 1 }}</b> (p={{ candidate.probability_concerning }})
                    <i class="pull-right" v-if="candidate._saving">Saving...</i>
                  </p>
                </div>

                <div class="collapse" :class="{ show: selectedCandidateIndex == index }">
                  <div class="card-block">
                    <candidate :candidate="candidate" :index="index"></candidate>
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
          </div>
        </div>
        <div class="col-md-8">
          <open-dicom :view="viewerData" :marker="marker"></open-dicom>
        </div>
      </div>
    </template>
    <template v-else>
      <p class="card-text">No candidates available.</p>
    </template>
    <button @click="showDicom">Show DICOM</button>
  </div>
</template>

<script>
  import Vue from 'vue'
  import {EventBus} from '../../main.js'
  import Candidate from './Candidate'
  import OpenDicom from '../open-image/OpenDICOM'

  export default {
    components: {Candidate, OpenDicom},
    data () {
      return {
        candidates: [],
        selectedCandidateIndex: -1,
        viewerData: {
          type: 'DICOM',
          prefixCS: ':/',
          prefixUrl: '/api/images/metadata?dicom_location=/',
          paths: []
        }
      }
    },
    computed: {
      marker () {
        if (!this.selectedCandidate) {
          return null
        }

        // extract centroid location
        const {x, y, z} = this.selectedCandidate.centroid

        return {x, y, z}
      },
      selectedCandidate () {
        return this.candidates[this.selectedCandidateIndex] || null
      }
    },
    created () {
      this.fetchCandidates()
    },
    mounted: function () {
      EventBus.$on('nodule-marker-moved', (x, y, z) => {
        if (!this.selectedCandidate) {
          console.error('can\'t save new coordinates - selectedCanidate is not found')
          return
        }

        const candidates = this.candidates
        const selectedCandidate = this.selectedCandidate
        const selectedCandidateIndex = this.selectedCandidateIndex

        // mark current candidate as saving
        selectedCandidate._saving = true

        // send data to backend
        this.$axios
            .post(selectedCandidate.url + 'move', {x, y, z})
            .then((response) => {
              debugger
              if (response.status === 200) {
                Vue.set(candidates, selectedCandidateIndex, response.data)
              }
            })
      })
    },
    methods: {
      showDicom () {
        this.viewerData.paths = ['/images/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178' +
                                 '/1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192/-115.000000.dcm']
      },
      fetchCandidates () {
        this.$axios.get('/api/candidates/')
            .then((response) => {
              for (let candidate of response.data) {
                // extending result data with technical properties
                candidate._saving = false
              }

              this.candidates = response.data

              this.viewerData.paths = ['/images/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178' +
                                       '/1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192/-115.000000.dcm']
            })
            .catch(() => {
              // TODO: error callback
            })
      },
      toggleShow (index) {
        this.selectedCandidateIndex = this.selectedCandidateIndex === index ? -1 : index
      },
      mark (candidate) {
        this.$axios.get(candidate.url + 'mark')
            .then((response) => {
              console.log(response)
            })
            .catch(() => {
              // TODO: error callback
            })
      },
      dismiss (candidate) {
        this.$axios.get(candidate.url + 'dismiss')
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
