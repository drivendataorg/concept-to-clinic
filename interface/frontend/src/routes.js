import VueRouter from 'vue-router'
import OpenImage from './views/OpenImage'
import DetectAndSelect from './views/DetectAndSelect'
import AnnotateAndSegment from './views/AnnotateAndSegment'
import ReportAndExport from './views/ReportAndExport'

const routes = [
  { path: '/', component: OpenImage },
  { path: '/detect-and-select', component: DetectAndSelect },
  { path: '/annotate-and-segment', component: AnnotateAndSegment },
  { path: '/report-and-export', component: ReportAndExport }
]

export default new VueRouter({
  routes,
  linkActiveClass: 'active',
  linkExactActiveClass: ''
})
