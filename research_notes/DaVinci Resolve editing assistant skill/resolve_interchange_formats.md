# DaVinci Resolve import formats for an AI edit plan (EDL, FCPXML, OTIO, AAF/DRT, markers, subtitles), as of October 2026

Scope note: Blackmagic's own sites (forum.blackmagicdesign.com, documents.blackmagicdesign.com, blackmagicdesign.com) and most vendor blogs could not be fetched from this research environment. The proxy blocked them. Claims about them come from search-result summaries and are marked as such. Primary evidence comes from open-source code and real example files on GitHub, plus local tests:
- OpenTimelineIO 0.18.1 and its adapter plugins, installed from PyPI.
- Apple FCPXML DTDs. The sample FCPXML below was validated against them with `xmllint --valid`.
- The auto-editor source (commit c9c8ee2, 21 Oct 2026, v31.7.3).

"Verified locally" means I generated or validated the snippet in this session. It does **not** mean I tested an import in Resolve; no Resolve install was available.

## Q1. EDL (CMX3600): clip EDLs and Resolve's "Timeline Markers from EDL"

### Takeaway
A clip EDL has three problems for this job:
- It carries one video track only.
- It has no file paths. Resolve matches media by reel name and timecode, which is fragile for phone or downloaded B-roll.
- It cannot carry scale/position, titles or audio-track layout in any useful way.

A **marker EDL**, by contrast, is the most reliable and best-documented route for markers. That is a one-frame CMX event plus Resolve's proprietary ` |C:ResolveColorX |M:name |D:frames` line, imported via *Timelines > Import > Timeline Markers from EDL*. It works the same in Free and Studio.

### Cited Findings
- Blackmagic staff said on their forum that Resolve reads markers only through an EDL **comment** structure. The example was an event line followed by a line with color, marker name and a numeric value. The fields were not formally defined there. This comes from a search summary of the thread, which could not be fetched directly — [Blackmagic Forum "EDL file format?"](https://forum.blackmagicdesign.com/viewtopic.php?p=752663)
- SubtitleEdit's Resolve format class gives the field meanings: C = marker color, M = marker name, D = duration in frames. Its own example is `001  001      V     C        01:00:05:00 01:00:05:01 01:00:05:00 01:00:05:01` followed by ` |C:ResolveColorBlue |M:Marker name |D:120`. It describes the format as what Resolve exports and imports via "Timelines > Export/Import > Timeline Markers to/from EDL" — [SubtitleEdit DaVinciResolveMarkerEdl.cs](https://github.com/SubtitleEdit/subtitleedit/blob/HEAD/src/libse/SubtitleFormats/DaVinciResolveMarkerEdl.cs)
- The vodcue writer says its byte layout "mirrors Resolve's own `Timeline Markers to EDL` export":
  - Two trailing spaces end every event line.
  - One leading space starts every annotation line.
  - `FCM: NON-DROP FRAME` is in the header.
  - Resolve places each marker at the **record-in** timecode, read as an absolute timeline position, "so the record timecodes must be pre-offset by the timeline start".
  - Its default timeline start is `01:00:00:00` ("Resolve's defaults").

  — [vodcue resolve_edl.rs](https://github.com/wdominik/vodcue/blob/HEAD/src/formats/resolve_edl.rs); [vodcue README](https://github.com/wdominik/vodcue/blob/HEAD/README.md)
- **Colors.** The 16 valid `|C:` values "mirror the `MARKER_*` constants of Resolve's scripting API": `ResolveColorBlue` (default), Cyan, Green, Yellow, Red, Pink, Purple, Fuchsia, Rose, Lavender, Sky, Mint, Lemon, Sand, Cocoa, Cream — [vodcue resolve_edl.rs](https://github.com/wdominik/vodcue/blob/HEAD/src/formats/resolve_edl.rs)
- **Duration markers.** Real Resolve-exported marker EDLs keep the event one frame long (in → in+1) and put the length only in `|D:`, for example `00:10:57:18 00:10:57:19 ... |C:ResolveColorBlue |M:Chapter 12 |D:4566` — [VyacheArt/edl-to-youtube example.edl](https://github.com/VyacheArt/edl-to-youtube/blob/HEAD/example.edl). Another Resolve export shows `|D:1` point markers with German umlauts in the name (`|M:Erklärung zu "Felder aufdecken"`) — [Gravitar64 "Teil_120_Timeline 1.edl"](https://github.com/Gravitar64/A-beautiful-code-in-Python/blob/HEAD/Teil_120_Timeline%201.edl)
- **Practical constraints** from a tool that ships Resolve marker EDLs:
  - Event numbers are 3 digits, so at most 999 markers.
  - "Resolve permits only one marker per output frame" and can discard duplicates.
  - Lines end in CRLF and the file is written as UTF-8.

  — [Aagedal StitchMarkerExport.swift](https://github.com/aagedal/Aagedal-Media-Converter/blob/HEAD/Aagedal%20Media%20Converter/Logic/Conversion/StitchMarkerExport.swift)
- **Import path:** right-click the timeline in the Media Pool, then "Timelines > Import > Timeline Markers from EDL". If no markers appear, check that they fall inside the timeline's timecode range. One vendor warns that Resolve "might not support special characters in marker names and comments" — [editingtools.io guide](https://editingtools.io/guides/convert-livenotes-to-resolve-marker); [Simon Says guide](https://www.simonsaysai.com/help/3852515-export-for-blackmagic-davinci-resolve-timeline-markers)
- **Clip EDL conform** (old forum posts, 2010–2018, via search summary):
  - Resolve matches EDL events to Media Pool clips mainly by **reel name + source timecode**.
  - Options include "Assist using reel names from the…" and "extract reel names from EDL comments".
  - Set these before importing media.
  - Cameras with no timecode, where every clip starts at 00:00:00:00, need unique reel names.

  — [Blackmagic Forum "Failed to link because timecode extents do not match"](https://forum.blackmagicdesign.com/viewtopic.php?p=248494)
- One NLE exporter treats EDL as the "oldest common denominator" (Resolve: File → Import → Timeline). Its EDL holds one video track only: reel `AX`, with the name in `* FROM CLIP NAME:` / `* SOURCE FILE:` comments, "editors find the media by name". It drops sound, text, levels and motion, and transliterates titles to 7-bit ASCII — [yt-cartell-studio internal/nle/edl.go](https://github.com/gitkalenyuk/yt-cartell-studio-source/blob/HEAD/internal/nle/edl.go)
- Verified locally with the official OTIO CMX adapter (`otio-cmx3600-adapter` 1.0.0, OpenTimelineIO 0.18.1). Writing a 2-video-track timeline raised `NotSupportedError('Only a single video track is supported, got: 2')`. A V2-only export produced:
  ```
  TITLE: V2only

  001  broll20m V     C        00:00:02:00 00:00:06:00 00:00:12:15 00:00:16:15
  * FROM CLIP NAME:  broll_market.mp4
  * FROM CLIP: file:///C:/Users/Ahmad/Videos/B-roll/broll%20market.mp4
  * OTIO TRUNCATED REEL NAME FROM: broll%20market.mp4
  ```
  Three things to notice:
  - The reel name was cut to 8 characters, taken from the *percent-encoded* filename.
  - Record TC began at 00:00:… even though `global_start_time` was 01:00:00:00.
  - Markers attached to the track were not written. The adapter only writes clip markers, as Avid-style `* LOC: <tc> <COLOR> <NAME UPPERCASED>` lines, not Resolve's `|C:` syntax.

  — [otio-cmx3600-adapter on PyPI](https://pypi.org/project/otio-cmx3600-adapter/)

#### Verified marker EDL template (generated locally; 30 fps, timeline starts at 01:00:00:00, CRLF, UTF-8)
```
TITLE: EditPlan v1
FCM: NON-DROP FRAME

001  001      V     C        01:00:12:15 01:00:12:16 01:00:12:15 01:00:12:16  
 |C:ResolveColorBlue |M:BROLL broll_market.mp4 (4s) |D:120

002  001      V     C        01:00:20:00 01:00:20:01 01:00:20:00 01:00:20:01  
 |C:ResolveColorRed |M:ZOOM 120% punch-in |D:15

003  001      V     C        01:00:35:00 01:00:35:01 01:00:35:00 01:00:35:01  
 |C:ResolveColorYellow |M:SFX whoosh |D:1
```

### Inferences
- A marker EDL has no separate field for the marker **note**. The skill should pack the instruction into `|M:` (for example `ZOOM 120% | 0.5s`) and swap `|` for `/`, since `|` delimits fields. One third-party writer also adds a `* note` comment line, but nothing shows Resolve reads it.
- Use one marker color per action type, so that "Delete markers by color" and the marker index act as a to-do list. For example: Blue = B-roll, Red = zoom, Yellow = SFX, Green = transition, Purple = caption.
- Record timecode must use the timeline's start timecode (usually 01:00:00:00) and the timeline's frame rate. Otherwise markers land outside the timeline and import silently fails.
- Do not use clip EDLs to place B-roll for this user. YouTube and phone B-roll usually has 00:00:00:00 timecode and no reel name, which is exactly the case the forum calls hard to conform.

### Gaps
- Not verified: whether Resolve 20/21 imports `|M:` text containing Arabic script. Latin-1 umlauts round-trip in a real export, and one test fixture uses Japanese characters, but no Arabic test was found.
- No source confirms whether Resolve reads `* LOC:` lines, or any note field, from an EDL.
- No official Blackmagic specification of the `|C:|M:|D:` syntax could be accessed.

## Q2. FCPXML: versions, a minimal multi-lane file, markers, time math, relinking, what survives

### Takeaway
FCPXML is the best single file for "A-roll on V1 + B-roll on V2 + SFX on A2 + markers". Its strengths:
- It carries absolute `file:///` media paths.
- It places connected clips (lane 1 = above, lane −1 = below) at exact rational times.
- It has `marker`, `chapter-marker` and `adjust-transform`.
- It imports via File > Import > Timeline in Free and Studio.

Target **FCPXML 1.10** for the widest Resolve compatibility (18 and newer), or 1.11 if the user is on 19.1 or later. Two things are not reliably confirmed: Resolve's import of FCPXML **markers** and of transform **keyframes**.

### Cited Findings
- **Version support** (mixed-quality evidence):
  - Resolve 17 imported FCPXML 1.9 but not 1.10 (2021 forum thread, via search) — [Blackmagic Forum "Resolve and fcpxml 1.9 and 1.10"](https://forum.blackmagicdesign.com/viewtopic.php?p=806873)
  - A vendor says Resolve 18/19 or later is needed for 1.10 — [ToolsOnAir JIM/DaVinci Resolve page](https://toolsonair.atlassian.net/wiki/spaces/TST/pages/3497623553/JIM+DaVinci+Resolve+v.5.5)
  - Resolve's scripting API (doc dated 3 Oct 2024) lists export types `EXPORT_FCPXML_1_8`, `_1_9` and `_1_10`, and none newer — [Resolve scripting README mirror](https://github.com/LenNerd42/DaVinciResolveAPI/blob/HEAD/docs/README.md)
  - A hands-on test imported an FCP-exported **1.11** file into Resolve 19.1 Studio successfully, per a search summary — [creativevideotips.com](https://creativevideotips.com/tutorials/final-cut-pro-to-davinci-resolve-xml-workflow)
  - A third-party exporter's source comment claims "Resolve 19.1.1 reads up to 1.13, Resolve 21 up to 1.14". It writes 1.10 because that is "the newest version the oldest supported Resolve (18) still reads". This claim is unverified — [yt-cartell-studio fcpxml.go](https://github.com/gitkalenyuk/yt-cartell-studio-source/blob/HEAD/internal/nle/fcpxml.go)
  - auto-editor (Oct 2026) writes **1.11 by default** for `--export resolve`. It offers `version=10` "for an older editor that can't read 1.11" — [auto-editor export skill](https://github.com/WyattBlue/auto-editor/blob/HEAD/skills/auto-editor-export/SKILL.md)
  - Final Cut Pro 12.0 writes FCPXML **1.14** — [Apple FCP release notes](https://support.apple.com/en-us/102825)
  - If Resolve's importer doesn't support the schema version, it fails with "Invalid XML" — [cutsio](https://cutsio.com/blog/fix-invalid-xml-fcp-davinci)
- **Structure rules from real FCP exports:**
  - With `tcStart="3600s"` (01:00:00:00), the first spine element has `offset="3600s"`. Spine offsets are therefore in timeline time, including the start timecode. Example: `<gap … offset="3600s" … duration="10s"/>` followed by `<asset-clip … offset="3610s" … start="684/25s" …>` — [OpenFCPXMLKit test sample 24With25Media.fcpxml](https://github.com/TheAcharya/OpenFCPXMLKit/blob/HEAD/Tests/FCPXML%20Samples/FCPXML/24With25Media.fcpxml)
  - **Connected clips (`lane="1"` and up above, `lane="-1"` and down below) and markers inside a clip use the *parent clip's source time*, not timeline time.** Example: parent `start="1102800/3000s"`, connected title `lane="1" offset="1104400/3000s"` — [nicknoonan/fcpxml example_complicated.fcpxml](https://github.com/nicknoonan/fcpxml/blob/HEAD/src/parser/example_complicated.fcpxml). Another: parent `start="3602s"` with `<marker start="3603s" …>` — [Tasweerix fixture final-cut.fcpxml](https://github.com/aliadel2002/Tasweerix/blob/HEAD/packages/interchange/test/fixtures/final-cut.fcpxml)
- **DTD facts** (FCPXML 1.10/1.11):
  - `marker` has `start` (required), `duration`, `value` (required, the name), `completed` (0/1, which makes a to-do marker), and `note`.
  - `chapter-marker` has `start`, `duration`, `value`, `note` and `posterOffset`.
  - `adjust-transform` has `position` (default "0 0"), `scale` ("1 1"), `rotation` and `anchor`. It can contain `<param name="scale"><keyframeAnimation><keyframe time=… value=…/>`.
  - `sequence audioLayout` is mono, stereo or surround.

  — [CommandPost copies of Apple FCPXML DTDs 1.0–1.14](https://github.com/CommandPost/CommandPost/tree/HEAD/src/extensions/cp/apple/fcpxml/dtd)
- **Time format.** Times are rational seconds such as `1001/30000s` (one frame at 29.97), `1/30s`, `100/3000s` or `3600s`. Real FCP files use these, for example `frameDuration="100/3000s"` and `duration="300300/30000s"` — [OpenFCPXMLKit samples](https://github.com/TheAcharya/OpenFCPXMLKit/blob/HEAD/Tests/FCPXML%20Samples/FCPXML/Annotations.fcpxml). auto-editor writes `{frames*den}/{num}s`, so 1 frame at 30 fps is `1/30s` — [auto-editor fcp11.nim](https://github.com/WyattBlue/auto-editor/blob/HEAD/src/exports/fcp11.nim)
- **auto-editor's Resolve FCPXML conventions** — [fcp11.nim](https://github.com/WyattBlue/auto-editor/blob/HEAD/src/exports/fcp11.nim):
  - It writes `media-rep kind="original-media" src=<file URL>`.
  - The sequence is `tcStart="0s" tcFormat="NDF"`, with `audioLayout` "stereo"/"surround" only and `audioRate` "48k"/"44.1k".
  - Cross Dissolve uses FCP's uid, and "Resolve matches the transition by name".
- **auto-editor's Windows file URLs**: backslashes become `/`, the prefix is `file:///`, and every byte outside `[A-Za-z0-9-._~/:]` is percent-encoded (spaces, `#`, `%`, non-ASCII) — [auto-editor util/fun.nim pathToUri](https://github.com/WyattBlue/auto-editor/blob/HEAD/src/util/fun.nim)
- Another exporter notes: "Media are referenced by absolute file:// URLs (Final Cut Pro and Resolve do not resolve relative ones)". Its `adjust-transform` position is "percent of the frame height from the centre, Y up". Its Resolve flavour drops keyframes on stills because "DaVinci Resolve imports only their first value (a text fading in would stay at opacity 0, a Ken Burns move would freeze)". Its Resolve output keeps a static `<adjust-transform position="0 0" scale="1.12 1.12" rotation="0"/>` — [yt-cartell-studio fcpxml.go and testdata/timeline-resolve.fcpxml](https://github.com/gitkalenyuk/yt-cartell-studio-source/blob/HEAD/internal/nle/fcpxml.go)
- Resolve's timeline import has a "Use sizing information" option. With it, position, scale, rotation and crop from the originating NLE are applied to the clip's Inspector transform — [Larry Jordan](https://larryjordan.com/articles/sending-projects-between-apple-final-cut-pro-and-davinci-resolve/). A forum user reported that transform data and keyframes survived an FCPXML→Resolve→XML round trip, but "spatial conform is messed" — [Creative COW](https://creativecow.net/?p=1860288). Older reports (FCPX 10.3 → Resolve 12.5) had about half of position values mistranslated — [Creative COW thread](https://creativecow.net/?p=1981035)
- **Markers.** An older forum report says Resolve "has never accepted" FCPX markers through FCPXML. This is a search summary of a Blackmagic forum thread, the exact thread is uncertain, and it is likely Resolve 15–17 era — [Blackmagic Forum "Import FCPXML issue"](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=82115). Old forum posts also say FCPX titles "lose their formatting" — [Blackmagic Forum](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=109013)
- Verified locally: OTIO's `otio-fcpx-xml-adapter` 1.0.0 output is poorly suited to Resolve:
  - It writes `version="1.8"` with no `tcStart`.
  - It puts loose `asset-clip`s at the document root.
  - It drops both markers.
  - It nests audio as `<clip lane="-1"><gap><audio …/></gap></clip>`.

  — [otio-fcpx-xml-adapter on PyPI](https://pypi.org/project/otio-fcpx-xml-adapter/)

#### Minimal FCPXML for Resolve (verified locally: valid against Apple's FCPXML 1.10 **and** 1.11 DTDs via `xmllint --valid`; not test-imported into Resolve)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.10">
  <resources>
    <format id="r1" name="FFVideoFormat1080p30" frameDuration="1/30s" width="1920" height="1080" colorSpace="1-1-1 (Rec. 709)"/>
    <asset id="r2" name="a-roll" start="0s" duration="600s" hasVideo="1" hasAudio="1" format="r1" audioSources="1" audioChannels="2" audioRate="48000">
      <media-rep kind="original-media" src="file:///C:/Users/Ahmad/Videos/Project/a-roll.mp4"/>
    </asset>
    <asset id="r3" name="broll market" start="0s" duration="20s" hasVideo="1" hasAudio="0" format="r1">
      <media-rep kind="original-media" src="file:///C:/Users/Ahmad/Videos/B-roll/broll%20market.mp4"/>
    </asset>
    <asset id="r4" name="whoosh" start="0s" duration="2s" hasVideo="0" hasAudio="1" audioSources="1" audioChannels="2" audioRate="48000">
      <media-rep kind="original-media" src="file:///C:/Users/Ahmad/Videos/SFX/whoosh.wav"/>
    </asset>
  </resources>
  <library>
    <event name="AI Edit Plan">
      <project name="EditPlan v1">
        <sequence format="r1" duration="60s" tcStart="3600s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">
          <spine>
            <!-- A-roll (V1+A1) at timeline 01:00:00:00; source 0s..60s -->
            <asset-clip ref="r2" name="a-roll" offset="3600s" start="0s" duration="60s" tcFormat="NDF" audioRole="dialogue">
              <!-- children are in PARENT SOURCE time: parent start=0s, so 25/2s = 12.5 s into the timeline -->
              <asset-clip ref="r3" name="broll market" lane="1" offset="25/2s" start="2s" duration="4s">
                <adjust-transform position="0 0" scale="1.2 1.2"/>
              </asset-clip>
              <asset-clip ref="r4" name="whoosh" lane="-1" offset="12s" start="0s" duration="1s" audioRole="effects"/>
              <marker start="20s" duration="1/2s" value="ZOOM 120%" note="punch-in on the punchline"/>
              <marker start="35s" duration="1/30s" value="TODO: check caption" completed="0"/>
              <chapter-marker start="0s" duration="1/30s" value="Intro" posterOffset="0s"/>
            </asset-clip>
          </spine>
        </sequence>
      </project>
    </event>
  </library>
</fcpxml>
```
Arabic file names percent-encode as UTF-8 bytes (verified with Python `PureWindowsPath(...).as_uri()`): `C:\Users\Ahmad\Videos\B-roll\سوق دمشق #1.mp4` → `file:///C:/Users/Ahmad/Videos/B-roll/%D8%B3%D9%88%D9%82%20%D8%AF%D9%85%D8%B4%D9%82%20%231.mp4`.

### Inferences
- Simplest robust layout: the whole voice/A-roll is one spine `asset-clip` with `start="0s"`. All B-roll, SFX and markers are its children. Then child `offset` equals "seconds into the video", with no parent-start arithmetic.
  - If the spine is cut into several pieces (silence removal), each child must attach to the spine clip under it. Its offset becomes `parent.start + (t_timeline − parent.offset)`.
- Snap every time to the frame grid before writing: `round(sec × fps)` frames → `frames × frameDuration`. Off-grid rationals are legal FCPXML but can cause one-frame rounding on import.
- Lane-to-track mapping (lane 1 → V2, lane −1 → A2 or the next free audio track) is the natural reading but was not confirmed for Resolve. Validate it with a test import.
- Treat FCPXML markers and keyframed zooms as "nice if they survive". Always also ship the marker EDL. Encode zooms as a static `adjust-transform scale` on a separate B-roll/adjustment piece rather than as keyframes.
- To get a zoom-in on the A-roll itself, split the spine clip at the zoom boundaries and give the middle segment `adjust-transform scale="1.2 1.2"`. Whether "Use sizing information" must be ticked for this to apply needs testing.

### Gaps
- No primary Blackmagic statement on which FCPXML versions Resolve 20.x or 21.x import. Blackmagic sites were unreachable; the 21-beta FCPXML headline and the "FCP 12 FCPXML" changelog line could not be read.
- Unconfirmed for Resolve 19–21: FCPXML `marker`/`chapter-marker` import (and what color they get), `completed` to-do markers, `adjust-transform` keyframes on video clips, and `title` elements.
- Unconfirmed how `audioRole` maps to Resolve audio tracks.

## Q3. OpenTimelineIO (.otio)

### Takeaway
Resolve has imported and exported `.otio` natively since **18.5**, in both Free and Studio, via File > Import > Timeline. 18.6.5 added compound clips and clip markers. OTIO is a good multi-track alternative to FCPXML for generating files in Python, using the `opentimelineio` library. It has no standard way to express transforms or zooms, so markers and the cut/B-roll/SFX layout are what reliably travel.

### Cited Findings
- The DaVinci Resolve 18.5 release notes list "import and export timelines using the OpenTimelineIO format" — [Newsshooter, 18.5 announced](https://www.newsshooter.com/2023/04/16/davinci-resolve-18-5-announced/)
- 18.6.5 added import/export of compound clips in OTIO "and clip markers" — [RedShark News](https://www.redsharknews.com/blackmagic-releases-davinci-resolve-18.6.5)
- Export is via File > Export > Timeline: `.otio` holds the timeline only, `.otioz` bundles the media. Version 18.5 or later is required — [ASWF OTIO wiki, AWS Picchu conversion notes](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/wiki/AWS-Picchu-Edit-OTIO-Conversion-Notes)
- The scripting API's `MediaPool.ImportTimelineFromFile(filePath, {importOptions})` accepts AAF/EDL/XML/FCPXML/DRT/ADL/OTIO, with these options:
  - `timelineName`
  - `importSourceClips` (default True)
  - `sourceClipsPath`: a folder to search when media is missing
  - `sourceClipsFolders`
  - `interlaceProcessing` (AAF only)

  — [Resolve scripting README mirror](https://github.com/LenNerd42/DaVinciResolveAPI/blob/HEAD/docs/README.md)
- Library status, verified locally via PyPI install: OpenTimelineIO **0.18.1**. CMX3600, FCPXML, FCP7 XML and AAF are separate plugin packages (`otio-cmx3600-adapter` 1.0.0, `otio-fcpx-xml-adapter` 1.0.0, `otio-fcp-adapter` 1.0.0, `otio-aaf-adapter` 2.0.0, which needs `pyaaf2>=1.7.0`). The adapters available after install were `['cmx_3600','fcpx_xml','fcp_xml','otio_json','otioz','otiod']` — [OpenTimelineIO on PyPI](https://pypi.org/project/OpenTimelineIO/); [otio-aaf-adapter on PyPI](https://pypi.org/project/otio-aaf-adapter/)
- OTIO 0.18.1 writes the schemas `Timeline.1`, `Stack.1`, `Track.1`, `Clip.2`, `Gap.1`, `ExternalReference.1` and `Marker.2` (verified locally). Fixtures modelled on Resolve exports use the same versions, carry `"metadata": {"Resolve_OTIO": {"Resolve OTIO Meta Version": "1.0"}}`, use `global_start_time` = 86400 frames at 24 fps (01:00:00:00), and write markers as `{"OTIO_SCHEMA":"Marker.2","color":"BLUE","name":…,"comment":…}`. These fixtures were not confirmed to be raw Resolve output — [veo_studio resolve.otio fixture](https://github.com/tatvama/veo_studio/blob/HEAD/frontend/src/editor/interop/__fixtures__/resolve.otio); [wabcut resolve_timeline.otio fixture](https://github.com/sorsama/wabcut/blob/HEAD/tests/interchange/fixtures/resolve_timeline.otio)
- Community "Resolve-safe OTIO" guidance, written for agents and unverified (its failure stories are unsourced):
  - Use `TrackKind` enums, never lowercase strings.
  - Use `target_url` as a proper `file:///C:/…` URI from `pathlib.Path(...).as_uri()`, never a bare Windows path.
  - Use one frame rate per track.
  - Never leave a track empty; add a Gap.
  - Use marker colors from the enum (PINK, RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, MAGENTA, BLACK, WHITE).
  - Never write negative durations or a zero rate.
  - Set `metadata["Resolve_OTIO"]["drop_frame"]` for 29.97/59.94.
  - Test-import into a throwaway project first. It claims malformed OTIO can crash Resolve or corrupt the .drp.

  — [BlueMediaRiot otio-timeline skill, resolve_compatibility.md](https://github.com/BlueMediaRiot/training-video-antigravity/blob/HEAD/.agents/skills/otio-timeline/resolve_compatibility.md)
- An NLE exporter's OTIO writer notes that OTIO "has no standard for levels, motion or fades". It keeps those in clip metadata, which "the editor ignores" — [yt-cartell-studio otio.go](https://github.com/gitkalenyuk/yt-cartell-studio-source/blob/HEAD/internal/nle/otio.go)

#### Verified generator skeleton (ran locally with OTIO 0.18.1; produces V1, V2 B-roll, A1, A2 SFX and markers)
```python
import opentimelineio as otio
from pathlib import PureWindowsPath
R = 30; RT = otio.opentime.RationalTime; TR = otio.opentime.TimeRange
def ref(win_path, dur_s):
    return otio.schema.ExternalReference(target_url=PureWindowsPath(win_path).as_uri(),
        available_range=TR(RT(0, R), RT(dur_s * R, R)))
tl = otio.schema.Timeline(name="EditPlan_v1"); tl.global_start_time = RT(3600 * R, R)   # 01:00:00:00
v1, v2 = (otio.schema.Track(name=n, kind=otio.schema.TrackKind.Video) for n in ("V1", "V2 B-roll"))
a1, a2 = (otio.schema.Track(name=n, kind=otio.schema.TrackKind.Audio) for n in ("A1 Voice", "A2 SFX"))
tl.tracks.extend([v1, v2, a1, a2])
main = r"C:\Users\Ahmad\Videos\Project\a-roll.mp4"
for t in (v1, a1):
    t.append(otio.schema.Clip(name="a-roll", media_reference=ref(main, 600), source_range=TR(RT(0, R), RT(60 * R, R))))
v2.append(otio.schema.Gap(source_range=TR(RT(0, R), RT(375, R))))            # 12.5 s
v2.append(otio.schema.Clip(name="broll market", media_reference=ref(r"C:\Users\Ahmad\Videos\B-roll\broll market.mp4", 20),
                           source_range=TR(RT(60, R), RT(120, R))))          # src 2 s, 4 s long
a2.append(otio.schema.Gap(source_range=TR(RT(0, R), RT(360, R))))            # 12.0 s
a2.append(otio.schema.Clip(name="whoosh", media_reference=ref(r"C:\Users\Ahmad\Videos\SFX\whoosh.wav", 2),
                           source_range=TR(RT(0, R), RT(30, R))))
tl.tracks.markers.append(otio.schema.Marker(name="ZOOM 120%", color=otio.schema.MarkerColor.RED,
    marked_range=TR(RT(600, R), RT(15, R)), comment="punch-in on punchline"))
otio.adapters.write_to_file(tl, "plan.otio")
```

### Inferences
- OTIO is easier to generate correctly than FCPXML. Gap-padded tracks map one-to-one to Resolve tracks, with no parent-relative lane arithmetic.
- Unconfirmed: whether Resolve maps marker `comment` to the marker note, and stack-level markers to timeline markers. Both are plausible.
- OTIO cannot express the zoom. Use markers, or a separate FCPXML, for zooms.

### Gaps
- No primary list of which OTIO features Resolve 19/20/21 import: track names, marker comment/duration/color, transitions, LinearTimeWarp.
- No confirmed upper OTIO schema version that Resolve accepts.
- The "otio corrupts the project" warnings come from a single community source.

## Q4. AAF and DRT: is generating them practical?

### Takeaway
Generating AAF is technically possible (OTIO's AAF adapter plus `pyaaf2`). It is binary, harder to debug and gains nothing over FCPXML/OTIO for this job. DRT is Resolve's proprietary timeline format with no public spec. Neither is recommended.

### Cited Findings
- `otio-aaf-adapter` 2.0.0 ships `aaf_writer.py` and needs `opentimelineio>=0.17.0` and `pyaaf2>=1.7.0` (verified from the wheel's metadata) — [otio-aaf-adapter on PyPI](https://pypi.org/project/otio-aaf-adapter/)
- Resolve's API lists DRT as an import and export type (`resolve.EXPORT_DRT`). Several `ImportTimelineFromFile` options are "Not valid for DRT import" — [Resolve scripting README mirror](https://github.com/LenNerd42/DaVinciResolveAPI/blob/HEAD/docs/README.md)
- Blackmagic's 20.1 New Features Guide has an entry about DRT timeline exports. Only its table of contents was visible via search — [DaVinci Resolve 20.1 New Features Guide (PDF)](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_20.1_New_Features_Guide.pdf)
- Avid/AAF conforms often run into a 01:00:00:00 timecode offset when sources carry no timecode — [Blackmagic Forum "Timecode mismatches when importing AAF created in Avid"](https://forum.blackmagicdesign.com/viewtopic.php?p=439783)

### Inferences
- DRT is only usable by exporting from Resolve and re-importing, for example as a template. Hand-generating it is not realistic.
- AAF only makes sense for Avid or Pro Tools hand-offs.

### Gaps
- No public DRT format documentation was found.
- No test of an `otio-aaf-adapter`-written AAF importing into Resolve was found.

## Q5. Markers: CSV import, best route, colors, names, notes, durations, scripting

### Takeaway
Resolve has **no native CSV marker import**: CSV must be converted to a marker EDL. Recommended routes, in order:
1. **Marker EDL.** Works in Free and Studio, gives exact frame, color, name and duration.
2. **FCPXML/OTIO markers** inside the timeline file. Convenient, but import fidelity is unverified.
3. **Scripting `Timeline.AddMarker`.** The only route with a separate **note** and `customData`.

From **Resolve 21.1 (8 Sep 2026)**, Python scripting and external scripting moved to **Studio**, so route 3 no longer works for Free users.

### Cited Findings
- Converter vendors say Resolve uses .edl files for marker metadata, so CSV must first be converted to a marker EDL. Their CSV needs columns "Timecode In", "Name" and "Comment", with "Colour" and "Timecode Out" optional — [editingtools.io CSV→Resolve marker guide](https://hu.editingtools.io/guides/convert-csv-to-resolve-marker); [Remoto help](https://remoto.helpjuice.com/how-to/importing-timecoded-markers-into-davinci-resolve-from-playback)
- Resolve can **export** marker and edit lists as CSV or tab-delimited text (`resolve.EXPORT_TEXT_CSV`, `EXPORT_TEXT_TAB`), but import is EDL only — [Resolve scripting README mirror](https://github.com/LenNerd42/DaVinciResolveAPI/blob/HEAD/docs/README.md)
- Scripting API marker calls: `Timeline.AddMarker(frameId, color, name, note, duration, customData)`, `GetMarkers()` and `DeleteMarkersByColor(color)` ("All" deletes all). `GetMarkers()` returns, for example, `{96.0: {'color': 'Green', 'duration': 1.0, 'note': '', 'name': 'Marker 1', 'customData': ''}}`. `customData` is "not exposed via UI" — [Resolve scripting README mirror](https://github.com/LenNerd42/DaVinciResolveAPI/blob/HEAD/docs/README.md)
- **Resolve 21.1 scripting change** (secondary coverage quoting the release notes):
  - Python scripting moved to Studio, because the Python API "was being used to hack studio features into the free version" — [CineD (ES)](https://www.cined.com/es/davinci-resolve-21-1-released-ai-assistant-integration-via-mcp-individual-hdr-trims-and-python-scripting-moves-to-studio/); [ProVideo Coalition](https://www.provideocoalition.com/davinci-resolve-21-1-is-a-huge-update/)
  - Puget says scripting was "entirely removed" from Free in 21.1 and recommends staying on 21.0 — [Puget Systems](https://www.pugetsystems.com/blog/2026/09/10/how-davinci-resolve-free-v21-1-scripting-changes-affect-puget-bench/)
  - Coverage conflicts on whether Free keeps console-only scripting: ProVideo Coalition says it does, Puget says scripting is removed entirely.
- Before 21.1, Free could run scripts only from inside Resolve (Workspace > Scripts / Console). External scripting needed Studio — [Arch Wiki DaVinci Resolve](https://wiki.archlinux.org/title/DaVinci_Resolve)
- 21.1 adds a **native MCP server in Studio**, which coverage says exposes about 88 tools for AI assistants like Claude. It needs External scripting set to Local in Preferences. Free does not expose the external scripting connection — [byteiota](https://byteiota.com/?p=22448); [Digital Production](https://digitalproduction.com/2026/09/08/resolve-21-1-adds-mcp-and-finally-gets-presets/); [No Film School](https://nofilmschool.com/davinci-resolve-update-21-1)
- **YouTube chapters:** on export, Resolve's "Chapters from markers" option takes all markers of one chosen color as chapters. Keep chapter markers in a dedicated color — [MediaZilla](https://support.mediazilla.com/en/articles/12143932-working-with-chapters-in-davinci-resolve)
- Ready-made converters that write Resolve marker EDLs:
  - SRT → marker EDL in Python — [feureau srtToEDL.py](https://github.com/feureau/Small-Scripts/blob/HEAD/Programming/srtToEDL.py)
  - XLS → marker EDL — [snorkem/xls-to-resolve-edl](https://github.com/snorkem/xls-to-resolve-edl)
  - REAPER regions → marker EDL with duration — [X-Raym ReaScript](https://github.com/X-Raym/REAPER-ReaScripts/blob/HEAD/Regions/X-Raym_Export%20markers%20and%20regions%20as%20Davinci%20Resolve%20EDL%20file.lua)
  - SubtitleEdit reads and writes the format natively — [SubtitleEdit](https://github.com/SubtitleEdit/subtitleedit/blob/HEAD/src/libse/SubtitleFormats/DaVinciResolveMarkerEdl.cs)

### Inferences
- The skill should always emit `markers.edl` as the universal fallback. It is the only marker route confirmed for Free 21.1 or later without scripting.
- Put the actionable instruction in `|M:`, and keep the longer rationale in the skill's human-readable edit plan.
- Keep at most one marker per frame. If two actions fall on the same frame, merge them into one name.
- Reserve one color for chapter markers so the user can use "Chapters from markers" on export.

### Gaps
- `AddMarker`'s `frameId` is presumably relative to the timeline start (GetMarkers keys like 96.0 suggest so), but this was not confirmed.
- The exact color-name strings accepted by `AddMarker` in 21.x were not confirmed (presumably "Blue", "Cyan" and so on).
- The exact 21.1 Free/Studio split for console scripting is unresolved because coverage conflicts.

## Q6. Subtitles: SRT import, formats, Arabic/RTL, burn-in

### Takeaway
SRT import into a subtitle track works in **Free**: File > Import > Subtitle, or right-click a Media Pool bin, then drag to the timeline. Studio is only needed for AI "Create Subtitles from Audio", and that feature did not support Arabic as of the 2024 API doc. Arabic/RTL rendering in Resolve's subtitle track and Text+ has a long history of bugs: letters not joining, text hidden when stroke > 0. Some reports say it works in recent versions, but none is verified, so the skill should tell the user to test one caption first.

### Cited Findings
- Import route: "File > Import > Subtitle…" creates subtitle data in the Master Bin, which is then placed on a subtitle track — [Blackmagic Forum (via search)](https://forum.blackmagicdesign.com/viewtopic.php?f=32&t=72007). The right-click "Import Subtitle" in the Media Pool is the same — [GoTranscript](https://gotranscript.com/blog/create-subtitles-davinci-resolve-import-srt-timing-export)
- **Formats:** HappyScribe lists SRT, VTT, XML and TTML — [HappyScribe](https://help.happyscribe.com/en/articles/6087119-how-to-import-captions-in-davinci-resolve). Rev lists SRT or FCPXML — [Rev](https://www.rev.com/blog/how-to-add-captions-and-subtitles-to-davinci-resolve-studio). The sources conflict, and no manual page was reachable.
- **Free vs Studio:** Free supports manual subtitle tracks and SRT import; transcription-based subtitle generation needs Studio. Match the timeline frame rate before importing an SRT to avoid drift — [GoTranscript](https://gotranscript.com/blog/create-subtitles-davinci-resolve-import-srt-timing-export)
- Delivery options: a separate subtitle file, embedded captions, or burn-in on the Deliver page — [Sonix](https://sonix.ai/ai/add-subtitles-davinci-resolve/)
- AI subtitle languages in the API (Oct 2024 doc): Auto, Danish, Dutch, English, French, German, Italian, Japanese, Korean, Mandarin (Simplified/Traditional), Norwegian, Portuguese, Russian, Spanish, Swedish. **No Arabic** — [Resolve scripting README mirror](https://github.com/LenNerd42/DaVinciResolveAPI/blob/HEAD/docs/README.md). A 2026 third-party guide also says Arabic is not on the transcription list and that full RTL layout, including mixed Arabic-Latin punctuation, is not built into the subtitle track — [Uncle (tryuncle.com)](https://tryuncle.com/learn/davinci-resolve/subtitles)
- **Arabic history:**
  - Resolve 17.4 announced Text+ support for combined glyphs and RTL, but users said the Edit-page controls were missing — [Blackmagic Forum "[done in 17.4] Add support for RTL languages"](https://forum.blackmagicdesign.com/viewtopic.php?f=33&t=147194)
  - Arabic rendered in "Text" but letters stayed disconnected in Text+ — [Blackmagic Forum "Arabic does not show properly in Text+"](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=143060)
  - In the Resolve 18 beta, Arabic subtitle captions disappeared when stroke > 0 — [Blackmagic Forum](https://forum.blackmagicdesign.com/viewtopic.php?p=845503)
  - A user reported being unable to insert an Arabic .srt into the timeline — [Blackmagic Forum](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=176547)
  - A short forum reply claims Arabic support arrived in v20 (unverified) — [Blackmagic Forum "Request for Arabic Language Support"](https://forum.blackmagicdesign.com/viewtopic.php?f=33&t=212513)
- A plugin vendor claims Text+ now joins letters and renders RTL with fonts like Cairo or Noto Naskh Arabic (marketing, unverified) — [xere.my](https://xere.my/video/captions/davinci-resolve-arabic-subtitles/)
- In other NLEs, RTL text from SRT often appears reversed. Fixes involve BiDi handling or Unicode embedding marks (U+202B…U+202C) per cue; these marks fix reading direction, not letter joining — [Adobe Community thread](https://community.adobe.com/t5/premiere-pro-discussions/srt-import-with-right-to-left-language-e-g-hebrew-arabic-text-is-reversed/m-p/13201694); [videodubbing RTL subtitle fixer](https://videodubbing.com/tools/rtl-subtitle-fixer/)

### Inferences
- Have the skill write a UTF-8 SRT (no BOM, or with one if Resolve misreads; to test) with frame-snapped times. Keep cues short: Syrian-dialect captions of 1–2 lines and about 42 characters.
  - Wrapping each cue in RLE/PDF or RLM marks can be offered as an optional fix if punctuation lands on the wrong side.
  - Keep stroke at 0 on first test, and pick an Arabic-capable font such as Noto Naskh Arabic or Cairo.
- If subtitle-track rendering fails on his version, fall back to Text+ titles, or burn captions in with an external tool such as ffmpeg/libass, which shapes Arabic properly. Resolve then just carries a video overlay.

### Gaps
- No primary list of import formats (VTT/TTML/ITT/STL) for Resolve 20/21.
- No confirmed status of Arabic shaping or RTL in the Resolve 20/21 subtitle track versus Text+.
- No confirmed SRT BOM behavior.

## Q7. Timecode math: start TC, frame rates, drop-frame, seconds → frames

### Takeaway
Work internally in **integer frames at the exact rational rate**, and format to timecode only at output.
- Resolve timelines default to start **01:00:00:00**. Every marker EDL record TC, and FCPXML `tcStart`/spine offset, must include that offset.
- Drop-frame (`;` separator, `FCM: DROP FRAME`, FCPXML `tcFormat="DF"`) applies only to 29.97 and 59.94.
- With DF, 01:00:00;00 is frame 107,892 at 29.97, not 108,000.

### Cited Findings
- vodcue: Resolve places a marker at the record-in TC read as an **absolute** timeline position, so record TCs must be pre-offset by the timeline start. Its documented default is `--timeline-start 01:00:00:00` — [vodcue](https://github.com/wdominik/vodcue/blob/HEAD/README.md)
- The scripting API has `Timeline.GetStartFrame()`, `GetStartTimecode()` and `SetStartTimecode(timecode)`, so start TC is a per-timeline setting — [Resolve scripting README mirror](https://github.com/LenNerd42/DaVinciResolveAPI/blob/HEAD/docs/README.md)
- auto-editor's SMPTE parser treats `;` as drop-frame. It subtracts `d × (totalMinutes − totalMinutes div 10)` frames with `d = round(fps)/15`, which is 2 at 29.97 and 4 at 59.94 — [auto-editor fcp11.nim parseSMPTE](https://github.com/WyattBlue/auto-editor/blob/HEAD/src/exports/fcp11.nim)
- The SubtitleEdit writer emits `FCM: DROP FRAME` when the frame rate is fractional — [SubtitleEdit](https://github.com/SubtitleEdit/subtitleedit/blob/HEAD/src/libse/SubtitleFormats/DaVinciResolveMarkerEdl.cs). Real Resolve marker EDL fixtures at 29.97/59.94 use `00:00:58;00 00:00:58;01` DF timecodes — [Aagedal 2997.edl fixture](https://github.com/aagedal/Aagedal-Media-Converter/blob/HEAD/Aagedal%20Media%20ConverterTests/Fixtures/StitchMarkers/2997.edl)
- Verified locally: my converter matched OTIO's `opentime.to_timecode` for all 8 rates. Results for "12.5 s from the transcript" on a 01:00:00:00 timeline:

  | Rate | 12.5 s → | 600 s → |
  |---|---|---|
  | 23.976 | 01:00:12:12 | 01:09:59:10 (NDF) |
  | 24 / 25 | 01:00:12:12 | — |
  | 29.97 DF | 01:00:12;15 | 01:10:00;00 |
  | 30 | 01:00:12:15 | — |
  | 50 | 01:00:12:25 | — |
  | 59.94 DF | 01:00:12;29 | — |
  | 60 | 01:00:12:30 | — |

  At 29.97 **NDF**, 600 s of real time (17,982 frames) labels as 01:09:59:12, about 18 frames behind wall clock. FCPXML for 12.5 s at 29.97 snaps to 375 frames = `375375/30000s` — [OpenTimelineIO on PyPI](https://pypi.org/project/OpenTimelineIO/)

#### Verified Python (frame-exact; DF per SMPTE)
```python
from fractions import Fraction
RATES = {"23.976":(24,Fraction(24000,1001)),"24":(24,Fraction(24)),"25":(25,Fraction(25)),
         "29.97":(30,Fraction(30000,1001)),"30":(30,Fraction(30)),"50":(50,Fraction(50)),
         "59.94":(60,Fraction(60000,1001)),"60":(60,Fraction(60))}
def seconds_to_frame(sec, rate):            # transcript seconds are wall-clock seconds of the audio
    return round(Fraction(str(sec)) * rate)  # nearest frame (use floor for cut-ins that must not precede a word)
def frames_to_tc(frames, base, drop=False):
    if drop:
        d = 2 if base == 30 else 4
        per10 = base*600 - d*9; per1 = base*60 - d
        tens, rem = divmod(frames, per10)
        frames += d*9*tens + (d*((rem - d)//per1) if rem > d else 0)
    ff = frames % base; s = frames // base
    return f"{s//3600:02d}:{s//60%60:02d}:{s%60:02d}{';' if drop else ':'}{ff:02d}"
# timeline start frame: NDF -> 3600*base ; DF 29.97 -> 107892 ; DF 59.94 -> 215784
```

### Inferences
Common pitfalls:
1. Forgetting the 01:00:00:00 offset, so markers fall before the timeline and do not import.
2. Using 30 instead of 30000/1001 for 29.97 material, which drifts about 1.8 s per 30 min.
3. Formatting 29.97 as NDF when the timeline is DF, or the reverse.
4. Using float seconds in FCPXML instead of frame-snapped rationals.
5. Computing the EDL record-out as in+duration for markers, when Resolve's own format is in+1 with `|D:` holding the length.
6. `round` versus `floor` at boundaries: a B-roll "at 12.5 s" should normally start on or just after the word onset.

The skill should ask, or read from his project, the timeline frame rate and start TC. Default to 01:00:00:00 and his footage fps. For a YouTuber that is typically 30, 29.97 or 25.

### Gaps
- Resolve's default fps for new projects (often 24) and whether his projects use DF at 29.97 must be confirmed with the user.
- No Blackmagic primary source for the 01:00:00:00 default was reachable. It is widely assumed and stated by vodcue.

## Q8. Media relinking on Windows

### Takeaway
FCPXML and OTIO carry absolute `file:///C:/…` URLs, percent-encoded as UTF-8. On import Resolve can "automatically import source clips into Media Pool" and search an extra folder (`sourceClipsPath`). Clips not found come in **offline**, and the user relinks them by pointing Resolve at the folder. EDLs carry no paths, so media must be in the Media Pool first and matched by reel/name/TC.

### Cited Findings
- The `ImportTimelineFromFile` options `importSourceClips` (default True), `sourceClipsPath` ("a filesystem path to search for source clips if the media is inaccessible in their original path") and `sourceClipsFolders` (Media Pool folders to search when not importing source clips) mirror the import dialog — [Resolve scripting README mirror](https://github.com/LenNerd42/DaVinciResolveAPI/blob/HEAD/docs/README.md)
- Resolve does not resolve relative URLs in FCPXML; use absolute `file://` URLs — [yt-cartell-studio fcpxml.go](https://github.com/gitkalenyuk/yt-cartell-studio-source/blob/HEAD/internal/nle/fcpxml.go)
- On Windows, auto-editor writes `file:///` + the path with forward slashes, percent-encoding everything outside the RFC 3986 unreserved set plus `/` and `:` — [auto-editor fun.nim](https://github.com/WyattBlue/auto-editor/blob/HEAD/src/util/fun.nim)
- In OTIO, bare Windows paths with backslashes are reported to cause Resolve path-resolver problems; use `pathlib.Path(...).as_uri()` (community guidance) — [BlueMediaRiot resolve_compatibility.md](https://github.com/BlueMediaRiot/training-video-antigravity/blob/HEAD/.agents/skills/otio-timeline/resolve_compatibility.md)
- XML exchange references media by path rather than embedding it, so the files must exist at the target — [Tella XML import/export definition](https://www.tella.com/definition/xml-import-export)
- Old reports (FCPX→Resolve) of clips that "can't be linked to media files" usually come down to path, timecode or extent mismatches — [Blackmagic Forum "Clips can't be linked to media files (from FCPX)"](https://forum.blackmagicdesign.com/viewtopic.php?f=3&t=320); [Blackmagic Forum "Failed to link because timecode extents do not match XML"](https://forum.blackmagicdesign.com/viewtopic.php?p=248665)
- In FCPXML the `asset` `start`/`duration` must describe the *source media*. auto-editor notes: "An asset's duration is that of the source media itself, not the (shorter) edited timeline". It also reads the media's embedded timecode into `asset start` — [auto-editor fcp11.nim](https://github.com/WyattBlue/auto-editor/blob/HEAD/src/exports/fcp11.nim)

### Inferences
- The skill should get each file's real duration, embedded start TC and fps with ffprobe, or ask for them. Writing a wrong `asset start`/`duration` is the classic cause of "timecode extents do not match" offline clips.
  - Most phone and stock clips have start TC 0, so `start="0s"` is right.
- Recommend one project folder, for example `D:\YouTube\EP12\{a-roll,broll,sfx}`, with the XML referencing those exact paths. If he moves the folder, he relinks once to the new root.
- Arabic and space characters in paths are fine if percent-encoded as UTF-8. Recommending ASCII file names for B-roll/SFX still removes a whole class of failures.

### Gaps
- The exact menu wording in Resolve 20/21 for relink ("Relink Selected Clips…" / "Relink Clips for Selected Bin…" / Media Pool "Change Source Folder") was not verified from the manual.
- Not verified whether Resolve on Windows accepts `file://localhost/C:/…` or un-encoded paths in FCPXML.

## Q9. Existing tools that turn edit plans or transcripts into Resolve-importable files

### Takeaway
**auto-editor** is the closest open-source analogue and a useful reference implementation. `--export resolve` writes **FCPXML 1.11** by default (1.10 optional); `resolve-fcp7` writes legacy FCP7 XML. Commercial tools split into file-export tools and Resolve plugins:
- File export: TimeBolt (XML/FCPXML/EDL), Descript (XML).
- Resolve plugins: FireCut.

Many small scripts convert SRT/CSV/XLS to Resolve marker EDLs.

### Cited Findings
- auto-editor v31.7.3 (commit c9c8ee2, 21 Oct 2026) — [skill doc](https://github.com/WyattBlue/auto-editor/blob/HEAD/skills/auto-editor-export/SKILL.md); [fcp11.nim](https://github.com/WyattBlue/auto-editor/blob/HEAD/src/exports/fcp11.nim); [fcp7.nim](https://github.com/WyattBlue/auto-editor/blob/HEAD/src/exports/fcp7.nim):
  - Export targets: `premiere` → fcp7 .xml; `resolve` → .fcpxml; `resolve-fcp7` → .xml; `final-cut-pro` → .fcpxml; plus shotcut, kdenlive, clip-sequence and v1/v2/v3 JSON timelines.
  - `resolve` and `final-cut-pro` accept `version=11` (default, FCPXML 1.11) or `version=10`.
  - The FCPXML writer uses the FCP Cross Dissolve uid (Resolve matches by name).
  - For Resolve it emits extra audio-track clips into the spine.
  - Its FCP7 Resolve path needs `<duration>` "present but empty" and only supports a single video track ("resolve-fcp7's link/id scheme is wired for a single video track").
- The auto-editor changelog for 31.7.3 adds `burn` (draw .srt/.ass subtitles over a section) and `text` actions. It uses whisper.cpp 1.9.5 — [auto-editor CHANGELOG](https://github.com/WyattBlue/auto-editor/blob/HEAD/CHANGELOG.md)
- TimeBolt's guide: cut in TimeBolt, then import into Resolve as **XML** with cuts preserved. A Resolve extension handles complex projects. Its export menu lists EDL, FCPXML and XML — [TimeBolt Notion guide](https://timebolt.notion.site/Export-XML-for-Davinci-Resolve-TimeBolt-f558a32dba7f4f87a858116c5091fdb7)
- FireCut for Resolve is a **plugin** inside Resolve, not a file export. It covers captions, silence removal, zooms, chapters, B-roll/music search and more, and is a "ground-up redesign" of its Premiere plugin — [FireCut pricing/FAQ](https://firecut.ai/pricing/davinci-resolve/); [Product Hunt](https://www.producthunt.com/p/firecut-ai/we-re-bringing-firecut-to-davinci-resolve)
- Descript exports timelines for Premiere, Resolve and FCP via XML. Users report simple cuts not translating in some cases — [GoTranscript transcript of a Descript walkthrough](https://gotranscript.com/public/move-descript-edits-into-any-post-production-workflow); [Descript feedback board](https://feedback.descript.com/features/p/davinci-resolve-support)
- No Gling documentation on its Resolve export format was found by search (gap).
- A Resolve MCP tool exports the active timeline to FCPXML 1.8/1.9/1.10, default 1.10 — [glama resolve-mcp export_fcpxml](https://glama.ai/mcp/servers/DigitalWorkflowCompany/resolve-mcp/tools/export_fcpxml)
- One NLE exporter writes FCPXML 1.10 with a Resolve flavour, plus FCP7 XML, OTIO, MLT and EDL from one model. It is a good multi-format reference — [yt-cartell-studio internal/nle](https://github.com/gitkalenyuk/yt-cartell-studio-source/tree/HEAD/internal/nle)
- Marker converters:
  - [feureau srtToEDL.py](https://github.com/feureau/Small-Scripts/blob/HEAD/Programming/srtToEDL.py) (SRT → Resolve marker EDL)
  - [snorkem/xls-to-resolve-edl](https://github.com/snorkem/xls-to-resolve-edl)
  - [vodcue](https://github.com/wdominik/vodcue) (Twitch CSV → Resolve marker EDL)
  - [editingtools.io](https://editingtools.io/guides/convert-livenotes-to-resolve-marker) (web converters)

### Inferences
- The skill can mirror auto-editor's FCPXML conventions, which are proven in the field for Resolve: `media-rep`, `tcFormat="NDF"`, stereo/48k sequence, Cross Dissolve by name. On top of that it adds lanes for B-roll and SFX and the marker EDL.
- If the user already uses auto-editor for silence cuts, the skill could post-process auto-editor's `.fcpxml`. Insert connected B-roll/SFX into the existing spine clips using parent-source-time offsets, and emit `markers.edl` against the same timeline.

### Gaps
- Gling's export format is unknown.
- No public source shows how FireCut writes into Resolve (API vs plugin SDK).

## Q10. Which format best suits "B-roll on V2 + SFX on A2 + markers with notes at exact timestamps"

### Takeaway
Ship **two files**:
1. **`edit_plan.fcpxml` (1.10)**. The A-roll is one spine clip; B-roll goes on `lane="1"` (V2) and SFX on `lane="-1"` (A2), at exact rational times. Static `adjust-transform scale` covers punch-ins, and FCPXML markers are a bonus.
2. **`markers.edl`** in Resolve's `|C:|M:|D:` dialect, imported via Timelines > Import > Timeline Markers from EDL, as the guaranteed marker layer. One color per action type.

Add `captions.srt` for captions. Use OTIO (`.otio`) as an alternative to (1) when transforms aren't needed. Avoid clip EDL, AAF and DRT. Do not rely on scripting: it is Studio-only from 21.1.

### Cited Findings
- Clip EDL is single-video-track and has no paths — [otio-cmx3600-adapter (local test)](https://pypi.org/project/otio-cmx3600-adapter/); [yt-cartell-studio edl.go](https://github.com/gitkalenyuk/yt-cartell-studio-source/blob/HEAD/internal/nle/edl.go)
- FCPXML supports connected clips by lane, absolute media URLs, markers and transforms, per the DTD and real FCP exports — [Apple DTDs (CommandPost mirror)](https://github.com/CommandPost/CommandPost/tree/HEAD/src/extensions/cp/apple/fcpxml/dtd); [nicknoonan example](https://github.com/nicknoonan/fcpxml/blob/HEAD/src/parser/example_complicated.fcpxml)
- Resolve imports FCPXML and OTIO in Free; the marker EDL route is long-established — [SubtitleEdit](https://github.com/SubtitleEdit/subtitleedit/blob/HEAD/src/libse/SubtitleFormats/DaVinciResolveMarkerEdl.cs); [Newsshooter 18.5](https://www.newsshooter.com/2023/04/16/davinci-resolve-18-5-announced/)
- Scripting is Studio-only from 21.1, while 21.1 Studio adds a native MCP server — [CineD](https://www.cined.com/es/davinci-resolve-21-1-released-ai-assistant-integration-via-mcp-individual-hdr-trims-and-python-scripting-moves-to-studio/); [byteiota](https://byteiota.com/?p=22448)

### Inferences
User workflow, with no scripting:
1. Put all media in one folder.
2. File > Import > Timeline > `edit_plan.fcpxml`, keeping "automatically import source clips" and "use sizing information" on.
3. Right-click the new timeline > Timelines > Import > Timeline Markers from EDL > `markers.edl`.
4. File > Import > Subtitle > `captions.srt`, then drag it onto the timeline.

Generator rules:
- Use exact rational frame math at the user's timeline fps.
- Start at 01:00:00:00.
- Percent-encode `file:///C:/…` URLs.
- Use one marker per frame, at most 999 markers, with names under about 60 characters and no `|`.
- Run a validation pass: xmllint against the 1.10 DTD, and assert every child offset lies within its parent clip's `[start, start+duration)`.

If he has Studio 21.1 or later, a later version of the skill could drive Resolve directly through the native MCP server or the API (`AppendToTimeline` with `trackIndex`/`recordFrame`, `AddMarker` with notes). That is an upgrade path, not the baseline.

### Gaps
- None of the recommended files was test-imported into an actual Resolve 19/20/21 build. A one-time smoke test on the user's machine should confirm three things:
  - FCPXML lane → track mapping.
  - Whether markers and `adjust-transform` survive.
  - That Arabic text renders in the subtitle track and in marker names.
