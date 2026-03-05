(function () {
  const cfg = window.TESTIMONY_CONFIG || {};
  const root = document.getElementById('testimony-list');
  const empty = document.getElementById('testimony-empty');

  if (!root) return;

  const supabase = window.supabase?.createClient(cfg.supabaseUrl || '', cfg.supabaseAnonKey || '');
  if (!supabase || !cfg.supabaseUrl || cfg.supabaseUrl.includes('YOUR_PROJECT')) {
    empty.textContent = 'Connect Supabase in testimony-config.js to load published testimonies.';
    return;
  }

  const escapeHtml = (str) =>
    String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');

  const renderCard = (row) => {
    const el = document.createElement('article');
    el.className = 'card testimony-card';
    const date = row.event_date || row.published_at || row.created_at || '';
    el.innerHTML = [
      '<p class="kicker">Approved Testimony</p>',
      `<h3>${escapeHtml(row.full_name || 'Anonymous')}</h3>`,
      `<p class="source-meta">${escapeHtml([row.country, row.parish, date].filter(Boolean).join(' • '))}</p>`,
      `<p>${escapeHtml(row.testimony_text || '').replace(/\n/g, '<br>')}</p>`
    ].join('');
    return el;
  };

  (async () => {
    const { data, error } = await supabase
      .from('testimonies')
      .select('full_name,country,parish,event_date,testimony_text,published_at,created_at')
      .eq('status', 'approved')
      .order('published_at', { ascending: false })
      .limit(200);

    if (error) {
      empty.textContent = `Could not load testimonies: ${error.message}`;
      return;
    }

    if (!data || data.length === 0) {
      empty.textContent = 'No approved testimonies published yet.';
      return;
    }

    empty.remove();
    data.forEach((row) => root.appendChild(renderCard(row)));
  })();
})();
