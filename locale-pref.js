document.addEventListener("click",function(e){
  var a=e.target&&e.target.closest?e.target.closest("a[hreflang]"):null;
  if(!a)return;
  var l=(a.getAttribute("hreflang")||"").toLowerCase();
  if(l==="x-default")l="en";
  try{localStorage.setItem("sc_lang_pref",l)}catch(_){}
});
