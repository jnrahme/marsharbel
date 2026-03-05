(() => {
  const getLangCode = () => {
    const params = new URLSearchParams(window.location.search);
    return (params.get('lang') || 'en').toLowerCase();
  };

  const selectedLang = getLangCode();
  const contentLang = selectedLang === 'ar' ? 'ar' : selectedLang === 'fr' ? 'fr' : 'en';
  const isRtl = contentLang === 'ar';

  const COPY = {
    en: {
      pagePrefix: 'Page',
      pageConnector: 'of',
      read: 'Read Aloud',
      stop: 'Stop Reading',
      prev: 'Previous Page',
      next: 'Next Page',
      fallbackMessage: 'Please wait while we open the storybook.',
      evidenceTitle: 'Evidence for This Page',
      evidenceFallback: 'General source basis for this page.'
    },
    ar: {
      pagePrefix: 'الصفحة',
      pageConnector: 'من',
      read: 'استمع',
      stop: 'إيقاف القراءة',
      prev: 'الصفحة السابقة',
      next: 'الصفحة التالية',
      fallbackMessage: 'يرجى الانتظار بينما نفتح كتاب القصة.',
      evidenceTitle: 'الأدلة لهذه الصفحة',
      evidenceFallback: 'مصادر عامة لهذه الصفحة.'
    },
    fr: {
      pagePrefix: 'Page',
      pageConnector: 'sur',
      read: 'Lire à voix haute',
      stop: 'Arrêter la lecture',
      prev: 'Page précédente',
      next: 'Page suivante',
      fallbackMessage: "Veuillez patienter pendant l'ouverture du livre.",
      evidenceTitle: 'Sources de cette page',
      evidenceFallback: 'Sources générales pour cette page.'
    }
  };

  const EVIDENCE_SOURCES = {
    vaticanBeatification1965: {
      label: 'Vatican (Paul VI, Beatification, Dec 5, 1965)',
      url: 'https://www.vatican.va/content/paul-vi/fr/speeches/1965/documents/hf_p-vi_spe_19651205_charbel-makhlouf.html'
    },
    vaticanCanonization1977: {
      label: 'Vatican (Paul VI, Canonization, Oct 9, 1977)',
      url: 'https://www.vatican.va/content/paul-vi/fr/homilies/1977/documents/hf_p-vi_hom_19771009.html'
    },
    annayaArchive: {
      label: 'Monastery of Saint Maron (Annaya archive source)',
      url: 'https://web.archive.org/web/20160304235515/http://www.saintcharbel-annaya.com/home.php?lgid=0'
    },
    wikiBio: {
      label: 'Biography Cross-Check',
      url: 'https://en.wikipedia.org/wiki/Charbel_Makhlouf'
    },
    catholicSaints: {
      label: 'Devotional Tradition Source',
      url: 'https://catholicsaints.info/saint-charbel-makhlouf/'
    }
  };

  const EVIDENCE_PRESETS = {
    earlyLife: [
      {
        type: 'documented',
        claim: 'Early life milestones in Bekaa Kafra and family context are documented in monastic and biographical records.',
        sources: ['annayaArchive', 'wikiBio']
      }
    ],
    vocationFormation: [
      {
        type: 'documented',
        claim: 'The Vatican canonization homily gives the structured formation path: Mayfouk, Annaya, Kfifan, ordination in 1859.',
        sources: ['vaticanCanonization1977']
      }
    ],
    monasticYears: [
      {
        type: 'documented',
        claim: 'The Vatican text states 16 years of community life and 23 years of hermitage life before his death.',
        sources: ['vaticanCanonization1977']
      }
    ],
    waterLampTradition: [
      {
        type: 'tradition',
        claim: 'This page presents a monastic tradition account, not a formal miracle used as canonical proof by the Church.',
        sources: ['annayaArchive', 'catholicSaints']
      }
    ],
    deathAndAfter: [
      {
        type: 'documented',
        claim: 'Death date, growth of devotion, and canonical process context are supported by Vatican and monastic historical records.',
        sources: ['vaticanCanonization1977', 'annayaArchive']
      }
    ],
    beatificationCanonization: [
      {
        type: 'documented',
        claim: 'Beatification (Dec 5, 1965) and canonization (Oct 9, 1977) are official Church acts by Pope Paul VI.',
        sources: ['vaticanBeatification1965', 'vaticanCanonization1977']
      }
    ],
    nohadTestimony: [
      {
        type: 'testimony',
        claim: 'Nohad El Shami (1993) is a widely known post-canonization testimony in Charbel devotion.',
        sources: ['annayaArchive', 'wikiBio']
      }
    ],
    pastoralApplication: [
      {
        type: 'pastoral',
        claim: 'This page is pastoral guidance based on Saint Charbel’s documented life and witness.',
        sources: ['vaticanBeatification1965', 'vaticanCanonization1977']
      }
    ]
  };

  const STORIES = {
    en: [
      {
        title: 'A Child in the Mountains',
        body: 'Youssef Antoun Makhlouf was born on May 8, 1828, in Bekaa Kafra, Lebanon, and was baptized a few days later according to Maronite custom. He grew up in a mountain village where faith, work, and prayer shaped daily life.',
        prayer: 'Little prayer: Jesus, thank You for my home and my family.',
        heart: 'Heart Moment: God begins great stories in humble places.',
        scene: 'birth',
        evidencePreset: 'earlyLife',
        illustration: './media/storybook/images/event-01.png',
        audio: 'page-01.mp3'
      },
      {
        title: 'He Lost His Father Young',
        body: 'As Pope Paul VI recalled at beatification, he lost his father very early in life. This sorrow did not harden him; it helped form a deep dependence on God.',
        prayer: 'Little prayer: Lord, stay close when life feels heavy.',
        heart: 'Heart Moment: Pain can become a doorway to deeper faith.',
        scene: 'birth',
        evidencePreset: 'earlyLife',
        illustration: './media/storybook/images/event-02.png',
        audio: 'page-02.mp3'
      },
      {
        title: 'He Chose Silence and Prayer',
        body: 'As a boy, he loved silent prayer and often withdrew to quiet places to be with God. From childhood, he learned that listening is part of loving.',
        prayer: 'Little prayer: Jesus, teach me to listen in silence.',
        heart: 'Heart Moment: A quiet heart can hear God clearly.',
        scene: 'birth',
        evidencePreset: 'earlyLife',
        illustration: './media/storybook/images/event-03.png',
        audio: 'page-03.mp3'
      },
      {
        title: 'Witnesses Who Formed Him',
        body: 'His mother taught him to pray with trust, and local monastic witnesses helped shape his imagination for holiness. From early years, he saw that a life close to God was possible.',
        prayer: 'Little prayer: Lord, place good examples in my life.',
        heart: 'Heart Moment: Holy examples can change a child forever.',
        scene: 'birth',
        evidencePreset: 'earlyLife',
        illustration: './media/storybook/images/birth.png',
        audio: 'page-04.mp3'
      },
      {
        title: 'Entering Monastic Life (1851)',
        body: 'At age 23, he left home in 1851 to enter the Lebanese Maronite Order. Following the pattern recalled by Pope Paul VI, his formation began at Our Lady of Mayfouk and continued at Saint Maron of Annaya.',
        prayer: 'Little prayer: Lord, give me courage to follow You.',
        heart: 'Heart Moment: Holiness begins with a brave yes.',
        scene: 'vocation',
        evidencePreset: 'vocationFormation',
        illustration: './media/storybook/images/event-04.png',
        audio: 'page-05.mp3'
      },
      {
        title: 'Name, Vows, and a Costly Yes',
        body: 'He took the name Charbel and made solemn monastic vows in 1853: obedience, poverty, and chastity. Maronite biographies recount the pain of family separation, including his mother’s visit and her blessing that God would make him a saint.',
        prayer: 'Little prayer: Jesus, make my heart faithful and pure.',
        heart: 'Heart Moment: True love sometimes asks for tears and sacrifice.',
        scene: 'vocation',
        evidencePreset: 'vocationFormation',
        illustration: './media/storybook/images/vocation.png',
        audio: 'page-06.mp3'
      },
      {
        title: 'Studies at Kfifan',
        body: 'After profession, he studied theology at Saint Cyprian of Kfifan. These years formed his mind and heart in Scripture, liturgy, and monastic discipline.',
        prayer: 'Little prayer: Lord, guide my mind and my heart.',
        heart: 'Heart Moment: Truth studied with humility becomes wisdom.',
        scene: 'priest',
        evidencePreset: 'vocationFormation',
        illustration: './media/storybook/images/event-06.png',
        audio: 'page-07.mp3'
      },
      {
        title: 'Ordained Priest in 1859',
        body: 'He was ordained a Maronite priest on July 23, 1859, and returned to Annaya. From then on, the Eucharist and adoration stood at the center of his life.',
        prayer: 'Little prayer: Lord, help me honor You in prayer.',
        heart: 'Heart Moment: At the altar, his whole heart belonged to God.',
        scene: 'priest',
        evidencePreset: 'vocationFormation',
        illustration: './media/storybook/images/priest.png',
        audio: 'page-08.mp3'
      },
      {
        title: 'Sixteen Years of Community Life',
        body: 'From 1859 to 1875, he lived 16 years of community monastic life at Annaya. He combined contemplation and manual labor, showing that ordinary duties can be holy.',
        prayer: 'Little prayer: Jesus, bless the work of my hands.',
        heart: 'Heart Moment: Ordinary work can become extraordinary love.',
        scene: 'priest',
        evidencePreset: 'monasticYears',
        illustration: './media/storybook/images/event-07.png',
        audio: 'page-09.mp3'
      },
      {
        title: 'He Ordered His Whole Day Around God',
        body: 'Saint Charbel did not pray only when he felt like it. He prayed faithfully at fixed times, day after day, because love needs commitment. He let prayer guide his work, his speech, and his choices.',
        prayer: 'Little prayer: Lord, help me be faithful, not just emotional.',
        heart: 'Heart Moment: Steady faithfulness makes a strong heart.',
        scene: 'priest',
        evidencePreset: 'monasticYears',
        illustration: './media/storybook/images/event-09.png',
        audio: 'page-10.mp3'
      },
      {
        title: 'Traditional Account: The Water Lamp',
        body: 'According to cherished monastic tradition, when Father Charbel was an adult monk and his hermitage request was being discerned, a brother gave him a lamp filled with water instead of oil. He lit it and it burned; this was remembered as an early sign in his lifetime.',
        prayer: 'Little prayer: Lord, increase my trust in You.',
        heart: 'Heart Moment: God honors humble faith, even when others mock it.',
        scene: 'hermit',
        evidencePreset: 'waterLampTradition',
        illustration: './media/storybook/images/hermit.png',
        audio: 'page-11.mp3'
      },
      {
        title: 'Hermitage Life (From 1875)',
        body: 'In 1875, he received permission to live at the hermitage of Saints Peter and Paul near Annaya. He spent about 23 years there in solitude, prayer, penance, and manual labor until his death.',
        prayer: 'Little prayer: Lord, teach me to love a simple life.',
        heart: 'Heart Moment: Hidden faithfulness shines in God’s eyes.',
        scene: 'hermit',
        evidencePreset: 'monasticYears',
        illustration: './media/storybook/images/event-08.png',
        audio: 'page-12.mp3'
      },
      {
        title: 'He Worked the Land in Silence',
        body: 'At the hermitage, he lived very simply and worked with his hands. In that hidden life, labor and prayer stayed together. Even growing food became an offering to God.',
        prayer: 'Little prayer: Jesus, make my work an act of love.',
        heart: 'Heart Moment: Holiness can grow in fields, kitchens, and classrooms.',
        scene: 'hermit',
        evidencePreset: 'monasticYears',
        illustration: './media/storybook/images/event-20.png',
        audio: 'page-13.mp3'
      },
      {
        title: 'Prayer, Penance, and Simplicity',
        body: 'His life was marked by long prayer, silence, fasting, and self-denial. He was very serious about staying away from sin: he guarded his eyes, words, and choices, and avoided anything that pulled his heart away from God. He practiced asceticism not to be admired, but to remain pure and faithful.',
        prayer: 'Little prayer: Jesus, keep my heart clean and close to You.',
        heart: 'Heart Moment: Holiness grows when we say no to sin and yes to love.',
        scene: 'hermit',
        evidencePreset: 'monasticYears',
        illustration: './media/storybook/images/event-09.png',
        audio: 'page-14.mp3'
      },
      {
        title: 'He Fled Sin with Determination',
        body: 'Saint Charbel knew that sin harms the heart. He guarded his senses, avoided empty talk, and examined his conscience seriously so his love for God would stay undivided.',
        prayer: 'Little prayer: Lord, guard my eyes, words, and choices.',
        heart: 'Heart Moment: Purity is love that protects what is holy.',
        scene: 'hermit',
        evidencePreset: 'monasticYears',
        illustration: './media/storybook/images/event-09.png',
        audio: 'page-15.mp3'
      },
      {
        title: 'A Holy Death (December 24, 1898)',
        body: 'In December 1898, he became gravely ill during the Divine Liturgy and died on Christmas Eve, December 24, 1898. He finished life as he lived it: near the Eucharist, faithful to the end.',
        prayer: 'Little prayer: Lord, keep me faithful every day.',
        heart: 'Heart Moment: True love for God perseveres to the end.',
        scene: 'passing',
        evidencePreset: 'deathAndAfter',
        illustration: './media/storybook/images/event-10.png',
        audio: 'page-16.mp3'
      },
      {
        title: 'Pilgrims and Hope',
        body: 'After his death, many people came to pray at his tomb in Annaya, asking his intercession. People from different backgrounds found hope, peace, and healing.',
        prayer: 'Little prayer: Jesus, comfort all who suffer.',
        heart: 'Heart Moment: One hidden life can touch the whole world.',
        scene: 'healing',
        evidencePreset: 'deathAndAfter',
        illustration: './media/storybook/images/event-13.png',
        audio: 'page-17.mp3'
      },
      {
        title: 'Lights Reported at His Tomb',
        body: 'In the years after his burial, people in Annaya reported unusual lights around his tomb. These reports stirred many hearts to return to prayer.',
        prayer: 'Little prayer: Jesus, shine Your light in our darkness.',
        heart: 'Heart Moment: God can use small signs to wake up sleeping hearts.',
        scene: 'healing',
        evidencePreset: 'deathAndAfter',
        illustration: './media/storybook/images/event-14.png',
        audio: 'page-18.mp3'
      },
      {
        title: 'Remarkable Signs at the Tomb',
        body: 'When his tomb was opened, witnesses reported unusual signs, including notable preservation and fluid at the body. Monastery and church authorities documented these reports carefully over time.',
        prayer: 'Little prayer: Lord, lead me to truth and deeper faith.',
        heart: 'Heart Moment: Signs are invitations to return to God.',
        scene: 'healing',
        evidencePreset: 'deathAndAfter',
        illustration: './media/storybook/images/event-15.png',
        audio: 'page-19.mp3'
      },
      {
        title: 'His Cause Was Studied Carefully',
        body: 'The Church did not rush. Witnesses, records, and medical facts were examined carefully over time before declaring anything miraculous.',
        prayer: 'Little prayer: Lord, teach me faith with honesty.',
        heart: 'Heart Moment: Truth and faith walk together.',
        scene: 'healing',
        evidencePreset: 'deathAndAfter',
        illustration: './media/storybook/images/healing.png',
        audio: 'page-20.mp3'
      },
      {
        title: 'Miracles for Beatification',
        body: 'For beatification, healings attributed to his intercession were investigated and recognized by the Church after strict medical and theological review.',
        prayer: 'Little prayer: Jesus, visit the sick with mercy.',
        heart: 'Heart Moment: The Lord hears cries from hospital rooms and homes.',
        scene: 'healing',
        evidencePreset: 'beatificationCanonization',
        illustration: './media/storybook/images/event-16.png',
        audio: 'page-21.mp3'
      },
      {
        title: 'Miracle for Canonization',
        body: 'For canonization, the Church recognized an additional miracle in his cause after strict review. Only then was his sainthood proclaimed for the universal Church.',
        prayer: 'Little prayer: Lord, increase our trust in Your power.',
        heart: 'Heart Moment: Miracles point us to God, not to ourselves.',
        scene: 'legacy',
        evidencePreset: 'beatificationCanonization',
        illustration: './media/storybook/images/event-17.png',
        audio: 'page-22.mp3'
      },
      {
        title: 'The Healing of Nohad El Shami (1993)',
        body: 'One of the most famous post-canonization testimonies is the healing of Nohad El Shami in 1993 after severe paralysis. Her testimony spread widely and moved many people to repentance and prayer.',
        prayer: 'Little prayer: Jesus, heal body, mind, and soul.',
        heart: 'Heart Moment: The biggest miracle is returning to God with a changed heart.',
        scene: 'healing',
        evidencePreset: 'nohadTestimony',
        illustration: './media/storybook/images/event-18.png',
        audio: 'page-23.mp3'
      },
      {
        title: 'A Saint for Many Nations',
        body: 'Today, people from many countries and backgrounds come to Annaya. Saint Charbel’s life of prayer, sacrifice, and purity still calls people toward mercy.',
        prayer: 'Little prayer: Jesus, unite all hearts in peace.',
        heart: 'Heart Moment: Holiness gathers people who would never meet otherwise.',
        scene: 'unity',
        evidencePreset: 'deathAndAfter',
        illustration: './media/storybook/images/event-19.png',
        audio: 'page-24.mp3'
      },
      {
        title: 'His Holiness Was Simple and Real',
        body: 'He did not become a saint by one dramatic event. He became a saint by daily fidelity: prayer, work, sacrifice, humility, and love, repeated for many years.',
        prayer: 'Little prayer: Jesus, help me be faithful in little things.',
        heart: 'Heart Moment: Repeated small yeses become a holy life.',
        scene: 'unity',
        evidencePreset: 'pastoralApplication',
        illustration: './media/storybook/images/event-20.png',
        audio: 'page-25.mp3'
      },
      {
        title: 'Beatified and Canonized',
        body: 'Pope Paul VI beatified him on December 5, 1965, and canonized him on October 9, 1977. Saint Charbel’s message remains clear for children and adults: pray deeply, live simply, work honestly, and trust Jesus.',
        prayer: 'Little prayer: Saint Charbel, pray for us.',
        heart: 'Heart Moment: Saints are made by faithful love, one day at a time.',
        scene: 'legacy',
        evidencePreset: 'beatificationCanonization',
        illustration: './media/storybook/images/event-21.png',
        audio: 'page-26.mp3'
      },
      {
        title: 'How We Can Live Like Him Today',
        body: 'You can begin now: pray each day, tell the truth, help at home, forgive quickly, and turn away from sin. Saint Charbel shows that holiness is possible for ordinary people who love God sincerely.',
        prayer: 'Little prayer: Jesus, teach me to live with a faithful heart.',
        heart: 'Heart Moment: Your everyday choices can become a path to sainthood.',
        scene: 'legacy',
        evidencePreset: 'pastoralApplication',
        illustration: './media/storybook/images/event-22.png',
        audio: 'page-27.mp3'
      }
    ],
    ar: [
      {
        title: 'صبي في الجبال',
        body: 'وُلد يوسف أنطون مخلوف في 8 مايو 1828 في بقاعكفرا بلبنان. ومنذ صغره كان يحب الصلاة والهدوء ومساعدة الناس.',
        prayer: 'صلاة صغيرة: يا يسوع، علّمني أن أجد وقتاً هادئاً معك.',
        scene: 'birth'
      },
      {
        title: 'اختار الدير',
        body: 'عندما بلغ الثالثة والعشرين، ترك بيته ودخل دير مار مارون في عنايا سنة 1851. وهناك أخذ اسم شربل وقدّم حياته لله بالكامل.',
        prayer: 'صلاة صغيرة: يا رب، ساعدني أن أختار الطريق الذي يقودني إليك.',
        scene: 'vocation'
      },
      {
        title: 'كاهن المذبح',
        body: 'تعلّم وخدم ورُسم كاهناً سنة 1859. وكان الناس يرون تواضعه ومحبة قلبه للقربان واهتمامه بكل من يطلب الصلاة.',
        prayer: 'صلاة صغيرة: يا يسوع، اجعل قلبي متواضعاً وأميناً.',
        scene: 'priest'
      },
      {
        title: 'ثلاثة وأربعون عاماً في الحياة الرهبانية',
        body: 'عاش القديس شربل 43 سنة راهباً. وفي سنة 1875 انتقل إلى محبسة قريبة، فعاش بالصوم والعمل والصمت والصلاة العميقة.',
        prayer: 'صلاة صغيرة: يا الله، علّمني السلام وسط ضجيج الحياة.',
        scene: 'hermit'
      },
      {
        title: 'قداسه الأخير',
        body: 'في ديسمبر 1898 اشتد عليه المرض أثناء خدمة القداس الإلهي، ثم انتقل إلى بيت الآب في 24 ديسمبر 1898. وتحدّث الناس سريعاً عن قداسته وسلامه.',
        prayer: 'صلاة صغيرة: يا رب، ساعدني أن أبقى قريباً منك كل يوم.',
        scene: 'passing'
      },
      {
        title: 'رجاء وشفاء',
        body: 'بدأ الزوّار يأتون من أماكن كثيرة إلى ضريحه. والكنيسة تدرس الأعاجيب بدقة، وكانت الأعاجيب المعترف بها جزءاً من مسيرته نحو إعلان القداسة.',
        prayer: 'صلاة صغيرة: يا يسوع، امنح المتألّمين تعزية وشفاء.',
        scene: 'healing'
      },
      {
        title: 'قديس للوحدة في المسيح',
        body: 'يلهم القديس شربل مسيحيين في العالم كله، وحتى أشخاصاً من تقاليد مختلفة يبحثون عن الله. حياته تشير إلى التوبة والرحمة والمحبة.',
        prayer: 'صلاة صغيرة: يا يسوع، وحّد قلوبنا في محبتك.',
        scene: 'unity'
      },
      {
        title: 'قديس للكنيسة كلها',
        body: 'أعلنه البابا بولس السادس طوباوياً في 5 ديسمبر 1965 وقديساً في 9 أكتوبر 1977. وما زالت رسالته تنير القلوب: صلاة عميقة ومحبة واسعة وثقة بيسوع.',
        prayer: 'صلاة صغيرة: يا مار شربل، صلِّ لأجلنا.',
        scene: 'legacy'
      }
    ],
    fr: [
      {
        title: 'Un garçon des montagnes',
        body: 'Youssef Antoun Makhlouf est né le 8 mai 1828 à Bkaakafra, au Liban. Enfant, il aimait la prière, le silence et le service des autres.',
        prayer: 'Petite prière : Jésus, aide-moi à trouver des moments de silence avec Toi.',
        scene: 'birth'
      },
      {
        title: 'Il choisit le monastère',
        body: "À 23 ans, il quitte sa maison et entre au monastère Saint-Maron d'Annaya en 1851. Il y prend le nom de Charbel et se donne entièrement à Dieu.",
        prayer: 'Petite prière : Seigneur, aide-moi à choisir ce qui me conduit vers Toi.',
        scene: 'vocation'
      },
      {
        title: "Prêtre de l'autel",
        body: 'Après ses années de formation, il est ordonné prêtre en 1859. Les gens voyaient sa profonde humilité et son amour de la Sainte Eucharistie.',
        prayer: 'Petite prière : Jésus, rends mon cœur humble et fidèle.',
        scene: 'priest'
      },
      {
        title: 'Quarante-trois ans de vie monastique',
        body: "Saint Charbel a vécu 43 ans comme moine. En 1875, il part à l'ermitage voisin et mène une vie de jeûne, de travail, de silence et de prière.",
        prayer: 'Petite prière : Mon Dieu, apprends-moi la paix quand tout est bruyant.',
        scene: 'hermit'
      },
      {
        title: 'Sa dernière messe',
        body: 'En décembre 1898, il tombe gravement malade pendant la liturgie, puis meurt le 24 décembre 1898. Très vite, les fidèles parlent de sa sainteté.',
        prayer: 'Petite prière : Seigneur, garde-moi près de Toi chaque jour.',
        scene: 'passing'
      },
      {
        title: 'Espérance et guérisons',
        body: "Des pèlerins de nombreux pays visitent son tombeau. L'Église étudie les miracles avec sérieux, et des guérisons reconnues ont soutenu sa cause.",
        prayer: 'Petite prière : Jésus, apporte consolation et guérison aux personnes qui souffrent.',
        scene: 'healing'
      },
      {
        title: "Un saint pour l'unité dans le Christ",
        body: "Saint Charbel inspire des chrétiens du monde entier, ainsi que des personnes d'autres traditions. Sa vie appelle à la conversion, à la miséricorde et à l'amour.",
        prayer: 'Petite prière : Jésus, unis nos cœurs dans Ton amour.',
        scene: 'unity'
      },
      {
        title: "Canonisé pour l'Église universelle",
        body: 'Le pape Paul VI le béatifie le 5 décembre 1965 et le canonise le 9 octobre 1977. Son message reste vivant : prier profondément, aimer largement, faire confiance à Jésus.',
        prayer: 'Petite prière : Saint Charbel, prie pour nous.',
        scene: 'legacy'
      }
    ]
  };

  const UI = COPY[contentLang];
  const pages = STORIES[contentLang];
  const AUDIO_BASE = {
    en: './media/storybook/en',
    ar: './media/storybook/ar',
    fr: './media/storybook/fr'
  };
  const SCENE_IMAGE_BASE = './media/storybook/images';
  const SCENE_IMAGES = {
    birth: `${SCENE_IMAGE_BASE}/birth.png`,
    vocation: `${SCENE_IMAGE_BASE}/vocation.png`,
    priest: `${SCENE_IMAGE_BASE}/priest.png`,
    hermit: `${SCENE_IMAGE_BASE}/hermit.png`,
    passing: `${SCENE_IMAGE_BASE}/passing.png`,
    healing: `${SCENE_IMAGE_BASE}/healing.png`,
    unity: `${SCENE_IMAGE_BASE}/unity.png`,
    legacy: `${SCENE_IMAGE_BASE}/legacy.png`
  };
  const VOICE_PACK_STORAGE_KEY = `storybook_voice_pack_${contentLang}`;
  const BROWSER_VOICE_PREF_KEY = 'rosary_audio_voice_pref';
  const VOICE_PACKS = {
    en: [
      { id: 'elevenlabs-charbel', label: 'ElevenLabs Story Voice (Recommended)', type: 'clips', base: './media/storybook/en-elevenlabs' },
      { id: 'studio-british', label: 'Studio British', type: 'clips', base: './media/storybook/en' },
      { id: 'browser', label: 'Browser Voice (Device)', type: 'browser' }
    ],
    ar: [
      { id: 'studio-ar', label: 'Studio Arabic (Recommended)', type: 'clips', base: './media/storybook/ar' },
      { id: 'browser', label: 'Browser Voice (Device)', type: 'browser' }
    ],
    fr: [
      { id: 'studio-fr', label: 'Studio French (Recommended)', type: 'clips', base: './media/storybook/fr' },
      { id: 'browser', label: 'Browser Voice (Device)', type: 'browser' }
    ]
  };

  const el = {
    panel: document.querySelector('.storybook-panel'),
    frame: document.querySelector('.storybook'),
    step: document.getElementById('story-step'),
    title: document.getElementById('story-title'),
    body: document.getElementById('story-body'),
    prayer: document.getElementById('story-prayer'),
    heart: document.getElementById('story-heart'),
    art: document.getElementById('story-illustration'),
    evidenceTitle: document.getElementById('story-evidence-title'),
    evidenceList: document.getElementById('story-evidence-list'),
    pack: document.getElementById('story-voice-pack'),
    prev: document.getElementById('story-prev'),
    next: document.getElementById('story-next'),
    read: document.getElementById('story-read')
  };

  if (!el.step || !el.title || !el.body || !el.prayer || !el.heart || !el.art || !el.evidenceTitle || !el.evidenceList || !el.pack || !el.prev || !el.next || !el.read || !el.panel || !el.frame) {
    return;
  }

  const updateUiLabels = () => {
    el.prev.textContent = UI.prev;
    el.next.textContent = UI.next;
    el.read.textContent = UI.read;
    el.evidenceTitle.textContent = UI.evidenceTitle;
  };

  const linkMarkup = sourceId => {
    const source = EVIDENCE_SOURCES[sourceId];
    if (!source) return '';
    return `<a href="${source.url}" target="_blank" rel="noopener">${source.label}</a>`;
  };

  const getEvidenceForPage = (_pageIndex, page) => {
    if (contentLang !== 'en') {
      return [
        {
          type: 'documented',
          claim: UI.evidenceFallback,
          sources: ['vaticanBeatification1965', 'vaticanCanonization1977']
        }
      ];
    }
    if (Array.isArray(page.evidence) && page.evidence.length) {
      return page.evidence;
    }
    if (page.evidencePreset && EVIDENCE_PRESETS[page.evidencePreset]) {
      return EVIDENCE_PRESETS[page.evidencePreset];
    }
    return EVIDENCE_PRESETS.pastoralApplication;
  };

  const renderEvidence = (pageIndex, page) => {
    const items = getEvidenceForPage(pageIndex, page);
    el.evidenceList.innerHTML = items.map(item => {
      const sourceLinks = (item.sources || []).map(linkMarkup).filter(Boolean).join(' | ');
      return `
        <li>
          <span class="story-evidence-type">${item.type}</span>
          ${item.claim}
          <span class="story-evidence-links">${sourceLinks}</span>
        </li>
      `;
    }).join('');
  };

  const sceneMarkup = (scene, illustration) => `
    <div class="scene-art scene-${scene}">
      <img class="scene-photo" src="${illustration || './gallery/charbel-portrait.jpg'}" alt="" loading="lazy" />
      <div class="scene-photo-overlay" aria-hidden="true"></div>
    </div>
  `;

  let index = 0;
  let reading = false;
  let activeUtterance = null;
  let activeClip = null;
  let availableVoicePacks = [];
  let activeVoicePack = null;
  const clipAvailability = new Map();
  const pageIndicator = idx => `${UI.pagePrefix} ${idx + 1} ${UI.pageConnector} ${pages.length}`;
  const storyUiFlags = {
    showBack: true,
    showToggle: true,
    showSkip: true,
    showOpen: false,
    showAutoPrayer: false,
    showNext: false,
    showCountdown: false,
    showSubtitle: true,
    showProgress: true,
    showVoiceSelect: false,
    prevSelector: '#story-prev',
    nextSelector: '#story-next',
    openHref: window.location.href
  };

  const syncAudioContext = extra => {
    const page = pages[index];
    if (!page || !window.RosaryAudioContext?.set) {
      return;
    }
    const text = `${page.title}. ${page.body} ${page.prayer} ${page.heart || ''}`.trim();
    window.RosaryAudioContext.set({
      source: 'storybook',
      mode: 'storybook',
      title: page.title,
      subtitle: pageIndicator(index),
      stage: 'Storybook',
      url: window.location.href,
      text,
      estimatedDurationMs: Math.max(3000, Math.round((text.trim().split(/\s+/).length / 130) * 60000)),
      ui: storyUiFlags,
      voicePack: activeVoicePack?.id || null,
      ...extra
    });
  };

  const readVoicePackPref = () => {
    try {
      return localStorage.getItem(VOICE_PACK_STORAGE_KEY) || '';
    } catch (_) {
      return '';
    }
  };

  const selectPreferredBrowserVoice = () => {
    if (!('speechSynthesis' in window)) {
      return null;
    }
    const voices = window.speechSynthesis.getVoices() || [];
    if (!voices.length) {
      return null;
    }

    try {
      const pref = JSON.parse(localStorage.getItem(BROWSER_VOICE_PREF_KEY) || '{}');
      if (pref?.name) {
        const match = voices.find(voice => voice.name === pref.name && (!pref.lang || voice.lang === pref.lang));
        if (match) {
          return match;
        }
      }
    } catch (_) {
      // no-op
    }

    const normalized = voices.map(voice => ({
      voice,
      name: (voice.name || '').toLowerCase(),
      lang: (voice.lang || '').toLowerCase()
    }));

    const preferred = normalized.find(item =>
      item.name.includes('google uk english female') || item.name.includes('uk english female')
    );
    if (preferred) return preferred.voice;

    const enGbFemale = normalized.find(item =>
      item.lang.startsWith('en-gb') && (item.name.includes('female') || item.name.includes('woman'))
    );
    if (enGbFemale) return enGbFemale.voice;

    const enGbAny = normalized.find(item => item.lang.startsWith('en-gb'));
    if (enGbAny) return enGbAny.voice;

    const enAny = normalized.find(item => item.lang.startsWith('en'));
    return (enAny && enAny.voice) || voices[0];
  };

  const writeVoicePackPref = packId => {
    try {
      localStorage.setItem(VOICE_PACK_STORAGE_KEY, packId);
    } catch (_) {
      // no-op
    }
  };

  const getBaseVoicePacks = () => VOICE_PACKS[contentLang] || VOICE_PACKS.en;
  const isLocalFilePreview = () => window.location.protocol === 'file:';

  const resolveVoicePacks = async () => {
    const candidates = getBaseVoicePacks();
    const checks = await Promise.all(candidates.map(async (pack) => {
      if (pack.type === 'browser') {
        return 'speechSynthesis' in window;
      }
      if (!pages.every(page => Boolean(page.audio))) {
        return false;
      }
      const probeUrl = `${pack.base}/page-01.mp3`;
      return checkClipAvailability(probeUrl);
    }));
    availableVoicePacks = candidates.filter((_, idx) => checks[idx]);
    if (!availableVoicePacks.length) {
      availableVoicePacks = [{ id: 'browser', label: 'Browser Voice (Device)', type: 'browser' }];
    }
  };

  const setActiveVoicePack = packId => {
    const selected = availableVoicePacks.find(pack => pack.id === packId);
    activeVoicePack = selected || availableVoicePacks[0] || null;
    if (activeVoicePack) {
      writeVoicePackPref(activeVoicePack.id);
    }
  };

  const getPreferredInitialVoicePack = () => {
    const elevenLabsPack = availableVoicePacks.find(pack => pack.id === 'elevenlabs-charbel');
    if (contentLang === 'en' && elevenLabsPack) {
      return elevenLabsPack.id;
    }
    return readVoicePackPref();
  };

  const renderVoicePackSelect = () => {
    el.pack.innerHTML = '';
    availableVoicePacks.forEach(pack => {
      const option = document.createElement('option');
      option.value = pack.id;
      option.textContent = pack.label;
      if (activeVoicePack && pack.id === activeVoicePack.id) {
        option.selected = true;
      }
      el.pack.appendChild(option);
    });
    if (availableVoicePacks.length <= 1) {
      el.pack.disabled = true;
    }
  };

  const stopReading = () => {
    if (activeClip) {
      activeClip.pause();
      activeClip.currentTime = 0;
      activeClip = null;
    }
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    reading = false;
    activeUtterance = null;
    el.read.textContent = UI.read;
    syncAudioContext({ playing: false, paused: false, completed: false });
  };

  const animatePageTurn = () => {
    el.panel.classList.remove('is-turning');
    window.requestAnimationFrame(() => {
      el.panel.classList.add('is-turning');
    });
  };

  const render = () => {
    const page = pages[index];
    const illustration = page.illustration || SCENE_IMAGES[page.scene] || './gallery/charbel-portrait.jpg';
    el.step.textContent = `${UI.pagePrefix} ${index + 1} ${UI.pageConnector} ${pages.length}`;
    el.title.textContent = page.title;
    el.body.textContent = page.body;
    el.prayer.textContent = page.prayer;
    el.heart.textContent = page.heart || '';
    el.heart.hidden = !page.heart;
    el.art.innerHTML = sceneMarkup(page.scene, illustration);
    renderEvidence(index, page);
    el.art.setAttribute('data-scene', page.scene);
    el.prev.disabled = index === 0;
    el.next.disabled = index === pages.length - 1;
    syncAudioContext({ playing: false, paused: false, completed: false });
    animatePageTurn();
  };

  const getClipUrl = page => {
    if (!page.audio || !activeVoicePack || activeVoicePack.type !== 'clips') return null;
    return `${activeVoicePack.base}/${page.audio}`;
  };

  const checkClipAvailability = async clipUrl => {
    if (!clipUrl) return false;
    if (isLocalFilePreview()) {
      clipAvailability.set(clipUrl, true);
      return true;
    }
    if (clipAvailability.has(clipUrl)) {
      return clipAvailability.get(clipUrl);
    }
    try {
      const response = await fetch(clipUrl, { method: 'HEAD' });
      const ok = response.ok;
      clipAvailability.set(clipUrl, ok);
      return ok;
    } catch (_) {
      clipAvailability.set(clipUrl, false);
      return false;
    }
  };

  const readCurrentPage = async () => {
    if (reading) {
      stopReading();
      return;
    }

    const page = pages[index];
    const clipUrl = getClipUrl(page);
    const hasClip = await checkClipAvailability(clipUrl);

    stopReading();

    if (hasClip && clipUrl) {
      try {
        const clip = new Audio(clipUrl);
        clip.onended = () => {
          reading = false;
          activeClip = null;
          el.read.textContent = UI.read;
          syncAudioContext({ mode: 'prerendered', playing: false, paused: false, completed: false });
        };
        clip.onerror = () => {
          reading = false;
          activeClip = null;
          el.read.textContent = UI.read;
          syncAudioContext({ mode: 'prerendered', playing: false, paused: false, completed: false });
        };
        activeClip = clip;
        reading = true;
        el.read.textContent = UI.stop;
        syncAudioContext({ mode: 'prerendered', playing: true, paused: false, completed: false, startedAt: Date.now() });
        await clip.play();
        return;
      } catch (_) {
        activeClip = null;
      }
    }

    if (!('speechSynthesis' in window)) {
      return;
    }

    const utterance = new SpeechSynthesisUtterance(`${page.title}. ${page.body} ${page.prayer} ${page.heart || ''}`.trim());
    utterance.rate = 0.92;
    utterance.pitch = 1.02;
    utterance.volume = 0.98;
    utterance.lang = contentLang === 'ar' ? 'ar-LB' : contentLang === 'fr' ? 'fr-FR' : 'en-US';
    utterance.voice = selectPreferredBrowserVoice();
    utterance.onend = () => {
      reading = false;
      activeUtterance = null;
      el.read.textContent = UI.read;
      syncAudioContext({ mode: 'speech', playing: false, paused: false, completed: false });
    };
    utterance.onerror = () => {
      reading = false;
      activeUtterance = null;
      el.read.textContent = UI.read;
      syncAudioContext({ mode: 'speech', playing: false, paused: false, completed: false });
    };

    reading = true;
    activeUtterance = utterance;
    el.read.textContent = UI.stop;
    syncAudioContext({ mode: 'speech', playing: true, paused: false, completed: false, startedAt: Date.now() });
    window.speechSynthesis.speak(utterance);
  };

  const movePage = direction => {
    stopReading();
    const nextIndex = Math.max(0, Math.min(pages.length - 1, index + direction));
    if (nextIndex === index) return;
    index = nextIndex;
    render();
  };

  el.prev.addEventListener('click', () => movePage(-1));
  el.next.addEventListener('click', () => movePage(1));
  el.read.addEventListener('click', readCurrentPage);
  el.pack.addEventListener('change', () => {
    setActiveVoicePack(el.pack.value);
    stopReading();
    syncAudioContext({ voicePack: activeVoicePack?.id || null });
  });

  document.addEventListener('keydown', event => {
    if (event.target && ['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) {
      return;
    }
    if (event.key === 'ArrowRight') {
      movePage(isRtl ? -1 : 1);
    }
    if (event.key === 'ArrowLeft') {
      movePage(isRtl ? 1 : -1);
    }
  });

  window.addEventListener('beforeunload', stopReading);
  window.addEventListener('rosary-audio-close', stopReading);

  if (isRtl) {
    el.frame.classList.add('is-rtl');
    el.frame.setAttribute('dir', 'rtl');
  } else {
    el.frame.setAttribute('dir', 'ltr');
  }

  if (!pages || !pages.length) {
    el.body.textContent = UI.fallbackMessage;
    return;
  }

  const init = async () => {
    await resolveVoicePacks();
    setActiveVoicePack(getPreferredInitialVoicePack());
    renderVoicePackSelect();
    updateUiLabels();
    render();
  };

  init();
})();
