# Drive Resolve edits through timecoded marker plans

The skill should **plan the edit, not try to perform it.** Claude analyses the recording on the user's own PC: faster-whisper word timestamps, silence and motion maps, and timestamped contact sheets it can look at. From that it writes one validated `edit_plan.json`. That file is turned into an Arabic (right-to-left) edit sheet, a Resolve **marker EDL** and an **SRT** caption file. All three work the same on DaVinci Resolve Free and Studio, with no scripting and nothing installed.

That design is forced by a change in September 2026. **Resolve 21.1 moved Python and external scripting to the US$295 Studio edition, and added a built-in MCP server for Claude Code that is also Studio-only.** Free users are left with an undocumented, sandboxed Lua path, and the sources disagree about it. So live control (placing B-roll on V2, adding transitions, fades, and markers with notes) is an upgrade for Studio 21.1+. A pre-built FCPXML timeline is a middle option, used only after a one-time import test on his machine.

Arabic is the main technical risk at every step:
- Whisper large-v3 scored about **59% word error rate (WER)** on Syrian-accented speech in one 2026 benchmark.
- In another study it produced no English words at all when speakers mixed Arabic and English.
- Resolve has no Arabic auto-caption language, and a long history of broken Arabic text rendering. One of his own uploads was hit by this.

So the skill should tie every decision to word timing, not exact wording, and render Arabic text outside Resolve.

Real data on retention is thin: two one-minute MrBeast cut counts, a 2014 study of online-course videos, and Netflix subtitle specs. Most other numbers are vendor rules of thumb, so the skill should present them as starting defaults and tune them against his own YouTube Studio "typical" retention.

For B-roll and SFX, four free APIs (Pexels, Pixabay, Coverr, Freesound) support a flow of search → show him → download only after his OK. That fits his "nothing downloaded without my OK" rule.

The first thing the skill must ask is **his Resolve edition and exact version**.

## Resolve 21.1 moved scripting and MCP behind a US$295 Studio licence

As of 22 October 2026 the current release is **DaVinci Resolve 21.1.1**. Its readme is dated 1 October and warns that projects opened in it can no longer be opened in 20.3.2 ([Blackmagic readme, via search summary](https://www.blackmagicdesign.com/support/content/readme/dfbb6e4233c144d1b328c109c7ebc11e)).

The release that matters is 21.1, shipped around 7–8 September 2026 ([Newsshooter](https://www.newsshooter.com/2026/09/07/blackmagic-design-davinci-resolve-21-1/)). Its official scripting changelog:
- Drops Python 2.
- Adds the first **transition API (`TimelineItem.AddTransition`)**.
- Adds get and set for clip fades, speed and native audio properties.
- Adds `NormalizeAudioLevel`.
- Adds **`MediaPoolItem.GetTranscription`**, which returns segments with a start and end timecode for each word and marks silences as "(...)" ([CHANGELOG mirror](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/CHANGELOG.md); [DaVinciResolveScript.pyi mirror](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/DaVinciResolveScript.pyi)).

21.1.1 added asynchronous status checks for transcription, scene-cut detection, Smart Reframe, subtitle creation and Quick Export ([Digital Production](https://digitalproduction.com/2026/10/06/davinci-resolve-21-1-1/)).

The documentation itself changed in three ways ([21.1 README mirror](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/README.md)):
- The API listing now lives in a typed stub, `DaVinciResolveScript.pyi`.
- `SetProperty` is deprecated in favour of `SetProperties({...})`, which applies all values or none.
- Resolve now ships its own **Python 3.14 interpreter, `ResolvePython.exe`**. It imports the scripting module with no environment variables, but does not support pip.

The headline change is the split between editions. Blackmagic's stated reason: "We have moved the ability to script in Python to the Studio version. The Python API was being used to hack studio features into the free version." On Free 21.1, Workspace > Scripts "ignores .py files entirely, with no warning dialog, no syntax error and no console log" ([xere.my](https://xere.my/journal/davinci-resolve-21-1-free-python-scripting-removed-lua-benchmark/); [CineD](https://www.cined.com/davinci-resolve-21-1-released-ai-assistant-integration-via-mcp-individual-hdr-trims-and-python-scripting-moves-to-studio/)). External scripting means anything driving Resolve from outside: a terminal, an editor, or any MCP server. It is set under Preferences > System > General, and in 21.1 it exists only "in DaVinci Resolve Studio" ([21.1 README mirror](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/README.md)). Studio costs a one-time **US$295** ([CineD](https://www.cined.com/davinci-resolve-21-1-released-ai-assistant-integration-via-mcp-individual-hdr-trims-and-python-scripting-moves-to-studio/)).

| His setup | Python | Lua | External scripting / MCP | What the skill can do |
|---|---|---|---|---|
| Free ≤21.0.x | Inside Resolve only (Console, Workspace > Scripts) | Inside Resolve | No | Files. Optionally a community in-app Python bridge. Warn him that upgrading to 21.1 silently breaks Python scripts. |
| Free 21.1+ | Removed | Sandboxed: no `io`, `os.execute`, `require`, `ffi` | No | Files (marker EDL, SRT, FCPXML/OTIO). Optionally an experimental Lua "mailbox" bridge. |
| Studio 21.1+ | Full, plus bundled `ResolvePython.exe` | Full | Yes, plus Blackmagic's built-in MCP | Files, plus live placement of clips, markers with notes, transitions and fades |

### The notes conflict on whether Lua still runs on Free 21.1

This is the sharpest disagreement in the research.

**The "it's gone" side:**
- Puget Systems reports that Blackmagic "has entirely removed scripting support from the free edition" and recommends staying on 21.0 ([Puget Systems](https://www.pugetsystems.com/blog/2026/09/10/how-davinci-resolve-free-v21-1-scripting-changes-affect-puget-bench/)).
- ProVideo Coalition says Free keeps console-only scripting ([ProVideo Coalition](https://www.provideocoalition.com/davinci-resolve-21-1-is-a-huge-update/)).
- The leading community MCP calls Python in the Free Console "unconfirmed" ([samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp)).

**The "Lua still runs" side:**
- saadk408's project measured Free build 21.1.0.17 and reports that "Workspace > Scripts lists and runs Lua files". Inside that Lua, `io`, `os.execute`, `require`, `ffi` and `debug` are missing ([saadk408/davinci-resolve-lua-mcp](https://github.com/saadk408/davinci-resolve-lua-mcp)).
- AutoSubs rebuilt its Resolve integration for the 21.1 sandbox and works on Free again. It uses a "file mailbox": an outside program writes `request.lua`, Lua runs it with `loadfile`, and Lua replies through `fusion:SetPrefs` + `SavePrefs`, which the outside program reads back from `Fusion.prefs` ([AutoSubs Resolve-Integration README](https://github.com/tmoroney/auto-subs/blob/main/Resolve-Integration/README.md)).

**Position taken:** sandboxed Lua does run from Workspace > Scripts on Free 21.1. Two independent, working, code-level confirmations outweigh a one-line summary. But the skill must treat this path as fragile:
- "Blackmagic documents neither this Lua host nor its sandbox, so a point release can change what works."
- Windows support is "experimental" and was measured on macOS.
- The bridge has to be relaunched after every Resolve start.
- Mailbox bridges need ASCII-only folder paths. That matters if his Windows user folder name contains Arabic characters ([saadk408](https://github.com/saadk408/davinci-resolve-lua-mcp); [emircbngl/davinci-resolve-mcp-free](https://github.com/emircbngl/davinci-resolve-mcp-free)).

A smaller conflict covers the period before 21.1. A Blackmagic forum answer said Free could script only through the built-in Console ([Blackmagic Forum](https://forum.blackmagicdesign.com/viewtopic.php?f=12&t=230652)). Yet several community bridges ran Python from Workspace > Scripts on Free ≤21.0. The practical answer is that Free ≤21.0 ran in-app Python, and 21.1 ended that.

### The built-in MCP is official but thinly documented

**How setup works:** Studio 21.1 adds **File > Setup AI Assistants**. Another guide words it "File → Set Up AI Assistance". It detects installed assistants (Claude, Claude Code, ChatGPT Codex), writes their MCP configuration, and asks for the assistant to be restarted. One guide says it also needs External scripting set to Local, or "setup fails silently" ([YMCinema](https://ymcinema.com/2026/09/17/davinci-resolve-21-1-mcp-ai-assistants-control-edit/); [Digital Production](https://digitalproduction.com/2026/09/08/resolve-21-1-adds-mcp-and-finally-gets-presets/)).

**What it covers:** media organisation, multicam switching, audio, markers, transcripts, renders and LUTs. Colour wheels, curves and masks are not exposed.

**How many tools it has is disputed:**
- One report says the assistant gets about **14 general tools** and does most of its work by writing Python against the scripting API ([scenepaper](https://scenepaper.com/blog/davinci-resolve-21-1-ai-agents-2026); [explainx](https://www.explainx.ai/blog/davinci-resolve-21-1-mcp-server-ai-agents-2026)).
- byteiota counts **about 88 tools** ([byteiota](https://byteiota.com/?p=22448)).
- No Blackmagic primary text was found that lists the tools or the transport.

**Security:** the same coverage warns that its scripts run with the assistant's disk and network access. His PC was once infected through an AI agent's command, so two things follow:
- Resolve's setup step rewrites Claude Code's MCP configuration. That is itself a change needing his explicit OK.
- Any Python the MCP generates should be shown to him before it runs.

Claude Desktop and Claude Code are also separate MCP clients. Configuring one does not prove the other can reach Resolve ([Vagon](https://vagon.io/blog/how-to-use-davinci-resolve-with-claude-mcp-computer-use)).

**Community servers:** there are now 15+ Resolve MCP servers.
- The clear leader is **samuelgursky/davinci-resolve-mcp**: 3,697 stars, pushed 19 Oct 2026. It offers a 37-tool compound server, a 390-tool granular server, and an 18-tool offline server. Its optional dependencies are heavy: openai-whisper, open_clip, transformers ([repo](https://github.com/samuelgursky/davinci-resolve-mcp)). Its Free in-app bridge now only works up to 21.0.x, and it calls its own output "a first-pass assembly", not editorial judgement.
- **AutoSubs** (~4.4k stars, MIT) ships a Windows installer, runs Whisper locally, handles Arabic via moonshine-tiny-ar and Cohere, and works on Free 21.1 through the mailbox ([AutoSubs](https://github.com/tmoroney/auto-subs)).
- Prior art for this exact idea: a Codex skill built on the official 21.1 MCP ([Yasei-no-otoko](https://github.com/Yasei-no-otoko/codex-skill-davinci-resolve-edit)), and lordhoell's server, which bundles a Claude Code skill ([lordhoell](https://github.com/lordhoell/davinci-resolve-mcp)).
- Many others are verified on macOS only, or predate 21.1 ([barckley75](https://github.com/barckley75/resolve-claude-mcp); [flamexnreal](https://github.com/flamexnreal/davinci-resolve-ai-bridge-mcp); [hiteshK03](https://github.com/hiteshK03/davinci-resolve-mcp)).
- Several expose `run_lua` or `execute_resolve_code`, meaning arbitrary code with his user rights.

**Python version (another conflict):** samuelgursky calls Python 3.10–3.12 the lowest-risk range. Tooflex insists on 3.10/3.11, and warns that uv-managed Python crashes `fusionscript.dll` on Windows ([Tooflex](https://github.com/tooflex/davinci-resolve-mcp)). On Studio 21.1 the bundled `ResolvePython.exe` avoids this argument for scripts that control Resolve. The machine-learning tools stay in his existing Python.

**Position taken:** the baseline needs no third-party server. On Studio, the built-in MCP or a short `ResolvePython.exe` script has fewer moving parts than any community project.

### The API can place clips and markers but cannot animate

On Studio 21.1+ the API covers nearly every row of a "put X at second Y" plan. The gaps are animation, splitting clips, and title text ([20.2 README](https://github.com/thomjiji/dri/blob/main/READMEs/20.2_README.txt); [21.1 .pyi](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/DaVinciResolveScript.pyi)).

| Edit action | API route (Studio 21.1+) | Limit or workaround |
|---|---|---|
| B-roll on V2 at second *t* | `ImportMedia`, `AddTrack("video")`, `AppendToTimeline([{mediaPoolItem, startFrame, endFrame, trackIndex, recordFrame, mediaType}])` | `recordFrame` appears to be an absolute timeline frame, while `AddMarker`'s `frameId` is relative to the timeline start. Convert with `GetStartFrame()` and verify on his build. |
| Marker carrying the instruction | `Timeline.AddMarker(frameId, color, name, note, duration, customData)` | 16 colours. `customData` is hidden in the UI, which makes it ideal for a plan-row ID. |
| Punch-in zoom | `SetProperties({"ZoomX":1.2,"ZoomY":1.2})` on its own segment | Static only. No Edit-page keyframes and no blade-at-frame. Animated zooms need a Fusion comp or `.setting` macro. |
| Transition | `AddTransition({type, category, position, alignment, duration})` | 21.1+ only. Only `'Cross Dissolve'` is documented as a type string. |
| SFX | `AppendToTimeline` with `mediaType: 2` + `trackIndex`, or `InsertAudioToCurrentTrackAtPlayhead` | Audio-only track indexing was fixed in 20.2.2 |
| Fades, speed, freeze | `SetFades({FadeIn, FadeOut})`, `SetSpeed({Percentage: 0})` | 21.1+ |
| Text pop-up | `SetCurrentTimecode`, then `InsertFusionTitleIntoTimeline(name)`, then Fusion `StyledText` | No text argument. One server calls setting the text "best effort" ([flamexnreal](https://github.com/flamexnreal/davinci-resolve-ai-bridge-mcp)). Arabic rendering is a risk. |
| Captions | `CreateSubtitlesFromAudio({...})` | No Arabic language constant in the 20.2 or 21.1 lists |

There is no API for colour wheels, curves, masks or Fairlight automation. The workarounds are Fusion comps, interchange files, or markers that a human follows.

**Hardware limit:** Resolve 21's Windows baseline is 16 GB RAM (32 GB with Fusion) and a 4 GB GPU. Its **advanced AI tools reportedly need 16 GB of GPU memory**, and API calls return False when "minimum system requirements of the function are not satisfied" ([Blackmagic Forum](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=234676); [davinciresolveclub](https://davinciresolveclub.com/davinci-resolve-system-requirements-2026/); [21.1 README](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/README.md)). With an 8 GB RTX 4060 and 16 GB RAM, heavy analysis belongs outside Resolve. Resolve should only receive the decisions.

## A marker EDL works everywhere, while FCPXML needs a one-time import test

Resolve accepts four file routes that matter here, and they are not equally reliable.

### Marker EDL: the one route proven on Free and Studio

The **marker EDL** is a one-frame CMX event followed by Resolve's own annotation line, ` |C:ResolveColorX |M:name |D:frames`. It is imported by right-clicking the timeline and choosing **Timelines > Import > Timeline Markers from EDL**. It is the only marker route confirmed to work on Free 21.1 without scripting ([SubtitleEdit format class](https://github.com/SubtitleEdit/subtitleedit/blob/HEAD/src/libse/SubtitleFormats/DaVinciResolveMarkerEdl.cs); [editingtools.io](https://editingtools.io/guides/convert-livenotes-to-resolve-marker)).

Rules taken from real Resolve exports and from tools that ship this format:
- Resolve places each marker at the **record-in timecode read as an absolute timeline position**, so times must include the timeline start (normally 01:00:00:00).
- Every event line ends in two spaces, and every annotation line starts with one.
- Duration lives only in `|D:`. The event itself stays one frame long ([vodcue](https://github.com/wdominik/vodcue/blob/HEAD/src/formats/resolve_edl.rs); [VyacheArt example.edl](https://github.com/VyacheArt/edl-to-youtube/blob/HEAD/example.edl)).
- Event numbers have three digits, so **at most 999 markers**.
- **Only one marker per frame** survives.
- Files use CRLF line endings and UTF-8 ([Aagedal](https://github.com/aagedal/Aagedal-Media-Converter/blob/HEAD/Aagedal%20Media%20Converter/Logic/Conversion/StitchMarkerExport.swift)).
- Resolve has no native CSV marker import; CSV must be converted to this format first ([editingtools.io](https://hu.editingtools.io/guides/convert-csv-to-resolve-marker)).
- There is no separate note field, and a vendor warns that "special characters" may fail.

So the skill should write short ASCII codes in the marker name (`B03 cube closeup`) and keep the full Arabic instruction on the sheet under the same code. The research generated and checked this template locally (30 fps, 01:00:00:00 start). It has not been test-imported into Resolve:

```
TITLE: EP42_v3
FCM: NON-DROP FRAME

001  001      V     C        01:00:12:15 01:00:12:16 01:00:12:15 01:00:12:16  
 |C:ResolveColorBlue |M:B03 cube closeup |D:90

002  001      V     C        01:00:20:00 01:00:20:01 01:00:20:00 01:00:20:01  
 |C:ResolveColorYellow |M:Z05 zoom 120 |D:15
```

Once imported, he moves through the markers with Shift+Down / Shift+Up (confirmed by third parties only) and sees them all in the Edit Index ([Miracamp](https://www.miracamp.com/learn/davinci-resolve/how-to-flip-between-markers); [Tutkit](https://tutkit.com/en/text-tutorials/1788-davinci-resolve-efficient-use-of-flags-and-markers)).

**Marker colours** are team-defined; no industry convention exists. The skill should save its own legend:
- Blue = B-roll
- Yellow = zoom
- Green = SFX
- Purple = transition
- Cyan = caption or pop-up
- Red = fix
- Sand = reserved for chapters

Reserving one colour for chapters matters because Resolve's "Chapters from markers" export option takes every marker of one chosen colour ([MediaZilla](https://support.mediazilla.com/en/articles/12143932-working-with-chapters-in-davinci-resolve)).

### FCPXML: the best format for placing clips, but unproven on his build

**FCPXML** is the best single file for actually *placing* things. It carries absolute `file:///` media paths, puts connected clips at exact rational times (lane 1 above the main clip, lane −1 below), and supports `adjust-transform`. It imports via File > Import > Timeline in both editions.

**Version support:**
- Target **1.10**.
- Resolve 17 rejected 1.10 ([Blackmagic Forum](https://forum.blackmagicdesign.com/viewtopic.php?p=806873)).
- A hands-on test imported 1.11 into Resolve 19.1 Studio ([creativevideotips](https://creativevideotips.com/tutorials/final-cut-pro-to-davinci-resolve-xml-workflow)).
- auto-editor now writes 1.11 by default for Resolve ([auto-editor export skill](https://github.com/WyattBlue/auto-editor/blob/HEAD/skills/auto-editor-export/SKILL.md)).
- One exporter claims, unverified, that Resolve 21 reads up to 1.14 ([yt-cartell-studio](https://github.com/gitkalenyuk/yt-cartell-studio-source/blob/HEAD/internal/nle/fcpxml.go)).
- An unsupported version fails with "Invalid XML" ([cutsio](https://cutsio.com/blog/fix-invalid-xml-fcp-davinci)).

**The rule that trips generators:** connected clips and markers inside a clip are timed in the **parent clip's source time**, not timeline time ([nicknoonan example](https://github.com/nicknoonan/fcpxml/blob/HEAD/src/parser/example_complicated.fcpxml); [OpenFCPXMLKit sample](https://github.com/TheAcharya/OpenFCPXMLKit/blob/HEAD/Tests/FCPXML%20Samples/FCPXML/24With25Media.fcpxml)). The simplest way around it is to make the whole voice recording one spine clip with `start="0s"`. Then a child's `offset` simply equals "seconds into the video".

Windows paths must be percent-encoded file URLs. For example, `سوق دمشق #1.mp4` becomes `%D8%B3...%20%231.mp4`, because Resolve does not resolve relative URLs ([auto-editor pathToUri](https://github.com/WyattBlue/auto-editor/blob/HEAD/src/util/fun.nim)).

**The notes conflict on what survives import:**
- An exporter built for Resolve says Resolve keeps only the first keyframe value on stills ("a Ken Burns move would freeze"), so it writes static transforms only ([yt-cartell-studio](https://github.com/gitkalenyuk/yt-cartell-studio-source/blob/HEAD/internal/nle/fcpxml.go)).
- A forum user reported transforms and keyframes surviving a round trip, with spatial conform "messed" ([Creative COW](https://creativecow.net/?p=1860288)).
- An older forum report says Resolve "has never accepted" FCPX markers ([Blackmagic Forum](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=82115)).

**Position taken:** the FCPXML writer uses only static `adjust-transform scale` values. Every marker is also sent in the marker EDL.

### OTIO, and formats to avoid

**OTIO** has imported and exported natively in Free and Studio since 18.5, and clip markers were added in 18.6.5 ([Newsshooter](https://www.newsshooter.com/2023/04/16/davinci-resolve-18-5-announced/); [RedShark](https://www.redsharknews.com/blackmagic-releases-davinci-resolve-18.6.5)). It is easier to generate correctly than FCPXML: tracks padded with gaps map one-to-one to Resolve tracks. But it has no standard way to express zooms. A single community source warns that malformed OTIO can corrupt a project, so test imports belong in a throwaway project ([BlueMediaRiot](https://github.com/BlueMediaRiot/training-video-antigravity/blob/HEAD/.agents/skills/otio-timeline/resolve_compatibility.md)).

**Avoid:**
- **Clip EDLs.** The official OTIO adapter refused a second video track outright ("Only a single video track is supported"). Clip EDLs carry no file paths, and Resolve matches clips by reel name and timecode, which is fragile for phone or stock clips that all start at 00:00:00:00 ([otio-cmx3600-adapter](https://pypi.org/project/otio-cmx3600-adapter/); [Blackmagic Forum](https://forum.blackmagicdesign.com/viewtopic.php?p=248494)).
- **AAF and DRT.** AAF is binary and hard to debug; DRT has no public spec.

### The notes disagree on the default deliverable

The interchange research recommends shipping "`edit_plan.fcpxml` + `markers.edl`" as the pair. The skill-design research rates pre-placed B-roll timelines "low–medium" reliability for a non-coder, because of relinking, frame-rate and start-timecode mismatches, and because an imported timeline is a *new* timeline he must merge into his own edit.

**Position taken:** both are right about different things. FCPXML is the best *placement* format, but placement is optional. The user asked to be told *which second* to put each thing. Markers plus the sheet do exactly that, with no merge step. FCPXML becomes an opt-in "B-roll and SFX layer" once a smoke test on his build proves the lane-to-track mapping.

### Subtitles, and why Arabic text should be rendered outside Resolve

SRT import into a subtitle track works on Free (File > Import > Subtitle). Match the timeline frame rate first to avoid drift ([GoTranscript](https://gotranscript.com/blog/create-subtitles-davinci-resolve-import-srt-timing-export)). The sources conflict on other subtitle formats: one lists SRT/VTT/XML/TTML, another lists SRT or FCPXML ([HappyScribe](https://help.happyscribe.com/en/articles/6087119-how-to-import-captions-in-davinci-resolve); [Rev](https://www.rev.com/blog/how-to-add-captions-and-subtitles-to-davinci-resolve-studio)).

Arabic is the real problem.

**Evidence that Arabic rendering is broken or awkward:**
- Text+ officially gained right-to-left and combined-glyph support in 17.4, but users reported letters staying disconnected ([Blackmagic Forum](https://forum.blackmagicdesign.com/viewtopic.php?f=33&t=147194); [Blackmagic Forum](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=143060)).
- One fix is to set Direction to Reverse Horizontal ([Blackmagic Forum](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=142463)).
- **Arabic subtitles vanish when stroke > 0**, and a 2026 guide still repeats that advice ([Blackmagic Forum](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=91891); [tryuncle](https://tryuncle.com/learn/davinci-resolve/subtitles)).
- His own video-maker skill records that plain Resolve text came out disconnected and backwards and broke one of his uploads.

**Evidence that it may now work (all unverified):** one forum reply claims Arabic arrived in v20 ([Blackmagic Forum](https://forum.blackmagicdesign.com/viewtopic.php?f=33&t=212513)).

**A second conflict, on burning captions in:** the interchange notes call ffmpeg/libass a safe way to burn shaped Arabic in. The retention notes cite a 2025 FFmpeg ticket showing the same class of Arabic bug in libass ([FFmpeg trac](https://ffmpeg.org/pipermail/ffmpeg-trac/2025-April/073389.html)).

**Position taken:** treat both Resolve and libass as unproven for Arabic until a test passes. The reliable path has two parts:
1. Upload the SRT to YouTube as closed captions. This takes rendering out of Resolve entirely, and a Discovery Digital Networks test measured **+7.32% views** for uploaded captions ([3Play Media](https://www.3playmedia.com/blog/studies-find-captions-improve-engagement)).
2. Pre-render stylised Arabic pop-ups as transparent PNGs from the browser engine his video-maker skill already uses. That engine shapes Arabic correctly, and Resolve then only carries a picture.

Resolve's own auto-captioning cannot help either. Neither the 20.2 nor the 21.1 API lists Arabic. Third-party guides say an "Extended AI Transcription" Extras package for Studio adds about 43 languages including Arabic, but that is unconfirmed ([21.1 .pyi](https://github.com/WheheoHu/bmd_doc/blob/main/_README_API/21_1_1/DaVinciResolveScript.pyi); [davinciresolveclub](https://davinciresolveclub.com/transcribe-audio-davinci-resolve/)).

### Timecode math must run in integer frames at the true frame rate

Transcript seconds are real time. The rule is:
1. Convert seconds to frames with the exact rational rate: `frame = round(sec × 30000/1001)` for "29.97".
2. Add the timeline start and any offset of the voice clip on the timeline.
3. Only then format as a timecode label.

Getting this wrong is costly:
- At 29.97 non-drop, 600 s of real time is 17,982 frames, which is labelled **01:09:59:12**, about 18 frames behind the wall clock. That is enough to put a zoom on the wrong word.
- Using 30 instead of 30000/1001 drifts about 1.8 s per 30 minutes.
- In drop-frame, 01:00:00;00 is frame 107,892 at 29.97, not 108,000 ([auto-editor parseSMPTE](https://github.com/WyattBlue/auto-editor/blob/HEAD/src/exports/fcp11.nim); [Aagedal DF fixture](https://github.com/aagedal/Aagedal-Media-Converter/blob/HEAD/Aagedal%20Media%20ConverterTests/Fixtures/StitchMarkers/2997.edl)).

The research checked this converter against OpenTimelineIO's `to_timecode` at eight frame rates ([OpenTimelineIO](https://pypi.org/project/OpenTimelineIO/)). It belongs in `scripts/timecode.py`:

```python
from fractions import Fraction
def seconds_to_frame(sec, rate):            # rate = Fraction(30000,1001) for 29.97
    return round(Fraction(str(sec)) * rate)  # use floor for cut-ins that must not precede a word
def frames_to_tc(frames, base, drop=False):  # base = nominal fps (30 for 29.97)
    if drop:
        d = 2 if base == 30 else 4
        per10 = base*600 - d*9; per1 = base*60 - d
        tens, rem = divmod(frames, per10)
        frames += d*9*tens + (d*((rem - d)//per1) if rem > d else 0)
    ff = frames % base; s = frames // base
    return f"{s//3600:02d}:{s//60%60:02d}:{s%60:02d}{';' if drop else ':'}{ff:02d}"
```

FCPXML wants the same frames as rationals: 12.5 s at 29.97 becomes `375375/30000s`.

Two more rules:
- The same 01:00:00:00 offset applies in reverse when reading analytics. A YouTube Studio retention timestamp equals the timeline timecode minus one hour.
- The probe step must flag variable frame rate (when `r_frame_rate` ≠ `avg_frame_rate`). Variable frame rate breaks the seconds-to-frames mapping, and the fix (a constant-frame-rate transcode) needs his OK.

## Local transcription and contact sheets let Claude "watch" a faceless video

### Arabic speech recognition: keep faster-whisper large-v3

Claude sees images, not video ([Claude vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)). So the pipeline turns the recording into two things Claude can read: a transcript with word timestamps, and timestamped contact sheets.

**Keep faster-whisper large-v3, which he already runs.** The evidence:
- **Dialect error rates are high everywhere.** Whisper V3 scored about **58.9% WER on Syrian speakers**, against 26.0% for Saudi, in the 2026 Bulbul dataset (accented formal Arabic) ([Bulbul](https://arxiv.org/pdf/2608.21950)). Across 14 systems, Levantine WER ranged from about 23.5 to 51.8 ([Arab Voices](https://arxiv.org/pdf/2601.13319)).
- **Mixed Arabic and English is a known weakness.** On mixed input, whisper-large-v3 produced **no English words in any decoding setting** and sometimes translated instead of transcribing ([Casablanca](https://arxiv.org/pdf/2410.04527)). Expect "F2L", "PLL" and "OLL" to come out in Arabic script, translated, or dropped.
- **Turbo is worse on dialects.** One community fine-tune's model card reports the zero-shot turbo model at 65% WER on Egyptian and 61.1% on Gulf Arabic ([oddadmix model card](https://huggingface.co/oddadmix/whisper-large-v3-turbo-arabic-dialectal)).
- **Newer Arabic-specialised models give text but no word timing.** **Cohere Transcribe Arabic** (7 July 2026, Apache-2.0) leads the Arabic leaderboard at 25.87 average WER, but has no word timestamps ([Hugging Face blog](https://huggingface.co/blog/CohereLabs/cohere-transcribe-arabic-07-2026-release); [Friendli](https://friendli.ai/models/CohereLabs/cohere-transcribe-arabic-07-2026)). Qwen3's forced aligner excludes Arabic ([Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR)).

What follows: **word timestamps matter more than exact words.** A noisy dialect transcript still gives usable word boundaries for cuts and zooms, and Claude can infer meaning from imperfect text plus frames.

The stack:
1. **Transcribe** with `language="ar"`, `word_timestamps=True` and `vad_filter=True` ([faster-whisper](https://github.com/SYSTRAN/faster-whisper)).
2. **Optionally tighten word edges** with WhisperX's default Arabic aligner, `jonatasgrosman/wav2vec2-large-xlsr-53-arabic`. In current code it maps Latin-script terms to a wildcard instead of dropping them ([WhisperX alignment.py](https://raw.githubusercontent.com/m-bain/whisperX/main/whisperx/alignment.py)). WhisperX itself warns that Whisper's native timestamps "can be inaccurate by several seconds" ([WhisperX](https://github.com/m-bain/whisperX)).
3. **Fix cubing terms** in a post-pass that maps Arabic-script spellings back to Latin terms, using the `glossary.md` his video-maker skill already keeps.
4. **If the video was scripted with video-maker**, align the approved script itself to the audio. That gives correct text with correct timing. This is an inference, not tested here.

**Model licences matter under his rules.** The default model of ctc-forced-aligner, and AutoSubs' optional MMS aligner, are **CC BY-NC 4.0** (non-commercial) ([ctc-forced-aligner](https://github.com/MahmoudAshraf97/ctc-forced-aligner); [AutoSubs](https://github.com/tmoroney/auto-subs)). The skill should exclude them on a monetised channel, the same way it excludes non-commercial footage.

**Not needed:** speaker diarization (he is the only speaker), and stable-ts, which was archived on 30 May 2026 ([stable-ts](https://github.com/jianfch/stable-ts)).

### Silence and retake detection

Silence cutting is a solved threshold problem. The most usable house rules come from **video-use**, an MIT-licensed Claude Code skill ([video-use SKILL.md](https://raw.githubusercontent.com/browser-use/video-use/main/SKILL.md)):
- Silences of **400 ms or more** are the cleanest cut points.
- **150–400 ms** is a phrase boundary that needs a visual check.
- **Under 150 ms** is unsafe to cut.
- Never cut inside a word. Pad edges by 30–200 ms and put 30 ms audio fades on every cut.

**auto-editor** (v31.7.x, now a Nim binary that bundles whisper.cpp) can do this for him ([auto-editor](https://github.com/WyattBlue/auto-editor)):
- Defaults: audio threshold 0.04 and a 0.2 s margin.
- It can combine audio and motion. For example, `(or audio:0.03 motion:0.06)` keeps a silent but active solve instead of cutting it as dead air.
- `--export resolve` writes FCPXML directly.

**Retakes:** commercial retake detection (Gling, AutoCut Repeat, Descript, Selects) is driven by the transcript, but none of these tools publishes its method ([AutoCut Repeat](https://autocut.com/help-center/autocut-repeat/introducing); [Gling](https://devtoollab.com/ai-tools/gling)). Claude can do it itself. Look for near-duplicate sentences in the word-timed transcript, plus Syrian restart cues ("لا لا", "خليني عيد", a long pause, then the same opening words). Keep the last complete take by default, and send every proposed cut to him for review.

Whisper tends to drop fillers such as "يعني" and "اممم". Silero VAD gaps inside segments are a backup signal for them ([silero-vad](https://github.com/snakers4/silero-vad)).

Resolve's own options are weaker for this job. The transcript-based "Remove Silent Portions" is Studio-only. Fairlight's Remove Silence is a blunt threshold tool ([davinciresolveclub](https://davinciresolveclub.com/remove-silence-davinci-resolve/)).

### Contact sheets let Claude see the footage

The pattern:
1. Detect shots with PySceneDetect 0.7.2 or ffmpeg ([PySceneDetect](https://github.com/Breakthrough/PySceneDetect)).
2. Sample frames every 2–5 s.
3. Burn the timestamp into each frame.
4. Tile them into sheets that fit Claude's vision limits.

**Claude's vision limits** ([Claude vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)):
- Images are downscaled above about **1568 px on the long edge or ~1.15 megapixels**.
- Cost is about ⌈w/28⌉×⌈h/28⌉ tokens.
- claude.ai allows **20 images per message**.
- Accuracy drops for images under 200 px.

**Sizing for this channel:**
- A 4×4 grid of 384×216 tiles is 1536×864, or about 1,700 tokens.
- A 10–20 minute video sampled every 3–5 s needs 8–25 sheets, roughly 15–40k tokens. That is affordable.
- On near-identical hands-and-cube footage, also burn a per-tile **motion score**, so Claude can tell scramble, inspection, solve and explanation apart.

video-use adds a "timeline view" tool: a filmstrip plus waveform plus word labels for any time range. It is called **only at decision points** and reused on the rendered output for self-checks ([video-use](https://github.com/browser-use/video-use)). The skill should copy that.

### Emphasis and B-roll matching

**What vendors do:** commercial tools match B-roll to the transcript. InVideo analyses keywords and sentiment per sentence ([InVideo](https://info.invideo.io/blog/automatic-b-roll-selection-video-script-invideo)). Users control it with a density slider and minimum/maximum clip durations ([AutoCut AutoB-Roll](https://autocut.com/en/autobroll); [Submagic](https://submagic.co/features/b-roll)). Pictory shows the failure mode of literal matching: email "open rates" turned into people opening paper mail ([fast.io review](https://fast.io/resources/pictory-ai-review-2026/)). Adobe's B-Script study (110 participants) found that recommending both B-roll *position and content* made videos rated more engaging ([arXiv 1902.11216](https://arxiv.org/abs/1902.11216)).

**Zoom and SFX candidates:** compute loudness and onset peaks with librosa, snap each to the nearest word start, and let Claude decide which peaks matter by meaning. On the gaming channel, run this on a voice-only track, because explosions in the game audio will dominate otherwise.

**Searching his own B-roll library:** build a local CLIP or SigLIP 2 frame-embedding index ([Voxel51 SigLIP2](https://docs.voxel51.com/plugins/plugins_ecosystem/siglip2.html)).
- Query it in English, since the text encoders are English-centric. Claude translates the Arabic keywords.
- Test CLIP against SigLIP on his own clips. A TREC 2025 team found SigLIP2 "did not work at all" in early tests ([TREC](https://trec.nist.gov/pubs/trec34/papers/ccilab.avs.pdf)).
- Optionally, a one-off Qwen3-VL-4B captioning pass via Ollama turns each clip into searchable text ([Ollama](https://registry.ollama.ai/library/qwen3-vl)).

### What fits on his laptop

GPU stages must run **one at a time** within 8 GB. faster-whisper's README measured these figures for a large-v2-class model on an 8 GB card ([faster-whisper](https://github.com/SYSTRAN/faster-whisper)):
- fp16: about 4.5 GB VRAM.
- fp16 at batch size 8: about 6.1 GB.
- int8: about 2.9 GB.

Two benchmarks measured large-v3 on an RTX 4060 at a **real-time factor of 0.16–0.25**, meaning 0.16–0.25 s of processing per second of audio ([GigaGPU](https://gigagpu.com/whisper-large-v3-on-rtx-4060-benchmark/); [jisaku](https://jisaku.com/posts/ai-bench-faster-whisper-speed-2026)). A third page claiming 46× real time is an outlier.

| Stage | Tool | Est. time, 15-min video | GPU |
|---|---|---|---|
| Probe and 16 kHz mono WAV | ffprobe/ffmpeg | <30 s | No |
| Transcript with word timestamps | faster-whisper large-v3 (already installed) | ~2.5–4 min | ~4.5–6 GB |
| Optional re-alignment | WhisperX align, Arabic wav2vec2 | ~0.5–1.5 min (guess) | ~1–2 GB (guess) |
| Silence and motion map | auto-editor, or Silero plus frame difference | ~0.5–2 min (guess) | No |
| Shots and contact sheets | PySceneDetect + ffmpeg `fps,drawtext,tile` | ~1–2 min (guess) | No |
| Emphasis peaks | librosa RMS/onset | <30 s | No |
| B-roll index (one-off) | open_clip SigLIP2 / CLIP | Depends on library size | Yes |

The total is roughly **5–12 minutes of preprocessing**. Only the transcription step was benchmarked; the rest are estimates. faster-whisper uses CTranslate2, not PyTorch, so the B-roll index and WhisperX are a **new PyTorch install of about 2–3 GB**. Under his rules that needs explicit approval.

## Most retention numbers are heuristics, so the skill should label them

The evidence base is thin, and the skill should say so.

### Hooks: the first 30 seconds

YouTube's only official hook metric is **"Intro": the share of viewers still watching at 30 s.** It appears only for videos of 60 s or more with at least 100 views ([YouTube Help](https://support.google.com/youtube/answer/9314415?hl=en)). Vendor targets for it disagree:
- 50–70% at 30 s ([Subscribr](https://subscribr.ai/youtube-strategy/youtube-analytics-improve-video-hooks-intros)).
- 60% or more ([vidIQ](https://vidiq.com/blog/post/increase-audience-retention-youtube/)).
- One creator who analysed 63 of his own graphs found **no link** between 30-s retention and promotion ([SocialVideoPlaza](https://www.socialvideoplaza.com/en/articles/what-to-say-youtube-intro-hook)).

The leaked MrBeast production memo has disputed provenance ([NetInfluencer](https://www.netinfluencer.com/mrbeast-productions-leaked-internal-document-rosanna-pansino/)). It says "the first minute has the most loss", and places re-engagement beats at about **3:00 and 6:00** ([Daniel Scrivner summary](https://www.danielscrivner.com/how-to-succeed-in-mrbeast-production-summary/)).

### Pacing: cuts per minute

The only hard pacing data is a Tubefilter count of one minute from each of two MrBeast videos ([Tubefilter](https://tubefilter.com/2024/03/04/mrbeast-editing-style-number-of-cuts-per-video/)):
- A March 2023 video: **38 cuts/min**, an average shot of about 1.6 s.
- An early-2024 video, after he publicly slowed down: **23 cuts/min**, about 2.6 s.

Hollywood shots have shrunk from about 12 s in 1930 to about 2.5 s today ([Cutting et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3485803/)). Audiences pushed back in 2024 against loud SFX, flashing effects and non-stop cutting ([GIGAZINE](https://gigazine.net/gsc_news/en/20240403-retention-editing-beastification-may-be-end); [YPulse](https://www.ypulse.com/newsfeed/2024/04/02/young-people-are-getting-tired-of-retention-editing-on-youtube/)).

For tutorials, the best study is old but large: **6.9 million viewing sessions** of online-course (edX) videos. Shorter segments (under 6 minutes) held attention better, and hand-drawn "Khan-style" visuals beat slides and screencasts ([Guo, Kim & Rubin 2014](https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf)). Hands physically turning a cube is the cubing version of that.

Vendor advice on how often the picture should change on faceless channels conflicts:
- Every 3–5 s ([Fluxnote](https://fluxnote.io/guides/faceless-channel-retention-strategies-2026)).
- Every 5–10 s ([Air.io](https://air.io/en/youtube-hacks/advanced-retention-editing-cutting-patterns-that-keep-viewers-past-minute-8)).
- Every 10–15 s in the opening ([Gyre](https://gyre.pro/blog/how-to-improve-audience-retention-on-youtube-top-tips)).

### B-roll, zooms and SFX

**B-roll:** guides converge on holds of **2–5 s**, and a static B-roll held for **8 s** under narration "starts to drag" ([Captions.ai](https://captions.ai/blog/practical-guide-b-roll-video); [SocialRails](https://socialrails.com/blog/b-roll-footage-complete-guide)).

**Zooms:**
- Tella's punch-in example scales to **130%** ([Tella](https://www.tella.com/docs/help/tips/punch-in-zoom-in-on-your-camera)).
- "A hard-cut zoom reads as intentional only when it lands exactly on the word's onset" ([Tella skills](https://www.tella.com/skills/add-zooms)).
- "Zooming in on every line gets tiring fast" ([OpusClip](https://www.opus.pro/tools/zoom-in-effect)).

**SFX:**
- Align the **transient (the peak) of the sound**, not the start of the file ([Krotos](https://krotos.studio/blog/sound-to-picture)).
- Lead whooshes by about 10–20 ms ([Pixflow](https://pixflow.net/blog/cinematic-whoosh-sound-effects/)).
- Sit SFX around **−12 to −18 dB peak**, below dialogue, and duck any music 15–20 dB under speech ([Pixflow](https://pixflow.net/blog/audio-mixing-premiere-pro/)).
- YouTube normalises playback to about **−14 LUFS**, turning loud uploads down but never quiet ones up ([IRPR](https://sounddesign.irpr.agency/guides/how-to-mix-audio-for-youtube/)).

### Captions

The data showing captions help is old or self-reported:
- Facebook's internal tests found **+12% view time** ([Hypebot](https://www.hypebot.com/shhh-why-you-need-to-optimize-your-facebook-videos-for-silence/)).
- A Verizon/Publicis survey of **5,616 adults** found 80% said captions made them more likely to finish a video ([3Play Media](https://www.3playmedia.com/blog/verizon-media-and-publicis-media-find-viewers-want-captions/)).
- The claimed 18–28% lift for animated word-by-word captions comes only from a vendor ([ClipSpeed](https://clipspeed.ai/blog/ai-captions-increase-views.html)).

The firm rules come from subtitling standards:
- Netflix events last between **5/6 s and 7 s**, with a 2-frame minimum gap ([Netflix](https://backlothelp.netflix.com/hc/en-us/articles/215758617)).
- Netflix sets **42 characters per line for Arabic** ([Netflix Arabic TTSG](https://backlothelp.netflix.com/hc/en-us/articles/215517947)).
- Reading-speed caps run 15–17 characters per second for adults ([Netflix Indonesian](https://backlothelp.netflix.com/hc/en-us/articles/216009727); [Malta guidelines](https://www.um.edu.mt/library/oar/bitstream/123456789/112270/1/Proposed%20subtitling%20guidelines_Spiteri%20Miggiani_%20MALTA%20revised%20July%202021%20wm.pdf)).

### Structure, endings and the retention graph

**End screens** take the last **5–20 s** and hold up to four elements ([TechCrunch](https://techcrunch.com/2016/10/26/youtube-launches-mobile-friendly-end-screens-feature-to-keep-viewers-watching-more-video/)). They should start right after the sign-off ([NexLev](https://www.nexlev.io/youtube-end-screen-tips)).

**Absolute retention benchmarks are unreliable:**
- Retention Rabbit's 2025 dataset (10,000+ videos) puts average retention at **23.7%**, with 5–10 min videos best at **31.5%** ([Retention Rabbit](https://translate.google.com/translate?u=https://www.retentionrabbit.com/blog/2025-youtube-audience-retention-benchmark-report&hl=es&sl=en&tl=es&client=srp)).
- Prepublish claims **50–60%** for the same length band ([Prepublish](https://prepublish.ai/blog/youtube-retention-benchmarks-2026)).

That is a 2× conflict, so the skill should judge only against YouTube's "typical" band, which compares a video with his own 10 latest videos of similar length ([YouTube Help](https://support.google.com/youtube/answer/1715160)). YouTube labels key moments as Top moments, Spikes (rewatched, which may mean confusing) and Dips (skipped or abandoned). It also advises moving late top moments earlier ([YouTube Help](https://support.google.com/youtube/answer/9314415?hl=en)).

### Proposed defaults for his two channels

The table below shows the defaults the skill should start from. These are **design choices built on the sources above**, not measured optima. The skill should say so to him, and overwrite them as `edit-preferences.md` learns his taste.

| Rule | Syrian Rubik (cubing) | SRB Gamer | Anchor |
|---|---|---|---|
| Opening | Strongest visual at 0:00 (solved cube, record time). Promise by ~0:07. 2–3 payoff teases of 1–3 s before 0:30. Brand card ≤2 s and only after the hook. | Same, with the gameplay climax first | YouTube "Intro" at 30 s; MrBeast memo |
| Visual change | Every 3–6 s. Holds up to 8–10 s while hands execute an algorithm, with a notation overlay | Every 2–4 s. Cut menus, loading screens and pauses >0.5 s. | Tubefilter; Guo et al.; vendor ranges |
| B-roll | 1.5–3 s illustrative, 3–5 s to read; never >6 s static. Start 2–4 frames before the trigger word. | Same, plus meme inserts | 2–5 s guides; "8 s drags" |
| Zoom | 110–115% to hide jump cuts, 120–130% for emphasis. At most ~1 per 10–15 s. Comic 150–250% snap at most ~1 per 45–90 s. Return to base framing within 1–4 s. Check for 4K source before going past ~130%. | Same, plus freeze + zoom + caption for fails and wins | Tella 130%; OpusClip fatigue |
| Transitions | Hard cut for ~90–95% of edits. Whip or zoom + whoosh only at chapter boundaries (6–12 frames). No dissolves inside a tutorial step. | Dip or flash for "3 hours later" | 2024 backlash coverage |
| SFX | Peak on the event frame, 0–1 frame early. 3–10 dB under voice peaks. No whoosh on every cut. | Gag stings within the zoom budget | Krotos; Pixflow |
| Audio bed (no music) | Room tone at about −50 to −60 dBFS under the voice. 2–4 frame crossfades on voice cuts. Cube clicks as natural "music". | In-game audio about −20 to −25 dB under voice. Mute licensed in-game songs. | Craft inference; Content ID rules |
| Captions | 1–2 lines, ≤42 chars, 0.83–7 s, ≤15–17 cps, stroke 0 | Shorts: 1–3 words per event | Netflix specs |
| Re-hooks | ~3:00 and ~6:00, then every 2–3 min. 1–2 open loops per video. | Same | MrBeast memo; Pixflow |
| Master loudness | −14 LUFS integrated, true peak ≤ −1 dBTP | Same | YouTube normalisation |

## Four free APIs support search-first, download-after-OK sourcing

### Stock video

Three free video sources have real APIs:

- **Pexels**
  - Licence: no credit needed in the video ([Pexels ToS](https://www.pexels.com/terms-of-service/)).
  - API: 200 requests/hour and 20,000/month. Its guidelines ask the *app* (here, the skill's search results) to show a prominent Pexels link and credit the creator where possible ([Pexels API](https://www.pexels.com/api/documentation/)).
  - Restrictions: no showing identifiable people in a bad light, and no implying a brand endorses you ([Pexels rules](https://help.pexels.com/hc/en-us/articles/360042332714-What-are-the-rules-for-using-Pexels-photos-or-videos)).
- **Pixabay**
  - Licence: no attribution needed. No commercial use of recognisable logos ([Pixabay licence](https://pixabay.com/en/service/license/)).
  - API: 100 requests per 60 s, with 24-hour caching ([Pixabay API](https://pixabay.com/api/docs/)). Third-party sites quote 5,000/hour; that conflicts with the official figure and should be ignored.
- **Coverr**
  - Licence: commercial use without credit ([Coverr FAQ](https://coverr.co/stock-video-footage/visuals)).
  - API: a free key, at 50 requests/hour in Demo and 2,000/hour in Production ([Coverr API](https://api.coverr.co/docs/auth)).
  - It also runs an **official MCP server** at `mcp.coverr.co` ([Coverr MCP](https://api.coverr.co/docs/mcp/)).

**Mixkit** is safe and its licence forbids registering items with Content ID, but no API was found ([Mixkit](https://mixkit.co/license/modal/sfxFree/)).

**Sites with conflicting or attribution-based licences** need a per-clip check:
- Videvo: its own guide calls its Standard licence legacy, while a 2025 review calls it current ([Videvo](https://www.videvo.net/blog/?p=314)).
- Mazwai: sources say both "no attribution" and "CC 3.0".

**Open archives** need a per-file licence filter that rejects anything NC or ND: Wikimedia Commons (licence fields in `extmetadata`) and Internet Archive ([Openverse handbook](https://make.wordpress.org/openverse/handbook/openverse-catalog/provider-api-wikimedia-commons/)).

### Sound effects

YouTube states that **sound effects and production loops cannot be Content ID reference files** ([YouTube Help](https://support.google.com/youtube/answer/2605065?hl=en)). That structurally lowers claim risk for SFX. The tiers:

1. **YouTube Audio Library.** YouTube promises its copyright-safe music and SFX "won't be claimed" and are monetisable in the Partner Program. There is no API ([YouTube Help](https://support.google.com/youtube/answer/3376882?hl=en)).
2. **Mixkit and Pixabay SFX.** No attribution needed. No audio API was confirmed.
3. **Freesound**, the only free SFX library with a full public API:
   - Token auth, at 60 requests/minute and 2,000/day.
   - A licence filter such as `license:"Creative Commons 0"`, and preview MP3s ([Freesound API](https://freesound.org/docs/api/overview.html); [CC blog](https://opensource.creativecommons.org/blog/entries/freesound-intro/)).
   - Allowed: CC0, and CC BY with credit.
   - Never allowed: CC BY-NC or the legacy Sampling+ licence ([Freesound FAQ](https://freesound.org/help/faq/)).
4. **Local packs:** Kenney (CC0) and the Sonniss GDC bundles. Sonniss is royalty-free with no attribution, and its 2024 licence bans AI training ([OpenGameArt Kenney](https://opengameart.org/content/51-ui-sound-effects-buttons-switches-and-clicks); [GameFromScratch](https://gamefromscratch.com/sonniss-27-5gb-sound-effect-giveaway-at-gdc-2024/)).

**Do not use:**
- **BBC Sound Effects (RemArc licence).** It is non-commercial without a paid licence ([DIYPhotography](https://www.diyphotography.net/the-bbc-sound-effects-archive-is-now-free-to-download-with-over-33000-files/)).
- **Zapsplat's free tier** requires a credit line ([Zapsplat](https://www.zapsplat.com/copyright-and-audio-licensing-for-beginners)).

The cleanest cube sounds are ones he records himself.

### Music, for the gaming channel

He avoids music, but the gaming channel raises it. Only the YouTube Audio Library carries a platform-level no-claim promise. Pixabay openly admits some contributors register tracks with Content ID, so a "legal" track can still be claimed and must be disputed with its licence certificate ([Pixabay FAQ](https://pixabay.com/service/faq/); [Pixabay blog](https://pixabay.com/blog/posts/how-to-clear-a-youtube-content-id-claim-with-a-pix-190/)).

**How disputes work:** the claimant has 30 days to respond, and a wrong dispute can escalate to a takedown and a strike ([YouTube Help](https://support.google.com/youtube/answer/2797454/dispute-a-content-id-claim?hl=en)). Paid libraries prevent claims by linking his channel: Envato's Claim Clear, Artlist's Clearlist, Epidemic's whitelist ([Envato](https://elements.envato.com/claim-clear-youtube-content-id); [Artlist Help](https://help.artlist.io/hc/en-us/articles/29648852943901-Understanding-copyright-and-Content-ID-claims); [Epidemic](https://www.epidemicsound.com/how-it-works/license-music-legally/)). None of them offers an API a personal skill can use.

### Gameplay

His own gameplay footage is monetisable under publisher policies, all of which can be revoked:
- **Nintendo:** allows monetisation through listed programs including the YouTube Partner Program, but only with creative input or commentary ([Nintendo](https://www.nintendo.co.jp/networkservice_guideline/en/index.html)).
- **Epic:** explicitly allows ad-monetised videos ([Epic](https://legal.epicgames.com/epicgames/fan-art-policy)).
- **Minecraft:** allows ad revenue ([ConductAtlas](https://conductatlas.com/platform/minecraft/minecraft-usage-guidelines/video-content-monetization-carve-out/)).
- **Riot:** bars its logos without a licence and requires a non-endorsement disclaimer ([Riot](https://www.riotgames.com/en/legal)).

The real Content ID risk is **licensed in-game music**. Publisher-owned soundtracks are valid reference files, so the skill should flag music tracks to mute and keep game SFX.

### Cubing-specific footage

- **WCA competition footage:** filming notices grant rights only to organisers, the WCA and their partners ([WCA NAC2024](https://www.worldcubeassociation.org/competitions/NAC2024/register)). Third-party competition clips therefore need the filmer's permission.
- **The Rubik's name:** Spin Master's brand guide restricts "RUBIK'S" to genuine products ([Rubik's brand guide](https://www.rubiks.com/brand-use-guide)).
- **Creative Commons YouTube videos:** discoverable with the Data API (`videoLicense=creativeCommon`, which requires `type=video`). Each video's licence and content still needs checking ([YouTube Data API](https://developers.google.com/youtube/v3/docs/search/list)).

**There is no safe number of seconds.** Content ID can match excerpts as short as about 5 seconds and does not judge fair use ([Berklee](https://www.berklee.edu/node/2538351); [EFF](https://www.eff.org/deeplinks/2020/01/tool-removes-copyrighted-works-not-substitute-fair-use)). So the skill never proposes third-party clips "because it's short".

### The sourcing flow and the licence log

The flow that satisfies his rules:
1. Query Pexels, Pixabay and Coverr for video, and Freesound for SFX (CC0 and CC BY only).
2. Show ID, page URL, preview link, duration, creator, licence and a suggested in-point. He opens the previews himself in his browser.
3. **Download nothing until he approves that batch.**
4. On approval: download, save a licence snapshot and SHA-256 hash, and generate the credit line where required.
5. Upload every video as **Unlisted** first, so claims surface before it goes public ([Pond5 Help](https://www.pond5.com/help/en/articles/10086114-how-to-dispute-clear-a-youtube-content-id-claim)).

Save a licence record at download time, because terms change. Pixabay moved from CC0 to its own licence in 2019, and Mixkit revised its terms in October 2025 ([Michigan Tech](https://blogs.mtu.edu/webmaster/2026/02/best-practices-for-responsible-stock-photography-documentation/)). The log fields: platform, asset ID, page URL, creator, licence name, licence snapshot, attribution text, download date, his approval date, local path, SHA-256, and the video and timecode where it was used. These rows extend the `footage-licenses.md` his video-maker skill already keeps.

| Source | Use | Credit in video | Content ID risk | Search API |
|---|---|---|---|---|
| Pexels | Video | No | Low (clips have no audio) | Yes, free key, 200/h |
| Pixabay | Video, SFX | No | Video low; audio medium | Video yes; audio not found |
| Coverr | Video | No | Low | Yes, free key, plus MCP |
| Freesound | SFX | CC BY only | Low (SFX can't be a reference) | Yes, token, 60/min |
| YouTube Audio Library | SFX, music | CC tracks only | None for copyright-safe items | No |
| Mixkit / Kenney / Sonniss | SFX | No | Very low | No (browse or local packs) |
| Wikimedia / Internet Archive | Video, audio | Per file | Low | Yes, keyless; filter out NC/ND |
| BBC RemArc | SFX | — | Not allowed (non-commercial) | — |

## Seven conflicts the skill must design around

| Conflict | Side A | Side B | Position taken |
|---|---|---|---|
| Lua on Free 21.1 | Puget: scripting "entirely removed" | saadk408 and AutoSubs: sandboxed Lua runs from Workspace > Scripts | Lua runs but is undocumented and experimental on Windows. Optional only, never the baseline. |
| Built-in MCP scope | ~14 general tools that write Python | ~88 tools (byteiota) | Unknown until he runs setup. Have the skill list the tools on first connection. |
| Default deliverable | Interchange research: FCPXML + marker EDL | Skill-design research: pre-placed timelines are low–medium reliability for a non-coder | Sheet + marker EDL + SRT by default. FCPXML opt-in after a smoke test. |
| FCPXML fidelity | Transforms and keyframes survived (forum) | Only the first keyframe imports; markers "never accepted" | Static scale only. Markers duplicated in the EDL. |
| Arabic rendering | 17.4 right-to-left support; forum claim of v20 fix; libass "shapes properly" | Disconnected letters, stroke bug, libass ticket, his own broken upload | Untrusted until tested. Captions uploaded to YouTube. Pop-ups pre-rendered by the browser engine. |
| Python for Resolve | 3.10–3.12 (samuelgursky) | 3.10/3.11 only (Tooflex) | Use bundled `ResolvePython.exe` on Studio 21.1. |
| Retention benchmarks | 23.7% average (Retention Rabbit) | 50–60% for 5–10 min (Prepublish) | Judge only against his own "typical" band |

Smaller conflicts also appear in the notes, and none of them changes the design:
- Free vs Studio tiering of Resolve 20's AI Animated Subtitles.
- Pricing for FireCut and AutoCut, and whether AutoCut supports Resolve.
- The required NVIDIA driver version (581.57+ vs 570.65).
- The line count at which a skill's reference file needs a table of contents: 100 lines in Anthropic's docs, 300 in skill-creator (use 100).

## One JSON plan, many renders, six checkpoints

### Packaging

His existing video-maker skill is a single 52 KB `SKILL.md`. That breaks Anthropic's guidance to keep `SKILL.md` **under 500 lines**, with detail in reference files one level deep ([best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)). It also matters more than it seems: after context compaction, Claude Code re-attaches only **the first 5,000 tokens** of each skill ([Claude Code skills docs](https://code.claude.com/docs/en/skills)).

So the new skill must put its non-negotiable rules in the **first ~60 lines**:
- Plain, short Syrian-Arabic chat.
- Nothing downloaded, installed or run without his OK for that exact thing.
- Licensed sources only, never NC or ND.
- The checkpoints.
- Read `_brain` first.

Keep the body to 200–350 lines.

**Name and frontmatter:**
- Name it **`editing-in-resolve`**: lowercase, under 64 characters, and without "claude".
- Write a third-person, slightly "pushy" description under 1,024 characters. Include Arabic triggers (مونتاج، دافينشي، بي رول، زوم، مؤثرات صوتية، ترجمة) and a negative pointer ("not for writing scripts or animations; use video-maker"). Descriptions drive triggering, and Claude "tends to undertrigger" ([skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)).
- If it lives in claude.ai like video-maker, which syncs into `~/.claude/skills/synced/` and overwrites local edits, the frontmatter may use only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`. Other fields such as `shell: powershell` cause a hard error on upload ([Claude Code skills docs](https://code.claude.com/docs/en/skills)).

### File layout

The skill shares video-maker's studio folder and memory, and adds one memory file:

```
editing-in-resolve/
  SKILL.md                 rules (first 60 lines) -> checklist -> output contract
  references/
    plan-schema.md         edit_plan.json fields + validator rules
    timecode-math.md       frames, DF/NDF, 01:00:00:00 offset, VFR
    resolve-by-edition.md  Free<=21.0 / Free 21.1 Lua / Studio API / built-in MCP
    import-steps-ar.md     his click-by-click steps in plain Syrian Arabic
    retention-rules.md     the defaults table, labelled as heuristics
    sources-licensing.md   allowed sources, API limits, licence-log fields
    arabic-text.md         caption rules, stroke=0, pre-render fallback
    windows-gotchas.md     UTF-8, no PowerShell '>' redirection, ASCII aliases
  scripts/
    probe_video.py  transcribe.py  fix_terms.py  silence_map.py  contact_sheets.py
    timeline_view.py  emphasis.py  broll_index.py  stock_search.py (search only)
    download_approved.py (only after OK; logs licence + sha256)  timecode.py
    validate_plan.py  plan_to_html.py  plan_to_edl.py  plan_to_srt.py
    plan_to_fcpxml.py  plan_to_lua.py (Free 21.1, data embedded; no io)
    plan_to_resolve.py (Studio, run with ResolvePython.exe)  retention_map.py
  assets/   edit_sheet_template.html (RTL, print CSS, legend), marker_legend.json
  evals/    evals.json (cubing tutorial, gaming highlight, 20-min long-form)

%USERPROFILE%\SyrianRubikStudio\
  _brain\edit-preferences.md   NEW: Resolve edition/version/fps/start TC,
                               smoke-test results, zoom %, SFX likes, B-roll density
  videos\<date>_<slug>\edit\   probe.json transcript.json sheets\ plans\edit_plan_vN.json
                               out\edit_sheet.html markers.edl captions.srt CHANGES.md
```

**How the scripts must behave on Windows:**
- Python with `pathlib`, list-form `subprocess` and UTF-8 everywhere.
- Write files directly from Python, never through PowerShell redirection.
- Accept forward slashes, since `${CLAUDE_SKILL_DIR}` may expand with backslashes.

Anthropic's own pattern for high-stakes batch work is **plan → validate → execute → verify** through an intermediate file checked by a script ([best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

### Pipeline and checkpoints

| Step | What happens | Checkpoint |
|---|---|---|
| 0 | Read `_brain` (preferences, glossary, edit-preferences, footage-licenses). Load the Resolve edition and version, or ask. | — |
| 1–5 | Probe → transcript → term fix → silence/retake map → contact sheets → emphasis peaks → own-library B-roll matches | **A:** 3–5 short lines: what the video is, its length and fps, any VFR problem; ask the energy and style he wants |
| 6 | Claude writes a plain-English (Syrian-Arabic) strategy: cuts, B-roll themes, zoom and SFX density, captions | **B:** approve the strategy before any detailed plan (the video-use rule) |
| 7–8 | `edit_plan_vN.json` → `validate_plan.py` until clean → render the sheet, EDL and SRT; stock candidates as links only | **C:** review the sheet; he approves or edits rows (bump the version, log it in CHANGES.md) |
| 9 | Download approved stock, copy any Lua or Python into Resolve, use the MCP, or install anything | **D:** OK per batch, for that exact thing |
| 10 | He applies: import markers, Shift+Down through them, place clips | **E:** what he kept or changed → append to `edit-preferences.md` |
| 11 | After publishing: Studio retention export → `retention_map.py` (minus 1 hour) → fixes for the next video | **F:** optional review of retention dips and spikes |

### The edit_plan.json schema

This is the single source of truth. It merges video-use's EDL fields (`start`, `end`, `quote`, `reason`) ([video-use SKILL.md](https://raw.githubusercontent.com/browser-use/video-use/main/SKILL.md)) with an assistant-editor row: timecode, track, asset, action, status. That row shape follows creator B-roll databases, which use a "Timecode" field and a "Fix Needed" status ([Thomas Frank](https://thomasjfrank.com/docs/creators-companion/databases/b-roll/)).

```json
{
  "schema": "resolve-edit-plan/1", "plan_version": 3, "channel": "syrian-rubik",
  "video": {"path": "D:/SyrianRubikStudio/videos/2026-10-20_f2l/raw/a-roll.mp4",
            "duration_s": 742.4, "fps_real": "30000/1001", "vfr": false},
  "timeline": {"nominal_fps": 30, "drop_frame": false, "start_tc": "01:00:00:00",
               "a_roll_offset_frames": 0},
  "resolve": {"edition": "free", "version": "21.1.1",
              "deliverables": ["sheet", "markers_edl", "srt"]},
  "strategy_ar": "…", "inputs": {"transcript": "transcript.json", "sheets": "sheets/"},
  "items": [{
    "id": "B03", "type": "broll", "src_sec": 12.50, "frame": 375, "tc_in": "01:00:12:15",
    "dur_frames": 90, "track": "V2", "quote": "…", "trigger_word": "…",
    "asset": {"path": "D:/SyrianRubikStudio/library/broll/cube_explode_02.mp4", "in_sec": 2.0,
              "source": "own|pexels|coverr|freesound|…", "source_id": null, "page_url": null,
              "license": "own footage", "attribution": null, "state": "on_disk|candidate|approved"},
    "params": {}, "say_ar": "حط لقطة المكعب عم ينفجر هون", "why": "…",
    "marker": {"color": "Blue", "name": "B03 cube explode"},
    "confidence": 0.7, "tight": false, "status": "todo|done|fix"}]
}
```

`type` is one of `cut`, `broll`, `zoom`, `sfx`, `transition`, `caption`, `popup`, `speed`, `freeze`, `chapter`, `fix` or `note`. Each type has its own `params`:
- **zoom:** `scale`, `anchor_xy`, `ease`, `hold_s`.
- **sfx:** `gain_db`, `align: "peak"`.
- **cut:** `end_sec`, and `reason` (silence, retake or filler).
- **caption:** `text_ar`.

**`validate_plan.py` fails the plan when:**
- An item falls outside the video's duration.
- `frame` ≠ `round(src_sec × fps_real)`.
- `tc_in` does not match `frame` plus the timeline start.
- Items overlap on the same track.
- An approved asset is missing on disk.
- A licence field is empty, NC or ND.
- A marker colour is not one of the 16 API names.
- There are more than 999 markers, or two markers on one frame.
- A marker name is non-ASCII, longer than about 60 characters, or contains `|`.

**It warns (but does not fail) when:**
- Zoom or SFX density exceeds his preferences.
- A static B-roll runs longer than 6 s.
- A caption exceeds 42 characters per line or 17 characters per second.

The sheet states that times are accurate to about ±0.5 s, because frames were sampled every 2–5 s. Rows marked `tight` get denser sheets and word-boundary snapping.

### Deliverables by edition

**Always, on every edition, with nothing to install:**
- `edit_sheet.html`: right-to-left Arabic, a thumbnail per row, both `mm:ss.s` and timeline timecode, colour-coded rows, checkboxes, and print CSS. It has two views: a "gather list" of assets to locate or approve first, and a chronological pass for executing the edit.
- `markers.edl`.
- `captions.srt`: UTF-8, frame-snapped, ≤42 characters per line.
- An upload note: chapters from the chapter-colour markers, credit lines for any CC BY items, and the "publish Unlisted first" reminder.

**After the smoke test passes:** `timeline.fcpxml` (1.10), with B-roll on lane 1 and SFX on lane −1, as a separate layer he can copy in.

**By edition:**
- **Free ≤21.0:** an in-app Python marker script is possible, along with a warning not to upgrade blindly.
- **Free 21.1+:** an optional one-click Lua marker script. The plan data is embedded in the `.lua` file, because the sandbox has no `io`. It brings marker notes and durations, but is unofficial.
- **Studio 21.1+:** `plan_to_resolve.py` run with `ResolvePython.exe`, or the built-in MCP. It can do `AddMarker` with notes and the plan ID in `customData`, `AppendToTimeline` for B-roll and SFX, `AddTransition` at chapter cuts, and `SetFades`. Zooms on their own segments come later, if he wants them.

### The one-time smoke test

Before trusting any file route, the skill should walk him through a 10-minute test in a throwaway project, and save the results in `edit-preferences.md`:
1. Export one hand-made marker via Timelines > Export > Timeline Markers to EDL, so the generator copies his build's exact format.
2. Import a generated `markers.edl` with one ASCII name and one Arabic name.
3. Import a test FCPXML with B-roll on lane 1, SFX on lane −1, a static 1.2 scale and one marker, with "Use sizing information" on ([Larry Jordan](https://larryjordan.com/articles/sending-projects-between-apple-final-cut-pro-and-davinci-resolve/)).
4. Import an Arabic SRT with stroke 0, and check letter joining and the order of mixed Arabic, English and numbers such as "R U R'" or "8.53".
5. On Studio only, run one `AddMarker` and confirm the `frameId` convention.

### Questions to ask on first run

| Question | Why it matters | Default if unanswered |
|---|---|---|
| Free or Studio, and the exact version (Help > About)? Already on 21.1? | Decides files-only vs Lua vs API/MCP. 21.1 silently drops Python on Free. | Assume Free 21.1: files only |
| Timeline fps, start timecode, drop-frame? Does the voice track start at the first frame? | Every timecode depends on these. A wrong start makes the marker import fail silently. | His footage fps, 01:00:00:00, NDF, offset 0 (confirm via the smoke-test EDL) |
| Plan on the raw recording, or on his own rough cut? | If he cuts silences first, every timestamp shifts. The plan must target what is actually on the timeline. | Raw recording, with cuts proposed as rows |
| Camera/phone/OBS? Resolution? | Variable frame rate causes drift. A 4K source allows ~200% punch-ins on a 1080p timeline. | Probe, flag VFR, cap zooms at 130% |
| Gaming: separate mic track? Which games? | Emphasis detection needs a clean voice track. Publisher policy and licensed in-game music vary. | Ask per video. Flag music to mute. |
| Where is his B-roll/SFX library, and what is in it? Will he record cube sounds? | The plan may only reference files that exist. Own sounds carry zero licence risk. | Index `SyrianRubikStudio\library\` |
| Captions: uploaded YouTube CC, burned-in, or none? | Arabic rendering in Resolve is unproven | Upload the SRT to YouTube; pre-render pop-ups |
| OK to create free API keys (Pexels, Coverr, Freesound, optionally YouTube Data API)? Where to store them? | Search-only use still sends network requests | No keys: give browse URLs instead |
| Which installs does he approve (auto-editor, scenedetect, librosa, PyTorch + open_clip ~2–3 GB, WhisperX, Ollama + Qwen3-VL)? | His security rule; 8 GB VRAM | Only what he already has: ffmpeg + faster-whisper |
| Does his Windows user folder or project path contain Arabic, or live in OneDrive? | Mailbox bridges need ASCII paths; long paths break tools | Use ASCII working aliases plus `names_map.json` |
| "Tell me where" (markers) or "do it for me" (FCPXML/MCP)? | Sets the deliverable tier | Tell me where |
| Claude Code or Claude Desktop for MCP? | Separate MCP clients. The Lua `.mcpb` bridge needs Desktop. | Claude Code |
| Will he share Studio retention exports after publishing? | Feeds the improvement loop | Ask after each upload |

Finally, follow Anthropic's eval-first advice before writing much content ([best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)):
- Build **three real test videos**: a short cubing tutorial, a gaming highlight and a 20-minute long-form.
- Measure a baseline without the skill, then iterate.
- Tune the description with skill-creator's loop of about 20 queries, using near-miss prompts taken from video-maker so the two skills don't trigger on each other's requests ([skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)).

## Conclusion

The research turns the question around. "Can Claude edit in Resolve?" is the wrong question, because on a Free 21.1 install the honest answer is "barely, and unofficially". The better question is what a strong assistant editor hands over. The answer is a cue sheet tied to exact frames, which the editor works through marker by marker, and that format has existed for decades. Resolve's own marker EDL carries it on both editions, and the scripting API and built-in MCP only make it faster. So the skill's value sits in the analysis layer: word timing that survives a 59% WER dialect transcript, retake detection, contact sheets, licence-checked sourcing, and a validator that refuses a plan with a wrong frame rate or a non-commercial clip. The analysis layer is independent of Blackmagic's choices about editions, which is why the design does not depend on the unresolved Lua question.

Two things will decide whether it works for him, and neither is a feature. The first is a one-time smoke test on his actual Resolve build. It settles the open questions about FCPXML lanes, marker names and Arabic rendering that no amount of web research could resolve. The second is a loop from YouTube Studio's "typical" retention back into `edit-preferences.md`. That turns the vendor heuristics in this report into his own measured rules. A skill that ships with both will improve on every video. A skill that hard-codes 130% zooms and three-second cuts will keep repeating someone else's defaults.
