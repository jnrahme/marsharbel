# Rosary factory pack registry

Binaries (donor masters, art, ledgers, maps) live in the Google Drive archive:
https://drive.google.com/drive/folders/1o1_aNIzhKfV_NJ67BjQltVQY5-Rl6s-t (anyone-reader).
This file is the pointer index; verify sha256 after every restore. Per-episode release
folders on Drive are `en-<date>-release` (anyone-reader) with master + description + map + manifest + qa frames.

## en/glorious
- donor_file: donor.mp4  sha256: b6d539effdc3ca3a9b7d5f034441233851557c7e9d976603085a5efaacd7788e
- donor_note: EN49 master-en-nov18-glorious.mp4 (release generation)
- donor_audio_interval: [8.04, 1956.22]  map_intro_s: 9.68  credits_s: 65.285
- label: GLORIOUS MYSTERIES  vr_style: combined  credits_mode: commons_lines
- art g1 sha256: e53964dfb126367eae0d6e1adee542f436be8dc1cf4010309e779bbd4e0d295d
- art g2 sha256: fd3243c267e585c2b39b58f5c9d2029bba41b874a61782e36a9c7511797a220c
- art g3 sha256: 4d46d5157464da89e7ad3604f2b4a9b5d9287a8c3b1c0f4438d443227fdbeaf6
- art g4 sha256: 070e6c258249b342f1058efe8b337559fdb5ae4a256a1befcd6ecd8664a6555f
- art g5 sha256: 3b5e9f035a49165d8d9126e2d8a7a8338fb4cbc7e031a69b4b18b56992d33230

## en/joyful
- donor_file: donor.mp4  sha256: 383b109d8028af606121156b91ebc6a93381230b4fe1766d5d37f9158089c97e
- donor_note: EN47 master-en-nov16-joyful.mp4 (published generation)
- donor_audio_interval: [9.28, 1967.82]  map_intro_s: 9.28  credits_s: 65.285
- label: JOYFUL MYSTERIES  vr_style: combined  credits_mode: giotto_template
- art g1 sha256: d4c8f2fc6a1d9f77a83fc849b3ac8cc494d34b7c570cb0d8dee06f85d600e0eb
- art g2 sha256: 37c40908d448acaed032684d052c9f545850d1ac8f808f6f1c19d9e0f2cb0236
- art g3 sha256: 93103e1009b502f049a5b718de9cb2f359145006b0899966f7d285048471c39a
- art g4 sha256: 09c039952a4465fbdc31300a8530206f139c13c3a15c0ec96589b2103df6569d
- art g5 sha256: 508bac209cebeb34d143dfd2b943d98e8a76df8957e9a7b7acf16ddb315969de

## en/sorrowful
- donor_file: donor.mp4  sha256: 90a5d28f6741a6cd601ad4ecaeffa5b98cdf99902ed44494e6a10739057e615c
- donor_note: EN30 r3 master-en-oct30-sorrowful-r3.mp4 (published dwPP8Cy7fvY generation)
- donor_audio_interval: [7.92, 2095.54]  map_intro_s: 9.52  credits_s: 65.285
- label: SORROWFUL MYSTERIES  vr_style: split  credits_mode: ledger_credit_copy
- art g1 sha256: f6a796be995c6edc2bd74821dce3e1568e75b10b57dc0b5f10bbadc57f74604a
- art g2 sha256: 7895bb0eaa48ed7634724266d2c9311bf5d848f86f58da50502af5714d620753
- art g3 sha256: 5902c416034d7ee8e62a61d6ca5f0b7676cb2911e71df5cd172b12ebe3a6a953
- art g4 sha256: fa95ec0345c43149c1d9cf157548ca334970d0abd908e47f9610937ee0eff367
- art g5 sha256: dec94cc1f5d93e4673b478dce6567470cab7100d2938b48a6ce4d96d34e19e53

## en/luminous
- STAGED 2026-11-19. Donor: EN43 master-en-nov12-luminous.mp4 Drive 1fdcCl7yaURTfpO9nQI1AiS66u9-Dz89B
  sha256 1c9c453b50cd819e7665fe896cfbca8ab625f5ae804adee44fc58ca82d3445cd (published generation).
  AUDIO donor only: EN43 predates the factory card layout, so the pack sets donor_layout=legacy
  (frame NCC vs donor printed, not asserted). Art = the exact art-d1..d5 PNGs from the EN43
  release folder (sha-pinned below). Map converted from film-time-map-nov12.json old-generation
  kinds; texts from luminous-body-unique-texts-v3-1.json.
- art g1 sha256: dc57a1b3d61a190c8ced451831bc31f8d5b656a1d2745bd3b0e9cb220331133a
- art g2 sha256: 819a0d5bafe58e3d0c06635dd173e02ab2690e0ead41db321525ad09d724bf2f
- art g3 sha256: ebd6f9c2b3517b78c880dbfc319190661dbc7385a7e03db8c713947871632c10
- art g4 sha256: 371b07e9b2b4632b3db8c5c77f73a953c959f14388366d9f9b969cd900c43c71
- art g5 sha256: e9bc482565eaa9bdcaa769005f3500ea898c04f22850e670c5947654a0ac0c82

## ar/* (Arabic) - UNBUILT
- The factory has no RTL card renderer and no Arabic texts; build_day.py refuses --lang ar.
  Opening the lane is new work: Arabic texts, RTL rendering (Noto Sans Arabic, right-aligned;
  reference: ar-prayalong-release card style), then packs staged per RULE.
- MAR-65 is an ARTIFACT-scoped hold on exactly one artifact: the Nov 16 2026 AR Joyful release
  (folder 13lHJffVCSyWxkL1zGj0wQm480J7OF_BC) - never release it. It is NOT eligible as a pack
  source; the hold does not lift when the lane opens.
