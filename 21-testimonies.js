(function () {
  const cfg = window.TESTIMONY_CONFIG || {};
  const root = document.getElementById('testimony-list');
  const empty = document.getElementById('testimony-empty');

  if (!root) return;

  const baseline = Array.isArray(window.TESTIMONY_BASELINE) ? window.TESTIMONY_BASELINE : [];
  const escapeHtmlEarly = (str) =>
    String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');

  const supabaseReady = window.supabase && cfg.supabaseUrl && !cfg.supabaseUrl.includes('YOUR_PROJECT');
  if (!supabaseReady) {
    if (!baseline.length) {
      empty.textContent = 'Connect Supabase in testimony-config.js to load published testimonies.';
      return;
    }
    empty.textContent = 'First entries: documented, recorded miracles, retold in the person\'s own words with their sources.';
    baseline.forEach((entry) => {
      const el = document.createElement('article');
      el.className = 'card testimony-card';
      el.innerHTML = [
        '<p class="kicker">Recorded Testimony</p>',
        `<h3>${escapeHtmlEarly(entry.name)}</h3>`,
        `<p class="source-meta">${escapeHtmlEarly(entry.meta)}</p>`,
        `<p>${escapeHtmlEarly(entry.text)}</p>`,
        `<p class="source-meta"><a href="${escapeHtmlEarly(entry.url)}" target="_blank" rel="noopener">${escapeHtmlEarly(entry.source)}</a></p>`
      ].join('');
      root.appendChild(el);
    });
    return;
  }

  const supabase = window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseAnonKey);

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
