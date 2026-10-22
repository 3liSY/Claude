# Sourcing clips and sounds (monetized-safe)

Checked 2026-10-22. License terms change, so re-check a site's license page before trusting a new source.

## Contents
1. Allowed / not allowed
2. Order of preference
3. API keys (free) and limits
4. The flow: search → show → OK → download → register
5. YouTube Creative Commons videos
6. Credits, Content ID, disputes
7. Gaming footage and cubing footage

## 1. Allowed / not allowed

| Source | OK? | Notes |
|---|---|---|
| His own clips and sounds | ✅ | Zero risk. Always first. Ask him to record cube sounds. |
| Pexels | ✅ | Free, monetized OK, no credit required (credit is polite). Clips reportedly have no audio. |
| Pixabay | ✅ | Free, no credit. Some *music* on Pixabay is registered with Content ID by contributors: no music anyway. |
| Coverr | ✅ | Free clips cleared for monetized YouTube, no credit. |
| Mixkit | ✅ | Free, no credit. No API. |
| YouTube Audio Library (SFX) | ✅ | YouTube says its copyright-safe music and SFX won't be claimed through Content ID. No API: he downloads them in Studio. |
| Freesound CC0 | ✅ | No credit. |
| Freesound CC BY | ✅ | **Credit required** in the description. |
| Freesound CC BY-NC / Sampling+ | ❌ | NonCommercial. Never. |
| Kenney (CC0 game audio) | ✅ | |
| Sonniss GDC bundles | ✅ | Royalty-free, no credit. |
| Zapsplat free tier | ⚠️ | Credit required. Paid tier removes it. |
| BBC Sound Effects (RemArc) | ❌ | Not for monetized use without a paid license. |
| YouTube videos with YouTube's **CC BY** license field | ✅ | Credit required. See §5. |
| "No copyright" in a title or description | ❌ | Means nothing. Only YouTube's license field counts. |
| Other creators' / WCA / brand clips | ⚠️ | Only with **written permission**. Draft the message for him; save the proof. |
| Any music bed | ❌ | His rule: no background music. |
| Memes, movie/TV clips, songs | ❌ | Recreate the idea as original pop-ups instead. |

Note: YouTube's Content ID rules say sound effects, Creative Commons and public-domain material, and non-exclusive content can't be registered as references. That makes claims on SFX structurally unlikely, but not impossible.

## 2. Order of preference

1. His own library: `library.py find`, then `library.py sheet`, and look at it.
2. Animation from video-maker, if he has it for this topic.
3. Pexels / Pixabay / Coverr / Mixkit.
4. YouTube CC BY.
5. Permission from creators.

Sounds: his own → YouTube Audio Library / Freesound CC0 / Mixkit / Kenney → Freesound CC BY.

## 3. API keys (he said "later"; set up when he's ready, 10 min, free)

They go in `EDITOR_HOME\keys.json`: `{"pexels": "...", "pixabay": "...", "freesound": "...", "youtube": "..."}`. Never print them in chat.

| Service | Where | Limits |
|---|---|---|
| Pexels | pexels.com/api → "Your API key" | 200 requests/hour, 20,000/month. Show a link to Pexels where results appear. |
| Pixabay | pixabay.com/api/docs (logged in) | 100 requests per 60 s. Cache results 24 h. |
| Freesound | freesound.org/apiv2/apply | 60/min, 2,000/day. A token is enough for search and previews. |
| YouTube Data API | console.cloud.google.com → YouTube Data API v3 → API key | Search costs 100 units of the 10,000/day quota. |
| Coverr | coverr.co/developers | 50/hour in demo. The skill uses browse links for Coverr. |

Without keys, `stock.py links "<words>"` prints ready search links, including the YouTube CC filter and Freesound CC0 only.

## 4. The flow

1. `stock.py search "<english words>" --project <p>` (add `--sfx` for sounds). Search in English: stock sites index English tags.
2. Candidates are saved in `analysis/candidates.json`. Put the good ones in the plan as `candidate:pexels:12345`. The sheet lists them under "Get these first".
3. **Checkpoint C:** show him the list (what, from where, which license, credit needed?) and ask for OK.
4. Only after OK: `stock.py download candidate:pexels:12345 --project <p>`. This:
   - saves the file to `library\stock\`
   - saves the API record next to it as proof (`.license.json`)
   - registers it in the library with its license and sha256
   - adds a row to `brain\license-log.csv`
   - prints the library id
5. Replace the `candidate:` ref with that library id. Run `plan.py validate --strict`.
6. Files he downloads himself (Mixkit, YouTube Audio Library, permission clips): `library.py register FILE --source mixkit --license "Mixkit License" --page URL [--creator] [--attribution]`.

## 5. YouTube Creative Commons videos

- Only YouTube's own license field counts: "Creative Commons Attribution license (reuse allowed)", shown under the description. Searching with the CC filter (`sp=EgIwAQ%253D%253D`, or the API's `videoLicense=creativeCommon`) finds them. Still check the field on the video page.
- **Credit** in the description: title, channel, link, "CC BY".
- **Getting the file:** YouTube's terms don't allow downloading with outside tools, and the skill does not do it. Tell him that plainly. He decides how to get the file (for example, asking the creator for it). Once he has it, register it with `--source youtube-cc`.
- A CC license on a video doesn't cover third-party content *inside* it, such as music playing in the background. Prefer clips without music.

## 6. Credits, Content ID, disputes

- `plan.py notes` collects all credits automatically.
- **Publish Unlisted first.** Wait for the copyright check in Studio before making it public.
- **If a claim lands on licensed material:**
  1. Dispute it with the license proof (from `license-log.csv` and the `.license.json` file).
  2. The claimant has 30 days to respond.
- Never dispute without a real license: a wrongful dispute can turn into a strike.
- There is no "safe number of seconds". Short excerpts have been matched.

## 7. Gaming footage and cubing footage

- **His own gameplay** is generally fine. Publisher policies (Nintendo lists the YouTube Partner Program; Epic, Minecraft) allow monetized videos with creative input. Riot bars its logos and trademarks without a license and requires a disclaimer.
- Watch for **licensed in-game music**: add a `fix` note to mute it.
- **WCA competition footage:** permission is needed from whoever filmed it. There is no general reuse policy.
- **Rubik's trademark:** say "puzzle cube" or the real brand for non-Rubik's cubes. No GAN or MoYu press kits were found, so ask those brands for permission if needed.
