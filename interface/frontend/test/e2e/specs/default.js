// For authoring Nightwatch tests, see
// http://nightwatchjs.org/guide#usage

const nightwatchConfig = require('../nightwatch.conf');

const {
  launch_url,
  launch_port,
  screenshots
} = nightwatchConfig.test_settings.default;

const interfaceUrl = `${launch_url}:${launch_port}`

module.exports = {
  'default e2e test': function (browser) {
    browser
      .url(interfaceUrl)
      .waitForElementVisible('#app-container', 5000)
      .assert.elementPresent('#navbar')
      .assert.containsText('a', 'Concept To Clinic')
      .saveScreenshot(`${screenshots.path}/success/default_e2e_test.png`)
      .end()
  }
}
