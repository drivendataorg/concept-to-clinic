// For authoring Nightwatch tests, see
// http://nightwatchjs.org/guide#usage
const nightwatchConfig = require('../nightwatch.conf');

const {
  launch_url,
  launch_port,
  screenshots
} = nightwatchConfig.test_settings.default;

const interfaceUrl = `${launch_url}:${launch_port}/#/`

const ssOkPath = `${screenshots.path}/default/ok`

module.exports = {
  'C2C header ok': function (browser) {
    const ssPath = `${ssOkPath}/c2c_header.png`;
    browser
      .url(interfaceUrl)
      .waitForElementVisible('#app-container', 5000)
      .assert.elementPresent('#navbar')
      .assert.containsText('a', 'Concept To Clinic')
      .saveScreenshot(ssPath)
      .end()
  },
  'Block navigation if prerequiste not met': function (browser) {

    browser
      .url(interfaceUrl)
      .waitForElementVisible('#app-container', 5000)
      .assert.elementPresent('#navbar')
      .click('a[href="#/detect-and-select"]')
      .pause(500)
      .assert.urlEquals(interfaceUrl)
      .end()
  }
}
