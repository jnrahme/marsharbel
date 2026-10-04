const {test,expect}=require('@playwright/test');
const books=['marina-story','maroun-story','magdalene-story','story','pio-story','jpii-story','mother-teresa-story','rafqa-story','hardini-story','peter-story','massabki-story'];
const sizes=[[390,844],[768,1024],[1280,800],[1920,1080]];
async function geometry(page){return page.evaluate(()=>{const r=s=>document.querySelector(s).getBoundingClientRect().toJSON();return{overflow:document.documentElement.scrollWidth>innerWidth,header:r('.topbar'),controls:r('.storybook-controls'),panel:r('.storybook-panel'),text:r('.storybook-text'),art:r('.storybook-illustration')};});}
for(const book of books)for(const[w,h]of sizes)test(`${book}: usable reader at ${w}`,async({page},info)=>{
 test.skip(info.project.name!=='laptop','Explicit four-breakpoint matrix runs once, not once per project');test.setTimeout(90000);
 await page.setViewportSize({width:w,height:h});await page.emulateMedia({reducedMotion:'reduce'});
 await page.addInitScript(()=>{window.__MARSHARBEL_QA__={kind:'monitoring',runner:'ci-storybook-responsive'};});
 await page.route(/google-analytics\.com/,r=>r.fulfill({status:204}));const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(`/${book}`);await expect(page.locator('#story-step')).toContainText('Page 1 of');
 const first=await geometry(page);expect(first.overflow).toBe(false);expect(first.panel.top).toBeLessThan(h-100);
 expect(await page.evaluate(()=>{const b=document.querySelector('.storybook');const summaries=[...document.querySelectorAll('main section.section')].filter(s=>s!==b&&!s.classList.contains('story-hero'));return summaries.every(s=>Boolean(b.compareDocumentPosition(s)&Node.DOCUMENT_POSITION_FOLLOWING));})).toBe(true);
 const count=Number((await page.locator('#story-step').textContent()).match(/of (\d+)/)[1]);
 for(let n=1;n<=count;n++){
  if(n>1)await page.locator('#story-next').click();await expect(page.locator('#story-step')).toHaveText(`Page ${n} of ${count}`);
  await expect.poll(async()=>{const g=await geometry(page);return g.controls.top>=g.header.bottom-2;}).toBe(true);
  const g=await geometry(page);expect(g.overflow).toBe(false);expect(g.controls.bottom).toBeLessThan(h);expect(g.art.width).toBeGreaterThan(100);expect(g.text.width).toBeGreaterThan(200);
  if(n>1&&w<=980)expect(g.text.top).toBeLessThan(h-120);
  if(await page.locator('.storybook-panel').evaluate(e=>e.classList.contains('is-reflection-page'))){expect(g.text.top).toBeGreaterThanOrEqual(g.art.bottom-1);expect(g.art.height).toBeLessThanOrEqual(281);}
 }
 // Wrapping at enlarged text must update the measured sticky inset.
 await page.evaluate(()=>document.documentElement.style.fontSize='125%');await page.locator('#story-prev').click();await page.waitForTimeout(100);const zoom=await geometry(page);expect(zoom.overflow).toBe(false);expect(zoom.controls.top).toBeGreaterThanOrEqual(zoom.header.bottom-2);
 await page.locator('details.story-settings summary').click();await page.locator('#story-reader-toggle').click();expect((await geometry(page)).overflow).toBe(false);expect(errors).toEqual([]);
});
for(const w of[390,768,1280,1920])test(`resume and AutoContinue keep controls visible at ${w}`,async({page},info)=>{
 test.skip(info.project.name!=='laptop');await page.setViewportSize({width:w,height:w===768?1024:w===1920?1080:844});await page.emulateMedia({reducedMotion:'reduce'});
 await page.addInitScript(()=>{window.__MARSHARBEL_QA__={kind:'monitoring',runner:'ci-storybook-resume'};localStorage.setItem('storybook_last_page_peter','3');window._testClips=[];window.Audio=function(src){const a={src,paused:true,playbackRate:1,play(){this.paused=false;return Promise.resolve();},pause(){this.paused=true;}};window._testClips.push(a);return a;};});
 await page.route(/google-analytics\.com/,r=>r.fulfill({status:204}));await page.goto('/peter-story');await page.locator('#story-resume-btn').click();await expect(page.locator('#story-step')).toHaveText('Page 4 of 10');
 let g=await geometry(page);expect(g.controls.top).toBeGreaterThanOrEqual(g.header.bottom-2);expect(g.panel.top).toBeGreaterThanOrEqual(g.controls.bottom-1);
 await page.locator('#story-read').click();await page.waitForFunction(()=>window._testClips.some(a=>!a.paused));await page.evaluate(()=>{const a=window._testClips.find(a=>!a.paused);a.pause();a.onerror=null;const ended=a.onended;a.onended=null;ended();});
 await expect(page.locator('#story-step')).toHaveText('Page 5 of 10');await expect.poll(async()=>{const g=await geometry(page);return g.controls.top>=g.header.bottom-2&&g.panel.top>=g.controls.bottom-1;}).toBe(true);
});
