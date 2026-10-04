/* Authored same-page language control. Unavailable choices never change the page. */
(function () {

 var api=window.SC_SAME_PAGE,manifest=window.SC_SAME_PAGE_MANIFEST;
 if(!api||!manifest)return;
 if(!document.getElementById('sc-language-css')){var css=document.createElement('link');css.id='sc-language-css';css.rel='stylesheet';css.href='/same-page-switcher.css';document.head.appendChild(css)}
 var current=api.locate(manifest,location.pathname);
 var actual=current?current.language:document.documentElement.lang;
 var copy=(window.SC_SAME_PAGE_COPY||{})[actual];
 if(!copy)return; // Never show unreviewed English UI as a translated catalog fallback.
 var host=document.getElementById('sc-language-switcher');
 if(!host){host=document.createElement('div');host.id='sc-language-switcher';host.className='lang-switcher'+' '+'notranslate';
  var slot=document.querySelector('.lang-switcher-slot'),nav=document.querySelector('.topbar'+ ' '+'.nav,header'+' '+'.masthead');
  if(slot)slot.replaceWith(host);else if(nav)nav.appendChild(host);else document.body.appendChild(host);
 }
 host.replaceChildren();
 var label=document.createElement('label');label.htmlFor='sc-language-select';label.textContent=copy.language;
 var select=document.createElement('select');select.id='sc-language-select';select.setAttribute('aria-label',copy.choose);select.setAttribute('aria-describedby','sc-language-helper');
 var names=copy.names;
 if(!names)return;
 var blocked=false;
 manifest.languages.forEach(function(lang){var option=document.createElement('option');option.value=lang;option.dir=actual==='ar'?'rtl':'ltr';var r=api.resolve(manifest,location.href,lang,actual);option.disabled=!r.available;option.textContent=names[lang]+(!r.available?' ('+copy.suffix+')':'');if(!r.available)blocked=true;select.appendChild(option)});
 select.value=actual;
 var helper=document.createElement('span');helper.id='sc-language-helper';helper.className='sc-language-helper';helper.textContent=blocked?copy.helper:'';
 var status=document.createElement('span');status.id='sc-language-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');status.setAttribute('aria-atomic','true');status.className='sc-language-status';
 function refuse(){var x=scrollX,y=scrollY;select.value=actual;status.textContent=copy.unavailable;window.scrollTo(x,y);}
 function request(lang){var r=api.resolve(manifest,location.href,lang,actual);if(!r.available){refuse();return false;}if(r.reason==='same-language'){select.value=actual;return true;}try{localStorage.setItem('sc_last_explicit_language',lang)}catch(_){}location.assign(r.href);return true;}
 select.addEventListener('change',function(){request(select.value)});
 host.append(label,select);
 var feedback=document.createElement('div');feedback.className='sc-language-feedback';feedback.append(helper,status);(host.closest('header')||document.querySelector('main')||host).appendChild(feedback);
 function showFeedback(){if(!blocked)return;var box=select.getBoundingClientRect();feedback.classList.add('is-open');var header=host.closest('header');feedback.style.top=(Math.max(box.bottom,header?header.getBoundingClientRect().bottom:box.bottom)+8)+'px';feedback.style.left=Math.max(8,Math.min(box.left,innerWidth-Math.min(320,innerWidth-16)-8))+'px';}
 function hideFeedback(){feedback.classList.remove('is-open');}
 select.addEventListener('focus',showFeedback);select.addEventListener('pointerdown',showFeedback);select.addEventListener('blur',hideFeedback);select.addEventListener('keydown',function(e){if(e.keyCode===27)hideFeedback()});window.addEventListener('scroll',hideFeedback,{passive:true});window.addEventListener('resize',hideFeedback);
 if(typeof window.__scInstallApp==='function'&&!document.getElementById('sc-install-app-btn')){var install=document.createElement('button');install.id='sc-install-app-btn';install.type='button';install.className='sc-install-app-btn';install.textContent=window.__scInstallLabel;install.addEventListener('click',window.__scInstallApp);host.after(install)}
 // Old stored preferences are observed only to explain an unavailable request.
 // They never redirect, rewrite ordinary links, or relabel document content.
 var query=new URLSearchParams(location.search).get('lang'),stored='';try{stored=localStorage.getItem('sc_lang_pref')||''}catch(_){}
 var requested=query||stored;if(requested&&requested!==actual&&!api.resolve(manifest,location.href,requested,actual).available)refuse();
 document.querySelectorAll('nav.locale-nav:not([data-locale-section-navigation])').forEach(function(nav){
  nav.querySelectorAll('.sc-language-helper,.sc-unavailable-suffix').forEach(function(n){n.remove()});
  nav.querySelectorAll('a[hreflang]').forEach(function(a){var lang=a.getAttribute('hreflang');var r=api.resolve(manifest,location.href,lang,actual);a.setAttribute('data-language-switch','');if(r.available){a.href=r.href;a.setAttribute('hreflang',lang);a.removeAttribute('aria-disabled');a.removeAttribute('tabindex');a.removeAttribute('aria-label');a.textContent=copy.names[lang]||a.textContent;a.removeAttribute('lang')}else{a.textContent=copy.names[lang]||a.textContent;a.removeAttribute('href');a.setAttribute('aria-disabled','true');a.setAttribute('tabindex','-1');a.setAttribute('aria-label',(a.textContent||'')+' ('+copy.suffix+')');a.removeAttribute('lang');var hint=document.createElement('span');hint.className='sc-unavailable-suffix';hint.lang=actual;hint.textContent=' ('+copy.suffix+')';a.appendChild(hint)}});
  nav.setAttribute('aria-describedby','sc-language-helper');
 });
 document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-language-switch]');if(!a)return;e.preventDefault();request(a.getAttribute('hreflang'))});
 window.SC_LANGUAGE_SWITCH={request:request,actualLanguage:actual};
 // Back/forward restores the page's own language; no preference redirect runs.
 window.addEventListener('pageshow',function(){select.value=actual});
})();
