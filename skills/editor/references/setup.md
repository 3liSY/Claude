# First-time setup (Windows 11, his PC)

Do it in this order. Each **OK?** line means: ask him first, using AskUserQuestion, and wait.

## Contents
1. Folders and memory
2. Check what's there
3. Python packages
4. The bridge inside Resolve
5. The self-test
6. His library folders
7. Optional extras
8. Keeping Resolve on 21.0.x

## 1. Folders and memory (local, safe; no OK needed)

```powershell
python "${CLAUDE_SKILL_DIR}/scripts/setup_check.py" --init
```

This creates `%USERPROFILE%\SyrianRubikStudio\editor\` with:
- `brain\`: edit-preferences, setup, edit-log, terms
- `library\`
- `projects\`
- `bridge\`
- `config.json`

`edit-preferences.md` already contains what he said on 2026-10-22, so don't ask him those things again.

## 2. Check what's there

```powershell
python "${CLAUDE_SKILL_DIR}/scripts/setup_check.py"
```

It reports Python, packages, ffmpeg, the GPU, Edge (for text cards), the bridge, the self-test, his folders and API keys. It changes nothing.

## 3. Python packages

**OK?** Show him the exact command before running it.

| Package | Needed for | Size |
|---|---|---|
| numpy, pillow | everything | small |
| faster-whisper | transcription (video-maker probably installed it already) | ~100 MB + the large-v3 model ~3 GB on first use, downloaded from Hugging Face |

```powershell
python -m pip install numpy pillow faster-whisper
```

Notes:
- The first transcription downloads the Whisper model. That is a download, so it needs **OK?** too, unless video-maker already has the model cached.
- If faster-whisper can't find CUDA (cuBLAS/cuDNN errors), the script falls back to the CPU on its own. The fix is NVIDIA's CUDA 12 + cuDNN 9 runtime. That is a big install: **OK?** first.
- ffmpeg must be on PATH. If it isn't, ask whether to install it (**OK?**), or point `config.json` → `"ffmpeg"` at an existing ffmpeg.exe.

## 4. The bridge inside Resolve (OK? because it installs into Resolve)

```powershell
python "${CLAUDE_SKILL_DIR}/scripts/setup_check.py" --install-bridge
```

This copies `resolve/Editor Bridge.py` to:
`%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility\Editor Bridge.py`

Then he:
1. Restarts Resolve and opens any project and timeline.
2. Clicks **Workspace > Scripts > Editor Bridge**. It shows no window and keeps running quietly.
3. Leaves it running. It stops on its own after 6 hours with no jobs, or when Resolve closes.

Notes:
- Resolve 21.0 runs Python scripts with **his installed Python** (3.10–3.12 64-bit is safest). If Workspace > Scripts doesn't list "Editor Bridge" after a restart, check that Python is installed "for all users" and on PATH.
- **Fallback start:** Workspace > Console, choose the **Py3** tab, and paste:
  `exec(open(r"%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility\Editor Bridge.py", encoding="utf-8").read())`
  (with the real path).
- If the `%APPDATA%` folder doesn't work, the all-users folder `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility\` works too.
- Check it with `python "${CLAUDE_SKILL_DIR}/scripts/bridge_send.py" ping`.

## 5. The self-test (once, and again after any Resolve update)

```powershell
python "${CLAUDE_SKILL_DIR}/scripts/bridge_send.py" selftest
```

It builds a temporary timeline, places a test clip, picture, sound, zoom, Fusion zoom and marker, measures how his Resolve build behaves, and then deletes the test timeline. The results are saved to `bridge\calibration.json`, which the bridge uses from then on, and to `brain\selftest.json`. Write a one-line summary into `brain/setup.md`.

If a check says NO, see `resolve-bridge.md` → "If the self-test fails". The skill still works; that feature just becomes a by-hand marker.

## 6. His library folders

Ask him where his own clips and sounds are. They are often in `Desktop\obs\`, `Desktop\` or a cubes folder. Then:

```powershell
python "${CLAUDE_SKILL_DIR}/scripts/library.py" add-folder broll "D:/path/to/clips"
python "${CLAUDE_SKILL_DIR}/scripts/library.py" add-folder sfx "D:/path/to/sfx"
python "${CLAUDE_SKILL_DIR}/scripts/library.py" index
python "${CLAUDE_SKILL_DIR}/scripts/library.py" sheet
```

Then:
- Look at the clip sheets and write a short note for the clips that matter (`library.py note <id> "red cube slow-mo pop"`). Notes make search much better.
- Suggest he records a few **cube sounds** (turns, pops, timer start/stop). They are the most unique SFX he can have, with zero license risk.

## 7. Optional extras (each one OK? first)

- **AI clip search:** `python -m pip install torch --index-url https://download.pytorch.org/whl/cu121` then `python -m pip install open_clip_torch`. That's about 3 GB, and the model weights download on first use. After that, run `library.py embed`. Worth it once his library has 100+ clips.
- **Playwright** (faster text cards): `python -m pip install playwright`. It is not needed, because Edge works out of the box.
- **API keys** (he said "later"): see `sourcing.md` §3. Until then, `stock.py links` gives him browse links.
- **Community MCP tools:** see `resolve-bridge.md` §6. These are third-party code, so treat them as an install.

## 8. Keeping Resolve on 21.0.x

- Free 21.1 removed Python scripting, and the bridge is Python. **He must not update past 21.0.x** unless he buys Studio. If Studio ever happens, the bridge also works there, and Studio 21.1 adds Blackmagic's own Claude connection.
- When Resolve offers an update, he declines it.
- If he updates by accident, the fallback is `plan.py edl` (a markers file he imports) plus the edit sheet.
- Keep the installer for his current version (DaVinci_Resolve_21.0.4_Windows.zip) somewhere safe, because Blackmagic's support page lists old versions too.
