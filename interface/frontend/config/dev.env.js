var merge = require('webpack-merge')
var shell = require('shelljs')
var prodEnv = require('./prod.env')
var hash = shell.cat('HEAD').exec('cut -d " " -f2', {silent: true}).stdout

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  GIT_HASH_VERSION: JSON.stringify(hash.slice(0, 9))
})
