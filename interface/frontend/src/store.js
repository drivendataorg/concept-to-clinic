import axios from 'axios'
import Vuex from 'vuex'
import Vue from 'vue'

Vue.use(Vuex)

// we should just use this to get the
// available endpoints, and then go from there
const API_ROOT = '/api/'

const actions = {
  populateEndpoints ({ commit }) {
    axios.get(API_ROOT).then((response) => { commit('GET_ENDPOINTS', response.data) })
  },
  loadCase ({ commit }, { url }) {
    axios.get(url).then((response) => { commit('SET_CASE_IN_PROGRESS', response.data) })
  },
  unloadCase ({ commit }) {
    commit('SET_CASE_IN_PROGRESS', {})
  },
  async startNewCase ({ commit }, { uri }) {
    axios.post(this.getters.endpoints.cases, {uri: uri})
      .then((response) => { commit('SET_CASE_IN_PROGRESS', response.data) })
  },
  refreshCase ({ dispatch }) {
    return dispatch('loadCase', store.state.caseInProgress)
  },
  async updateCandidate ({ commit }, candidate) {
    await axios.patch(candidate.url, candidate)
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
    }
  },
  actions
})

export default store
