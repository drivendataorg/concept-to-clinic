import Vue from 'vue'
import VueResource from 'vue-resource'
import VueRouter from 'vue-router'
import router from './routes'
import constants from './constants'
import App from './App'
import axios from 'axios'
import './assets/css/bootstrap.min.css'
import './assets/css/font-awesome.min.css'
import './assets/css/project.css'
import './assets/js/ie10-viewport-bug-workaround.js'
export const EventBus = new Vue()
Vue.use(VueResource)
Vue.use(VueRouter)
Vue.prototype.$constants = constants
Vue.prototype.$axios = axios.create({
  timeout: 10000,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
})

/* eslint-disable no-new */
new Vue({
  el: '#app-container',
  components: { App },
  router
})
