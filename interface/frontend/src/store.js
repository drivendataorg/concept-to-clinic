import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export const store = new Vuex.Store({
  state: {
    caseInProgress: {}
  },
  getters: {
    caseInProgress (state) {
      return state.caseInProgress
    }
  }
})
