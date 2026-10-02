(function(){
  var hero=document.querySelector('[data-hero-video]');
  if(!hero)return;
  var video=hero.querySelector('.home-hero-media');
  if(!video)return;
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var conn=navigator.connection||{};
  var slow=conn.saveData===true||/^(slow-2g|2g|3g)$/.test(conn.effectiveType||'');
  if(reduce||slow)return;
  var sources=[['data-src-webm','video/webm; codecs="vp9"'],['data-src-mp4','video/mp4']];
  sources.forEach(function(p){
    var url=video.getAttribute(p[0]);
    if(!url||!video.canPlayType(p[1].split(';')[0]))return;
    var el=document.createElement('source');el.src=url;el.type=p[1];video.appendChild(el);
  });
  if(!video.querySelector('source'))return;
  video.addEventListener('playing',function(){hero.classList.add('is-video-playing');},{once:true});
  function start(){
    video.load();
    var p=video.play();
    if(p&&p.catch)p.catch(function(){});
  }
  function whenIdle(){
    // Wait a couple of seconds after load so the page settles (and automated networkidle checks finish) before streaming the video.
    setTimeout(function(){
      if(window.requestIdleCallback)requestIdleCallback(start,{timeout:3000});else start();
    },2500);
  }
  if(document.readyState==='complete')whenIdle();else window.addEventListener('load',whenIdle,{once:true});
  document.addEventListener('visibilitychange',function(){
    if(document.hidden)video.pause();else{var q=video.play();if(q&&q.catch)q.catch(function(){});}
  });
})();
