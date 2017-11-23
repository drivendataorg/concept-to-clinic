require('browser-env')();

const hooks = require('require-extension-hooks');
const Vue = require('vue');

Vue.config.productionTip = false;

Vue.prototype.$axios = {
  get : () => new Promise(function(resolve, reject) {
    resolve()
  })
}

hooks('vue').plugin('vue').push()

hooks(['vue','js']).plugin('babel').push()
