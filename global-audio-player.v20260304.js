(() => {
  const STORAGE_KEY = 'rosary_audio_context';
  const DOCK_STATE_KEY = 'rosary_audio_dock_state';
  const DOCK_POS_KEY = 'rosary_audio_dock_position';
  const VOICE_PREF_KEY = 'rosary_audio_voice_pref';
  const STORY_PAGE = /\/story(\.html)?$/.test(window.location.pathname || '');
  const ROSARY_PAGE = /\/(mysteries\/|rosary-|mystery-meditation|saint-charbel-prayers)/.test(window.location.pathname || '');
  const VOICE_TESTIMONY_PAGE = /\/voice-testimony(\.html)?$/.test(window.location.pathname || '');

  const readJSON = key => {
    try {
      return JSON.parse(localStorage.getItem(key) || '{}');
    } catch (_) {
      return {};
    }
  };

  const writeJSONMerge = (key, next) => {
    try {
      const prev = readJSON(key);
      localStorage.setItem(key, JSON.stringify({ ...prev, ...next }));
    } catch (_) {
      // no-op
    }
  };

  const readContext = () => readJSON(STORAGE_KEY);
  const writeContext = next => writeJSONMerge(STORAGE_KEY, next);
  const readDockState = () => readJSON(DOCK_STATE_KEY);
  const writeDockState = next => writeJSONMerge(DOCK_STATE_KEY, next);
  const readDockPosition = () => readJSON(DOCK_POS_KEY);
  const writeDockPosition = next => {
    try {
      localStorage.setItem(DOCK_POS_KEY, JSON.stringify(next));
    } catch (_) {
      // no-op
    }
  };

  window.RosaryAudioContext = {
    set(data = {}) {
      writeContext(data);
      window.dispatchEvent(new CustomEvent('rosary-audio-context-updated'));
    },
    clear() {
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch (_) {
        // no-op
      }
      window.dispatchEvent(new CustomEvent('rosary-audio-context-updated'));
    }
  };

  const root = document.createElement('aside');
  root.className = 'floating-audio';
  root.setAttribute('aria-live', 'polite');
  root.innerHTML = `
    <div class="floating-audio-head">
      <button id="floating-audio-close" type="button" class="floating-audio-close" aria-label="Close player">Close</button>
      <p class="floating-audio-label">Audio In Progress</p>
      <button id="floating-audio-minimize" type="button" class="floating-audio-minimize" aria-label="Minimize player">Minimize</button>
    </div>
    <p id="floating-audio-mode" class="floating-audio-mode">Guided Audio</p>
    <p id="floating-audio-mystery-progress" class="floating-audio-mystery-progress" hidden></p>
    <p id="floating-audio-prayer-name" class="floating-audio-prayer-name"></p>
    <p id="floating-audio-title" class="floating-audio-title">Rosary narration</p>
    <p id="floating-audio-subtitle" class="floating-audio-subtitle">Active step</p>
    <p id="floating-audio-status" class="floating-audio-status">Playing</p>
    <div class="floating-audio-step-progress" aria-hidden="true">
      <span id="floating-audio-step-fill" class="floating-audio-step-fill"></span>
    </div>
    <p id="floating-audio-step-label" class="floating-audio-step-label" hidden></p>
    <p id="floating-audio-countdown" class="floating-audio-countdown" hidden></p>
    <div class="floating-audio-progress" aria-hidden="true">
      <span id="floating-audio-progress-fill" class="floating-audio-progress-fill"></span>
    </div>
    <p id="floating-audio-elapsed" class="floating-audio-elapsed" hidden></p>
    <div class="floating-audio-voice-row">
      <label for="floating-audio-voice">Voice</label>
      <select id="floating-audio-voice" class="floating-audio-voice" aria-label="Select narration voice"></select>
    </div>
    <div class="floating-audio-actions">
      <button id="floating-audio-back" type="button" class="btn subtle" aria-label="Previous step" title="Previous step">&lt;&lt;</button>
      <button id="floating-audio-toggle" type="button" class="btn subtle">Pause</button>
      <button id="floating-audio-skip" type="button" class="btn subtle" aria-label="Next step" title="Next step">&gt;&gt;</button>
      <a id="floating-audio-open" class="btn primary" href="/rosary-visual-guide">Open Mystery</a>
    </div>
    <button id="floating-audio-auto-prayer" type="button" class="btn subtle floating-audio-auto-prayer-btn">Auto Prayer: Disabled</button>
    <button id="floating-audio-next" type="button" class="btn primary floating-audio-next">Next</button>
    <button id="floating-audio-mobile-toggle" type="button" class="floating-audio-mobile-toggle">Expand</button>
  `;
  document.body.appendChild(root);

  const titleEl = document.getElementById('floating-audio-title');
  const subtitleEl = document.getElementById('floating-audio-subtitle');
  const modeEl = document.getElementById('floating-audio-mode');
  const statusEl = document.getElementById('floating-audio-status');
  const mysteryProgressEl = document.getElementById('floating-audio-mystery-progress');
  const prayerNameEl = document.getElementById('floating-audio-prayer-name');
  const stepFillEl = document.getElementById('floating-audio-step-fill');
  const stepBarEl = root.querySelector('.floating-audio-step-progress');
  const stepLabelEl = document.getElementById('floating-audio-step-label');
  const countdownEl = document.getElementById('floating-audio-countdown');
  const progressFillEl = document.getElementById('floating-audio-progress-fill');
  const progressBarEl = document.querySelector('.floating-audio-progress');
  const elapsedEl = document.getElementById('floating-audio-elapsed');
  const voiceEl = document.getElementById('floating-audio-voice');
  const voiceRowEl = document.querySelector('.floating-audio-voice-row');
  const closeEl = document.getElementById('floating-audio-close');
  const backEl = document.getElementById('floating-audio-back');
  const toggleEl = document.getElementById('floating-audio-toggle');
  const skipEl = document.getElementById('floating-audio-skip');
  const openEl = document.getElementById('floating-audio-open');
  const autoPrayerEl = document.getElementById('floating-audio-auto-prayer');
  const nextEl = document.getElementById('floating-audio-next');
  const minimizeEl = document.getElementById('floating-audio-minimize');
  const mobileToggleEl = document.getElementById('floating-audio-mobile-toggle');

  if (STORY_PAGE) {
    if (autoPrayerEl) autoPrayerEl.style.display = 'none';
    if (openEl) openEl.style.display = 'none';
    if (nextEl) nextEl.style.display = 'none';
    if (voiceRowEl) voiceRowEl.style.display = 'none';
  }

  // Force prerecorded-audio-only mode to avoid browser TTS fallback.
  const supportsSpeech = false;
  const getNarrationController = () => window.RosaryNarrationController || null;
  let restoreInFlight = false;
  let lastRestoreText = '';
  let dragging = false;
  let dragOffsetX = 0;
  let dragOffsetY = 0;
  let minimized = Boolean(readDockState().minimized);
  let mobileCollapsed = readDockState().mobileCollapsed !== false;
  let lastRestoreKey = '';
  let lastRestoreAt = 0;
  let availableVoices = [];

  const clearLegacySpeechMode = () => {
    const context = readContext();
    if (context.mode !== 'speech') {
      return;
    }
    writeContext({
      mode: 'prerendered',
      playing: false,
      paused: false,
      completed: false,
      text: '',
      pausedAt: null,
      totalPausedMs: 0,
      estimatedDurationMs: 0
    });
  };
  clearLegacySpeechMode();

  const readVoicePref = () => {
    try {
      return JSON.parse(localStorage.getItem(VOICE_PREF_KEY) || '{}');
    } catch (_) {
      return {};
    }
  };

  const writeVoicePref = voice => {
    if (!voice) return;
    try {
      localStorage.setItem(VOICE_PREF_KEY, JSON.stringify({
        name: voice.name || '',
        lang: voice.lang || ''
      }));
    } catch (_) {
      // no-op
    }
  };

  const defaultMysteryHref = () => (window.location.pathname.includes('/mysteries/')
    ? '../rosary-visual-guide'
    : './rosary-visual-guide');

  const isMobileViewport = () => window.innerWidth <= 680;
  const isStoryPage = () => STORY_PAGE;
  const getPageUiProfile = context => {
    if (isStoryPage() || context?.source === 'storybook' || context?.stage === 'Storybook') {
      return {
        showBack: true,
        showToggle: true,
        showSkip: true,
        showOpen: false,
        showAutoPrayer: false,
        showNext: false,
        showCountdown: false,
        showSubtitle: true,
        showProgress: true,
        showVoiceSelect: false
      };
    }
    return {
      showBack: true,
      showToggle: true,
      showSkip: true,
      showOpen: true,
      showAutoPrayer: true,
      showNext: true,
      showCountdown: true,
      showSubtitle: true,
      showProgress: true,
      showVoiceSelect: true
    };
  };

  const setHidden = hidden => {
    root.classList.toggle('on', !hidden);
  };

  const setDockState = ({ paused, status }) => {
    toggleEl.textContent = paused ? 'Play' : 'Pause';
    toggleEl.setAttribute('aria-label', paused ? 'Play narration' : 'Pause narration');
    statusEl.textContent = status;
  };

  const setAutoPrayerButton = enabled => {
    autoPrayerEl.textContent = enabled ? 'Auto Prayer: Enabled' : 'Auto Prayer: Disabled';
    autoPrayerEl.classList.toggle('is-enabled', Boolean(enabled));
  };

  const formatCountdown = seconds => {
    const whole = Math.max(0, Number(seconds) || 0);
    const mins = Math.floor(whole / 60);
    const secs = whole % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  const renderCountdown = context => {
    if (!countdownEl) {
      return;
    }
    const timerEnabled = Boolean(context.autoTimerEnabled);
    const countdown = Math.max(0, Number(context.autoTimerCountdown) || 0);

    if (!timerEnabled) {
      countdownEl.hidden = true;
      countdownEl.classList.remove('is-armed');
      countdownEl.textContent = '';
      nextEl.classList.remove('is-countdown');
      nextEl.removeAttribute('data-countdown-label');
      return;
    }

    countdownEl.hidden = false;
    if (countdown > 0) {
      countdownEl.classList.remove('is-armed');
      countdownEl.innerHTML = `Prayer Countdown <strong>${formatCountdown(countdown)}</strong>`;
      nextEl.classList.add('is-countdown');
      nextEl.setAttribute('data-countdown-label', `⏳ ${formatCountdown(countdown)}`);
      return;
    }

    countdownEl.classList.add('is-armed');
    countdownEl.textContent = 'Auto timer armed: starts after narration';
    nextEl.classList.remove('is-countdown');
    nextEl.removeAttribute('data-countdown-label');
  };

  const setDockPosition = ({ left, top }) => {
    root.style.left = `${Math.max(8, left)}px`;
    root.style.top = `${Math.max(8, top)}px`;
    root.style.right = 'auto';
    root.style.bottom = 'auto';
  };

  const applySavedPosition = () => {
    const pos = readDockPosition();
    if (typeof pos.left === 'number' && typeof pos.top === 'number') {
      setDockPosition({ left: pos.left, top: pos.top });
    }
  };

  const renderContext = context => {
    const ui = { ...(context?.ui || {}), ...getPageUiProfile(context) };
    const enabled = (value, fallback = true) => value === undefined ? fallback : Boolean(value);
    const isRosary = context.source === 'rosary';

    titleEl.textContent = context.title || 'Rosary narration';
    subtitleEl.textContent = context.stage || context.subtitle || 'Active step';
    openEl.href = context.url || defaultMysteryHref();
    openEl.textContent = ui.openLabel || 'Open Mystery';
    setAutoPrayerButton(Boolean(context.autoPrayerVoiceEnabled));
    renderCountdown(context);

    if (isRosary && context.mysteryNum && context.totalMysteries) {
      mysteryProgressEl.textContent = `Mystery ${context.mysteryNum} of ${context.totalMysteries} — ${context.mysterySetLabel || ''}`;
      mysteryProgressEl.hidden = false;
    } else {
      mysteryProgressEl.hidden = true;
    }

    if (isRosary && context.prayerLabel) {
      prayerNameEl.textContent = context.prayerLabel;
      prayerNameEl.hidden = false;
      titleEl.hidden = true;
      subtitleEl.hidden = true;
    } else {
      prayerNameEl.hidden = true;
      titleEl.hidden = false;
      subtitleEl.hidden = !enabled(ui.showSubtitle, true);
    }

    if (isRosary && typeof context.stepIndex === 'number' && context.totalSteps) {
      const step = context.stepIndex + 1;
      const total = context.totalSteps;
      const ratio = Math.round((step / total) * 100);
      stepFillEl.style.width = `${ratio}%`;
      stepLabelEl.textContent = `Step ${step} of ${total}`;
      stepLabelEl.hidden = false;
      stepBarEl.hidden = false;
    } else {
      stepBarEl.hidden = true;
      stepLabelEl.hidden = true;
    }

    backEl.hidden = !enabled(ui.showBack, true);
    toggleEl.hidden = !enabled(ui.showToggle, true);
    skipEl.hidden = !enabled(ui.showSkip, true);
    openEl.hidden = !enabled(ui.showOpen, true);
    autoPrayerEl.hidden = !enabled(ui.showAutoPrayer, true);
    nextEl.hidden = !enabled(ui.showNext, true);
    if (voiceRowEl) {
      voiceRowEl.hidden = true;
    }
    countdownEl.hidden = countdownEl.hidden || !enabled(ui.showCountdown, true);
    progressBarEl.hidden = !enabled(ui.showProgress, true);

    const mode = context.mode === 'speech'
      ? 'Voice'
      : context.mode === 'prerendered'
        ? 'Guided Audio'
      : context.mode === 'storybook'
        ? 'Story Audio'
      : context.mode === 'studio'
        ? 'Studio Track'
        : context.mode === 'ambient'
          ? 'Ambient'
          : 'Audio';
    modeEl.textContent = mode;
  };

  const renderMinimized = () => {
    root.classList.toggle('is-minimized', minimized);
    minimizeEl.textContent = minimized ? 'Expand' : 'Minimize';
    minimizeEl.setAttribute('aria-label', minimized ? 'Expand player' : 'Minimize player');
  };

  const renderMobilePill = () => {
    const active = isMobileViewport() && mobileCollapsed;
    root.classList.toggle('is-mobile-pill', active);
    mobileToggleEl.textContent = active ? 'Expand Player' : 'Collapse';
    mobileToggleEl.setAttribute('aria-label', active ? 'Expand audio player' : 'Collapse audio player');
  };

  const renderCompletion = completed => {
    root.classList.toggle('is-complete', completed);
    if (completed) {
      if (isMobileViewport() && mobileCollapsed) {
        mobileCollapsed = false;
        writeDockState({ mobileCollapsed: false });
        renderMobilePill();
      }
      setDockState({ paused: true, status: 'Step complete. Continue with Next.' });
      progressFillEl.style.width = '100%';
    }
  };

  const isSpeakingActive = () => supportsSpeech && (window.speechSynthesis.speaking || window.speechSynthesis.paused);

  const selectCalmVoice = () => {
    if (!supportsSpeech) return null;
    const voices = window.speechSynthesis.getVoices() || [];
    if (!voices.length) return null;
    const selected = getSelectedVoice();
    if (selected) {
      return selected;
    }
    const englishVoices = voices.filter(voice => (voice.lang || '').toLowerCase().startsWith('en'));
    const candidates = englishVoices.length ? englishVoices : voices;
    const calmPriority = [
      'serena',
      'samantha',
      'ava',
      'aria',
      'allison',
      'karen',
      'moira',
      'victoria',
      'siri'
    ];

    let best = null;
    let bestScore = -1;
    candidates.forEach((voice) => {
      const name = (voice.name || '').toLowerCase();
      let score = 0;
      const calmIndex = calmPriority.findIndex(token => name.includes(token));
      if (calmIndex >= 0) {
        score += 100 - calmIndex;
      }
      if (name.includes('female') || name.includes('woman')) {
        score += 20;
      }
      if (name.includes('natural') || name.includes('neural') || name.includes('enhanced')) {
        score += 8;
      }
      if (name.includes('english') || name.includes('en-us')) {
        score += 4;
      }
      if (!best || score > bestScore) {
        best = voice;
        bestScore = score;
      }
    });

    return best || candidates[0] || voices[0];
  };

  const findVoiceByPref = (voices, pref) => {
    if (!voices?.length || !pref?.name) return null;
    return voices.find(voice => voice.name === pref.name && (!pref.lang || voice.lang === pref.lang)) || null;
  };

  const renderVoiceOptions = () => {
    if (!voiceEl) return;
    if (!supportsSpeech) {
      voiceEl.disabled = true;
      voiceEl.innerHTML = '<option value="">Browser voice unavailable</option>';
      return;
    }

    availableVoices = window.speechSynthesis.getVoices() || [];
    if (!availableVoices.length) {
      voiceEl.disabled = true;
      voiceEl.innerHTML = '<option value="">Loading voices...</option>';
      return;
    }

    const pref = readVoicePref();
    const fallback = selectCalmVoice();
    const selected = findVoiceByPref(availableVoices, pref) || fallback || availableVoices[0];

    voiceEl.disabled = false;
    voiceEl.innerHTML = '';
    availableVoices.forEach((voice, index) => {
      const option = document.createElement('option');
      option.value = String(index);
      option.textContent = `${voice.name} (${voice.lang})`;
      if (selected && voice.name === selected.name && voice.lang === selected.lang) {
        option.selected = true;
      }
      voiceEl.appendChild(option);
    });

    if (selected) {
      writeVoicePref(selected);
      writeContext({ voiceName: selected.name, voiceLang: selected.lang });
    }
  };

  const getSelectedVoice = () => {
    if (!supportsSpeech) return null;
    const voices = window.speechSynthesis.getVoices() || [];
    if (!voices.length) return null;

    if (voiceEl && voiceEl.value !== '' && !Number.isNaN(Number(voiceEl.value))) {
      const idx = Number(voiceEl.value);
      if (voices[idx]) {
        return voices[idx];
      }
    }

    return findVoiceByPref(voices, readVoicePref());
  };

  const estimateDurationMsFromText = text => {
    if (!text) {
      return 0;
    }
    const words = String(text).trim().split(/\s+/).filter(Boolean).length;
    return Math.max(3500, Math.round((words / 130) * 60 * 1000));
  };

  const formatElapsed = ms => {
    const totalSec = Math.floor(ms / 1000);
    const m = Math.floor(totalSec / 60);
    const s = totalSec % 60;
    return `${m}:${String(s).padStart(2, '0')}`;
  };

  const updateProgress = context => {
    const countdown = Number(context.autoTimerCountdown || 0);
    const duration = Number(context.autoTimerDuration || 0);
    if (countdown > 0 && duration > 0) {
      progressBarEl?.classList.add('is-countdown');
      const ratio = Math.max(0, Math.min(1, countdown / duration));
      progressFillEl.style.width = `${Math.round(ratio * 100)}%`;
      if (elapsedEl) {
        elapsedEl.textContent = `Next step in ${countdown}s`;
        elapsedEl.hidden = false;
      }
      return;
    }

    progressBarEl?.classList.remove('is-countdown');
    if (!context?.mode || (context.mode !== 'speech' && context.mode !== 'prerendered' && context.mode !== 'storybook')) {
      progressFillEl.style.width = '0%';
      if (elapsedEl) elapsedEl.hidden = true;
      return;
    }
    if (context.completed) {
      progressFillEl.style.width = '100%';
      if (elapsedEl) {
        elapsedEl.textContent = 'Completed';
        elapsedEl.hidden = false;
      }
      return;
    }
    if (!context.playing) {
      progressFillEl.style.width = '0%';
      if (elapsedEl) elapsedEl.hidden = true;
      return;
    }

    const estimatedDuration = Number(context.estimatedDurationMs) || estimateDurationMsFromText(context.text);
    const startedAt = Number(context.startedAt) || Date.now();
    const totalPausedMs = Number(context.totalPausedMs || 0);
    const pauseAnchor = context.paused && context.pausedAt ? Number(context.pausedAt) : Date.now();
    const elapsed = Math.max(0, pauseAnchor - startedAt - totalPausedMs);
    const ratio = Math.min(1, elapsed / Math.max(1, estimatedDuration));
    progressFillEl.style.width = `${Math.round(ratio * 100)}%`;
    if (elapsedEl) {
      elapsedEl.textContent = estimatedDuration > 0
        ? `${formatElapsed(elapsed)} / ${formatElapsed(estimatedDuration)}`
        : formatElapsed(elapsed);
      elapsedEl.hidden = false;
    }
  };

  const restoreSpeechFromContext = context => {
    if (!supportsSpeech || restoreInFlight || !context?.text) {
      return;
    }
    if (context.mode !== 'speech') {
      return;
    }
    if (!context.playing || context.paused || context.completed) {
      return;
    }
    if (window.speechSynthesis.speaking || window.speechSynthesis.pending) {
      return;
    }
    if (lastRestoreText === context.text) {
      return;
    }

    const restoreKey = `${context.title || ''}::${context.stage || ''}::${context.text || ''}`;
    const now = Date.now();
    if (lastRestoreKey === restoreKey && now - lastRestoreAt < 15000) {
      return;
    }

    restoreInFlight = true;
    try {
      const utterance = new SpeechSynthesisUtterance(context.text);
      utterance.rate = 0.8;
      utterance.pitch = 0.95;
      utterance.volume = 0.92;
      utterance.lang = 'en-US';
      utterance.voice = selectCalmVoice();
      utterance.onstart = () => {
        restoreInFlight = false;
      };
      utterance.onend = () => {
        restoreInFlight = false;
        writeContext({ playing: false, paused: false, completed: true });
        window.dispatchEvent(new CustomEvent('rosary-audio-context-updated'));
      };
      utterance.onerror = () => {
        restoreInFlight = false;
      };
      lastRestoreKey = restoreKey;
      lastRestoreAt = now;
      lastRestoreText = context.text;
      window.speechSynthesis.speak(utterance);
    } catch (_) {
      restoreInFlight = false;
      // no-op
    }
  };

  const isRosarySourceContext = ctx => ctx?.source === 'rosary' || (ctx?.mode === 'prerendered' && !ctx?.source);
  const isStorySourceContext = ctx => ctx?.source === 'storybook';
  const isContextPageRelevant = ctx => {
    if (isRosarySourceContext(ctx)) return ROSARY_PAGE;
    if (isStorySourceContext(ctx)) return STORY_PAGE;
    return true;
  };

  const renderSpeechState = () => {
    const context = readContext();

    if (!isContextPageRelevant(context) && !isSpeakingActive()) {
      if (context.playing || context.paused) {
        writeContext({ playing: false, paused: false, completed: false });
      }
      setHidden(true);
      return;
    }

    if (!isSpeakingActive()) {
      restoreSpeechFromContext(context);
    }

    const active = isSpeakingActive();
    let samePage = true;
    if (context?.url) {
      try {
        const contextPath = new URL(context.url, window.location.href).pathname;
        samePage = contextPath === window.location.pathname;
      } catch (_) {
        samePage = true;
      }
    }
    const contextActive = (context.mode === 'speech' || context.mode === 'prerendered' || context.mode === 'storybook')
      && (context.playing || context.paused || context.completed)
      && (samePage || active || Boolean(context.persistentAcrossPages));

    if (!active && !contextActive) {
      setHidden(true);
      return;
    }

    setHidden(false);
    renderContext(context);
    renderMinimized();
    renderMobilePill();
    updateProgress(context);
    renderCompletion(Boolean(context.completed));

    if (context.completed) {
      return;
    }

    const paused = active ? window.speechSynthesis.paused : Boolean(context.paused);
    if (paused) {
      setDockState({ paused: true, status: 'Paused narration' });
    } else if (active) {
      setDockState({ paused: false, status: 'Playing narration' });
    } else {
      setDockState({ paused: false, status: 'Resuming narration...' });
    }
  };

  minimizeEl.addEventListener('click', () => {
    minimized = !minimized;
    writeDockState({ minimized });
    renderMinimized();
  });

  mobileToggleEl.addEventListener('click', () => {
    mobileCollapsed = !mobileCollapsed;
    writeDockState({ mobileCollapsed });
    renderMobilePill();
  });

  const goPrevious = () => {
    const context = readContext();
    const selector = context?.ui?.prevSelector;
    if (selector) {
      const target = document.querySelector(selector);
      if (target && typeof target.click === 'function') {
        target.click();
        writeContext({ completed: false });
        window.dispatchEvent(new CustomEvent('rosary-audio-context-updated'));
        return;
      }
    }

    const controller = getNarrationController();
    if (controller?.previous) {
      controller.previous();
      writeContext({ completed: false });
      window.dispatchEvent(new CustomEvent('rosary-audio-context-updated'));
      return;
    }

    const pagePrev = document.getElementById('prev-step');
    if (pagePrev && typeof pagePrev.click === 'function') {
      pagePrev.click();
      writeContext({ completed: false });
      window.dispatchEvent(new CustomEvent('rosary-audio-context-updated'));
    }
  };

  const goNext = () => {
    const context = readContext();
    const selector = context?.ui?.nextSelector;
    if (selector) {
      const target = document.querySelector(selector);
      if (target && typeof target.click === 'function') {
        target.click();
        writeContext({ completed: false });
        window.dispatchEvent(new CustomEvent('rosary-audio-context-updated'));
        return;
      }
    }

    const controller = getNarrationController();
    if (controller?.next) {
      controller.next();
      writeContext({ completed: false });
      window.dispatchEvent(new CustomEvent('rosary-audio-context-updated'));
      return;
    }

    const pageNext = document.getElementById('next-step');
    if (pageNext && typeof pageNext.click === 'function') {
      pageNext.click();
      writeContext({ completed: false });
      window.dispatchEvent(new CustomEvent('rosary-audio-context-updated'));
      return;
    }

    window.location.href = context?.ui?.openHref || context.url || defaultMysteryHref();
  };

  backEl.addEventListener('click', goPrevious);
  skipEl.addEventListener('click', goNext);
  nextEl.addEventListener('click', goNext);

  root.addEventListener('pointerdown', event => {
    if (window.innerWidth <= 740) {
      return;
    }
    const target = event.target;
    if (target.closest('button') || target.closest('a') || target.closest('.floating-audio-actions')) {
      return;
    }

    dragging = true;
    root.classList.add('is-dragging');
    const rect = root.getBoundingClientRect();
    dragOffsetX = event.clientX - rect.left;
    dragOffsetY = event.clientY - rect.top;
    root.setPointerCapture(event.pointerId);
  });

  root.addEventListener('pointermove', event => {
    if (!dragging) {
      return;
    }
    const left = Math.max(8, Math.min(window.innerWidth - root.offsetWidth - 8, event.clientX - dragOffsetX));
    const top = Math.max(8, Math.min(window.innerHeight - root.offsetHeight - 8, event.clientY - dragOffsetY));
    setDockPosition({ left, top });
  });

  root.addEventListener('pointerup', event => {
    if (!dragging) {
      return;
    }
    dragging = false;
    root.classList.remove('is-dragging');
    root.releasePointerCapture(event.pointerId);
    const rect = root.getBoundingClientRect();
    const snapLeft = rect.left + rect.width / 2 < window.innerWidth / 2 ? 8 : window.innerWidth - rect.width - 8;
    const snapTop = rect.top + rect.height / 2 < window.innerHeight / 2 ? 8 : window.innerHeight - rect.height - 8;
    setDockPosition({ left: snapLeft, top: snapTop });
    writeDockPosition({ left: snapLeft, top: snapTop });
  });

  root.addEventListener('pointercancel', () => {
    dragging = false;
    root.classList.remove('is-dragging');
  });

  toggleEl.addEventListener('click', () => {
    const context = readContext();
    const controller = getNarrationController();
    if (controller?.togglePause && (context.mode === 'prerendered' || context.source === 'storybook')) {
      controller.togglePause();
      setTimeout(renderSpeechState, 40);
      return;
    }

    if (!supportsSpeech) {
      return;
    }

    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
      const context = readContext();
      const pauseDuration = context.pausedAt ? Math.max(0, Date.now() - Number(context.pausedAt)) : 0;
      writeContext({
        mode: 'speech',
        playing: true,
        paused: false,
        completed: false,
        pausedAt: null,
        totalPausedMs: Number(context.totalPausedMs || 0) + pauseDuration
      });
      setDockState({ paused: false, status: 'Playing narration' });
    } else if (window.speechSynthesis.speaking) {
      window.speechSynthesis.pause();
      writeContext({ mode: 'speech', playing: true, paused: true, pausedAt: Date.now(), completed: false });
      setDockState({ paused: true, status: 'Paused narration' });
    } else {
      if (context.mode === 'speech' && context.text) {
        writeContext({ playing: true, paused: false, pausedAt: null, completed: false });
        restoreSpeechFromContext({ ...context, playing: true, paused: false, completed: false });
        setDockState({ paused: false, status: 'Resuming narration...' });
      }
    }

    setTimeout(renderSpeechState, 40);
  });

  closeEl.addEventListener('click', () => {
    const context = readContext();
    const controller = getNarrationController();

    // Stop any prerendered narration controller
    if (controller?.stop && (context.mode === 'prerendered' || context.mode === 'storybook')) {
      controller.stop();
    }

    // Cancel browser speech synthesis if active
    if (supportsSpeech) {
      window.speechSynthesis.cancel();
    }

    // Notify storybook (or any page) to reset its own reading state
    window.dispatchEvent(new CustomEvent('rosary-audio-close'));

    // Clear context and hide the dock
    writeContext({ mode: context.mode || 'prerendered', playing: false, paused: false, completed: false });
    lastRestoreText = '';
    setHidden(true);
  });

  autoPrayerEl?.addEventListener('click', () => {
    const context = readContext();
    const enabled = !Boolean(context.autoPrayerVoiceEnabled);
    writeContext({
      mode: context.mode || 'prerendered',
      playing: Boolean(context.playing || context.paused || context.completed),
      paused: Boolean(context.paused),
      completed: Boolean(context.completed),
      autoPrayerVoiceEnabled: enabled
    });
    setAutoPrayerButton(enabled);
    const pageToggle = document.getElementById('auto-prayer-toggle');
    if (pageToggle) {
      pageToggle.checked = enabled;
      pageToggle.dispatchEvent(new Event('change', { bubbles: true }));
    } else {
      window.dispatchEvent(new CustomEvent('rosary-audio-context-updated'));
    }
  });

  voiceEl?.addEventListener('change', () => {
    if (!supportsSpeech) return;
    const voices = window.speechSynthesis.getVoices() || [];
    const selected = voices[Number(voiceEl.value)] || null;
    if (!selected) return;
    writeVoicePref(selected);
    writeContext({
      voiceName: selected.name,
      voiceLang: selected.lang
    });
    window.dispatchEvent(new CustomEvent('rosary-audio-context-updated'));
  });

  window.addEventListener('rosary-audio-context-updated', renderSpeechState);
  window.addEventListener('focus', renderSpeechState);
  if (supportsSpeech) {
    window.speechSynthesis.onvoiceschanged = () => {
      renderVoiceOptions();
      renderSpeechState();
    };
  }
  window.addEventListener('resize', () => {
    if (window.innerWidth <= 740) {
      root.style.left = '';
      root.style.top = '';
      root.style.right = '';
      root.style.bottom = '';
      renderMobilePill();
      return;
    }
    applySavedPosition();
    renderMobilePill();
  });

  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      renderSpeechState();
    }
  });

  document.addEventListener('keydown', event => {
    if (!root.classList.contains('on')) {
      return;
    }

    const target = event.target;
    if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT' || target.isContentEditable)) {
      return;
    }

    if (event.code === 'Space') {
      event.preventDefault();
      toggleEl.click();
    }
    if (event.code === 'Escape') {
      closeEl.click();
    }
  });

  applySavedPosition();
  renderVoiceOptions();
  renderMinimized();
  renderMobilePill();
  renderSpeechState();
  setInterval(renderSpeechState, 500);
})();
