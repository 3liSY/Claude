"""Map YouTube retention dips/spikes back to the edits around them.

  python retention.py PROJECT --dips 1:23,4:05 --spikes 2:10      # times read off his retention graph
  python retention.py PROJECT --csv "Table data.csv"              # a Studio export with time + retention columns

For each moment: what was said, what the picture did, which planned edits were
within 5 s. Writes analysis/retention.md. Claude then explains the likely cause
in plain words and turns real patterns into rules in edit-preferences.md.
"""
from __future__ import annotations

import argparse
import csv
import re

import edcommon as ec

WINDOW = 5.0


def read_curve(path: str, duration: float) -> list[tuple[float, float]]:
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        rows = list(csv.reader(f))
    head = [h.lower() for h in rows[0]]
    tcol = next((i for i, h in enumerate(head) if re.search(r"position|time|moment|second", h)), None)
    rcol = next((i for i, h in enumerate(head) if re.search(r"retention|watching|audience", h)), None)
    if tcol is None or rcol is None:
        ec.die(f"Could not find time + retention columns in: {rows[0]}")
    pct_time = "%" in head[tcol] or "percent" in head[tcol]
    curve = []
    for r in rows[1:]:
        try:
            tv = r[tcol].strip().rstrip("%")
            t = ec.parse_time(tv)
            if pct_time:
                t = t / 100.0 * duration
            v = float(r[rcol].strip().rstrip("%"))
            curve.append((t, v))
        except (ValueError, IndexError):
            continue
    return sorted(curve)


def find_moments(curve: list[tuple[float, float]], k: int = 5) -> tuple[list[float], list[float]]:
    drops, rises = [], []
    for (t0, v0), (t1, v1) in zip(curve, curve[1:]):
        rate = (v1 - v0) / max(0.5, t1 - t0)
        (drops if rate < 0 else rises).append((rate, t0))
    drops.sort()
    rises.sort(reverse=True)
    pick = lambda lst: sorted({round(t, 1) for _, t in lst[:k]})
    return pick(drops), pick([r for r in rises if r[0] > 0])


def context(t: float, plan: dict | None, words: list[dict]) -> tuple[str, str]:
    said = " ".join(w["w"] for w in words if t - 3 <= w["s"] <= t + 3)
    near = []
    if plan:
        for it in plan.get("items", []):
            if it.get("status") == "rejected":
                continue
            if abs(float(it["at"]) - t) <= WINDOW:
                near.append(f"{it['id']} {it['type']} @{ec.fmt_time(it['at'])}")
    return said, ", ".join(near) or "no planned edit nearby"


def main() -> None:
    ec.setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", nargs="?")
    ap.add_argument("--dips", default="")
    ap.add_argument("--spikes", default="")
    ap.add_argument("--csv")
    args = ap.parse_args()
    proj = ec.resolve_project(args.project)
    words = ec.read_json(proj / "analysis" / "words.json")["words"] if (proj / "analysis" / "words.json").exists() else []
    plan = None
    plans = sorted((proj / "plan").glob("edit_plan_v*.json"), key=lambda p: int(re.search(r"_v(\d+)", p.stem).group(1)))
    if plans:
        plan = ec.read_json(plans[-1])
    duration = float((plan or {}).get("timeline", {}).get("duration") or 0)
    dips = [ec.parse_time(x) for x in args.dips.split(",") if x.strip()]
    spikes = [ec.parse_time(x) for x in args.spikes.split(",") if x.strip()]
    if args.csv:
        d2, s2 = find_moments(read_curve(args.csv, duration))
        dips += d2
        spikes += s2
    lines = [f"# Retention moments — {proj.name}", "",
             "Dips = people skip or leave. Spikes = people rewatch (great moment, or confusing).", "",
             "| moment | kind | what he says | edits within 5 s |", "|---|---|---|---|"]
    for kind, times in (("DIP", dips), ("SPIKE", spikes)):
        for t in sorted(times):
            said, near = context(t, plan, words)
            lines.append(f"| {ec.fmt_time(t)} | {kind} | {said[:90]} | {near} |")
    out = ec.write_text(proj / "analysis" / "retention.md", "\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
