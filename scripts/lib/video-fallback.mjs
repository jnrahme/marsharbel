// Static links survive blocked scripts, offline players and unsupported errors.
export function renderVideoFallback(copy, id, context) {
  if (!/^[\w-]{11}$/.test(id) || !/^\.\/[a-z0-9/-]+$/.test(context)) throw new Error('Invalid video fallback target');
  const escape = value => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;');
  return `<div class="video-fallback" data-video-id="${id}">
            <p class="video-status" role="status" aria-live="polite" aria-atomic="true">${escape(copy['video.help'])}</p>
            <p class="video-links"><a href="https://www.youtube.com/watch?v=${id}" target="_blank" rel="noopener noreferrer">${escape(copy['video.original'])}</a> <a href="${context}">${escape(copy['video.read'])}</a></p>
            <template data-error="100">${escape(copy['video.unavailable'])}</template>
            <template data-error="101 150">${escape(copy['video.restricted'])}</template>
            <template data-error="153">${escape(copy['video.referrer'])}</template>
            <template data-error="2 5">${escape(copy['video.generic'])}</template>
          </div>`;
}
