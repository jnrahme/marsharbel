(async function () {
  'use strict';
  const {client,node,rpc}=window.Testimony;
  const publishedRoot=document.getElementById('reader-testimony-list'); const message=document.getElementById('testimony-empty');
  if(!publishedRoot)return;
  if(!client){message.textContent=window.TESTIMONY_COPY.readerUnavailable;return;}
  let offset=0;const more=node('button','Load more reader testimonies','btn subtle');more.type='button';more.hidden=true;publishedRoot.after(more);
  async function load(){
    more.disabled=true;
    try{
      const {data,error}=await client.from('testimony_publications').select('id,display_name,story,country,event_date,published_at,label').order('published_at',{ascending:false}).order('id',{ascending:false}).range(offset,offset+19);
      if(error)throw new Error();
      for(const row of data){
        const article=node('article',null,'card testimony-card');article.append(node('p',row.label,'kicker'),node('h3',row.display_name),node('p',[row.country,row.event_date].filter(Boolean).join(' · '),'source-meta'),node('p',row.story,'testimony-text'));
        const report=node('details');report.append(node('summary','Report this testimony'));
        const form=node('form',null,'testimony-form');const label=node('label','What should the moderator review?');const reason=node('textarea');reason.required=true;reason.minLength=10;reason.maxLength=1000;label.append(reason);
        const send=node('button','Send report','btn subtle');send.type='submit';const result=node('p');result.setAttribute('role','status');form.append(label,send,result);
        form.addEventListener('submit',async event=>{event.preventDefault();send.disabled=true;try{const {data:{session}}=await client.auth.getSession();if(!session){result.replaceChildren(document.createTextNode('Please sign in to report abuse. '));const a=node('a','Your account');a.href='account.html';result.append(a);return;}await rpc('testimony_report',{p_id:row.id,p_reason:reason.value.trim()});result.textContent='Your private report has been sent to the moderator.';form.reset();}catch(error){result.textContent=error.message;}finally{send.disabled=false;}});
        report.append(form);article.append(report);publishedRoot.append(article);
      }
      offset+=data.length;more.hidden=data.length<20;message.textContent=window.TESTIMONY_COPY.readerSuccess;
    }catch{message.textContent=window.TESTIMONY_COPY.readerError;}
    finally{more.disabled=false;}
  }
  more.addEventListener('click',load);await load();
})();
