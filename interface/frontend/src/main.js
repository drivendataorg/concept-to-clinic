import Vue from 'vue'
import VueResource from 'vue-resource'
import App from './App'
import './assets/css/bootstrap.min.css'
import './assets/css/font-awesome.min.css'
import './assets/css/project.css'
window.jQuery = window.$ = require('./assets/js/jquery-3.1.1.slim.min.js')
window.Tether = require('./assets/js/tether.min.js')
require('./assets/js/bootstrap.min.js')
require('./assets/js/ie10-viewport-bug-workaround.js')

Vue.use(VueResource)

/* eslint-disable no-new */
new Vue({
  el: '#app-container',
  components: { App }
})
