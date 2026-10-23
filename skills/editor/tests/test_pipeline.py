"""End-to-end test: the real scripts + the real bridge, against a fake Resolve.

  python tests/test_pipeline.py

Needs ffmpeg, numpy, Pillow and a Chromium/Edge browser. Transcription is faked
(no Whisper needed). Everything happens in a temp folder.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SCRIPTS = SKILL / "scripts"
TMP = Path(tempfile.mkdtemp(prefix="editor_test_"))
HOME = TMP / "home"
os.environ["EDITOR_HOME"] = str(HOME)
os.environ["EDITOR_BRIDGE_TEST"] = "1"
sys.path[:0] = [str(SCRIPTS), str(HERE)]

import mock_resolve as mr  # noqa: E402

FF = ["ffmpeg", "-v", "error", "-y"]


def sh(*args, ok=True):
    cp = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, cwd=SCRIPTS,
                        env={**os.environ})
    out = cp.stdout + cp.stderr
    print(f"$ {' '.join(map(str, args))}\n{out.strip()}\n")
    if ok and cp.returncode != 0:
        raise SystemExit(f"FAILED ({cp.returncode}): {args}")
    return out


def make_media():
    m = TMP / "media"
    (m / "broll").mkdir(parents=True)
    (m / "sfx").mkdir(parents=True)
    subprocess.run(FF + ["-f", "lavfi", "-i", "testsrc2=size=1920x1080:rate=60:duration=20", "-f", "lavfi",
                         "-i", "sine=f=200:d=20", "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac",
                         "-shortest", m / "aroll1.mp4"], check=True)
    subprocess.run(FF + ["-f", "lavfi", "-i", "smptebars=size=1920x1080:rate=60:duration=15", "-f", "lavfi",
                         "-i", "sine=f=300:d=15", "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac",
                         "-shortest", m / "aroll2.mp4"], check=True)
    subprocess.run(FF + ["-f", "lavfi", "-i", "mandelbrot=size=1280x720:rate=30", "-t", "6", "-c:v", "libx264",
                         "-preset", "ultrafast", m / "broll" / "cube explode.mp4"], check=True)
    subprocess.run(FF + ["-f", "lavfi", "-i", "anoisesrc=d=0.8:a=0.5", "-af",
                         "volume='if(between(t,0.25,0.35),1,0.1)':eval=frame", m / "sfx" / "whoosh fast.wav"], check=True)
    subprocess.run(FF + ["-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=60:duration=30", "-f", "lavfi",
                         "-i", "sine=f=220:d=30", "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac",
                         "-shortest", m / "review_src.mp4"], check=True)
    subprocess.run(FF + ["-f", "lavfi", "-i", "color=c=red:size=600x200", "-frames:v", "1", m / "title.png"], check=True)
    return m


class TitleItem(mr.TimelineItem):
    """A Fusion title: no media pool item."""

    def GetMediaPoolItem(self):
        return None

    def GetName(self):
        return "Text+"


def build_project(m):
    proj = mr.Project(str(m / "review_src.mp4"))
    tl = mr.Timeline(proj, "Main", fps=60, start=216000)
    proj.timelines.append(tl)
    proj.current = tl
    pool = proj.GetMediaPool()
    a1, a2 = pool.ImportMedia([str(m / "aroll1.mp4"), str(m / "aroll2.mp4")])
    pool.AppendToTimeline([{"mediaPoolItem": a1, "startFrame": 60, "endFrame": 60 + 1080 - 1, "trackIndex": 1,
                            "recordFrame": 216000, "mediaType": 1}])
    pool.AppendToTimeline([{"mediaPoolItem": a2, "startFrame": 0, "endFrame": 719, "trackIndex": 1,
                            "recordFrame": 217080, "mediaType": 1}])
    pool.AppendToTimeline([{"mediaPoolItem": a1, "startFrame": 60, "endFrame": 60 + 1080 - 1, "trackIndex": 1,
                            "recordFrame": 216000, "mediaType": 2}])
    tl.AddTrack("video")
    title = TitleItem(mr.MediaPoolItem(str(m / "title.png")), 216000 + 25 * 60, 120, 0, "video")
    tl.tracks["video"][1]["items"].append(title)
    return proj, tl


def start_bridge(resolve):
    spec = importlib.util.spec_from_file_location("editor_bridge", SKILL / "resolve" / "Editor Bridge.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    th = threading.Thread(target=mod.Bridge(resolve).run, daemon=True)
    th.start()
    for _ in range(50):
        if (HOME / "bridge" / "status.json").exists():
            return th
        time.sleep(0.1)
    raise SystemExit("bridge did not start")


def main():
    m = make_media()
    proj, tl = build_project(m)
    start_bridge(mr.Resolve(proj))
    sh("setup_check.py", "--init")
    sh("bridge_send.py", "ping")
    out = sh("bridge_send.py", "selftest")
    calib = json.loads((HOME / "bridge" / "calibration.json").read_text())
    assert calib["record_absolute"] is True and calib["end_inclusive"] is True, calib
    assert "smooth (Fusion) zoom:        yes" in out
    assert len(proj.timelines) == 1, "selftest timeline must be deleted"

    sh("bridge_send.py", "prepare", "2026-10-22_demo")
    P = HOME / "projects" / "2026-10-22_demo"
    assert (P / "review.mp4").exists() and (P / "bridge" / "snapshot_before.json").exists()
    words = [{"w": f"كلمة{i}", "s": round(i * 0.5, 2), "e": round(i * 0.5 + 0.4, 2), "p": 0.9} for i in range(56)]
    words[10]["w"] = "بي ال ال"  # glued into one "word"
    words[20]["w"], words[21]["w"], words[22]["w"] = "البي", "ال", "ال"  # split over three words, with "al-"
    (P / "analysis" / "words.json").write_text(json.dumps({"words": words, "raw_words": words}, ensure_ascii=False),
                                              encoding="utf-8")
    sh("transcribe.py", "2026-10-22_demo", "--refix")
    fixed = json.loads((P / "analysis" / "words.json").read_text(encoding="utf-8"))["words"]
    assert fixed[10]["w"] == "PLL", fixed[10]
    assert any(w["w"] == "الـ PLL" and w["s"] == 10.0 and w["e"] == 11.4 for w in fixed), fixed[18:22]
    sh("analyze.py", "2026-10-22_demo")
    sh("sheets.py", "2026-10-22_demo")
    sh("library.py", "add-folder", "broll", m / "broll")
    sh("library.py", "add-folder", "sfx", m / "sfx")
    sh("library.py", "index")
    sh("library.py", "find", "explode")
    lib = json.loads((HOME / "library" / "index" / "library.json").read_text(encoding="utf-8"))
    clip_id = next(iter(lib["clips"]))
    sfx_id = next(iter(lib["sfx"]))
    assert abs(lib["sfx"][sfx_id]["peak_offset"] - 0.3) < 0.08, lib["sfx"][sfx_id]

    sh("plan.py", "init", "2026-10-22_demo")
    pp = P / "plan" / "edit_plan_v1.json"
    plan = json.loads(pp.read_text(encoding="utf-8"))
    plan["summary"] = "Test plan"
    plan["style"] = {"pacing": "medium", "zooms": "mix"}
    plan["items"] = [
        {"id": "C01", "type": "chapter", "at": 0, "params": {"title": "Intro"}, "why": "start"},
        {"id": "Z01", "type": "zoom", "at": 2.0, "dur": 1.5, "params": {"scale": 1.25, "center": [0.5, 0.6]},
         "why": "punchline", "quote": "كلمة4"},
        {"id": "B01", "type": "broll", "at": 6.0, "dur": 2.5, "asset": {"ref": clip_id, "in": 1.0}, "why": "show it"},
        {"id": "S01", "type": "sfx", "at": 6.0, "asset": {"ref": sfx_id}, "params": {"gain_db": -3}, "why": "whoosh in"},
        {"id": "S02", "type": "sfx", "at": 6.1, "asset": {"ref": sfx_id}, "why": "layered"},
        {"id": "P01", "type": "popup", "at": 9.0, "dur": 1.6, "params": {"text": "هاد الـ PLL", "style": "pop",
                                                                         "position": "top"}, "why": "key term"},
        {"id": "C02", "type": "chapter", "at": 10.0, "params": {"title": "Part 2"}, "why": "section"},
        {"id": "F01", "type": "freeze", "at": 12.0, "dur": 1.0, "params": {"scale": 1.3}, "why": "fail moment"},
        {"id": "N01", "type": "note", "at": 15.0, "params": {"text": "audio pop here"}, "why": "check"},
        {"id": "X01", "type": "transition", "at": 18.0, "params": {"kind": "whip", "dur_frames": 10}, "why": "new part"},
        {"id": "Z02", "type": "zoom", "at": 20.0, "dur": 3.0, "params": {"scale": 1.2, "mode": "smooth", "out": True},
         "why": "slow push"},
        {"id": "C03", "type": "chapter", "at": 20.0, "params": {"title": "End"}, "why": "section"},
        {"id": "Z04", "type": "zoom", "at": 4.0, "dur": 0.5, "params": {"scale": 1.2, "mode": "shake"},
         "why": "funny fail hit"},
        {"id": "Z05", "type": "zoom", "at": 14.0, "dur": 1.0, "status": "unsure", "params": {"scale": 1.2},
         "why": "not sure this is funny"},
        {"id": "Z03", "type": "zoom", "at": 25.5, "dur": 1.0, "params": {"scale": 1.3}, "why": "title on top -> manual"},
    ]
    pp.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    sh("plan.py", "validate", "2026-10-22_demo", "--strict")
    sh("plan.py", "sheet", "2026-10-22_demo")
    sh("plan.py", "edl", "2026-10-22_demo")
    sh("plan.py", "srt", "2026-10-22_demo")
    sh("plan.py", "notes", "2026-10-22_demo")
    edl = (P / "out" / "markers.edl").read_text(encoding="utf-8")
    assert "01:00:02:00 01:00:02:01" in edl and "|C:ResolveColorYellow |M:Z01" in edl, edl[:400]

    out = sh("bridge_send.py", "apply", "2026-10-22_demo")
    assert "BY HAND Z03" in out and "BY HAND X01" in out and "BY HAND Z05" in out, out
    assert "Z05" not in {r["id"] for r in json.loads((P / "bridge" / "applied_v1.json").read_text(encoding="utf-8"))["results"] if r["op"] != "marker"}
    rec = json.loads((P / "bridge" / "applied_v1.json").read_text(encoding="utf-8"))
    res = {r["id"]: r for r in rec["results"] if r["op"] != "marker"}
    bad = [r for r in rec["results"] if not r["ok"]]
    assert not bad, bad
    names = [t["name"] for t in tl.tracks["video"]]
    assert {"ED ZOOM", "ED B-ROLL", "ED TEXT"} <= set(names), names
    z1 = next(it for t in tl.tracks["video"] if t["name"] == "ED ZOOM" for it in t["items"] if it.uid == res["Z01"]["result"]["uid"])
    assert z1.start == 216000 + 120 and z1.src_start == 60 + 120 and z1.dur == 90, (z1.start, z1.src_start, z1.dur)
    assert abs(z1.props["ZoomX"] - 1.25) < 1e-6 and abs(z1.props["Tilt"] - 135.0) < 1e-6, z1.props
    z2 = next(it for t in tl.tracks["video"] for it in t["items"] if it.uid == res["Z02"]["result"]["uid"])
    assert z2.src_start == 120 and z2.comps, "smooth zoom = Fusion comp on the copy of clip 2"
    sizes = z2.comps[0].tools["Transform2"].keys["Size"]
    assert sizes[0] == 1.0 and max(sizes.values()) == 1.2, sizes
    shake = [r for i, r in res.items() if i == "Z04" or i.startswith("Z04~")]
    assert len(shake) == 15, len(shake)
    pans = [next(it for t in tl.tracks["video"] for it in t["items"] if it.uid == r["result"]["uid"]).props["Pan"]
            for r in shake]
    assert pans[0] * pans[1] < 0 and abs(pans[-1]) < abs(pans[0]) + 1, pans  # alternates, calms down
    b1 = next(it for t in tl.tracks["video"] for it in t["items"] if it.uid == res["B01"]["result"]["uid"])
    assert b1.src_start == 30 and b1.dur == 75 and abs(b1.props["ZoomX"] - 1.0) < 1e-6, (b1.src_start, b1.dur, b1.props)
    s1 = next(it for t in tl.tracks["audio"] for it in t["items"] if it.uid == res["S01"]["result"]["uid"])
    assert abs(s1.start - (216000 + 360 - 18)) <= 4, s1.start  # loud part (0.25-0.35 s) lands on 6.0 s
    s2_track = res["S02"]["result"]["track"]
    assert s2_track == "ED SFX 2", s2_track
    assert 120 in tl.markers and tl.markers[120]["color"] == "Yellow"
    z3_marker = next(v for v in tl.markers.values() if v["customData"] == "editor:v1:Z03")
    assert z3_marker["color"] == "Red" and "DO BY HAND" in z3_marker["note"]
    assert any("before editor" in t.name for t in proj.timelines), "backup timeline"

    # he edits: deletes a sound, nudges the B-roll, tones down a zoom, adds his own sound
    tl.DeleteClips([s1])
    b1.start += 6
    z1.props["ZoomX"] = 1.15
    sfx_track = next(i for i, t in enumerate(tl.tracks["audio"], 1) if t["name"] == "ED SFX 1")
    own = mr.MediaPoolItem(str(m / "sfx" / "whoosh fast.wav"))
    tl._append({"mediaPoolItem": own, "startFrame": 0, "endFrame": 40, "trackIndex": sfx_track,
                "recordFrame": 216000 + 900, "mediaType": 2})
    sh("bridge_send.py", "snapshot", "2026-10-22_demo", "--label", "after")
    out = sh("learn.py", "2026-10-22_demo")
    learn = json.loads((P / "bridge" / "learn_v1.json").read_text(encoding="utf-8"))
    fates = {r["id"]: r["fate"] for r in learn["rows"]}
    assert fates["S01"] == "deleted" and fates["B01"] == "moved" and "rezoomed" in fates["Z01"], fates
    assert len(learn["added_by_him"]) == 1, learn["added_by_him"]

    sh("plan.py", "bump", "2026-10-22_demo", "--note", "fewer sounds")
    sh("bridge_send.py", "apply", "2026-10-22_demo", ok=False)  # must refuse without --replace
    sh("bridge_send.py", "apply", "2026-10-22_demo", "--replace")
    assert sum(1 for t in proj.timelines if "before editor" in t.name) == 1, "only one backup"
    sh("bridge_send.py", "remove", "2026-10-22_demo")
    left = [t["name"] for t in tl.tracks["video"] + tl.tracks["audio"] if t["name"].startswith("ED ")]
    assert left == ["ED SFX 1"], left  # his own sound keeps that track alive
    assert not [v for v in tl.markers.values() if v["customData"].startswith("editor:")], "markers removed"
    assert len(tl.tracks["video"][0]["items"]) == 2, "his cut untouched"
    sh("retention.py", "2026-10-22_demo", "--dips", "0:06,0:20")
    sh("bridge_send.py", "stop")
    print(f"ALL CHECKS PASSED  (files in {TMP})")


if __name__ == "__main__":
    main()
