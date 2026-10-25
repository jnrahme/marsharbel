# NEW RECONSTRUCTION (2026-10-25) - NOT the original 85fc5eaa bytes
Rebuilt 2026-10-25 ~06:48 EDT by the locale review lane on Main's closed-reference reconstruction authorization.
Method: verbatim replay of the recorded producer generator script (chat_event 2026-10-23 05:05:14 EDT) with the
attested petition-after values recovered from the recorded 2026-10-23 04:56:40 printout, each cross-checked
byte-equal against the live repo catalogs at stage f2d9cd0 (all 8 locales match). The body below the rule is the
replayed output; the original file had no such header.
LOST REFERENCE (originals unrecoverable): original producer commit 85fc5eaa (local /tmp/mb4 branch b1-recovery,
never pushed; git fetch confirms no remote ref). Original was shipped inside zip b1-c1-anxiety-full-v1.zip
sha256 f9eb5ff25f82229a5f1537bcd0bc5cfdfcf8f2fb48ace690d462de50fcdd3710 (sent to Main 2026-10-23 05:13:06 EDT).

---

# ADJUDICATION POINT - B1 C1 a-miracle: AR attested clause vs EN omission
Recorded 2026-10-23 ~05:10 EDT per parent directive (05:04): "AR attested clause vs EN omission is an explicit
source/mirror editorial adjudication point, not resolved by byte-copy provenance alone. Preserve exact source
locators and side-by-side wording for later review." Status: OPEN - awaiting Scrum/editorial ruling.

## Question
The certified Arabic novena catalog's day-1 petition-after carries a clause the certified English catalog
(and the live EN a-miracle page) do not have. The a-miracle AR catalog byte-copied the attested AR form, so
the AR twin's miracle quote says more than the EN page's quote. Keep attested bytes (current packet state),
or align the clause across locales? Editorial decision, not provenance.

## Side-by-side (miracle quote assembly = petition-before + " " + placeholder + petition-after)
EN (certified catalog locales/en/saint-charbel-novena-master-copy.json,
    key saint-charbel-novena.traditional.day-1.petition-after):
  petition-after = '. Amen.'
  -> EN quote ends: "...the grace which I need (name the grace). Amen."
  Live EN page saint-charbel-prayer-for-a-miracle.html blockquote matches this exactly.

AR (certified catalog locales/ar/saint-charbel-novena-master-copy.json,
    key saint-charbel-novena.traditional.day-1.petition-after):
  petition-after = '، إن كانت لمجد الله وخير نفسي. آمين.'
  -> AR quote ends: "...النعمة التي أنا بحاجة إليها (اذكرها)، إن كانت لمجد الله وخير نفسي. آمين."
  i.e. adds ", if it be for the glory of God and the good of my soul." before Amen.

Other locales (petition-after, same key): fr='. Amen.' es='. Amén.'
  de='. Amen.' it='. Amen.' pl='. Amen.' pt='. Amém.'
  -> only AR carries the extra clause; all others match the EN shape.

## Source locators
- Live EN page: saint-charbel-prayer-for-a-miracle.html, "A Prayer to Saint Charbel for a Miracle" blockquote.
- EN certified catalog: locales/en/saint-charbel-novena-master-copy.json (petition-before/placeholder/petition-after/collect).
- AR certified catalog: locales/ar/saint-charbel-novena-master-copy.json (same keys).
- Monastery source page cited in the 2026-10-22 19:39 ruling: https://saintcharbel.com/novena-of-saint-charbel-en/ (Day 1).
- B1 content rulings recovered verbatim: /tmp/b1-rulings-recovered.md (chat_events 2026-10-22 19:37:20-19:45:00 EDT).
- Affected packet keys: miracle.invBefore/invPlaceholder/invAfter in locales/ar/mirrors/saint-charbel-prayer-for-a-miracle.json;
  FAQ a1Quote is built from petition-before only (unaffected by the clause).
