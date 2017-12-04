var merge = require('webpack-merge')
var shell = require('shelljs')
var prodEnv = require('./prod.env')

var cat = shell.cat('HEAD')
var hash = '0000000'
if (cat.code === 0) {
  var cut = cat.exec('cut -d " " -f2', {silent: true}).stdout
  hash = JSON.stringify(cut.slice(0, 7))
}

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  GIT_HASH_VERSION: hash
})
