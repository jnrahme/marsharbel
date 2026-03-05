const mysteries = window.ROSARY_MYSTERIES || {};
const params = new URLSearchParams(window.location.search);
const key = window.MYSTERY_KEY || params.get('m') || 'luminous_1';
const basePath = window.MYSTERY_BASE || './';
const audioVersion = window.ROSARY_AUDIO_VERSION || '20260302-intro-audio-fix';
const mystery = mysteries[key] || mysteries.luminous_1;
const textLibrary = window.ROSARY_MYSTERY_LIBRARY || {};
const mysteryText = textLibrary[key] || null;
const clipManifestPath = `${basePath}media/rosary/manifest.json`;

const orderedKeys = [
  'joyful_1', 'joyful_2', 'joyful_3', 'joyful_4', 'joyful_5',
  'luminous_1', 'luminous_2', 'luminous_3', 'luminous_4', 'luminous_5',
  'sorrowful_1', 'sorrowful_2', 'sorrowful_3', 'sorrowful_4', 'sorrowful_5',
  'glorious_1', 'glorious_2', 'glorious_3', 'glorious_4', 'glorious_5'
];
const mysterySets = {
  joyful: ['joyful_1', 'joyful_2', 'joyful_3', 'joyful_4', 'joyful_5'],
  luminous: ['luminous_1', 'luminous_2', 'luminous_3', 'luminous_4', 'luminous_5'],
  sorrowful: ['sorrowful_1', 'sorrowful_2', 'sorrowful_3', 'sorrowful_4', 'sorrowful_5'],
  glorious: ['glorious_1', 'glorious_2', 'glorious_3', 'glorious_4', 'glorious_5']
};
const mysterySetLabel = {
  joyful: 'Joyful Mysteries',
  luminous: 'Luminous Mysteries',
  sorrowful: 'Sorrowful Mysteries',
  glorious: 'Glorious Mysteries'
};
const ROSARY_SESSION_KEY = 'rosary_full_session';
const currentSet = key.split('_')[0];

const detectTodaySet = () => {
  const day = new Date().getDay();
  if (day === 1 || day === 6) return 'joyful';
  if (day === 2 || day === 5) return 'sorrowful';
  if (day === 4) return 'luminous';
  return 'glorious';
};

const readRosarySession = () => {
  try {
    return JSON.parse(localStorage.getItem(ROSARY_SESSION_KEY) || 'null');
  } catch (_) {
    return null;
  }
};

const writeRosarySession = data => {
  try {
    localStorage.setItem(ROSARY_SESSION_KEY, JSON.stringify(data));
  } catch (_) {
    // no-op
  }
};

const clearRosarySession = () => {
  try {
    localStorage.removeItem(ROSARY_SESSION_KEY);
  } catch (_) {
    // no-op
  }
};

let rosarySession = readRosarySession();

const keyToSlug = mysteryKey => mysteryKey.replace('_', '-');
const mysteryUrl = mysteryKey => `${basePath}mysteries/${keyToSlug(mysteryKey)}.html`;
const activeIndex = Math.max(0, orderedKeys.indexOf(key));
const getActiveLang = () => {
  const lang = (new URLSearchParams(window.location.search).get('lang') || '').toLowerCase();
  return lang && lang !== 'en' ? lang : '';
};
const normalizeReflectionText = value =>
  {
    let text = String(value || '')
      .replace(/^Pause(?:\s+for)?\s+[^.?!]*[.?!]\s*/i, '')
      .replace(/^(See|Picture|Watch|Imagine|Notice)\s+/i, 'Reflect on ')
      .replace(/^Hear\s+/i, 'Reflect on the words: ')
      .trim();

    const replacements = [
      [/\bJesus enter\b/g, 'Jesus enters'],
      [/\bJesus receive\b/g, 'Jesus receives'],
      [/\bJesus lead\b/g, 'Jesus leads'],
      [/\bJesus handed over\b/g, 'Jesus being handed over'],
      [/\bJesus stripped and nailed\b/g, 'Jesus being stripped and nailed'],
      [/\bGabriel arrive\b/g, 'Gabriel arriving'],
      [/\bHim ask\b/g, 'Jesus asks'],
      [/\bHim fall and rise\b/g, 'Jesus falls and rises'],
      [/\bHim entrust\b/g, 'Jesus entrusts'],
      [/\bHim cry\b/g, 'Jesus cries'],
      [/\bHim bow\b/g, 'Jesus bows'],
      [/\bHim bound\b/g, 'Jesus bound'],
      [/\bHim pray\b/g, 'Jesus prays'],
      [/\bsurrender His spirit\b/g, 'surrenders His spirit'],
      [/\bthe angel strengthen\b/g, 'the angel strengthens'],
      [/\bMary meet\b/g, 'Mary meets'],
      [/\bVeronica offer\b/g, 'Veronica offers'],
      [/\bHis face shine\b/g, 'His face shines'],
      [/\bthem press\b/g, 'soldiers press'],
      [/\bthe words:\s*Him\b/g, 'the words: Jesus']
    ];

    replacements.forEach(([pattern, next]) => {
      text = text.replace(pattern, next);
    });

    text = text
      .replace(/\bthe words:\s*the blows and feel the violence of sin\b/i, 'the words: the blows and the violence of sin')
      .replace(/\bReflect on soldiers mock\b/i, 'Reflect on soldiers mocking');

    return text;
  };

const titleEl = document.getElementById('mystery-main-title');
const subEl = document.getElementById('mystery-main-sub');
const imageEl = document.getElementById('mystery-hero-image');
const heroSection = document.querySelector('.meditation-hero');
const stageBadge = document.getElementById('stage-badge');
const stageTitle = document.getElementById('stage-title');
const stageText = document.getElementById('stage-text');
const stepCounter = document.getElementById('step-counter');
const progressEl = document.getElementById('bead-progress');

const prevMysteryButton = document.getElementById('prev-mystery');
const nextMysteryButton = document.getElementById('next-mystery');
const mysteryPicker = document.getElementById('mystery-picker');
const topMysteryControls = mysteryPicker?.closest('.meditation-top-controls') || null;
const backToListButton = topMysteryControls?.querySelector('a.btn[href*="rosary-visual-guide"]') || null;

if (backToListButton) {
  backToListButton.remove();
}

const heroMeta = document.createElement('article');
heroMeta.className = 'card mystery-hero-meta';
heroMeta.innerHTML = `
  <p class="mystery-hero-progress" id="mystery-hero-progress">Mystery 1 of ${orderedKeys.length}</p>
  <p class="mystery-hero-ref" id="mystery-hero-ref">Scripture focus</p>
`;
if (heroSection) {
  const controlsStart = heroSection.querySelector('.meditation-top-controls');
  if (controlsStart) {
    heroSection.insertBefore(heroMeta, controlsStart);
  } else {
    heroSection.appendChild(heroMeta);
  }
}
const mysteryHeroProgressEl = document.getElementById('mystery-hero-progress');
const mysteryHeroRefEl = document.getElementById('mystery-hero-ref');

const prevButton = document.getElementById('prev-step');
const nextButton = document.getElementById('next-step');
const playButton = document.getElementById('play-audio');
const pauseButton = document.getElementById('pause-audio');
const stopButton = document.getElementById('stop-audio');
const studioPlayButton = document.getElementById('play-studio');
const studioPauseButton = document.getElementById('pause-studio');
const soundButton = document.getElementById('toggle-sound');
const soundStatus = document.getElementById('sound-status');
const studioAudio = document.getElementById('studio-audio');
const autoTimerSeconds = document.getElementById('auto-timer-seconds');
const autoTimerToggle = document.getElementById('auto-timer-toggle');
const autoTimerCountdownEl = document.getElementById('auto-timer-countdown');
const meditationContent = document.querySelector('.meditation-content');
const meditationActions = document.querySelector('.meditation-actions');
const stepNavLabel = document.getElementById('step-nav-label');
const stepNavBar = document.getElementById('step-nav-bar');
const stepNavFill = document.getElementById('step-nav-fill');

const contextPanel = document.createElement('section');
contextPanel.className = 'mystery-source-panel';
contextPanel.innerHTML = `
  <p class="mystery-source-kicker">Mystery Text Companion</p>
  <h3 class="mystery-source-heading">Explanation, Full Reading, and Reflection</h3>
  <article class="mystery-source-card">
    <h4>Explanation</h4>
    <p id="mystery-explanation"></p>
  </article>
  <article class="mystery-source-card">
    <h4 id="mystery-reading-title">Full Reading</h4>
    <p id="mystery-reading"></p>
  </article>
  <article class="mystery-source-card mystery-source-reflection">
    <h4>Reflection</h4>
    <p id="mystery-reflection"></p>
  </article>
  <a class="btn subtle mystery-source-link" href="${basePath}rosary-minibook.html">Open Rosary Minibook</a>
`;
meditationContent?.appendChild(contextPanel);
const mysteryExplanationEl = document.getElementById('mystery-explanation');
const mysteryReadingTitleEl = document.getElementById('mystery-reading-title');
const mysteryReadingEl = document.getElementById('mystery-reading');
const mysteryReflectionEl = document.getElementById('mystery-reflection');

if (!mystery) {
  stageTitle.textContent = 'Mystery not found';
  stageText.textContent = 'Please return to the Rosary guide and choose a mystery.';
} else {
  titleEl.textContent = mystery.title;
  subEl.textContent = `${mystery.day} | Fruit: ${mystery.fruit}`;
  imageEl.src = mystery.image;
  imageEl.alt = mystery.title;
}

if (mysteryHeroProgressEl) {
  mysteryHeroProgressEl.textContent = `Mystery ${activeIndex + 1} of ${orderedKeys.length}`;
}
if (mysteryHeroRefEl) {
  const scriptureRef = mysteryText?.readingTitle || '';
  mysteryHeroRefEl.textContent = scriptureRef ? `Scripture focus: ${scriptureRef}` : 'Scripture focus: Rosary meditation';
}

const scriptureRef = mysteryText?.readingTitle || 'Gospel reading';
const scriptureReading = mysteryText?.reading || 'Remain in silence and attention before the Lord.';

const lectureText = mystery
  ? `Reflect on ${mystery.title}. ${scriptureReading} Ask for the grace of ${mystery.fruit}.`
  : 'Meditate on the mystery with attention and peace.';

const initialStage = params.get('stage');
const isLastMysteryInActiveSession = Boolean(
  rosarySession?.active
  && Array.isArray(rosarySession.sequence)
  && rosarySession.sequence.length
  && rosarySession.sequence[rosarySession.sequence.length - 1] === key
);
const includeEndPrayersStage = initialStage === 'end' || isLastMysteryInActiveSession;

const baseStages = [
  {
    kind: 'intro_prayers',
    clipStep: null,
    badge: 'Intro Prayers',
    title: 'Begin The Rosary',
    text: "Pray the Apostles' Creed, one Our Father, three Hail Marys for faith, hope, and charity, and one Glory Be."
  },
  {
    kind: 'lecture',
    clipStep: 1,
    badge: 'Lecture',
    title: 'Receive The Mystery',
    text: lectureText
  },
  {
    kind: 'our_father',
    clipStep: 2,
    badge: 'Scripture Prompt',
    title: 'Listen To The Word',
    text: `Scripture reading: ${scriptureRef}. ${scriptureReading} Pray one Our Father with attention.`
  },
  ...(mystery
    ? mystery.steps.map((text, index) => ({
        kind: 'hail_mary',
        clipStep: index + 3,
        badge: `Meditation ${index + 1}`,
        title: `Meditation`,
        text: `Meditation ${index + 1}. ${normalizeReflectionText(text)} Speak to Christ now about what you need in this mystery.`
      }))
    : []),
  {
    kind: 'decade_closing',
    clipStep: 13,
    badge: 'Decade Closing',
    title: 'Complete This Decade',
    text: 'Pray the Glory Be and the Fatima Prayer.'
  }
];

const endPrayersStage = {
    kind: 'end_prayers',
    clipStep: null,
    badge: 'End Prayers',
    title: 'Close The Rosary',
    text: 'Pray the Hail Holy Queen and the concluding Rosary prayer, then finish with the Sign of the Cross.'
};

const stages = includeEndPrayersStage
  ? [...baseStages, endPrayersStage]
  : baseStages;

// Default to the first mystery step. Intro/end are explicit via URL params.
let stageIndex = 1;
if (initialStage === 'intro') {
  stageIndex = 0;
} else if (initialStage === 'end') {
  stageIndex = Math.max(0, stages.length - 1);
}
let autoTimerId = null;
let autoRunning = false;
let autoRemainingSeconds = 0;
let autoTimerDuration = 0;
let autoCountdownStageIndex = -1;
let dotsTimerId = null;
let dotsFrame = 0;
let autoPrayerVoiceEnabled = false;
let churchMusicEnabled = false;
let clipManifest = null;
let clipAvailable = false;
let clipAudio = null;
let clipPreload = null;
let prayerClipAudio = null;
let activeNarrationMode = 'prerendered';
let hasUserStartedPlayback = false;
let playbackRequestId = 0;
let playbackPending = false;

const prayerTexts = {
  apostles_creed: "I believe in God, the Father almighty, Creator of Heaven and earth, and in Jesus Christ, His only Son, our Lord; who was conceived by the Holy Spirit, born of the Virgin Mary, suffered under Pontius Pilate, was crucified, died, and was buried. He descended into hell; on the third day He rose again from the dead; He ascended into Heaven, and sits at the right hand of God the Father almighty; from thence He shall come to judge the living and the dead. I believe in the Holy Spirit, the holy Catholic Church, the communion of saints, the forgiveness of sins, the resurrection of the body, and life everlasting. Amen.",
  hail_mary: "Hail Mary, full of grace, the Lord is with thee. Blessed art thou among women, and blessed is the fruit of thy womb, Jesus. Holy Mary, Mother of God, pray for us sinners, now and at the hour of our death. Amen.",
  our_father: "Our Father, who art in heaven, hallowed be Thy name; Thy kingdom come; Thy will be done on earth as it is in heaven. Give us this day our daily bread; and forgive us our trespasses, as we forgive those who trespass against us; and lead us not into temptation, but deliver us from evil. Amen.",
  glory_be: "Glory be to the Father, and to the Son, and to the Holy Spirit. As it was in the beginning, is now, and ever shall be, world without end. Amen.",
  fatima: "O my Jesus, forgive us our sins, save us from the fires of hell. Lead all souls to heaven, especially those in most need of Thy mercy.",
  hail_holy_queen: "Hail, Holy Queen, Mother of mercy, our life, our sweetness, and our hope. To thee do we cry, poor banished children of Eve. To thee do we send up our sighs, mourning and weeping in this valley of tears. Turn then, most gracious advocate, thine eyes of mercy toward us, and after this our exile show unto us the blessed fruit of thy womb, Jesus. O clement, O loving, O sweet Virgin Mary. Pray for us, O Holy Mother of God, that we may be made worthy of the promises of Christ.",
  rosary_concluding_prayer: "O God, whose only-begotten Son, by His life, death and resurrection, has purchased for us the rewards of eternal life; grant, we beseech Thee, that by meditating on these mysteries of the most holy Rosary of the Blessed Virgin Mary, we may imitate what they contain and obtain what they promise, through the same Christ our Lord. Amen."
};
const prayerLabels = {
  apostles_creed: "Apostles' Creed",
  our_father: 'Our Father',
  hail_mary: 'Hail Mary',
  glory_be: 'Glory Be',
  fatima: 'Fatima Prayer',
  hail_holy_queen: 'Hail Holy Queen',
  rosary_concluding_prayer: 'Concluding Rosary Prayer'
};
const prayerAudioPaths = {
  apostles_creed: `${basePath}media/rosary/prayers/apostles_creed.mp3`,
  hail_mary: `${basePath}media/rosary/prayers/hail_mary.mp3`,
  our_father: `${basePath}media/rosary/prayers/our_father.mp3`,
  glory_be: `${basePath}media/rosary/prayers/glory_be.mp3`,
  fatima: `${basePath}media/rosary/prayers/fatima.mp3`,
  hail_holy_queen: `${basePath}media/rosary/prayers/hail_holy_queen.mp3`,
  rosary_concluding_prayer: `${basePath}media/rosary/prayers/rosary_concluding_prayer.mp3`
};

const livePanel = document.createElement('div');
livePanel.className = 'prayer-live-panel';
livePanel.innerHTML = `
  <p class="prayer-live-label">Prayer In Progress</p>
  <p id="prayer-live-text" class="prayer-live-text">Listen to the mystery</p>
  <p id="prayer-live-timer" class="prayer-live-timer">Hands-free timer: off</p>
  <p class="prayer-live-timer">Praying<span id="prayer-live-dots" class="prayer-live-dots">.</span></p>
`;
meditationContent?.appendChild(livePanel);
const livePrayerText = document.getElementById('prayer-live-text');
const liveTimerText = document.getElementById('prayer-live-timer');
const liveDots = document.getElementById('prayer-live-dots');

const prayerAssistPanel = document.createElement('section');
prayerAssistPanel.className = 'prayer-assist-panel';
prayerAssistPanel.innerHTML = `
  <p class="prayer-assist-kicker">Prayer + Music Controls</p>
  <div class="prayer-assist-grid">
    <label class="prayer-assist-row">
      <span>Auto Prayer Sequence (Full Rosary Flow)</span>
      <input id="auto-prayer-toggle" type="checkbox" />
    </label>
    <label class="prayer-assist-row">
      <span>Church Music In Background</span>
      <input id="church-music-toggle" type="checkbox" />
    </label>
  </div>
  <p class="source-meta">When enabled: opening prayers + decade prayers play automatically and advance continuously through the full sequence.</p>
`;
meditationContent?.appendChild(prayerAssistPanel);
const autoPrayerToggle = document.getElementById('auto-prayer-toggle');
const churchMusicToggle = document.getElementById('church-music-toggle');

const dots = stages.map(() => {
  const dot = document.createElement('span');
  dot.className = 'bead-dot';
  progressEl.appendChild(dot);
  return dot;
});
if (progressEl) {
  progressEl.style.setProperty('--bead-count', String(stages.length));
}

if (playButton) {
  playButton.remove();
}
if (stopButton) {
  stopButton.remove();
}
if (studioPauseButton) {
  studioPauseButton.remove();
}

const startGuidedAudioButton = document.createElement('button');
startGuidedAudioButton.id = 'start-guided-audio';
startGuidedAudioButton.type = 'button';
startGuidedAudioButton.className = 'btn primary start-guided-audio-btn';
startGuidedAudioButton.textContent = 'Play Guided Audio';
if (meditationActions) {
  meditationActions.prepend(startGuidedAudioButton);
}

const nextPlaybackRequest = () => {
  playbackRequestId += 1;
  return playbackRequestId;
};

const isActivePlaybackRequest = requestId => requestId === playbackRequestId;

const renderMysteryTextCompanion = () => {
  if (!mysteryText) {
    if (mysteryExplanationEl) mysteryExplanationEl.textContent = 'Explanation text will appear here.';
    if (mysteryReadingTitleEl) mysteryReadingTitleEl.textContent = 'Full Reading';
    if (mysteryReadingEl) mysteryReadingEl.textContent = 'Reading text will appear here.';
    if (mysteryReflectionEl) mysteryReflectionEl.textContent = 'Reflection text will appear here.';
    return;
  }
  if (mysteryExplanationEl) mysteryExplanationEl.textContent = mysteryText.explanation;
  if (mysteryReadingTitleEl) mysteryReadingTitleEl.textContent = `Full Reading - ${mysteryText.readingTitle}`;
  if (mysteryReadingEl) mysteryReadingEl.textContent = mysteryText.reading;
  if (mysteryReflectionEl) mysteryReflectionEl.textContent = mysteryText.reflection;
};

const syncGlobalAudioContext = extra => {
  const payload = {
    title: stages[stageIndex]?.title || 'Meditation',
    subtitle: stages[stageIndex]?.badge || 'Meditation',
    stage: stages[stageIndex]?.badge || 'Meditation',
    url: window.location.href,
    autoPrayerVoiceEnabled,
    autoTimerEnabled: autoRunning,
    autoTimerCountdown: autoRemainingSeconds,
    autoTimerDuration,
    ...extra
  };

  try {
    localStorage.setItem('rosary_audio_context', JSON.stringify(payload));
  } catch (_) {
    // no-op
  }

  if (window.RosaryAudioContext?.set) {
    window.RosaryAudioContext.set(payload);
  } else {
    window.dispatchEvent(new CustomEvent('rosary-audio-context-updated'));
  }
};

const readAudioContext = () => {
  try {
    return JSON.parse(localStorage.getItem('rosary_audio_context') || '{}');
  } catch (_) {
    return {};
  }
};

const initialAudioContext = readAudioContext();
if (typeof initialAudioContext.autoPrayerVoiceEnabled === 'boolean') {
  autoPrayerVoiceEnabled = initialAudioContext.autoPrayerVoiceEnabled;
  if (autoPrayerToggle) {
    autoPrayerToggle.checked = autoPrayerVoiceEnabled;
  }
}
if (params.get('auto') === '1') {
  autoPrayerVoiceEnabled = true;
  if (autoPrayerToggle) {
    autoPrayerToggle.checked = true;
  }
}

const stageClipStep = index => {
  const step = Number(stages[index]?.clipStep || 0);
  return step > 0 ? step : null;
};
const stageStepKey = index => {
  const step = stageClipStep(index);
  return step ? `step-${String(step).padStart(2, '0')}` : null;
};
const stagePrayerClipPath = index => {
  const kind = stages[index]?.kind;
  if (kind === 'intro_prayers') {
    return `${basePath}media/rosary/prayers/intro_prayers.mp3`;
  }
  if (kind === 'end_prayers') {
    // Keep end-prayer stage on individual prayer clips only
    // until the dedicated end_prayers.mp3 is re-recorded.
    return null;
  }
  return null;
};
const normalizeClipPath = clipPath => {
  if (!clipPath) return '';
  const appendVersion = path =>
    `${path}${path.includes('?') ? '&' : '?'}v=${encodeURIComponent(audioVersion)}`;
  if (/^https?:\/\//i.test(clipPath) || /^file:\/\//i.test(clipPath)) {
    return appendVersion(clipPath);
  }
  if (clipPath.startsWith('/') && window.location.protocol === 'file:') {
    return appendVersion(`${basePath}${clipPath.slice(1)}`);
  }
  return appendVersion(clipPath);
};

const fallbackClipForStage = index => {
  if (index < 0 || index >= stages.length) return null;
  const prayerClip = stagePrayerClipPath(index);
  if (prayerClip) return { path: prayerClip, duration_sec: 0 };
  const stepKey = stageStepKey(index);
  if (!stepKey) return null;
  const path = `${basePath}media/rosary/${key}/${stepKey}.mp3`;
  return { path, duration_sec: 0 };
};

const clipForStage = index => {
  const prayerClip = stagePrayerClipPath(index);
  if (prayerClip) {
    return { path: prayerClip, duration_sec: 0 };
  }
  const stepKey = stageStepKey(index);
  if (!stepKey) return null;
  const mysteryClips = clipManifest?.mysteries?.[key];
  return mysteryClips?.[stepKey] || fallbackClipForStage(index);
};

const loadClipManifest = async () => {
  try {
    const response = await fetch(clipManifestPath, { cache: 'no-store' });
    if (!response.ok) {
      clipAvailable = false;
      return;
    }
    clipManifest = await response.json();
    clipAvailable = Boolean(clipForStage(stageIndex));
  } catch (_) {
    clipManifest = null;
    clipAvailable = Boolean(fallbackClipForStage(stageIndex));
  }
};

const ensureClipPlayers = () => {
  if (!clipAudio) {
    clipAudio = new Audio();
    clipAudio.preload = 'auto';
  }
  if (!clipPreload) {
    clipPreload = new Audio();
    clipPreload.preload = 'auto';
  }
};

const stopVoice = () => {
  nextPlaybackRequest();
  playbackPending = false;
  clearAutoCountdown();
  if (clipAudio) {
    clipAudio.onended = null;
    clipAudio.onpause = null;
    clipAudio.onplay = null;
    clipAudio.pause();
    clipAudio.currentTime = 0;
  }
  if (prayerClipAudio) {
    prayerClipAudio.onended = null;
    prayerClipAudio.onpause = null;
    prayerClipAudio.onplay = null;
    prayerClipAudio.onerror = null;
    prayerClipAudio.pause();
    prayerClipAudio.currentTime = 0;
  }
};

const clearAutoCountdown = (resetRemaining = true) => {
  if (autoTimerId) {
    clearInterval(autoTimerId);
    autoTimerId = null;
  }
  autoCountdownStageIndex = -1;
  if (resetRemaining) {
    autoRemainingSeconds = 0;
    autoTimerDuration = 0;
  }
};

const hasActiveNarration = () => {
  if (prayerClipAudio && !prayerClipAudio.ended) {
    return !prayerClipAudio.paused || prayerClipAudio.currentTime > 0;
  }
  if (activeNarrationMode === 'prerendered' && clipAudio) {
    return !clipAudio.paused || clipAudio.currentTime > 0;
  }
  return false;
};

const updateVoiceButtonLabel = () => {
  if (!pauseButton) {
    return;
  }
  if (playbackPending) {
    pauseButton.textContent = 'Starting\u2026';
    return;
  }
  const isPlaying = (prayerClipAudio && !prayerClipAudio.ended && !prayerClipAudio.paused)
    || (activeNarrationMode === 'prerendered' && clipAudio && !clipAudio.paused && !clipAudio.ended);
  const isPaused = (prayerClipAudio && !prayerClipAudio.ended && prayerClipAudio.paused)
    || (activeNarrationMode === 'prerendered' && clipAudio && clipAudio.paused && clipAudio.currentTime > 0);

  if (isPlaying) {
    pauseButton.textContent = '\u23F8 Pause';
    pauseButton.setAttribute('aria-label', 'Pause voice narration');
    return;
  }
  if (isPaused) {
    pauseButton.textContent = '\u25B6 Play';
    pauseButton.setAttribute('aria-label', 'Resume voice narration');
    return;
  }
  if (hasUserStartedPlayback) {
    pauseButton.textContent = '\u21BB Replay';
    pauseButton.setAttribute('aria-label', 'Replay voice narration');
    return;
  }
  pauseButton.textContent = '\u25B6 Play';
  pauseButton.setAttribute('aria-label', 'Play voice narration');
};

const updateStartGuidedAudioButton = () => {
  if (!startGuidedAudioButton) return;
  if (playbackPending) {
    startGuidedAudioButton.textContent = 'Starting\u2026';
    return;
  }
  if (hasActiveNarration()) {
    startGuidedAudioButton.textContent = '\u25B6 Playing\u2026';
    startGuidedAudioButton.classList.add('is-playing');
    return;
  }
  startGuidedAudioButton.classList.remove('is-playing');
  startGuidedAudioButton.textContent = hasUserStartedPlayback ? '\u21BB Replay Guided Audio' : '\u25B6 Play Guided Audio';
};

const speakPrayer = (prayerKey, onComplete = null, requestId = playbackRequestId) => {
  const prayerLabel = prayerLabels[prayerKey] || prayerKey;
  const prayerClip = prayerAudioPaths[prayerKey];
  if (prayerClip) {
    if (!prayerClipAudio) {
      prayerClipAudio = new Audio();
      prayerClipAudio.preload = 'auto';
    }
    prayerClipAudio.src = normalizeClipPath(prayerClip);
    prayerClipAudio.onplay = () => {
      if (!isActivePlaybackRequest(requestId)) {
        return;
      }
      playbackPending = false;
      soundStatus.textContent = `Praying ${prayerLabel}...`;
      syncGlobalAudioContext({
        mode: 'prerendered',
        playing: true,
        paused: false,
        completed: false,
        stage: prayerLabel,
        subtitle: prayerLabel,
        text: prayerTexts[prayerKey] || '',
        startedAt: Date.now(),
        pausedAt: null,
        totalPausedMs: 0,
        estimatedDurationMs: Math.round((Number(prayerClipAudio.duration) || 0) * 1000)
      });
      updateVoiceButtonLabel();
      updateStartGuidedAudioButton();
    };
    prayerClipAudio.onpause = () => {
      if (!isActivePlaybackRequest(requestId)) {
        return;
      }
      if (!prayerClipAudio.ended) {
        syncGlobalAudioContext({ mode: 'prerendered', playing: true, paused: true, pausedAt: Date.now() });
      }
      updateVoiceButtonLabel();
      updateStartGuidedAudioButton();
    };
    prayerClipAudio.onended = () => {
      if (!isActivePlaybackRequest(requestId)) {
        return;
      }
      syncGlobalAudioContext({ mode: 'prerendered', playing: false, paused: false, completed: true });
      if (typeof onComplete === 'function') {
        onComplete();
      }
      updateStartGuidedAudioButton();
    };
    prayerClipAudio.onerror = () => {
      if (!isActivePlaybackRequest(requestId)) {
        return;
      }
      playbackPending = false;
      if (typeof onComplete === 'function') {
        onComplete();
      }
      updateStartGuidedAudioButton();
    };
    prayerClipAudio.play().catch(() => {
      if (!isActivePlaybackRequest(requestId)) {
        return;
      }
      playbackPending = false;
      // Do not auto-skip prayers when autoplay is blocked.
      // Keep the sequence pending so a user Play click can resume correctly.
      soundStatus.textContent = `Press Play to begin ${prayerLabel}.`;
      syncGlobalAudioContext({
        mode: 'prerendered',
        playing: false,
        paused: false,
        completed: false,
        stage: prayerLabel,
        subtitle: prayerLabel
      });
      updateVoiceButtonLabel();
      updateStartGuidedAudioButton();
    });
    return;
  }

  soundStatus.textContent = `Missing recorded prayer audio for ${prayerLabel}.`;
  if (typeof onComplete === 'function') {
    onComplete();
  }
};

const speakPrayerSequence = (sequence, onComplete = null, requestId = playbackRequestId) => {
  const list = Array.isArray(sequence) ? sequence.filter(Boolean) : [];
  if (!list.length) {
    if (typeof onComplete === 'function') onComplete();
    return;
  }
  let idx = 0;
  const next = () => {
    if (!isActivePlaybackRequest(requestId)) {
      return;
    }
    if (idx >= list.length) {
      if (typeof onComplete === 'function') onComplete();
      return;
    }
    const prayerKey = list[idx++];
    speakPrayer(prayerKey, next, requestId);
  };
  next();
};

const prayerSequenceForStage = currentStageIndex => {
  const kind = stages[currentStageIndex]?.kind;
  if (kind === 'intro_prayers') {
    return ['apostles_creed', 'our_father', 'hail_mary', 'hail_mary', 'hail_mary', 'glory_be'];
  }
  if (kind === 'end_prayers') {
    return ['hail_holy_queen', 'rosary_concluding_prayer'];
  }
  if (!autoPrayerVoiceEnabled) {
    return [];
  }
  if (kind === 'our_father') {
    return ['our_father'];
  }
  if (kind === 'hail_mary') {
    return ['hail_mary'];
  }
  if (kind === 'decade_closing') {
    return ['glory_be', 'fatima'];
  }
  return [];
};

const handleNarrationComplete = currentStageIndex => {
  if (currentStageIndex !== stageIndex) {
    return;
  }
  soundStatus.textContent = 'Voice complete. Continue in silence or press Next.';
  syncGlobalAudioContext({ mode: activeNarrationMode, playing: false, paused: false, completed: true });

  const stagePrayerSequence = prayerSequenceForStage(currentStageIndex);
  if (autoPrayerVoiceEnabled && stagePrayerSequence.length) {
    soundStatus.textContent = 'Praying auto sequence...';
    speakPrayerSequence(stagePrayerSequence, () => {
      if (currentStageIndex !== stageIndex) {
        return;
      }
      if (autoPrayerVoiceEnabled) {
        nextStage();
        return;
      }
      soundStatus.textContent = 'Prayer complete. Press Next when ready.';
      updateVoiceButtonLabel();
    });
    return;
  }

  if (autoPrayerVoiceEnabled) {
    nextStage();
    return;
  }

  if (autoRunning) {
    startAutoCountdown(currentStageIndex);
    return;
  }

  soundStatus.textContent = 'Voice complete. Press Next when ready.';
  updateVoiceButtonLabel();
};

const preloadNextClip = index => {
  if (!clipAvailable || !clipPreload) {
    return;
  }
  const next = clipForStage(index + 1);
  if (next?.path) {
    clipPreload.src = next.path;
    clipPreload.load();
  }
};

const playClipIfAvailable = async (currentStageIndex, narrationText, requestId) => {
  if (!clipAvailable) {
    return false;
  }
  const clip = clipForStage(currentStageIndex);
  if (!clip?.path) {
    return false;
  }

  ensureClipPlayers();
  activeNarrationMode = 'prerendered';
  clipAudio.src = normalizeClipPath(clip.path);
  clipAudio.onended = () => {
    if (!isActivePlaybackRequest(requestId)) {
      return;
    }
    handleNarrationComplete(currentStageIndex);
    updateStartGuidedAudioButton();
  };
  clipAudio.onpause = () => {
    if (!isActivePlaybackRequest(requestId)) {
      return;
    }
    if (!clipAudio.ended) {
      syncGlobalAudioContext({ mode: 'prerendered', playing: true, paused: true, pausedAt: Date.now() });
    }
    updateVoiceButtonLabel();
    updateStartGuidedAudioButton();
  };
  clipAudio.onplay = () => {
    if (!isActivePlaybackRequest(requestId)) {
      return;
    }
    playbackPending = false;
    syncGlobalAudioContext({
      mode: 'prerendered',
      playing: true,
      paused: false,
      completed: false,
      text: narrationText,
      startedAt: Date.now(),
      pausedAt: null,
      totalPausedMs: 0,
      estimatedDurationMs: Math.round(Number(clip.duration_sec || 0) * 1000)
    });
    updateVoiceButtonLabel();
    updateStartGuidedAudioButton();
  };

  try {
    await clipAudio.play();
    if (!isActivePlaybackRequest(requestId)) {
      return false;
    }
    playbackPending = false;
    soundStatus.textContent = 'Audio clip playing.';
    preloadNextClip(currentStageIndex);
    updateStartGuidedAudioButton();
    return true;
  } catch (_) {
    if (isActivePlaybackRequest(requestId)) {
      playbackPending = false;
      updateStartGuidedAudioButton();
    }
    return false;
  }
};

const playVoice = ({ userInitiated = false } = {}) => {
  if (userInitiated) {
    hasUserStartedPlayback = true;
  }
  if (!hasUserStartedPlayback) {
    soundStatus.textContent = 'Press Play Guided Audio to begin.';
    updateVoiceButtonLabel();
    updateStartGuidedAudioButton();
    return;
  }
  if (playbackPending) {
    return;
  }
  playbackPending = true;
  const requestId = nextPlaybackRequest();
  clearAutoCountdown();
  updateLivePrayerPanel();
  if (clipAudio) {
    clipAudio.pause();
    clipAudio.currentTime = 0;
  }
  if (prayerClipAudio) {
    prayerClipAudio.pause();
    prayerClipAudio.currentTime = 0;
  }
  const current = stages[stageIndex];
  const currentStageIndex = stageIndex;
  const narrationText = current.text;
  updateVoiceButtonLabel();
  updateStartGuidedAudioButton();
  playClipIfAvailable(currentStageIndex, narrationText, requestId).then(played => {
    if (!isActivePlaybackRequest(requestId)) {
      return;
    }
    playbackPending = false;
    if (played) {
      return;
    }
    const stagePrayerSequence = prayerSequenceForStage(currentStageIndex);
    if (stagePrayerSequence.length) {
      soundStatus.textContent = 'Praying sequence...';
      speakPrayerSequence(stagePrayerSequence, () => {
        if (!isActivePlaybackRequest(requestId) || currentStageIndex !== stageIndex) {
          return;
        }
        if (autoPrayerVoiceEnabled) {
          nextStage();
          return;
        }
        soundStatus.textContent = 'Prayer complete. Press Next when ready.';
        updateVoiceButtonLabel();
        updateStartGuidedAudioButton();
      });
      return;
    }
    soundStatus.textContent = 'Recorded audio is unavailable for this step. No browser voice fallback.';
    syncGlobalAudioContext({
      mode: 'prerendered',
      playing: false,
      paused: false,
      completed: false
    });
    updateVoiceButtonLabel();
    updateStartGuidedAudioButton();
  });
};

const togglePauseVoice = () => {
  if (!hasUserStartedPlayback) {
    playVoice({ userInitiated: true });
    return;
  }
  if (!hasActiveNarration()) {
    playVoice({ userInitiated: true });
    return;
  }

  if (prayerClipAudio && !prayerClipAudio.ended) {
    if (!prayerClipAudio.paused) {
      prayerClipAudio.pause();
      soundStatus.textContent = 'Prayer audio paused.';
      syncGlobalAudioContext({ mode: 'prerendered', playing: true, paused: true, pausedAt: Date.now() });
      updateVoiceButtonLabel();
      updateStartGuidedAudioButton();
      return;
    }
    prayerClipAudio.play().then(() => {
      soundStatus.textContent = 'Prayer audio resumed.';
      syncGlobalAudioContext({ mode: 'prerendered', playing: true, paused: false, pausedAt: null });
      updateVoiceButtonLabel();
      updateStartGuidedAudioButton();
    }).catch(() => {});
    return;
  }

  if (activeNarrationMode === 'prerendered' && clipAudio) {
    if (!clipAudio.paused) {
      clipAudio.pause();
      soundStatus.textContent = 'Audio clip paused.';
      syncGlobalAudioContext({ mode: 'prerendered', playing: true, paused: true, pausedAt: Date.now() });
      updateVoiceButtonLabel();
      updateStartGuidedAudioButton();
      return;
    }
    clipAudio.play().then(() => {
      soundStatus.textContent = 'Audio clip resumed.';
      syncGlobalAudioContext({ mode: 'prerendered', playing: true, paused: false, pausedAt: null });
      updateVoiceButtonLabel();
      updateStartGuidedAudioButton();
    }).catch(() => {});
    return;
  }

  soundStatus.textContent = 'No active audio to pause.';
};

const render = () => {
  const current = stages[stageIndex];
  clipAvailable = Boolean(clipForStage(stageIndex));
  stageBadge.textContent = current.badge;
  stageTitle.textContent = current.title;
  stageText.textContent = current.text;
  stepCounter.textContent = `Step ${stageIndex + 1} of ${stages.length}`;

  if (stepNavLabel) {
    stepNavLabel.textContent = `Step ${stageIndex + 1} of ${stages.length}`;
  }
  if (stepNavBar) {
    stepNavBar.setAttribute('aria-valuenow', String(stageIndex + 1));
    stepNavBar.setAttribute('aria-valuemax', String(stages.length));
  }
  if (stepNavFill) {
    stepNavFill.style.width = `${Math.round(((stageIndex + 1) / stages.length) * 100)}%`;
  }

  dots.forEach((dot, idx) => {
    dot.classList.toggle('on', idx <= stageIndex);
  });

  prevButton.disabled = stageIndex === 0;
  nextButton.textContent = stageIndex === stages.length - 1 ? 'Next Mystery' : 'Next';
  updateLivePrayerPanel();
  updateVoiceButtonLabel();
  updateStartGuidedAudioButton();
  updateAutoTimerToggleState();
  syncGlobalAudioContext();
  preloadNextClip(stageIndex);

  if (meditationContent) {
    meditationContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  window.dispatchEvent(new CustomEvent('sc:content-updated'));
};

const prayerCueForStage = () => {
  const kind = stages[stageIndex]?.kind;
  if (kind === 'intro_prayers') {
    return "Pray: Apostles' Creed, Our Father, 3 Hail Marys, Glory Be";
  }
  if (kind === 'lecture') {
    return 'Listen and enter the mystery.';
  }
  if (kind === 'our_father') {
    return 'Pray: Our Father';
  }
  if (kind === 'decade_closing') {
    return 'Pray: Glory Be, then Fatima Prayer';
  }
  if (kind === 'end_prayers') {
    return 'Pray: Hail Holy Queen and concluding Rosary prayer';
  }
  return 'Pray: Hail Mary';
};

const updateLivePrayerPanel = () => {
  if (livePrayerText) {
    livePrayerText.textContent = prayerCueForStage();
  }
  if (liveTimerText) {
    liveTimerText.textContent = autoRunning
      ? (autoRemainingSeconds > 0
        ? `Hands-free timer: next step in ${autoRemainingSeconds}s`
        : 'Hands-free timer armed: starts after narration')
      : 'Hands-free timer: off';
  }
  syncGlobalAudioContext();
};

const startAutoCountdown = currentStageIndex => {
  const duration = Number(autoTimerDuration || 0);
  if (!autoRunning || !duration || currentStageIndex !== stageIndex) {
    return;
  }

  clearAutoCountdown(false);
  autoCountdownStageIndex = currentStageIndex;
  autoRemainingSeconds = duration;
  soundStatus.textContent = `Prayer time: ${autoRemainingSeconds}s before next step.`;
  updateLivePrayerPanel();

  autoTimerId = setInterval(() => {
    if (!autoRunning || autoCountdownStageIndex !== stageIndex) {
      clearAutoCountdown();
      updateAutoTimerToggleState();
      updateLivePrayerPanel();
      return;
    }

    autoRemainingSeconds -= 1;
    if (autoRemainingSeconds <= 0) {
      clearAutoCountdown();
      updateAutoTimerToggleState();
      updateLivePrayerPanel();
      nextStage();
      return;
    }

    soundStatus.textContent = `Prayer time: ${autoRemainingSeconds}s before next step.`;
    updateAutoTimerToggleState();
    updateLivePrayerPanel();
  }, 1000);
};

const startDotsAnimation = () => {
  if (dotsTimerId || !liveDots) {
    return;
  }
  dotsTimerId = setInterval(() => {
    dotsFrame = (dotsFrame % 3) + 1;
    liveDots.textContent = '.'.repeat(dotsFrame);
  }, 500);
};

const stopDotsAnimation = () => {
  if (dotsTimerId) {
    clearInterval(dotsTimerId);
    dotsTimerId = null;
  }
  dotsFrame = 0;
  if (liveDots) {
    liveDots.textContent = '.';
  }
};

const navigateToKey = mysteryKey => {
  const url = new URL(mysteryUrl(mysteryKey), window.location.href);
  const autoMode = autoPrayerVoiceEnabled || Boolean(rosarySession?.autoPrayer);
  const lang = getActiveLang();
  if (lang) {
    url.searchParams.set('lang', lang);
  }
  if (autoMode) {
    url.searchParams.set('auto', '1');
  }
  window.location.href = url.toString();
};

const navigateMystery = index => {
  const clamped = Math.max(0, Math.min(index, orderedKeys.length - 1));
  navigateToKey(orderedKeys[clamped]);
};

const nextStage = () => {
  clearAutoCountdown();
  stopVoice();
  if (stageIndex < stages.length - 1) {
    stageIndex += 1;
    render();
    if (hasUserStartedPlayback) {
      playVoice();
    }
    return;
  }
  stopAutoTimer();
  if (rosarySession?.active && Array.isArray(rosarySession.sequence) && rosarySession.sequence.length) {
    const currentPos = rosarySession.sequence.indexOf(key);
    if (currentPos >= 0 && currentPos < rosarySession.sequence.length - 1) {
      const nextKey = rosarySession.sequence[currentPos + 1];
      rosarySession = { ...rosarySession, currentKey: nextKey };
      writeRosarySession(rosarySession);
      navigateToKey(nextKey);
      return;
    }
    clearRosarySession();
    rosarySession = null;
    window.location.href = `${basePath}rosary-visual-guide.html`;
    return;
  }
  navigateMystery((activeIndex + 1) % orderedKeys.length);
};

prevButton.addEventListener('click', () => {
  clearAutoCountdown();
  stopVoice();
  if (stageIndex > 0) {
    stageIndex -= 1;
    render();
    if (hasUserStartedPlayback) {
      playVoice();
    }
  }
});

nextButton.addEventListener('click', nextStage);
pauseButton.addEventListener('click', togglePauseVoice);

if (prevMysteryButton) {
  prevMysteryButton.addEventListener('click', () => navigateMystery(activeIndex - 1));
}
if (nextMysteryButton) {
  nextMysteryButton.addEventListener('click', () => navigateMystery(activeIndex + 1));
}
if (mysteryPicker) {
  Object.entries(mysterySets).forEach(([setKey, setItems]) => {
    const group = document.createElement('optgroup');
    group.label = mysterySetLabel[setKey] || setKey;

    const introOption = document.createElement('option');
    introOption.value = `intro:${setKey}`;
    introOption.textContent = `Intro Prayers (${mysterySetLabel[setKey] || setKey})`;
    if (initialStage === 'intro' && setKey === currentSet) {
      introOption.selected = true;
    }
    group.appendChild(introOption);

    setItems.forEach(mysteryKey => {
      const option = document.createElement('option');
      option.value = mysteryKey;
      option.textContent = mysteries[mysteryKey]?.title || mysteryKey;
      if (mysteryKey === key && initialStage !== 'intro' && initialStage !== 'end') {
        option.selected = true;
      }
      group.appendChild(option);
    });

    const endOption = document.createElement('option');
    endOption.value = `end:${setKey}`;
    endOption.textContent = `End Prayers (${mysterySetLabel[setKey] || setKey})`;
    if (initialStage === 'end' && setKey === currentSet) {
      endOption.selected = true;
    }
    group.appendChild(endOption);

    mysteryPicker.appendChild(group);
  });
  mysteryPicker.addEventListener('change', () => {
    const selected = mysteryPicker.value;
    if (selected.startsWith('intro:')) {
      const setName = selected.split(':')[1];
      startSetSession(setName, 'intro');
      return;
    }
    if (selected.startsWith('end:')) {
      const setName = selected.split(':')[1];
      const setItems = mysterySets[setName] || [];
      const lastKey = setItems[setItems.length - 1];
      if (lastKey) {
        const url = new URL(mysteryUrl(lastKey), window.location.href);
        const lang = getActiveLang();
        if (lang) {
          url.searchParams.set('lang', lang);
        }
        url.searchParams.set('stage', 'end');
        window.location.href = url.toString();
      }
      return;
    }
    navigateMystery(orderedKeys.indexOf(selected));
  });
}

const startSetSession = (setName, startStage = null) => {
  const sequence = mysterySets[setName] || [];
  if (!sequence.length) {
    return;
  }
  const first = sequence[0];
  rosarySession = {
    active: true,
    set: setName,
    sequence,
    currentKey: first,
    autoPrayer: true,
    startedAt: Date.now()
  };
  writeRosarySession(rosarySession);
  autoPrayerVoiceEnabled = true;
  if (autoPrayerToggle) {
    autoPrayerToggle.checked = true;
    autoPrayerToggle.dispatchEvent(new Event('change', { bubbles: true }));
  }
  if (startStage === 'intro') {
    const url = new URL(mysteryUrl(first), window.location.href);
    const lang = getActiveLang();
    if (lang) {
      url.searchParams.set('lang', lang);
    }
    url.searchParams.set('stage', 'intro');
    window.location.href = url.toString();
    return;
  }
  navigateToKey(first);
};

window.RosaryNarrationController = {
  play: () => playVoice({ userInitiated: true }),
  togglePause: togglePauseVoice,
  stop: () => {
    stopVoice();
    updateVoiceButtonLabel();
    syncGlobalAudioContext({ mode: activeNarrationMode, playing: false, paused: false, completed: false });
  },
  next: nextStage,
  previous: () => {
    if (stageIndex > 0) {
      stopVoice();
      stageIndex -= 1;
      render();
      if (hasUserStartedPlayback) {
        playVoice();
      }
    }
  }
};

if (startGuidedAudioButton) {
  startGuidedAudioButton.addEventListener('click', () => {
    playVoice({ userInitiated: true });
  });
}

let ambientContext;
let ambientNodes = [];
let ambientOn = false;

const makeAmbient = () => {
  if (ambientContext) {
    return;
  }

  ambientContext = new AudioContext();
  const master = ambientContext.createGain();
  master.gain.value = 0.04;
  master.connect(ambientContext.destination);

  const freqs = [130.81, 196, 261.63, 392];
  freqs.forEach((freq, i) => {
    const osc = ambientContext.createOscillator();
    const gain = ambientContext.createGain();
    osc.type = i === 0 ? 'sine' : 'triangle';
    osc.frequency.value = freq;
    gain.gain.value = i === 0 ? 0.03 : 0.012;
    osc.connect(gain);
    gain.connect(master);
    osc.start();
    ambientNodes.push({ gain });
  });
};

const toggleAmbient = async () => {
  makeAmbient();
  if (ambientContext.state === 'suspended') {
    await ambientContext.resume();
  }

  ambientOn = !ambientOn;
  churchMusicEnabled = ambientOn;
  if (churchMusicToggle) {
    churchMusicToggle.checked = churchMusicEnabled;
  }
  ambientNodes.forEach(({ gain }, i) => {
    gain.gain.setTargetAtTime(ambientOn ? (i === 0 ? 0.03 : 0.012) : 0, ambientContext.currentTime, 0.35);
  });

  soundButton.textContent = `Church Music: ${ambientOn ? 'On' : 'Off'}`;
};

soundButton.addEventListener('click', toggleAmbient);

if (autoPrayerToggle) {
  autoPrayerToggle.addEventListener('change', () => {
    autoPrayerVoiceEnabled = autoPrayerToggle.checked;
    if (rosarySession?.active) {
      rosarySession = { ...rosarySession, autoPrayer: autoPrayerVoiceEnabled };
      writeRosarySession(rosarySession);
    }
    if (autoPrayerVoiceEnabled && autoRunning) {
      stopAutoTimer();
    }
    soundStatus.textContent = autoPrayerVoiceEnabled
      ? 'Auto Prayer Sequence is on. The flow will continue automatically.'
      : 'Auto Prayer Sequence is off. Press Next when ready.';
    syncGlobalAudioContext({ autoPrayerVoiceEnabled });
  });
}

if (churchMusicToggle) {
  churchMusicToggle.addEventListener('change', () => {
    if (churchMusicToggle.checked !== ambientOn) {
      toggleAmbient();
    }
  });
}

const studioPath = `${basePath}audio/${key}.mp3`;
studioPlayButton.hidden = true;
studioAudio.preload = 'metadata';
studioAudio.src = studioPath;

studioPlayButton.addEventListener('click', async () => {
  if (studioAudio.paused) {
    try {
      await studioAudio.play();
      studioPlayButton.textContent = '\u23F8 Pause Studio Track';
    } catch (_) {
      soundStatus.textContent = 'Could not play studio track.';
    }
    return;
  }
  studioAudio.pause();
  studioPlayButton.textContent = '\u25B6 Play Studio Track';
});
studioAudio.addEventListener('ended', () => {
  studioPlayButton.textContent = '\u25B6 Play Studio Track';
});
studioAudio.addEventListener('loadedmetadata', () => {
  studioPlayButton.hidden = false;
  studioPlayButton.textContent = '\u25B6 Play Studio Track';
});
studioAudio.addEventListener('error', () => {
  studioPlayButton.hidden = true;
});

const updateAutoTimerToggleState = () => {
  const seconds = Number(autoTimerSeconds.value || 0);
  if (autoRunning) {
    autoTimerToggle.textContent = `Stop Auto (${autoTimerDuration}s)`;
    autoTimerToggle.disabled = false;
  } else {
    autoTimerToggle.textContent = seconds ? 'Start Auto' : 'Start Auto';
    autoTimerToggle.disabled = !seconds;
  }
  if (autoTimerCountdownEl) {
    if (autoRunning && autoRemainingSeconds > 0) {
      autoTimerCountdownEl.hidden = false;
      autoTimerCountdownEl.textContent = `Auto running \u2014 next in ${autoRemainingSeconds}s`;
    } else if (autoRunning) {
      autoTimerCountdownEl.hidden = false;
      autoTimerCountdownEl.textContent = `Auto running (${autoTimerDuration}s)`;
    } else {
      autoTimerCountdownEl.hidden = true;
      autoTimerCountdownEl.textContent = '';
    }
  }
};

const stopAutoTimer = () => {
  clearAutoCountdown();
  autoRunning = false;
  stopDotsAnimation();
  updateAutoTimerToggleState();
  updateLivePrayerPanel();
};

autoTimerToggle.addEventListener('click', () => {
  const seconds = Number(autoTimerSeconds.value || 0);

  if (autoRunning) {
    stopAutoTimer();
    soundStatus.textContent = 'Auto timer is off.';
    return;
  }

  if (!seconds) {
    soundStatus.textContent = 'Select a timer duration first.';
    return;
  }

  autoRunning = true;
  autoTimerDuration = seconds;
  autoRemainingSeconds = 0;
  soundStatus.textContent = `Auto timer enabled (${seconds}s). Countdown starts after narration ends.`;
  startDotsAnimation();
  updateAutoTimerToggleState();
  updateLivePrayerPanel();
});

autoTimerSeconds.addEventListener('change', () => {
  const seconds = Number(autoTimerSeconds.value || 0);
  autoTimerToggle.disabled = !seconds && !autoRunning;
});

render();
renderMysteryTextCompanion();
window.dispatchEvent(new CustomEvent('sc:content-updated'));
soundButton.textContent = 'Church Music: Off';
updateVoiceButtonLabel();
updateStartGuidedAudioButton();
updateAutoTimerToggleState();
ensureClipPlayers();
loadClipManifest()
  .finally(() => {
    soundStatus.textContent = 'Press Play Guided Audio to begin.';
    updateStartGuidedAudioButton();
  });
