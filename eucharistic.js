// Static semantic links are the source of truth; motion never gates access to content.
(() => { if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('.euch-places a').forEach(link => link.addEventListener('click', event => {
    const target = document.querySelector(link.getAttribute('href'));
    if (!target) return;
    event.preventDefault(); target.scrollIntoView({behavior:'smooth', block:'center'});
    history.replaceState(null, '', link.getAttribute('href'));
  }));
})();
