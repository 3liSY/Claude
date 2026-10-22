"""First-time setup and health check for the /editor skill (Windows 11).

  python setup_check.py                  # check everything, say what's missing (changes nothing)
  python setup_check.py --init           # create the studio folders + memory files (safe, local)
  python setup_check.py --install-bridge # copy the bridge into Resolve's Scripts folder (ask him first)

Installing Python packages is never done here: the skill shows him the exact
command and runs it only after his OK.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import edcommon as ec

PREFS_TEMPLATE = """# Edit preferences (the /editor skill reads this before every plan)

Newest rule wins. Every learned line is dated. Mark replaced lines with ~~strikethrough~~ (superseded YYYY-MM-DD).

## What he told us (2026-10-22)
- Resolve **Free 21.0.4**: do NOT update to 21.1 (Free 21.1 removed Python scripting; the bridge needs it).
- Timeline: 60 fps. The skill edits his finished cut (a Resolve timeline): it only ADDS layers on new tracks, never moves his cut.
- Videos: Syrian Rubik long-form and SRB Gamer long-form. No Shorts for now.
- Footage: hands + cubes (phone/camera), gameplay/screen (OBS). Animations rarely. Never his face.
- **No background music, ever.** Short dings/stings/SFX are fine.
- Pacing, zoom style, transitions, captions, text pop-ups: **decide per video** (propose options each time).
- Humor edits: only where they make the video funnier and never repetitive.
- B-roll sources: his own clips, free safe stock (Pexels, Pixabay, Coverr, Mixkit), YouTube videos with YouTube's own Creative Commons label.
- SFX sources: free safe libraries (YouTube Audio Library, Freesound CC0/CC BY, Mixkit, Pixabay, Kenney) + SFX he already has.
- Always show the plan sheet before placing anything. Place it for him, he reviews.
- Learn automatically from what he changes, then tell him in a short list what was learned.
- After he uploads: remind him to share the retention graph.
- API keys: later. Installs: Full is approved in principle, but still ask before each one.

## Starting defaults (rules of thumb from research, NOT measured on his channel; replace as we learn)
| | Syrian Rubik (cubing) | SRB Gamer |
|---|---|---|
| Hook (0-30 s) | strongest visual at 0:00, promise by ~0:07, 2-3 quick payoff teases | gameplay climax first |
| Visual change | every 3-6 s; up to 8-10 s while hands do an algorithm (add a notation label) | every 2-4 s; cut menus/loading |
| B-roll | 1.5-3 s illustrative, 3-5 s to read; never > 6 s static; start 2-4 frames before the word | same + meme-style inserts (licensed/own only) |
| Zoom | 110-115% to hide jump cuts, 120-130% for emphasis, max ~1 per 10-15 s; comic snap 150-250% max ~1 per 45-90 s; back within 1-4 s | same + freeze + zoom + caption on fails/wins |
| Transitions | hard cuts ~90-95%; whip/zoom + whoosh only at chapter changes | dip/flash for "3 hours later" |
| SFX | peak on the event frame (0-1 frame early); 3-10 dB under voice; no whoosh on every cut | gag stings within the zoom budget |
| Captions | 1-2 lines, <= 42 chars, 0.83-7 s, <= 15-17 chars/s | same |
| Re-hooks | ~3:00 and ~6:00, then every 2-3 min; 1-2 open loops | same |

## Learned rules
(none yet)

## Never
- Never move, trim or delete his own clips. Only add on "ED ..." tracks.
- Never NC/ND licensed material, never copyrighted music/memes/clips without a license or written permission.
"""

SETUP_TEMPLATE = """# Setup facts (the /editor skill keeps this current)

- Resolve: Free 21.0.4 (Help > About). Do not update past 21.0.x.
- Timeline fps: 60
- Bridge installed: not yet
- Self-test: not run yet
- Python packages approved: (fill in after each OK)
- API keys: none yet (search uses browse links)
- B-roll folders: (ask him)
- SFX folders: (ask him)
"""

LOG_TEMPLATE = """# Edit log (one entry per video)

<!-- date | project | plan version | what was placed | what he changed | learned | uploaded? | retention shared? -->
"""


def ok(flag: bool, text: str, fix: str = "") -> bool:
    print(f"  [{'OK' if flag else '!!'}] {text}" + (f"\n        -> {fix}" if (fix and not flag) else ""))
    return flag


def has(mod: str) -> bool:
    return importlib.util.find_spec(mod) is not None


def resolve_scripts_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "Blackmagic Design" / "DaVinci Resolve" / "Support" / "Fusion" / "Scripts" / "Utility"
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"
    return Path.home() / ".local/share/DaVinciResolve/Fusion/Scripts/Utility"


def bridge_source() -> Path:
    return ec.SKILL_DIR / "resolve" / "Editor Bridge.py"


def installed_bridge_version(p: Path) -> str | None:
    if not p.exists():
        return None
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("BRIDGE_VERSION"):
            return line.split("=", 1)[1].strip().strip('"')
    return "?"


def cmd_check() -> None:
    from text_cards import find_browser

    print("Python and packages")
    ok(sys.version_info >= (3, 10), f"Python {sys.version.split()[0]}", "Python 3.10-3.12 64-bit recommended")
    ok(has("numpy"), "numpy", "pip install numpy")
    ok(has("PIL"), "Pillow (pictures)", "pip install pillow")
    ok(has("faster_whisper"), "faster-whisper (transcription)", "pip install faster-whisper")
    print("  optional:", ", ".join(f"{m}={'yes' if has(m) else 'no'}" for m in ("torch", "open_clip", "playwright")))
    print("Tools")
    ok(bool(shutil.which(ec.ffmpeg_bin())), "ffmpeg", "install ffmpeg and add it to PATH (or set 'ffmpeg' in config.json)")
    ok(bool(shutil.which(ec.ffprobe_bin())), "ffprobe")
    smi = shutil.which("nvidia-smi")
    gpu = ""
    if smi:
        try:
            gpu = subprocess.run([smi, "--query-gpu=name,memory.total", "--format=csv,noheader"],
                                 capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            pass
    ok(bool(gpu), f"NVIDIA GPU {gpu}", "no GPU found: transcription will be slow (CPU)")
    ok(bool(find_browser()), f"browser for text cards ({find_browser() or 'none'})", "Edge normally ships with Windows")
    print("DaVinci Resolve")
    exe = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Blackmagic Design" / "DaVinci Resolve" / "Resolve.exe"
    if os.name == "nt":
        ok(exe.exists(), f"Resolve at {exe}")
    target = resolve_scripts_dir() / "Editor Bridge.py"
    v = installed_bridge_version(target)
    ok(v == ec.BRIDGE_VERSION, f"Editor Bridge in Resolve's Scripts menu (installed: {v or 'no'}, skill: {ec.BRIDGE_VERSION})",
       "python setup_check.py --install-bridge  (then restart Resolve)")
    calib = ec.bridge_dir() / "calibration.json"
    ok(calib.exists(), "self-test done on this PC", "with the bridge running: python bridge_send.py selftest")
    print("Studio folders")
    home = ec.editor_home()
    ok(home.exists(), f"EDITOR_HOME {home}", "python setup_check.py --init")
    cfg = ec.load_config()
    for key in ("broll_folders", "sfx_folders"):
        folders = cfg["library"][key]
        ok(bool(folders) and all(Path(f).exists() for f in folders), f"{key}: {folders or 'none set'}",
           f"python library.py add-folder {'broll' if key.startswith('broll') else 'sfx'} \"D:/path\"")
    keys = ec.load_keys()
    print(f"  API keys: {', '.join(sorted(keys)) or 'none (fine: search falls back to links)'}")


def cmd_init() -> None:
    home = ec.editor_home()
    for sub in ("brain", "library/stock/video", "library/stock/sfx", "library/index/thumbs", "library/cache/sfx",
                "projects", "bridge/inbox", "bridge/outbox"):
        (home / sub).mkdir(parents=True, exist_ok=True)
    seeds = {ec.brain_dir() / "edit-preferences.md": PREFS_TEMPLATE, ec.brain_dir() / "setup.md": SETUP_TEMPLATE,
             ec.brain_dir() / "edit-log.md": LOG_TEMPLATE}
    for p, text in seeds.items():
        if not p.exists():
            ec.write_text(p, text)
            print(f"created {p}")
    from transcribe import load_terms

    load_terms()  # seeds brain/terms.md
    if not ec.config_path().exists():
        ec.save_config(ec.load_config())
        print(f"created {ec.config_path()}")
    print(f"Studio folder ready: {home}")


def cmd_install_bridge() -> None:
    src = bridge_source()
    dst_dir = resolve_scripts_dir()
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / "Editor Bridge.py"
    shutil.copy2(src, dst)
    print(f"Installed: {dst}")
    print("Restart Resolve, open the project + timeline, then Workspace > Scripts > Editor Bridge.")


def main() -> None:
    ec.setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--install-bridge", action="store_true")
    args = ap.parse_args()
    if args.init:
        cmd_init()
    if args.install_bridge:
        cmd_install_bridge()
    if not (args.init or args.install_bridge):
        cmd_check()


if __name__ == "__main__":
    main()
