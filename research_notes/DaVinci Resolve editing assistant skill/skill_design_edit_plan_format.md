# Designing a Claude Agent Skill (SKILL.md) for a Human-in-the-Loop DaVinci Resolve Editing Assistant, and the Ideal "Edit Plan" Deliverable (as of Oct 22, 2026)

Research notes for the report writer. Scope: (1) Agent Skill authoring practice and file layout; (2) edit-plan deliverable formats for a non-coder Syrian-Arabic YouTuber on Windows 11 who edits in DaVinci Resolve. Research method note: several primary pages (blackmagicdesign.com, forum.blackmagicdesign.com, pugetsystems.com, nofilmschool.com, digitalproduction.com, primalvideo.com, davinciresolve21.com, thomasjfrank.com, agentskills.io) failed DNS resolution from the research sandbox, so for those the findings come from search-engine result summaries. Each such item is marked "(search summary; page not fetched)". Pages fetched in full: Anthropic best-practices doc, Claude Code skills doc, Anthropic engineering blog, anthropics/skills skill-creator SKILL.md, Claude vision doc, samuelgursky/davinci-resolve-mcp README, saadk408/davinci-resolve-lua-mcp README.

**Most important time-sensitive finding:** DaVinci Resolve 21.1 (released around early September 2026) (a) moved Python scripting and the external scripting API to the paid Studio edition, and (b) added a native, Studio-only MCP "AI Assistance" integration that supports Claude Code. This changes which "push the plan into Resolve" options work for this user. It depends on whether he runs free or Studio, and which version. **The skill must ask which edition and version he has, and branch on the answer.**

---

## 1. What do Anthropic's official Agent Skills docs and best practices say (frontmatter, length, progressive disclosure, descriptions, scripts, evals, sync, 2026 updates)?

### Takeaway
Treat SKILL.md as a short table of contents. Keep it under 500 lines, with the critical rules in the first ~5,000 tokens. Put detail in `references/` files that link one level deep from SKILL.md. Put deterministic work in `scripts/` that Claude runs instead of reading. Put templates in `assets/`. The description (third person, what + when, a bit "pushy") is the only thing always in context, and it drives triggering. Build 3+ evals before writing a lot of content. The user's current 52 KB single-file `video-maker` skill breaks the 500-line guidance. After compaction it also loses everything past its first 5,000 tokens. The new skill should not copy that pattern.

### Cited Findings
**Frontmatter rules (platform / open standard)**
- `name`: max 64 characters; lowercase letters, numbers and hyphens only; no XML tags; cannot contain the reserved words "anthropic" or "claude". `description`: non-empty, max 1,024 characters, no XML tags, should say what the skill does and when to use it. — [Anthropic: Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- Gerund names are recommended (e.g., `processing-pdfs`). Noun phrases (`pdf-processing`) and action forms (`process-pdfs`) are acceptable. Avoid vague names (`helper`, `utils`) and inconsistent patterns within one collection. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- Descriptions must be in **third person** ("Processes Excel files…", not "I can help…" or "You can use…") because the description is injected into the system prompt. Claude uses the description to choose among "potentially 100+ available Skills". — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- Outside Claude Code (claude.ai uploads, Skills API), frontmatter allows only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Any other field "cause[s] a hard error on upload". — [Claude Code docs: Skills](https://code.claude.com/docs/en/skills)

**Claude Code–specific frontmatter (Oct 2026)**
- Supported fields: `name` (defaults to directory name), `description`, `when_to_use` (extra trigger context), `argument-hint`, `arguments` (named positional args), `disable-model-invocation` (only the user can invoke), `user-invocable` (false = hidden from `/` menu), `allowed-tools` (pre-approved tools for the invoking turn; clears on the next user message), `disallowed-tools`, `model`, `effort` (low–max), `context: fork` + `agent` (run in a subagent), `background`, `hooks`, `paths` (glob-limited auto-activation), `shell` (`bash` default or `powershell`), plus spec fields `metadata`, `license`, `compatibility` (max 500 chars). Unknown fields are silently ignored. — [Claude Code docs: Skills](https://code.claude.com/docs/en/skills)
- `description` + `when_to_use` together are **truncated at 1,536 characters** in the skill listing. — [Claude Code docs: Skills](https://code.claude.com/docs/en/skills)
- Substitutions available: `$ARGUMENTS`, `$0..$N`, named `$arg`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_SESSION_ID}`, etc. Docs: "Use `${CLAUDE_SKILL_DIR}` for stable paths." — [Claude Code docs: Skills](https://code.claude.com/docs/en/skills)
- Dynamic context injection: `` !`command` `` (or a fenced ```` ```! ```` block) runs before Claude sees the skill and pastes in the output. A non-zero exit aborts the whole invocation (append `|| true`). Default timeout is 2 minutes. — [Claude Code docs: Skills](https://code.claude.com/docs/en/skills)
- **Windows:** `shell: bash` fails on Windows without Git Bash ("…requires bash… but Git Bash was not found"). `shell: powershell` runs injected commands through the PowerShell tool, which is on by default on Windows without Git Bash. — [Claude Code docs: Skills](https://code.claude.com/docs/en/skills)

**Length, context lifecycle, progressive disclosure**
- "Keep the `SKILL.md` body under 500 lines for optimal performance"; split into separate files when you get close to that. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices); same 500-line guidance in [Claude Code docs](https://code.claude.com/docs/en/skills) and [skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
- Three loading levels: (1) name + description always in context, "about 100 words"; (2) SKILL.md body when the skill triggers; (3) bundled resources as needed, with no stated limit. "Scripts can run without being loaded." — [skill-creator SKILL.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md); same model in [Anthropic engineering blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- **Context lifecycle in Claude Code:** full skill content stays in context for the rest of the session and is not re-read from disk. "After compaction, the most recent invocation of each skill is re-attached, keeping the first 5,000 tokens each, within a combined 25,000-token budget." — [Claude Code docs: Skills](https://code.claude.com/docs/en/skills)
- Keep references **one level deep** from SKILL.md. With nested references Claude may only `head -100` a file and get incomplete information. Reference files over 100 lines should start with a table of contents. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices). skill-creator gives the TOC threshold as 300 lines instead. — [skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) (minor conflict between the two; the official doc says 100)
- Organize by domain or variant so only the relevant file loads (e.g., `reference/finance.md`, `reference/sales.md`). Name files descriptively, not `doc2.md`. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- skill-creator anatomy: `SKILL.md` (required); `scripts/` (executable code for deterministic or repeated tasks); `references/` (docs loaded into context as needed); `assets/` (files used in output: templates, icons, fonts). — [skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)

**Writing style, degrees of freedom, workflows**
- "Default assumption: Claude is already very smart." Only add context Claude doesn't already have. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- Match freedom to fragility. Use low freedom ("Run exactly this script… Do not modify the command") for fragile, sequence-critical operations. Use high freedom for judgment tasks. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- For complex tasks, give a copyable checklist ("Copy this checklist and track your progress") plus a validate → fix → repeat feedback loop. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- Template pattern: "ALWAYS use this exact template structure" for strict outputs. Use input/output example pairs when style matters. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- skill-creator tells authors to use imperative instructions, explain the *why*, and avoid heavy capital-letter ALWAYS/NEVER. It also says descriptions should be "pushy" because "Claude tends to undertrigger skills". — [skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
- Avoid time-sensitive statements. Put deprecated info in an "Old patterns" `<details>` section. Use consistent terminology. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

**Scripts**
- "Solve, don't defer": scripts should handle errors themselves rather than fail and leave the fix to Claude. No "voodoo constants". — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- Pre-made utility scripts are more reliable than generated code, save tokens and time, and keep runs consistent. Say clearly whether Claude should **run** a script or **read** it. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- **Plan-validate-execute:** "analyze → create plan file → validate plan → execute → verify", using an intermediate structured file (e.g., `changes.json`) checked by a script. Use it for batch, destructive or high-stakes operations. Validators should give verbose, specific errors. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- "Use visual analysis": convert inputs to images (e.g., `pdf_to_images.py`) so Claude can look at them. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- Use forward slashes in paths inside skills, even on Windows. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- Name MCP tools fully as `ServerName:tool_name`. Don't assume packages are installed; state the dependencies. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

**Evaluation and testing**
- "Create evaluations BEFORE writing extensive documentation." Find gaps by running without the skill, build **three** scenarios, measure a baseline, write minimal instructions, iterate. Example eval JSON: `{"skills":[...],"query":...,"files":[...],"expected_behavior":[...]}`. "There is not currently a built-in way to run these evaluations." — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- Test with Haiku, Sonnet and Opus. Use a "Claude A" (author) / "Claude B" (fresh tester) loop. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- skill-creator workflow: 2–3 realistic prompts in `evals/evals.json`; with-skill vs baseline runs; `grading.json` (`text`, `passed`, `evidence`); `python -m scripts.aggregate_benchmark` → `benchmark.json/.md`; an HTML viewer (`eval-viewer/generate_review.py`) for human feedback → `feedback.json`. — [skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
- Description optimization: 20 trigger queries (8–10 should-trigger, 8–10 near-miss should-not). `python -m scripts.run_loop --max-iterations 5` uses a 60/40 train/test split and runs each query 3×. It needs `claude -p`, so it works in Claude Code and Cowork but not claude.ai. — [skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)

**Where skills live and how they sync**
- Personal: `~/.claude/skills/<name>/SKILL.md` ("All your projects (not Cowork or cloud sessions)"). Project: `.claude/skills/`. Plugin: `<plugin>/skills/<name>/SKILL.md`, invoked as `/plugin-name:skill-name`. claude.ai account skills reach "Cowork, cloud, and signed-in terminal sessions". — [Claude Code docs: Skills](https://code.claude.com/docs/en/skills)
- **claude.ai sync:** "terminal sessions download account skills into `~/.claude/skills/synced/`. Local edits are overwritten on the next sync. Requires v2.1.273+." Don't name a skill folder `synced`. — [Claude Code docs: Skills](https://code.claude.com/docs/en/skills)
- Live change detection picks up edits without a restart. A new top-level skills dir needs `/reload-skills`. `.claude/commands/*.md` still works, but skills are preferred. — [Claude Code docs: Skills](https://code.claude.com/docs/en/skills)
- Sharing: commit project skills, distribute plugins through a marketplace, or use managed settings. Access control: `Skill(name)` permission rules or `skillOverrides` (`on`/`name-only`/`user-invocable-only`/`off`). — [Claude Code docs: Skills](https://code.claude.com/docs/en/skills)
- **Versioning:** the Claude Code skills page documents no skill `version` field, only feature-level Claude Code version requirements. — [Claude Code docs: Skills](https://code.claude.com/docs/en/skills) (`metadata` is an allowed spec field and could hold a version string; that is an inference, not documented)
- Timeline: engineering blog published Oct 16, 2025. Updated Dec 18, 2025: "We've published Agent Skills as an open standard for cross-platform portability." Skills work in Claude.ai, Claude Code, the Agent SDK and the Developer Platform. — [Anthropic engineering blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- Security: "We recommend installing skills only from trusted sources." Review bundled files, dependencies and any network-connecting instructions. — [Anthropic engineering blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### Inferences
- **The 5,000-token compaction rule matters a lot for this user.** His `video-maker` skill is ~52 KB, roughly 13k tokens. After compaction only its first ~5k tokens come back, so rules placed later (licensing, "ask before installing", checkpoints) can silently drop out of context in long editing sessions. In the new skill, put the non-negotiable rules (plain short Syrian-Arabic chat, no installs or downloads without OK, licensed footage only, approval checkpoints, load the `_brain` memory) in the **first ~60 lines** of SKILL.md. Keep the whole body well under 500 lines (target 200–350).
- **Synced vs local copy:** in this session the user's existing skill shows up as `anthropic-skills:video-maker`, i.e. a claude.ai account skill synced into `~/.claude/skills/synced/`. Local edits to a synced copy get overwritten. The new skill should be authored either (a) in claude.ai, so it syncs everywhere, with frontmatter limited to the six claude.ai-allowed fields, or (b) as a personal skill in `%USERPROFILE%\.claude\skills\<name>\`, where Claude Code–only fields like `shell: powershell`, `argument-hint` or `disable-model-invocation` can be used but it won't reach Cowork/cloud. For a Windows-only Resolve workflow, option (b) is reasonable. Option (a) is safer if he also uses Cowork. If he uploads to claude.ai, do **not** include `shell`, `when_to_use`, `argument-hint`, etc. (hard error).
- **Suggested name:** `editing-in-resolve` or `resolve-edit-planner` (≤64 chars, lowercase/hyphens, no "claude"). It should stay clearly distinct from `video-maker`.
- **Description draft** (third person, pushy, with Arabic trigger words since he types in Syrian Arabic; well under 1,024 chars). Example: *"Plans edits for the user's own recorded footage (Syrian Rubik / SRB Gamer) in DaVinci Resolve. Analyzes a video's transcript and frames, then produces a timecoded edit plan: which B-roll clip goes at which second, zooms/punch-ins, SFX, transitions and captions, as a printable sheet plus Resolve marker/subtitle files and optional Resolve scripts. Use whenever the user wants to edit, cut, polish or add B-roll/zooms/sound effects/captions to a recorded video, mentions DaVinci, Resolve, timeline, markers, montage, مونتاج, دافينشي, بي رول, زوم, مؤثرات صوتية, ترجمة. Not for writing scripts or making animations from scratch (use video-maker)."* Then run skill-creator's description loop with near-miss negatives taken from `video-maker` prompts.
- Use `${CLAUDE_SKILL_DIR}/scripts/...` in commands so scripts resolve no matter what the working directory is. On Windows the expanded path may contain backslashes; the scripts should accept either.
- Dynamic injection (`!command`) could auto-load `_brain\edit-preferences.md`. But a non-zero exit aborts the skill, and on Windows the shell choice matters. A plain instruction ("Read these files first") is more robust for a non-coder.

### Gaps
- Could not fetch agentskills.io (DNS failure), so the open-standard spec's exact token guidance and its `skills-ref` validator were not verified.
- No official skill-versioning mechanism was found in the docs fetched. Plugins/marketplaces may carry versions in `plugin.json`, but this was not verified.
- The "100 lines" (official doc) vs "300 lines" (skill-creator) TOC threshold is a minor conflict. Use the official doc's 100.

---

## 2. What existing public skills, MCP servers and tools cover video/media work and DaVinci Resolve, and how are they structured?

### Takeaway
No canonical public "Resolve edit-plan" skill exists. The ecosystem has (a) code-generation skills (Remotion) and ffmpeg pipeline skills built as SKILL.md + `rules/*.md` + scripts, and (b) several DaVinci Resolve MCP servers. Most of those servers need Resolve **Studio** external scripting. The landscape shifted in Sept 2026: Resolve 21.1 moved Python/external scripting to Studio and added a native Studio-only MCP "AI Assistance" that supports Claude Code. On the free edition, only Lua scripts from `Workspace > Scripts` reportedly still run, and that comes from a third-party source.

### Cited Findings
**Video/media skills**
- The official Remotion skill for Claude Code "went viral in January 2026, with 6M+ views… 25k+ installs in the first week" (third-party roundup; marketing-ish). — [Tella: best Claude Code skills 2026](https://www.tella.com/blog/best-claude-code-skills)
- A Remotion best-practices skill copy (calesthio/openmontage) defers to a rules file: "For video operations such as trimming videos or detecting silence, FFmpeg should be used. Load the ./rules/ffmpeg.md file". This is progressive disclosure through a `rules/` folder. — [claudeskills.info: remotion-best-practices](https://claudeskills.info/ja/skills/calesthio/openmontage/remotion-best-practices/)
- affaan-m/everything-claude-code `video-editing` skill (added March 2026): "raw footage through FFmpeg cutting, Remotion compositions, ElevenLabs voiceover, fal.ai assets, and final polish." — [vibeindex.ai](https://vibeindex.ai/skills/affaan-m/everything-claude-code/video-editing)
- wilwaldon/Claude-Code-Video-Toolkit (Feb 2026): bundles Remotion, screen recording, a YouTube clipper (needs yt-dlp, ffmpeg, pysrt) and FFmpeg post-processing. — [GitHub](https://github.com/wilwaldon/Claude-Code-Video-Toolkit) (search summary)
- A generic FFmpeg skill covers conversion, trimming and filters with CLI and ffmpeg.wasm patterns. — [claudskills.com ffmpeg-media](https://claudskills.com/skills/ffmpeg-media/)
- One roundup warns "there are now thousands of skills on GitHub, and most are thin wrappers or abandoned experiments." — [Tella](https://www.tella.com/blog/best-claude-code-skills) (search summary)
- An MCP Market listing exists for a "DaVinci Resolve MCP - Claude Code Skill for Video Editing" (davinci-resolve-studio-automation); not inspected. — [mcpmarket.com](https://mcpmarket.com/tools/skills/davinci-resolve-studio-automation)

**DaVinci Resolve MCP servers**
- samuelgursky/davinci-resolve-mcp (README badge v4.14.4): "compound server (37 tools, recommended)" or "full granular server (390 tools)". Covers markers (timeline/item/clip, custom data, review reports), timeline editing (ripple insert, gap/overlap checks, "checked interchange" import/export), render, grading, Fusion and Fairlight. Requires Resolve 18.5+; tested on Studio 19.1.3/20.3.2/21.0.2 and **free 21.0.3 via an in-app bridge** run from Workspace > Scripts. "Resolve 21.1 moved Python scripting to Studio, so the bridge path on free 21.1 is unconfirmed." Python 3.10–3.12 is the lowest-risk range. Windows: bridge works from `%PROGRAMDATA%` and `%APPDATA%`; on builds before v2.70.3 check for a stale `fuscript.exe`. Self-described limits: "It does not judge whether an edit is good… not a replacement for an editor. Its output is a first-pass assembly." — [GitHub: samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp)
- Tooflex/davinci-resolve-mcp: 32 tools + 6 read-only resources. Needs **Studio 18+** with external scripting and 64-bit CPython 3.10 or 3.11 ("Resolve's scripting module still imports a module removed in Python 3.12"). Free edition "can start but stays disconnected". On Windows, avoid uv-managed standalone Python (fusionscript.dll crashes). — [GitHub: tooflex/davinci-resolve-mcp](https://github.com/tooflex/davinci-resolve-mcp) (search summary)
- saadk408/davinci-resolve-lua-mcp (targets **free 21.1**, measured build 21.1.0.17): "One door is still open on the free edition: `Workspace > Scripts` lists and runs Lua files." It is a Lua bridge with `add_marker` (frame, one of 16 colours, name, note, duration), `delete_markers` (needs `confirm: true`), read-only inspection including subtitle tracks, render, and `run_lua`. Caveats: Windows support "experimental"; Scripts folder `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility` (documented, "unmeasured" on Windows); free edition "mutes `print` in menu scripts"; `io`, `os.execute`, `require`, `ffi`, `debug` unavailable; "Blackmagic documents neither this Lua host nor its sandbox, so a point release can change what works"; must be relaunched after each Resolve start. — [GitHub: saadk408/davinci-resolve-lua-mcp](https://github.com/saadk408/davinci-resolve-lua-mcp)
- Community wrappers of the Resolve API's `AddMarker` expose: frame (one wrapper: "zero-based frame offset in the active timeline"), color from {Blue, Cyan, Green, Yellow, Red, Pink, Purple, Fuchsia, Rose, Lavender, Sky, Mint, Lemon, Sand, Cocoa, Cream}, name, note, duration in frames (default 1), customData. — [glama: DigitalWorkflowCompany add_timeline_marker](https://glama.ai/mcp/servers/DigitalWorkflowCompany/resolve-mcp/tools/add_timeline_marker); [glama: Mandrilsquad1441 resolve_add_marker](https://glama.ai/mcp/servers/Mandrilsquad1441/codex-davinci-resolve-mcp/tools/resolve_add_marker); [glama: BillyRaz add_marker](https://glama.ai/mcp/servers/BillyRaz/Davinci-MCP/tools/add_marker) (all search summaries; not Blackmagic docs)

**Resolve 21.1 changes (Sept 2026)**
- Blackmagic's 21.1 readme reportedly says advanced scripting now requires Studio and Python scripting moved there. Blackmagic's stated reason: the Python API "was being used to hack studio features into the free version". Python 2 support was removed entirely. — [Blackmagic readme: About DaVinci Resolve 21](https://www.blackmagicdesign.com/support/content/readme/baf7c071c0524fbf8ccc961925c9f443) (search summary; page not fetched)
- Puget Systems (Sept 10, 2026) reports Blackmagic "has entirely removed scripting support from the free edition". This conflicts with the Lua-bridge project's report that `Workspace > Scripts` still runs Lua on free 21.1. — [Puget Systems](https://www.pugetsystems.com/blog/2026/09/10/how-davinci-resolve-free-v21-1-scripting-changes-affect-puget-bench/) (search summary); contradicted by [saadk408/davinci-resolve-lua-mcp](https://github.com/saadk408/davinci-resolve-lua-mcp)
- Resolve 21.1 adds a native MCP server for AI assistants (Claude, Claude Code, ChatGPT Codex), **Studio only**. Setup: "File → Set Up AI Assistance" (another guide says "File > Setup AI Assistants"). Reportedly needs Preferences > System > General > External scripting = Local, otherwise "setup fails silently". Restart Claude after setup. Blackmagic's examples: "analyzing projects, organizing media, changing settings and batch rendering… organize timelines, create custom looks, create and run scripts". The manual reportedly includes examples of adding coloured markers and exporting them to CSV. — [YMCinema, Sept 17 2026](https://ymcinema.com/2026/09/17/davinci-resolve-21-1-mcp-ai-assistants-control-edit/); [Digital Production, Sept 8 2026](https://digitalproduction.com/2026/09/08/resolve-21-1-adds-mcp-and-finally-gets-presets/); [Phoronix](https://phoronix.com/news/DaVinci-Resolve-21.1); [explainx.ai](https://www.explainx.ai/blog/davinci-resolve-21-1-mcp-server-ai-agents-2026); [Vagon](https://vagon.io/blog/how-to-use-davinci-resolve-with-claude-mcp-computer-use) (all search summaries; menu-path wording differs between sources)
- Studio is a one-time US$295 licence (per third-party coverage of 21.1). Claude Desktop and Claude Code are separate MCP clients, so configuring one doesn't prove the other can reach Resolve. — search summary of [YMCinema](https://ymcinema.com/2026/09/17/davinci-resolve-21-1-mcp-ai-assistants-control-edit/) / [Vagon](https://vagon.io/blog/how-to-use-davinci-resolve-with-claude-mcp-computer-use)
- The free 21.1 edition keeps the same processing as Studio but caps output at Ultra HD and supports a single GPU on Windows/Linux. — [Blackmagic readme](https://www.blackmagicdesign.com/support/content/readme/59dd4eef1f4941c29fb8dc48b33f5c87) (search summary)

### Inferences
- **Structural lesson from public skills:** successful media skills keep a thin SKILL.md and push tool detail into rule/reference files (Remotion `rules/ffmpeg.md`). That matches Anthropic's progressive-disclosure guidance. Copy this layout.
- **For this user, the "push into Resolve" path depends on his edition and version:**
  - Free ≤21.0.x: Python and the community MCP bridge may still work, but he should not upgrade blindly.
  - Free 21.1+: no Python. Lua via `Workspace > Scripts` reportedly works (unofficial; could break in a point release). File imports (marker EDL, SRT subtitles) need no scripting.
  - Studio 21.1+: native AI Assistance MCP, which Claude Code can drive directly, plus the full Python API.
  The skill's first-run checkpoint should record `resolve_edition` and `resolve_version` in `_brain/preferences.md` and branch on them.
- Installing any community MCP server needs his explicit OK under his existing rules, and he is not a coder. File-based outputs that need no install are the safer default. Note that the MCP servers themselves say they produce "first-pass assembly" only, which fits a human-in-the-loop plan rather than auto-editing.

### Gaps
- Could not fetch Blackmagic's 21.1 readme or manual directly. The exact wording on Lua in free 21.1, and whether the Console still runs anything, is unverified. Puget's "entirely removed" and saadk408's "Lua still runs" conflict.
- Did not verify which Resolve edition or version the user has. This is critical and must be asked.
- No public skill was found that outputs a timecoded B-roll/SFX/zoom plan for Resolve. This appears to be a gap in the ecosystem.

---

## 3. How do professional editors and assistant editors write edit notes, paper edits, B-roll lists and marker conventions?

### Takeaway
Pro notes are always **timecode-anchored rows** (in/out or a single point), with a type or category, the asset or source, an action, and a done/fix status. Review tools (Frame.io) export comments as CSV with a "Timecode" column. Marker colors are **team-defined**: no industry-standard "blue = B-roll, red = fix" mapping was found, so the skill should define and save its own legend.

### Cited Findings
- Thomas Frank's creator B-roll database (Notion template for YouTubers) has a **Timecode** field: "The timecode (or timestamp) in your A-roll cut where this b-roll item should go. The term 'Timecode' is used because it is the term Frame.io uses in its comment CSV exports." It also has a checkbox ("Once you've fully edited this b-roll item into your video, check this box to mark it off") and a "**Fix Needed**" option "for fixes that need to be made to the current cut". — [Thomas Frank: Creator's Companion B-roll database](https://thomasjfrank.com/docs/creators-companion/databases/b-roll/) (search summary; page not fetched)
- First Assistant (Zygoat, Mac app) builds timecode-based editorial notes for "ADR or VFX lists, stock footage or music cue sheets, and notes for the online editor or colourist", imports a Final Cut Pro 7 timeline, and exports text for Excel. — [Zygoat First Assistant: Editor's notes](https://www.zygoat.ca/firstassistant/guide/editornotes.html)
- Paper edits "usually refer to hours minutes and seconds, because the specifics of frames don't apply to paper edits". Burning timecode into the video is recommended so collaborators reference the same numbers. (2008, old but still standard practice.) — [Alex4D blog](https://blog.alex4d.com/2008/11/10/timecode-quicktime-movies/)
- Assistant-editor logging in practice: "marking down the corresponding 'In and Out' point of the time code using Final Cut Pro and Microsoft Excel". — [StaffMeUp profile](https://staffmeup.com/profile/thomaschiki)
- In Resolve, double-clicking a marker lets you set name, notes and duration. The **Edit Index** lists all markers with colors, names and descriptions for quick navigation. **Flags** (clip-level color tags) are separate from markers. — [Tutkit: flags and markers](https://tutkit.com/en/text-tutorials/1788-davinci-resolve-efficient-use-of-flags-and-markers)
- **Shift+Down Arrow = next marker, Shift+Up Arrow = previous marker** (Edit, Color, Fairlight pages). These navigate all timeline markers regardless of track. — [Miracamp: flip between markers (2026)](https://www.miracamp.com/learn/davinci-resolve/how-to-flip-between-markers); [Simon Says shortcuts](https://www.simonsaysai.com/blog/davinci-resolve-keyboard-shortcuts) (search summary; Blackmagic's own Resolve 15 shortcut PDF lists only Up/Down for edits, so the Shift variants are confirmed only by third parties)
- Search found no standard "red = fix" marker convention; it "will likely be a team-defined rule rather than a built-in Resolve standard". — search synthesis (no single source); see [Tutkit](https://tutkit.com/en/text-tutorials/1788-davinci-resolve-efficient-use-of-flags-and-markers)
- Typical YouTube workflow order in Resolve (guide updated for 21.0.2, July 2026): set up project → organize/proxy → rough cut → sync audio → **cut in B-roll** → titles → two-node grade. — [tryuncle: Resolve workflow for YouTube creators](https://tryuncle.com/learn/davinci-resolve/davinci-resolve-editing-workflow-for-youtube-creators)
- A paid "Paper-Edit Assistant" skill for Claude/ChatGPT claims to output "selected quotes in final story order, each timecoded and justified plus a B-roll map". This is marketing, but it shows that the "timecoded selects + B-roll map" deliverable shape exists. — [Etsy listing](https://www.etsy.com/listing/4556753093) (search summary)

### Inferences
- **Recommended edit-sheet columns.** These synthesize the Frame.io "Timecode" convention, Thomas Frank's B-roll DB, assistant-editor in/out logs and Resolve marker fields:
  `#` | `TC in` (timeline, HH:MM:SS:FF) | `TC out` or `Dur` | `Source sec` (raw video seconds, for cross-checking) | `Track` (V2/V3/A2/Subtitle) | `Type` (B-roll / Zoom / SFX / Transition / Caption / Cut / Fix) | `Asset` (exact filename + folder + licence/source) | `What to do` (one short plain-Arabic instruction, e.g. "زوم 120% على المكعب، ٠.٥ ثانية") | `Why` (one line, optional) | `Marker colour` | `Thumb` (frame image at TC in) | `Done ☐`.
  Paper-edit practice (HH:MM:SS) supports also showing a simplified `mm:ss` column for a student who isn't used to frames.
- **Proposed marker-colour legend.** Not an industry standard, so save it in `_brain/edit-preferences.md` and let him change it. Uses only the 16 API colour names: Blue = B-roll, Yellow = Zoom/punch-in, Green = SFX, Purple = Transition, Cyan = Caption/on-screen text, Pink = Music change, Red = Fix/problem (bad take, mistake, audio issue), Cream = Note/idea (optional). Keep one colour per type so the Edit Index can be scanned by colour.
- Group rows by type (all B-roll, then zooms, etc.) **and** offer chronological order. Editors usually execute chronologically in one pass (Shift+Down marker to marker), but a gather list ("download/locate these 7 B-roll clips first") is useful before starting.

### Gaps
- Could not fetch real Frame.io CSV export column lists or Frame.io blog templates (Frame.io pages were not reached). Only the "Timecode" column name is confirmed, via Thomas Frank.
- No authoritative source on marker-colour conventions (Blackmagic training books, r/editors threads) was found within the tool budget.

---

## 4. Which edit-plan deliverable formats work best for a non-coder (sheet vs markers vs importable timeline vs one-click script), and which is most reliable?

### Takeaway
Use **one machine-readable plan file as the source of truth** (`edit_plan.json`) and **render it into several layers**:
1. Always: a printable HTML edit sheet with thumbnails and colour-coded rows.
2. Always: a Resolve **Timeline-Markers EDL** that he imports via the menu (no scripting; jump with Shift+Up/Down).
3. If captions are needed: an **SRT** for the subtitle track.
4. Optionally, by edition: a one-click **Lua** script (free 21.1+, unofficial), or **Python** or the native **AI Assistance MCP** (Studio).

Pre-placed B-roll timelines (FCPXML/OTIO/EDL) are the least reliable for a non-coder because of relinking, frame-rate and track-placement risks. The sheet + marker EDL combination is the most robust: it works on free and Studio and needs no install.

### Cited Findings
- Marker EDL import path: right-click the timeline in the Media Pool → "Timelines > Import > Timeline Markers from EDL". Export the same way ("Timeline > Export > Timeline Markers to EDL"). Troubleshooting: markers must be "in the correct timecode range"; zoom out; select the sequence first; "Resolve might not support special characters in marker names and comments." — [editingtools.io guide](https://editingtools.io/guides/convert-livenotes-to-resolve-marker); [editingtools.io CSV→Resolve marker](https://zh.editingtools.io/guides/convert-csv-to-resolve-marker)
- Resolve's marker EDL uses EDL comment lines under each event. A Blackmagic staffer's example shows `|C:` (colour, e.g. `ResolveColorBlue`), `|M:` (marker name) and `|D:` (duration, example 300 frames). "I did not find an official Blackmagic specification" (search synthesis). — [Blackmagic forum: EDL file format?](https://forum.blackmagicdesign.com/viewtopic.php?p=752663) (search summary; page not fetched)
- The Edit Index shows all markers with colour/name/notes for navigation. — [Tutkit](https://tutkit.com/en/text-tutorials/1788-davinci-resolve-efficient-use-of-flags-and-markers)
- Timeline import routes: File > Import > Timeline (AAF, EDL, XML), or Media Pool right-click → Timelines > Import > AAF/EDL/XML/DRT/ADL/OTIO. `.otio` holds metadata only and media must be relinked; `.otioz` bundles media. A user's FCPXML import failed until they chose the right import type. — [OTIO wiki: AWS Picchu conversion notes](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/wiki/AWS-Picchu-Edit-OTIO-Conversion-Notes); [tryuncle: Premiere→Resolve](https://tryuncle.com/learn/davinci-resolve/how-to-switch-from-premiere-pro-to-davinci-resolve); [Blackmagic forum FCPXML import](https://forum.blackmagicdesign.com/viewtopic.php?p=743265) (search summaries)
- Search found no source confirming whether an imported timeline keeps B-roll on V2 in the free version; "that needs testing". — search synthesis
- Lua bridge on free 21.1: `add_marker` with frame, 16 colours, name, note and duration works via `Workspace > Scripts`. It is unofficial and experimental on Windows, and Lua `io`/`require` are unavailable. — [saadk408/davinci-resolve-lua-mcp](https://github.com/saadk408/davinci-resolve-lua-mcp)
- Resolve 21.1 Studio's native AI Assistance (MCP) supports Claude Code; "a human still has to check what it changed". — [YMCinema](https://ymcinema.com/2026/09/17/davinci-resolve-21-1-mcp-ai-assistants-control-edit/) (search summary)
- Community MCPs describe their output as "a first-pass assembly", not a judgment of edit quality. — [samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp)
- Anthropic recommends plan-validate-execute with an intermediate structured plan file checked by a script before applying changes. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

### Inferences
**Pros/cons of each format (synthesis):**

| Format | Works on | Pros | Cons / risks | Reliability |
|---|---|---|---|---|
| **HTML edit sheet** (RTL Arabic, thumbnails, colour rows, checkboxes, print CSS); Markdown copy in chat | Any | Zero install; readable on a second monitor or printed; Arabic renders fine in a browser; thumbnails show *what* to look for; he can tick rows | Manual execution; he can mistype timecodes | Very high |
| **Timeline-markers EDL** (`markers.edl`) | Free + Studio (file import, not scripting) | Coloured markers at exact TCs; Shift+Down jumps marker to marker; Edit Index lists them | Format only forum-documented; Arabic/special chars may fail → use ASCII/English short names (`BROLL-03 cube-closeup`) and keep the Arabic detail on the sheet; timeline start TC and fps must match; whether marker notes survive is unverified | High (test once) |
| **SRT captions** | Free + Studio | Standard; goes to a subtitle track | Arabic RTL/font/style set in Resolve; timing at real seconds vs NDF labels (see Q5) | High (not verified in this research) |
| **Lua one-click marker script** (free 21.1+) | Free 21.1 (unofficial), Studio | Real markers with **notes** and durations; one menu click | Undocumented sandbox; may break in a point release; Windows "experimental"; must copy the script into the Scripts folder (needs his OK) | Medium |
| **Python script / community MCP** | Studio (and free ≤21.0) | Full API: markers, append clips | Install steps; Python 3.10–3.12 constraints; Studio needed on 21.1+ | Medium |
| **Native Resolve 21.1 AI Assistance (MCP)** | Studio 21.1+ only | Official; Claude Code can act directly; can create/run scripts | US$295; brand new; setup quirks (External scripting = Local) | Medium–high (new) |
| **Importable timeline with B-roll pre-placed** (FCPXML/OTIO/EDL) | Both (import) | B-roll actually placed on V2 | Relinking media, fps/start-TC mismatches, new timeline must be merged with his edit, track placement unverified | Low–medium for a non-coder |

- **Recommended default:** `edit_plan.json` → validate → render `edit_sheet.html` + `markers.edl` (+ `captions.srt`). Offer the Lua or Studio route only after he confirms his edition and approves installing or copying a script.
- Generate the EDL with **plain ASCII marker names** like `B03 cube closeup`, `Z05 zoom 120`, `S02 whoosh`. Put the matching row number (`B03`) on the HTML sheet so the short code links the marker to the full Arabic instruction. This avoids the special-character risk.
- **Sketch of the marker EDL** (based on the forum-described fields, *not* an official spec; the skill should first ask him to export one marker from Resolve via Timeline > Export > Timeline Markers to EDL and copy that exact format):
  ```
  TITLE: Rubik_EP42_v1
  FCM: NON-DROP FRAME

  001  001      V     C        01:00:12:15 01:00:12:16 01:00:12:15 01:00:12:16
   |C:ResolveColorBlue |M:B01 cube closeup |D:45
  ```
- **Suggested `edit_plan.json` row schema** (source of truth; validated by `scripts/validate_plan.py`):
  `{"id":"B01","type":"broll|zoom|sfx|transition|caption|cut|fix","src_sec":12.5,"tc_in":"01:00:12:15","dur_frames":45,"track":"V2","asset":{"path":"D:/SyrianRubik/broll/cube_closeup.mp4","license":"own footage"},"params":{"zoom_pct":120,"ease":"in-out"},"say":"short Arabic instruction","why":"…","marker_color":"Blue","status":"todo"}` plus a header `{"video":…, "fps":"30000/1001", "timeline_start":"01:00:00:00", "drop_frame":false, "plan_version":3, "based_on_transcript":"…"}`.
- Validator checks: TC within duration; no overlapping B-roll on the same track; asset files exist; licence field filled; colours in the 16-name set; fps and start TC match probe.json. Use verbose error messages, as Anthropic recommends.

### Gaps
- Arabic text in EDL marker names/notes was not tested; the editingtools.io warning suggests a risk.
- Not verified: whether `|M:` and a note both carry over, and whether the EDL needs a specific event-line layout. The fix is to export a sample from his Resolve first.
- SRT import behaviour for Arabic in Resolve 21 was not researched (no source collected).
- FCPXML/OTIO V2 placement in free Resolve was not verified.

---

## 5. How should the skill handle ingestion, transcript-to-timecode mapping, versioning, preference learning and approval checkpoints?

### Takeaway
Use a fixed, checklist-driven pipeline with scripts for every deterministic step: probe → transcript → contact sheets → draft plan JSON → validate → render outputs. Add **human checkpoints** at (1) the ingest summary, (2) the draft sheet, (3) before anything touches Resolve or installs, and (4) after he edits, to capture feedback into memory. Do all timecode maths in **frames**: compute frame counts from real seconds and the real fps, then label them with the timeline's nominal fps and start TC (default 01:00:00:00).

### Cited Findings
- Anthropic's recommended structure for complex skills is a copyable progress checklist plus a validation loop ("Only proceed when validation passes"). — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- Plan-validate-execute: "Reversible planning: Claude can iterate on the plan without touching originals." — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- "Iterate with Claude: have Claude capture successful approaches and common mistakes into the skill." — [Anthropic engineering blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- Marker EDL import fails silently if markers fall outside the timeline's timecode range. — [editingtools.io](https://editingtools.io/guides/convert-livenotes-to-resolve-marker)
- Resolve API marker frame positions are frame offsets on the active timeline (one wrapper: "zero-based frame offset"); duration is in frames. — [glama wrappers](https://glama.ai/mcp/servers/DigitalWorkflowCompany/resolve-mcp/tools/add_timeline_marker) (search summary)
- The Claude Code skill body stays in context for the session; after compaction only the first 5,000 tokens are re-attached. — [Claude Code docs](https://code.claude.com/docs/en/skills)

### Inferences
**Pipeline (put in SKILL.md as a copyable checklist):**
```
Edit-plan progress:
- [ ] 0. Load brain: preferences.md, edit-preferences.md, video-log.md (+ resolve edition/version)
- [ ] 1. Probe video  → scripts/probe_video.py  → probe.json (fps r/avg, duration, start TC tag, VFR flag)
- [ ] 2. Transcript   → (existing transcript or local Whisper — ask before installing) → transcript.json (word/segment seconds)
- [ ] 3. Contact sheets → scripts/contact_sheets.py → sheets/*.jpg (+ per-row thumbs later)
- [ ] CHECKPOINT A: tell him in 3–5 short lines what the video is, length, fps; ask what style/energy he wants
- [ ] 4. Draft plan   → edit_plan_vN.json (Claude writes)
- [ ] 5. Validate     → scripts/validate_plan.py (fix until OK)
- [ ] 6. Render       → plan_to_html.py, plan_to_edl.py, plan_to_srt.py
- [ ] CHECKPOINT B: show the sheet; he approves/changes rows → bump version
- [ ] CHECKPOINT C: before copying any script into Resolve or installing anything
- [ ] 7. He applies in Resolve (markers → Shift+Down through them)
- [ ] CHECKPOINT D: ask what he kept/changed → append to edit-preferences.md + video-log.md
```
- **Probe:** run `ffprobe -v error -show_streams -show_format -of json` and record `r_frame_rate`, `avg_frame_rate`, `duration`, any `timecode` tag, width/height and audio. If `r_frame_rate` ≠ `avg_frame_rate`, flag **VFR**. Phone, OBS and game-capture recordings are often VFR, which causes transcript/TC drift; offer a CFR transcode, but only with his OK.
- **Timecode maths (critical, easy to get wrong):** transcript seconds are *real time*.
  - `frame = round(sec × fps_real)`, where `fps_real` = 30000/1001 for "29.97".
  - Then `timeline_frame = start_frames + frame + (offset of the clip on the timeline)`.
  - For an NDF 29.97 timeline, label with the **nominal 30** frames per second: `start_frames = 1×3600×30 = 108000` for 01:00:00:00.
  - Example: 600.0 s → 17,982 frames → label `01:09:59:12` (NDF), not `01:10:00:00`. That is ~0.6 s of drift at 10 min, enough to put a zoom on the wrong word.
  - Drop-frame timelines need the DF formula. Integer rates (24/25/30/60) are trivial.
  - Store `src_sec`, `frame` and `tc_in` in every row so errors can be caught.
  - Ask him (or read from a Resolve export) the timeline start TC and fps once per project, and save them. Resolve's default start is 01:00:00:00 (from prior knowledge; not re-verified in this research).
- **Clip offset:** if his A-roll doesn't start at the timeline start (intro, cold open), the plan needs `timeline_offset_frames`. The easiest way to get it is to have him export one marker EDL placed on the first frame of the A-roll.
- **Versioning:** `plans/<video-slug>/edit_plan_v1.json` → `v2`…; never overwrite. Each render embeds the version in titles (`TITLE: EP42_v3`) and in the sheet header. Keep a `CHANGES.md` line per version ("v3: removed 2 zooms he said were too many"). Marker EDL names include the version so stale markers can be spotted.
- **Preference learning:** add `_brain/edit-preferences.md` (zoom style and %, SFX he likes/hates, caption style, B-roll density per minute, colour legend, Resolve edition/version/fps/start TC). Append-only, dated bullets after Checkpoint D. Read it at step 0. Fits his existing `_brain` convention (`preferences.md`, `video-log.md`).
- **Reference files to split out** (one level deep): `references/plan-schema.md`, `references/timecode-math.md`, `references/marker-colors.md`, `references/resolve-import-steps-ar.md` (his click-by-click steps in plain Syrian Arabic, with screenshots if possible), `references/resolve-scripting-by-edition.md` (free ≤21.0 / free 21.1 Lua / Studio Python / Studio AI Assistance), `references/windows-gotchas.md`.

**Suggested layout:**
```
editing-in-resolve/
  SKILL.md                    (≤350 lines; rules + checklist + output contract first)
  references/ plan-schema.md, timecode-math.md, marker-colors.md,
              resolve-import-steps-ar.md, resolve-scripting-by-edition.md, windows-gotchas.md
  scripts/    probe_video.py, contact_sheets.py, validate_plan.py,
              plan_to_html.py, plan_to_edl.py, plan_to_srt.py,
              plan_to_lua.py (free 21.1, embeds data in the .lua since io is unavailable),
              plan_to_resolve_py.py (Studio)
  assets/     edit_sheet_template.html (RTL, print CSS, colour legend), sample_marker_export.edl
  evals/      evals.json (3+ real videos: short cubing tutorial, gaming clip, long-form)
```

### Gaps
- Transcription engine choice (faster-whisper on an RTX 4060 8 GB, Arabic dialect accuracy) is outside this note's scope and was not researched here.
- Resolve's default start timecode and project-fps lock behaviour were not re-verified against the Blackmagic manual (fetch blocked).

---

## 6. What pitfalls should the skill handle (Claude can't watch video, context limits, Windows paths/Arabic filenames, PowerShell quirks)?

### Takeaway
Claude sees **images, not video**, so the skill must extract frames and contact sheets with ffmpeg and pair them with a timestamped transcript. Image budgets are limited: 20 images per message on claude.ai, and a stricter 2000 px cap above 20 images per API request, so use tiled contact sheets and process long videos in chunks. On Windows, Arabic filenames are mainly a problem of *how* paths are passed (shell code pages, PowerShell redirection), not of ffmpeg itself. Scripts should use Python with list-form `subprocess`, UTF-8 everywhere, and ASCII working copies of names when in doubt.

### Cited Findings
- Claude accepts JPEG, PNG, GIF and WebP images. "Animations are unsupported, and only the first frame is used." The vision doc mentions no video input. — [Claude vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)
- Limits: 20 images per message on claude.ai; 100 per API request for 200k-context models; 600 for others; max 8000×8000 px. Above 20 images per request a stricter limit applies, so "resize each image so that neither dimension exceeds 2000 px, or keep the request to 20 or fewer". There is a 32 MB request size limit. — [Claude vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)
- Token cost = ⌈width/28⌉ × ⌈height/28⌉ visual tokens. Claude 4.7+ models use a high-res tier (long edge 2,576 px, max 4,784 tokens). A 1920×1080 image costs 2,691 tokens on high-res, or 1,560 tokens when downsized to 1456×819 on standard. — [Claude vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)
- Images work best placed before the text; label multiple images ("Image 1:"…). Accuracy drops on "very small images under 200 pixels". — [Claude vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)
- Anthropic recommends converting inputs to images for visual analysis inside skills. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- Windows/ffmpeg: "On Windows, FFmpeg API expects file paths in UTF8 encoding… When using ffmpeg.exe, encoding conversion should be done implicitly". The problem is usually how the calling program passes arguments. (2019) — [FFmpeg-user list](https://ffmpeg.org/pipermail/ffmpeg-user/2019-March/043600.html). Older code-page-based behaviour could not open names outside the local code page. (2012, superseded) — [FFmpeg-devel](https://lists.ffmpeg.org/pipermail/ffmpeg-devel/2012-April/123449.html)
- youtube-dl had to add a Windows-specific filename-encoding path for every ffmpeg/ffprobe subprocess call. — [youtube-dl commit](https://gitdab.com/w/youtube-dl/commit/8bf48f237dbd7b3fc606de69cf468827643ecfdd)
- Use forward slashes in skill-internal paths. — [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices). On Windows, `shell: bash` needs Git Bash; `shell: powershell` is the alternative. — [Claude Code docs](https://code.claude.com/docs/en/skills)
- Tooflex: on Windows avoid uv-managed standalone Python with Resolve (fusionscript.dll crashes); use CPython 3.10/3.11 for Resolve's Python module. — [tooflex/davinci-resolve-mcp](https://github.com/tooflex/davinci-resolve-mcp) (search summary)
- Lua bridge on Windows is "experimental"; modal dialogs block it; it must be relaunched after each Resolve start. — [saadk408/davinci-resolve-lua-mcp](https://github.com/saadk408/davinci-resolve-lua-mcp)

### Inferences
- **"Watching" the video:** `contact_sheets.py` should use ffmpeg `fps=1/2,scale=320:-1,tile=4x4` (16 frames = 32 s per sheet), with the **timestamp burned into each tile** (drawtext) so Claude can cite seconds. At 1280×720 a sheet costs ≈ 46×26 = 1,196 tokens. A 10-min video → ~19 sheets → ~23k tokens. Feed sheets in batches of ≤20 per message to respect claude.ai's limit, and keep sheets ≤2000 px. Also extract a single full-res frame at each planned `tc_in` for the HTML sheet's thumbnail column.
- **Context limits:** for long videos (gaming streams, 30–60 min), process in **chapters** of about 5 min each (transcript chunk + that chunk's sheets), write each chapter's rows into the JSON, then merge. Never paste the full transcript into chat; save to file and Read the relevant ranges. Let the scripts do the counting and arithmetic.
- **Arabic filenames / Windows:**
  - In Python, pass paths as `pathlib.Path`.
  - Call ffmpeg with `subprocess.run([...], shell=False)` (no shell string).
  - Open all text files with `encoding="utf-8"`; use `"utf-8-sig"` for CSV that Excel opens.
  - Set `PYTHONUTF8=1`.
  - Never rely on PowerShell `>` redirection to write files. In Windows PowerShell 5.1 it writes UTF-16LE, which breaks EDL/SRT. Have the Python scripts write the files directly. (This PowerShell behaviour is from prior knowledge, not re-verified here.)
  - EDL marker names should be ASCII. For media, if Resolve or ffmpeg ever chokes, use ASCII working aliases (`clip_001.mp4`) with a `names_map.json`.
  - Avoid paths over 260 characters (deep OneDrive folders). From prior knowledge; flag as a general Windows risk.
- **Hallucinated assets:** the plan must only reference B-roll and SFX files that actually exist in his library folders. The validator should check `asset.path` exists, and the licence field must be filled, enforcing his "licensed footage only" rule.
- **Frame-accuracy honesty:** Claude's timing comes from the transcript plus sampled frames (every 2 s). The sheet should state that times are ±0.5 s and he should nudge to the exact beat. Finer contact sheets can be generated only around rows marked "tight".
- **Resolve 21.1 upgrade trap:** if he is on free ≤21.0 and relies on Python scripts, upgrading to 21.1 breaks them. The skill should warn before he updates.

### Gaps
- No 2025–2026 source specifically on PowerShell 7 / Windows Terminal handling of Arabic arguments to ffmpeg was found. The ffmpeg sources are 2012–2019.
- Arabic RTL rendering in Resolve's subtitle track and in EDL marker text was not verified.
- Not tested: how reliably Claude reads burned-in timestamps on small contact-sheet tiles. Images under 200 px are flagged as an accuracy risk, so tiles should be ≥300 px wide.
