const {test,expect}=require('@playwright/test');
const CARDS=[
 ['Instagram','https://www.instagram.com/marsharbelmakhlouf/'],
 ['Facebook','https://www.facebook.com/marsharbelmakhlouf/'],
 ['YouTube','https://www.youtube.com/channel/UCcMMQgJdnV_VZuNMyKXcyGQ'],
];
for(const [path,cardHeight] of [['/',97],['/ar/',118]]){
 test(`follow-us cards ${path}`,async({page},info)=>{
  test.skip(!['phone','laptop'].includes(info.project.name));
  await page.route(url=>!['127.0.0.1','localhost'].includes(new URL(url).hostname),r=>r.abort());
  await page.goto(path,{waitUntil:'load'});
  const section=page.locator('#follow-us');
  await expect(section).toBeVisible();
  const cards=section.locator('a.follow-card');
  await expect(cards).toHaveCount(3);
  for(let i=0;i<3;i++){
   const card=cards.nth(i);
   await expect(card).toHaveAttribute('href',CARDS[i][1]);
   await expect(card).toHaveAttribute('target','_blank');
   await expect(card).toHaveAttribute('rel',/\bnoopener\b/);
   await expect(card.locator('.follow-txt strong')).toHaveText(CARDS[i][0]);
   const box=await card.boundingBox();
   expect(Math.round(box.height),`card ${i} height ${path}`).toBe(cardHeight);
  }
  if(path==='/ar/'){
   await expect(page.locator('html')).toHaveAttribute('dir','rtl');
   const sBox=await section.boundingBox(),cBox=await cards.nth(0).boundingBox();
   expect(Math.abs((cBox.x+cBox.width)-(sBox.x+sBox.width))<2,'first card at right edge in RTL').toBe(true);
  }
 });
}
for(const [path,zoom] of [['/',1],['/',2],['/ar/',1],['/ar/',2]]){
 test(`follow-us no horizontal overflow ${path} ${zoom*100}% text 390px`,async({page},info)=>{
  test.skip(info.project.name!=='laptop');
  await page.setViewportSize({width:390,height:844});
  await page.route(url=>!['127.0.0.1','localhost'].includes(new URL(url).hostname),r=>r.abort());
  await page.goto(path,{waitUntil:'load'});
  if(zoom!==1)await page.evaluate(z=>{document.documentElement.style.fontSize=`${z*100}%`},zoom);
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
  expect(overflow,`horizontal overflow ${path} at ${zoom*100}%`).toBe(0);
  const boxes=await page.locator('#follow-us a.follow-card').evaluateAll(ns=>ns.map(n=>{const b=n.getBoundingClientRect();return [Math.round(b.x),Math.round(b.y)]}));
  expect(new Set(boxes.map(b=>b[0])).size,'single column below 760px').toBe(1);
  expect(new Set(boxes.map(b=>b[1])).size,'cards stacked vertically').toBe(3);
 });
}
