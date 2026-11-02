const {test,expect}=require('@playwright/test');
for(const lang of ['en','de','ar'])for(const width of [390,768,1100,1280])for(const textSize of [100,200])for(const stress of ['normal','german-expanded','long','short'])test(`language controls ${lang} ${width} ${textSize}% ${stress}`,async({page},info)=>{
 test.skip(info.project.name!=='laptop');
 await page.setViewportSize({width,height:900});
 await page.goto({en:'/travel',de:'/de/travel',ar:'/ar/travel'}[lang]);
 await page.addStyleTag({content:`html{font-size:${textSize}%}`});
 if(stress!=='normal')await page.evaluate(mode=>{document.querySelector('#sc-language-select').selectedOptions[0].textContent=mode==='long'?'DonaudampfschifffahrtsgesellschaftskapitänSprachübersetzung':mode==='german-expanded'?'Deutsche Sprache':'X';document.querySelector('#sc-install-app-btn').textContent=mode==='long'?'Anwendung installieren und zum Startbildschirm hinzufügen':mode==='german-expanded'?'App jetzt installieren':'X'},stress);
 const state=await page.evaluate(()=>{
  const controls=['#sc-language-select','#sc-install-app-btn'].map(s=>document.querySelector(s).getBoundingClientRect());
  const els=[...document.querySelectorAll('header .brand,header .links > a,header .links > .nav-group,#sc-language-switcher,#sc-install-app-btn')].filter(e=>e.getClientRects().length);let hits=[];
  for(let i=0;i<els.length;i++)for(let j=i+1;j<els.length;j++){let a=els[i].getBoundingClientRect(),b=els[j].getBoundingClientRect();if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)hits.push([i,j]);}
  const brand=document.querySelector('header .brand');const br=brand.getBoundingClientRect();const clipped=[...brand.children].filter(e=>e.getClientRects().length).some(e=>{const r=e.getBoundingClientRect();return r.left<br.left-1||r.right>br.right+1||r.top<br.top-1||r.bottom>br.bottom+1;});
  return{brandHeight:br.height,brandFont:parseFloat(getComputedStyle(brand).fontSize),clipped,hits,overflow:document.documentElement.scrollWidth>innerWidth,heights:controls.map(r=>r.height),widths:controls.map(r=>r.width)};
 });
 expect(state.brandHeight).toBeLessThanOrEqual(state.brandFont*3);expect(state.clipped).toBe(false);expect(state.hits).toEqual([]);expect(state.overflow).toBe(false);for(const h of state.heights)expect(h).toBeGreaterThanOrEqual(44);for(const w of state.widths)expect(w).toBeGreaterThanOrEqual(44);
});
for(const lang of ['en','de','ar','zh-Hans'])for(const width of [390,768])test(`language name readable ${lang} ${width} 200%`,async({page},info)=>{
 test.skip(info.project.name!=='laptop');await page.setViewportSize({width,height:900});await page.goto({en:'/travel',de:'/de/travel',ar:'/ar/travel','zh-Hans':'/travel'}[lang]);await page.addStyleTag({content:'html{font-size:200%}'});
 if(lang==='zh-Hans')await page.evaluate(()=>{document.querySelector('#sc-language-select').selectedOptions[0].textContent='简体中文';});
 const state=await page.evaluate(()=>{const e=document.querySelector('#sc-language-select'),s=getComputedStyle(e),c=document.createElement('canvas').getContext('2d');c.font=s.font;return{scroll:e.scrollWidth,client:e.clientWidth,text:c.measureText(e.selectedOptions[0].textContent).width,neededPadding:parseFloat(s.paddingLeft)+parseFloat(s.paddingRight)+20,label:e.selectedOptions[0].textContent};});
 expect(state.label).toBe({en:'English',de:'Deutsch',ar:'العربية','zh-Hans':'简体中文'}[lang]);expect(state.scroll).toBeLessThanOrEqual(state.client);expect(state.text+state.neededPadding).toBeLessThanOrEqual(state.client);
});
