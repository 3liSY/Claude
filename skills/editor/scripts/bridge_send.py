"""Talk to the Editor Bridge running inside DaVinci Resolve.

  python bridge_send.py status                  # is the bridge running?
  python bridge_send.py ping                    # Resolve version, project, timeline facts
  python bridge_send.py prepare SLUG            # new project: read timeline + render review.mp4
  python bridge_send.py snapshot PROJECT --label after    # read the timeline again (for learning)
  python bridge_send.py apply PROJECT [--replace] [--no-backup]
  python bridge_send.py remove PROJECT          # take back everything the last apply placed
  python bridge_send.py selftest                # one-time check of how his Resolve behaves
  python bridge_send.py stop

If the bridge is not running, he starts it in Resolve: Workspace > Scripts > Editor Bridge.
"""
from __future__ import annotations

import argparse
import shutil
import time
import uuid
from pathlib import Path

import edcommon as ec

START_HINT = ("The Resolve bridge isn't running. In DaVinci Resolve: Workspace > Scripts > Editor Bridge "
              "(Resolve must have a project and the timeline open). Then try again.")


def paths():
    b = ec.bridge_dir()
    return b, b / "inbox", b / "outbox", b / "status.json"


def bridge_alive(max_age: float = 8.0) -> tuple[bool, dict]:
    """Running = recent heartbeat. Busy jobs beat less often, so waits allow more slack."""
    _, _, _, st = paths()
    if not st.exists():
        return False, {}
    try:
        s = ec.read_json(st)
    except Exception:
        return False, {}
    age = time.time() - float(s.get("heartbeat", 0))
    return (s.get("state") != "stopped" and age < max_age), s


def send(action: str, args: dict | None = None, timeout: float = 120, quiet: bool = False) -> dict:
    base, inbox, outbox, _ = paths()
    for d in (inbox, outbox):
        d.mkdir(parents=True, exist_ok=True)
    alive, st = bridge_alive()
    if not alive:
        ec.die(START_HINT, 3)
    if st.get("bridge_version") != ec.BRIDGE_VERSION and not quiet:
        print(f"(note: bridge in Resolve is v{st.get('bridge_version')}, skill expects v{ec.BRIDGE_VERSION}; "
              f"run setup_check.py --install-bridge)")
    jid = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    job = {"id": jid, "action": action, "args": args or {}, "created": time.time(),
           "expires": time.time() + 60, "client_version": ec.BRIDGE_VERSION}
    tmp = inbox / f"{jid}.tmp"
    ec.write_json(tmp, job)
    tmp.replace(inbox / f"{jid}.json")
    out = outbox / f"{jid}.json"
    t0 = time.time()
    last_note = 0.0
    while not out.exists():
        time.sleep(0.3)
        el = time.time() - t0
        ok, st = bridge_alive(max_age=60)
        if not ok and el > 10:
            (inbox / f"{jid}.json").unlink(missing_ok=True)
            ec.die("The bridge stopped answering. " + START_HINT, 3)
        if el > timeout:
            (inbox / f"{jid}.json").unlink(missing_ok=True)
            ec.die(f"No answer after {timeout:.0f}s ({action}). Check Resolve for a dialog box.", 4)
        if not quiet and el - last_note > 15:
            print(f"  ... still working ({el:.0f}s)")
            last_note = el
    time.sleep(0.1)
    res = ec.read_json(out)
    out.unlink(missing_ok=True)
    if not res.get("ok"):
        ec.die(f"Resolve said: {res.get('error')}", 5)
    return res["result"]


# ------------------------------------------------------------------ commands


def cmd_status(args) -> None:
    alive, st = bridge_alive()
    if alive:
        print(f"Bridge running (v{st.get('bridge_version')}, {st.get('state')}).")
    else:
        print(START_HINT)


def cmd_ping(args) -> None:
    r = send("ping", timeout=20)
    print(f"{r['product']} {r['version']} · project '{r['project']}' · Python {r.get('python')}")
    t = r.get("timeline")
    if t:
        print(f"Timeline '{t['name']}': {t['fps']} fps, {t['width']}x{t['height']}, starts {t['start_tc']} "
              f"(frame {t['start_frame']}), tracks V{t['tracks']['video']} A{t['tracks']['audio']}")
    else:
        print("No timeline open.")
    if not r.get("calibration"):
        print("Self-test not done yet on this PC: run bridge_send.py selftest once.")


def cmd_prepare(args) -> None:
    slug = args.slug if args.slug[:4].isdigit() else f"{ec.today()}_{ec.slugify(args.slug)}"
    proj = ec.project_dir(slug)
    print(f"Project folder: {proj}")
    ping = send("ping", timeout=20)
    ec.write_json(proj / "bridge" / "ping.json", ping)
    if not ping.get("timeline"):
        ec.die("Open the video's timeline in Resolve first.")
    print(f"Reading timeline '{ping['timeline']['name']}' ...")
    snap = send("read_timeline", timeout=180)
    ec.write_json(proj / "bridge" / "snapshot_before.json", snap)
    if not args.no_render:
        review = proj / "review.mp4"
        if review.exists():
            review.unlink()
        print("Rendering a small review copy (this can take a few minutes) ...")
        cfg = ec.load_config()["review_render"]
        r = send("render_review", {"target_dir": str(proj), "name": "review",
                                   "long_side": max(cfg["width"], cfg["height"])}, timeout=3600)
        got = Path(r["path"])
        if got.resolve() != review.resolve():
            shutil.move(str(got), str(review))
        print(f"Review copy: {review}")
    t = snap["timeline"]
    ec.write_json(proj / "project.json", {"slug": slug, "created": ec.now_iso(), "timeline": t,
                                          "resolve": f"{ping['product']} {ping['version']}"})
    print(f"Ready. Next: transcribe.py {slug} / analyze.py {slug} / sheets.py {slug}")


def cmd_snapshot(args) -> None:
    proj = ec.resolve_project(args.project)
    snap = send("read_timeline", timeout=180)
    p = ec.write_json(proj / "bridge" / f"snapshot_{args.label}.json", snap)
    print(f"Snapshot: {p}")


def applied_files(proj: Path) -> list[Path]:
    return sorted((proj / "bridge").glob("applied_v*.json"), key=lambda p: p.stat().st_mtime)


def active_applied(proj: Path) -> Path | None:
    live = [p for p in applied_files(proj) if not ec.read_json(p).get("removed")]
    return live[-1] if live else None


def do_remove(proj: Path, applied_path: Path) -> dict:
    from plan import ALL_TRACKS

    rec = ec.read_json(applied_path)
    uids = [r["result"]["uid"] for r in rec.get("results", []) if r.get("ok") and r.get("result", {}).get("uid")]
    res = send("remove", {"uids": uids, "marker_prefix": f"editor:v{rec['plan_version']}:",
                          "track_names": ALL_TRACKS}, timeout=300)
    rec["removed"] = ec.now_iso()
    ec.write_json(applied_path, rec)
    return res


def cmd_apply(args) -> None:
    from plan import build_ops, load_plan, validate

    proj = ec.resolve_project(args.project)
    plan, plan_path = load_plan(proj, args.plan)
    errors, warns = validate(plan, proj, strict=True)
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
        ec.die("Plan has errors; nothing was sent to Resolve.", 2)
    prev = active_applied(proj)
    if prev and not args.replace:
        ec.die(f"{prev.name} is already on the timeline. Use --replace to swap it for v{plan['version']}.")
    ping = send("ping", timeout=20, quiet=True)
    if not ping.get("calibration"):
        print("(self-test not run yet: using safe defaults. Run 'bridge_send.py selftest' once.)")
    want = plan.get("timeline", {}).get("name")
    have = (ping.get("timeline") or {}).get("name")
    if want and have and want != have and not args.force:
        ec.die(f"Resolve has timeline '{have}' open, but the plan is for '{want}'. Open the right one (or --force).")
    if prev:
        print(f"Removing {prev.name} first ...")
        do_remove(proj, prev)
    print("Reading the timeline as it is right now ...")
    snap = send("read_timeline", timeout=180, quiet=True)
    v = plan["version"]
    ec.write_json(proj / "bridge" / f"snapshot_pre_v{v}.json", snap)
    backup = not args.no_backup and not applied_files(proj)
    ops, manual, notes = build_ops(plan, proj, snap, backup=backup)
    print(f"Placing {sum(1 for o in ops if o['op'] != 'marker' and o['op'] != 'backup')} edits "
          f"and {sum(1 for o in ops if o['op'] == 'marker')} markers ...")
    res = send("apply", {"ops": ops}, timeout=ec.load_config()["bridge"]["timeout_s"])
    rec = {"plan_version": v, "plan_file": plan_path.name, "applied": ec.now_iso(), "timeline": res.get("timeline"),
           "ops": ops, "results": res["results"], "manual": manual, "notes": notes}
    out = ec.write_json(proj / "bridge" / f"applied_v{v}.json", rec)
    ok = [r for r in res["results"] if r.get("ok")]
    bad = [r for r in res["results"] if not r.get("ok")]
    drift = [r for r in ok if r.get("result", {}).get("wanted_start") not in (None, r["result"].get("start"))]
    print(f"Done: {len(ok)} worked, {len(bad)} failed. Record: {out}")
    for r in bad:
        print(f"  FAILED {r['id']} ({r['op']}): {r.get('error')}")
    for r in drift:
        print(f"  CHECK {r['id']}: landed at frame {r['result']['start']}, wanted {r['result']['wanted_start']}")
    for m in manual:
        print(f"  BY HAND {m['id']} {m['type']} at {ec.fmt_time(m['at'])}: {m.get('manual_reason') or m.get('why', '')}")
    for n in notes:
        print(f"  note: {n}")
    if any(r.get("op") == "backup" and r.get("ok") for r in res["results"]):
        b = next(r for r in res["results"] if r.get("op") == "backup")
        print(f"Backup of your timeline: '{b['result']['backup']}'")


def cmd_remove(args) -> None:
    proj = ec.resolve_project(args.project)
    target = Path(args.applied) if args.applied else active_applied(proj)
    if not target:
        ec.die("Nothing applied to remove.")
    res = do_remove(proj, target)
    print(f"Removed {res['clips_found']} clips and {res['markers_removed']} markers "
          f"(empty editor tracks removed: {', '.join(res['tracks_removed']) or 'none'}).")


def make_test_media(folder: Path) -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    vid, img, aud = folder / "selftest.mp4", folder / "selftest.png", folder / "selftest.wav"
    ff = ec.ffmpeg_bin()
    if not vid.exists():
        ec.run([ff, "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=60:duration=4",
                "-f", "lavfi", "-i", "sine=f=440:d=4", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-shortest", str(vid)])
    if not img.exists():
        ec.run([ff, "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=1280x720", "-frames:v", "1", str(img)])
    if not aud.exists():
        ec.run([ff, "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=880:d=1", str(aud)])
    return {"video": str(vid), "image": str(img), "audio": str(aud), "still_out": str(folder / "still_test.png")}


def cmd_selftest(args) -> None:
    media = make_test_media(ec.bridge_dir() / "selftest")
    print("Running the self-test on a temporary timeline (it deletes itself) ...")
    r = send("selftest", media, timeout=300)
    c = r["checks"]
    def yn(v):
        return "yes" if v is True else "NO" if v is False else "unknown"
    print(f"  clips land where asked:      {yn(c.get('record_absolute') is not None)} (absolute frames: {c.get('record_absolute')})")
    print(f"  clip length exact:           {yn(c.get('end_inclusive') is not None)} (got {c.get('end_duration')} of 60 frames)")
    print(f"  zoom/position settable:      {yn(c.get('zoom_props'))} / {yn(c.get('pan_props'))}")
    print(f"  smooth (Fusion) zoom:        {yn(c.get('fusion_zoom'))} {c.get('fusion_error', '')}")
    print(f"  pictures (text cards):       {yn(c.get('still_ok'))} (got {c.get('still_duration')} frames)")
    print(f"  sounds on new audio track:   {yn(c.get('audio_ok'))}")
    print(f"  markers with notes:          {yn(c.get('marker_ok'))} / hidden id: {yn(c.get('marker_custom'))}")
    print(f"  delete what it placed:       {yn(c.get('delete_ok'))}")
    print(f"  export still frame:          {yn(c.get('export_still'))}")
    ec.write_json(ec.brain_dir() / "selftest.json", r)
    print(f"Saved: {ec.brain_dir() / 'selftest.json'}")


def cmd_stop(args) -> None:
    alive, _ = bridge_alive()
    if not alive:
        print("Bridge is not running.")
        return
    send("stop", timeout=15)
    print("Bridge stopped.")


def main() -> None:
    ec.setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    sub.add_parser("ping").set_defaults(fn=cmd_ping)
    s = sub.add_parser("prepare"); s.add_argument("slug"); s.add_argument("--no-render", action="store_true")
    s.set_defaults(fn=cmd_prepare)
    s = sub.add_parser("snapshot"); s.add_argument("project", nargs="?"); s.add_argument("--label", default="after")
    s.set_defaults(fn=cmd_snapshot)
    s = sub.add_parser("apply"); s.add_argument("project", nargs="?"); s.add_argument("--plan")
    s.add_argument("--replace", action="store_true"); s.add_argument("--no-backup", action="store_true")
    s.add_argument("--force", action="store_true"); s.set_defaults(fn=cmd_apply)
    s = sub.add_parser("remove"); s.add_argument("project", nargs="?"); s.add_argument("--applied")
    s.set_defaults(fn=cmd_remove)
    sub.add_parser("selftest").set_defaults(fn=cmd_selftest)
    sub.add_parser("stop").set_defaults(fn=cmd_stop)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
