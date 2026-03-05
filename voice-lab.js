const grid = document.getElementById('voice-grid');
const feedbackEl = document.getElementById('feedback');
const copyBtn = document.getElementById('copy-feedback');
const browserVoiceEl = document.getElementById('browser-voice');
const browserTextEl = document.getElementById('browser-text');
const playBrowserBtn = document.getElementById('play-browser');
const stopBrowserBtn = document.getElementById('stop-browser');

let activeAudio = null;
let voices = [];

const stopActiveAudio = () => {
  if (activeAudio) {
    activeAudio.pause();
    activeAudio.currentTime = 0;
    activeAudio = null;
  }
};

const renderVoiceCards = () => {
  grid.innerHTML = '';
  voices.forEach(voice => {
    const card = document.createElement('article');
    card.className = 'voice-card';
    card.innerHTML = `
      <h3>${voice.label}</h3>
      <p class="voice-tag">Base: ${voice.voice} | Rate: ${voice.rate} wpm | ${voice.duration_sec}s</p>
      <label class="voice-tag" for="score-${voice.id}">Score (1-10)</label>
      <input id="score-${voice.id}" class="voice-score" type="number" min="1" max="10" placeholder="8" />
      <div class="voice-actions">
        <button type="button" class="btn subtle" data-play="${voice.id}">Play Sample</button>
        <button type="button" class="btn subtle" data-stop="${voice.id}">Stop</button>
      </div>
    `;
    grid.appendChild(card);
  });
};

const loadOptions = async () => {
  try {
    const response = await fetch('./media/voice-lab/options.json', { cache: 'no-store' });
    voices = response.ok ? await response.json() : [];
  } catch (_) {
    voices = [];
  }
  renderVoiceCards();
};

grid.addEventListener('click', event => {
  const play = event.target.closest('[data-play]');
  const stop = event.target.closest('[data-stop]');

  if (play) {
    const key = play.getAttribute('data-play');
    stopActiveAudio();
    const voice = voices.find(v => v.id === key);
    if (!voice?.file) {
      return;
    }
    const audio = new Audio(voice.file);
    activeAudio = audio;
    audio.onended = () => {
      if (activeAudio === audio) {
        activeAudio = null;
      }
    };
    audio.play().catch(() => {});
    return;
  }

  if (stop) {
    stopActiveAudio();
  }
});

const browserVoices = () => (window.speechSynthesis?.getVoices() || []).filter(v => (v.lang || '').toLowerCase().startsWith('en'));

const renderBrowserVoices = () => {
  const list = browserVoices();
  browserVoiceEl.innerHTML = '';
  list.forEach((voice, index) => {
    const option = document.createElement('option');
    option.value = String(index);
    option.textContent = `${voice.name} (${voice.lang})`;
    browserVoiceEl.appendChild(option);
  });
};

renderBrowserVoices();
if ('speechSynthesis' in window) {
  window.speechSynthesis.onvoiceschanged = renderBrowserVoices;
}

playBrowserBtn.addEventListener('click', () => {
  if (!('speechSynthesis' in window)) {
    return;
  }
  window.speechSynthesis.cancel();
  const options = browserVoices();
  const voice = options[Number(browserVoiceEl.value)] || options[0] || null;
  const utterance = new SpeechSynthesisUtterance(browserTextEl.value || 'Remain peaceful and attentive before God in this mystery.');
  utterance.voice = voice;
  utterance.rate = 0.86;
  utterance.pitch = 0.95;
  utterance.volume = 0.92;
  utterance.lang = 'en-US';
  window.speechSynthesis.speak(utterance);
});

stopBrowserBtn.addEventListener('click', () => {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
});

copyBtn.addEventListener('click', async () => {
  const scores = voices.map(v => {
    const val = document.getElementById(`score-${v.id}`)?.value || '';
    return `${v.label}: ${val || 'n/a'}`;
  }).join('\n');

  const payload = `Voice Lab Feedback\n${scores}\n\nNotes:\n${feedbackEl.value || '(none)'}`;

  try {
    await navigator.clipboard.writeText(payload);
    copyBtn.textContent = 'Copied';
    setTimeout(() => {
      copyBtn.textContent = 'Copy Feedback + Scores';
    }, 1500);
  } catch (_) {
    copyBtn.textContent = 'Copy Failed';
  }
});

loadOptions();
