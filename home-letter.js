(async function () {
  const form = document.getElementById('home-letter-form');
  if (!form) return;
  const config = document.getElementById('sc-home-labels');
  const labels = config ? JSON.parse(config.textContent) : await fetch('/locales/en/home-copy.json').then(response => {
    if (!response.ok) throw new Error('HOME_CATALOG_UNAVAILABLE');
    return response.json();
  });
  const storageError = labels['home.runtime.letter.storageError'];
  if (typeof storageError !== 'string') throw new Error('HOME_LETTER_STORAGE_KEY_MISSING');
  const draft = document.getElementById('home-letter-draft');
  const error = document.getElementById('home-letter-error');
  try {
    const saved = sessionStorage.getItem('saint_charbel_letter_draft');
    if (saved && !draft.value) draft.value = saved.slice(0, 7000);
  } catch { /* Still allow a fresh draft without browser storage. */ }
  const grow = () => {
    draft.style.height = 'auto';
    draft.style.height = `${Math.max(draft.scrollHeight, 160)}px`;
  };
  form.querySelector('button[type=submit]').disabled = false;
  draft.addEventListener('input', grow);
  grow();
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    try {
      sessionStorage.setItem('saint_charbel_letter_draft', draft.value);
      window.location.assign('/submit-testimony');
    } catch {
      error.textContent = storageError;
      error.hidden = false;
    }
  });
})();
