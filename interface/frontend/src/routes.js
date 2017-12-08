import store from './store.js'
import VueRouter from 'vue-router'

import OpenImage from './views/OpenImage'
import DetectAndSelect from './views/DetectAndSelect'
import AnnotateAndSegment from './views/AnnotateAndSegment'
import ReportAndExport from './views/ReportAndExport'

const routes = [
  { path: '/', component: OpenImage },
  {
    path: '/detect-and-select',
    component: DetectAndSelect,
    beforeEnter: (to, from, next) => { if (store.getters.candidatesExist) next() }
  },
  {
    path: '/annotate-and-segment',
    component: AnnotateAndSegment,
    beforeEnter: (to, from, next) => { if (store.getters.nodulesExist) next() }
  },
  {
    path: '/report-and-export',
    component: ReportAndExport,
    beforeEnter: (to, from, next) => { if (store.getters.nodulesExist) next() }
  }
]

const router = new VueRouter({
  routes,
  linkActiveClass: 'active',
  linkExactActiveClass: ''
})

export default router
