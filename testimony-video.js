(function (root) {
  // Accept ordinary video links only; never use a submitted URL as iframe src.
  function idFromUrl(value) {
    if (typeof value !== 'string' || value.length > 500) return null;
    let url;
    try { url = new URL(value.trim()); } catch { return null; }
    if (url.protocol !== 'https:' || url.username || url.password || url.port || url.hash) return null;
    const host = url.hostname.toLowerCase();
    const parts = url.pathname.split('/').filter(Boolean);
    if (parts.some(part => part === '.' || part === '..')) return null;
    let id = null;
    if (host === 'youtu.be' && parts.length === 1) id = parts[0];
    else if (['youtube.com','www.youtube.com','m.youtube.com','youtube-nocookie.com','www.youtube-nocookie.com'].includes(host)) {
      if (url.pathname === '/watch') id = url.searchParams.get('v');
      else if (parts.length === 2 && ['shorts','live','embed'].includes(parts[0])) id = parts[1];
    }
    return /^[A-Za-z0-9_-]{11}$/.test(id || '') ? id : null;
  }
  function embedUrl(id) {
    return /^[A-Za-z0-9_-]{11}$/.test(id || '') ? `https://www.youtube-nocookie.com/embed/${id}` : null;
  }
  root.TestimonyVideo = { idFromUrl, embedUrl };
})(typeof window === 'undefined' ? globalThis : window);
