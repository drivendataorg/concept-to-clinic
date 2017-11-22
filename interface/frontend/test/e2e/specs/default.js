// For authoring Nightwatch tests, see
// http://nightwatchjs.org/guide#usage

const nightwatchConfig = require('../nightwatch.conf');

module.exports = {
  'default e2e tests': function (browser) {

    browser
      .url('http://0.0.0.0:8080')
      .waitForElementVisible('#app-container', 5000)
      .assert.elementPresent('#navbar')
      .assert.containsText('a', 'Concept To Clinic')
      .assert.elementCount('img', 1)
      .end()
  }
}
