// see http://vuejs-templates.github.io/webpack for documentation.
var path = require('path')

module.exports = {
  build: {
    index: path.resolve(__dirname, process.env.NODE_ENV === 'production' ? 'templates/index.html' : 'index.html'),
    assetsRoot: path.resolve(__dirname, process.env.NODE_ENV === 'production' ? 'static' : 'src'),
    assetsSubDirectory: process.env.NODE_ENV === 'production' ? '' : '/assets',
    assetsPublicPath: process.env.NODE_ENV === 'production' ? '/static' : '/',
    productionSourceMap: true
  },
  dev: {
    port: 8080,
    proxyTable: {}
  }
}
