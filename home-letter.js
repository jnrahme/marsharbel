(function () {
  const form = document.getElementById('home-letter-form');
  if (!form) return;
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
      window.location.assign('./submit-testimony');
    } catch {
      error.textContent = 'This browser could not carry your letter to the next page. Keep a copy before continuing.';
      error.hidden = false;
    }
  });
})();
