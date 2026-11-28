const {test,expect}=require('@playwright/test');
// Saint of the Day archive card grid: dated text cards reuse the .news-row shell without its
// thumb/text/arrow structure, so their four children must stack in a single column with no
// in-grid overlap and an unclipped Read button at every breakpoint (regression: 768px/1440px EN
// overlapped titles over summaries and squeezed the CTA into the 96px thumb lane, 2026-11-20).
// The share bar is injected at runtime, so the check waits for it before measuring.
for(const path of ['/saint-of-the-day','/ar/saint-of-the-day'])for(const width of [390,768,1440]){
 test(`archive rows no in-grid overlap ${path} ${width}px`,async({page},info)=>{
  test.skip(info.project.name!=='laptop');
  await page.route(url=>!['127.0.0.1','localhost'].includes(new URL(url).hostname),r=>r.abort());
  await page.setViewportSize({width,height:900});
  await page.goto(path,{waitUntil:'load'});
  await page.evaluate(()=>document.querySelectorAll('.reveal').forEach(e=>e.classList.add('is-visible')));
  await page.waitForTimeout(500);
  const bad=await page.evaluate(()=>{
   const out=[];
   const rows=[...document.querySelectorAll('.news-list .news-row')];
   if(!rows.length)out.push('no archive rows found');
   for(const row of rows){
    const rr=row.getBoundingClientRect();
    const kids=[...row.children].filter(e=>e.getClientRects().length);
    const rects=kids.map(e=>({cls:e.className.split(' ')[0],r:e.getBoundingClientRect()}));
    for(let i=0;i<rects.length;i++)for(let j=i+1;j<rects.length;j++){
     const a=rects[i].r,b=rects[j].r;
     if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)
      out.push(`overlap ${rects[i].cls} x ${rects[j].cls} in ${row.id||'row'}`);
    }
    const cta=row.querySelector('.news-lead-cta');
    if(cta&&cta.getClientRects().length){
     const cr=cta.getBoundingClientRect();
     if(cr.left<rr.left-1||cr.right>rr.right+1)out.push(`cta outside row in ${row.id||'row'}`);
     if(cta.scrollWidth>cta.clientWidth+1)out.push(`cta label clipped in ${row.id||'row'}`);
    }
    // RTL collapse: a squeezed grid track can drop to zero width while its text keeps painting
    // over neighbours (box intersection misses it); horizontal text overflow catches it.
    for(const e of kids){
     if(e.classList.contains('share-bar'))continue;
     if(e.scrollWidth>e.clientWidth+1)out.push(`${e.className.split(' ')[0]} text overflows its track in ${row.id||'row'} (scroll ${e.scrollWidth} > client ${e.clientWidth})`);
    }
   }
   if(document.documentElement.scrollWidth>window.innerWidth+1)out.push('page sideways scroll');
   return out;
  });
  expect(bad).toEqual([]);
 });
}
