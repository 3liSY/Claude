"""His own B-roll and SFX library: index, look, search, level.

  python library.py add-folder broll "D:/Videos/cube clips"
  python library.py add-folder sfx "D:/SFX"
  python library.py index                 # scan folders (fast, incremental)
  python library.py sheet --kind clips    # contact sheets of clip strips for Claude to look at
  python library.py find "cube explode"   # keyword search (+ AI search if `embed` was run)
  python library.py note c-cube-pop-3f2a "slow-mo cube pop, red cube, white table"
  python library.py embed                 # optional AI index (needs torch + open_clip, asks first)
  python library.py register FILE --source pexels --id 123 --page URL --creator NAME --license "Pexels License"
"""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

import edcommon as ec

STRIP_W, STRIP_H = 320, 180
BAD_LICENSE = re.compile(r"\b(nc|non-?commercial|nd|no-?deriv)", re.I)


def lib_path() -> Path:
    return ec.library_dir() / "index" / "library.json"


def load_library() -> dict:
    p = lib_path()
    if p.exists():
        return ec.read_json(p)
    return {"version": 1, "clips": {}, "sfx": {}}


def save_library(lib: dict) -> None:
    lib["updated"] = ec.now_iso()
    ec.write_json(lib_path(), lib)


def make_id(path: Path, prefix: str) -> str:
    stem = ec.slugify(path.stem)[:28] or "file"
    h = hashlib.sha1(str(path.resolve()).lower().encode("utf-8")).hexdigest()[:4]
    return f"{prefix}-{stem}-{h}"


def tags_from_path(path: Path, root: Path) -> list[str]:
    words = []
    try:
        rel = path.relative_to(root)
        parts = list(rel.parts[:-1]) + [path.stem]
    except ValueError:
        parts = [path.stem]
    for p in parts:
        words += [w for w in re.split(r"[^0-9A-Za-z\u0600-\u06FF]+", p.lower()) if len(w) > 1]
    return sorted(set(words))


def bad_license(text: str | None) -> bool:
    return bool(text) and bool(BAD_LICENSE.search(text))


# ------------------------------------------------------------------ indexing


def scan_folder(root: Path, exts: set[str]):
    if not root.exists():
        print(f"  (folder not found, skipped: {root})")
        return
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts and not p.name.startswith("."):
            yield p


def clip_strip(path: Path, info: dict, out: Path, label: str) -> None:
    """Three frames side by side (15%, 50%, 85%) with the id written on it."""
    from PIL import Image, ImageDraw

    dur = max(0.1, info.get("duration") or 0.1)
    tiles = []
    for frac in (0.15, 0.5, 0.85):
        cp = ec.run([ec.ffmpeg_bin(), "-v", "error", "-ss", f"{dur * frac:.3f}", "-i", str(path),
                     "-frames:v", "1", "-vf", f"scale={STRIP_W}:{STRIP_H}:force_original_aspect_ratio=decrease,"
                     f"pad={STRIP_W}:{STRIP_H}:(ow-iw)/2:(oh-ih)/2", "-f", "image2pipe", "-vcodec", "png", "-"],
                    check=False)
        if cp.returncode == 0 and cp.stdout:
            import io

            tiles.append(Image.open(io.BytesIO(cp.stdout)).convert("RGB"))
        else:
            tiles.append(Image.new("RGB", (STRIP_W, STRIP_H), (40, 40, 40)))
    strip = Image.new("RGB", (STRIP_W * 3, STRIP_H + 26), (16, 16, 16))
    for i, t in enumerate(tiles):
        strip.paste(t, (i * STRIP_W, 26))
    d = ImageDraw.Draw(strip)
    d.text((6, 6), label, fill=(255, 220, 80))
    out.parent.mkdir(parents=True, exist_ok=True)
    strip.save(out, quality=85)


def sfx_features(path: Path) -> dict:
    import numpy as np

    y, sr = ec.decode_audio_mono(path, 16000)
    if y.size == 0:
        return {"peak_offset": 0.0, "peak_db": -120.0, "rms_db": -120.0}
    win = int(sr * 0.01)
    n = max(1, y.size // win)
    env = np.sqrt(np.mean(y[: n * win].reshape(n, win) ** 2, axis=1) + 1e-12)
    peak_i = int(np.argmax(env))
    # loudest 300 ms window = how loud the sound "feels"
    k = max(1, int(0.3 / 0.01))
    if n > k:
        roll = np.convolve(env ** 2, np.ones(k) / k, mode="valid")
        loud = float(np.sqrt(roll.max()))
    else:
        loud = float(np.sqrt(np.mean(env ** 2)))
    return {
        "peak_offset": round(peak_i * 0.01, 3),
        "peak_db": round(20 * np.log10(float(np.max(np.abs(y))) + 1e-12), 1),
        "loud_db": round(20 * np.log10(loud + 1e-12), 1),
    }


def cmd_index(args) -> None:
    cfg = ec.load_config()
    lib = load_library()
    seen = set()
    stock = ec.library_dir() / "stock"
    groups = [("clips", "c", ec.VIDEO_EXT | ec.IMAGE_EXT, cfg["library"]["broll_folders"] + [str(stock / "video")]),
              ("sfx", "s", ec.AUDIO_EXT, cfg["library"]["sfx_folders"] + [str(stock / "sfx")])]
    for kind, prefix, exts, folders in groups:
        if not folders:
            continue
        print(f"Scanning {kind} ...")
        for folder in folders:
            root = Path(folder)
            for p in scan_folder(root, exts):
                cid = make_id(p, prefix)
                seen.add(cid)
                st = p.stat()
                old = lib[kind].get(cid)
                if old and old.get("size") == st.st_size and old.get("mtime") == int(st.st_mtime) and not args.force:
                    continue
                try:
                    info = ec.media_info(p)
                except SystemExit:
                    print(f"  skipped (unreadable): {p.name}")
                    continue
                entry = old or {}
                entry.update({
                    "id": cid, "path": str(p.resolve()), "size": st.st_size, "mtime": int(st.st_mtime),
                    "duration": round(info.get("duration", 0.0), 3), "tags": tags_from_path(p, root),
                })
                entry.setdefault("source", "own")
                entry.setdefault("license", "own footage" if kind == "clips" else "own / already owned")
                if kind == "clips":
                    entry.update({k: info.get(k) for k in ("width", "height", "fps", "vfr", "has_audio")})
                    entry["kind"] = "image" if p.suffix.lower() in ec.IMAGE_EXT else "video"
                    thumb = ec.library_dir() / "index" / "thumbs" / f"{cid}.jpg"
                    try:
                        clip_strip(p, info, thumb, f"{cid}  {entry['duration']:.1f}s  {info.get('width')}x{info.get('height')}")
                        entry["thumb"] = str(thumb)
                    except Exception as e:  # thumbnails are a nicety, never fatal
                        print(f"  (no thumbnail for {p.name}: {e})")
                else:
                    entry.update(sfx_features(p))
                lib[kind][cid] = entry
                print(f"  + {cid}")
    # forget files that disappeared from configured folders
    for kind in ("clips", "sfx"):
        for cid in list(lib[kind]):
            if cid not in seen and not Path(lib[kind][cid]["path"]).exists():
                del lib[kind][cid]
    save_library(lib)
    print(f"Library: {len(lib['clips'])} clips, {len(lib['sfx'])} sounds.")


def cmd_sheet(args) -> None:
    """Grid of clip strips (6 per image) so Claude can see the library."""
    from PIL import Image

    lib = load_library()
    entries = [e for e in lib["clips"].values() if e.get("thumb") and Path(e["thumb"]).exists()]
    if args.tag:
        entries = [e for e in entries if args.tag.lower() in " ".join(e.get("tags", [])).lower()]
    entries.sort(key=lambda e: e["id"])
    out_dir = ec.library_dir() / "index" / "sheets"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("clips_*.jpg"):
        old.unlink()
    per = 6
    paths = []
    for n in range(0, len(entries), per):
        chunk = entries[n:n + per]
        sheet = Image.new("RGB", (STRIP_W * 3, (STRIP_H + 26) * len(chunk)), (0, 0, 0))
        for i, e in enumerate(chunk):
            sheet.paste(Image.open(e["thumb"]), (0, i * (STRIP_H + 26)))
        p = out_dir / f"clips_{n // per + 1:03d}.jpg"
        sheet.save(p, quality=82)
        paths.append(p)
    print(f"{len(paths)} sheet(s) in {out_dir}")
    for p in paths:
        print(p)


def keyword_score(e: dict, words: list[str]) -> float:
    hay = " ".join([e["id"], " ".join(e.get("tags", [])), e.get("note", ""), Path(e["path"]).stem]).lower()
    return sum(1.0 for w in words if w in hay)


def cmd_find(args) -> None:
    lib = load_library()
    kind = "sfx" if args.sfx else "clips"
    words = [w for w in re.split(r"\s+", args.query.lower()) if w]
    scores = {cid: keyword_score(e, words) for cid, e in lib[kind].items()}
    emb_used = False
    if kind == "clips":
        sem = semantic_scores(args.query)
        if sem:
            emb_used = True
            for cid, s in sem.items():
                scores[cid] = scores.get(cid, 0) + 3.0 * s
    ranked = sorted(((s, cid) for cid, s in scores.items() if s > 0), reverse=True)[: args.top]
    print(f"{'AI + keyword' if emb_used else 'keyword'} search: {args.query!r}")
    for s, cid in ranked:
        e = lib[kind][cid]
        print(f"{cid}  score={s:.2f}  {e.get('duration', 0):.1f}s  {e.get('note', '')}  [{', '.join(e.get('tags', [])[:6])}]")
    if not ranked:
        print("(nothing found)")


def cmd_note(args) -> None:
    lib = load_library()
    for kind in ("clips", "sfx"):
        if args.id in lib[kind]:
            lib[kind][args.id]["note"] = args.text
            save_library(lib)
            print(f"Saved note for {args.id}")
            return
    ec.die(f"No library item with id {args.id}")


def cmd_add_folder(args) -> None:
    cfg = ec.load_config()
    key = "broll_folders" if args.kind == "broll" else "sfx_folders"
    path = str(Path(args.path).resolve())
    if path not in cfg["library"][key]:
        cfg["library"][key].append(path)
    ec.save_config(cfg)
    print(f"{args.kind} folders: {cfg['library'][key]}")


def cmd_register(args) -> None:
    """Add an approved outside file (stock / CC) with its license record."""
    if bad_license(args.license):
        ec.die(f"License '{args.license}' is NonCommercial or NoDerivatives: not allowed on a monetized channel.")
    p = Path(args.file).resolve()
    if not p.exists():
        ec.die(f"File not found: {p}")
    kind = "sfx" if p.suffix.lower() in ec.AUDIO_EXT else "clips"
    lib = load_library()
    cid = make_id(p, "s" if kind == "sfx" else "c")
    info = ec.media_info(p)
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    entry = {"id": cid, "path": str(p), "size": p.stat().st_size, "mtime": int(p.stat().st_mtime),
             "duration": round(info.get("duration", 0.0), 3), "tags": tags_from_path(p, p.parent),
             "source": args.source, "source_id": args.id, "page_url": args.page, "creator": args.creator,
             "license": args.license, "license_url": args.license_url, "attribution": args.attribution,
             "sha256": sha, "registered": ec.now_iso()}
    if kind == "clips":
        entry.update({k: info.get(k) for k in ("width", "height", "fps", "vfr", "has_audio")})
        entry["kind"] = "image" if p.suffix.lower() in ec.IMAGE_EXT else "video"
        thumb = ec.library_dir() / "index" / "thumbs" / f"{cid}.jpg"
        try:
            clip_strip(p, info, thumb, f"{cid}  {entry['duration']:.1f}s")
            entry["thumb"] = str(thumb)
        except Exception:
            pass
    else:
        entry.update(sfx_features(p))
    lib[kind][cid] = entry
    save_library(lib)
    log_license(entry)
    print(f"Registered {cid} ({args.source}, {args.license})")


def log_license(entry: dict) -> None:
    import csv

    path = ec.brain_dir() / "license-log.csv"
    new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date", "library_id", "file", "source", "source_id", "page_url", "creator",
                        "license", "license_url", "attribution", "sha256", "used_in"])
        w.writerow([ec.today(), entry["id"], entry["path"], entry.get("source"), entry.get("source_id"),
                    entry.get("page_url"), entry.get("creator"), entry.get("license"),
                    entry.get("license_url"), entry.get("attribution"), entry.get("sha256"), ""])


# ------------------------------------------------------------------ assets for plans


def resolve_asset(ref: str, lib: dict | None = None) -> dict:
    """Plan asset ref -> library entry. Accepts a library id or a file path."""
    lib = lib or load_library()
    for kind in ("clips", "sfx"):
        if ref in lib[kind]:
            e = dict(lib[kind][ref])
            e["lib_kind"] = kind
            return e
    p = Path(ref)
    if p.exists():
        kind = "sfx" if p.suffix.lower() in ec.AUDIO_EXT else "clips"
        for e in lib[kind].values():
            if Path(e["path"]).resolve() == p.resolve():
                e = dict(e)
                e["lib_kind"] = kind
                return e
        return {"id": None, "path": str(p.resolve()), "lib_kind": kind, "source": "unindexed",
                "license": None}
    return {}


def level_sfx(entry: dict, gain_db: float = 0.0, target_loud_db: float = -20.0) -> tuple[Path, float]:
    """Copy of the sound at a consistent loudness (+gain). Returns (path, peak_offset)."""
    src = Path(entry["path"])
    loud = entry.get("loud_db")
    if loud is None:
        feats = sfx_features(src)
        loud, peak_db, offset = feats["loud_db"], feats["peak_db"], feats["peak_offset"]
    else:
        peak_db, offset = entry.get("peak_db", -1.0), entry.get("peak_offset", 0.0)
    change = (target_loud_db - loud) + float(gain_db)
    change = min(change, -1.0 - peak_db)  # never clip: peak stays under -1 dBFS
    tag = f"{change:+.1f}".replace(".", "p")
    out = ec.library_dir() / "cache" / "sfx" / f"{entry.get('id') or ec.slugify(src.stem)}_{tag}.wav"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        ec.run([ec.ffmpeg_bin(), "-v", "error", "-y", "-i", str(src), "-af", f"volume={change:.2f}dB",
                "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(out)])
    return out, float(offset)


# ------------------------------------------------------------------ optional AI search


def emb_paths():
    d = ec.library_dir() / "index"
    return d / "clip_emb.npy", d / "clip_emb_ids.json"


def _load_clip_model():
    import open_clip  # optional install (Full)
    import torch

    model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k")
    tokenizer = open_clip.get_tokenizer("ViT-B-32")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return model.to(device).eval(), preprocess, tokenizer, device


def cmd_embed(args) -> None:
    try:
        import numpy as np
        import torch
        from PIL import Image
    except ImportError:
        ec.die("AI search needs the Full install (torch + open_clip). Ask him first.")
    model, preprocess, _, device = _load_clip_model()
    lib = load_library()
    ids, vecs = [], []
    for cid, e in sorted(lib["clips"].items()):
        if not e.get("thumb") or not Path(e["thumb"]).exists():
            continue
        strip = Image.open(e["thumb"]).convert("RGB")
        tiles = [strip.crop((i * STRIP_W, 26, (i + 1) * STRIP_W, 26 + STRIP_H)) for i in range(3)]
        with torch.no_grad():
            batch = torch.stack([preprocess(t) for t in tiles]).to(device)
            f = model.encode_image(batch).float()
            f = f / f.norm(dim=-1, keepdim=True)
            v = f.mean(0)
            v = v / v.norm()
        ids.append(cid)
        vecs.append(v.cpu().numpy())
    e_npy, e_ids = emb_paths()
    np.save(e_npy, np.stack(vecs) if vecs else np.zeros((0, 512), dtype=np.float32))
    ec.write_json(e_ids, ids)
    print(f"AI index built for {len(ids)} clips.")


def semantic_scores(query: str) -> dict:
    e_npy, e_ids = emb_paths()
    if not e_npy.exists():
        return {}
    try:
        import numpy as np
        import torch

        model, _, tokenizer, device = _load_clip_model()
    except Exception:
        return {}
    ids = ec.read_json(e_ids)
    mat = np.load(e_npy)
    with torch.no_grad():
        t = model.encode_text(tokenizer([query]).to(device)).float()
        t = (t / t.norm(dim=-1, keepdim=True)).cpu().numpy()[0]
    sims = mat @ t
    return {cid: float(s) for cid, s in zip(ids, sims) if s > 0.2}


def main() -> None:
    ec.setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("index"); s.add_argument("--force", action="store_true"); s.set_defaults(fn=cmd_index)
    s = sub.add_parser("sheet"); s.add_argument("--kind", default="clips"); s.add_argument("--tag"); s.set_defaults(fn=cmd_sheet)
    s = sub.add_parser("find"); s.add_argument("query"); s.add_argument("--sfx", action="store_true")
    s.add_argument("--top", type=int, default=12); s.set_defaults(fn=cmd_find)
    s = sub.add_parser("note"); s.add_argument("id"); s.add_argument("text"); s.set_defaults(fn=cmd_note)
    s = sub.add_parser("add-folder"); s.add_argument("kind", choices=["broll", "sfx"]); s.add_argument("path")
    s.set_defaults(fn=cmd_add_folder)
    s = sub.add_parser("embed"); s.set_defaults(fn=cmd_embed)
    s = sub.add_parser("register"); s.add_argument("file"); s.add_argument("--source", required=True)
    s.add_argument("--id"); s.add_argument("--page"); s.add_argument("--creator"); s.add_argument("--license", required=True)
    s.add_argument("--license-url"); s.add_argument("--attribution"); s.set_defaults(fn=cmd_register)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
