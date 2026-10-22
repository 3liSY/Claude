"""Turn the review video into signals Claude can read (Claude can't watch video).

  python analyze.py PROJECT

Reads PROJECT/review.mp4 (+ analysis/words.json if transcribed) and writes:
  analysis/probe.json     size, fps, duration, VFR warning
  analysis/signals.json   loudness peaks (emphasis), silences, motion curve, shot cuts, still stretches
  analysis/timeline.md    one line per 5 seconds: words + what the picture/audio does.
                          THE main thing to read before planning.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

import edcommon as ec

HOP = 0.05  # audio envelope step (s)
MOTION_FPS = 4


def audio_signals(media: Path) -> dict:
    y, sr = ec.decode_audio_mono(media, 16000)
    if y.size == 0:
        return {"silences": [], "peaks": [], "env_db": []}
    hop = int(sr * HOP)
    n = y.size // hop
    env = np.sqrt(np.mean(y[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(env + 1e-9)
    voiced = db[db > -60]
    speech_level = float(np.median(voiced)) if voiced.size else -30.0
    floor = float(np.percentile(db, 10))
    thr = min(max(floor + 8, speech_level - 18), speech_level - 6)  # never call steady talking "silence"
    # silences >= 0.4 s
    silences, start = [], None
    for i, v in enumerate(db):
        if v < thr and start is None:
            start = i
        elif v >= thr and start is not None:
            if (i - start) * HOP >= 0.4:
                silences.append([round(start * HOP, 2), round(i * HOP, 2)])
            start = None
    if start is not None and (n - start) * HOP >= 0.4:
        silences.append([round(start * HOP, 2), round(n * HOP, 2)])
    # emphasis peaks: short-term loudness well above the local (4 s) level
    k_short, k_long = 4, int(4 / HOP)
    short = np.convolve(db, np.ones(k_short) / k_short, mode="same")
    pad = k_long // 2
    voiced_only = np.where(db >= thr, db, np.nan)  # baseline = talking level, not pauses
    padded = np.pad(voiced_only, pad, mode="edge")
    with np.errstate(all="ignore"):
        import warnings

        warnings.simplefilter("ignore", RuntimeWarning)
        local = np.array([np.nanmedian(padded[i:i + k_long]) for i in range(0, n)]) if n else np.array([])
    local = np.where(np.isnan(local), speech_level, local)
    peaks = []
    last = -10.0
    for i in range(1, n - 1):
        lift = short[i] - local[i]
        if lift >= 6 and short[i] >= short[i - 1] and short[i] >= short[i + 1] and short[i] > speech_level - 3:
            t = i * HOP
            if t - last >= 1.5:
                peaks.append({"t": round(t, 2), "lift_db": round(float(lift), 1)})
                last = t
            elif peaks and lift > peaks[-1]["lift_db"]:
                peaks[-1] = {"t": round(t, 2), "lift_db": round(float(lift), 1)}
                last = t
    return {"speech_level_db": round(speech_level, 1), "silences": silences, "peaks": peaks,
            "env_db_4hz": [round(float(np.max(db[i:i + 5])), 1) for i in range(0, n, 5)]}


def motion_signals(media: Path, duration: float) -> dict:
    w, h = 64, 36
    cp = ec.run([ec.ffmpeg_bin(), "-v", "error", "-i", str(media), "-an", "-vf",
                 f"fps={MOTION_FPS},scale={w}:{h},format=gray", "-f", "rawvideo", "-"])
    frames = np.frombuffer(cp.stdout, dtype=np.uint8)
    nf = frames.size // (w * h)
    if nf < 2:
        return {"motion": [], "cuts": [], "still_stretches": []}
    fr = frames[: nf * w * h].reshape(nf, h, w).astype(np.float32)
    diff = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))  # mean abs change per step
    motion = np.concatenate([[0.0], diff])
    # hard cuts: big spike relative to neighbours
    cuts = []
    for i in range(1, nf):
        lo, hi = max(0, i - 8), min(nf, i + 8)
        neigh = np.median(motion[lo:hi])
        if motion[i] > 18 and motion[i] > 4 * (neigh + 1):
            t = round(i / MOTION_FPS, 2)
            if not cuts or t - cuts[-1] > 0.5:
                cuts.append(t)
    # still stretches: >= 6 s of low change and no cut (candidates for zoom/B-roll/pop-up)
    low = motion < 2.0
    stretches, start = [], None
    cutset = {int(c * MOTION_FPS) for c in cuts}
    for i in range(nf):
        quiet = low[i] and i not in cutset
        if quiet and start is None:
            start = i
        elif not quiet and start is not None:
            if (i - start) / MOTION_FPS >= 6:
                stretches.append([round(start / MOTION_FPS, 2), round(i / MOTION_FPS, 2)])
            start = None
    if start is not None and (nf - start) / MOTION_FPS >= 6:
        stretches.append([round(start / MOTION_FPS, 2), round(nf / MOTION_FPS, 2)])
    per_sec = [round(float(motion[i:i + MOTION_FPS].mean()), 2) for i in range(0, nf, MOTION_FPS)]
    return {"motion_per_sec": per_sec, "cuts": cuts, "still_stretches": stretches}


def level_word(v: float) -> str:
    return "still" if v < 1.5 else "low" if v < 4 else "med" if v < 10 else "high"


def timeline_md(info: dict, aud: dict, mot: dict, words: list[dict], window: float = 5.0) -> str:
    dur = info["duration"]
    lines = [f"# Timeline of the video ({ec.fmt_time(dur)}, {info.get('width')}x{info.get('height')} @ {info.get('fps')} fps)",
             "", "Legend: motion = how much the picture changes; cut = shot change; "
             "PEAK = loud/emphasized moment (+dB over surroundings); sil = silence.", ""]
    stats = summary_stats(info, aud, mot, words)
    lines += ["## Overview", *[f"- {k}: {v}" for k, v in stats.items()], ""]
    if mot.get("still_stretches"):
        lines.append("## Picture barely changes here (prime spots for zoom / B-roll / pop-up)")
        for a, b in mot["still_stretches"]:
            lines.append(f"- {ec.fmt_time(a)} – {ec.fmt_time(b)} ({b - a:.0f} s)")
        lines.append("")
    lines += ["## 5-second windows", ""]
    mps = mot.get("motion_per_sec", [])
    t = 0.0
    while t < dur:
        e = min(dur, t + window)
        ws = [w["w"] for w in words if t <= w["s"] < e]
        m = mps[int(t):int(e)] if mps else []
        mlevel = level_word(float(np.mean(m))) if m else "?"
        cuts = [c for c in mot.get("cuts", []) if t <= c < e]
        pk = []
        for p in aud.get("peaks", []):
            if t <= p["t"] < e:
                near = min(words, key=lambda w: abs(w["s"] - p["t"]), default=None) if words else None
                word = f' "{near["w"]}"' if near and abs(near["s"] - p["t"]) < 0.6 else ""
                pk.append(f"PEAK {ec.fmt_time(p['t'])}{word} +{p['lift_db']}dB")
        sil = [f"sil {ec.fmt_time(a)}–{ec.fmt_time(b)}" for a, b in aud.get("silences", [])
               if t <= a < e and b - a >= 0.6]
        tags = [f"motion {mlevel}"] + [f"cut {ec.fmt_time(c)}" for c in cuts] + pk + sil
        lines.append(f"[{ec.fmt_time(t)}–{ec.fmt_time(e)}] {'; '.join(tags)}")
        if ws:
            lines.append(f"    {' '.join(ws)}")
        t = e
    return "\n".join(lines) + "\n"


def summary_stats(info, aud, mot, words) -> dict:
    dur = info["duration"] or 1.0
    sil_total = sum(b - a for a, b in aud.get("silences", []))
    cuts = mot.get("cuts", [])
    st = {
        "length": ec.fmt_time(dur),
        "words": len(words),
        "speaking speed": f"{len(words) / (dur / 60):.0f} words/min" if words else "not transcribed yet",
        "silence": f"{sil_total:.0f} s total ({100 * sil_total / dur:.0f}%)",
        "shot cuts detected": f"{len(cuts)} (avg shot {dur / (len(cuts) + 1):.1f} s)",
        "emphasis peaks": len(aud.get("peaks", [])),
        "voice level": f"{aud.get('speech_level_db')} dBFS (median while talking)",
    }
    if info.get("vfr"):
        st["WARNING"] = "variable frame rate source: timing may drift; trust word times over frame counts"
    return st


def main() -> None:
    ec.setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", nargs="?")
    ap.add_argument("--media")
    args = ap.parse_args()
    proj = ec.resolve_project(args.project)
    media = Path(args.media) if args.media else proj / "review.mp4"
    if not media.exists():
        ec.die(f"Missing {media}. Run bridge_send.py prepare first (or export the timeline to that file).")
    info = ec.media_info(media)
    ec.write_json(proj / "analysis" / "probe.json", info)
    print("Listening to the audio ...")
    aud = audio_signals(media)
    print("Watching the picture ...")
    mot = motion_signals(media, info["duration"])
    words_p = proj / "analysis" / "words.json"
    words = ec.read_json(words_p)["words"] if words_p.exists() else []
    ec.write_json(proj / "analysis" / "signals.json", {"audio": aud, "motion": mot})
    md = timeline_md(info, aud, mot, words)
    ec.write_text(proj / "analysis" / "timeline.md", md)
    stats = summary_stats(info, aud, mot, words)
    for k, v in stats.items():
        print(f"{k}: {v}")
    print(f"Read: {proj / 'analysis' / 'timeline.md'}")


if __name__ == "__main__":
    main()
