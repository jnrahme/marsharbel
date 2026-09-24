// Read Aloud: speaks the page's main content with the browser's built-in
// voices. One button (.read-aloud-btn) toggles speak/stop. No dependencies.
(function () {
  var btn = document.querySelector('.read-aloud-btn');
  if (!btn || !('speechSynthesis' in window)) return;
  var speaking = false;

  function pageText() {
    var main = document.querySelector('main');
    if (!main) return '';
    return main.innerText.replace(/\s+/g, ' ').trim();
  }

  function stop() {
    window.speechSynthesis.cancel();
    speaking = false;
    btn.textContent = 'Read Aloud';
    btn.setAttribute('aria-pressed', 'false');
  }

  btn.addEventListener('click', function () {
    if (speaking) { stop(); return; }
    var text = pageText();
    if (!text) return;
    var utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.onend = utterance.onerror = function () { stop(); };
    window.speechSynthesis.speak(utterance);
    speaking = true;
    btn.textContent = 'Stop Reading';
    btn.setAttribute('aria-pressed', 'true');
  });

  document.addEventListener('visibilitychange', function () {
    if (document.hidden && speaking) stop();
  });
})();
