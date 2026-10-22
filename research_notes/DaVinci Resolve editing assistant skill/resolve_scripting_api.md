# DaVinci Resolve Scripting API and AI/MCP Integrations (state as of 22 Oct 2026)

Method note: blackmagicdesign.com, forum.blackmagicdesign.com and most news sites (CineD, Newsshooter, Digital Production, Puget, YMCinema, xere.my) could NOT be opened directly from this environment (DNS blocked). Facts from them come from search-result summaries and are marked "(via search summary)". The official scripting docs were read in full from verbatim GitHub mirrors of the files Blackmagic ships in `Developer/Scripting/` (README.txt for 20.2 and 21.0.2; README.md + CHANGELOG.md + DaVinciResolveScript.pyi for 21.1.x). Those are the most reliable sources here.

## Q1. Current Resolve version and recent scripting API changes

### Takeaway
As of 22 Oct 2026 the current release is **DaVinci Resolve 21.1.1** (readme dated 1 Oct 2026). The two biggest recent changes are in **21.1 (early Sept 2026)**: **Python scripting moved to Studio only**, and Blackmagic added a **built-in MCP server for AI assistants (also Studio only)**. 21.1 also added a large set of API calls, including the first-ever **transition API (`TimelineItem.AddTransition`)**, fades, clip speed, `SetProperties`, and transcription readout. 21.1.1 added **async job-status APIs**.

### Cited Findings
**Version timeline**
- Resolve 20: announced at NAB in April 2025 ("100+ new features", AI IntelliScript, AI Animated Subtitles, AI Multicam SmartSwitch, AI Audio Assistant). Final release 27 May 2025. — [Newsshooter, Resolve 20 announced](https://www.newsshooter.com/2025/04/04/blackmagic-design-davinci-resolve-20-announced-with-100-new-features-including-ai-enhancements/); [Newsshooter, Resolve 20 final](https://www.newsshooter.com/2025/05/27/davinci-resolve-20-final-release/) (via search summary)
- Resolve 20.2.2 shipped Oct 2025. — [AlternativeTo](https://alternativeto.net/news/2025/10/davinci-resolve-20-2-2-improves-color-management-and-audio-playback)
- Resolve 21: announced 13 Apr 2026 with a new Photo page and AI tools (AI IntelliSearch, CineFocus, Speech Generator, face retouch). Final release in early June 2026 (sources say 2 or 3 June). — [Newsshooter, 21 announced](https://www.newsshooter.com/2026/04/13/blackmagic-design-announces-davinci-resolve-21-major-update-adds-new-photo-page/); [Newsshooter, 21 final](https://www.newsshooter.com/2026/06/02/davinci-resolve-21-final-release/); [Digital Production, "21 leaves beta"](https://digitalproduction.com/2026/06/05/davinci-resolve-21-leaves-beta/) (via search summary)
- Point releases: 21.0.1 on 24 June 2026, 21.0.2 on 1 July 2026, 21.0.4 around 5 Aug 2026, 21.1 around 7–8 Sept 2026, 21.1.1 around 1–6 Oct 2026. — [Newsshooter 21.0.4](https://www.newsshooter.com/2026/08/05/davinci-resolve-21-0-4-update/); [Newsshooter 21.1](https://www.newsshooter.com/2026/09/07/blackmagic-design-davinci-resolve-21-1/); [Digital Production 21.1.1](https://digitalproduction.com/2026/10/06/davinci-resolve-21-1-1/) (via search summary)
- The 21.1.1 readme is dated 1 Oct 2026. It warns that projects opened in 21.1.1 can no longer be opened in 20.3.2, and it recommends backing up the project library first. — [Blackmagic "About DaVinci Resolve 21" readme](https://www.blackmagicdesign.com/support/content/readme/dfbb6e4233c144d1b328c109c7ebc11e) (via search summary)
- No 21.1.2 or 21.2 beta turned up in search as of 22 Oct 2026. — (search for "21.1.2 / 21.2 beta" returned nothing; see Gaps)

**Official API changelog (CHANGELOG.md shipped in Developer/Scripting, "Last Updated: 1 Sep 2026")** — [CHANGELOG.md mirror](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/CHANGELOG.md)
- **21.1 notes:** "Python 2 is no longer supported." "Built-in Python support for script menu and console scripts." "Overloaded function signatures are deprecated."
- **21.1 added:**
  - Keyboard presets.
  - Project Settings presets.
  - Render presets: `Project.UpdateRenderPreset`, `SetQuickExportEnabledForRenderPreset`.
  - Audio render formats and codecs: `GetAudioRenderCodecs`, `GetAudioRenderFormats`.
  - **`MediaPoolItem.GetTranscription`**.
  - Multicam: `MediaPool.CreateMulticamClip`, `TimelineItem.FlattenMulticam`, `PerformMulticamSmartSwitch`, `Timeline.AutoAlignClips`.
  - TimelineItem get/set of **native audio properties and enabled states**.
  - TimelineItem **Get/Set Fades, Speed**, OutputBlanking and `GetType`.
  - **"Transition API - TimelineItem.AddTransition."**
  - `Timeline.Get/SetOutputBlanking`.
  - **`Timeline.GetNormalizeAudioModes`, `NormalizeAudioLevel`**.
  - `MediaPoolItem.SetAudioMapping`, `TimelineItem.SetSourceAudioChannelMapping`.
  - Media Storage clone.
  - `ValidateDCTL` / `EncryptDCTL`.
  - Utility getters `resolve.GetCurrentProject` / `GetCurrentTimeline` / `GetMediaPool` / `GetGallery`.
- **21.0.4 added:** `Timeline.GetSelectedClips`, plus `SetRenderSettings` options for handles, full extents and data burn.
- **21.0 added:**
  - Optional `useSpeakerDetection` argument for `TranscribeAudio`.
  - `PerformAudioClassification` / `ClearAudioClassification`.
  - `RemoveMotionBlur`.
  - `AnalyzeForIntellisearch(identifyFaces, isBetterMode)`.
  - `AnalyzeForSlate(markerColor)` and a new Marker colour enum.
  - `Resolve.DisableBackgroundTasksForCurrentResolveSession`.
  - `Project.GenerateSpeech({speechGenerationSettings}, timecode)`.
- **20.x:**
  - 20.0: `LinkFullResolutionMedia`, `ReplaceClipPreserveSubClip`, `MonitorGrowingFile`.
  - 20.1: Timeline and TimelineItem `Get/SetVoiceIsolationState`.
  - 20.2: `SetName` on TimelineItem and MediaPoolItem, the `ExportSubtitle`/`SubtitleFormat` render settings, and `ResetAllNodeColors`.
  - 20.2.2: `CreateProject` takes a `mediaLocationPath`, plus `GetFairlightPresets` and `ApplyFairlightPresetToCurrentTimeline`.
  - 20.3.2: fix for `AppendToTimeline` failing when no media pool clip is selected.
- **21.1.1 (async APIs):** "asynchronous APIs for Quick Export, transcription, scene cut detection, Smart Reframe and subtitle creation", and `ApplyGradeFromDRX` gains an option to apply to all node layers. — [Digital Production 21.1.1](https://digitalproduction.com/2026/10/06/davinci-resolve-21-1-1/); [WindowsForum 21.1.1](https://windowsforum.com/news/davinci-resolve-21-1-1-adds-windows-11-usac-audio-trim-preview-and-async-apis.449011/) (via search summary). The shipped `.pyi` contains the matching status pollers on `Project`:
  - `GetTranscribeAudioStatus()`, `GetSmartReframeStatus()`, `GetDetectSceneCutsStatus()`, `GetCreateSubtitlesFromAudioStatus()`, `GetAnalyzeForSlateStatus()`.
  - `RenderWithQuickExport(quickExportPresetName, presetInfo)` and `GetRenderWithQuickExportStatus()`.
  - Each returns a dict with `JobStatus` ('Inactive', 'Initializing', 'Analyzing', 'Cancelling', 'Cancelled', 'Complete'), `CompletionPercentage`, `EstimatedTimeRemaining` and `Error`.
  - — [DaVinciResolveScript.pyi mirror](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/DaVinciResolveScript.pyi)
- **Doc format change in 21.1:**
  - README.txt became README.md. The full API listing moved into a typed stub, `DaVinciResolveScript.pyi` ("Please refer to the included DaVinciResolveScript.pyi Python API definition").
  - The README was last updated 31 Aug 2026.
  - — [21.1.x README.md mirror](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/README.md)
- **Deprecations in 21.1:**
  - `TimelineItem.SetProperty(key, value)` / `GetProperty` → use **`SetProperties({...})` / `GetProperties()`**. All keys are validated first, and either all are applied or none.
  - `GetSetting`/`SetSetting` → `GetSettings()`/`SetSettings({...})`.
  - Bare-list `AppendToTimeline(clip1, clip2)` / `ImportMedia([paths])` → dict forms `AppendToTimeline([AppendClipInfo])` / `ImportMedia([{"FilePath":...}])`.
  - Deprecated, not removed.
  - — [21.1.x README.md mirror](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/README.md)
- Earlier README versions: 20.2 README "Last Updated: 18 Aug 2025"; 21.0.2 README "Last Updated: 26 May 2026" (same text format as 20.2). — [20.2 README mirror](https://github.com/thomjiji/dri/blob/main/READMEs/20.2_README.txt); [21.0.2 README mirror](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_0_2/README.txt)

### Inferences
- The skill should target **Resolve 21.1.x Studio** as the primary scripting path and assume the old `SetProperty` form still works but is deprecated. Code should feature-detect with `resolve.GetVersion()` and the new `resolve.IsStudio()` (present in the 21.1 `.pyi`).
- The CHANGELOG mirror (1 Sep 2026) has no "21.1.1" section, even though the `.pyi` in the same folder has the async status calls. The status calls may have been documented only in the `.pyi`, or the mirror may mix files. Treat the exact 21.1.1 async signatures as "verify on install". The authoritative local copy is `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\` on the user's PC.

### Gaps
- Could not open Blackmagic's own release notes pages or forum release threads directly, so the exact 21.1 and 21.1.1 release-note wording is from secondary summaries.
- No confirmation of any build newer than 21.1.1 as of 22 Oct 2026.

## Q2. Free vs Studio: who can run scripts, from where (and the built-in MCP)

### Takeaway
The rules depend on the version:
- **≤21.0.x Free:** Python and Lua run only *inside* Resolve (Console, Workspace > Scripts). External or terminal scripting needs Studio.
- **21.1+ Free:** **Python is removed entirely**. `.py` files no longer appear in Workspace > Scripts. Only **sandboxed Lua** run from Workspace > Scripts (and the Console Lua tab) remains, with no sockets and no file I/O.
- **External scripting** (terminal, IDE, MCP server attaching directly) and **Blackmagic's built-in MCP server** are **Studio only**.

If the user has Free 21.1, the only live-control routes are community Lua "mailbox" bridges. A file-based route is to generate FCPXML or DRT and import it.

### Cited Findings
- **Pre-21.1 rule (Blackmagic forum, ~late 2025):** "the free version of DaVinci Resolve does support scripting, but only internally via the built-in console"; running scripts from the OS terminal, an IDE or the Scripts menu requires Studio. — [Blackmagic Forum, "How do I actually run Python scripts?"](https://forum.blackmagicdesign.com/viewtopic.php?f=12&t=230652) (via search summary). Note: other community projects (hiteshK03, samuelgursky's free bridge) did run Python from Workspace > Scripts on Free ≤21.0, so the "Scripts menu requires Studio" part is contested.
- **21.1 change:**
  - "Advanced scripting now requires DaVinci Resolve Studio." Blackmagic's stated reason: "We have moved the ability to script in Python to the Studio version. The Python API was being used to hack studio features into the free version."
  - On free 21.1, Workspace > Scripts "ignores .py files entirely, with no warning dialog, no syntax error and no console log."
  - — [xere.my, "21.1 Silently Removed Python from the Free Edition"](https://xere.my/journal/davinci-resolve-21-1-free-python-scripting-removed-lua-benchmark/); [CineD 21.1](https://www.cined.com/davinci-resolve-21-1-released-ai-assistant-integration-via-mcp-individual-hdr-trims-and-python-scripting-moves-to-studio/); [Puget Systems](https://www.pugetsystems.com/blog/2026/09/10/how-davinci-resolve-free-v21-1-scripting-changes-affect-puget-bench/) (via search summary)
- CineD (via search summary): Workflow Integrations, the native UIManager and external scripting access are Studio only in 21.1, and Python 2 was removed from both editions. — [CineD 21.1](https://www.cined.com/davinci-resolve-21-1-released-ai-assistant-integration-via-mcp-individual-hdr-trims-and-python-scripting-moves-to-studio/)
- samuelgursky README: "Resolve 21.1 moved Python scripting to Studio." On free 21.1 the Scripts menu no longer lists .py files but Lua scripts still appear. Whether the Console still runs Python on free 21.1 is "unconfirmed". It also says the free edition's `scriptapp("Resolve")` refuses outside processes. — [samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp)
- **Free 21.1 Lua sandbox:**
  - Per saadk408's measurements, `io`, `os.execute`, `os.remove`, `require`, `package`, `ffi` and `debug` do not exist in the Lua state.
  - AutoSubs found `io`, `ffi`, `package`, `require`, `os.execute` and `bmd.readdir` are nil, so the old `ljsocket` HTTP server can no longer run.
  - Bridges now use a "file mailbox". The external process writes `request.lua`, Lua runs it via `loadfile`, and Lua replies via `fusion:SetPrefs(...)` + `fusion:SavePrefs()`, which the external process reads from `Fusion.prefs`.
  - — [saadk408/davinci-resolve-lua-mcp](https://github.com/saadk408/davinci-resolve-lua-mcp); [AutoSubs Resolve-Integration README](https://github.com/tmoroney/auto-subs/blob/main/Resolve-Integration/README.md)
- "Blackmagic documents neither this Lua host nor its sandbox, so a point release can change what works." — [saadk408/davinci-resolve-lua-mcp](https://github.com/saadk408/davinci-resolve-lua-mcp)
- **Official README on editions (21.1):**
  - "The DaVinci Resolve scripting APIs cover a common superset of functions for both the Free and Studio versions."
  - Calls return False when "the function references a Studio function from the free DaVinci Resolve version", when minimum system requirements aren't met, or when required Extras aren't downloaded.
  - External scripting is configured "In DaVinci Resolve Studio, Preferences > System > General" (None / Local / Network).
  - — [21.1.x README.md mirror](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/README.md)
- **Built-in MCP (21.1, Studio only):**
  - Set up via **File > Setup AI Assistants**. Resolve detects installed assistants and writes their MCP configuration, and the assistant must then be restarted.
  - Named assistants: Claude, Claude Code and ChatGPT Codex. The manual screenshot reportedly also shows Google Antigravity and Grok.
  - Covers media organisation, multicam switching, audio tweaks, markers, transcripts, renders and LUTs.
  - One report says the assistant gets ~14 general tools and does most work by writing Python against the scripting API.
  - Colour wheels, curves and masks are not exposed.
  - Security caution: scripts run with the assistant's disk and network access.
  - — [YMCinema](https://ymcinema.com/2026/09/17/davinci-resolve-21-1-mcp-ai-assistants-control-edit/); [Digital Production 21.1](https://digitalproduction.com/2026/09/08/resolve-21-1-adds-mcp-and-finally-gets-presets/); [scenepaper](https://scenepaper.com/blog/davinci-resolve-21-1-ai-agents-2026); [explainx](https://www.explainx.ai/blog/davinci-resolve-21-1-mcp-server-ai-agents-2026); [Motion Media](https://www.motionmedia.com/mm-blog/davinci-resolve-21-1-update-new-features) (all via search summary; the exact tool list is unverified)
- Studio price: US$295 one-time (CG Channel figure); ~€308 incl. VAT at one EU retailer. — (via search summary of [CineD 21.1](https://www.cined.com/davinci-resolve-21-1-released-ai-assistant-integration-via-mcp-individual-hdr-trims-and-python-scripting-moves-to-studio/) and related)

### Inferences
- **Decision tree for the skill:**
  - **(a) Studio 21.1+:** use the official File > Setup AI Assistants MCP. It is zero third-party install, but Resolve writes the Claude Code MCP config, so the user must approve that. Alternatively use a community Python MCP over External scripting = Local.
  - **(b) Free 21.1+:** the skill should *produce a plan plus an importable timeline file* (FCPXML/DRT/EDL) and/or markers. Optionally it can use a Lua mailbox bridge (experimental on Windows).
  - **(c) Free ≤21.0.x:** Python bridges via Workspace > Scripts still work. Advise the user *not* to upgrade blindly if he relies on one.
- The skill must ask the user which edition and version he has: Help > About, or `resolve.GetVersionString()` / `resolve.IsStudio()`.

### Gaps
- No primary Blackmagic text found for the exact list of what the built-in MCP exposes, its transport (stdio vs HTTP), or whether it can add titles or transitions.
- Unconfirmed whether the Console still accepts Python on Free 21.1.

## Q3. Windows setup (env vars, Python, DLL path, preferences)

### Takeaway
On Windows, Studio users have two options. They can run scripts with Resolve's **bundled `ResolvePython.exe` (Python 3.14, 21.1+)** with no env vars needed. Or they can use their own 64-bit Python ≥3.6 with three env vars that point at `fusionscript.dll` and the `Modules` folder. In both cases **Preferences > System > General > External scripting using = Local** must be set (Studio only).

### Cited Findings
- **Official Windows env vars (unchanged from 20.2 to 21.1):** — [20.2 README](https://github.com/thomjiji/dri/blob/main/READMEs/20.2_README.txt); [21.1.x README.md](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/README.md)
  ```
  RESOLVE_SCRIPT_API="%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
  RESOLVE_SCRIPT_LIB="C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
  PYTHONPATH="%PYTHONPATH%;%RESOLVE_SCRIPT_API%\Modules\"
  ```
- **Built-in interpreters (21.1+):**
  - "DaVinci Resolve 21.1 and above includes a custom Python 3.14 distribution": `import DaVinciResolveScript` works out of the box with no env vars, and "`pip`, `TK` and `IDLE` are not supported".
  - Windows path: `C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\ResolvePython.exe`.
  - LuaJIT 5.1: `C:\Program Files\Blackmagic Design\DaVinci Resolve\fuscript.exe`.
  - — [21.1.x README.md](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/README.md)
- **Supported languages:**
  - 21.1 README: "Lua 5.1" and "Python >= 3.6 64-bit". Python 2.7 was dropped in 21.1.
  - 20.2 README: Lua 5.1, Python ≥3.6 64-bit or Python 2.7 64-bit, "installed for all users".
  - — [21.1.x README.md](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/README.md); [20.2 README](https://github.com/thomjiji/dri/blob/main/READMEs/20.2_README.txt)
- Community guidance: samuelgursky recommends Python 3.10–3.12 as lowest risk and says 3.13/3.14 work on recent builds. — [samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp)
- **Preferences (21.1):**
  - "Preferences > System > General": External scripting (None, Local or Network) and "Automatic scripted actions" (recommended "Allow safe").
  - Network scripting listens on **port 1144**, with return connections in the 49152–65535 range.
  - Headless mode via `-nogui`.
  - — [21.1.x README.md](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/README.md)
- **Script menu folders on Windows:**
  - All users: `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts`.
  - Specific user: `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts` (21.1 README). The 20.2 README wrote `%APPDATA%\Roaming\...`, which doubles "Roaming".
  - Subfolders: `Utility` (all pages), `Edit`, `Color`, `Deliver`, `Comp`/`Tool` (Fusion).
  - — [21.1.x README.md](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/README.md); [20.2 README](https://github.com/thomjiji/dri/blob/main/READMEs/20.2_README.txt)
- When run internally (Console or Scripts menu), `bmd`, `resolve` and `fusion` are predefined globals. The recommended idiom is `if 'resolve' not in globals(): import DaVinciResolveScript as dvr_script; resolve = dvr_script.scriptapp("Resolve")`. — [21.1.x README.md](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/README.md)
- samuelgursky (Windows): a stale `fuscript.exe` can hold the bridge port on older builds, and the free-edition bridge was confirmed under both `%PROGRAMDATA%` and `%APPDATA%` on Windows 11. — [samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp)
- Lua mailbox bridges on Windows need ASCII-only state paths, and antivirus can cause EBUSY/EPERM errors. One project suggests `%PUBLIC%\resolve-pilot\bridge` for non-ASCII user folders. This is relevant if the Windows username contains Arabic characters. — [saadk408/davinci-resolve-lua-mcp](https://github.com/saadk408/davinci-resolve-lua-mcp); [emircbngl/davinci-resolve-mcp-free](https://github.com/emircbngl/davinci-resolve-mcp-free); [AutoSubs Resolve-Integration README](https://github.com/tmoroney/auto-subs/blob/main/Resolve-Integration/README.md) (paths are baked as ANSI code-page bytes with 8.3 short-path fallback)

### Inferences
- With Studio 21.1+, a skill can run one-off Python scripts with `ResolvePython.exe` and needs **no Python install and no env vars**. That fits "nothing installed without approval". Third-party pip packages (whisper, etc.) need a separate Python because pip isn't supported in ResolvePython.
- If the Windows user profile path has Arabic characters, file-mailbox bridges may break. Check `%USERNAME%` early.

### Gaps
- No official statement on which Python minor versions Resolve's `fusionscript.dll` binds reliably beyond "≥3.6 64-bit".

## Q4. Exact API calls relevant to an editing assistant (with version notes)

### Takeaway
The API covers the core of a "put X at second Y" plan: import media, append clips at exact record frames on chosen tracks, add tracks, add markers with notes and hidden customData, insert titles and generators at the playhead, set static transform/crop/opacity/composite properties, and (since 21.1) add transitions, set fades and change speed. **Edit-page keyframes are still not settable.** Animated zooms need Fusion comps or Resolve's Dynamic Zoom.

### Cited Findings (signatures are verbatim from the official README/.pyi)
**Media Pool** — [20.2 README](https://github.com/thomjiji/dri/blob/main/READMEs/20.2_README.txt); [21.1 .pyi](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/DaVinciResolveScript.pyi)
- `ImportMedia([items...]) --> [MediaPoolItems]`: imports file/folder paths into the current Media Pool folder. `ImportMedia([{clipInfo}])` takes `{"FilePath":"file_%03d.dpx","StartIndex":1,"EndIndex":100}` for image sequences. In 21.1 the canonical form is `ImportMedia(clipInfos: list[ImportClipInfo])` and the bare-path list is deprecated.
- `AppendToTimeline([{clipInfo}, ...]) --> [TimelineItem]`: clipInfo keys are `"mediaPoolItem"`, `"startFrame"` (float/int, source in), `"endFrame"` (source out), optional `"mediaType"` (1 = video only, 2 = audio only), `"trackIndex"` (int) and `"recordFrame"` (float/int, timeline position). 21.1 `AppendClipInfo` marks all but mediaPoolItem optional.
- `CreateTimelineFromClips(name, [{clipInfo}])`, `CreateEmptyTimeline(name)`.
- `ImportTimelineFromFile(filePath, {importOptions}) --> Timeline` accepts AAF/EDL/XML/FCPXML/DRT/ADL/OTIO. Options: `timelineName`, `importSourceClips` (default True), `sourceClipsPath`, `sourceClipsFolders`, `interlaceProcessing` (AAF only). `timelineName`/`importSourceClips` are "Not valid for DRT import".
- `GetSelectedClips()`, `SetSelectedClip(item)`, `AutoSyncAudio([items], {settings})`, `MoveClips`, `AddSubFolder(folder, name)`, `ImportFolderFromFile(drbPath)`.
- MediaPoolItem has `AddMarker`, `GetMarkers`, `SetClipColor`, `AddFlag`, `SetMetadata({...})` and `GetClipProperty()`.
- Transcription: `TranscribeAudio(useSpeakerDetection=None, transcribeAsNestedClip=False)` (speaker arg added in 21.0) and `ClearTranscription()`.
- **21.1:** `GetTranscription(useNestedClipTranscription=False) --> Transcription` returns `{language, segments:[{start, end, text, speaker, words:[{start, end, text}]}]}` with timecodes like '01:00:02:05', and '(...)' marks silence.

**Timeline** — [20.2 README](https://github.com/thomjiji/dri/blob/main/READMEs/20.2_README.txt); [21.1 .pyi](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/DaVinciResolveScript.pyi)
- `AddMarker(frameId, color, name, note, duration, customData) --> Bool`: "frameId" is the offset from timeline start, and customData is optional.
  - 21.1 `.pyi` typing: `AddMarker(frameId: int, color: MarkerColor, name: str, note: str, duration: int, customData: str | None = None)`.
  - **Marker colours (21.1 .pyi):** Blue, Cyan, Green, Yellow, Red, Pink, Purple, Fuchsia, Rose, Lavender, Sky, Mint, Lemon, Sand, Cocoa, Cream (16).
  - Clip colours: Orange, Apricot, Yellow, Lime, Olive, Green, Teal, Navy, Blue, Purple, Violet, Pink, Tan, Beige, Brown, Chocolate.
- `GetMarkers() --> {frameId: {'color','duration','note','name','customData'}}`, `GetMarkerByCustomData(cd)`, `UpdateMarkerCustomData(frameId, cd)`, `GetMarkerCustomData(frameId)`, `DeleteMarkersByColor(color|"All")`, `DeleteMarkerAtFrame(f)`, `DeleteMarkerByCustomData(cd)`. Per the README, "CustomData is not exposed via UI and is useful for scripting developer to attach any user specific data to markers".
- `AddTrack(trackType, subTrackType)`:
  - trackType is "video", "subtitle" or "audio".
  - Audio subTrackType is one of "mono", "stereo", "5.1", "7.1", "adaptive1"…"adaptive36", etc., defaulting to mono.
  - Alternate form: `AddTrack(trackType, {'audioType':..., 'index':...})`.
  - Related: `DeleteTrack(type, idx)`, `GetTrackCount(type)`, `SetTrackName`, `SetTrackEnable`, `SetTrackLock`, `GetTrackSubType`.
- `GetItemListInTrack(trackType, index) --> [TimelineItem]`. The dict-returning `GetItemsInTrack` is deprecated.
- `DeleteClips([items], ripple=False)`, `SetClipsLinked([items], Bool)`, `CreateCompoundClip([items], {"startTimecode","name"})`, `CreateFusionClip([items])`, `DuplicateTimeline(name)`.
- `GetCurrentTimecode()` / `SetCurrentTimecode(tc)` work "for Cut, Edit, Color, Fairlight and Deliver pages". `GetCurrentVideoItem()` returns the current video item.
- `InsertGeneratorIntoTimeline(name)`, `InsertFusionGeneratorIntoTimeline(name)`, `InsertFusionCompositionIntoTimeline()`, `InsertOFXGeneratorIntoTimeline(name)`, `InsertTitleIntoTimeline(titleName)` and `InsertFusionTitleIntoTimeline(titleName)` each return a TimelineItem. They take a name only, with no position, track or text arguments.
- `Export(fileName, exportType, exportSubtype)`:
  - Types: `EXPORT_AAF`, `EXPORT_DRT`, `EXPORT_EDL`, `EXPORT_FCP_7_XML`, `EXPORT_FCPXML_1_8/1_9/1_10`, `EXPORT_TEXT_CSV`, `EXPORT_TEXT_TAB`, `EXPORT_OTIO`, `EXPORT_ALE`, `EXPORT_ALE_CDL`, HDR10/Dolby Vision.
  - Subtype is required only for AAF and EDL.
  - FCPXML 1.3–1.7 export has been unsupported since 18.1.
- `ImportIntoTimeline(filePath, {importOptions})` imports items from an **AAF file** into the *existing* timeline. Options include `insertAdditionalTracks` and `insertWithOffset` "00:00:00:00", `autoImportSourceClipsIntoMediaPool`, `sourceClipsPath`, etc.
- `CreateSubtitlesFromAudio({autoCaptionSettings}) --> Bool`. The 20.2 settings keys are `resolve.SUBTITLE_LANGUAGE`, `SUBTITLE_CAPTION_PRESET`, `SUBTITLE_CHARS_PER_LINE` (1–60, default 42), `SUBTITLE_LINE_BREAK` and `SUBTITLE_GAP` (0–10). The 21.1 `.pyi` `AutoCaptionSettings` uses keys `language`, `captionPreset`, `charsPerLine`, `lineBreak`, `gap`.
- `DetectSceneCuts() --> Bool` (status poller in 21.1.1), `ConvertTimelineToStereo()`, `GrabStill()`, `GetMarkInOut/SetMarkInOut/ClearMarkInOut`.
- `GetVoiceIsolationState(trackIndex)` / `SetVoiceIsolationState(trackIndex, {isEnabled, amount 0–100})` (20.1+).
- **21.0.4+:** `Timeline.GetSelectedClips() --> [TimelineItem]`.
- **21.1:** `NormalizeAudioLevel([items], {options})`, `GetNormalizeAudioModes()`, `AutoAlignClips([items], {options})`, `Get/SetOutputBlanking`, `GetSettings()`/`SetSettings({...})`.
- `Project.InsertAudioToCurrentTrackAtPlayhead(mediaPath, startOffsetInSamples, durationInSamples) --> Bool` (present in the 20.2 README and the 21.1 .pyi). It is useful for SFX at the playhead.

**TimelineItem** — [20.2 README](https://github.com/thomjiji/dri/blob/main/READMEs/20.2_README.txt); [21.1 .pyi](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/DaVinciResolveScript.pyi); [21.1 README.md](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/README.md)
- `SetProperty(key, value)` / `GetProperty(key)`: deprecated in 21.1 in favour of `SetProperties({...})` / `GetProperties()`. Supported keys (20.2 README):
  - **Transform:**
    - `Pan` (−4·width…4·width) and `Tilt` (−4·height…4·height).
    - `ZoomX` and `ZoomY` (0.0–100.0) plus `ZoomGang`.
    - `RotationAngle` (−360…360), `AnchorPointX/Y`, `Pitch`/`Yaw` (−1.5…1.5) and `FlipX/FlipY`.
  - **Crop:** `CropLeft/Right` (0…width), `CropTop/Bottom` (0…height), `CropSoftness` (−100…100) and `CropRetain`.
  - **Dynamic zoom:** `DynamicZoomEase` (LINEAR / IN / OUT / IN_AND_OUT).
  - **Compositing:** `CompositeMode` (COMPOSITE_NORMAL…, 32 modes incl. SCREEN, OVERLAY, ADD) and `Opacity` (0–100).
  - **Lens:** `Distortion`.
  - **Retime and scaling:** `RetimeProcess` (project / nearest / frame blend / optical flow), `MotionEstimation` (incl. Speed Warp), `Scaling` (project / crop / fit / fill / stretch) and `ResizeFilter`.
- **21.1 additions to TimelineItemProperties:**
  - Enable toggles: `TransformEnabled`, `CroppingEnabled`, `DynamicZoomEnabled`, `CompositeEnabled`, `LensCorrectionEnabled`, `RetimeAndScalingEnabled`.
  - Audio: `AudioVolumeEnabled`/`AudioVolume`, `AudioPanEnabled`/`AudioPan`, `AudioPitchEnabled`/`AudioPitchSemiTones`/`AudioPitchCents`.
  - Voice isolation: `AudioVoiceIsolationEnabled`/`AudioVoiceIsolationAmount`.
  - Dialogue leveler: `AudioDialogueLevelerEnabled`/`Mode`/`ReduceLoudDialogue`/`LiftSoftDialogue`/`BackgroundReduction`/`OutputGain`.
  - Some audio keys are marked "[Active Timeline Only]".
- **21.1 `AddTransition(transitionOptions) --> TimelineItem | None`**: "Adds a transition of the given type/category to the start or end of this item". The options are:
  - `type` (e.g. 'Cross Dissolve').
  - `category` ('simple', 'fusion', 'ofx' or 'audio').
  - `position` ('start' or 'end').
  - `alignment` ('left', 'center' or 'right').
  - `duration` (frames; default "automatically calculated").
- **21.1 `GetType()`** returns 'video', 'audio', 'generator' or 'transition'.
- **21.1 fades and speed:**
  - `SetFades({FadeIn, FadeOut})` / `GetFades()` set the fade durations in frames.
  - `SetSpeed({Percentage, PitchCorrection, StretchKeyframesToFit, RippleTimeline})` / `GetSpeed()`; Percentage 0.0 gives a freeze frame.
- `AddMarker(frameId, color, name, note, duration, customData)`: frameId is the clip offset. TimelineItems also have `GetMarkers`, `SetClipColor`, `AddFlag`, `SetClipEnabled(Bool)` and `SetName` (20.2+).
- Positions: `GetStart()`, `GetEnd()`, `GetDuration()`, `GetSourceStartFrame()`, `GetSourceEndFrame()`, `GetLeftOffset()`, `GetRightOffset()`, `GetTrackTypeAndIndex()`, `GetLinkedItems()`.
- Fusion: `AddFusionComp()`, `ImportFusionComp(path)`, `ExportFusionComp(path, idx)`, `LoadFusionCompByName`, `GetFusionCompByIndex(i)`, `GetFusionCompNameList()`.
- AI ops: `CreateMagicMask("F"|"B"|"BI")`, `RegenerateMagicMask()`, `Stabilize()`, `SmartReframe()`, `SetVoiceIsolationState({isEnabled, amount})`.
- **Keyframing:**
  - The only keyframe API is `Resolve.GetKeyframeMode()/SetKeyframeMode()` with modes `KEYFRAME_MODE_ALL/COLOR/SIZING`. The 21.1 .pyi says GetKeyframeMode is "Color Page only".
  - Stereo convergence keyframes are read-only (`GetStereoConvergenceValues`).
  - The 21.1 .pyi has no keyframe setter for Inspector properties.
  - — [21.1 .pyi](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/DaVinciResolveScript.pyi); [20.2 README](https://github.com/thomjiji/dri/blob/main/READMEs/20.2_README.txt)

**Audio / Fairlight**
- Available: `AddTrack("audio", "stereo")`, `AppendToTimeline` with `mediaType: 2` plus `trackIndex`, `InsertAudioToCurrentTrackAtPlayhead`, `Get/SetVoiceIsolationState`, `ApplyFairlightPresetToCurrentTimeline(preset)` (20.2.2), `GetFairlightPresets()`, `NormalizeAudioLevel` (21.1), audio properties via `SetProperties` (21.1) and `SetFades` (21.1). — [CHANGELOG](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/CHANGELOG.md); [21.1 .pyi](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/DaVinciResolveScript.pyi)
- A changelog fix in 20.2.2: "AppendToTimeline validating trackIndex as video track indices in 'Audio Only' mode". Before 20.2.2, audio-only appends to higher audio tracks could fail. — [CHANGELOG](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/CHANGELOG.md)

### Inferences
- A "plan → Resolve" push on Studio 21.1+ can be done fully with the API:
  - Import B-roll and SFX (`ImportMedia`).
  - `AddTrack` for V2/V3 and A2/A3.
  - `AppendToTimeline` with `recordFrame = timelineStart + round(sec*fps)`, `trackIndex`, `mediaType`.
  - Static punch-in zooms via `SetProperties({"ZoomX":1.2,"ZoomY":1.2})` on a blade-split segment.
  - `AddTransition` at cut points.
  - `SetFades` on music and SFX.
  - Coloured markers carrying the instruction text in `note` and a JSON plan id in `customData`.
- `recordFrame` and marker `frameId` conventions differ: AppendToTimeline's recordFrame is an absolute timeline frame (often starting at 86400 for 01:00:00:00 at 24fps), while Timeline.AddMarker's frameId is relative to the timeline start. This should be verified on the user's machine, and `GetStartFrame()` used to convert.
- There is no API to blade or split a clip at a frame. Community tools rebuild clips via AppendToTimeline with start and end frames (flamexnreal's `split_clip` "rebuilds clips", see Q6). Punch-in zooms therefore require placing separate segments.
- `InsertTitleIntoTimeline` and `InsertFusionTitleIntoTimeline` insert at the playhead on the current or selected track, so `SetCurrentTimecode` must be called first. Setting the actual text requires going into the item's Fusion comp (`GetFusionCompByIndex(1)` → Text+ tool → `StyledText` input). This is standard Fusion scripting and is not covered in the Resolve README.

### Gaps
- No official doc on which `type` strings `AddTransition` accepts beyond 'Cross Dissolve', or whether it works on Free via Lua.
- The exact recordFrame semantics are not stated in the README.
- No official statement on whether `InsertTitleIntoTimeline` respects the selected track.

## Q5. What CANNOT be done via the API, and workarounds

### Takeaway
The main hard limits as of 21.1.1:
- **No Edit-page keyframes** (animated zoom, pan or opacity).
- **No direct text content argument for titles.**
- **No blade/split at a frame.**
- **No Fairlight automation or plugin inserts.**
- **No colour wheels, curves or masks.**
- **No transitions before 21.1.**

The workarounds are Fusion comps or templates (`.setting` macros and `.comp` files via `ImportFusionComp`, where keyframes are possible), timeline interchange files (FCPXML/DRT/AAF/OTIO via `ImportTimelineFromFile`), and markers or a cue-sheet the editor follows by hand.

### Cited Findings
- **Transitions:** there is no transition function in the 20.2 README. 21.1 added "Transition API - TimelineItem.AddTransition". Before 21.1, transitions could not be added via API. — [20.2 README](https://github.com/thomjiji/dri/blob/main/READMEs/20.2_README.txt); [CHANGELOG](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/CHANGELOG.md)
- **Keyframes:**
  - TimelineItem properties are set as single static values. The README says "Values beyond the range will be clipped" and documents no time parameter.
  - The only keyframe-mode calls are Color-page modes.
  - `SetSpeed` includes `StretchKeyframesToFit`, which shows keyframes exist on items but are not writable via the API.
  - — [21.1 .pyi](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/DaVinciResolveScript.pyi); [20.2 README](https://github.com/thomjiji/dri/blob/main/READMEs/20.2_README.txt)
- **Fusion keyframes as workaround:** community MCP servers implement "`animate_zoom` (keyframed Fusion zoom)" and `keyframe_clip_saturation` through Fusion comps. — [flamexnreal/davinci-resolve-ai-bridge-mcp](https://github.com/flamexnreal/davinci-resolve-ai-bridge-mcp)
- **Fusion macro as caption/title template:** AutoSubs adds subtitles using the Fusion macro `autosubs-macro.setting`, "an animated caption template with per-word highlighting", via its `AddSubtitles` routine, and it reads available "Fusion templates in the media pool". — [AutoSubs Resolve-Integration README](https://github.com/tmoroney/auto-subs/blob/main/Resolve-Integration/README.md)
- **Titles:** flamexnreal lists `insert_title` as "best effort; check `text_set`", which implies setting the text is unreliable. — [flamexnreal/davinci-resolve-ai-bridge-mcp](https://github.com/flamexnreal/davinci-resolve-ai-bridge-mcp)
- **Colour:** "For colour, the API handles LUTs, CDL, grades from a DRX still and enabling or disabling nodes. Colour wheels, curves and masks are not exposed." — (via search summary of [scenepaper](https://scenepaper.com/blog/davinci-resolve-21-1-ai-agents-2026) / [explainx](https://www.explainx.ai/blog/davinci-resolve-21-1-mcp-server-ai-agents-2026)). This is consistent with the .pyi: `SetCDL`, `ExportLUT`, `ApplyGradeFromDRX`, Graph node LUT functions.
- **Interchange workarounds:**
  - `ImportTimelineFromFile` accepts AAF/EDL/XML/FCPXML/DRT/ADL/OTIO.
  - `Timeline.Export` writes DRT/FCPXML 1.8–1.10/OTIO/EDL/AAF/CSV.
  - `MediaPool.ImportFolderFromFile(drbPath)` imports bins.
  - — [20.2 README](https://github.com/thomjiji/dri/blob/main/READMEs/20.2_README.txt)
- Free-edition projects already use "FCPXML export: Claude builds a timeline outside Resolve, which you import via File › Import › Timeline". — [emircbngl/davinci-resolve-mcp-free](https://github.com/emircbngl/davinci-resolve-mcp-free); [wassermanproductions/unofficial-davinci-mcp](https://github.com/wassermanproductions/unofficial-davinci-mcp) ("free-edition FCPXML/LUT workflows", per its GitHub description)
- **Splitting:** flamexnreal says "Splits rebuild clips. Audio links, fades, keyframes, and some metadata are not guaranteed." — [flamexnreal/davinci-resolve-ai-bridge-mcp](https://github.com/flamexnreal/davinci-resolve-ai-bridge-mcp)
- **Long synchronous calls:** `RenderWithQuickExport`, `TranscribeAudio`, `Export`, `ArchiveProject` and `LoadProject` block a Lua bridge until done, and the bridge "cannot answer modal dialogs". — [saadk408/davinci-resolve-lua-mcp](https://github.com/saadk408/davinci-resolve-lua-mcp)
- **Studio-gated Extras:**
  - `AnalyzeForIntellisearch` needs "AI IntelliSearch - Faster/Better", `AnalyzeForSlate` needs "AI Slate ID", and `GenerateSpeech` needs "AI Speech Generator".
  - "Transcription workflows with extended language models" need an Extras download, installed via the Extras Download Manager in **Studio**.
  - — [21.1 README.md](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/README.md)

### Inferences
- For a free-edition user, the most robust push path is to **generate an FCPXML (or OTIO/EDL) timeline** containing the A-roll plus B-roll, SFX, titles and transitions, and have him import it via File > Import > Timeline. Alternatively, give him a **marker cue sheet** (EDL with markers or CSV) and he does the craft edits manually.
- For animated zooms: (a) use Resolve's Dynamic Zoom (`DynamicZoomEnabled` and `DynamicZoomEase` are settable, but the start and end rectangles are not documented as settable), (b) apply a Fusion `.setting` macro or `.comp` via `ImportFusionComp`, or (c) script keyframes in the Fusion comp.

### Gaps
- Unverified how faithfully Resolve 21 imports FCPXML keyframed transforms, titles with text, and transitions. A Resolve 21 beta 4 report says FCPXML support was improved ([Motion Media](https://www.motionmedia.com/mm-blog/davinci-resolve-21-beta-4-fcpxml-ai-updates), via search summary), but no fidelity details were found.
- Power Bin access via API was not found in the docs.

## Q6. Existing open-source projects (MCP servers, libraries, plugins)

### Takeaway
There are now 15+ Resolve MCP servers. **samuelgursky/davinci-resolve-mcp** (~3.7k★, active, pushed 19 Oct 2026) is the clear leader. Almost all of them need **Studio** for live control. For **Free 21.1+**, only Lua file-mailbox bridges (saadk408, emircbngl, AutoSubs-style) work, and they are young and lightly tested on Windows. **Blackmagic's own MCP (Studio 21.1+)** makes third-party servers optional for Studio users.

### Cited Findings
**Star counts and push dates:** GitHub search API, 22 Oct 2026, unless noted.

- **samuelgursky/davinci-resolve-mcp** — https://github.com/samuelgursky/davinci-resolve-mcp
  - **Activity:** 3,697★, pushed 2026-10-19, version badge 4.14.4.
  - **Tools:**
    - Compound server with 37 tools (136 guarded workflow actions).
    - Granular server with 390 tools, one per API method.
    - Offline Node server with 18 tools that operate on .drp/.drt/.drx files without Resolve running.
  - **Coverage:** app/project, media pool, media analysis, timeline editing and conform, colour, Fusion, Fairlight, render, extension authoring.
  - **Requirements:** Resolve 18.5+ and Python 3.10+. Node is needed for the advanced server.
  - **Optional installs:** ffmpeg, numpy, librosa, openai-whisper, open_clip_torch, transformers, opencv-python.
  - **Install:** `npx davinci-resolve-mcp setup` or `python install.py` (creates a venv and configures clients).
  - **Edition:** External scripting needs Studio. The free in-app bridge runs via Workspace > Scripts > resolve_bridge ("supported-until-it-is-not"), and it is a 21.0.x path only after 21.1.
  - Includes a copy of the API reference ("Last Updated: 24 Jul 2026"): [docs/reference/resolve_scripting_api.txt](https://github.com/samuelgursky/davinci-resolve-mcp/blob/main/docs/reference/resolve_scripting_api.txt).
  - — [repo](https://github.com/samuelgursky/davinci-resolve-mcp)
- **barckley75/resolve-claude-mcp** — https://github.com/barckley75/resolve-claude-mcp
  - **Activity:** 388★, pushed 2026-05-14.
  - **Tools:** 52, including Magic Mask, Smart Reframe, stabilise, scene cuts, subtitles, voice isolation, and `execute_resolve_code` for arbitrary Python.
  - **Requirements:** Studio 18+, Python 3.10+, `uv`.
  - **Status:** tested only on macOS. Its transcription and screenshot tools are macOS-only, and it says "Do not use in production."
  - — [repo](https://github.com/barckley75/resolve-claude-mcp)
- **hiteshK03/davinci-resolve-mcp** — https://github.com/hiteshK03/davinci-resolve-mcp
  - **Activity:** 141★, pushed 2026-03-28.
  - **Tools:** README claims 44 or 162 tools, with "155 of 162 tools work on Free".
  - **How it works:** a Python bridge `CursorBridge.py` runs via Workspace > Scripts over localhost HTTP.
  - **Extras:** faster-whisper local transcription (CPU).
  - **Requirements:** Python 3.9+, Resolve 18+ Free or Studio.
  - **Status:** has a Windows/WSL config. Predates 21.1, which removes .py from the free Scripts menu.
  - — [repo](https://github.com/hiteshK03/davinci-resolve-mcp)
- **apvlv/davinci-resolve-mcp** — https://github.com/apvlv/davinci-resolve-mcp
  - **Activity:** 79★, pushed 2026-04-07.
  - **Scope:** Resolve and Fusion. Python 3.10+, launched with `uv run`.
  - — [search summary](https://github.com/apvlv/davinci-resolve-mcp)
- **wassermanproductions/unofficial-davinci-mcp**: 37★, pushed 2026-07-20. "live Studio control, free-edition FCPXML/LUT workflows, reference color matching, beat-aware mu[sic]" (GitHub description). — https://github.com/wassermanproductions/unofficial-davinci-mcp
- **flamexnreal/davinci-resolve-ai-bridge-mcp** — https://github.com/flamexnreal/davinci-resolve-ai-bridge-mcp
  - **Activity:** 37★, pushed 2026-10-17.
  - **Edition:** claims Free and Studio. On Free it runs a Python worker from the Scripts menu or the Console (Py3) with file-based requests in `~/.resolve-ai-bridge/requests/`, and it attaches directly on Studio.
  - **Tools:** `split_clip`, `review_silence`, `apply_silence_cuts`, `animate_zoom` (keyframed Fusion zoom), `set_clip_transform`, `add_marker`, `insert_title`, speed changes.
  - **Status:** live-verified only on macOS with Resolve Free 21.0.3. Windows installers (`install-windows.bat`, `install.ps1`) exist but are "not live-verified".
  - **Python dependency:** relies on Python in Resolve, so likely broken on Free 21.1.
  - — [repo](https://github.com/flamexnreal/davinci-resolve-ai-bridge-mcp)
- **hoyt-harness/davinci-mcp-professional**: 25★, pushed 2026-10-10, "Token-efficient MCP server for DaVinci Resolve Studio — kernel + domain architecture". — https://github.com/hoyt-harness/davinci-mcp-professional (GitHub description only)
- **lordhoell/davinci-resolve-mcp** — https://github.com/lordhoell/davinci-resolve-mcp
  - **Activity:** 22★, last push 2026-04-03.
  - **Tools:** 440+, plus a bundled **Claude Code skill** (`skill/davinci-resolve-mcp/`).
  - **Install:** `pip install davinci-resolve-mcp`, then `claude mcp add davinci-resolve -- davinci-resolve-mcp`.
  - **Requirements:** Resolve 19+, Python 3.10+.
  - — [repo](https://github.com/lordhoell/davinci-resolve-mcp)
- **Tooflex/davinci-resolve-mcp**: 20★, pushed 2026-07-25, 32 tools plus 6 resources, Studio. — https://github.com/Tooflex/davinci-resolve-mcp ([listing](https://mcpservers.org/servers/Tooflex/davinci-resolve-mcp))
- **mhadifilms/dvr**: 15★, pushed 2026-10-21. "DaVinci Resolve CLI, Python library, and MCP server". — https://github.com/mhadifilms/dvr (GitHub description). The same author's v20.3 API gist is a useful reference: [gist](https://gist.github.com/mhadifilms/2b84d469135315793220dbf2226cbe63).
- **guycochran/resolve-mcp-server** (13★, 53 tools) and **allwavemedia/resolve-ai-toolkit** (10★, 21 tools). — https://github.com/guycochran/resolve-mcp-server ; https://github.com/allwavemedia/resolve-ai-toolkit (GitHub descriptions)
- **Free-edition 21.1 Lua bridges:**
  - **saadk408/davinci-resolve-lua-mcp** — https://github.com/saadk408/davinci-resolve-lua-mcp
    - **Activity:** 4★, 65 commits. There is also a fork at bryankthompson.
    - **Install:** a Claude Desktop `.mcpb` extension (Node 20, supplied by Claude Desktop), plus a Lua `resolve_mcp_bridge` launched via Workspace > Scripts after every Resolve start.
    - **Tools (15):** `run_lua`, `add_marker`, `list_timelines`, `get_timeline_items`, render, and others.
    - **Status:** measured on free 21.1.0.17 on macOS. "Windows support: Experimental."
    - — [repo](https://github.com/saadk408/davinci-resolve-lua-mcp)
  - **emircbngl/davinci-resolve-mcp-free** — https://github.com/emircbngl/davinci-resolve-mcp-free
    - **Activity:** 9★, pushed 2026-10-15.
    - **How it works:** a Lua bridge "ResolvePilotBridge", FCPXML export, and pasteable Lua snippets.
    - **Tools:** scene/beat/silence detection, transcription, rough-cut plans, SRT.
    - **Requirements:** Python 3.11+ and ffmpeg/ffprobe.
    - **Status:** Windows supported (UI automation macOS-only), but "not yet tried on a 21.1 install".
    - — [repo](https://github.com/emircbngl/davinci-resolve-mcp-free)
- **Yasei-no-otoko/codex-skill-davinci-resolve-edit**: 9★, pushed 2026-09-14, a "Codex skill for local video editing with DaVinci Resolve 21.1 MCP and UI workflows". This is a prior-art skill built on the official MCP. — https://github.com/Yasei-no-otoko/codex-skill-davinci-resolve-edit (GitHub description)
- **legionsound/open-fusion-mcp**: 8★, pushed 2026-10-02, "MCP server and agent skills for motion design in DaVinci Resolve Fusion: 179 checked operations". — https://github.com/legionsound/open-fusion-mcp (GitHub description)
- **pydavinci (pedrolabonia)**: 183★, a typed Python wrapper. It needs Studio, the banner reads "This project needs maintainers!", and pip versions target Resolve 17/18. It is effectively stale. — [repo](https://github.com/pedrolabonia/pydavinci)
- **AutoSubs (tmoroney/auto-subs)** — https://github.com/tmoroney/auto-subs
  - **Activity:** ~4.4k★, MIT.
  - **Platforms:** Windows x64 installer, macOS and Linux.
  - **Engines:** local Whisper (tiny…large-v3, large-v3-turbo via whisper-rs/GGML) plus Moonshine, Parakeet, SenseVoice, Canary, Cohere, GigaAM, Omni-ASR.
  - **Arabic:** via "moonshine-tiny-ar" and Cohere (Arabic among 14 languages).
  - **Other features:** speaker diarization, and an optional MMS forced-alignment model (~320 MB, CC BY-NC 4.0) for word timestamps.
  - **Resolve 21.1 compatibility:** the Resolve integration was rewritten for the 21.1 sandbox as a file mailbox and works on Free again. The script can no longer launch the app, so the user starts AutoSubs first and then Workspace > Scripts > AutoSubs.
  - **Windows install locations:** `%LOCALAPPDATA%\AutoSubs\AutoSubs.exe`, with scripts in `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility\`.
  - — [repo](https://github.com/tmoroney/auto-subs); [Resolve-Integration README](https://github.com/tmoroney/auto-subs/blob/main/Resolve-Integration/README.md); [releases](https://github.com/tmoroney/auto-subs/releases) (via search summary)
- **Snap Captions 2 (Orson Lord, paid):** works on Resolve **Studio 19.1+** and does not run on the free version. Animated captions build on Resolve's own transcription languages, and Arabic was not listed in the results. — [caption-x comparison page](https://caption-x.com/snap-captions-davinci-resolve) (via search summary; vendor-competitor page, so treat with care)
- **FireCut (firecut.ai):** silence removal inside the Resolve timeline (Basic→Tight, or Advanced dB threshold, minimum duration, padding) and animated captions in 50+ languages. Pricing claims conflict: one source says silence and rough-cut tools are free on Resolve Free and Studio with Pro at $16/mo, while another lists from $19/mo ($10/mo billed yearly). — [FireCut Resolve silence page](https://firecut.ai/features/davinci-resolve/remove-silences); [FireCut captions](https://firecut.ai/features/davinci-resolve/captions); [drrave comparison](https://shop.drrave.com/blogs/blog/roughcut-vs-autocut-vs-firecut-davinci-resolve) (via search summary)
- **AutoCut:** the vendor says it is available for Premiere Pro and DaVinci Resolve, and CineD says it supports Resolve 18.6/19+ incl. Free. One roundup says it uses a volume threshold (can cut mid-word), and another (competitor) guide claims there is no Resolve version. The claims conflict. — [AutoCut](https://www.autocut.com/en/autocutsilences/); [CineD AutoCut](https://www.cined.com/autocut-plugin-now-integrates-ai-directly-into-premiere-pro-to-automatically-handle-time-consuming-tasks/); [PremiereCopilot](https://www.premierecopilot.com/en/blog/remove-silence-davinci-resolve) (via search summary)

### Inferences
- **Security and installs for each path:**
  - **Official MCP:** nothing third-party, but needs Studio 21.1+ and lets Resolve write the Claude Code MCP config.
  - **samuelgursky:** Python 3.10+ venv plus Node/npx, with optional heavy ML pip packages.
  - **Lua bridges:** a Lua script in the Fusion Scripts folder plus Node (via Claude Desktop) or Python.
  - **AutoSubs:** a native .exe plus Lua scripts, with models downloaded on demand.
  - All of these should be presented to the user for approval before install.
- Several servers expose `run_lua` or `execute_resolve_code`, which means arbitrary code execution with the user's privileges. The skill should prefer typed tools, or show the code before running it.

### Gaps
- "Storycut" and "Vibe editing" Resolve projects were not found in searches. No reliable info.
- Star counts for some smaller repos come from the GitHub search API at the time of research and were not otherwise verified.
- Windows behaviour of most bridges is unverified by their own authors.

## Q7. Built-in Resolve AI / Neural Engine features that complement the skill

### Takeaway
Resolve has strong built-in AI, but most of it is **Studio-only**: transcription and text-based editing, IntelliScript, Smart Reframe, Magic Mask (full), Voice Isolation, Dialogue Leveler, scene-cut detection, IntelliSearch and Speech Generator. Several are callable from the API (`TranscribeAudio`/`GetTranscription`, `CreateSubtitlesFromAudio`, `DetectSceneCuts`, `SmartReframe`, `CreateMagicMask`, voice isolation, `NormalizeAudioLevel`). **Arabic is not in the built-in transcription language list.** It reportedly comes via an "extended" transcription Extras package. There is **no native one-click silence-cut on the Edit timeline**. The transcript "Remove Silent Portions" option is Studio-only, and Fairlight has a threshold-based Remove Silence.

### Cited Findings
- **Auto-caption languages in the API:**
  - 20.2 README: Auto, Danish, Dutch, English, French, German, Italian, Japanese, Korean, Mandarin Simplified and Traditional, Norwegian, Portuguese, Russian, Spanish, Swedish.
  - 21.1 .pyi adds Finnish, Hindi, Indonesian, Malay, Polish, Romanian, Turkish, Vietnamese, Tamil and Thai.
  - **No `AUTO_CAPTION_ARABIC` constant exists in either.**
  - — [20.2 README](https://github.com/thomjiji/dri/blob/main/READMEs/20.2_README.txt); [21.1 .pyi](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/DaVinciResolveScript.pyi)
- 21.1 README: "Transcription workflows with extended language models [require Extras]. Languages from built in models will be used as a fallback if unavailable." Extras are installed via the Studio Extras Download Manager. — [21.1 README.md](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/README.md)
- Third-party guides say an "Extended AI Transcription Support Package" from the Extras Downloads Manager adds ~43 languages "among them Arabic". The sources are secondary and disagree in places. Blackmagic forum threads requesting Arabic transcription exist. — [davinciresolveclub, Transcribe Audio in Resolve 21](https://davinciresolveclub.com/transcribe-audio-davinci-resolve/); [Blackmagic Forum, Support Arabic transcription](https://forum.blackmagicdesign.com/viewtopic.php?f=33&t=199838); [Blackmagic Forum, Request for Arabic Language Support](https://forum.blackmagicdesign.com/viewtopic.php?f=33&t=212513) (via search summary)
- **IntelliScript is Studio only:** it builds a timeline by matching transcribed clips to a script, and alternate takes go on disabled tracks. Resolve 21 adds Final Draft or plain-text script import. — [cutsio IntelliScript](https://cutsio.com/blog/davinci-intelliscript-tutorial-what-it-can-and-cant-do); [Resolve 21 New Features Guide PDF](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_21_New_Features_Guide.pdf?_v=1776322810000) (via search summary)
- **Silence:**
  - The Transcription window's "Remove Silent Portions" is Studio-only, and silences show as "(...)".
  - Fairlight has a "Remove Silence" command that deletes audio below a volume threshold.
  - One 2026 guide says Resolve has no native "detect and delete pauses" feature for the edit timeline.
  - The 21.1 `GetTranscription` marks silence words as '(...)', which a skill can use to compute cut lists.
  - — [davinciresolveclub, Remove Silence](https://davinciresolveclub.com/remove-silence-davinci-resolve/); [PremiereCopilot](https://www.premierecopilot.com/en/blog/remove-silence-davinci-resolve) (via search summary); [21.1 .pyi](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/DaVinciResolveScript.pyi)
- **Resolve 20 AI tools:** AI IntelliScript, AI Animated Subtitles (captions animate in sync with words, from transcription data), AI Multicam SmartSwitch, AI Audio Assistant (auto-mix) and AI Dialogue Matcher. **Free vs Studio tiering is contested:**
  - Key Code Media lists Animated Subtitles, Audio Assistant and Dialogue Matcher as Studio.
  - Two other sites claim IntelliScript, Animated Subtitles, SmartSwitch and Audio Assistant are in Free.
  - These are unverified against Blackmagic's comparison chart.
  - — [Key Code Media](https://www.keycodemedia.com/whats-new-in-davinci-resolve-20/); [openyourais](https://openyourais.com/blog/davinci-resolve-20-ai-features-production-workflow-breakdown/); [CineD Resolve 20](https://www.cined.com/davinci-resolve-20-released-with-handful-of-ai-assisted-features/) (via search summary)
- **Resolve 21 additions:** AI IntelliSearch (objects, dialogue keywords, faces), CineFocus, Speech Generator, face retouch, faster transcription, improved subtitle word timing, and subtitle search and replace. One source says the new AI tools appear limited to Studio. — [Neowin](https://www.neowin.net/news/davinci-resolve-21-lands-with-hollywood-level-photo-feature-and-massive-ai-upgrades/); [Broadcast Now](https://www.broadcastnow.co.uk/tech-innovation/blackmagic-adds-ai-search-and-voice-creation-in-davinci-resolve-21/5216037.article) (via search summary)
- **API-reachable AI ops:**
  - TimelineItem: `CreateMagicMask`, `RegenerateMagicMask`, `Stabilize`, `SmartReframe`.
  - Timeline: `DetectSceneCuts`, `CreateSubtitlesFromAudio`, `Get/SetVoiceIsolationState`, `NormalizeAudioLevel` (21.1).
  - Dialogue Leveler properties on TimelineItem (21.1).
  - MediaPoolItem/Folder: `TranscribeAudio(useSpeakerDetection)`, `GetTranscription` (21.1), `PerformAudioClassification`, `AnalyzeForIntellisearch`, `RemoveMotionBlur`.
  - Project: `GenerateSpeech`.
  - Async status pollers (21.1.1).
  - — [21.1 .pyi](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/DaVinciResolveScript.pyi)
- **Hardware (relevant to RTX 4060 8 GB / 16 GB RAM):**
  - Resolve 21 baseline on Windows is 16 GB RAM (32 GB with Fusion) and a 4 GB VRAM GPU with CUDA 12.8 / OpenCL 1.2.
  - **Advanced AI tools reportedly require 16 GB GPU memory on Windows/Linux.** Background rendering reportedly needs 32 GB RAM and 12 GB VRAM.
  - NVIDIA Studio driver 581.57+ is cited by the Blackmagic forum thread, but a third-party guide says 570.65.
  - — [Blackmagic Forum, Release of DaVinci Resolve Studio 21](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=234676); [davinciresolveclub requirements](https://davinciresolveclub.com/davinci-resolve-system-requirements-2026/); [ifilmthings](https://ifilmthings.com/davinci-resolve-system-requirements/); [clipverdict](https://clipverdict.com/davinci-resolve-system-requirements/) (via search summary)

### Inferences
- With 8 GB VRAM, some Resolve 21 "advanced AI" features may refuse to run or run slowly even in Studio. The README notes API calls return False when "minimum system requirements of the function are not satisfied". The skill should therefore do heavy analysis outside Resolve: local Whisper or faster-whisper with an Arabic-capable model, plus ffmpeg silence detection. Resolve then only receives the edit decisions.
- For Syrian-dialect Arabic, Resolve's built-in transcription is at best via the extended Extras package (Studio). An external Whisper large-v3 or large-v3-turbo pass (as AutoSubs does) is more predictable and works on Free.

### Gaps
- Could not access Blackmagic's official Free vs Studio feature chart for 20/21, so the tiering of Animated Subtitles, Audio Assistant and Music Remixer is unresolved.
- The exact list of AI tools gated by the 16 GB VRAM requirement was not found.
- No source confirms whether "Music Remixer" or "Detect Silence" changed in 21.x.

## Q8. Arabic text (RTL, connected letters) in Resolve titles and subtitles

### Takeaway
Text+ has officially supported RTL and combined glyphs **since Resolve 17.4**. In practice users report needing **Direction = Reverse Horizontal** and Fusion's Character Level Styling for fine control. The subtitle track has a long-standing bug where **Arabic disappears when stroke > 0**. No 2025–2026 source confirms full fixes for mixed Arabic/Latin bidi ordering. Pre-shaping tools (Arabic reshaper plus bidi) are the common fallback for renderers that don't shape.

### Cited Findings
- **RTL in 17.4:** a forum thread titled "[done in 17.4] Add support for RTL languages" quotes the 17.4 notes: Text+ support for combined glyphs, right-to-left text and vertical layouts. A moderator notes per-character controls aren't reachable in the Edit page, but Fusion's "Character Level Styling" modifier can be used. — [Blackmagic Forum t=147194](https://forum.blackmagicdesign.com/viewtopic.php?f=33&t=147194) (via search summary)
- A user fix for Arabic in Text+ is to set **Direction → Reverse Horizontal**. Simply flipping the text reverses words and leaves letter direction wrong. — [Blackmagic Forum, Right-to-Left text direction in titles](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=142463); [Left to right Arabic error](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=149979) (via search summary)
- **Subtitle stroke bug:** Arabic subtitle captions vanish when stroke > 0 and reappear at 0. This was reported in the 18 public beta, a 2022 reply said it was unchanged, and a 2026 subtitle guide repeats the advice. — [Blackmagic Forum, Fix Arabic and the RTL fonts' issue](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=91891); [tryuncle subtitles guide, updated for 21.0.1](https://tryuncle.com/learn/davinci-resolve/subtitles) (via search summary)
- Older reports: Arabic and Hebrew SRT import and subtitle bugs in Resolve 15/16 on Windows. — [Blackmagic Forum, Resolve 15 Subtitles doesn't support Arabic](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=74427) (via search summary)
- A secondary source says full RTL layout (punctuation, numerals, mixed Arabic-Latin ordering) isn't fully handled, and the Resolve UI has no Arabic localisation. — (via search summary for "Resolve transcription Arabic"; underlying URLs not individually identified)
- AutoSubs ships a `font_fallback.lua` module "for non-Latin scripts" but documents no RTL handling. — [AutoSubs Resolve-Integration README](https://github.com/tmoroney/auto-subs/blob/main/Resolve-Integration/README.md)

### Inferences
- The skill should set Arabic text in titles through Text+ (Fusion) with an Arabic-capable font and test Direction settings. It should avoid strokes on subtitle-track captions, or burn captions in as Text+ instead. Mixed Arabic/English (e.g., "OLL", "PLL", cube notation) should be visually checked, or isolated with Unicode bidi marks (RLM/LRM).
- When text is injected via Fusion `StyledText`, the proper Unicode logical-order Arabic string should be passed first. Only fall back to pre-shaped or reversed text if rendering is broken on his version.

### Gaps
- No 2025–2026 primary source (release notes or manual) confirming Arabic shaping and bidi fixes in Resolve 20 or 21 Text+ or subtitles.
- No test data for Syrian-dialect transcription accuracy in Resolve's extended models.
