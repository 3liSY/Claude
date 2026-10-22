# The Resolve bridge

## Contents
1. How it works
2. What it can do on Resolve 21.0.4 Free, and what it can't
3. Commands
4. Safety: backups, undo, what it never touches
5. If the self-test fails / troubleshooting
6. Optional community tools (davinci-resolve-mcp etc.)
7. Facts about the Resolve scripting API this relies on

## 1. How it works

- Resolve Free does not allow outside programs to control it ("external scripting" is Studio-only). It *does* run Python scripts started from its own menu. That works through 21.0.x; it was removed from Free in 21.1.
- **Editor Bridge** is such a script. He starts it once per Resolve session (Workspace > Scripts > Editor Bridge). It then watches a mailbox folder (`EDITOR_HOME\bridge\inbox`) and does each job it finds.
- It writes the answer to `outbox`, plus a heartbeat in `status.json`. Resolve's UI stays usable while it runs; menu scripts run in their own process.
- **It only knows fixed actions:** `ping`, `read_timeline`, `render_review`, `apply` (sub-ops `backup`, `place`, `place_segment`, `marker`), `remove`, `selftest`, `stop`.
- **It never runs code sent to it**, never uses the network, and never deletes anything it didn't place (it removes clips by its own unique ids, and markers by its `editor:` tag).
- `bridge_send.py` is the PC side. It writes a job, waits, and prints a plain summary.
- Logs: `EDITOR_HOME\bridge\bridge.log`.

## 2. What it can do on 21.0.4 Free, and what it can't

**Automatic:**
- Read every track, clip, transform and marker.
- Render a review MP4.
- Add named tracks.
- Import media into an `EDITOR` bin.
- Place clips and stills and sounds at exact frames on chosen tracks.
- Set zoom, position and crop on placed clips.
- Add a Fusion keyframed push-in on placed clips (if the self-test confirms Fusion works).
- Add markers with color, name, note, duration and a hidden id.
- Delete only its own clips and markers.
- Duplicate the timeline as a backup.

**Not possible through the 21.0.4 API, so these become by-hand items (red markers):**
- Transitions. The transition API arrived in 21.1, which Free can't script.
- Clip volume and fades. The audio properties API is also 21.1. So SFX are pre-leveled copies, and a `gain_db` that sounds wrong means re-applying with a new gain.
- Keyframes on the Edit page itself. The workaround is Fusion inside the placed clip.
- Typed titles with Arabic. Resolve breaks Arabic, so the workaround is PNG cards.
- Speed changes on his clips. Zooming a sped-up clip is refused.
- Splitting or moving his clips: by design, the bridge never does it.

## 3. Commands (PC side)

```powershell
python "${CLAUDE_SKILL_DIR}/scripts/bridge_send.py" status|ping|selftest|stop
python "${CLAUDE_SKILL_DIR}/scripts/bridge_send.py" prepare <slug> [--no-render]
python "${CLAUDE_SKILL_DIR}/scripts/bridge_send.py" apply <project> [--replace] [--no-backup] [--force]
python "${CLAUDE_SKILL_DIR}/scripts/bridge_send.py" snapshot <project> --label after
python "${CLAUDE_SKILL_DIR}/scripts/bridge_send.py" remove <project>
```

- `apply` validates the plan strictly, refuses if the wrong timeline is open (`--force` overrides), and re-reads the timeline first, so the positions match his cut *right now*.
- It writes `bridge\applied_vN.json` with every op and the unique id of every placed clip. `learn.py` and `remove` depend on that file, so never delete it.

## 4. Safety

- **First apply:** a duplicate timeline named `<name> (before editor vN)` is created first, so his untouched cut always exists.
- **Undo everything:** `bridge_send.py remove <project>`. It deletes only the clips with the recorded ids and only the `editor:vN:` markers, then removes `ED` tracks that are left empty. If he added his own clip on an `ED` track, that track stays.
- **Re-apply a new version:** `apply --replace` removes the old version first.
- **If he moved or trimmed his own clips after `prepare`:** apply uses the fresh read, so zoom copies still match. But `at` times in the plan are on the old clock. If his cut changed a lot, re-run `prepare` and re-time the plan.

## 5. If the self-test fails / troubleshooting

| Check says NO | Meaning | What to do |
|---|---|---|
| clips land where asked | recordFrame works differently on this build | Calibration auto-switches to relative frames; re-run the self-test to confirm |
| clip length exact | endFrame is exclusive on this build | Calibration handles it automatically |
| zoom/position settable | SetProperty is blocked | Zooms become by-hand markers; tell him |
| smooth (Fusion) zoom | Fusion scripting failed | Use `mode: "hard"` only |
| pictures (text cards) | stills too short or refused | Keep pop-ups under 5 s; if still NO, by hand |
| sounds on new audio track | audio append failed | SFX by hand from markers |
| markers / hidden id | old build | Removing markers will need doing by hand |
| export still frame | normal on Free | Freeze frames use ffmpeg on the source file instead (default) |

**Common problems:**
- **"Bridge isn't running"**
  1. Resolve must be open with a project and timeline.
  2. Run the menu item again.
  3. Check `bridge.log`.
  4. If the Scripts menu has no "Editor Bridge": restart Resolve, then use the Console fallback in `setup.md` §4.
- **"Resolve refused to place the clip"**
  - the file is missing or offline
  - the track is locked
  - the media type is unsupported (some phone HEVC files need a converted copy)
- **A zoom shows the wrong moment of his clip:** his source media has its own start timecode. Tell him, test on one clip, and if confirmed, re-time by hand. Report it so the skill can be fixed (use `left_offset` instead of `src_start`).
- **Fusion zoom zooms the wrong way vertically:** Fusion's y-axis goes up. Check `center`, and if needed flip it (`1 - y`) in a fix.
- **A Resolve dialog is open** (save, relink…): the bridge waits on Resolve. He closes the dialog, then retry.

## 6. Optional community tools

These are only for things the bridge can't do. They are third-party code, so treat each one as an install: **OK? first**.

- **samuelgursky/davinci-resolve-mcp**
  - About 3.7k stars; 37 compound or 390 granular MCP tools.
  - Has a Free in-app bridge (Workspace > Scripts > resolve_bridge), tested on Free 21.0.3.
  - Needs Python 3.10+ and Node for the advanced server.
  - Useful for: splitting clips, more Fusion work, more media analysis.
- **flamexnreal/davinci-resolve-ai-bridge-mcp**
  - About 37 stars; Free and Studio.
  - Has `split_clip`, `apply_silence_cuts`, `animate_zoom`.
  - Live-tested only on macOS, so Windows is unverified.
- **AutoSubs** (about 4.4k stars): Resolve subtitles with local Whisper, with a Windows installer. An option if he ever wants Resolve-native subtitles, though Arabic rendering in Resolve stays risky.

Don't run two bridges at once against the same project.

## 7. Facts this relies on (Resolve 21.0.2 scripting README, mirrored)

- `MediaPool.AppendToTimeline([{mediaPoolItem, startFrame, endFrame, mediaType (1 video / 2 audio), trackIndex, recordFrame}])`.
  - `recordFrame` is treated as absolute (timeline start included).
  - `endFrame` is treated as inclusive.
  - Both are verified by the self-test.
- `Timeline.AddMarker(frameId, color, name, note, duration, customData)`. `frameId` is relative to the timeline start.
- `TimelineItem.SetProperty` keys: ZoomX/ZoomY (0–100), Pan/Tilt (±4×width/height), Crop*, Opacity, RotationAngle, FlipX/Y.
- `Timeline.AddTrack`, `SetTrackName`, `GetItemListInTrack`, `DeleteClips(items, ripple=False)`, `DeleteTrack`, `DuplicateTimeline`, `GetUniqueId`.
- `TimelineItem.AddFusionComp()` → Fusion comp with MediaIn1/MediaOut1. The bridge inserts a Transform and keyframes `Size` with a BezierSpline, using the comp's own render range.
- Render: `SetCurrentRenderFormatAndCodec`, `SetRenderSettings({SelectAllFrames, TargetDir, CustomName, FormatWidth, FormatHeight})`, `AddRenderJob`, `StartRendering`. The review render changes his Deliver page settings, which is harmless; he picks his own preset when he exports.
- **Studio or 21.1 notes:**
  - On Studio, the same bridge works.
  - 21.1 Studio adds `AddTransition`, `SetFades` and `SetProperties` (including volume), plus Blackmagic's built-in MCP (File > Setup AI Assistants).
  - If he ever moves to Studio 21.1+, transitions and volume can become automatic: extend the bridge then.
