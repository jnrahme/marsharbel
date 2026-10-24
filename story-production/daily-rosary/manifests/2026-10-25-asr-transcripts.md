# Oct 25 ASR + signal checks (faster-whisper base, CPU int8; same accepted-garble-class practice)

## EN intro WAV (speech-20261024-191529-2f23b273.wav)
- sha256 81cd7efb549c75f80f7eafa5fb8bd2b3 (prefix), pcm_s16le 24kHz mono, 11.16s, true peak -2.9 dBTP
- ASR: "Today, October 25th, we remember Saint's Cresanthus and Daria, martyrs of the early church in Rome. Saint's Cresanthus and Daria, pray for us."
- Expected: "Today, October twenty-fifth, we remember Saints Chrysanthus and Daria, martyrs of the early Church in Rome. Saints Chrysanthus and Daria, pray for us."
- Variance: Saint's/Saints (accepted class), Cresanthus/Chrysanthus (proper-noun mishearing class). PASS signal/text.

## AR intro WAV (speech-20261024-191532-ae5f5e57.wav)
- sha256 3fb1a4888de2d3d9547d7b95a62f82e8 (prefix), pcm_s16le 24kHz mono, 19.08s, true peak -4.5 dBTP
- ASR matches expected with diacritic drops and proper-noun garble classes (قدسين/قدّيسين, خيرسانثس/خريسانثوس, رومة/روما).
- FLAG unverified variance: ASR heard "نفكر" where expected "نذكر" (consonant ف/ذ cannot be resolved by ASR; could be mishearing or actual TTS substitution - actual-ear review would settle; not claimed either way).
- Segments 0.00-19.00, no truncation, pacing normal. PASS signal/text with the one flagged item.

## Final master intro (re-check after assembly)
- ASR of final-en-oct25.mp4 [0-12.05]: same text/garble classes as source WAV. PASS.
- Master true peak -5.2 dBTP. Duration 2038.318s = 12.05 intro + 2026.265 body (+3ms).
- Frame probes: 6s = Oct 25 card; 12.3s = Glorious body entry card; 200s = The Resurrection meditation. Splice clean.
