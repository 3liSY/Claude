"""Shared helpers for the /editor skill scripts.

Everything here is plain Python 3.9+ standard library (numpy only where a
script imports it itself). All files are read and written as UTF-8 so Arabic
text and Arabic file names survive on Windows.
"""
from __future__ import annotations

import datetime as _dt
import json
import math
import os
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
BRIDGE_VERSION = "1.0.0"  # must match BRIDGE_VERSION in resolve/Editor Bridge.py

# ---------------------------------------------------------------- paths


def editor_home() -> Path:
    """Root data folder. Override with the EDITOR_HOME environment variable."""
    env = os.environ.get("EDITOR_HOME")
    if env:
        return Path(env).expanduser()
    return Path.home() / "SyrianRubikStudio" / "editor"


def brain_dir() -> Path:
    return editor_home() / "brain"


def library_dir() -> Path:
    return editor_home() / "library"


def projects_dir() -> Path:
    return editor_home() / "projects"


def bridge_dir() -> Path:
    return editor_home() / "bridge"


def project_dir(slug: str, create: bool = True) -> Path:
    p = projects_dir() / slug
    if create:
        for sub in ("analysis", "analysis/sheets", "plan", "out", "out/text", "out/thumbs", "bridge"):
            (p / sub).mkdir(parents=True, exist_ok=True)
    return p


def resolve_project(arg: str | None) -> Path:
    """Accept a slug, a path, or nothing (newest project)."""
    if arg:
        p = Path(arg)
        if p.exists():
            return p.resolve()
        p = projects_dir() / arg
        if p.exists():
            return p
        die(f"Project not found: {arg}")
    pd = projects_dir()
    if not pd.exists():
        die("No projects yet. Start one with: bridge_send.py prepare <slug>")
    items = sorted((d for d in pd.iterdir() if d.is_dir()), key=lambda d: d.stat().st_mtime)
    if not items:
        die("No projects yet.")
    return items[-1]


# ---------------------------------------------------------------- config

DEFAULT_CONFIG = {
    "library": {
        "broll_folders": [],   # filled on first run: his own clip folders
        "sfx_folders": [],     # his own SFX folders
    },
    "ffmpeg": "ffmpeg",
    "ffprobe": "ffprobe",
    "whisper": {"model": "large-v3", "device": "cuda", "compute_type": "float16", "language": "ar"},
    "review_render": {"width": 1280, "height": 720},
    "bridge": {"timeout_s": 600},
    "browser": "",  # optional path to msedge/chrome for text cards
}


def config_path() -> Path:
    return editor_home() / "config.json"


def load_config() -> dict:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    p = config_path()
    if p.exists():
        user = read_json(p)
        _deep_update(cfg, user)
    return cfg


def save_config(cfg: dict) -> None:
    write_json(config_path(), cfg)


def _deep_update(base: dict, new: dict) -> None:
    for k, v in new.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_update(base[k], v)
        else:
            base[k] = v


def load_keys() -> dict:
    """API keys live in editor_home/keys.json. Never print them."""
    p = editor_home() / "keys.json"
    return read_json(p) if p.exists() else {}


# ---------------------------------------------------------------- io


def read_json(path) -> dict | list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data, indent: int = 2) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
        f.write("\n")
    os.replace(tmp, path)
    return path


def write_text(path, text: str, newline: str = "\n") -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline=newline) as f:
        f.write(text)
    return path


def append_text(path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(text)


def die(msg: str, code: int = 1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def setup_stdout() -> None:
    """Make print() safe for Arabic on Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def today() -> str:
    return _dt.date.today().isoformat()


def now_iso() -> str:
    return _dt.datetime.now().replace(microsecond=0).isoformat()


def slugify(text: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return s or "video"


# ---------------------------------------------------------------- processes


def run(cmd: list, check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a command given as a list (never a shell string)."""
    cmd = [str(c) for c in cmd]
    try:
        cp = subprocess.run(cmd, capture_output=capture, check=False)
    except FileNotFoundError:
        die(f"Program not found: {cmd[0]}. Is it installed and on PATH?")
    if check and cp.returncode != 0:
        err = (cp.stderr or b"").decode("utf-8", "replace")[-2000:]
        die(f"Command failed ({cp.returncode}): {' '.join(cmd[:6])} ...\n{err}")
    return cp


def ffmpeg_bin() -> str:
    return load_config().get("ffmpeg") or "ffmpeg"


def ffprobe_bin() -> str:
    return load_config().get("ffprobe") or "ffprobe"


def ffprobe(path) -> dict:
    cp = run([ffprobe_bin(), "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    return json.loads(cp.stdout.decode("utf-8", "replace"))


def media_info(path) -> dict:
    """Small, normalized summary of a media file."""
    data = ffprobe(path)
    fmt = data.get("format", {})
    info = {
        "path": str(Path(path).resolve()),
        "duration": float(fmt.get("duration") or 0.0),
        "has_video": False,
        "has_audio": False,
    }
    for st in data.get("streams", []):
        if st.get("codec_type") == "video" and not info["has_video"]:
            if st.get("disposition", {}).get("attached_pic"):
                continue
            info["has_video"] = True
            info["width"] = int(st.get("width") or 0)
            info["height"] = int(st.get("height") or 0)
            r = parse_fps(st.get("r_frame_rate", "0/1"))
            a = parse_fps(st.get("avg_frame_rate", "0/1"))
            info["fps"] = round(float(r), 3) if r else 0.0
            info["fps_avg"] = round(float(a), 3) if a else 0.0
            # Variable frame rate (phones, OBS) drifts against timecode.
            info["vfr"] = bool(r and a and abs(float(r) - float(a)) > 0.05)
            if not info["duration"] and st.get("duration"):
                info["duration"] = float(st["duration"])
            info["codec"] = st.get("codec_name")
        elif st.get("codec_type") == "audio" and not info["has_audio"]:
            info["has_audio"] = True
            info["sample_rate"] = int(st.get("sample_rate") or 0)
            info["channels"] = int(st.get("channels") or 0)
    if not info["has_video"] and Path(path).suffix.lower() in IMAGE_EXT:
        info["still"] = True
    return info


VIDEO_EXT = {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".webm", ".mxf", ".mts", ".m2ts", ".wmv"}
AUDIO_EXT = {".wav", ".mp3", ".aif", ".aiff", ".flac", ".ogg", ".m4a", ".aac", ".opus"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


def decode_audio_mono(path, sr: int = 16000):
    """Decode any media file to a mono float32 numpy array via ffmpeg."""
    import numpy as np  # local import: only scripts that need audio pay for numpy

    cp = run([ffmpeg_bin(), "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"])
    return np.frombuffer(cp.stdout, dtype=np.float32), sr


# ---------------------------------------------------------------- time math


def num(value, default: float = 0.0) -> float:
    """First number in a value: '59.94' / '29.97 DF' / 60 -> float."""
    m = re.search(r"-?\d+(?:\.\d+)?", str(value if value is not None else ""))
    return float(m.group(0)) if m else default


def parse_fps(value) -> Fraction:
    """'60000/1001' -> Fraction, '59.94' -> 60000/1001, 60 -> 60."""
    if isinstance(value, Fraction):
        return value
    if isinstance(value, (int,)):
        return Fraction(value)
    s = str(value).strip()
    if "/" not in s:
        s = str(num(s))
    if "/" in s:
        n, d = s.split("/", 1)
        d = int(d) if d.strip() else 1
        return Fraction(int(n), d) if d else Fraction(0)
    f = float(s)
    for nominal in (24, 30, 48, 60, 120):
        if abs(f - nominal * 1000 / 1001) < 0.01:
            return Fraction(nominal * 1000, 1001)
    return Fraction(f).limit_denominator(1001)


def nominal_fps(fps) -> int:
    return int(round(float(parse_fps(fps))))


def sec_to_frames(sec: float, fps) -> int:
    """Seconds since timeline start -> frame count, at the TRUE frame rate."""
    return int(round(float(sec) * float(parse_fps(fps))))


def frames_to_sec(frames: int, fps) -> float:
    return float(frames) / float(parse_fps(fps))


def frames_to_tc(frames: int, fps, drop_frame: bool = False) -> str:
    """Frame count -> SMPTE timecode string. Drop-frame only for 29.97/59.94."""
    nom = nominal_fps(fps)
    if drop_frame and nom in (30, 60):
        drop = 2 if nom == 30 else 4
        per_10min = nom * 600 - drop * 9
        per_min = nom * 60 - drop
        d, m = divmod(frames, per_10min)
        if m > drop:
            frames = frames + drop * 9 * d + drop * ((m - drop) // per_min)
        else:
            frames = frames + drop * 9 * d
        sep = ";"
    else:
        sep = ":"
    ff = frames % nom
    s = (frames // nom) % 60
    mnt = (frames // (nom * 60)) % 60
    h = frames // (nom * 3600)
    return f"{h:02d}:{mnt:02d}:{s:02d}{sep}{ff:02d}"


def tc_to_frames(tc: str, fps, drop_frame: bool | None = None) -> int:
    nom = nominal_fps(fps)
    parts = re.split(r"[:;.]", tc.strip())
    if len(parts) != 4:
        raise ValueError(f"Bad timecode: {tc}")
    h, m, s, f = (int(x) for x in parts)
    if drop_frame is None:
        drop_frame = ";" in tc
    total = ((h * 3600 + m * 60 + s) * nom) + f
    if drop_frame and nom in (30, 60):
        drop = 2 if nom == 30 else 4
        total_min = h * 60 + m
        total -= drop * (total_min - total_min // 10)
    return total


def fmt_time(sec: float) -> str:
    """Human time for the sheet and chat: 1:23.4 or 1:02:03.4"""
    if sec is None or (isinstance(sec, float) and math.isnan(sec)):
        return "?"
    sign = "-" if sec < 0 else ""
    sec = abs(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h >= 1:
        return f"{sign}{int(h)}:{int(m):02d}:{s:04.1f}"
    return f"{sign}{int(m)}:{s:04.1f}"


def parse_time(text) -> float:
    """'83.4', '1:23.4', '1:02:03.4' -> seconds."""
    if isinstance(text, (int, float)):
        return float(text)
    parts = str(text).strip().split(":")
    total = 0.0
    for p in parts:
        total = total * 60 + float(p)
    return total


# ---------------------------------------------------------------- markers

MARKER_COLORS = [
    "Blue", "Cyan", "Green", "Yellow", "Red", "Pink", "Purple", "Fuchsia",
    "Rose", "Lavender", "Sky", "Mint", "Lemon", "Sand", "Cocoa", "Cream",
]

# Default legend; edit-preferences.md may override it.
TYPE_COLOR = {
    "broll": "Blue",
    "zoom": "Yellow",
    "sfx": "Green",
    "transition": "Purple",
    "popup": "Cyan",
    "caption": "Cyan",
    "freeze": "Pink",
    "fix": "Red",
    "cut": "Red",
    "note": "Cream",
    "chapter": "Sand",
}


def ascii_marker_name(item: dict) -> str:
    """Short ASCII name: Resolve marker names may mangle Arabic."""
    label = item.get("label") or item.get("type", "")
    label = re.sub(r"[^A-Za-z0-9 .,%+\-_'()]", "", str(label)).strip()
    name = f"{item['id']} {label}".strip()
    return name.replace("|", "/")[:60]
