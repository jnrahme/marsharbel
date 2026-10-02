(function(){
  var root=document.querySelector('[data-letters-globe]');
  if(!root)return;
  var canvas=root.querySelector('canvas');
  var panel=root.querySelector('[data-globe-panel]');
  var chips=root.querySelector('[data-globe-chips]');
  var SPR='./media/letters/flags-sprite.webp?v=1',DATA='./media/letters/letters-countries.json?v=1',WORLD='./media/letters/world-110m.json?v=1';
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var conn=navigator.connection||{};
  var saver=conn.saveData===true||/^(slow-2g|2g)$/.test(conn.effectiveType||'');
  var countries=[],land=[],sprite=null,active=null,rot=[-30,24],drag=null,spin=!reduce,raf=0,visible=false,size=0,dpr=1,ctx=canvas.getContext&&canvas.getContext('2d');
  function rad(d){return d*Math.PI/180}
  function project(lon,lat){
    var l=rad(lon+rot[0]),p=rad(lat),r=rad(rot[1]);
    var cp=Math.cos(p),x=cp*Math.sin(l),y=Math.sin(p),z=cp*Math.cos(l);
    var y2=y*Math.cos(r)-z*Math.sin(r),z2=y*Math.sin(r)+z*Math.cos(r);
    return [x,y2,z2];
  }
  function decode(topo,obj){
    var t=topo.transform,sc=t.scale,tr=t.translate;
    var arcs=topo.arcs.map(function(a){var x=0,y=0;return a.map(function(p){x+=p[0];y+=p[1];return [x*sc[0]+tr[0],y*sc[1]+tr[1]]})});
    function ring(idx){var out=[];idx.forEach(function(i){var a=i<0?arcs[~i].slice().reverse():arcs[i];out=out.concat(out.length?a.slice(1):a)});return out}
    var polys=[];
    obj.geometries.forEach(function(g){
      if(g.type==='Polygon')polys.push(g.arcs.map(ring));
      else if(g.type==='MultiPolygon')g.arcs.forEach(function(p){polys.push(p.map(ring))});
    });
    return polys;
  }
  function resize(){
    var w=Math.min(root.clientWidth,720);size=w;dpr=Math.min(window.devicePixelRatio||1,2);
    canvas.width=Math.round(w*dpr);canvas.height=Math.round(w*dpr);canvas.style.width=w+'px';canvas.style.height=w+'px';
    draw();
  }
  function draw(){
    if(!ctx)return;
    var s=size*dpr,R=s*0.42,c=s/2;
    ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,s,s);
    var halo=ctx.createRadialGradient(c,c,R*0.96,c,c,R*1.22);
    halo.addColorStop(0,'rgba(214,170,98,.34)');halo.addColorStop(1,'rgba(214,170,98,0)');
    ctx.fillStyle=halo;ctx.beginPath();ctx.arc(c,c,R*1.22,0,7);ctx.fill();
    var sea=ctx.createRadialGradient(c-R*.35,c-R*.4,R*.1,c,c,R);
    sea.addColorStop(0,'#2c4a5e');sea.addColorStop(.6,'#142a3a');sea.addColorStop(1,'#0a1722');
    ctx.fillStyle=sea;ctx.beginPath();ctx.arc(c,c,R,0,7);ctx.fill();
    ctx.save();ctx.beginPath();ctx.arc(c,c,R,0,7);ctx.clip();
    ctx.strokeStyle='rgba(239,230,214,.07)';ctx.lineWidth=dpr;
    for(var lo=-180;lo<180;lo+=30)line(function(i){return [lo,-80+i*8]},21,c,R);
    for(var la=-60;la<=60;la+=30)line(function(i){return [-180+i*12,la]},31,c,R);
    land.forEach(function(poly){
      poly.forEach(function(ring,ri){
        if(ri>0)return;
        ctx.beginPath();var started=false,any=false,zs=0;
        for(var i=0;i<ring.length;i++){
          var p=project(ring[i][0],ring[i][1]);zs+=p[2];
          var px=c+p[0]*R,py=c-p[1]*R;
          if(!started){ctx.moveTo(px,py);started=true}else ctx.lineTo(px,py);
          if(p[2]>0)any=true;
        }
        if(!any)return;
        ctx.closePath();
        var lit=Math.max(0,Math.min(1,zs/ring.length+.55));
        ctx.fillStyle='rgba('+Math.round(150+60*lit)+','+Math.round(128+50*lit)+','+Math.round(92+30*lit)+',.95)';
        ctx.fill();ctx.strokeStyle='rgba(20,14,8,.35)';ctx.lineWidth=.6*dpr;ctx.stroke();
      });
    });
    ctx.restore();
    var shade=ctx.createRadialGradient(c-R*.4,c-R*.45,R*.2,c,c,R*1.02);
    shade.addColorStop(0,'rgba(255,240,210,.14)');shade.addColorStop(.55,'rgba(0,0,0,0)');shade.addColorStop(1,'rgba(4,8,12,.62)');
    ctx.fillStyle=shade;ctx.beginPath();ctx.arc(c,c,R,0,7);ctx.fill();
    countries.forEach(function(k){pin(k,c,R)});
  }
  function line(fn,n,c,R){
    ctx.beginPath();var pen=false;
    for(var i=0;i<=n;i++){var q=fn(i),p=project(q[0],q[1]);
      if(p[2]<0){pen=false;continue}
      var x=c+p[0]*R,y=c-p[1]*R;if(!pen){ctx.moveTo(x,y);pen=true}else ctx.lineTo(x,y)}
    ctx.stroke();
  }
  function pin(k,c,R){
    var p=project(k.lon,k.lat);k._p=null;
    if(p[2]<0.08||k.f==null)return;
    var bx=c+p[0]*R,by=c-p[1]*R,h=R*(k.letters?.1:.066),w=h*1.333,fade=Math.min(1,(p[2]-.08)*5);
    var ty=by-h*1.45;
    ctx.globalAlpha=fade;
    ctx.fillStyle='rgba(0,0,0,.35)';ctx.beginPath();ctx.ellipse(bx,by+1.5*dpr,w*.22,w*.08,0,0,7);ctx.fill();
    ctx.strokeStyle='#efe6d6';ctx.lineWidth=1.4*dpr;ctx.beginPath();ctx.moveTo(bx,by);ctx.lineTo(bx,ty+h);ctx.stroke();
    if(sprite&&sprite.complete&&sprite.naturalWidth){ctx.drawImage(sprite,(k.f%12)*80,Math.floor(k.f/12)*60,80,60,bx,ty,w,h)}else{ctx.fillStyle='#d6aa62';ctx.fillRect(bx,ty,w,h)}
    ctx.lineWidth=(active===k?2.5:1)*dpr;ctx.strokeStyle=active===k?'#ffd98a':'rgba(239,230,214,.65)';ctx.strokeRect(bx,ty,w,h);
    ctx.globalAlpha=1;
    k._p={x:bx/dpr,y:ty/dpr,w:w/dpr,h:(by-ty)/dpr,z:p[2]};
  }
  function frame(){
    raf=0;
    if(spin&&!drag&&visible&&!document.hidden){rot[0]-=.18;draw()}
    if(spin&&visible)raf=requestAnimationFrame(frame);
  }
  function kick(){if(!raf&&spin&&visible)raf=requestAnimationFrame(frame)}
  function show(k){
    active=k;
    if(chips)[].forEach.call(chips.children,function(b){b.setAttribute('aria-pressed',b.dataset.name===k.name?'true':'false')});
    panel.hidden=false;panel.innerHTML='';
    var h=document.createElement('h3');h.textContent=k.name;panel.append(h);
    if(k.letters){
      var n=document.createElement('p');n.textContent=k.letters.length+(k.letters.length===1?' letter':' letters')+' on this page';panel.append(n);
      var ul=document.createElement('ul');
      k.letters.forEach(function(l){var li=document.createElement('li');var b=document.createElement('strong');b.textContent=l.who;li.append(b,document.createTextNode(l.note?' - '+l.note:''));ul.append(li)});
      panel.append(ul);
    }else{var q=document.createElement('p');q.textContent='Letters to Saint Charbel have come from '+k.name+'.';panel.append(q)}
    var cur=rot[0],target=-k.lon,t0=performance.now();
    spin=false;
    (function turn(now){
      var t=Math.min(1,((now||performance.now())-t0)/(reduce?1:900)),e=1-Math.pow(1-t,3);
      rot[0]=cur+(target-cur)*e;rot[1]=rot[1]+((k.lat*.8)-rot[1])*e;draw();
      if(t<1)requestAnimationFrame(turn);
    })(t0);
  }
  function hit(x,y){
    var best=null;
    for(var i=0;i<countries.length;i++){var p=countries[i]._p;if(p&&x>=p.x-5&&x<=p.x+p.w+5&&y>=p.y-5&&y<=p.y+p.h+5&&(!best||p.z>best._p.z))best=countries[i]}
    return best;
  }
  function bind(){
    canvas.addEventListener('pointerdown',function(e){drag={x:e.clientX,y:e.clientY,r0:rot.slice(),moved:false};canvas.setPointerCapture(e.pointerId)});
    canvas.addEventListener('pointermove',function(e){
      if(!drag)return;var dx=e.clientX-drag.x,dy=e.clientY-drag.y;
      if(Math.abs(dx)+Math.abs(dy)>4)drag.moved=true;
      rot[0]=drag.r0[0]+dx*.4;rot[1]=Math.max(-70,Math.min(70,drag.r0[1]-dy*.3));draw();
    });
    canvas.addEventListener('pointerup',function(e){
      var d=drag;drag=null;
      if(d&&!d.moved){var r=canvas.getBoundingClientRect(),k=hit(e.clientX-r.left,e.clientY-r.top);if(k)show(k)}
    });
    canvas.addEventListener('pointermove',function(e){if(drag)return;var r=canvas.getBoundingClientRect();canvas.style.cursor=hit(e.clientX-r.left,e.clientY-r.top)?'pointer':'grab'});
    window.addEventListener('resize',resize);
  }
  function chipsFor(){
    if(!chips)return;chips.innerHTML='';
    countries.forEach(function(k){
      var b=document.createElement('button');b.type='button';b.className='globe-chip';b.dataset.name=k.name;b.setAttribute('aria-pressed','false');
      if(k.f!=null){var f=document.createElement('span');f.className='globe-flag';f.setAttribute('aria-hidden','true');f.style.backgroundPosition='-'+(k.f%12)*24+'px -'+Math.floor(k.f/12)*18+'px';b.append(f)}
      b.append(document.createTextNode(k.name));
      b.addEventListener('click',function(){show(k);if(k.f!=null&&canvas.scrollIntoView&&!k._p)canvas.scrollIntoView({block:'nearest'})});chips.append(b);
    });
  }
  function start(){
    Promise.all([fetch(DATA).then(function(r){return r.json()}),(saver?Promise.resolve(null):fetch(WORLD).then(function(r){return r.json()}))]).then(function(res){
      countries=res[0];chipsFor();root.classList.add('has-chips');
      if(!res[1]||!ctx){root.classList.add('is-static');return}
      land=decode(res[1],res[1].objects.countries);
      sprite=new Image();sprite.onload=draw;sprite.src=SPR;
      root.classList.add('is-live');bind();resize();
      if('IntersectionObserver' in window)new IntersectionObserver(function(es){visible=es[0].isIntersecting;kick()}).observe(canvas);else{visible=true;kick()}
    }).catch(function(){root.classList.add('is-static');try{chipsFor()}catch(e){}});
  }
  if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){if(es[0].isIntersecting){io.disconnect();start()}},{rootMargin:'300px'});io.observe(root)}else start();
})();
