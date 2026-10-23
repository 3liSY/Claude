"""Learn from what he changed after the skill placed its edits.

  python bridge_send.py snapshot PROJECT --label after     # first: read his finished timeline
  python learn.py PROJECT

Compares every clip the bridge placed (by Resolve's unique id) with the timeline
now: kept, deleted, moved, trimmed, re-zoomed. Also lists what he added himself
(things the plan missed). Writes bridge/learn_vN.json, appends one line per video
to brain/learned.jsonl (for trends across videos), and prints suggested rules.
Claude turns the suggestions into dated lines in brain/edit-preferences.md and
tells him in plain words what it learned.
"""
from __future__ import annotations

import argparse
import json
from statistics import mean

import edcommon as ec


def index_items(snap: dict) -> dict[str, dict]:
    out = {}
    for ttype in ("video", "audio"):
        for tr in snap["tracks"].get(ttype, []):
            for it in tr.get("items", []):
                out[it["uid"]] = {**it, "track": tr.get("name"), "ttype": ttype}
    return out


def diff(applied: dict, plan: dict, pre: dict, after: dict) -> dict:
    fps = float(after["timeline"]["fps"])
    now = index_items(after)
    before = index_items(pre)
    plan_items = {it["id"]: it for it in plan.get("items", [])}
    placed_uids = set()
    rows = []
    for r in applied.get("results", []):
        if not r.get("ok") or not (r.get("result") or {}).get("uid"):
            continue
        res = r["result"]
        uid = res["uid"]
        placed_uids.add(uid)
        if "~" in r["id"]:  # later pieces of a shake zoom: the first piece speaks for the whole edit
            continue
        pid = r["id"][:-1] if r["id"].endswith("a") and r["id"][:-1] in plan_items else r["id"]
        it = plan_items.get(pid, {})
        row = {"id": r["id"], "type": it.get("type", "?"), "asset": (it.get("asset") or {}).get("ref"),
               "planned_at": it.get("at"), "planned_dur": it.get("dur")}
        cur = now.get(uid)
        if not cur:
            row["fate"] = "deleted"
        else:
            d_start = (cur["start"] - res["start"]) / fps
            d_dur = ((cur["end"] - cur["start"]) - (res["end"] - res["start"])) / fps
            row.update({"d_start": round(d_start, 3), "d_dur": round(d_dur, 3),
                        "final_dur": round((cur["end"] - cur["start"]) / fps, 3)})
            fate = []
            if abs(d_start) >= 2 / fps:
                fate.append("moved")
            if abs(d_dur) >= 2 / fps:
                fate.append("trimmed" if d_dur < 0 else "extended")
            if cur.get("enabled") is False:
                fate.append("disabled")
            if it.get("type") == "zoom":
                planned = (next((o for o in applied["ops"] if o.get("id") == r["id"]), {}).get("props") or {}).get("ZoomX")
                got = (cur.get("props") or {}).get("ZoomX")
                if planned and got and abs(float(got) - float(planned)) > 0.01:
                    fate.append("rezoomed")
                    row["zoom_planned"], row["zoom_final"] = float(planned), float(got)
            row["fate"] = "+".join(fate) or "kept"
        rows.append(row)
    added = []
    for uid, cur in now.items():
        if uid in placed_uids or uid in before:
            continue
        media = cur.get("media") or {}
        added.append({"track": cur.get("track"), "ttype": cur["ttype"],
                      "at": round((cur["start"] - after["timeline"]["start_frame"]) / fps, 2),
                      "dur": round((cur["end"] - cur["start"]) / fps, 2),
                      "name": media.get("name") or cur.get("name"), "path": media.get("path")})
    his_changed = sum(1 for uid, b in before.items() if uid in now and (now[uid]["start"], now[uid]["end"]) != (b["start"], b["end"]))
    his_deleted = sum(1 for uid in before if uid not in now)
    return {"plan_version": applied.get("plan_version"), "rows": rows, "added_by_him": added,
            "his_clips_changed": his_changed, "his_clips_deleted": his_deleted}


def stats(d: dict) -> dict:
    by: dict[str, dict] = {}
    for r in d["rows"]:
        s = by.setdefault(r["type"], {"placed": 0, "kept": 0, "deleted": 0, "moved": [], "dur_change": [],
                                       "rezoom": [], "deleted_assets": []})
        s["placed"] += 1
        if r["fate"] == "deleted":
            s["deleted"] += 1
            if r.get("asset"):
                s["deleted_assets"].append(r["asset"])
            continue
        if r["fate"] == "kept":
            s["kept"] += 1
        if "moved" in r["fate"]:
            s["moved"].append(r["d_start"])
        if "trimmed" in r["fate"] or "extended" in r["fate"]:
            s["dur_change"].append(r["d_dur"])
        if "rezoomed" in r["fate"]:
            s["rezoom"].append((r["zoom_planned"], r["zoom_final"]))
    return by


def suggestions(by: dict, d: dict) -> list[str]:
    out = []
    for t, s in by.items():
        n = s["placed"]
        if n == 0:
            continue
        if s["deleted"] / n >= 0.4 and n >= 3:
            out.append(f"He deleted {s['deleted']} of {n} {t} edits: use fewer {t} edits (or different ones).")
        elif s["kept"] / n >= 0.8 and n >= 3:
            out.append(f"He kept {s['kept']} of {n} {t} edits untouched: this density/style works.")
        if len(s["moved"]) >= 2:
            avg = mean(s["moved"])
            if abs(avg) >= 0.08:
                out.append(f"He moves {t} edits {abs(avg):.2f}s {'earlier' if avg < 0 else 'later'} on average: shift timing.")
        if len(s["dur_change"]) >= 2:
            avg = mean(s["dur_change"])
            if abs(avg) >= 0.2:
                out.append(f"He makes {t} edits {abs(avg):.1f}s {'shorter' if avg < 0 else 'longer'} on average.")
        if s["rezoom"]:
            pl = mean(p for p, _ in s["rezoom"])
            fi = mean(f for _, f in s["rezoom"])
            out.append(f"He changed zoom amounts from ~{pl:.0%} to ~{fi:.0%}.")
        rep = {a: s["deleted_assets"].count(a) for a in set(s["deleted_assets"])}
        for a, k in rep.items():
            if k >= 2:
                out.append(f"He removed {a} {k} times: stop using it (or ask him).")
    if d["added_by_him"]:
        kinds = {}
        for a in d["added_by_him"]:
            kinds.setdefault(a["track"] or a["ttype"], []).append(a)
        for track, lst in kinds.items():
            out.append(f"He added {len(lst)} clip(s) himself on '{track}' (e.g. {lst[0]['name']} at {ec.fmt_time(lst[0]['at'])}): "
                       f"look at what the plan missed there.")
    if d["his_clips_changed"] or d["his_clips_deleted"]:
        out.append(f"He also changed his own cut ({d['his_clips_changed']} clips moved/trimmed, {d['his_clips_deleted']} removed): "
                   f"timing comparisons may be off where the cut changed.")
    return out


def main() -> None:
    ec.setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", nargs="?")
    ap.add_argument("--after", default="after", help="snapshot label (default: after)")
    args = ap.parse_args()
    proj = ec.resolve_project(args.project)
    applied_files = sorted((proj / "bridge").glob("applied_v*.json"), key=lambda p: p.stat().st_mtime)
    if not applied_files:
        ec.die("Nothing was applied in this project, so there is nothing to compare.")
    applied = ec.read_json(applied_files[-1])
    v = applied["plan_version"]
    plan = ec.read_json(proj / "plan" / applied["plan_file"])
    pre = ec.read_json(proj / "bridge" / f"snapshot_pre_v{v}.json")
    after_p = proj / "bridge" / f"snapshot_{args.after}.json"
    if not after_p.exists():
        ec.die(f"Missing {after_p.name}. Run: bridge_send.py snapshot {proj.name} --label {args.after}")
    after = ec.read_json(after_p)
    d = diff(applied, plan, pre, after)
    by = stats(d)
    sugg = suggestions(by, d)
    d["stats"], d["suggestions"] = by, sugg
    ec.write_json(proj / "bridge" / f"learn_v{v}.json", d)
    line = {"date": ec.today(), "project": proj.name, "plan_version": v,
            "stats": {t: {k: (len(x) if isinstance(x, list) else x) for k, x in s.items()} for t, s in by.items()},
            "added_by_him": len(d["added_by_him"]), "suggestions": sugg}
    ec.append_text(ec.brain_dir() / "learned.jsonl", json.dumps(line, ensure_ascii=False) + "\n")
    print(f"Compared plan v{v} with his timeline:")
    for t, s in sorted(by.items()):
        print(f"  {t:10s} placed {s['placed']:3d} · kept {s['kept']:3d} · deleted {s['deleted']:3d} · "
              f"moved {len(s['moved']):3d} · length changed {len(s['dur_change']):3d}")
    if d["added_by_him"]:
        print(f"  he added {len(d['added_by_him'])} clip(s) himself")
    print("Suggested rules (write the real ones into brain/edit-preferences.md, dated):")
    for s in sugg or ["(no strong pattern yet: one video is not enough; keep collecting)"]:
        print(f"  - {s}")


if __name__ == "__main__":
    main()
