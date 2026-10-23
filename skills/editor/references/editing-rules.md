# Editing rules

These are the starting rules. **`brain/edit-preferences.md` always wins over this file.** Evidence labels:
- **DATA**: measured.
- **OFFICIAL**: YouTube or Netflix specs.
- **MEMO**: the leaked MrBeast production memo, whose origin is disputed.
- **CRAFT**: editor/creator rules of thumb with no measurement behind them.

If he asks "why", say which kind of rule it is.

## Contents
1. Per-video style menu (checkpoint A)
2. Structure: hook, re-hooks, ending
3. Zooms
4. B-roll
5. Sound effects
6. Text pop-ups and numbers
7. Freeze frames and humor
8. Transitions
9. Chapters
10. Cubing videos (Syrian Rubik)
11. Gaming videos (SRB Gamer)
12. What the research does and doesn't say

## 1. Per-video style menu (checkpoint A)

He chose "decide per video" for pacing, zooms, transitions, captions, pop-ups and humor. Ask with AskUserQuestion in one round of up to 4 questions. Put the option that fits *this* video first, marked (Recommended). Skip any question his preferences already answer firmly.

| Question | Options (pick 3–4) |
|---|---|
| Pacing | Calm · Medium · Fast · "You decide per section" |
| Zooms | Mix: hard on punchlines, smooth on explanations · Hard punch-ins · Smooth push-ins · Few zooms |
| Transitions | Hard cuts only · Hard cuts + whoosh at chapter changes · Energetic: whip/zoom at sections |
| Captions | None · Arabic .srt for YouTube · Burned-in · Both |
| Text pop-ups | Key moments only · Terms + numbers · Lots · None |
| Humor edits | Only real funny moments · Often · Rarely · None |

Targets per pacing level. These are CRAFT numbers: a starting point, then tune them to his preferences.

| | Calm | Medium | Fast |
|---|---|---|---|
| Visual change (anything: zoom, B-roll, pop-up, his own cut) | every 8–12 s | every 4–6 s | every 2–3 s |
| Planned visual edits per minute | 3–6 | 7–12 | 13–22 |
| Zooms per minute | ≤ 2 | 2–4 | 4–6 |
| SFX per minute | 1–3 | 3–6 | 6–10 |
| Longest stretch with no visual change | 15 s | 8 s | 5 s |

Count his own cuts (`analyze.py` shot cuts) as visual changes. Don't add edits where his footage already changes a lot.

## 2. Structure: hook, re-hooks, ending

- **0–30 s is the hook.** OFFICIAL: YouTube Studio shows "Intro" retention as the share still watching at 30 s. MEMO: "the first minute has the most loss".
  - Make this the densest part of the plan.
  - Put the strongest visual at 0:00: the payoff, the solved cube, the record time, the gameplay climax.
  - Back the promise with a text pop-up when he states it.
  - Add 2–3 quick teases of the payoff before 0:30 (by hand if they need re-cutting: add a `note` item).
- **Re-hooks** (MEMO + CRAFT): around 3:00 and 6:00, then every 2–3 minutes. When he says something like "but wait" or "here's the crazy part", back it with a zoom, a pop-up or an SFX sting.
- **No dead air.** Silences longer than 1 s that he left in get a `note` (he may want to cut them). The bridge never cuts his clips.
- **Ending.** When he signs off, end-screen elements take the last 5–20 s (OFFICIAL, 2016). Add a `note` there: "end screen starts here". No edits after it.
- **Long still stretches.** For any stretch `analyze.py` lists as "picture barely changes", plan at least one of: a zoom, B-roll, a pop-up, or a freeze, matched to the words there.

## 3. Zooms

- **Scale:**
  - 110–115%: hides a jump cut or adds a subtle shift.
  - 120–130%: emphasis.
  - 150–250%: comic snap, max ~1 per 45–90 s unless he chose "often".
  - CRAFT; the Tella tool's default punch-in is 130%.
- **Resolution check.** The bridge zooms the clip as it is on his timeline. On a 1080p source in a 1080p timeline, anything over ~130% gets soft. Check `snapshot_before.json` → item `media.resolution`. A 4K source can take ~200% cleanly.
- **Hard punch-in** (`mode: "hard"`):
  - Lands **exactly on the first frame of the stressed word**. A hard zoom only reads as intentional on the word onset (CRAFT, Tella).
  - Lasts 0.8–3 s, then cuts back.
- **Smooth push-in** (`mode: "smooth"`):
  - For explanations and building tension: 2–6 s, ease 0.3–0.6 s.
  - Set `"out": true` to ease back out at the end.
- **Center** (`center: [x, y]`, 0–1 from the top-left):
  - Point at what matters: the cube in his hands, the timer, the kill feed.
  - Read it off the contact sheets. Don't always use [0.5, 0.5]: for hands on a table it's often around [0.5, 0.6].
- **Don't:**
  - zoom twice within 2 s (the validator warns)
  - zoom on every sentence ("zooming on every line gets tiring fast": CRAFT, OpusClip)
  - zoom while a B-roll is up
- **The bridge can't zoom (by-hand marker instead)** where a title or second layer sits over his clip, and where his clip is sped up or slowed down.

## 4. B-roll

- **When:** the words name something showable (a cube model, a record, a game item, a place, a person). Use it also to cover a jump cut or break a still stretch.
- **Length:**
  - illustrative: 1.5–3 s
  - something to read or understand: 3–5 s
  - never more than ~6 s static ("8 s drags": CRAFT)
- **Start 2–4 frames before the trigger word** (0.03–0.07 s at 60 fps). Set `at` = word start − 0.05.
- **Sound:** B-roll audio is off by default. Turn it on (`"audio": true`) only when the sound is the point, for example a cube pop or a game sound.
- **Source order:**
  1. his own clips (zero risk)
  2. Pexels/Pixabay/Coverr/Mixkit
  3. YouTube CC BY (needs a credit)
- **Never** put B-roll over his hands mid-algorithm in a tutorial, or over important gameplay. Use a pop-up instead.

## 5. Sound effects

- **Align the loud point (the transient), not the file start** (CRAFT, Krotos). `align: "peak"` is the default and does this automatically.
- **Whooshes** lead the visual by ~10–20 ms (CRAFT, Pixflow). With `align: "peak"` on the visual's frame that is already right.
- **Level:** sit 3–10 dB under his voice peaks. `gain_db` 0 = a standard level about −20 dBFS, roughly under speech. Typical values:

  | SFX | gain_db |
  |---|---|
  | whooshes | −4 to −8 |
  | pops and dings | −2 to −6 |
  | comic stings | 0 to −3 |

  He can't change clip volume through the bridge, so pick the gain well.
- **Which sound where:**

  | Moment | Sound |
  |---|---|
  | B-roll in or a section change | whoosh |
  | text pop-up | pop or click |
  | a number or record | ding or riser into a hit |
  | a fail | comic sting, record scratch, buzzer |
  | a win | short success sting |
  | a cube moment | **his own cube sounds** first |

- **Variety:** never the same file more than 4 times in a video (the validator warns at 5), and never on every cut.
- **No music beds, ever** (his rule). Short melodic stings under 2 s are fine.
- Loudness at export is his job. Remind him: about −14 LUFS integrated, true peak ≤ −1 dBTP (OFFICIAL: YouTube turns loud audio down but never turns quiet audio up).

## 6. Text pop-ups and numbers

- **What:** key English terms ("PLL", "F2L"), algorithms ("R U R' U'"), times and records ("8.53"), short Arabic punchlines (2–5 words), and labels ("GAN 14").
- **When:** the pop-up appears with the word (`at` = word start) and stays up for at least 0.6 s + characters/15 (the validator warns otherwise). Usually 1–2.5 s.
- **Styles:**
  - `pop`: big, white with a black outline.
  - `number`: big yellow; use for times and records.
  - `label`: dark pill; use for algorithms and names.
  - `warning`: red box; use for "DNF" and fails.
  - `caption`.
- **Position:**
  - `top` when his hands or cube are in the middle or bottom.
  - `upper` or `lower` for variety.
  - Never cover the cube during an algorithm.
- **Arabic:** always rendered by `text_cards.py`. Look at the preview, and check that every word is joined, with its hamza, in the right order.

## 7. Freeze frames and humor

- **Freeze** (`freeze`, 0.5–1.5 s, often `scale` 1.2–1.4) works on:
  - a fail, a lockup, a pop
  - a "wait what" moment
  - a funny face of the cube or the game
  - an add-on of a red `warning` pop-up plus a comic sting
- **Humor only where it is actually funny** (his rule): absurd lines he says, a cuber in-joke (pops, lockups, DNFs, +2, bad scramble), gaming fails.
  - Never repeat the same gag format back to back.
  - Default budget is 1 comic edit per 45–90 s.
- Recreate meme formats as original pop-ups. Never use meme *clips* or meme audio taken from memes. Meme-*style* sounds are allowed only from his own files or CC0 / CC BY sources (see §11).
- **Shake zoom** (`mode: "shake"`, scale 1.12–1.3, 0.3–1.0 s): the funny-hit zoom for fails and big reactions. Max 1 per 45–90 s. Pair it with a freeze or a hit sound, not with both plus a pop-up.

## 8. Transitions

- **Resolve 21.0.4 has no scripting command for transitions**, so they are always by-hand items (`transition`), with a red marker and an instruction.
- **Default:** hard cuts for ~90–95% of edits. Use a whip or zoom transition plus a whoosh only at chapter or section changes, 6–12 frames long. CRAFT; 2024 backlash coverage.
- **Never** a dissolve inside a tutorial step.
- For gaming, a dip-to-black or flash suits "3 hours later".
- You *can* place the whoosh SFX for a transition automatically: add a separate `sfx` item at the same time.

## 9. Chapters

OFFICIAL YouTube rules: the first chapter at 0:00, at least 3 chapters, each at least 10 s long. Put them at real section changes, with short titles in the video's language. `plan.py notes` writes the description lines.

## 10. Cubing videos (Syrian Rubik)

- Hands on the cube are the "Khan-style" visual that holds attention in tutorials (DATA: Guo et al. 2014, 6.9M edX sessions, older). Keep them visible. Add the notation as a `label` pop-up instead of covering them.
- A hold of up to 8–10 s while an algorithm runs is fine when it carries a notation label.
- **Time and record reveals:** big `number` pop-up + ding + 120% zoom on the timer.
- **Cube reviews:** B-roll of the cube from his own clips (close-ups, turning, magnets), plus a `label` with the model name.
- **Avoid** using "Rubik's" for non-Rubik's brand cubes in pop-ups ("puzzle cube" or the real brand); this is trademark-safe.

## 11. Gaming videos (SRB Gamer, his main channel)

Facts he gave: many different games, no face cam, mostly Syrian Arabic voice with some English game words, edits of about 6–10 per minute, "kills, wins and clutches", "fails and funny deaths", "reactions and shouting". What needs the most editing varies per video.

**Start from `analysis/moments.md`.** It ranks his loudest reactions and lists dead stretches. Look at each one on a contact sheet before you plan anything for it. Loudness alone cannot tell a kill from a fail.

| Moment | Edit recipe (pick one or two, not all) |
|---|---|
| Kill, win, clutch | Hard zoom on the kill feed, score or crosshair, landing on the first frame of the event (not the word). Short pop-up ("CLUTCH", the number). One hit sound, quiet. Or a 0.5 s freeze. |
| Fail, funny death | Freeze (0.5–1 s) plus a `shake` zoom, a meme-style hit sound, a short pop-up. Only if it is really funny. |
| Reaction, shouting | Hard zoom or `shake` on the loudest word. No pop-up if his words already say it. |
| Calm talking over gameplay | Slow push-in (`smooth`), or a pop-up for a number or term. |
| Dead stretch (menus, loading, waiting) | A `note` ("cut or speed up 4x here") with the exact times. The bridge cannot change speed. |

- **No face cam:** never plan a webcam reaction. Zoom centers go to the action, the HUD, the kill feed, the minimap or the score.
- **No B-roll over key gameplay.** B-roll is for talking parts only.
- **Never cover the HUD part that matters** (ammo, health, score, objective) with a pop-up. Use `position: top` or `lower` after looking at the sheet.
- **Meme-style sound hits** (bruh, boom, record scratch): only sounds that are CC0 or CC BY on Freesound, or his own. Never rip a sound from a meme or a video. The sound must be a different recording that merely *sounds* similar. Max 1 per 60–90 s, never the same sound twice in a row, level at −12 dB under his voice.
- In-game licensed music: add a `fix` note to mute it if it plays loudly (Content ID risk).
- **Different game each time:** put the game name into `brain/terms.md` before transcribing, so Whisper spells it right. Ask him for the exact name if you are not sure.
- **Syrian Rubik vs SRB Gamer:** read `references/channels.md` for the two profiles. Ask which channel the video belongs to if the project doesn't say.

## 12. What the research does and doesn't say

- **Hard pacing data:**
  - MrBeast at 38 cuts/min (2023) and 23 cuts/min (2024) (DATA, Tubefilter, one minute each).
  - Hollywood's average shot is about 2.5 s (DATA, Cutting et al.).
  - There is no data for cubing or gaming channels.
- **Retention benchmarks conflict 2×:** 23.7% vs 50–60% for 5–10 minute videos. Only compare against **his own "typical" band** in YouTube Studio (OFFICIAL).
- **Captions help:** old or self-reported data (Facebook +12% view time; a Verizon survey). The claims that word-by-word captions beat full lines come from vendors only.
- **Subtitle specs** (OFFICIAL, Netflix): ≤ 42 characters per line for Arabic, 5/6–7 s per event, a 2-frame gap, about 15–17 characters per second.
- **No controlled studies exist** on how often to use zooms or SFX. That's why the learning loop matters: after a few videos, his own data beats every number in this file.
