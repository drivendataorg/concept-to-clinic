// For authoring Nightwatch tests, see
// http://nightwatchjs.org/guide#usage

const nightwatchConfig = require('../nightwatch.conf');

const {
  launch_url,
  launch_port
} = nightwatchConfig.test_settings.default;

const interfaceUrl = `${launch_url}:${launch_port}`

module.exports = {
  'default e2e tests': function (browser) {
    browser
      .url(interfaceUrl)
      .waitForElementVisible('#app-container', 5000)
      .assert.elementPresent('#navbar')
      .assert.containsText('a', 'Concept To Clinic')
      .assert.elementCount('img', 1)
      .end()
  }
}
