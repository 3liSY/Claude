# The learning loop

Goal: after a few videos, his own behavior replaces every rule of thumb.

## Contents
1. After he fine-tunes (every video)
2. How to write a preference rule
3. Trends across videos
4. Edit log format
5. Retention review (after upload)
6. Things he says in chat

## 1. After he fine-tunes (every video)

1. He says he's done, or asks what you learned.
2. `bridge_send.py snapshot <p> --label after`
3. `learn.py <p>`. It compares every placed clip (by Resolve's unique id) with his timeline now:
   - **kept / deleted / moved / trimmed / extended / disabled / rezoomed** for each item
   - **added by him**: clips he put in himself, often things the plan missed
   - whether he changed his own cut, which makes the timing comparisons rougher
4. It prints suggested rules and appends a line to `brain/learned.jsonl`.
5. **You decide what's real.**
   - One deleted SFX is noise.
   - 4 of 6 whooshes deleted is a rule.
   - A consistent 0.1–0.2 s shift is a timing rule.
6. Write the rules into `brain/edit-preferences.md` → "Learned rules", dated.
7. Tell him in 2–5 plain bullets, for example:
   - "You removed most whooshes, so fewer whooshes from now on."
   - "You made zooms smaller (~115%), so I'll use 115–120%."
   - "You added a ding on every time reveal, so I'll do that myself next time."
8. Add the edit-log entry (§4).

Also learn from **checkpoint B and C**: items he rejected on the sheet (`status: rejected`), and his reasons, are the strongest signal of all.

## 2. How to write a preference rule

Specific, dated, measurable, with the evidence:

```
- 2026-10-29 (SR long-form, gan14 review): zoom punch-ins 115-120%, not 125%+ (he re-zoomed 5/7 down to ~117%).
- 2026-10-29: no whoosh on B-roll entries in tutorial sections (deleted 4/6); keep them at chapter changes.
- 2026-11-04 (SRB Gamer): he likes freeze + red "DNF"-style warning on deaths (kept 3/3, added 1 himself).
- ~~2026-10-29: zoom 115-120%~~ (superseded 2026-11-12: 120-125% on 4K footage).
```

- **Newest wins.** Strike through old lines; never delete them.
- **Keep the channels apart:** "SR" (Syrian Rubik) vs "SRB". A gaming habit is not a cubing rule.
- A preference also overrides the numbers in `editing-rules.md`.

## 3. Trends across videos

`brain/learned.jsonl` has one JSON line per video: per-type placed, kept and deleted counts, how many he added himself, and the suggestions. Every 3–5 videos, read it and look for:
- **steady deletion of a type**: lower that type's density
- **things he keeps adding himself**: the plan should do them
- **pacing choices** at checkpoint A: if he always picks the same option, make it the default and skip asking (tell him)

## 4. Edit log format (`brain/edit-log.md`, newest at the bottom)

```
## 2026-10-29 · 2026-10-29_gan14-review · plan v2
- channel: SR long-form, 12:41, 60 fps
- style: medium pacing, mix zooms, hard cuts + whoosh at chapters, srt captions, terms+numbers pop-ups
- placed: 9 zooms, 7 B-roll, 14 SFX, 8 pop-ups, 1 freeze; by hand: 3 transitions, 2 notes
- he changed: deleted 4 whooshes, re-zoomed 5, moved 2 B-roll earlier, added 2 dings
- learned: (the bullets you told him)
- uploaded: no   · retention: pending
```

When he says it's uploaded, change it to `uploaded: yes (YYYY-MM-DD)`. At the start of every session, remind him about any `uploaded: yes` with `retention: pending` that is 3 or more days old.

## 5. Retention review (after upload)

1. Ask for a screenshot of YouTube Studio → the video → Engagement → Audience retention, plus the "Key moments" (Intro, Top moments, Spikes, Dips). A CSV works too, if he exports one.
2. Read the times off the graph: dips, spikes, and the 30 s "Intro" value.
3. `retention.py <p> --dips 1:23,4:05 --spikes 2:10`. It lists what he said and which edits were nearby.
4. Explain plainly. Judge only against **his own "typical" band**, never internet benchmarks, which conflict 2×.
   - **Dip:** something slowed down, confused people, or overstayed. Look at the planned edits and the still stretches there.
   - **Spike:** a rewatch: great, or confusing. Read the context.
   - **Low Intro (30 s):** the hook needs work next time.
5. Turn a pattern into a rule only after seeing it in **2 or more videos**. Log `retention: done` with one line of findings.

## 6. Things he says in chat

Any direct statement ("I hate the whoosh sound", "zooms are too much") goes straight into preferences, dated, and it beats every measured trend. Confirm it in one line.
