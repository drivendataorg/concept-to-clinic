import VueRouter from 'vue-router'

import OpenImage from './views/OpenImage'
import DetectAndSelect from './views/DetectAndSelect'
import AnnotateAndSegment from './views/AnnotateAndSegment'
import ReportAndExport from './views/ReportAndExport'

import Store from './store'

const routes = [
  { path: '/', component: OpenImage },
  { path: '/detect-and-select', component: DetectAndSelect },
  { path: '/annotate-and-segment', component: AnnotateAndSegment },
  { path: '/report-and-export', component: ReportAndExport }
]

const router = new VueRouter({
  routes,
  linkActiveClass: 'active',
  linkExactActiveClass: ''
})

// Global guard that check for each piece of data in the store
// to ensure next step has the required data
router.beforeEach((to, from, next) => {
  const routeResult = Store.getRouteDependency(to.path)
  if (!routeResult) {
    return next(Store.getFirstValidRoute())
  }
  // Do some extra validation per route to ensure data in the store is valid.
  // Or, do the validation from the route itself is also ok!
  next()
})

export default router
