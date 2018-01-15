import axios from 'axios'
import Vuex from 'vuex'
import Vue from 'vue'

Vue.use(Vuex)

// we should just use this to get the
// available endpoints, and then go from there
const API_ROOT = '/api/'

const actions = {
  populateEndpoints ({ commit }) {
    axios.get(API_ROOT)
      .then((response) => { commit('GET_ENDPOINTS', response.data) })
  },
  loadCase ({ commit }, { url }) {
    axios.get(url)
      .then((response) => { commit('SET_CASE_IN_PROGRESS', response.data) })
  },
  unloadCase ({ commit }) {
    commit('SET_CASE_IN_PROGRESS', {})
  },
  async startNewCase ({ commit }, { uri }) {
    axios.post(this.getters.endpoints.cases, {uri: uri})
      .then((response) => { commit('SET_CASE_IN_PROGRESS', response.data) })
  },
  refreshCaseInProgress ({ dispatch }) {
    dispatch('loadCase', store.state.caseInProgress)
  },
  updateCandidate ({ commit }, candidate) {
    axios.patch(candidate.url, candidate).then((response) => {
      if (response.status === 200) commit('UPDATE_SPECIFIC_CANDIDATE', response.data)
    })
  },
  updateNodule ({ commit }, nodule) {
    axios.patch(nodule.url, nodule).then((response) => {
      if (response.status === 200) commit('UPDATE_SPECIFIC_NODULE', response.data)
    })
  },
  async addCandidateToCaseInProgress ({commit}, candidate) {
    await axios.post(this.getters.endpoints.candidates, candidate)
      .then((response) => {
        if (response.status === 201) commit('ADD_CANDIDATE_TO_CASE_IN_PROGRESS', response.data)
      })
  }
}

const store = new Vuex.Store({
  state: {
    // the case that we are working on, either selected or
    // created on the open and import page
    caseInProgress: {},

    // the top-level URLs returned from a call to the base `/api` URL
    topLevelEndpoints: {}
  },
  getters: {
    caseInProgress (state) {
      return state.caseInProgress
    },
    caseInProgressIsValid  (state, getters) {
      return ('url' in getters.caseInProgress)
    },
    endpoints (state) {
      return state.topLevelEndpoints
    },
    candidates (state) {
      return state.caseInProgress ? state.caseInProgress.candidates : []
    },
    candidatesExist (state, getters) {
      if (!getters.caseInProgressIsValid) return false
      return getters.candidates && getters.candidates.length > 0
    },
    nodules (state) {
      return state.caseInProgress ? state.caseInProgress.nodules : []
    },
    nodulesExist (state, getters) {
      if (!getters.caseInProgressIsValid) return false
      return getters.nodules && getters.nodules.length > 0
    },
    imagePaths (state) {
      if (state.caseInProgress.series) {
        return state.caseInProgress.series.images.map((x) => x.preview_url)
      } else {
        return []
      }
    }
  },
  mutations: {
    GET_ENDPOINTS (state, endpoints) {
      state.topLevelEndpoints = endpoints
    },
    SET_CASE_IN_PROGRESS (state, _case) {
      state.caseInProgress = _case
    },
    ADD_CANDIDATE_TO_CASE_IN_PROGRESS (state, candidate) {
      state.caseInProgress.candidates.push(candidate)
    },
    UPDATE_SPECIFIC_CANDIDATE (state, updated) {
      var candidates = state.caseInProgress.candidates
      var index = candidates.findIndex(c => c.url === updated.url)
      candidates.splice(index, 1, updated)
      state.caseInProgress.candidates = candidates
    },
    UPDATE_SPECIFIC_NODULE (state, updated) {
      var nodules = state.caseInProgress.nodules
      var index = nodules.findIndex(c => c.url === updated.url)
      nodules.splice(index, 1, updated)
      state.caseInProgress.nodules = nodules
    }
  },
  actions
})

export default store
