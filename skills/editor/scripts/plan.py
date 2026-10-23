"""The edit plan: one JSON file is the single source of truth.

  python plan.py init PROJECT                 # new edit_plan_v1.json with timeline facts filled in
  python plan.py bump PROJECT                 # copy latest plan to the next version
  python plan.py validate PROJECT [--strict]  # errors stop everything; warnings are advice
  python plan.py sheet PROJECT                # out/edit_sheet.html (thumbnails, colors, checkboxes)
  python plan.py edl PROJECT                  # out/markers.edl (fallback: import markers by hand)
  python plan.py srt PROJECT                  # out/captions.srt from the word timings
  python plan.py captions PROJECT             # add burned-in caption items to the plan
  python plan.py notes PROJECT                # out/upload-notes.md: chapters, credits, reminders

Full field list: references/plan-schema.md
"""
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

import edcommon as ec

TYPES = {"zoom", "broll", "sfx", "popup", "freeze", "transition", "chapter", "note", "fix", "caption"}
NEEDS_DUR = {"zoom", "broll", "popup", "freeze", "caption"}
MANUAL_TYPES = {"transition", "note", "fix", "chapter"}  # bridge places markers only
BY_HAND_TYPES = {"transition", "note", "fix"}  # rows he does himself
NO_MARKER_BY_DEFAULT = {"sfx", "caption"}
TRACK = {"zoom": "ED ZOOM", "freeze": "ED ZOOM", "broll": "ED B-ROLL", "popup": "ED TEXT", "caption": "ED CAPTIONS"}
SFX_TRACKS = ["ED SFX 1", "ED SFX 2"]
BROLL_AUDIO_TRACK = "ED B-ROLL AUDIO"
ALL_TRACKS = list(dict.fromkeys(list(TRACK.values()) + SFX_TRACKS + [BROLL_AUDIO_TRACK]))
TYPE_LABEL = {"zoom": "Zoom", "broll": "B-roll", "sfx": "Sound", "popup": "Text pop-up", "freeze": "Freeze",
              "transition": "Transition", "chapter": "Chapter", "note": "Note", "fix": "Fix", "caption": "Caption"}


# ------------------------------------------------------------------ files


def plan_dir(proj: Path) -> Path:
    return proj / "plan"


def plan_files(proj: Path) -> list[Path]:
    files = list(plan_dir(proj).glob("edit_plan_v*.json"))
    return sorted(files, key=lambda p: int(re.search(r"_v(\d+)", p.stem).group(1)))


def latest_plan_path(proj: Path) -> Path:
    files = plan_files(proj)
    if not files:
        ec.die("No plan yet. Run: plan.py init PROJECT")
    return files[-1]


def load_plan(proj: Path, path: str | None = None) -> tuple[dict, Path]:
    p = Path(path) if path else latest_plan_path(proj)
    return ec.read_json(p), p


def timeline_facts(proj: Path) -> dict:
    snap_p = proj / "bridge" / "snapshot_before.json"
    probe_p = proj / "analysis" / "probe.json"
    facts = {}
    if snap_p.exists():
        t = ec.read_json(snap_p)["timeline"]
        facts = {k: t.get(k) for k in ("name", "fps", "start_frame", "start_tc", "width", "height", "drop_frame")}
    if probe_p.exists():
        pr = ec.read_json(probe_p)
        facts["duration"] = round(pr["duration"], 3)
        facts.setdefault("fps", pr.get("fps"))
        facts.setdefault("width", pr.get("width"))
        facts.setdefault("height", pr.get("height"))
    facts.setdefault("start_frame", 0)
    facts.setdefault("drop_frame", False)
    return facts


def cmd_init(args) -> None:
    proj = ec.resolve_project(args.project)
    if plan_files(proj) and not args.force:
        ec.die("A plan already exists. Use 'bump' for a new version (or --force).")
    plan = {
        "schema": "editor-plan/1",
        "version": 1,
        "project": proj.name,
        "channel": args.channel,
        "created": ec.now_iso(),
        "timeline": timeline_facts(proj),
        "style": {},
        "summary": "",
        "items": [],
    }
    p = ec.write_json(plan_dir(proj) / "edit_plan_v1.json", plan)
    print(f"New plan: {p}")


def cmd_bump(args) -> None:
    proj = ec.resolve_project(args.project)
    plan, path = load_plan(proj)
    plan["version"] = int(plan.get("version", 1)) + 1
    plan["created"] = ec.now_iso()
    p = ec.write_json(plan_dir(proj) / f"edit_plan_v{plan['version']}.json", plan)
    ec.append_text(plan_dir(proj) / "CHANGES.md", f"\n## v{plan['version']} ({ec.today()})\n- {args.note or 'new version'}\n")
    print(f"Now editing: {p}")


# ------------------------------------------------------------------ validation


def active_items(plan: dict) -> list[dict]:
    return [it for it in plan.get("items", []) if it.get("status") != "rejected"]


def item_end(it: dict) -> float:
    return float(it["at"]) + float(it.get("dur") or 0.0)


def wants_marker(it: dict) -> bool:
    return bool(it.get("marker", it.get("type") not in NO_MARKER_BY_DEFAULT))


def validate(plan: dict, proj: Path, strict: bool = False) -> tuple[list[str], list[str]]:
    from library import bad_license, load_library, resolve_asset

    errors, warns = [], []
    tl = plan.get("timeline", {})
    dur = float(tl.get("duration") or 0)
    if plan.get("schema") != "editor-plan/1":
        errors.append("schema must be 'editor-plan/1'")
    if not dur:
        errors.append("timeline.duration missing (run analyze.py, then plan.py init)")
    lib = load_library()
    ids = set()
    items = active_items(plan)
    for it in items:
        iid = it.get("id", "?")
        where = f"{iid}"
        if not re.match(r"^[A-Za-z0-9_-]{1,10}$", str(iid)):
            errors.append(f"{where}: id must be short letters/digits (like Z03)")
        if iid in ids:
            errors.append(f"{where}: duplicate id")
        ids.add(iid)
        t = it.get("type")
        if t not in TYPES:
            errors.append(f"{where}: unknown type {t!r}")
            continue
        if not isinstance(it.get("at"), (int, float)) or it["at"] < 0:
            errors.append(f"{where}: 'at' must be seconds >= 0")
            continue
        if dur and it["at"] > dur + 0.05:
            errors.append(f"{where}: starts after the video ends ({ec.fmt_time(it['at'])} > {ec.fmt_time(dur)})")
        if t in NEEDS_DUR:
            d = it.get("dur")
            if not isinstance(d, (int, float)) or d <= 0:
                errors.append(f"{where}: needs 'dur' (seconds > 0)")
                continue
            if dur and item_end(it) > dur + 0.05:
                errors.append(f"{where}: runs past the end of the video")
        if not it.get("why"):
            warns.append(f"{where}: no 'why' (the sheet and the learning loop need it)")
        p = it.get("params", {})
        if t == "zoom":
            s = p.get("scale")
            if not isinstance(s, (int, float)) or not 1.01 <= s <= 4.0:
                errors.append(f"{where}: zoom scale must be 1.01-4.0 (1.25 = 125%)")
            elif s > 1.5:
                warns.append(f"{where}: {s:.0%} zoom can look soft on 1080p footage")
            c = p.get("center", [0.5, 0.5])
            if not (isinstance(c, list) and len(c) == 2 and all(0 <= v <= 1 for v in c)):
                errors.append(f"{where}: center must be [x, y] between 0 and 1")
            if p.get("mode", "hard") not in ("hard", "smooth", "shake"):
                errors.append(f"{where}: zoom mode must be hard, smooth or shake")
            elif p.get("mode") == "shake":
                if isinstance(s, (int, float)) and s < 1.08:
                    errors.append(f"{where}: a shake zoom needs scale 1.08 or more (the shake needs spare picture at the edges)")
                if float(it.get("dur") or 0) > 1.5:
                    warns.append(f"{where}: shake works best under 1.5 s")
        if t in ("broll", "sfx"):
            ref = (it.get("asset") or {}).get("ref")
            if not ref:
                errors.append(f"{where}: needs asset.ref (library id or file path)")
            else:
                a = resolve_asset(ref, lib)
                cand = str(ref).startswith("candidate:")
                if not a and not cand:
                    errors.append(f"{where}: asset {ref!r} not found in library or on disk")
                elif cand and strict:
                    errors.append(f"{where}: {ref} is only a candidate: download it (with his OK) and register it first")
                elif cand:
                    warns.append(f"{where}: {ref} still needs his OK + download")
                if a:
                    if bad_license(a.get("license")):
                        errors.append(f"{where}: license {a.get('license')!r} is NC/ND: not allowed")
                    if a.get("source") not in ("own", None, "unindexed") and not a.get("license"):
                        errors.append(f"{where}: outside asset without a logged license")
                    if a.get("source") == "unindexed":
                        warns.append(f"{where}: file is not in the library index (no license record)")
                    if t == "broll" and a.get("duration") and a.get("kind") != "image":
                        src_in = float((it.get("asset") or {}).get("in", 0.0))
                        if src_in + float(it.get("dur", 0)) > a["duration"] + 0.05:
                            errors.append(f"{where}: clip is only {a['duration']:.1f}s, plan uses {src_in:.1f}+{it['dur']:.1f}s")
        if t == "broll" and it.get("dur", 0) > 6:
            warns.append(f"{where}: B-roll held {it['dur']:.1f}s (over ~6s a static shot drags)")
        if t in ("popup", "caption"):
            text = str(p.get("text", "")).strip()
            if not text:
                errors.append(f"{where}: needs params.text")
            else:
                need = 0.6 + len(text) / 15.0
                if it.get("dur", 0) < need:
                    warns.append(f"{where}: {len(text)} characters need ~{need:.1f}s on screen to read")
                if t == "caption" and any(len(line) > 42 for line in text.split("\n")):
                    warns.append(f"{where}: caption line over 42 characters")
        if t == "chapter" and not p.get("title"):
            errors.append(f"{where}: chapter needs params.title")
    # overlaps on the same output track
    lanes: dict[str, list[dict]] = {}
    for it in items:
        tr = TRACK.get(it.get("type"))
        if tr and isinstance(it.get("at"), (int, float)) and it.get("dur"):
            lanes.setdefault(tr, []).append(it)
    for tr, lst in lanes.items():
        lst.sort(key=lambda x: x["at"])
        for a, b in zip(lst, lst[1:]):
            if b["at"] < item_end(a) - 0.01:
                errors.append(f"{a['id']} and {b['id']} overlap on {tr}")
    sfx = sorted((it for it in items if it.get("type") == "sfx"), key=lambda x: x["at"])
    for a, b, c in zip(sfx, sfx[1:], sfx[2:]):
        if c["at"] - a["at"] < 0.3:
            warns.append(f"{a['id']}/{b['id']}/{c['id']}: three sounds within 0.3s")
    # taste checks
    zooms = sorted((it for it in items if it.get("type") == "zoom"), key=lambda x: x["at"])
    for a, b in zip(zooms, zooms[1:]):
        if b["at"] - item_end(a) < 2.0:
            warns.append(f"{a['id']}->{b['id']}: zooms less than 2s apart feel tiring")
    used: dict[str, int] = {}
    for it in sfx:
        ref = (it.get("asset") or {}).get("ref")
        used[ref] = used.get(ref, 0) + 1
    for ref, n in used.items():
        if n >= 5:
            warns.append(f"sound {ref} used {n} times: repetitive, vary it")
    visual = [it for it in items if it.get("type") in ("zoom", "broll", "popup", "freeze")]
    if dur and not any(it["at"] < 10 for it in visual):
        warns.append("nothing visual happens in the first 10 s (the hook)")
    counted = [it for it in items if it.get("type") in ("zoom", "broll", "popup", "freeze", "sfx")
               and it.get("status") != "unsure"]
    if dur >= 60:
        per_min = len(counted) / (dur / 60)
        pacing = str(plan.get("style", {}).get("pacing", "medium")).lower()
        lo, hi = {"calm": (2, 5), "fast": (10, 20)}.get(pacing, (6, 10))
        if per_min < lo * 0.8:
            warns.append(f"only {per_min:.1f} edits per minute; {pacing} pacing aims for {lo}-{hi}")
        elif per_min > hi * 1.2:
            warns.append(f"{per_min:.1f} edits per minute is a lot; {pacing} pacing aims for {lo}-{hi}")
        for m in range(int(dur // 60) + 1):
            n = sum(1 for it in counted if m * 60 <= it["at"] < (m + 1) * 60)
            if n > hi * 1.6:
                warns.append(f"minute {m}: {n} edits at once is too busy, thin it out")
    for it in items:
        if it.get("type") == "sfx" and float(it.get("params", {}).get("gain_db", 0)) > 0:
            warns.append(f"{it['id']}: sound boosted above its level; it may cover his voice")
    chapters = sorted((it for it in items if it.get("type") == "chapter"), key=lambda x: x["at"])
    if chapters:
        if chapters[0]["at"] > 0.01:
            warns.append("YouTube chapters must start at 0:00")
        if len(chapters) < 3:
            warns.append("YouTube needs at least 3 chapters")
        for a, b in zip(chapters, chapters[1:]):
            if b["at"] - a["at"] < 10:
                warns.append(f"chapters {a['id']}->{b['id']} closer than 10s (YouTube ignores them)")
    if sum(1 for it in items if wants_marker(it)) > 999:
        errors.append("more than 999 markers")
    return errors, warns


def cmd_validate(args) -> None:
    proj = ec.resolve_project(args.project)
    plan, path = load_plan(proj, args.plan)
    errors, warns = validate(plan, proj, args.strict)
    counts = {}
    for it in active_items(plan):
        counts[it.get("type")] = counts.get(it.get("type"), 0) + 1
    print(f"{path.name}: {len(active_items(plan))} edits " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    for w in warns:
        print(f"  warning: {w}")
    for e in errors:
        print(f"  ERROR: {e}")
    if errors:
        ec.die(f"{len(errors)} error(s): fix the plan and validate again.", 2)
    print("OK: plan is valid.")


# ------------------------------------------------------------------ edit sheet


SHEET_CSS = """
:root{--bg:#f6f5f2;--card:#fff;--ink:#16161a;--muted:#5d5d66;--line:#e2e0da}
@media (prefers-color-scheme:dark){:root{--bg:#121214;--card:#1c1c20;--ink:#ececf1;--muted:#a0a0ab;--line:#2c2c33}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 'Segoe UI',system-ui,sans-serif}
main{max-width:1180px;margin:0 auto;padding:20px 16px 60px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:28px 0 10px}.muted{color:var(--muted)}
.legend{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}.chip{display:inline-block;padding:2px 9px;border-radius:999px;color:#000;font-weight:700;font-size:12px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
td.t{white-space:nowrap;font-variant-numeric:tabular-nums}td img{width:220px;border-radius:6px;display:block}
.ar{direction:rtl;unicode-bidi:plaintext;font-family:'Segoe UI','Tahoma',sans-serif}
.asset img{width:240px;margin-top:6px}.asset img.card{background:#777 repeating-conic-gradient(#999 0 25%,#777 0 50%) 0 0/16px 16px}.manual{background:rgba(255,80,80,.08)}.rej{opacity:.35}
.summary{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kv{display:grid;grid-template-columns:max-content 1fr;gap:4px 14px}
input[type=checkbox]{width:20px;height:20px}
@media (max-width:760px){td img{width:140px}.asset img{width:150px}th:nth-child(6),td:nth-child(6){display:none}}
@media print{body{background:#fff;color:#000}td img{width:150px}}
"""

CHIP = {"Blue": "#4c8dff", "Yellow": "#ffd23f", "Green": "#3ecf6e", "Purple": "#a970ff", "Cyan": "#33d6e6",
        "Pink": "#ff7ac0", "Red": "#ff5a5a", "Cream": "#f3ead2", "Sand": "#d8b98a", "Lavender": "#c9b6ff",
        "Mint": "#9ef0c9", "Sky": "#9fd6ff", "Rose": "#ff9fb0", "Lemon": "#f4f78a", "Cocoa": "#a07858", "Fuchsia": "#ff4fd8"}


def describe(it: dict, lib: dict) -> str:
    from library import resolve_asset

    p = it.get("params", {})
    t = it["type"]
    if t == "zoom":
        return f"{p.get('mode', 'hard')} zoom to {float(p.get('scale', 1)):.0%} on {p.get('center', [0.5, 0.5])} for {it['dur']:.1f}s"
    if t == "broll":
        a = resolve_asset(it["asset"]["ref"], lib) if it.get("asset") else {}
        name = Path(a["path"]).name if a.get("path") else it["asset"]["ref"]
        return f"B-roll <b>{html.escape(name)}</b> from {float(it['asset'].get('in', 0)):.1f}s, {it['dur']:.1f}s" + (" (with its sound)" if it["asset"].get("audio") else "")
    if t == "sfx":
        a = resolve_asset(it["asset"]["ref"], lib) if it.get("asset") else {}
        name = Path(a["path"]).name if a.get("path") else it["asset"]["ref"]
        return f"Sound <b>{html.escape(name)}</b> {p.get('gain_db', 0):+g} dB, peak on this moment"
    if t in ("popup", "caption"):
        return f"Text “<bdi>{html.escape(str(p.get('text', '')))}</bdi>” ({p.get('style', 'pop')}, {p.get('position', 'center')}) {it['dur']:.1f}s"
    if t == "freeze":
        return f"Freeze frame {it['dur']:.1f}s" + (f", zoom {float(p['scale']):.0%}" if p.get("scale") else "")
    if t == "transition":
        return f"Transition: {html.escape(str(p.get('kind', 'cut')))} ({p.get('dur_frames', 10)} frames) — you add this one"
    if t == "chapter":
        return f"Chapter: <b>{html.escape(str(p.get('title', '')))}</b>"
    return html.escape(str(p.get("text", "")))


def cmd_sheet(args) -> None:
    from library import load_library, resolve_asset
    from sheets import thumbs_at

    proj = ec.resolve_project(args.project)
    plan, path = load_plan(proj, args.plan)
    errors, warns = validate(plan, proj)
    lib = load_library()
    review = proj / "review.mp4"
    items = sorted(plan.get("items", []), key=lambda x: (x.get("at", 0), x.get("id", "")))
    thumbs = thumbs_at(review, sorted({round(float(it.get("at", 0)) + 0.05, 2) for it in items}), proj / "out" / "thumbs") if review.exists() else {}
    tl = plan.get("timeline", {})
    fps, start = tl.get("fps") or 30, int(tl.get("start_frame") or 0)
    snap_p = proj / "bridge" / "snapshot_before.json"
    snap = ec.read_json(snap_p) if snap_p.exists() else None
    pops = [{"id": it["id"], **it.get("params", {})} for it in items if it.get("type") == "popup" and it.get("params", {}).get("text")]
    previews = {}
    if pops and not args.no_previews:
        from text_cards import render_cards

        w, h = int(tl.get("width") or 1920), int(tl.get("height") or 1080)
        previews = render_cards(pops, proj / "out" / "text" / f"sheet_v{plan.get('version')}", w, h)
    rows, gather = [], []
    for it in items:
        t = it.get("type", "note")
        color = ec.TYPE_COLOR.get(t, "Cream")
        th = thumbs.get(round(float(it.get("at", 0)) + 0.05, 2))
        img = f"<img src='thumbs/{th.name}' alt=''>" if th else ""
        asset_html = ""
        if t in ("broll", "sfx") and it.get("asset"):
            ref = it["asset"]["ref"]
            a = resolve_asset(ref, lib)
            if not a or str(ref).startswith("candidate:"):
                gather.append(f"<li><b>{it['id']}</b>: {html.escape(str(ref))} {html.escape(str(it['asset'].get('url', '')))}</li>")
            elif a.get("thumb") and Path(a["thumb"]).exists():
                asset_html = f"<div class='asset'><img src='{Path(a['thumb']).as_uri()}' alt=''></div>"
            if a and a.get("source") not in (None, "own", "unindexed"):
                asset_html += f"<div class='muted'>{html.escape(str(a.get('source')))} · {html.escape(str(a.get('license')))}</div>"
        tc = ec.frames_to_tc(start + ec.sec_to_frames(it.get("at", 0), fps), fps, tl.get("drop_frame", False))
        hand = t in BY_HAND_TYPES
        if snap and t in ("zoom", "freeze") and isinstance(it.get("at"), (int, float)) and it.get("dur"):
            f0 = start + ec.sec_to_frames(it["at"], fps)
            base, _, reason = find_base(snap, f0, f0 + ec.sec_to_frames(it["dur"], fps))
            if base is None:
                hand = True
                asset_html += f"<div><b>By hand:</b> {html.escape(reason or '')}</div>"
        if it.get("id") in previews:
            asset_html += f"<div class='asset'><img class='card' src='{previews[it['id']].relative_to(proj / 'out').as_posix()}' alt=''></div>"
        cls = "rej" if it.get("status") == "rejected" else ("manual" if hand or it.get("status") == "unsure" else "")
        quote = f"<div class='ar'><bdi>“{html.escape(it['quote'])}”</bdi></div>" if it.get("quote") else ""
        rows.append(
            f"<tr class='{cls}'><td><input type='checkbox' aria-label='done {it.get('id')}'></td>"
            f"<td><span class='chip' style='background:{CHIP.get(color, '#ddd')}'>{html.escape(str(it.get('id')))}</span><br>"
            f"<span class='muted'>{TYPE_LABEL.get(t, t)}</span></td>"
            f"<td class='t'><b>{ec.fmt_time(it.get('at', 0))}</b><br><span class='muted'>{tc}</span></td>"
            f"<td>{img}</td><td>{describe(it, lib)}{asset_html}{quote}</td>"
            f"<td class='muted'>{html.escape(str(it.get('why', '')))}</td></tr>")
    counts = {}
    for it in active_items(plan):
        counts[it.get("type")] = counts.get(it.get("type"), 0) + 1
    minutes = max(1e-6, float(tl.get("duration") or 1) / 60)
    legend = "".join(f"<span class='chip' style='background:{CHIP[c]}'>{TYPE_LABEL[t]}</span>"
                     for t, c in ec.TYPE_COLOR.items() if t in TYPE_LABEL and c in CHIP)
    style = "".join(f"<div class='muted'>{html.escape(str(k))}</div><div>{html.escape(str(v))}</div>"
                    for k, v in (plan.get("style") or {}).items())
    issues = "".join(f"<li>{html.escape(w)}</li>" for w in warns) + "".join(f"<li><b>ERROR:</b> {html.escape(e)}</li>" for e in errors)
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Edit plan v{plan.get('version')} · {html.escape(proj.name)}</title><style>{SHEET_CSS}</style></head><body><main>
<h1>Edit plan v{plan.get('version')} — {html.escape(str(tl.get('name') or proj.name))}</h1>
<div class="muted">{ec.fmt_time(float(tl.get('duration') or 0))} · {fps} fps · made {html.escape(str(plan.get('created', '')))} · times are from the start of your timeline</div>
<div class="legend">{legend}</div>
<div class="summary"><div>{html.escape(plan.get('summary', ''))}</div><div class="kv" style="margin-top:8px">{style}</div>
<div class="muted" style="margin-top:8px">{' · '.join(f'{v} {TYPE_LABEL.get(k, k).lower()}' for k, v in sorted(counts.items()))} · {sum(counts.get(k, 0) for k in ('zoom', 'broll', 'popup', 'freeze')) / minutes:.1f} visual edits per minute</div></div>
{f'<h2>Get these first</h2><ul>{"".join(gather)}</ul>' if gather else ''}
{f'<h2>Notes from the checker</h2><ul>{issues}</ul>' if issues else ''}
<h2>All edits in order</h2>
<table><thead><tr><th>✓</th><th>ID</th><th>Time</th><th>Frame</th><th>What</th><th>Why</th></tr></thead><tbody>
{''.join(rows)}</tbody></table>
<p class="muted">Red rows are yours to do by hand. Everything else the bridge can place for you.</p>
</main></body></html>"""
    out = ec.write_text(proj / "out" / "edit_sheet.html", doc)
    print(f"Sheet: {out}")


# ------------------------------------------------------------------ EDL / SRT / notes


def cmd_edl(args) -> None:
    proj = ec.resolve_project(args.project)
    plan, _ = load_plan(proj, args.plan)
    tl = plan["timeline"]
    fps, start, df = tl.get("fps") or 30, int(tl.get("start_frame") or 0), bool(tl.get("drop_frame"))
    lines = [f"TITLE: {ec.slugify(proj.name)}_v{plan.get('version')}", f"FCM: {'DROP FRAME' if df else 'NON-DROP FRAME'}", ""]
    used = set()
    n = 0
    for it in sorted(active_items(plan), key=lambda x: x["at"]):
        if not wants_marker(it):
            continue
        f = start + ec.sec_to_frames(it["at"], fps)
        while f in used:
            f += 1
        used.add(f)
        n += 1
        tc_in, tc_out = ec.frames_to_tc(f, fps, df), ec.frames_to_tc(f + 1, fps, df)
        color = ec.TYPE_COLOR.get(it["type"], "Blue")
        d = max(1, ec.sec_to_frames(it.get("dur") or 0, fps))
        lines.append(f"{n:03d}  001      V     C        {tc_in} {tc_out} {tc_in} {tc_out}  ")
        lines.append(f" |C:ResolveColor{color} |M:{ec.ascii_marker_name(it)} |D:{d}")
        lines.append("")
        if n == 999:
            break
    out = ec.write_text(proj / "out" / "markers.edl", "\r\n".join(lines) + "\r\n", newline="")
    print(f"{n} markers -> {out}")
    print("In Resolve: right-click the timeline in the Media Pool > Timelines > Import > Timeline Markers from EDL.")


def srt_time(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def caption_chunks(words: list[dict], max_chars: int = 42, max_dur: float = 7.0, gap: float = 0.5,
                   min_dur: float = 0.83, cps: float = 17.0, two_lines: bool = False) -> list[dict]:
    limit = max_chars * (2 if two_lines else 1)
    chunks, cur = [], []

    def flush():
        if cur:
            chunks.append({"s": cur[0]["s"], "e": cur[-1]["e"], "text": " ".join(w["w"] for w in cur)})

    for w in words:
        text_len = len(" ".join(x["w"] for x in cur + [w]))
        if cur and (w["s"] - cur[-1]["e"] > gap or text_len > limit or w["e"] - cur[0]["s"] > max_dur
                    or re.search(r"[.!?؟،,]$", cur[-1]["w"])):
            flush()
            cur = []
        cur.append(w)
    flush()
    # timing polish: reading speed, minimum length, 2-frame gap
    for i, c in enumerate(chunks):
        nxt = chunks[i + 1]["s"] if i + 1 < len(chunks) else c["e"] + 2.0
        want = max(c["e"], c["s"] + max(min_dur, len(c["text"]) / cps))
        c["e"] = round(min(want, nxt - 0.07, c["s"] + max_dur), 3)
        if two_lines and len(c["text"]) > max_chars:
            ws = c["text"].split(" ")
            best = min(range(1, len(ws)), key=lambda k: abs(len(" ".join(ws[:k])) - len(" ".join(ws[k:]))))
            c["text"] = " ".join(ws[:best]) + "\n" + " ".join(ws[best:])
    return chunks


def cmd_srt(args) -> None:
    proj = ec.resolve_project(args.project)
    wp = proj / "analysis" / "words.json"
    if not wp.exists():
        ec.die("No words.json. Run transcribe.py first.")
    chunks = caption_chunks(ec.read_json(wp)["words"], two_lines=args.two_lines)
    out = []
    for i, c in enumerate(chunks, 1):
        out += [str(i), f"{srt_time(c['s'])} --> {srt_time(c['e'])}", c["text"], ""]
    p = ec.write_text(proj / "out" / "captions.srt", "\n".join(out))
    print(f"{len(chunks)} captions -> {p}")
    print("Check the wording before uploading: Whisper can mishear Syrian Arabic.")


def cmd_captions(args) -> None:
    """Add burned-in caption items (K###) from the word timings to the latest plan."""
    proj = ec.resolve_project(args.project)
    plan, path = load_plan(proj, args.plan)
    words = ec.read_json(proj / "analysis" / "words.json")["words"]
    plan["items"] = [it for it in plan["items"] if it.get("type") != "caption"]
    for i, c in enumerate(caption_chunks(words, max_chars=args.max_chars), 1):
        plan["items"].append({"id": f"K{i:03d}", "type": "caption", "at": c["s"], "dur": round(c["e"] - c["s"], 3),
                              "params": {"text": c["text"], "style": "caption", "position": args.position},
                              "why": "burned-in caption", "marker": False})
    plan.setdefault("style", {})["captions"] = "burned-in"
    ec.write_json(path, plan)
    print(f"Added {i} caption items to {path.name}")


def cmd_notes(args) -> None:
    from library import load_library, resolve_asset

    proj = ec.resolve_project(args.project)
    plan, _ = load_plan(proj, args.plan)
    lib = load_library()
    lines = [f"# Upload notes — {proj.name}", ""]
    chapters = sorted((it for it in active_items(plan) if it["type"] == "chapter"), key=lambda x: x["at"])
    if chapters:
        lines += ["## Chapters (paste into the description)", ""]
        for c in chapters:
            s = int(c["at"])
            lines.append(f"{s // 60}:{s % 60:02d} {c['params']['title']}")
        lines.append("")
    credits = []
    for it in active_items(plan):
        if it["type"] in ("broll", "sfx") and it.get("asset"):
            a = resolve_asset(it["asset"]["ref"], lib)
            if a and a.get("source") not in (None, "own", "unindexed"):
                credit = a.get("attribution") or f"{a.get('creator') or 'unknown'} ({a.get('source')}) – {a.get('license')}"
                if a.get("page_url"):
                    credit += f" – {a['page_url']}"
                credits.append(credit)
    if credits:
        lines += ["## Credits (required for CC BY; polite for the rest)", ""] + [f"- {c}" for c in sorted(set(credits))] + [""]
    lines += ["## Before you publish", "",
              "- Upload as Unlisted first and wait for the copyright check to finish.",
              "- Upload captions.srt as Arabic subtitles if you made one.",
              "- Tell me when it's live, so I can remind you to share the retention graph later.", ""]
    p = ec.write_text(proj / "out" / "upload-notes.md", "\n".join(lines))
    print(f"Notes: {p}")


# ------------------------------------------------------------------ bridge operations


def find_base(snap: dict, f0: int, f1: int) -> tuple[dict | None, dict | None, str | None]:
    """The clip of HIS cut that shows on screen at f0 (topmost non-editor video track)."""
    tracks = [t for t in snap["tracks"]["video"] if not str(t.get("name", "")).startswith("ED ")]
    tracks = [t for t in tracks if t.get("enabled", True)]
    tracks.sort(key=lambda t: -t["index"])
    for ti, tr in enumerate(tracks):
        for it in tr.get("items", []):
            if it["start"] <= f0 < it["end"] and it.get("enabled", True) is not False:
                media = it.get("media") or {}
                mtype = str(media.get("type", "")).lower()
                if not media.get("path") or not ("video" in mtype or "still" in mtype or not mtype):
                    return None, None, "a title, effect or compound clip is on top here"
                above = tracks[:ti]
                for up in above:
                    for o in up.get("items", []):
                        if o["start"] < f1 and o["end"] > f0:
                            return None, None, f"another layer ({up.get('name')}) is on top here"
                props = it.get("props") or {}
                if float(props.get("Opacity", 100) or 100) < 99 or float(props.get("ZoomX", 1) or 1) < 0.99:
                    return None, None, "the clip here is see-through or picture-in-picture"
                return it, tr, None
    return None, None, "no clip of yours under this spot"


def zoom_props(base_props: dict, s: float, cx: float, cy: float, w: int, h: int) -> dict:
    """Base transform x extra zoom s, moved so point (cx, cy) heads to the middle (edges never show)."""
    z0x = float(base_props.get("ZoomX", 1.0) or 1.0)
    z0y = float(base_props.get("ZoomY", 1.0) or 1.0)
    p0 = float(base_props.get("Pan", 0.0) or 0.0)
    t0 = float(base_props.get("Tilt", 0.0) or 0.0)
    qx, qy = (cx - 0.5) * w, (0.5 - cy) * h  # y up
    lim_x, lim_y = (s - 1) * w / 2, (s - 1) * h / 2
    tx = max(-lim_x, min(lim_x, -s * qx))
    ty = max(-lim_y, min(lim_y, -s * qy))
    props = {k: v for k, v in base_props.items() if k in ("RotationAngle", "FlipX", "FlipY", "CropLeft", "CropRight",
                                                          "CropTop", "CropBottom", "AnchorPointX", "AnchorPointY") and v not in (None, "")}
    props.update({"ZoomX": round(z0x * s, 4), "ZoomY": round(z0y * s, 4),
                  "Pan": round(p0 * s + tx, 2), "Tilt": round(t0 * s + ty, 2)})
    return props


def copy_props(base_props: dict) -> dict:
    keep = ("ZoomX", "ZoomY", "Pan", "Tilt", "RotationAngle", "FlipX", "FlipY", "CropLeft", "CropRight",
            "CropTop", "CropBottom", "AnchorPointX", "AnchorPointY")
    return {k: base_props[k] for k in keep if base_props.get(k) not in (None, "")}


def shake_ops(op: dict, hard: dict, f0: int, f1: int, fps: float, w: int, h: int) -> list[dict]:
    """Impact zoom: the hard punch-in cut into 2-frame pieces that jump a few pixels, fading out.
    Each piece is its own clip on the zoom track, so the whole thing is plain clips (no keyframes)."""
    step = 2
    n = max(1, (f1 - f0) // step)
    spare_x = (float(hard["ZoomX"]) - 1) * w / 2 * 0.6  # never show the picture edge
    spare_y = (float(hard["ZoomY"]) - 1) * h / 2 * 0.6
    amp_x, amp_y = min(0.02 * w, spare_x), min(0.02 * h, spare_y)
    cfps = op["src_len"] / max(1, f1 - f0)
    out = []
    for i in range(n):
        fade = 1.0 - i / n
        sign = 1 if i % 2 == 0 else -1
        seg_len = step if i < n - 1 else (f1 - f0) - step * i
        props = dict(hard)
        props["Pan"] = round(float(hard["Pan"]) + sign * amp_x * fade, 2)
        props["Tilt"] = round(float(hard["Tilt"]) - sign * amp_y * fade * 0.7, 2)
        seg = dict(op)
        seg.update({"id": op["id"] if i == 0 else f"{op['id']}~{i}",
                    "at": op["at"] + step * i / fps,
                    "src_start": op["src_start"] + int(round(step * i * cfps)),
                    "src_len": max(1, int(round(seg_len * cfps))), "props": props})
        out.append(seg)
    return out


def broll_fill_props(asset: dict, w: int, h: int, extra: float = 1.0) -> dict:
    aw, ah = asset.get("width") or w, asset.get("height") or h
    fit = min(w / aw, h / ah)
    z = max(w / (aw * fit), h / (ah * fit)) * extra
    return {"ZoomX": round(z, 4), "ZoomY": round(z, 4)} if abs(z - 1) > 0.001 else {}


def build_ops(plan: dict, proj: Path, snap: dict, backup: bool = True) -> tuple[list[dict], list[dict], list[str]]:
    """Plan + fresh timeline snapshot -> low-level bridge operations.
    Returns (ops, manual items for him, notes)."""
    from library import level_sfx, load_library, resolve_asset
    from text_cards import render_cards

    lib = load_library()
    tl = snap["timeline"]
    fps, start = float(tl["fps"]), int(tl["start_frame"])
    w, h = int(tl["width"]), int(tl["height"])
    tag = f"v{plan.get('version', 1)}"
    ops, manual, notes = [], [], []
    if backup:
        ops.append({"op": "backup", "id": "backup", "label": tag})
    items = sorted(active_items(plan), key=lambda x: (x["at"], x["id"]))

    def frames(sec):
        return start + int(round(float(sec) * fps))

    # text cards (pop-ups + burned captions) are rendered first, all at timeline size
    cards = [{"id": it["id"], **it.get("params", {})} for it in items if it["type"] in ("popup", "caption")]
    card_paths = render_cards(cards, proj / "out" / "text" / tag, w, h) if cards else {}
    sfx_lane_end = [0.0 for _ in SFX_TRACKS]
    for it in items:
        t, iid, p = it["type"], it["id"], it.get("params", {})
        color = "Orange"
        if it.get("status") == "unsure":
            manual.append({**it, "manual_reason": "I was not sure about this one: you decide"})
            continue
        if t in ("zoom", "freeze"):
            f0, f1 = frames(it["at"]), frames(item_end(it))
            base, _tr, why_not = find_base(snap, f0, f1)
            if base is None:
                manual.append({**it, "manual_reason": why_not})
                continue
            if f1 > base["end"]:
                f1 = base["end"]
                notes.append(f"{iid}: shortened to end with your clip at {ec.fmt_time((f1 - start) / fps)}")
                if (f1 - f0) / fps < 0.4:
                    manual.append({**it, "manual_reason": "your clip ends right here"})
                    continue
            media = base.get("media") or {}
            cfps = ec.num(media.get("fps"), fps) or fps
            exp = (base["end"] - base["start"]) * cfps / fps
            src_span = (base.get("src_end") or 0) - (base.get("src_start") or 0)
            if base.get("src_end") is not None and abs(src_span - exp) > max(2, 0.02 * exp):
                manual.append({**it, "manual_reason": "your clip is sped up or slowed down here"})
                continue
            src0 = int(base.get("src_start") or 0) + int(round((f0 - base["start"]) * cfps / fps))
            s = float(p.get("scale", 1.0))
            cx, cy = (p.get("center") or [0.5, 0.5])
            bprops = base.get("props") or {}
            if t == "zoom":
                hard = zoom_props(bprops, s, cx, cy, w, h)
                op = {"op": "place_segment", "id": iid, "track": TRACK[t], "base_uid": base["uid"],
                      "base_start": base["start"], "at": it["at"], "src_start": src0,
                      "src_len": max(1, int(round((f1 - f0) * cfps / fps))), "color": color}
                if p.get("mode", "hard") == "shake":
                    ops.extend(shake_ops(op, hard, f0, f1, fps, w, h))
                    continue
                if p.get("mode", "hard") == "smooth":
                    op["props"] = copy_props(bprops)
                    op["fusion_zoom"] = {"scale": s, "cx": cx, "cy": cy, "out": bool(p.get("out", False)),
                                         "ease_frames": max(2, int(round(float(p.get("ease", 0.3)) * fps)))}
                    op["fallback_props"] = hard
                else:
                    op["props"] = hard
                ops.append(op)
            else:  # freeze: still of the exact frame, laid over his clip
                png = proj / "out" / "freeze" / f"{iid}.png"
                png.parent.mkdir(parents=True, exist_ok=True)
                src_sec = src0 / cfps
                if "still" in str(media.get("type", "")).lower():
                    png = Path(media["path"])
                else:
                    ec.run([ec.ffmpeg_bin(), "-v", "error", "-y", "-ss", f"{src_sec:.4f}", "-i", media["path"],
                            "-frames:v", "1", str(png)])
                props = zoom_props(bprops, s, cx, cy, w, h) if s > 1.001 else copy_props(bprops)
                ops.append({"op": "place", "id": iid, "track": TRACK[t], "ttype": "video", "path": str(png),
                            "at": it["at"], "dur": (f1 - f0) / fps, "still": True, "props": props, "color": color})
        elif t == "broll":
            a = resolve_asset(it["asset"]["ref"], lib)
            if not a or str(it["asset"]["ref"]).startswith("candidate:"):
                manual.append({**it, "manual_reason": "clip not downloaded/approved yet"})
                continue
            extra = float(p.get("scale", 1.0))
            props = broll_fill_props(a, w, h, extra) if p.get("fit", "fill") == "fill" else (
                {"ZoomX": extra, "ZoomY": extra} if extra != 1.0 else {})
            ops.append({"op": "place", "id": iid, "track": TRACK[t], "ttype": "video", "path": a["path"],
                        "at": it["at"], "dur": it["dur"], "src_in": float(it["asset"].get("in", 0.0)),
                        "still": a.get("kind") == "image", "props": props, "color": color})
            if it["asset"].get("audio") and a.get("has_audio"):
                ops.append({"op": "place", "id": iid + "a", "track": BROLL_AUDIO_TRACK, "ttype": "audio",
                            "path": a["path"], "at": it["at"], "dur": it["dur"],
                            "src_in": float(it["asset"].get("in", 0.0))})
        elif t in ("popup", "caption"):
            ops.append({"op": "place", "id": iid, "track": TRACK[t], "ttype": "video", "path": str(card_paths[iid]),
                        "at": it["at"], "dur": it["dur"], "still": True, "color": color})
        elif t == "sfx":
            a = resolve_asset(it["asset"]["ref"], lib)
            if not a or str(it["asset"]["ref"]).startswith("candidate:"):
                manual.append({**it, "manual_reason": "sound not downloaded/approved yet"})
                continue
            path, peak = level_sfx(a, float(p.get("gain_db", 0.0)))
            at = float(it["at"]) - (peak if p.get("align", "peak") == "peak" else 0.0)
            at = max(0.0, at)
            length = float(it.get("dur") or a.get("duration") or 1.0)
            length = min(length, float(a.get("duration") or length))
            lane = next((i for i, e in enumerate(sfx_lane_end) if e <= at + 1e-3), None)
            if lane is None:
                notes.append(f"{iid}: more than two sounds at once, skipped")
                continue
            sfx_lane_end[lane] = at + length
            ops.append({"op": "place", "id": iid, "track": SFX_TRACKS[lane], "ttype": "audio", "path": str(path),
                        "at": at, "dur": length, "src_in": 0.0})
        elif t in MANUAL_TYPES:
            if t != "chapter":
                manual.append(it)
    # markers last, so a marker never blocks a clip
    manual_ids = {m["id"] for m in manual}
    for it in items:
        if not wants_marker(it) and it["id"] not in manual_ids:
            continue
        t = it["type"]
        note = f"{TYPE_LABEL.get(t, t)}: {it.get('why', '')}"
        reason = next((m.get("manual_reason") for m in manual if m["id"] == it["id"]), None)
        if reason:
            note = f"DO BY HAND ({reason}). " + note
        if t == "transition":
            note += f" | Add a {it.get('params', {}).get('kind', 'transition')} here: select the cut, Ctrl+T, then swap it in Effects > Video Transitions."
        if it.get("quote"):
            note += f" | says: {it['quote']}"
        ops.append({"op": "marker", "id": it["id"], "at": it["at"],
                    "color": "Red" if reason else ec.TYPE_COLOR.get(t, "Blue"),
                    "name": ec.ascii_marker_name(it), "note": note[:900],
                    "dur_frames": max(1, int(round(float(it.get("dur") or 0) * fps))),
                    "custom": f"editor:{tag}:{it['id']}"})
    return ops, manual, notes


def main() -> None:
    ec.setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, **extra):
        s = sub.add_parser(name)
        s.add_argument("project", nargs="?")
        s.add_argument("--plan")
        for k, v in extra.items():
            s.add_argument(k, **v)
        s.set_defaults(fn=fn)

    add("init", cmd_init, **{"--channel": {"default": "srb-gamer"}, "--force": {"action": "store_true"}})
    add("bump", cmd_bump, **{"--note": {}})
    add("validate", cmd_validate, **{"--strict": {"action": "store_true"}})
    add("sheet", cmd_sheet, **{"--no-previews": {"action": "store_true"}})
    add("edl", cmd_edl)
    add("srt", cmd_srt, **{"--two-lines": {"action": "store_true"}})
    add("captions", cmd_captions, **{"--max-chars": {"type": int, "default": 32}, "--position": {"default": "bottom"}})
    add("notes", cmd_notes)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
