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
      .then((response) => {
        commit('GET_ENDPOINTS', response.data)
      })
  },
  loadCase ({ commit }, { url }) {
    console.log(url)
    axios.get(url)
      .then((response) => {
        commit('SET_CASE_IN_PROGRESS', response.data)
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
    endpoints (state) {
      return state.topLevelEndpoints
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
