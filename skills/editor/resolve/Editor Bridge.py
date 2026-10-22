"""Editor Bridge: lets the /editor skill place edits in DaVinci Resolve.

Install: copy this file to
  %APPDATA%\\Blackmagic Design\\DaVinci Resolve\\Support\\Fusion\\Scripts\\Utility\\
then restart Resolve and run Workspace > Scripts > Editor Bridge.

How it works: the skill writes small JSON "jobs" into a mailbox folder on your
PC. This script (running inside Resolve) picks each job up, does it, and writes
the answer back. It only knows a fixed list of actions (read the timeline,
render a review copy, place clips/markers, remove what it placed, self-test).
It never runs code sent to it and never touches the internet.

Works on DaVinci Resolve 21.0.x Free and Studio (Python scripting from the
Scripts menu). Resolve 21.1+ Free removed Python scripting: there the skill
falls back to marker files.
"""
import json
import os
import re
import sys
import time
import traceback

BRIDGE_VERSION = "1.0.0"
POLL_S = 0.5
HEARTBEAT_S = 2.0
IDLE_LIMIT_S = 6 * 3600
EDITOR_TAG = "editor"  # customData prefix on markers the bridge creates
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp")


# ------------------------------------------------------------------ setup


def editor_home():
    env = os.environ.get("EDITOR_HOME")
    if env:
        return os.path.expanduser(env)
    return os.path.join(os.path.expanduser("~"), "SyrianRubikStudio", "editor")


BRIDGE_DIR = os.path.join(editor_home(), "bridge")
INBOX = os.path.join(BRIDGE_DIR, "inbox")
OUTBOX = os.path.join(BRIDGE_DIR, "outbox")
STATUS = os.path.join(BRIDGE_DIR, "status.json")
CALIB = os.path.join(BRIDGE_DIR, "calibration.json")
LOG = os.path.join(BRIDGE_DIR, "bridge.log")
STOP_FILE = os.path.join(BRIDGE_DIR, "STOP")


def get_resolve():
    g = globals()
    if g.get("resolve"):
        return g["resolve"]
    try:
        return bmd.scriptapp("Resolve")  # noqa: F821 (provided by Resolve)
    except Exception:
        pass
    try:
        return app.GetResolve()  # noqa: F821
    except Exception:
        pass
    try:
        import DaVinciResolveScript as dvr  # external Python (Studio)

        return dvr.scriptapp("Resolve")
    except Exception:
        return None


def log(msg):
    line = "%s  %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    try:
        if os.path.exists(LOG) and os.path.getsize(LOG) > 1024 * 1024:
            os.replace(LOG, LOG + ".1")
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
    try:
        print("[Editor Bridge] " + msg)
    except Exception:
        pass


def write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(jsonable(data), f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def read_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def jsonable(x):
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    return str(x)


def to_float(v, default=0.0):
    """'59.94', '29.97 DF', '60' -> float (first number in the text)."""
    m = re.search(r"-?\d+(?:\.\d+)?", str(v if v is not None else ""))
    return float(m.group(0)) if m else default


# ------------------------------------------------------------------ context


class Ctx(object):
    """Everything an action needs: Resolve objects + frame math."""

    def __init__(self, resolve, beat):
        self.resolve = resolve
        self.beat = beat
        self.pm = resolve.GetProjectManager()
        self.project = self.pm.GetCurrentProject()
        if not self.project:
            raise RuntimeError("No project is open in Resolve.")
        self.timeline = self.project.GetCurrentTimeline()
        self.media_pool = self.project.GetMediaPool()
        self.calib = read_json(CALIB, {}) or {}
        self._media_cache = {}
        self._bin = None

    def need_timeline(self):
        if not self.timeline:
            raise RuntimeError("No timeline is open. Open your video's timeline first.")
        return self.timeline

    # -- timeline facts
    def fps(self, tl=None):
        tl = tl or self.need_timeline()
        v = tl.GetSetting("timelineFrameRate") or self.project.GetSetting("timelineFrameRate")
        return to_float(v, 0.0) or 30.0

    def start_frame(self, tl=None):
        return int((tl or self.need_timeline()).GetStartFrame())

    def sec_to_record(self, sec, tl=None):
        """Seconds from timeline start -> recordFrame for AppendToTimeline."""
        f = int(round(float(sec) * self.fps(tl)))
        if self.calib.get("record_absolute", True):
            return self.start_frame(tl) + f
        return f

    def sec_to_marker(self, sec, tl=None):
        """Timeline markers use frames relative to the timeline start."""
        return int(round(float(sec) * self.fps(tl)))

    def resolution(self, tl=None):
        tl = tl or self.need_timeline()
        w = to_float(tl.GetSetting("timelineResolutionWidth") or self.project.GetSetting("timelineResolutionWidth"), 1920)
        h = to_float(tl.GetSetting("timelineResolutionHeight") or self.project.GetSetting("timelineResolutionHeight"), 1080)
        return int(w), int(h)

    # -- tracks
    def find_track(self, ttype, name, tl=None):
        tl = tl or self.need_timeline()
        for i in range(1, int(tl.GetTrackCount(ttype)) + 1):
            if (tl.GetTrackName(ttype, i) or "") == name:
                return i
        return 0

    def ensure_track(self, ttype, name, tl=None):
        tl = tl or self.need_timeline()
        idx = self.find_track(ttype, name, tl)
        if idx:
            return idx
        ok = tl.AddTrack(ttype, "stereo") if ttype == "audio" else tl.AddTrack(ttype)
        if not ok:
            raise RuntimeError("Could not add a %s track." % ttype)
        idx = int(tl.GetTrackCount(ttype))
        tl.SetTrackName(ttype, idx, name)
        return idx

    # -- media
    def editor_bin(self):
        if self._bin:
            return self._bin
        root = self.media_pool.GetRootFolder()
        for f in root.GetSubFolderList() or []:
            if f.GetName() == "EDITOR":
                self._bin = f
                return f
        self._bin = self.media_pool.AddSubFolder(root, "EDITOR") or root
        return self._bin

    def import_media(self, path):
        key = os.path.normcase(os.path.abspath(path))
        if key in self._media_cache:
            return self._media_cache[key]
        if not os.path.exists(path):
            raise RuntimeError("File not found: %s" % path)
        b = self.editor_bin()
        for clip in b.GetClipList() or []:
            fp = clip.GetClipProperty("File Path") or ""
            if fp and os.path.normcase(os.path.abspath(fp)) == key:
                self._media_cache[key] = clip
                return clip
        prev = self.media_pool.GetCurrentFolder()
        self.media_pool.SetCurrentFolder(b)
        try:
            items = self.media_pool.ImportMedia([path])
        finally:
            if prev:
                self.media_pool.SetCurrentFolder(prev)
        if not items:
            raise RuntimeError("Resolve could not import: %s" % path)
        self._media_cache[key] = items[0]
        return items[0]

    def clip_fps(self, mpi, fallback):
        return to_float(mpi.GetClipProperty("FPS"), 0.0) or fallback

    def all_items(self, tl=None):
        tl = tl or self.need_timeline()
        for ttype in ("video", "audio"):
            for i in range(1, int(tl.GetTrackCount(ttype)) + 1):
                for it in tl.GetItemListInTrack(ttype, i) or []:
                    yield ttype, i, it

    def item_by_uid(self, uid, tl=None):
        for ttype, i, it in self.all_items(tl):
            if it.GetUniqueId() == uid:
                return ttype, i, it
        return None, 0, None

    def append(self, info):
        items = self.media_pool.AppendToTimeline([info])
        if not items:
            raise RuntimeError("Resolve refused to place the clip (AppendToTimeline returned nothing).")
        return items[0]

    def end_frame(self, start, length):
        """endFrame for AppendToTimeline; inclusive unless the self-test says otherwise."""
        if self.calib.get("end_inclusive", True):
            return start + max(1, length) - 1
        return start + max(1, length)


TRANSFORM_KEYS = ("ZoomX", "ZoomY", "Pan", "Tilt", "RotationAngle", "AnchorPointX", "AnchorPointY",
                  "FlipX", "FlipY", "CropLeft", "CropRight", "CropTop", "CropBottom", "Opacity")


def item_info(ctx, ttype, it, with_props=True):
    d = {
        "uid": it.GetUniqueId(),
        "name": it.GetName(),
        "start": it.GetStart(),
        "end": it.GetEnd(),
        "duration": it.GetDuration(),
    }
    for key, fn in (("src_start", "GetSourceStartFrame"), ("src_end", "GetSourceEndFrame"),
                    ("left_offset", "GetLeftOffset"), ("color", "GetClipColor"),
                    ("enabled", "GetClipEnabled"), ("fusion_comps", "GetFusionCompCount")):
        try:
            d[key] = getattr(it, fn)()
        except Exception:
            pass
    try:
        mpi = it.GetMediaPoolItem()
    except Exception:
        mpi = None
    if mpi:
        d["media"] = {
            "name": mpi.GetName(),
            "path": mpi.GetClipProperty("File Path"),
            "fps": mpi.GetClipProperty("FPS"),
            "resolution": mpi.GetClipProperty("Resolution"),
            "type": mpi.GetClipProperty("Type"),
            "uid": mpi.GetUniqueId(),
        }
    if with_props and ttype == "video":
        props = {}
        for k in TRANSFORM_KEYS:
            try:
                props[k] = it.GetProperty(k)
            except Exception:
                pass
        d["props"] = props
    try:
        d["markers"] = it.GetMarkers() or {}
    except Exception:
        pass
    return d


def timeline_summary(ctx, tl):
    w, h = ctx.resolution(tl)
    return {
        "name": tl.GetName(),
        "uid": tl.GetUniqueId(),
        "fps": ctx.fps(tl),
        "drop_frame": str(tl.GetSetting("timelineDropFrameTimecode") or "0") in ("1", "True", "true"),
        "start_frame": tl.GetStartFrame(),
        "end_frame": tl.GetEndFrame(),
        "start_tc": tl.GetStartTimecode(),
        "width": w,
        "height": h,
        "tracks": {t: int(tl.GetTrackCount(t)) for t in ("video", "audio", "subtitle")},
    }


# ------------------------------------------------------------------ actions


def act_ping(ctx, args):
    out = {
        "bridge_version": BRIDGE_VERSION,
        "product": ctx.resolve.GetProductName(),
        "version": ctx.resolve.GetVersionString(),
        "project": ctx.project.GetName(),
        "page": ctx.resolve.GetCurrentPage(),
        "python": sys.version.split()[0],
        "calibration": ctx.calib,
    }
    if ctx.timeline:
        out["timeline"] = timeline_summary(ctx, ctx.timeline)
    return out


def act_read_timeline(ctx, args):
    tl = ctx.need_timeline()
    snap = {"bridge_version": BRIDGE_VERSION, "taken": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "project": ctx.project.GetName(), "timeline": timeline_summary(ctx, tl), "tracks": {}}
    for ttype in ("video", "audio", "subtitle"):
        tracks = []
        for i in range(1, int(tl.GetTrackCount(ttype)) + 1):
            ctx.beat()
            t = {"index": i, "name": tl.GetTrackName(ttype, i)}
            try:
                t["enabled"] = tl.GetIsTrackEnabled(ttype, i)
                t["locked"] = tl.GetIsTrackLocked(ttype, i)
            except Exception:
                pass
            if ttype != "subtitle":
                t["items"] = [item_info(ctx, ttype, it) for it in (tl.GetItemListInTrack(ttype, i) or [])]
            else:
                t["items"] = [{"name": it.GetName(), "start": it.GetStart(), "end": it.GetEnd()}
                              for it in (tl.GetItemListInTrack(ttype, i) or [])]
            tracks.append(t)
        snap["tracks"][ttype] = tracks
    snap["markers"] = tl.GetMarkers() or {}
    return snap


def _pick_render(project, want_ext, codec_words):
    formats = project.GetRenderFormats() or {}
    fmt_args = []
    for name, ext in formats.items():
        if str(ext).lower() == want_ext or str(name).lower() == want_ext:
            fmt_args += [ext, name]
    for fmt in fmt_args:
        codecs = project.GetRenderCodecs(fmt) or {}
        ranked = []
        for desc, cname in codecs.items():
            text = ("%s %s" % (desc, cname)).lower()
            if any(w in text for w in codec_words):
                hw = any(w in text for w in ("nvidia", "amd", "intel", "quick sync", "nvenc"))
                ranked.append((1 if hw else 0, desc, cname))
        ranked.sort()
        for _, desc, cname in ranked:
            if project.SetCurrentRenderFormatAndCodec(fmt, cname):
                return fmt, cname
    return None, None


def act_render_review(ctx, args):
    """Render the whole timeline to a small H.264 MP4 the skill can analyze."""
    tl = ctx.need_timeline()
    target_dir = args["target_dir"]
    name = args.get("name", "review")
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    p = ctx.project
    p.SetCurrentRenderMode(1)
    fmt, codec = _pick_render(p, "mp4", ("h.264", "h264", "264"))
    if not fmt:
        fmt, codec = _pick_render(p, "mov", ("h.264", "h264", "264"))
    if not fmt:
        raise RuntimeError("No H.264 render option found. Use File > Quick Export > H.264 instead.")
    w, h = ctx.resolution(tl)
    long_side = int(args.get("long_side", 1280))
    scale = min(1.0, float(long_side) / max(w, h))
    rw, rh = int(w * scale) // 2 * 2, int(h * scale) // 2 * 2
    settings = {"SelectAllFrames": True, "TargetDir": target_dir, "CustomName": name,
                "ExportVideo": True, "ExportAudio": True, "FormatWidth": rw, "FormatHeight": rh}
    if not p.SetRenderSettings(settings):
        settings.pop("FormatWidth")
        settings.pop("FormatHeight")
        p.SetRenderSettings(settings)
    job = p.AddRenderJob()
    if not job:
        raise RuntimeError("Could not add a render job.")
    try:
        p.StartRendering([job], isInteractiveMode=False)
    except TypeError:
        p.StartRendering(job)
    t0 = time.time()
    while p.IsRenderingInProgress():
        ctx.beat()
        time.sleep(1.0)
        if time.time() - t0 > float(args.get("timeout_s", 3600)):
            p.StopRendering()
            raise RuntimeError("Render took too long and was stopped.")
    status = p.GetRenderJobStatus(job) or {}
    try:
        p.DeleteRenderJob(job)
    except Exception:
        pass
    out_path = None
    for fn in os.listdir(target_dir):
        if fn.startswith(name) and fn.lower().endswith((".mp4", ".mov")):
            cand = os.path.join(target_dir, fn)
            if out_path is None or os.path.getmtime(cand) > os.path.getmtime(out_path):
                out_path = cand
    if not out_path:
        raise RuntimeError("Render finished but no file was found (status: %s)." % status)
    return {"path": out_path, "format": fmt, "codec": codec, "size": [rw, rh], "status": status}


def op_backup(ctx, op):
    tl = ctx.need_timeline()
    name = "%s (before editor %s)" % (tl.GetName(), op.get("label", time.strftime("%m-%d %H%M")))
    dup = tl.DuplicateTimeline(name)
    ctx.project.SetCurrentTimeline(tl)
    if not dup:
        raise RuntimeError("Could not make a backup copy of the timeline.")
    return {"backup": dup.GetName()}


def op_place(ctx, op):
    """Place a file (B-roll, SFX, text card, freeze frame) at a time on a named track."""
    tl = ctx.need_timeline()
    ttype = op.get("ttype", "video")
    idx = ctx.ensure_track(ttype, op["track"], tl)
    mpi = ctx.import_media(op["path"])
    tl_fps = ctx.fps(tl)
    rec = ctx.sec_to_record(op["at"], tl)
    is_still = op.get("still") or op["path"].lower().endswith(IMAGE_EXT)
    if is_still:
        src_start = 0
        length = max(1, int(round(float(op["dur"]) * tl_fps)))
    else:
        cfps = ctx.clip_fps(mpi, tl_fps)
        src_start = int(round(float(op.get("src_in", 0.0)) * cfps))
        length = max(1, int(round(float(op["dur"]) * cfps)))
    info = {"mediaPoolItem": mpi, "startFrame": src_start, "endFrame": ctx.end_frame(src_start, length),
            "trackIndex": idx, "recordFrame": rec, "mediaType": 2 if ttype == "audio" else 1}
    item = ctx.append(info)
    for k, v in (op.get("props") or {}).items():
        item.SetProperty(k, v)
    if op.get("color"):
        item.SetClipColor(op["color"])
    return {"uid": item.GetUniqueId(), "track": op["track"], "ttype": ttype,
            "start": item.GetStart(), "end": item.GetEnd(), "wanted_start": rec}


def _add_fusion_zoom(item, fz):
    """Keyframed push-in inside the item's own Fusion comp. Returns True on success."""
    comp = item.GetFusionCompByIndex(1) if item.GetFusionCompCount() else item.AddFusionComp()
    if not comp:
        return False
    mi = comp.FindTool("MediaIn1")
    mo = comp.FindTool("MediaOut1")
    if not mi or not mo:
        return False
    attrs = comp.GetAttrs() or {}
    f0 = int(attrs.get("COMPN_RenderStart", 0))
    f1 = int(attrs.get("COMPN_RenderEnd", f0 + 1))
    ease = max(1, int(fz.get("ease_frames", 12)))
    comp.Lock()
    try:
        xf = comp.AddTool("Transform", -32768, -32768)
        xf.SetAttrs({"TOOLS_Name": "EditorZoom"})
        xf.ConnectInput("Input", mi)
        mo.ConnectInput("Input", xf)
        cx, cy = float(fz.get("cx", 0.5)), 1.0 - float(fz.get("cy", 0.5))  # Fusion y goes up
        xf.SetInput("Pivot", {1: cx, 2: cy, 3: 0})
        xf.SetInput("Center", {1: cx, 2: cy, 3: 0})
        xf.AddModifier("Size", "BezierSpline")
        s = float(fz["scale"])
        xf.SetInput("Size", 1.0, f0)
        xf.SetInput("Size", s, min(f1, f0 + ease))
        if fz.get("out") and f1 - ease > f0 + ease:
            xf.SetInput("Size", s, f1 - ease)
            xf.SetInput("Size", 1.0, f1)
    finally:
        comp.Unlock()
    return True


def op_place_segment(ctx, op):
    """Copy a piece of the base clip onto a higher track (zoom layer / punch-in)."""
    tl = ctx.need_timeline()
    _, _, base = ctx.item_by_uid(op["base_uid"], tl)
    if base is None:
        raise RuntimeError("The clip under this spot changed since the timeline was read. Re-read and retry.")
    if int(base.GetStart()) != int(op["base_start"]):
        raise RuntimeError("The clip under this spot moved since the timeline was read. Re-read and retry.")
    mpi = base.GetMediaPoolItem()
    idx = ctx.ensure_track("video", op["track"], tl)
    rec = ctx.sec_to_record(op["at"], tl)
    info = {"mediaPoolItem": mpi, "startFrame": int(op["src_start"]),
            "endFrame": ctx.end_frame(int(op["src_start"]), int(op["src_len"])),
            "trackIndex": idx, "recordFrame": rec, "mediaType": 1}
    item = ctx.append(info)
    for k, v in (op.get("props") or {}).items():
        item.SetProperty(k, v)
    fusion_ok = None
    if op.get("fusion_zoom"):
        try:
            fusion_ok = _add_fusion_zoom(item, op["fusion_zoom"])
        except Exception as e:
            fusion_ok = False
            log("fusion zoom failed: %s" % e)
        if not fusion_ok and op.get("fallback_props"):
            for k, v in op["fallback_props"].items():
                item.SetProperty(k, v)
    if op.get("color"):
        item.SetClipColor(op["color"])
    return {"uid": item.GetUniqueId(), "track": op["track"], "ttype": "video",
            "start": item.GetStart(), "end": item.GetEnd(), "wanted_start": rec, "fusion": fusion_ok}


def op_marker(ctx, op):
    tl = ctx.need_timeline()
    frame = ctx.sec_to_marker(op["at"], tl)
    existing = tl.GetMarkers() or {}
    taken = set(int(float(k)) for k in existing.keys())
    while frame in taken:  # only one marker per frame
        frame += 1
    custom = op.get("custom") or ("%s:%s" % (EDITOR_TAG, op.get("id", "")))
    ok = tl.AddMarker(frame, op.get("color", "Blue"), op.get("name", ""), op.get("note", ""),
                      max(1, int(op.get("dur_frames", 1))), custom)
    if not ok:
        raise RuntimeError("Resolve refused the marker at frame %d." % frame)
    return {"frame": frame, "custom": custom}


OPS = {"backup": op_backup, "place": op_place, "place_segment": op_place_segment, "marker": op_marker}


def act_apply(ctx, args):
    """Run a list of prepared operations. Each one reports success or its error."""
    results = []
    for op in args.get("ops", []):
        ctx.beat()
        kind = op.get("op")
        entry = {"id": op.get("id"), "op": kind}
        try:
            fn = OPS.get(kind)
            if not fn:
                raise RuntimeError("Unknown operation: %s" % kind)
            entry["result"] = fn(ctx, op)
            entry["ok"] = True
        except Exception as e:
            entry["ok"] = False
            entry["error"] = str(e)
            log("op %s %s failed: %s" % (kind, op.get("id"), e))
        results.append(entry)
    return {"results": results, "timeline": ctx.need_timeline().GetName()}


def act_remove(ctx, args):
    """Delete only things the bridge placed (by unique id) and its own markers."""
    tl = ctx.need_timeline()
    uids = set(args.get("uids", []))
    found = [it for _, _, it in ctx.all_items(tl) if it.GetUniqueId() in uids]
    deleted = bool(tl.DeleteClips(found, False)) if found else True
    prefix = args.get("marker_prefix", EDITOR_TAG + ":")
    removed_markers = 0
    for frame, info in list((tl.GetMarkers() or {}).items()):
        if str(info.get("customData", "")).startswith(prefix):
            if tl.DeleteMarkerAtFrame(int(float(frame))):
                removed_markers += 1
    removed_tracks = []
    for ttype in ("video", "audio"):
        for i in range(int(tl.GetTrackCount(ttype)), 0, -1):
            name = tl.GetTrackName(ttype, i) or ""
            if name in args.get("track_names", []) and not (tl.GetItemListInTrack(ttype, i) or []):
                if tl.DeleteTrack(ttype, i):
                    removed_tracks.append(name)
    return {"clips_found": len(found), "clips_deleted": deleted, "markers_removed": removed_markers,
            "tracks_removed": removed_tracks}


def act_selftest(ctx, args):
    """Measure how this Resolve build behaves, on a throwaway timeline."""
    report = {"checks": {}}
    chk = report["checks"]
    original = ctx.timeline
    mp = ctx.media_pool
    test = mp.CreateEmptyTimeline("EDITOR SELFTEST %s" % time.strftime("%H%M%S"))
    if not test:
        raise RuntimeError("Could not create a test timeline.")
    ctx.project.SetCurrentTimeline(test)
    ctx.timeline = test
    try:
        tl = test
        start = int(tl.GetStartFrame())
        fps = ctx.fps(tl)
        report["test_timeline"] = {"start_frame": start, "fps": fps}
        vid = ctx.import_media(args["video"])
        # 1) recordFrame convention + endFrame inclusivity
        tl.AddTrack("video")
        v2 = int(tl.GetTrackCount("video"))
        item = ctx.append({"mediaPoolItem": vid, "startFrame": 0, "endFrame": 59, "trackIndex": v2,
                           "recordFrame": start + 60, "mediaType": 1})
        got = int(item.GetStart())
        dur = int(item.GetDuration())
        if got == start + 60:
            chk["record_absolute"] = True
        elif got in (60, start + start + 60):
            chk["record_absolute"] = False
        else:
            chk["record_absolute"] = None
        chk["record_got"] = got
        chk["end_inclusive"] = True if dur == 60 else (False if dur == 59 else None)
        chk["end_duration"] = dur
        # 2) transform properties
        item.SetProperty("ZoomX", 1.3)
        item.SetProperty("ZoomY", 1.3)
        item.SetProperty("Pan", 100.0)
        chk["zoom_props"] = abs(to_float(item.GetProperty("ZoomX")) - 1.3) < 0.01
        chk["pan_props"] = abs(to_float(item.GetProperty("Pan")) - 100.0) < 0.5
        # 3) Fusion keyframed zoom
        try:
            chk["fusion_zoom"] = bool(_add_fusion_zoom(item, {"scale": 1.2, "cx": 0.5, "cy": 0.5, "ease_frames": 10}))
        except Exception as e:
            chk["fusion_zoom"] = False
            chk["fusion_error"] = str(e)
        # 4) still image length
        if args.get("image"):
            img = ctx.import_media(args["image"])
            tl.AddTrack("video")
            v3 = int(tl.GetTrackCount("video"))
            st = ctx.append({"mediaPoolItem": img, "startFrame": 0, "endFrame": 89, "trackIndex": v3,
                             "recordFrame": start + 30, "mediaType": 1})
            chk["still_duration"] = int(st.GetDuration())
            chk["still_ok"] = int(st.GetDuration()) in (89, 90)
        # 5) audio on a new audio track
        if args.get("audio"):
            aud = ctx.import_media(args["audio"])
            tl.AddTrack("audio", "stereo")
            a2 = int(tl.GetTrackCount("audio"))
            ai = ctx.append({"mediaPoolItem": aud, "startFrame": 0, "endFrame": 29, "trackIndex": a2,
                             "recordFrame": start + 120, "mediaType": 2})
            chk["audio_ok"] = int(ai.GetStart()) in (start + 120, 120)
        # 6) markers
        chk["marker_ok"] = bool(tl.AddMarker(30, "Blue", "SELFTEST", "test note", 1, "editor:selftest"))
        keys = [int(float(k)) for k in (tl.GetMarkers() or {}).keys()]
        chk["marker_keys"] = keys
        chk["marker_custom"] = bool(tl.GetMarkerByCustomData("editor:selftest"))
        # 7) unique ids + delete
        uid = item.GetUniqueId()
        chk["unique_id"] = bool(uid)
        chk["delete_ok"] = bool(tl.DeleteClips([item], False))
        # 8) still export of the current frame (for freeze frames)
        if args.get("still_out"):
            try:
                tl.SetCurrentTimecode(tl.GetStartTimecode())
                chk["export_still"] = bool(ctx.project.ExportCurrentFrameAsStill(args["still_out"]))
            except Exception as e:
                chk["export_still"] = False
                chk["export_still_error"] = str(e)
    finally:
        ctx.project.SetCurrentTimeline(original) if original else None
        ctx.timeline = original
        try:
            mp.DeleteTimelines([test])
        except Exception:
            pass
    calib = {"record_absolute": chk.get("record_absolute") is not False,
             "end_inclusive": chk.get("end_inclusive") is not False,
             "fusion_zoom": bool(chk.get("fusion_zoom")),
             "still_ok": bool(chk.get("still_ok", True)),
             "export_still": bool(chk.get("export_still")),
             "measured": time.strftime("%Y-%m-%d %H:%M"),
             "resolve_version": ctx.resolve.GetVersionString()}
    write_json(CALIB, calib)
    ctx.calib = calib
    report["calibration"] = calib
    return report


ACTIONS = {
    "ping": act_ping,
    "read_timeline": act_read_timeline,
    "render_review": act_render_review,
    "apply": act_apply,
    "remove": act_remove,
    "selftest": act_selftest,
}


# ------------------------------------------------------------------ main loop


class Bridge(object):
    def __init__(self, resolve):
        self.resolve = resolve
        self.started = time.time()
        self.last_job = time.time()
        self.last_beat = 0.0
        self.state = "idle"
        self.current = None

    def beat(self, force=False):
        now = time.time()
        if not force and now - self.last_beat < HEARTBEAT_S:
            return
        self.last_beat = now
        write_json(STATUS, {"pid": os.getpid(), "bridge_version": BRIDGE_VERSION, "state": self.state,
                            "job": self.current, "heartbeat": now, "started": self.started})

    def another_running(self):
        st = read_json(STATUS, {}) or {}
        return (st.get("pid") != os.getpid() and st.get("state") != "stopped"
                and time.time() - float(st.get("heartbeat", 0)) < 3 * HEARTBEAT_S)

    def handle(self, path):
        job = read_json(path)
        try:
            os.remove(path)
        except Exception:
            pass
        if not isinstance(job, dict) or "id" not in job:
            return
        jid = str(job["id"])
        action = job.get("action")
        result = {"id": jid, "action": action, "bridge_version": BRIDGE_VERSION, "ok": False}
        if job.get("expires") and time.time() > float(job["expires"]):
            result["error"] = "Job expired before the bridge saw it."
        elif action == "stop":
            result["ok"] = True
            result["result"] = {"stopped": True}
            write_json(os.path.join(OUTBOX, jid + ".json"), result)
            raise SystemExit
        elif action not in ACTIONS:
            result["error"] = "Unknown action: %s" % action
        else:
            self.state, self.current = "busy", jid
            self.beat(force=True)
            log("job %s: %s" % (jid, action))
            try:
                ctx = Ctx(self.resolve, self.beat)
                result["result"] = ACTIONS[action](ctx, job.get("args") or {})
                result["ok"] = True
            except Exception as e:
                result["error"] = str(e)
                result["trace"] = traceback.format_exc()[-3000:]
                log("job %s failed: %s" % (jid, e))
            self.state, self.current = "idle", None
        result["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        write_json(os.path.join(OUTBOX, jid + ".json"), result)
        self.last_job = time.time()

    def run(self):
        for d in (BRIDGE_DIR, INBOX, OUTBOX):
            if not os.path.isdir(d):
                os.makedirs(d)
        if self.another_running():
            log("Another Editor Bridge is already running. This one will close.")
            return
        if os.path.exists(STOP_FILE):
            os.remove(STOP_FILE)
        log("EDITOR BRIDGE READY (v%s). Leave Resolve open; the skill talks to it now." % BRIDGE_VERSION)
        self.beat(force=True)
        try:
            while True:
                if os.path.exists(STOP_FILE):
                    os.remove(STOP_FILE)
                    break
                jobs = sorted(f for f in os.listdir(INBOX) if f.endswith(".json"))
                for fn in jobs:
                    self.handle(os.path.join(INBOX, fn))
                if time.time() - self.last_job > IDLE_LIMIT_S:
                    log("No jobs for a long time; stopping. Run Editor Bridge again when needed.")
                    break
                self.beat()
                time.sleep(POLL_S)
        except SystemExit:
            pass
        finally:
            self.state = "stopped"
            self.beat(force=True)
            log("Editor Bridge stopped.")


def main():
    resolve = get_resolve()
    if resolve is None:
        log("Could not reach Resolve. Run this from Workspace > Scripts inside DaVinci Resolve.")
        return
    Bridge(resolve).run()


if os.environ.get("EDITOR_BRIDGE_TEST") != "1":
    main()
