"""Contact sheets: frames of the video in a grid, each stamped with its time.

This is how Claude "sees" the video. Each sheet is at most 1568 px wide (the
size Claude reads without shrinking).

  python sheets.py PROJECT                         # whole video, auto spacing (<= ~240 frames)
  python sheets.py PROJECT --every 1 --start 60 --end 90     # dense look at one part
  python sheets.py PROJECT --at 12.5,30.2,61 --thumbs        # single thumbnails for the edit sheet
"""
from __future__ import annotations

import argparse
import io
import math
import tempfile
from pathlib import Path

import edcommon as ec

TILE_W = 392  # 4 columns -> 1568 px


def label(img, text: str):
    from PIL import ImageDraw, ImageFont

    try:
        font = ImageFont.load_default(size=20)
    except TypeError:  # Pillow < 10.1
        font = ImageFont.load_default()
    d = ImageDraw.Draw(img)
    box = d.textbbox((0, 0), text, font=font)
    d.rectangle([0, 0, box[2] + 10, box[3] + 8], fill=(0, 0, 0))
    d.text((5, 3), text, fill=(255, 230, 60), font=font)
    return img


def extract_range(media: Path, start: float, end: float, every: float, tmp: Path) -> list[tuple[float, Path]]:
    """One ffmpeg pass: frames at start, start+every, ..."""
    pattern = tmp / "f_%05d.jpg"
    ec.run([ec.ffmpeg_bin(), "-v", "error", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(media),
            "-an", "-vf", f"fps=1/{every},scale={TILE_W}:-2", "-q:v", "4", str(pattern)])
    frames = sorted(tmp.glob("f_*.jpg"))
    return [(start + i * every, p) for i, p in enumerate(frames)]


def build_sheets(frames: list[tuple[float, Path]], out_dir: Path, cols: int, rows: int, prefix: str) -> list[Path]:
    from PIL import Image

    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob(f"{prefix}_*.jpg"):
        old.unlink()
    per = cols * rows
    paths = []
    for n in range(0, len(frames), per):
        chunk = frames[n:n + per]
        first = Image.open(chunk[0][1])
        tw, th = first.size
        r = math.ceil(len(chunk) / cols)
        sheet = Image.new("RGB", (tw * cols, th * r), (0, 0, 0))
        for i, (t, p) in enumerate(chunk):
            im = label(Image.open(p).convert("RGB"), ec.fmt_time(t))
            sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
        path = out_dir / f"{prefix}_{n // per + 1:03d}_{ec.fmt_time(chunk[0][0]).replace(':', 'm')}.jpg"
        sheet.save(path, quality=80)
        paths.append(path)
    return paths


def thumbs_at(media: Path, times: list[float], out_dir: Path, width: int = 480) -> dict[float, Path]:
    from PIL import Image

    out_dir.mkdir(parents=True, exist_ok=True)
    res = {}
    for t in times:
        p = out_dir / f"t_{t:09.2f}.jpg"
        if not p.exists():
            cp = ec.run([ec.ffmpeg_bin(), "-v", "error", "-ss", f"{max(0.0, t):.3f}", "-i", str(media),
                         "-frames:v", "1", "-vf", f"scale={width}:-2", "-f", "image2pipe", "-vcodec", "png", "-"],
                        check=False)
            if cp.returncode != 0 or not cp.stdout:
                continue
            im = label(Image.open(io.BytesIO(cp.stdout)).convert("RGB"), ec.fmt_time(t))
            im.save(p, quality=82)
        res[t] = p
    return res


def main() -> None:
    ec.setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", nargs="?")
    ap.add_argument("--media")
    ap.add_argument("--every", type=float)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--rows", type=int, default=4)
    ap.add_argument("--at", help="comma-separated seconds")
    ap.add_argument("--thumbs", action="store_true")
    args = ap.parse_args()
    proj = ec.resolve_project(args.project)
    media = Path(args.media) if args.media else proj / "review.mp4"
    if not media.exists():
        ec.die(f"Missing {media}")
    if args.at:
        times = [ec.parse_time(x) for x in args.at.split(",") if x.strip()]
        res = thumbs_at(media, times, proj / "out" / "thumbs")
        for t, p in res.items():
            print(f"{ec.fmt_time(t)}  {p}")
        return
    dur = ec.media_info(media)["duration"]
    end = min(args.end or dur, dur)
    span = max(0.1, end - args.start)
    every = args.every or max(2.0, round(span / 240, 1))
    prefix = "sheet" if args.start == 0 and args.end is None else f"zoom_{int(args.start)}s"
    with tempfile.TemporaryDirectory() as tmp:
        frames = extract_range(media, args.start, end, every, Path(tmp))
        paths = build_sheets(frames, proj / "analysis" / "sheets", args.cols, args.rows, prefix)
    print(f"{len(frames)} frames every {every:g}s -> {len(paths)} sheet(s). Look at each one:")
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
