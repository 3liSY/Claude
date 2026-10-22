# Arabic speech, terms and captions

## Contents
1. Transcription: what to expect
2. terms.md: keeping English terms in English
3. Captions: .srt for YouTube (default)
4. Burned-in captions
5. Arabic on screen: the rendering rule

## 1. Transcription: what to expect

- faster-whisper large-v3 (not turbo) on his RTX 4060: about 4–6× real time, so roughly 3 minutes for a 15-minute video. The first run downloads the model, which needs his **OK**.
- **Syrian dialect is hard.** One 2026 benchmark measured Whisper large-v3 at about 59% word error on Syrian speakers. Expect wrong words.
  - **Timing is still good**, and the plan only needs timing. It hangs edits on when words happen, not on perfect spelling.
- **Mixed Arabic and English:** one study found Whisper produced *no* English words when speakers mixed the two. So "PLL" may come out as "بي ال ال" or vanish. The skill prompts Whisper with the terms and then fixes known spellings (§2).
- If a key word is missing at a moment you need, look at the contact sheet and his loudness peaks around there. Or ask him: "At 2:13, what do you say?"
- Low-confidence words (`p < 0.4` in `words.json`) are where mishearings cluster. Never quote them on screen without checking.
- If timing must be frame-tight (comic beats), make a dense contact sheet of that second, and trust the picture plus the loudness peak.

## 2. terms.md: keeping English terms in English

`brain/terms.md` lines look like `PLL: بي ال ال | بي إل إل | بيل`. That is the canonical term, then the Arabic-letter spellings Whisper produced.

- Every time you spot a new mangled spelling in `transcript.txt`, add it, then run `transcribe.py <p> --refix`. That is instant, with no new transcription.
- The fixer handles one-word or multi-word spellings, and an attached "ال" (it becomes "الـ PLL").
- Add gaming terms the same way: game names, "clutch", "headshot", and so on.
- video-maker's `_brain\glossary.md` is read for extra English terms. Never write to it.

## 3. Captions: .srt for YouTube (default)

- `plan.py srt <p>` writes `out\captions.srt`:
  - UTF-8
  - 1 line of ≤ 42 characters (or `--two-lines`)
  - on screen 0.83–7 s, ≤ 17 characters per second
  - a 2-frame gap
  - breaks on pauses and punctuation
  - Netflix Arabic specs (OFFICIAL)
- Times are video times, starting at 0, which is what YouTube expects.
- **He must read it before uploading**, because of the error rate. Offer to fix the wording: he tells you the right words, and you edit the .srt directly.
- Upload as an "Arabic" subtitle track in YouTube Studio.

## 4. Burned-in captions (only if he picks them for a video)

- `plan.py captions <p> [--max-chars 32] [--position bottom]` adds `K001...` caption items from the word timings to the latest plan. Correct the texts in the plan first, using his corrections or the script if he has one.
- At apply time each caption becomes a full-frame PNG card on `ED CAPTIONS`. Rendering is a browser screenshot per card (about 0.5 s each), so a 15-minute video takes a few minutes.
- Keep them clear of his hands and the cube. If the cube sits at the bottom, use `--position upper`.
- Resolve's own subtitle track is **not** used for Arabic: letters break, and captions vanish when stroke is above 0, a long-known bug.

## 5. Arabic on screen: the rendering rule

- **Never** type Arabic into Resolve Text+, titles, or subtitle styling. It breaks: letters come out disconnected and in reverse order (this broke one of his uploads before).
- All on-screen text comes from `text_cards.py`. A real browser engine shapes Arabic correctly: joined letters, right-to-left, and mixed English and numbers in the right order (`هاد الـ PLL`, `8.53`, `R U R'`).
- **After rendering:**
  1. Open the `_preview.jpg` grid, and the full-size PNG for anything doubtful.
  2. Check every word is joined, with its hamza, in the right order.
  3. Check that numbers and English read left-to-right inside the Arabic.
- **Fonts:** the cards try Cairo, Tajawal, Noto Kufi Arabic, Segoe UI and Tahoma, in that order. If he has a brand font from video-maker, add it to `FONT_STACK` in `text_cards.py` (installed fonts only).
