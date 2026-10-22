# Claude skills workspace

- `skills/editor/` — the **/editor** skill: Claude plans and places zooms, B-roll, sound effects, text pop-ups,
  freeze frames and chapters in DaVinci Resolve (Free 21.0.x) through its own bridge script, shows a visual
  plan sheet first, and learns from every change. Install: copy the `editor` folder to
  `%USERPROFILE%\.claude\skills\editor`, then say `/editor` in Claude Code and it runs first-time setup.
- `reports/` — research reports (e.g. the DaVinci Resolve editing assistant research behind /editor).
- `research_notes/` — the source notes behind each report.

Test the editor skill without Resolve: `python skills/editor/tests/test_pipeline.py` (needs ffmpeg, numpy,
Pillow and Edge/Chrome; uses a fake Resolve).
