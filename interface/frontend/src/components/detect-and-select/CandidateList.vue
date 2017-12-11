<template>
  <div class="container">
    <template>
      <div class="row">
        <div class="col-md-3">
          <div id="accordion">
            <template v-for="(candidate, index) in candidates">
              <div class="card">
                <div class="card-header cursor-pointer" @click="toggleShow(index)">
                  <p class="mb-0" :class="{ 'candidate-active': candidate.url === selectedCandidate.url,
                     'candidate-inactive': candidate.url !== selectedCandidate.url}"
                  >
                    <span class="candidate-title">
                      Candidate {{ index + 1 }}
                    </span>
                    <span v-if="candidate.probability_concerning">
                      (p={{ candidate.probability_concerning | round3 }})
                    </span>
                    <span v-else-if="candidate.added_by_hand">
                      (added manually)
                    </span>

                    <span class="float-right" v-if="candidate._saving">
                      <i class="fa fa-spinner fa-spin"></i>
                    </span>
                    <span class="float-right" v-else>
                      <i class="fa fa-times danger" v-if="candidate.review_result === REVIEW_RESULT.DISMISSED"></i>
                      <i class="fa fa-check success" v-if="candidate.review_result === REVIEW_RESULT.MARKED"></i>
                      <i class="fa fa-question default" v-if="candidate.review_result === REVIEW_RESULT.NONE"></i>
                    </span>
                  </p>
                </div>

                <div class="collapse" :class="{ show: selectedCandidateIndex == index }">
                  <div class="card-block">
                    <candidate :candidate="candidate" :index="index"></candidate>
                    <div class="float-right">
                      <button type="button" class="btn btn-sm btn-secondary"
                        @click="markOrDismiss(candidate, REVIEW_RESULT.DISMISSED)"
                        :disabled="candidate._saving || candidate.review_result === REVIEW_RESULT.DISMISSED"
                      >
                        <i class="fa fa-times danger"></i> Dismiss
                      </button>
                      <button type="button" class="btn btn-sm btn-secondary"
                        @click="markOrDismiss(candidate, REVIEW_RESULT.MARKED)"
                        :disabled="candidate._saving || candidate.review_result === REVIEW_RESULT.MARKED"
                      >
                        <i class="fa fa-check success"></i> Mark concerning
                      </button>
                    </div>
                    <div class="clearfix"></div>
                  </div>
                </div>
              </div>
            </template>
            <div class="mt-2">
              <span class="float-right">
                <a href="#">
                  <button @click="addCandidate()" class="btn btn-default">Manually add location</button>
                </a>
              </span>
              <div class="clearfix"></div>
            </div>
          </div>
        </div>
        <div class="col-md-9" style="min-height: 500px">
          <open-dicom :view="viewerData" :marker="marker"></open-dicom>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
  import {EventBus} from '../../main.js'
  import Candidate from './Candidate'
  import OpenDicom from '../common/OpenDICOM'

  export default {
    components: {Candidate, OpenDicom},
    data () {
      return {
        REVIEW_RESULT: this.$constants.CANDIDATE_REVIEW_RESULT,
        selectedCandidateIndex: 0
      }
    },
    computed: {
      candidates () {
        return this.$store.getters.candidates.sort((a, b) => {
          return b.probability_concerning - a.probability_concerning
        })
      },
      viewerData () {
        return {
          type: 'DICOM',
          prefixCS: ':/',
          prefixUrl: '/api/images/preview?dicom_location=',
          paths: this.$store.getters.imagePaths,
          sliceIndex: this.selectedCandidateIndex || 0
        }
      },
      marker () {
        if (!this.selectedCandidate) {
          return null
        }

        // extract centroid location
        const {x, y, z} = this.selectedCandidate.centroid

        return {x, y, z}
      },
      selectedCandidate () {
        // selected candidate is changing
        const candidate = this.candidates[this.selectedCandidateIndex] || null

        if (candidate) {
          this.viewerData.sliceIndex = candidate.centroid.z
        }
        return candidate
      }
    },
    mounted: function () {
      EventBus.$on('nodule-marker-moved', (x, y, z) => {
        this.moveSelectedCandidate(x, y, z)
      })
    },
    methods: {
      toggleShow (index) {
        this.selectedCandidateIndex = this.selectedCandidateIndex === index ? -1 : index
      },
      async markOrDismiss (candidate, result) {
        if (!candidate._saving && result !== candidate.review_result) {
          candidate._saving = true
          candidate.review_result = result
          await this.$store.dispatch('updateCandidate', candidate)
        }
      },
      async moveSelectedCandidate (x, y, z) {
        if (!this.selectedCandidate) {
          console.error('can\'t save new coordinates - selectedCanidate is not found')
          return
        }

        // mark current candidate as saving
        this.selectedCandidate._saving = true
        this.selectedCandidate.centroid.x = x
        this.selectedCandidate.centroid.y = y
        this.selectedCandidate.centroid.z = z

        // send data to backend
        await this.$store.dispatch('updateCandidate', this.selectedCandidate)
      },
      async addCandidate () {
        var newCandidate = {
          centroid: {x: 5, y: 5, z: 5},
          probability_concerning: null,
          case: this.$store.getters.caseInProgress.url,
          added_by_hand: true,
          review_result: this.REVIEW_RESULT.MARKED
        }
        await this.$store.dispatch('addCandidateToCaseInProgress', newCandidate)
        var newestTimestamp = this.candidates.map(d => d.created).sort()[this.candidates.length - 1]
        var newestCandidateIndex = this.candidates.findIndex(d => d.created === newestTimestamp)
        this.selectedCandidateIndex = newestCandidateIndex
      }
    }
  }
</script>

<style lang="scss" scoped>
  .candidate-inactive {
    opacity: 0.5;
  }

  .candidate-active .candidate-title {
    font-weight: bold;
  }
</style>
