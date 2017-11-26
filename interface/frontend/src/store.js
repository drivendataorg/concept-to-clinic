// Used to quickly retrieve the result of each route in the guard
const ROUTE_DEPENDENCY_MAP = {
  '/': 'login',
  '/detect-and-select': 'openImage',
  '/annotate-and-segment': 'detectAndSelect',
  '/report-and-export': 'annotateAndSegment'
}

const ROUTE_RESULT_MAP = {
  '/': 'openImage',
  '/detect-and-select': 'detectAndSelect',
  '/annotate-and-segment': 'annotateAndSegment',
  '/report-and-export': 'reportAndExport'
}

const ROUTE_RESULT = {
  // NOTE: Used to store user's login.
  // Make it true for now as it is the begining of the flow
  login: true,
  // Used to store the active image or any returning result from Openiamge
  openImage: null,
  // Used to store result (can be an object, or etc) from DetectAndSelect
  detectAndSelect: null,
  // Same as above
  annotateAndSegment: null,
  // This might not be needed, but for completeness
  reportAndExport: null
}

const ROUTE_ORDER = [
  '/',
  '/detect-and-select',
  '/annotate-and-segment',
  '/report-and-export'
]

// NOTE: This localstore can be easily replaced with any key-val storage,
// like localstorage or redis for instance.
export default class Store {

  // This trace the route order and return the first route that
  // is a missing dependency
  static getFirstValidRoute () {
    for (let i = 0; i < ROUTE_ORDER.length; i++) {
      const route = ROUTE_ORDER[i]
      const resultKey = ROUTE_RESULT_MAP[route]

      if (!ROUTE_RESULT[resultKey]) {
        return route
      }
    }
    return ROUTE_ORDER[0]
  }

  static getRouteDependency (route) {
    const resultKey = ROUTE_DEPENDENCY_MAP[route]
    return ROUTE_RESULT[resultKey]
  }

  static setRouteResult (route, value) {
    const resultKey = ROUTE_RESULT_MAP[route]
    ROUTE_RESULT[resultKey] = value
  }
}
