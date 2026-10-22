# YouTube Retention-Focused Editing: Quantified Rules for an Editing-Assistant Skill (as of Oct 2026)

Evidence tags used below: **[OFFICIAL]** = YouTube/Google documentation or a YouTube employee; **[DATA]** = measured study or count (peer-reviewed or a published count); **[MEMO]** = the leaked 2024 MrBeast Productions handbook ("How to Succeed in MrBeast Production"); **[CREATOR]** = named creator or editor heuristic; **[VENDOR]** = tool-vendor or marketing blog; numbers usually unsourced, so treat as unverified. Method note: the egress proxy blocked direct page fetches (support.google.com, tubefilter.com, the MrBeast PDF host and others returned DNS or 403 errors), so every finding below comes from search-result extracts of the cited pages. Exact wording should be spot-checked before it is quoted verbatim to the user.

## 1. Hooks: the first 0–30 seconds (and the first minute)

### Takeaway
YouTube's only official "hook" metric is the share of viewers still watching at 30 s (the "Intro" key moment). There is no official target. Creator-tool benchmarks cluster around 50–70% at 30 s, and vidIQ suggests at least 60%. The strongest practitioner evidence (the MrBeast memo) says the first minute is where most viewers leave, and recommends front-loading the best moments within the first 60 s. Branded intros should go, or move after the hook.

### Cited Findings
- [OFFICIAL] YouTube Studio's "Key moments for audience retention" defines **Intro** as "what percentage of your audience still watched your video after the first 30 seconds". YouTube says a high figure suggests the opening matched the title and thumbnail, and that you can raise it by revising the title or thumbnail or by testing different openings. — [YouTube Help: Measure key moments for audience retention](https://support.google.com/youtube/answer/9314415?hl=en)
- [OFFICIAL] Key-moment labels appear only for videos **≥60 s long with ≥100 views**, and not every video gets every label. — [YouTube Help](https://support.google.com/youtube/answer/9314415?hl=en)
- [OFFICIAL, secondary] Todd Beaupré (YouTube) is quoted as saying "For many viewers, the video intro is the new thumbnail", because the homepage and search increasingly use inline video previews instead of static thumbnails. — [TubeBuddy: The Death of Intros](https://www.tubebuddy.com/blog/video-intro-death-youtube-custom-thumbnail/)
- [OFFICIAL? unverified] Several blogs say YouTube's Creator Insider channel "confirmed in 2025 that creators should establish value within seven seconds". I found no primary Creator Insider transcript. — [Elite Content Marketer](https://www.elitecontentmarketer.com/get-more-youtube-views-for-free/); [Creator Playbook](https://www.creator-playbook.com/articles/your-intro-sucks-fix-first-30-seconds)
- [MEMO] "As with almost every video on Youtube, the first minute has the most loss. This is why we freak out so much about the first minute." The memo reportedly says the channel "lost 21 million viewers in the first minute" of one video, a rate that was still better than the platform average. — [Alexander Jarvis copy of memo](https://www.alexanderjarvis.com/memo-how-to-succeed-in-mrbeast-production/); [Creator Handbook summary](https://www.creatorhandbook.net/leaked-document-allegedly-reveals-mrbeasts-secrets-to-youtube-success-the-key-takeaways/)
- [MEMO] The memo recommends teasing the video's best moments within the first 60 s, then moving from "hype to execution". The hook must match the title and thumbnail. — [OMR (German)](https://omr.com/de/daily/mrbeast-doc-pdf-leak); [Daniel Scrivner summary](https://www.danielscrivner.com/how-to-succeed-in-mrbeast-production-summary/)
- [MEMO, provenance] Rosanna Pansino posted the document in Aug 2024. Two anonymous former MrBeast producers confirmed it to Passionfruit, but other outlets call it unconfirmed. — [NetInfluencer](https://www.netinfluencer.com/mrbeast-productions-leaked-internal-document-rosanna-pansino/)
- [CREATOR] Paddy Galloway (Shorts context, Apr 2023): "make your first second really punchy and engaging to hook viewers early… Treat your intro like a thumbnail." — [Paddy Galloway on X](https://x.com/PaddyG96/status/1646898373365051392?lang=en)
- [VENDOR] 30-s benchmarks disagree: Subscribr says 50–70% at 30 s and 40–60% at 60 s. vidIQ says ≥60%, with the best hooks above 65%; its own six-video sample ranged from 38.1% to 67.9%. — [Subscribr](https://subscribr.ai/youtube-strategy/youtube-analytics-improve-video-hooks-intros); [vidIQ](https://vidiq.com/blog/post/increase-audience-retention-youtube/)
- [DATA, small-n, contrarian] One creator analysed 63 of his own retention graphs to test whether 30-s retention predicts promotion and **could not confirm a pattern**. He also notes that YouTube has never said 30-s retention is an algorithm input. — [SocialVideoPlaza: 63 hooks tested](https://www.socialvideoplaza.com/en/articles/what-to-say-youtube-intro-hook)
- [VENDOR] Suggested three-phase opening: a pattern interrupt at **0–5 s**, a specific payoff promise at **5–15 s**, and a commitment hook at **15–30 s**. Record or write the hook last, after the edit, so it promises only what the video delivers. A sharp drop in the first 30 s points to a hook problem, and a slow slide through the middle points to pacing. — [Prepublish: first 30 seconds](https://prepublish.ai/guides/first-30-seconds); [OutlierKit](https://outlierkit.com/resources/youtube-hooks-and-retention/)
- [VENDOR] Advice on intro length: cut branded intros entirely or keep them under 5 s (some say under 10 s), and place any brand card **after** the hook. — [Creator Playbook](https://www.creator-playbook.com/articles/your-intro-sucks-fix-first-30-seconds); [vidIQ algorithm guide](https://vidiq.com/blog/post/understanding-youtube-algorithm/)

### Inferences
- Proposed rule for the skill: **0:00–0:01** opens on the most striking visual of the video (a solved state, a record time, the weird scramble, the gameplay climax), with no logo or channel sting. **0:00–0:07** states the promise or payoff (this follows the unverified "7 s" guidance and Galloway's "first second" advice). **0:07–0:30** shows 2–3 quick previews of later payoffs (MrBeast-style teasing), each 1–3 s, with on-screen text naming what is coming. Any channel-brand card is ≤2 s and comes after about 0:20–0:30.
- Because "Intro" is measured at exactly 30 s, the skill should treat 0:00–0:30 as the densest-edited stretch of a long-form video, with the most visual changes per second (see Section 2).
- The skill should benchmark against the creator's own "typical" retention (Section 10), not against 70%. Absolute 30-s targets are vendor folklore, and at least one small analysis found no link to promotion.

### Gaps
- I found no primary YouTube document giving a numeric 30-s target, and no primary Creator Insider source for the "7 seconds" claim.
- I found no measured data on how many visual changes per second appear in the first 30 s of top videos. All numbers are heuristics.

## 2. Pacing: shot length, cuts per minute, pattern interrupts

### Takeaway
The best hard data point is a Tubefilter count of MrBeast: **38 cuts/min** in a Mar 2023 video against **23 cuts/min** in an early-2024 video, after he publicly said he had slowed down. Film-studies data puts modern Hollywood average shot length at about 2.5–4 s. Educational research (Guo et al. 2014) favours short segments and hand-drawn or "Khan-style" visuals over slides or screencasts. Since 2024 the industry has moved away from "overstimulated" retention editing. "Visual change every 3–8 s" is a heuristic, not measured data.

### Cited Findings
- [DATA, n=2 one-minute samples] Tubefilter counted cuts in one minute from the midpoint of each video: the **Mar 2023 MrBeast video had 38 cuts/min, and "I Survived 7 Days In An Abandoned City" (2024) had 23**. The newer video used longer, zoomed-out shots and calmer dialogue. — [Tubefilter, 4 Mar 2024](https://tubefilter.com/2024/03/04/mrbeast-editing-style-number-of-cuts-per-video/)
- [CREATOR/OFFICIAL-ish] On 3 Mar 2024 MrBeast posted on X that over the past year his team had slowed videos down, emphasised storytelling, let scenes breathe, yelled less and made videos longer, and that views had "skyrocketed". He urged creators to drop the ultra-fast-paced style. Tubefilter notes that the 90-day average views rose from about 60M (Aug 2022) to about 150M but says it cannot attribute this to the pacing change. — [Tubefilter](https://tubefilter.com/2024/03/04/mrbeast-editing-style-number-of-cuts-per-video/); [Benzinga](https://www.benzinga.com/news/24/03/37448542/mrbeast-reveals-secret-sauce-to-skyrocketing-youtube-views-slower-longer-videos-could-be-the-future)
- [DATA/reporting] The 2024 backlash against "retention editing" (loud SFX, fast cuts, flashing effects, no pauses) is documented. Noah Kettle called it the "Beastification of YouTube", and YPulse (Apr 2024) reported young viewers tiring of it and favouring slower, candid videos. — [GIGAZINE, Apr 2024](https://gigazine.net/gsc_news/en/20240403-retention-editing-beastification-may-be-end); [YPulse](https://www.ypulse.com/newsfeed/2024/04/02/young-people-are-getting-tired-of-retention-editing-on-youtube/)
- [MEMO] Minutes 3–6 should have fast scene changes and "simple, stimulating content tied to the story". — [Daniel Scrivner summary](https://www.danielscrivner.com/how-to-succeed-in-mrbeast-production-summary/)
- [DATA, older] Cutting et al. (i-Perception 2011) measured 160 English-language films (1935–2010) and found shot lengths steadily shortening. Cutting has said ASL fell from about **12 s (1930) to about 2.5 s** today, and another report gives **8–10 s in the 1960s and 3–4 s by 2005**. Cutting rejects "MTV caused it", since the decline predates MTV and continued at the same rate afterwards. — [PMC: Cutting et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3485803/); [FlowingData](https://flowingdata.com/2014/09/22/evolution-of-movies/)
- [DATA, older, 2014] Guo, Kim & Rubin analysed **6.9M video-watching sessions** across 4 edX courses. Shorter videos were much more engaging, and the authors recommend segmenting into chunks **<6 min**. Talking head interspersed with slides beat slides alone. **Khan-style tablet drawing beat PowerPoint slides and code screencasts**, and informal settings with extemporaneous speech worked well. — [Guo et al., L@S 2014 PDF](https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf); [UBC summary](https://blogs.ubc.ca/videolearninghub/?p=569)
- [VENDOR] Faceless or educational content: "visual should change every **3–5 s**", and text overlays, zooms, animated graphics and slow Ken Burns pushes count as a change. Another source says faceless videos should change every **5–10 s** and that a still image held for 30 s drives viewers away. A third suggests **10–15 s** in the opening stretch. These figures conflict and none is sourced. — [Fluxnote](https://fluxnote.io/guides/faceless-channel-retention-strategies-2026); [Air.io advanced retention editing](https://air.io/en/youtube-hacks/advanced-retention-editing-cutting-patterns-that-keep-viewers-past-minute-8); [Gyre](https://gyre.pro/blog/how-to-improve-audience-retention-on-youtube-top-tips)
- [VENDOR, weak] High-performing Shorts reportedly average **one cut every 2–4 s**. — [OpusClip](https://opus.pro/blog/ideal-youtube-shorts-length-format-retention)
- [VENDOR] Vary the pace: speed through less important sections and slow down for key points, because uniform pacing flattens retention. — [Pippit](https://www.pippit.ai/resource/top-tips-for-building-audience-retention-on-faceless-youtube-channels)
- [CREATOR, anecdotal] Gaming-channel briefs ask for jump cuts, meme inserts, zooms and subtitles in 8–15 min videos, with viewers "laughing every few seconds, never waiting for the next highlight". — [Freelancer.de listing](https://www.freelancer.de/projects/sound-design/gaming-youtube-video-editor)

### Inferences
- Derived from the Tubefilter counts: 38 cuts/min is an average shot of about **1.6 s**, and 23 cuts/min is about **2.6 s**. Even MrBeast's "slowed-down" style changes picture every 2–3 s, which matches modern film ASL. That is a ceiling for spectacle entertainment, not a target for tutorials.
- Proposed defaults for the skill. These are heuristics, so the skill should label them that way to the user:
  - **Cubing long-form (explainer, story, review):** visual change, meaning any cut, zoom, text pop or B-roll insert, every **3–6 s** on average. In step-by-step algorithm demonstrations, allow holds of up to **8–10 s** while the hands execute a move sequence, because the viewer needs to read the move. Use an on-screen move notation overlay so the "change" comes from text, not cuts.
  - **Gaming long-form:** visual change every **2–4 s**. Cut all dead air, loading screens and menus. Comedic beats (freeze, zoom, caption) roughly every **15–30 s** in highlight sections.
  - **Shorts:** a cut or visual change every **1.5–3 s**, and motion in frame 1.
  - **Pace modulation:** after a dense 20–40 s stretch, allow one "breathing" shot of 4–8 s with no new graphic. This reflects the post-2024 move away from constant overstimulation.
- Guo et al.'s "Khan-style tablet drawing > slides/screencast" finding supports showing **hands physically turning a cube** with drawn or animated annotations over static diagrams or plain screen recordings. That evidence is old (2014, MOOC learners).

### Gaps
- I found no measured ASL or cuts-per-minute analysis for Ali Abdaal, Veritasium, Mark Rober or any cubing or gaming channel. The only creator-specific count is the two-minute MrBeast sample.
- I found no controlled study linking cut frequency to YouTube retention. A skill could gather this from the user's own videos by counting cuts per minute alongside the retention curve.

## 3. B-roll: frequency, duration, timing to speech, J/L cuts

### Takeaway
Editing guides converge on a typical B-roll hold of **2–5 s**, shorter for detail or reaction shots (1–3 s) and longer for documentary-style shots (6–10 s). A static B-roll held for about 8 s under narration "starts to drag". I found no measured data on timing B-roll to a keyword. "Cut on the noun" is practitioner craft.

### Cited Findings
- [VENDOR/editor guides] Individual B-roll clips "generally run **2–5 s**", and a static B-roll running **8 s** while you talk "starts to drag". Another guide calls **2–4 s** the comfortable range. Pace guidance: fast **2–3 s** clips for social, medium **4–6 s** for explainers, slow **6–10 s** for documentaries. By shot type: establishing **2–4 s**, detail **1.5–3 s**, reaction **1–2 s**, cutaway **2–5 s**. (These figures come from a group of guides; the search extracts did not show which page gave which figure.) — [Captions.ai](https://captions.ai/blog/practical-guide-b-roll-video); [SocialRails](https://socialrails.com/blog/b-roll-footage-complete-guide); [Lumira Studio](https://www.lumirastudio.com/blog/insights/what-is-b-roll-in-video/); [Beerolls 2026](https://www.beerolls.com/blog/how-to-add-b-roll-to-videos-2026-guide)
- [VENDOR] For short-form, a 30-s Short needs about 8–12 s of cutaways in total, spread over several moments, rather than long single shots. — [AutoShorts](https://www.autoshorts.app/en/blog/b-roll-short-form-video-guide)
- [VENDOR] When shooting, hold each shot **10+ s**, or a 20 s minimum, so there is room to choose the best few seconds. — [TechSmith](https://www.techsmith.com/blog/b-roll-secret-sauce-great-video/); [Descript](https://www.descript.com/blog/article/using-b-roll-a-beginners-guide)
- [VENDOR] J-cut means audio before video, and L-cut means video before audio. B-roll is commonly used to hide a cut in trimmed narration. — [Descript](https://www.descript.com/blog/article/using-b-roll-a-beginners-guide)
- [OFFICIAL-adjacent] YouTube marks "Spikes" as moments viewers rewatched. A spike can mean the content was unclear and viewers had to replay it. For tutorials, B-roll or zooms at a confusing step may be causing or fixing such rewatches. — [YouTube Help](https://support.google.com/youtube/answer/9314415?hl=en)

### Inferences
- Proposed rules for the skill:
  - **Keyword sync:** start the B-roll on the **first frame of the keyword's first syllable**, or 2–4 frames before it, so the image arrives as the word lands. End it at a phrase boundary or breath, not mid-word. This is craft convention and is not measured.
  - **Duration:** 1.5–3 s for illustrative inserts (a cube close-up, a gameplay item); 3–5 s for anything the viewer must read or understand (a notation diagram, a stat); never more than 6 s static. If longer, add a slow push of +3–5% over the clip, or cut to a second angle.
  - **J-cut into new sections:** start the next section's voice-over 0.3–1.0 s before its first visual (J-cut). Hold the outgoing visual 0.5–1 s past the end of a sentence (L-cut) when a reveal needs to land.
  - **Density for a voice-over channel:** because there is no face to return to, the "A-roll" is the main hands or gameplay footage. Treat inserts (graphics, diagrams, archive clips, memes) as the B-roll layer, roughly one every 10–20 s, with zooms and text filling the gaps in between.

### Gaps
- I found no measured evidence on whether B-roll should lead or follow the spoken word, or by how many frames.
- I found no published J/L-cut offset figures. The 0.3–1.0 s values above are an inference, not sourced.

## 4. Zooms and punch-ins

### Takeaway
Tool documentation shows punch-ins of about **130%**, and practitioners say a hard zoom only reads as intentional when it lands exactly on the onset of a word. Use slow, eased pushes for reflective lines and hard snaps for punchlines. Zooming on every line causes fatigue, so zoom in and then back out to reset the frame. I found no numeric frequency limit.

### Cited Findings
- [VENDOR doc] Tella's punch-in example uses a layout that scales the camera to **130%**: it zooms in at the start of the marked range and back out at the end. A zoom "signals to the viewer that the content is important and deserves their attention." — [Tella help](https://www.tella.com/docs/help/tips/punch-in-zoom-in-on-your-camera)
- [VENDOR/craft] "A hard-cut zoom reads as intentional only when it lands exactly on the word's onset — timing is the whole game." Use hard punches for emphasis and subtle Ken Burns slow pushes for insightful lines. — [Tella skills: add zooms](https://www.tella.com/skills/add-zooms)
- [VENDOR] Eased punch-in curves feel like "a camera operator pushing in rather than the frame jumping between crop settings". — [Eliro](https://eliro.pro/tools/auto-zoom-video)
- [VENDOR] "Zooming in on every line gets tiring fast." Zoom in and then back out so the frame does not creep ever closer. — [OpusClip zoom tool](https://www.opus.pro/tools/zoom-in-effect)
- [VENDOR] Treat punch-ins as a late layer: first remove friction (silences, tight transitions, captions), then add "a few" punch-ins, and avoid overuse. — [Jupitrr, updated Sep 2026](https://jupitrr.com/how-to/edit-talking-head-videos)

### Inferences
- Proposed rules for the skill. These are heuristics; no source gives frequencies.
  - **Scales:** subtle emphasis or jump-cut masking at **110–115%**; standard punch-in at **120–130%**; comedic "absurd" snap zoom at **150–250%**, ideally on a detail such as a single sticker, the timer digits or an in-game face, held **0.5–1.5 s** and paired with a freeze-frame or sting.
  - **Timing:** a hard zoom lands on the stressed syllable's first frame. A slow push runs **+5–10% over 2–4 s** under explanation-heavy lines.
  - **Jump-cut masking:** alternate 100% and 115% framing across consecutive cuts of the same continuous shot, such as a fixed overhead camera on hands.
  - **Frequency ceiling:** at most about 1 emphasis zoom per **10–15 s**, and at most about 1 comedic snap-zoom per **45–90 s** in long-form, so the gag stays surprising. Always return to the base framing within 1–4 s.
  - **Faceless caveat:** zooming into hands or cube footage loses resolution. The skill should check whether the source was shot at 4K for a 1080p timeline, which allows up to about 200% punch-in without visible softening.

### Gaps
- I found no source giving zoom-frequency limits or data on viewer fatigue.
- I found no source specific to zooming on hands, objects or gameplay rather than faces.

## 5. Sound effects: timing, level, density

### Takeaway
Align the **transient (peak) of the SFX** with the visual event frame, not the start of the audio file. Whooshes can lead slightly (sources say 10–20 ms or "a hair before"). Keep SFX below dialogue, around −12 to −18 dB (peak) per one guide, and master to about −14 LUFS integrated, because YouTube turns louder audio down but does not turn quiet audio up. Use SFX sparingly, since overuse backfires.

### Cited Findings
- [VENDOR/craft] Align the transient, not the file start: SFX files often have a few frames of near-silence before the hit, which makes cues look late. Zoom the timeline to frame level before judging sync. Nudge in single frames. Check the rendered export, because laggy previews mislead. — [Krotos: sound to picture](https://krotos.studio/blog/sound-to-picture); [Morphic: sync SFX](https://morphic.com/resources/how-to/how-to-sync-sound-effects-to-video)
- [VENDOR] Start whooshes slightly before the visual move, about **10–20 ms** early, so the sound leads. Another source says sounds often feel best "a hair before or right on the visual". The 10–20 ms figure is a rule of thumb. — [Pixflow: whoosh SFX](https://pixflow.net/blog/cinematic-whoosh-sound-effects/); [Krotos](https://krotos.studio/blog/sound-to-picture)
- [VENDOR] Sound effects usually sit at **−12 to −18 dB** (peak), and are "never louder than your dialogue unless a big intentional moment calls for it". Background music is ducked **15–20 dB** under the voice while someone is speaking. — [Pixflow: mixing in Premiere](https://pixflow.net/blog/audio-mixing-premiere-pro/)
- [VENDOR/forum] YouTube normalises playback to about **−14 LUFS**, turning louder uploads down but never turning quiet uploads up. Levels below about −16 LUFS are hard to hear on phone speakers. — [IRPR Sound](https://sounddesign.irpr.agency/guides/how-to-mix-audio-for-youtube/); [Shotcut forum](https://forum.shotcut.org/t/video-volume/24529)
- [CREATOR guide] In comedic and gaming edits, a funny sound on a quick cut makes a reaction land, but overloading with effects backfires. Sudden audio pauses strengthen comedic timing. — [Air.io: editing tricks for funny videos](https://air.io/en/youtube-hacks/editing-tricks-for-fast-paced-funny-videos)
- [DATA/reporting] "Loud sound effects" were named as a hallmark of the 2024 retention-editing style that audiences began to tire of. — [GIGAZINE](https://gigazine.net/gsc_news/en/20240403-retention-editing-beastification-may-be-end)

### Inferences
- Proposed rules for the skill:
  - **Sync:** put the SFX peak on the event frame. For whooshes on a transition, place the whoosh's loudest point on the cut frame, with the build starting 3–8 frames before it. 10–20 ms is under one frame at 30 fps (33 ms), so "0–1 frame early" is the practical rule. Text-pop "pops" land on the text's first visible frame. Dings land on the reveal frame, such as the cube's solved state or the timer stopping.
  - **Level:** keep voice at about −20 to −16 LUFS short-term, set SFX peaks 3–10 dB below voice peaks, and allow comedic stings to briefly match the voice peak. Final master: −14 LUFS integrated, true peak ≤ −1 dBTP. The dBTP figure is standard streaming practice, not from these sources.
  - **Density:** at most about 1 SFX per visual event worth marking. Do not put a whoosh on every cut. Gag stings follow the zoom budget above (one per 45–90 s). "Silence-as-SFX", meaning a hard audio drop for 0.3–0.8 s before a punchline, is a valid tool for a channel without music.

### Gaps
- I found no measured study on SFX density and retention, and no authoritative dB-under-dialogue standard for transient SFX. The −12/−18 figures come from a single vendor guide and use peak dB, not LUFS.

## 6. Text pop-ups and captions (including Arabic RTL)

### Takeaway
Evidence that captions help comes from older or self-reported studies: Facebook's internal test found +12% view time, Verizon/Publicis 2019 is a self-reported survey, and DDN measured +7.32% views on YouTube. Claims that word-by-word "animated" captions beat sentence captions come only from vendors. Readability rules from subtitling standards are solid: Netflix requires each subtitle event to last **between 5/6 s and 7 s**, with ≤42 characters per line for Arabic and ≤2 lines. Reading-speed caps range from **12–20 characters/s** depending on the guideline. DaVinci Resolve has long-standing Arabic RTL rendering problems, especially strokes on RTL subtitles and Text+.

### Cited Findings
- [DATA, internal, older ~2016] Facebook's internal tests found that captions increased view time by an average of **12%**. Facebook client A&W Canada reported **+25% watch time** on captioned videos. — [Hypebot](https://www.hypebot.com/shhh-why-you-need-to-optimize-your-facebook-videos-for-silence/); [3Play Media](https://www.3playmedia.com/blog/studies-find-captions-improve-engagement)
- [DATA, survey, 2019] A Verizon Media/Publicis Media survey of **5,616 US adults aged 18–54** (Apr 2019) found that 80% said they were more likely to watch a video to completion when captions were available. This is self-reported intent, not observed behaviour. — [3Play Media](https://www.3playmedia.com/blog/verizon-media-and-publicis-media-find-viewers-want-captions/)
- [DATA, older] A Discovery Digital Networks test on YouTube found an overall **+7.32% views** on captioned videos. These were uploaded closed captions, not burned-in text. — [3Play Media](https://www.3playmedia.com/blog/studies-find-captions-improve-engagement)
- [VENDOR, unverified] Animated word-by-word captions reportedly give an 18–28% retention lift against 8–12% for static subtitles. No study or sample size is named. A more sceptical vendor calls the advantage "probably true" but unverifiable, based on an OpusClip dataset in which 78.6% of clips had animated captions. — [ClipSpeed](https://clipspeed.ai/blog/ai-captions-increase-views.html); [Blitzcut](https://blitzcutai.com/blog/animated-captions-vs-static-captions)
- [VENDOR] Reserve emphasis styling for the **2–3 words per clip** that carry the beat. Keep **no more than 2 lines** on screen. — [Kompozy](https://kompozy.io/how-to/video-captions-for-retention); [OpusClip Shorts captions](https://www.opus.pro/blog/youtube-shorts-caption-subtitle-best-practices)
- [OFFICIAL standard: Netflix] A subtitle event lasts at least **5/6 s** (20 frames at 24 fps) and at most **7 s**, with a **2-frame minimum gap** between events in supplemental assets. — [Netflix Timed Text: General Requirements](https://backlothelp.netflix.com/hc/en-us/articles/215758617); [Netflix Supplementals guide](https://backlothelp.netflix.com/hc/en-us/articles/115000239632-Timed-Text-Style-Guide-Supplementals-Marketing-Assets)
- [OFFICIAL standard: Netflix] The Arabic Timed Text guide sets **42 characters per line**. A university lecture gives 34–36 for Arabic. Netflix measures reading speed in characters per second, counting spaces and punctuation. — [Netflix Arabic TTSG](https://backlothelp.netflix.com/hc/en-us/articles/215517947); [Netflix reading-speed FAQ](https://backlothelp.netflix.com/hc/en-us/articles/115001352212-How-is-reading-speed-measured-Do-punctuation-and-spaces-count)
- [OFFICIAL standards, other] Reading-speed caps: Netflix Indonesian **17 cps** for adults and 13 cps for children; proposed Malta guidelines **15 cps** for adults and 12 for children. One blog cites 17–20 cps for Netflix adults without a primary source. — [Netflix Indonesian TTSG](https://backlothelp.netflix.com/hc/en-us/articles/216009727); [Spiteri Miggiani, Malta guidelines 2021](https://www.um.edu.mt/library/oar/bitstream/123456789/112270/1/Proposed%20subtitling%20guidelines_Spiteri%20Miggiani_%20MALTA%20revised%20July%202021%20wm.pdf)
- [FORUM, Resolve-specific] DaVinci Resolve Arabic issues: Text+ shows RTL alignment and spacing problems, and the Basic Text title works better. Arabic subtitles **disappear when stroke > 0**: reported on Resolve 18 beta, and acknowledged by Blackmagic staff in 2018 for Resolve 15 (Windows only at that time). Users work around it by rendering Arabic text as PNGs in GIMP or Inkscape. The same class of bug exists in FFmpeg/libass Arabic burn-in (2025). — [Blackmagic forum: Fix Arabic RTL](https://forum.blackmagicdesign.com/viewtopic.php?p=845503); [Blackmagic forum: Middle Eastern subtitle bug](https://forum.blackmagicdesign.com/viewtopic.php?p=486190); [ZoftwareHub overview](https://zoftwarehub.com/en-ae/products/davinci-resolve/overview); [FFmpeg trac #11566](https://ffmpeg.org/pipermail/ffmpeg-trac/2025-April/073389.html)

### Inferences
- Proposed caption rules for the skill:
  - **Long-form burned-in Arabic captions:** phrase-level chunks of 2–6 words, 1 line preferred and at most 2, ≤42 characters per line. On screen for at least 0.83 s (25 frames at 30 fps) and at most 7 s. Target ≤15–17 cps, counting spaces. Keep at least a 2-frame gap between events. Lower-third safe area, above YouTube's progress bar and away from the bottom ~15% where player controls overlay.
  - **Shorts:** 1–3 words per event, word-by-word highlight, centred in the lower-middle third, kept clear of the right-side action buttons and bottom description overlay. Syrian-dialect spelling is fine, but be consistent.
  - **Keyword pop-ups** (separate from captions): 1–3 words, appearing on the spoken word's first frame. Hold for at least ~1 s plus 0.3 s per extra word, then remove. One pop per 10–20 s maximum in long-form. Pair each pop with a soft "pop" SFX only when it is a key term, not every time.
  - **Comedic captions** (the user's absurd-edit style): hold long enough to read twice, about 1.5–2.5 s, usually over a freeze-frame.
  - **Arabic in Resolve:** test in the user's Resolve version before committing. Default to the Basic Text / subtitle track with **no stroke**, and use a drop shadow or semi-opaque background box for contrast. If a stroke or animated style is required, generate the Arabic text externally as PNGs or via a correctly shaped renderer and import it. The skill should also check for broken letter joining (isolated glyph forms) and reversed word order in mixed Arabic–English–number lines, such as cube notation "R U R'" or times "8.53". Wrapping embedded LTR runs, or splitting them into separate text layers, is a common fix. This is an inference; I found no source specific to Resolve 20/21.

### Gaps
- I found no controlled YouTube study comparing burned-in captions with uploaded captions, or word-by-word with sentence-level captions, for retention.
- I could not find an Arabic-specific cps limit in Netflix's Arabic guide via search.
- I could not verify whether Resolve 19/20/21 has fixed Arabic stroke or Text+ shaping. A Resolve 21.0.1 (June 2026) subtitle guide exists ([tryuncle](https://tryuncle.com/learn/davinci-resolve/subtitles)), but its content was not retrievable.

## 7. Transitions: hard cuts versus whip and zoom transitions

### Takeaway
Little hard evidence exists. The evidence that does exist (the 2024 "retention editing" backlash and creators' warnings about overuse) favours **hard cuts as the default**. Stylised transitions (whip, zoom, glitch) should be reserved for section or scene changes, and flashy effects should not be stacked.

### Cited Findings
- [DATA/reporting] "Flashing effects" and "fast cut switching" were named as markers of the over-edited retention style that audiences were tiring of by 2024. — [GIGAZINE](https://gigazine.net/gsc_news/en/20240403-retention-editing-beastification-may-be-end); [YPulse](https://www.ypulse.com/newsfeed/2024/04/02/young-people-are-getting-tired-of-retention-editing-on-youtube/)
- [VENDOR] Pattern interrupts include a change of camera angle, a music drop, a sound effect or on-screen text, not only transitions. "Cut on completion": shots should not run longer than needed. — [Pixflow retention editing](https://pixflow.net/blog/youtube-video-retention-editing/); [Air.io](https://air.io/en/youtube-hacks/advanced-retention-editing-cutting-patterns-that-keep-viewers-past-minute-8)
- [CREATOR guide] In gaming and comedy, timing cuts to audio rhythm and using sudden pauses makes gags land better than adding effects. — [Air.io: funny edits](https://air.io/en/youtube-hacks/editing-tricks-for-fast-paced-funny-videos)

### Inferences
- Proposed rules for the skill: **hard cut** for about 90–95% of edits. A **whip or zoom transition with a whoosh** only at chapter or section boundaries, roughly 1 per 1–3 min, lasting 6–12 frames. **Never** use dissolves inside a tutorial step, because they blur the move being taught. A short **dip to black or a 2–4 frame flash** can mark a time jump ("3 hours later") in gaming. Match cuts are ideal for cubing, for example a cut on the same turn from a different angle, or from a scrambled cube to a solved one.

### Gaps
- I found no study or credible count of transition frequency in top channels. The rules above are practitioner inference.

## 8. Re-hooks, open loops, structure, chapters and end screens

### Takeaway
The MrBeast memo gives the most concrete timeline: a first-minute hook, "crazy progression" from 1–3 min, a **re-engagement at ~3:00**, fast story-driven content from 3–6 min, and a **second re-engagement at ~6:00**. Vendors suggest a forward-looking tease every **60–90 s**, with only 1–2 big open loops per video. End screens occupy the last **5–20 s** and should appear right after the sign-off, with no long fade-out.

### Cited Findings
- [MEMO] Minutes 1–3: "crazy progression", compressing several days of story into the first 3 minutes so the viewer becomes "super invested". **Minute 3**: a "3 minute re-engagement", usually a spectacle, to stop viewers clicking away. **Minutes 3–6**: "make them fall in love with the story", with fast scene changes. **Minute 6**: a second re-engagement for the back half. — [Daniel Scrivner summary](https://www.danielscrivner.com/how-to-succeed-in-mrbeast-production-summary/); [Cybernews](https://cybernews.com/news/mrbeast-leaked-pdf-spills-secrets-how-to-be-successful-on-youtube/); [OMR](https://omr.com/de/daily/mrbeast-doc-pdf-leak)
- [MEMO] Metrics tracked are CTR, AVD and AVP, plus a qualitative "wow factor": "You can't track the 'wow factor' but I can describe it." — [Alexander Jarvis copy](https://www.alexanderjarvis.com/memo-how-to-succeed-in-mrbeast-production/); [Herpaperroute](https://herpaperroute.com/leaked-mrbeast-document/)
- [OFFICIAL] YouTube advises that if "Top moments" (where almost no one leaves) fall late in a video, that content should move earlier, because audiences shrink as a video progresses. — [YouTube Help](https://support.google.com/youtube/answer/9314415?hl=en)
- [VENDOR] Include a forward-looking hook every **60–90 s**. The vendor claims this lifts the 50% and 75% retention markers by 15–25%; the figure is unverified. — [Fluxnote](https://fluxnote.io/guides/faceless-channel-retention-strategies-2026)
- [VENDOR] Pattern interrupts every 60–90 s in the body. Use only **1–2 open loops** per video, because more erode trust that they will be paid off. Another vendor says something new every 30 s. — [Pixflow](https://pixflow.net/blog/youtube-video-retention-editing/); [Gyre psychology hacks](https://gyre.pro/blog/10-psychology-hacks-to-keep-viewers-watching-until-the-end)
- [OFFICIAL, older 2016] End screens can occupy the **last 5–20 s** of a video and hold up to **4 elements**. — [TechCrunch 2016, citing YouTube docs](https://techcrunch.com/2016/10/26/youtube-launches-mobile-friendly-end-screens-feature-to-keep-viewers-watching-more-video/)
- [VENDOR] The end screen should appear right after you finish speaking and sign off, because long pauses or fade-outs give viewers a chance to leave. Leave open space in the final frames so elements do not cover important visuals. Linking a playlist keeps the session going. — [NexLev](https://www.nexlev.io/youtube-end-screen-tips); [SocialKit](https://socialk.it/en/blog/youtube-end-screens-and-cards-guide)

### Inferences
- Proposed structure template for an 8–20 min video:
  - 0:00–0:30 hook and payoff previews.
  - 0:30–1:00 context, kept short.
  - **~1:00** the first "progress" beat.
  - **~3:00** re-engagement #1: the most visually surprising moment in the middle part, such as a crazy solve, a record or an absurd gag.
  - **~6:00** re-engagement #2.
  - Then a re-hook every **~2–3 min** (videos over 10 min), each one a spoken tease ("the hardest step is coming") plus a visual change such as a new location, new cube, chapter card or zoom gag.
  - A small open loop at each chapter boundary that is closed within the next chapter. Keep one "big" loop, the main payoff, open until the final 10–20%.
- **Outro:** no recap and no long goodbye. The final payoff should be followed within ≤5 s by a verbal handoff ("watch this next…") and a 10–15 s end screen. Retention drops at outros are normal, so the aim is to shorten the tail, not to fight it.
- **Chapters:** YouTube chapters let viewers skip, which can show up as "Dips" (skips) in Key moments. The skill should read a dip that falls right before a chapter boundary as "this section is skippable", not as "viewers left".

### Gaps
- I could not verify the memo's exact wording because the PDF host was blocked. The memo excerpts reached me only through secondary summaries.
- I found no measured data on the best re-hook interval for 8–20 min educational videos.

## 9. Music: why creators use it, and alternatives for a no-music channel

### Takeaway
Music fills silence, smooths cuts, sets tone and masks imperfect recordings. Most "music boosts retention X%" figures are unsourced vendor claims. For a no-music channel the main risks are **audible edit seams** and **dead digital silence**. Low-level room tone or ambience, plus deliberate SFX and silence beats, address those risks.

### Cited Findings
- [VENDOR] Music "fills silence, smooths cuts, and sets emotional tone". Voice-over without music "can sound bland". — [RouteNote licensing blog](https://licensing.routenote.com/blog/?p=8164); [Lumen5](https://lumen5.com/learn/why-you-should-combined-music-with-your-voiceovers-tlcvideo/)
- [VENDOR] Background music can hide unclean recordings, which a voice-over studio calls "a dangerous game to play". — [Bunny Studio](https://bunnystudio.com/blog/wp-json/wp/v2/posts/27562)
- [VENDOR] Duck music 15–20 dB under speech. — [Pixflow](https://pixflow.net/blog/audio-mixing-premiere-pro/)
- [UNRELIABLE] Claims such as "background music keeps viewers 20% longer" appear without any cited study. — flagged during search; no credible source found.
- [VENDOR] Ambient sound can "transport viewers into the scene". When recording, turn off fans, AC and fridges to reduce noise. — [Subscribr: sound mixing](https://subscribr.ai/youtube-strategy/youtube-sound-mixing-importance)

### Inferences
- The skill should explain the trade-off: without music, every jump cut in the voice-over is audible. It should therefore (a) lay a continuous **room-tone bed**, recorded in the same room for 30 s, at about −50 to −60 dBFS under the whole voice track so cuts do not drop to digital silence; (b) use 2–4 frame audio crossfades on every voice cut; (c) let natural cube-turning sounds or game audio carry pacing (cube clicks are diegetic "music" for the cubing niche); (d) use short stings or dings on reveals and silence drops before punchlines. These are craft inferences, not sourced.
- **Gaming:** in-game soundtrack or ambience at about −20 to −25 dB under the voice serves the energy role of music without a separate music bed. It needs a Content ID check for copyrighted game OSTs (not researched here).

### Gaps
- I found no controlled evidence that background music changes YouTube retention, either way.
- I found no source on room tone as a retention technique.

## 10. Reading YouTube Studio retention graphs to fix edits

### Takeaway
Use Key moments (Intro / Top moments / Spikes / Dips) and the **"typical" retention comparison**, which compares against the user's own 10 latest videos of similar length, or against all of YouTube via "See more". Absolute benchmarks are unreliable. Retention Rabbit's 2025 dataset puts average retention at about **23.7%**, with 5–10 min videos highest at **31.5%**. Diagnosis: a steep early drop means the hook or title-thumbnail is mismatched, a slow middle slide means pacing, a spike means rewatching (good or confusing), and a dip means skipping or leaving.

### Cited Findings
- [OFFICIAL] Key moments definitions: **Top moments** are where almost no one dropped off. **Spikes** are segments rewatched or shared, meaning either more engaging or unclear content that had to be replayed. **Dips** are segments skipped, or where viewers stopped watching. — [YouTube Help](https://support.google.com/youtube/answer/9314415?hl=en)
- [OFFICIAL] You can compare a video with your 10 latest videos of similar length ("typical retention"), and "See more" compares it with all YouTube videos of similar length. Creator Insider earlier described typical retention as based on similar-length videos from the past year on the creator's own channel, with cross-channel comparison planned. — [YouTube Help 1715160](https://support.google.com/youtube/answer/1715160); [Search Engine Journal](https://searchenginejournal.com/youtube-typical-audience-retention/421700)
- [DATA, vendor dataset] The Retention Rabbit 2025 report (10,000+ videos, 1,000+ channels) found average retention of **23.7%**; only **16.8%** of videos keep more than 50% of their audience; **5–10 min videos retain best at 31.5%**. — [Retention Rabbit 2025 report (via proxy)](https://translate.google.com/translate?u=https://www.retentionrabbit.com/blog/2025-youtube-audience-retention-benchmark-report&hl=es&sl=en&tl=es&client=srp); [Stripo benchmarks](https://research.stripo.email/youtube-benchmarks)
- [VENDOR, unsourced, conflicts with the above] Prepublish gives average-percentage-viewed ranges of 65–75% for videos <5 min, 50–60% for 5–10 min, 40–50% for 10–15 min, and 35–45% for 15+ min. Its niche ranges for 8–12 min videos are **education/tutorial 45–55%** and **gaming 35–45%**. — [Prepublish 2026 benchmarks](https://prepublish.ai/blog/youtube-retention-benchmarks-2026)
- [VENDOR] Diagnosis: a sharp drop in the first 30 s is a hook problem, and a slow slide through the middle is a retention or pacing problem. — [Prepublish](https://prepublish.ai/guides/first-30-seconds)
- [OFFICIAL, secondary] Beaupré advises creators to "look at your retention graphs… to see where people are relatively dropping off". Satisfaction signals (surveys, return visits, session continuation) weight watch time. — [vidIQ algorithm guide](https://vidiq.com/blog/post/understanding-youtube-algorithm/)
- [OFFICIAL/secondary] Shorts: YouTube publishes no official "viewed vs swiped away" benchmark. Creator data calls 70–79% viewed "working" and ≥80% "strong". Galloway is credited, second-hand, with 70–90% for top Shorts. Since **31 Mar 2025** a Shorts view is counted whenever a Short starts or replays, so earlier and later view counts are not comparable. A low viewed rate means a weak first 1–2 s; a good viewed rate with low average percentage viewed means weak pacing after the hook. — [1of10 Shorts analytics](https://1of10.com/blog/youtube-shorts-analytics/); [Creator Essentials glossary](https://www.creatoressentials.com/glossary/viewed-vs-swiped-away/); [Medium/Ershov](https://medium.com/@AlexanderErshov/youtube-shorts-getting-0-views-heres-exactly-why-and-how-to-fix-it-84202c3eb6b3)

### Inferences
- Proposed re-edit workflow for the skill. The user exports or reads timestamps from Studio, and the skill maps them back to the timeline.
  1. **Mapping:** the Studio graph timestamp equals the timeline timecode if the timeline starts at 00:00:00:00. Resolve's default start is 01:00:00:00, so the skill must subtract 1 hour.
  2. **Dip of ≥3–5 percentage points within ≤10 s:** inspect 5–15 s *before* the dip. Viewers decide during the slow part and leave at its end. Fixes: trim, add a visual change, or move the next payoff earlier.
  3. **Spike in a tutorial step:** if comments or the step's complexity suggest confusion, add a zoom, slow-motion repeat or notation overlay rather than cutting.
  4. **Gradual slope steeper than "typical":** raise the visual-change rate and add a re-hook in that stretch.
  5. **Late "Top moments":** move a teaser of them into 0:00–0:30.
  6. **Intro below typical:** re-cut the first 30 s first, then reconsider the title and thumbnail match.
- Because absolute benchmarks conflict by 2× across vendors, the skill should only judge against the user's own "typical" band.

### Gaps
- YouTube publishes no official numeric benchmark. The Retention Rabbit niche breakdown was not retrievable.
- I found no official threshold for what dip size counts as a "Dip" key moment.

## 11. Niche-specific guidance: cubing tutorials, gaming, and faceless channels

### Takeaway
Direct evidence for faceless, cubing or gaming editing is thin, and almost all of it is vendor or freelancer material. The transferable principles are: (1) change the visual through zooms, text and angle changes instead of returning to a face; (2) for tutorials, the hands-on, "drawn" style beats slides and screencasts (Guo et al.); (3) for gaming, cut all dead time and use memes and SFX in moderation.

### Cited Findings
- [VENDOR] On faceless channels a visual change can be a text overlay, a zoom, an animated graphic or a slow Ken Burns push; it does not have to be a new clip. A static image for about 30 s causes exits. — [Fluxnote](https://fluxnote.io/guides/faceless-channel-retention-strategies-2026); [Air.io](https://air.io/en/youtube-hacks/advanced-retention-editing-cutting-patterns-that-keep-viewers-past-minute-8)
- [VENDOR] Annotated screencasts and animated explainers with voice-over are listed as viable faceless formats. — [Framesail](https://framesail.com/blog/high-retention-faceless-youtube-videos)
- [DATA, older] Khan-style drawing tutorials are more engaging than slides or code screencasts. Segment into chunks <6 min. — [Guo et al. 2014](https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf)
- [CREATOR guide] Gaming: keep only the most entertaining parts, remove pauses and loading screens, add commentary, SFX or memes, and do not overload. — [SuperJump Magazine](https://www.superjumpmagazine.com/how-to-cut-gaming-videos-without-losing-quality-for-youtube/); [Air.io funny edits](https://air.io/en/youtube-hacks/editing-tricks-for-fast-paced-funny-videos)

### Inferences
- **Cubing tutorials:** each algorithm should get (a) a full-speed demo, (b) a slowed or step-by-step repeat with notation text synced to each turn, and (c) a zoom on the affected layer. Cut to a top-down or "cube-face" 2D animation when spatial reasoning is needed, which is the "Khan-style" equivalent. Chapter each method step; per Guo, keep each step ≤6 min. Show time-lapse or speed-ramped "dead" solving at 2–8× with a visible timer.
- **Faceless visual-variety menu**, to be cycled so the same device never repeats more than about 2× in a row: alternate camera angle on the hands; macro close-up; screen animation or diagram; on-screen keyword; meme or reaction insert; freeze-frame plus caption; speed ramp; split-screen comparison (two methods side by side); timer or stat overlay; map or chart.
- **Gaming:** cut every pause over 0.5 s in commentary. Remove menus and loading screens entirely, or replace them with a 1-s "loading…" gag. Use freeze-frame plus zoom plus caption for fails and wins. Use speed-ups at 2–4× for traversal.

### Gaps
- I found no published editing analysis of cubing channels (such as J Perm or CubeHead) or of Arabic-language faceless channels. I found no evidence specific to an Arabic-speaking audience on pacing or caption preferences.
