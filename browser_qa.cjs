// Browser verification of the saved synthetic report. No model or network service.
// QA-only dependencies: playwright-core 1.62.1, @sparticuz/chromium 153.0.0 (MIT).
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {createHash} = require('node:crypto');
const {pathToFileURL} = require('node:url');
const {chromium: playwright} = require('playwright-core');
const chromiumModule = require('@sparticuz/chromium');
const chromium = chromiumModule.default || chromiumModule;

async function main() {
  const report = path.resolve(process.argv[2] || 'qa_20261022/preview');
  const output = path.resolve(process.argv[3] || 'browser_qa.json');
  const screenshots = process.argv[4] ? path.resolve(process.argv[4]) : null;
  const plan = JSON.parse(fs.readFileSync(path.join(report, 'plan.json'), 'utf8'));
  const hashReports = () => Object.fromEntries(['review.html','plan.json','review.md'].map(name =>
    [name, createHash('sha256').update(fs.readFileSync(path.join(report,name))).digest('hex')]));
  const before = hashReports();
  const browser = await playwright.launch({args: chromium.args,
    executablePath: await chromium.executablePath(), headless: true});
  const result = {browser: browser.version(), runtime: process.version,
    dependencies: {playwright_core: require('playwright-core/package.json').version,
      sparticuz_chromium: JSON.parse(fs.readFileSync(path.join(path.dirname(require.resolve('@sparticuz/chromium')), '..', 'package.json'), 'utf8')).version},
    report: 'qa_20261022/preview/review.html', synthetic_only: true,
    cases: [], network_requests: [], errors: [], screenshots_saved: Boolean(screenshots)};
  try {
    const context = await browser.newContext({offline: true});
    const page = await context.newPage();
    page.on('pageerror', e => result.errors.push(e.message));
    page.on('request', r => {if (/^https?:/.test(r.url())) result.network_requests.push(r.url());});
    for (const [width, height] of [[1280,900], [375,812], [320,800]]) {
      await page.setViewportSize({width, height});
      await page.goto(pathToFileURL(path.join(report, 'review.html')).href);
      const observed = await page.evaluate(() => ({
        title: document.title, lang: document.documentElement.lang,
        viewport: innerWidth, scroll_width: document.documentElement.scrollWidth,
        cards: [...document.querySelectorAll('article.file')].map(el => ({
          decision: el.dataset.decision, name: el.querySelector('h3 code').textContent,
          width: el.getBoundingClientRect().width})),
        scripts: document.scripts.length,
        unsafe_elements: document.querySelectorAll('img,iframe,form,object,embed').length,
        headings: [...document.querySelectorAll('h2')].map(el => el.textContent),
        main_count: document.querySelectorAll('main').length,
        links: [...document.querySelectorAll('a')].map(el => el.getAttribute('href'))
      }));
      assert.equal(observed.lang, 'en');
      assert.equal(observed.main_count, 1);
      assert.equal(observed.cards.length, plan.items.length);
      assert(observed.scroll_width <= width, 'horizontal overflow at '+width);
      assert.equal(observed.scripts, 0);
      assert.equal(observed.unsafe_elements, 0);
      assert.deepEqual(observed.links, ['plan.json', 'review.md']);
      assert.equal(observed.cards.filter(c => c.decision === 'review').length, plan.summary.needs_review);
      assert.equal(observed.cards.filter(c => c.decision === 'suggest').length, plan.summary.suggestions);
      assert.deepEqual(observed.cards.map(({decision,name})=>({decision,name})),
        ['review','suggest'].flatMap(decision=>plan.items.filter(r=>r.decision===decision)
          .map(r=>({decision,name:r.name.replace(/\n/g,'\\n')}))));
      for (const card of observed.cards) assert(card.width > 0 && card.width <= width);
      if (screenshots) {
        fs.mkdirSync(screenshots, {recursive:true});
        await page.screenshot({path:path.join(screenshots, 'report-'+width+'.png'), fullPage:true});
      }
      result.cases.push({name:'layout-'+width, passed:true, ...observed});
    }
    await page.goto(pathToFileURL(path.join(report, 'review.html')).href);
    await page.keyboard.press('Tab');
    const first = await page.locator(':focus').getAttribute('href');
    assert.equal(first, 'plan.json');
    const focus = await page.locator(':focus').evaluate(el => ({
      outlineStyle:getComputedStyle(el).outlineStyle, outlineWidth:getComputedStyle(el).outlineWidth}));
    assert.equal(focus.outlineStyle, 'solid');
    assert.equal(focus.outlineWidth, '3px');
    await page.keyboard.press('Tab');
    assert.equal(await page.locator(':focus').getAttribute('href'), 'review.md');
    for (const target of ['plan.json','review.md']) {
      await page.goto(pathToFileURL(path.join(report, target)).href);
      assert.equal(await page.locator('body').innerText().then(t=>t.length>0), true);
    }
    result.cases.push({name:'keyboard-and-sibling-links', passed:true, focus});
    assert.deepEqual(result.network_requests, []);
    assert.deepEqual(result.errors, []);
    assert.deepEqual(hashReports(), before);
    result.report_sha256_unchanged = before;
    result.passed = true;
    fs.writeFileSync(output, JSON.stringify(result,null,2)+'\n');
    console.log(JSON.stringify({passed: true, browser:result.browser, cases:result.cases.length}));
  } finally {await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
