/* Explicitly opt owned Playwright browsers into the QA marker on all navigation. */
function markerScript(marker) { window.__MARSHARBEL_QA__ = marker; }
async function markContext(context, runner, kind = 'monitoring') {
  await context.addInitScript(markerScript, { kind, runner });
  await context.route(/https:\/\/(?:[a-z0-9.-]+\.)?google-analytics\.com\//, route => route.fulfill({status:204}));
  return context;
}
function installQaMarker(browser, runner, kind = 'monitoring') {
  const newContext = browser.newContext.bind(browser);
  const newPage = browser.newPage.bind(browser);
  browser.newContext = async (...args) => markContext(await newContext(...args), runner, kind);
  browser.newPage = async (...args) => {
    const page = await newPage(...args);
    await markContext(page.context(), runner, kind);
    return page;
  };
  return browser;
}
module.exports = { installQaMarker, markContext };
