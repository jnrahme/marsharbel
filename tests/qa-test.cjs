const base = require('@playwright/test');
const { markContext, installQaMarker } = require('../scripts/analytics/qa-browser.cjs');
const test = base.test.extend({
  browser: async ({ browser }, use) => {
    installQaMarker(browser, "quality.extra-context");
    await use(browser);
  },
  qaMarker: [async ({ context }, use, testInfo) => {
    await markContext(context, `quality.${testInfo.project.name}`);
    await use();
  }, { auto: true }]
});
module.exports = { ...base, test };
