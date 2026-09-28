// Static semantic links are the source of truth; motion never gates access to content.
(() => { if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('.euch-places a').forEach(link => link.addEventListener('click', event => {
    const target = document.querySelector(link.getAttribute('href'));
    if (!target) return;
    event.preventDefault(); target.scrollIntoView({behavior:'smooth', block:'center'});
    history.replaceState(null, '', link.getAttribute('href'));
  }));
})();
(() => {
  const buttons = document.querySelectorAll('.euch-filter button');
  const cards = document.querySelectorAll('.euch-grid > [data-country]');
  buttons.forEach(button => button.addEventListener('click', () => {
    const country = button.dataset.filter;
    buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    let visible = 0;
    cards.forEach(card => {
      const show = country === 'all' || card.dataset.country === country;
      card.hidden = !show;
      if (show) visible++;
    });
    document.querySelector('.euch-empty').hidden = visible > 0;
  }));
})();
