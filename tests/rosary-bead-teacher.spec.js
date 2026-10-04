const {test,expect}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
test.beforeEach(async({page})=>{await page.route(url=>!['127.0.0.1','localhost'].includes(new URL(url).hostname),route=>route.abort());});
test('poster-first teaching, keyboard activation and whole decade',async({page})=>{
 await page.goto('/rosary-prayer-coach');
 await expect(page.locator('.bead-poster')).toBeVisible();
 await expect(page.locator('#bead-controls')).toBeHidden();
 await page.locator('#bead-practice summary').focus();await page.keyboard.press('Enter');
 await expect(page.locator('#bead-current')).toContainText('Our Father');
 await expect(page.locator('[data-current]')).toHaveAttribute('data-bead','0');
 await page.locator('#bead-next').focus();await page.keyboard.press('Enter');
 await expect(page.locator('#bead-current')).toContainText('Hail Mary 1 of 10');
 for(let i=0;i<9;i++)await page.locator('#bead-next').click();
 await expect(page.locator('#bead-current')).toContainText('Hail Mary 10 of 10');
 await expect(page.locator('#bead-next')).toHaveText('Finish decade');
 await page.locator('#bead-next').click();await expect(page.locator('#bead-current')).toContainText('Glory Be');
 await expect(page.locator('#bead-next')).toBeDisabled();
 await page.locator('#bead-previous').click();await expect(page.locator('#bead-current')).toContainText('Hail Mary 10');
 await page.locator('#bead-reset').click();await expect(page.locator('#bead-previous')).toBeDisabled();
 await page.locator('#coach-time').selectOption('5');await page.locator('#coach-build').click();
 await expect(page.locator('#coach-output')).toContainText('5 minutes, 1 decade');
 expect((await new AxeBuilder({page}).include('.bead-teacher').analyze()).violations).toEqual([]);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
test('no-WebGL and reduced-motion preserve practice',async({page})=>{
 await page.addInitScript(()=>{HTMLCanvasElement.prototype.getContext=()=>null;});
 await page.emulateMedia({reducedMotion:'reduce'});await page.goto('/rosary-prayer-coach');
 await page.locator('#bead-practice summary').click();await page.locator('#bead-next').click();
 await expect(page.locator('#bead-current')).toContainText('Hail Mary 1');
 expect(await page.locator('.bead-teacher').evaluate(el=>el.getAnimations({subtree:true}).filter(a=>a.playState==='running').length)).toBe(0);
 expect(await page.locator('canvas, model-viewer').count()).toBe(0);
});
test('without JavaScript poster and complete text order still work',async({browser,baseURL})=>{
 const ctx=await browser.newContext({javaScriptEnabled:false});const p=await ctx.newPage();await p.goto(baseURL+'/rosary-prayer-coach');
 await expect(p.locator('.bead-poster')).toBeVisible();await p.locator('summary').click();await expect(p.locator('.bead-intro')).toContainText('Glory Be');await expect(p.locator('#bead-controls')).toBeHidden();await ctx.close();
});
test('enlarged text remains readable with keyboard-scrollable diagram',async({page})=>{
 await page.goto('/rosary-prayer-coach');await page.addStyleTag({content:'html {font-size:200% !important}'});
 await expect(page.locator('.bead-intro')).toContainText('meditating on the mystery');
 const diagram=page.getByRole('group',{name:'Bead order illustration. Scroll horizontally if text is enlarged.'});
 await diagram.focus();await page.keyboard.press('ArrowRight');
 if(await page.evaluate(()=>innerWidth<800)) expect(await diagram.evaluate(el=>el.scrollWidth>el.clientWidth)).toBe(true);
 expect(await page.locator('.bead-teacher').evaluate(el=>el.getBoundingClientRect().right<=innerWidth+1)).toBe(true);
 const label=page.locator('.bead-numbers span').first();expect(await label.evaluate(el=>parseFloat(getComputedStyle(el).fontSize))).toBeGreaterThanOrEqual(27);
});
