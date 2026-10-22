"""Word-by-word transcript with timestamps (faster-whisper, runs on his GPU).

  python transcribe.py PROJECT            # uses PROJECT/review.mp4
  python transcribe.py PROJECT --media other.wav --lang ar

Writes analysis/words.json (every word with start/end seconds) and
analysis/transcript.txt (one short line per phrase, for reading).

English terms inside Syrian Arabic (F2L, PLL, TPS...) often come out in Arabic
letters or get dropped. brain/terms.md lists them and their common mis-hearings;
they are fixed after transcription. Timing matters more than spelling here: the
plan hangs every edit on word timing.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import edcommon as ec

DEFAULT_TERMS = """# Terms the skill keeps in English (Latin letters).
# Format:  CANONICAL: variant | variant | variant
# Variants are how Whisper tends to write them in Arabic letters. Add new ones as you see them.
F2L: اف تو ال | إف تو إل | اف٢ل | f2l
OLL: او ال ال | أو إل إل | اول | oll
PLL: بي ال ال | بي إل إل | بيل | pll
TPS: تي بي اس | تي بي إس | tps
WCA: دبليو سي اي | دبليو سي إيه | wca
DNF: دي ان اف | دي إن إف | dnf
lookahead: لوك اهيد | لوك أهيد | لوكهيد
scramble: سكرامبل | سكرامبلة
lockup: لوك اب | لوكاب
GAN: غان
MoYu: مويو | موي يو
"""


def terms_path() -> Path:
    return ec.brain_dir() / "terms.md"


def load_terms() -> dict[str, list[str]]:
    p = terms_path()
    if not p.exists():
        ec.write_text(p, DEFAULT_TERMS)
    terms: dict[str, list[str]] = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        canon, variants = line.split(":", 1)
        canon = canon.strip()
        terms[canon] = [v.strip() for v in variants.split("|") if v.strip()]
    # video-maker's glossary (read only) adds more English terms to the prompt
    gl = Path.home() / "SyrianRubikStudio" / "_brain" / "glossary.md"
    if gl.exists():
        for word in re.findall(r"\b[A-Z][A-Za-z0-9+']{1,15}\b", gl.read_text(encoding="utf-8", errors="replace")):
            terms.setdefault(word, [])
    return terms


def norm(s: str) -> str:
    s = re.sub(r"[ً-ْـ]", "", s)  # tashkeel + tatweel
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    return re.sub(r"[^\w؀-ۿ]+", "", s.lower())


def fix_terms(words: list[dict], terms: dict[str, list[str]]) -> tuple[list[dict], int]:
    """Replace (multi-word) Arabic spellings of English terms with the term."""
    patterns = []
    for canon, variants in terms.items():
        for v in variants + [canon]:
            toks = [norm(t) for t in v.split() if norm(t)]
            if toks:
                patterns.append((toks, canon))
    patterns.sort(key=lambda p: -len(p[0]))  # longest first
    out, i, fixed = [], 0, 0
    normed = [norm(w["w"]) for w in words]
    while i < len(words):
        hit = None
        for toks, canon in patterns:
            n = len(toks)
            seg = normed[i:i + n]
            if len(seg) == n and all(a == b or (b.startswith("ال") and a == b[2:]) or a == "ال" + b
                                     for a, b in zip(toks, seg)):
                hit = (n, canon)
                break
            joined = "".join(toks)  # Whisper sometimes glues the letters into one word
            if n > 1 and normed[i] in (joined, "ال" + joined):
                hit = (1, canon)
                break
        if hit:
            n, canon = hit
            first, last = words[i], words[i + n - 1]
            prefix = "الـ " if normed[i].startswith("ال") and not norm(canon).startswith("ال") else ""
            new = {"w": prefix + canon, "s": first["s"], "e": last["e"], "p": min(w["p"] for w in words[i:i + n])}
            if new["w"] != first["w"] or n > 1:
                fixed += 1
            out.append(new)
            i += n
        else:
            out.append(words[i])
            i += 1
    return out, fixed


def build_prompt(terms: dict[str, list[str]]) -> str:
    latin = [t for t in terms if re.match(r"^[A-Za-z0-9'+ ]+$", t)][:40]
    return "حكي سوري عن مكعب روبيك والألعاب. مصطلحات بالإنكليزي: " + ", ".join(latin) + "."


def transcribe(media: Path, lang: str, cfg: dict, terms: dict) -> dict:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        ec.die("faster-whisper is not installed. Run setup_check.py to see what's missing.")
    wcfg = cfg["whisper"]
    attempts = [(wcfg["device"], wcfg["compute_type"]), ("cuda", "int8_float16"), ("cpu", "int8")]
    model, used = None, None
    for device, ctype in attempts:
        try:
            model = WhisperModel(wcfg["model"], device=device, compute_type=ctype)
            used = (device, ctype)
            break
        except Exception as e:  # no CUDA / not enough VRAM -> next option
            print(f"(could not load on {device}/{ctype}: {str(e)[:120]})")
    if model is None:
        ec.die("Could not load the Whisper model.")
    print(f"Transcribing with {wcfg['model']} on {used[0]} ({used[1]}) ...")
    kwargs = dict(language=lang, word_timestamps=True, vad_filter=True, beam_size=5,
                  vad_parameters={"min_silence_duration_ms": 300}, condition_on_previous_text=False,
                  initial_prompt=build_prompt(terms))
    hot = " ".join(t for t in terms if re.match(r"^[A-Za-z0-9]+$", t))
    try:
        segments, info = model.transcribe(str(media), hotwords=hot, **kwargs)
    except TypeError:  # older faster-whisper without hotwords
        segments, info = model.transcribe(str(media), **kwargs)
    words, segs = [], []
    for seg in segments:
        segs.append({"s": round(seg.start, 3), "e": round(seg.end, 3), "text": seg.text.strip()})
        for w in seg.words or []:
            words.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3),
                          "p": round(w.probability, 3)})
        print(f"  {ec.fmt_time(seg.start)}  {seg.text.strip()[:70]}")
    return {"language": info.language, "duration": round(info.duration, 3), "model": wcfg["model"],
            "device": used[0], "words": words, "segments": segs}


def transcript_lines(words: list[dict], max_chars: int = 70, gap: float = 0.6) -> list[str]:
    """Phrase-per-line text with start times; breaks on pauses and length."""
    lines, cur, start, last_e = [], [], None, None
    for w in words:
        if cur and (w["s"] - last_e > gap or len(" ".join(cur)) + len(w["w"]) > max_chars):
            lines.append(f"[{ec.fmt_time(start)}] {' '.join(cur)}")
            cur, start = [], None
        if start is None:
            start = w["s"]
        cur.append(w["w"])
        last_e = w["e"]
    if cur:
        lines.append(f"[{ec.fmt_time(start)}] {' '.join(cur)}")
    return lines


def main() -> None:
    ec.setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", nargs="?")
    ap.add_argument("--media")
    ap.add_argument("--lang")
    ap.add_argument("--refix", action="store_true", help="only re-apply terms.md to existing words.json")
    args = ap.parse_args()
    proj = ec.resolve_project(args.project)
    cfg = ec.load_config()
    terms = load_terms()
    out = proj / "analysis" / "words.json"
    if args.refix:
        data = ec.read_json(out)
        data["words"] = data.get("raw_words", data["words"])
    else:
        media = Path(args.media) if args.media else proj / "review.mp4"
        if not media.exists():
            ec.die(f"No media to transcribe: {media}")
        data = transcribe(media, args.lang or cfg["whisper"]["language"], cfg, terms)
        data["raw_words"] = data["words"]
    data["words"], fixed = fix_terms(data["raw_words"], terms)
    ec.write_json(out, data)
    lines = transcript_lines(data["words"])
    ec.write_text(proj / "analysis" / "transcript.txt", "\n".join(lines) + "\n")
    low = sum(1 for w in data["words"] if w["p"] < 0.4)
    print(f"Done: {len(data['words'])} words, {fixed} term fixes, {low} low-confidence words.")
    print(f"Read: {proj / 'analysis' / 'transcript.txt'}")


if __name__ == "__main__":
    main()
