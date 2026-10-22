"""A small fake of DaVinci Resolve's scripting API (21.0.x behavior as documented).

Enough to run the Editor Bridge end to end without Resolve: tracks, items,
markers, media pool, render, Fusion comps. Conventions follow the README:
AppendToTimeline recordFrame is absolute, endFrame is inclusive, timeline
markers are relative to the timeline start.
"""
import json
import shutil
import subprocess
import uuid


def probe(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", path],
                             capture_output=True, text=True).stdout
        for st in json.loads(out).get("streams", []):
            if st.get("codec_type") == "video":
                n, d = st["r_frame_rate"].split("/")
                return {"fps": round(int(n) / int(d), 3), "w": st["width"], "h": st["height"], "type": "Video + Audio"}
        return {"fps": 0, "w": 0, "h": 0, "type": "Audio"}
    except Exception:
        return {"fps": 0, "w": 0, "h": 0, "type": "Unknown"}


class MediaPoolItem:
    def __init__(self, path):
        self.path = path
        self.uid = uuid.uuid4().hex
        info = probe(path)
        is_img = path.lower().endswith((".png", ".jpg", ".jpeg"))
        self.props = {"File Path": path, "FPS": "" if is_img else str(info["fps"] or ""),
                      "Resolution": f"{info['w']}x{info['h']}", "Type": "Still" if is_img else info["type"]}

    def GetName(self):
        return self.path.replace("\\", "/").split("/")[-1]

    def GetClipProperty(self, key=None):
        return self.props if key is None else self.props.get(key, "")

    def GetUniqueId(self):
        return self.uid


class Tool:
    def __init__(self, name):
        self.name = name
        self.inputs = {}
        self.keys = {}
        self.attrs = {}

    def SetAttrs(self, a):
        self.attrs.update(a)

    def ConnectInput(self, name, other):
        self.inputs[name] = other

    def AddModifier(self, name, kind):
        self.keys[name] = {}
        return True

    def SetInput(self, name, value, time=None):
        if time is not None and name in self.keys:
            self.keys[name][time] = value
        else:
            self.inputs[name] = value


class Comp:
    def __init__(self, length):
        self.tools = {"MediaIn1": Tool("MediaIn1"), "MediaOut1": Tool("MediaOut1")}
        self.length = length

    def FindTool(self, name):
        return self.tools.get(name)

    def AddTool(self, kind, x=0, y=0):
        t = Tool(kind)
        self.tools[f"{kind}{len(self.tools)}"] = t
        return t

    def GetAttrs(self):
        return {"COMPN_RenderStart": 0, "COMPN_RenderEnd": self.length - 1}

    def Lock(self):
        pass

    def Unlock(self):
        pass


class TimelineItem:
    def __init__(self, mpi, start, dur, src_start, track_type):
        self.mpi, self.start, self.dur, self.src_start = mpi, start, dur, src_start
        self.track_type = track_type
        self.uid = uuid.uuid4().hex
        self.props = {"ZoomX": 1.0, "ZoomY": 1.0, "Pan": 0.0, "Tilt": 0.0, "Opacity": 100.0}
        self.color = ""
        self.comps = []
        self.markers = {}
        self.enabled = True

    def GetName(self):
        return self.mpi.GetName()

    def GetUniqueId(self):
        return self.uid

    def GetStart(self, sub=False):
        return self.start

    def GetEnd(self, sub=False):
        return self.start + self.dur

    def GetDuration(self, sub=False):
        return self.dur

    def GetSourceStartFrame(self):
        return self.src_start

    def GetSourceEndFrame(self):
        return self.src_start + self.dur

    def GetLeftOffset(self, sub=False):
        return self.src_start

    def GetMediaPoolItem(self):
        return self.mpi

    def SetProperty(self, k, v):
        self.props[k] = v
        return True

    def GetProperty(self, k=None):
        return dict(self.props) if k is None else self.props.get(k)

    def SetClipColor(self, c):
        self.color = c
        return True

    def GetClipColor(self):
        return self.color

    def GetClipEnabled(self):
        return self.enabled

    def GetFusionCompCount(self):
        return len(self.comps)

    def AddFusionComp(self):
        c = Comp(self.dur)
        self.comps.append(c)
        return c

    def GetFusionCompByIndex(self, i):
        return self.comps[i - 1]

    def GetMarkers(self):
        return dict(self.markers)


class Timeline:
    def __init__(self, project, name, fps=60, start=216000, w=1920, h=1080):
        self.project, self.name, self.fps, self.start = project, name, fps, start
        self.w, self.h = w, h
        self.uid = uuid.uuid4().hex
        self.tracks = {"video": [{"name": "Video 1", "items": []}], "audio": [{"name": "Audio 1", "items": []}],
                       "subtitle": []}
        self.markers = {}

    # facts
    def GetName(self):
        return self.name

    def GetUniqueId(self):
        return self.uid

    def GetSetting(self, key=None):
        return {"timelineFrameRate": str(self.fps), "timelineResolutionWidth": str(self.w),
                "timelineResolutionHeight": str(self.h), "timelineDropFrameTimecode": "0"}.get(key, "")

    def GetStartFrame(self):
        return self.start

    def GetEndFrame(self):
        ends = [it.GetEnd() for t in self.tracks["video"] + self.tracks["audio"] for it in t["items"]]
        return max(ends or [self.start])

    def GetStartTimecode(self):
        return "01:00:00:00"

    def SetCurrentTimecode(self, tc):
        return True

    # tracks
    def GetTrackCount(self, t):
        return len(self.tracks[t])

    def AddTrack(self, t, sub=None):
        self.tracks[t].append({"name": f"{t.title()} {len(self.tracks[t]) + 1}", "items": []})
        return True

    def DeleteTrack(self, t, i):
        if 1 <= i <= len(self.tracks[t]):
            del self.tracks[t][i - 1]
            return True
        return False

    def GetTrackName(self, t, i):
        return self.tracks[t][i - 1]["name"]

    def SetTrackName(self, t, i, name):
        self.tracks[t][i - 1]["name"] = name
        return True

    def GetIsTrackEnabled(self, t, i):
        return True

    def GetIsTrackLocked(self, t, i):
        return False

    def GetItemListInTrack(self, t, i):
        return sorted(self.tracks[t][i - 1]["items"], key=lambda x: x.start)

    def DeleteClips(self, items, ripple=False):
        ids = {id(x) for x in items}
        for t in ("video", "audio"):
            for tr in self.tracks[t]:
                tr["items"] = [x for x in tr["items"] if id(x) not in ids]
        return True

    # markers (frame relative to timeline start)
    def AddMarker(self, frame, color, name, note, dur, custom=""):
        if frame in self.markers:
            return False
        self.markers[frame] = {"color": color, "name": name, "note": note, "duration": dur, "customData": custom or ""}
        return True

    def GetMarkers(self):
        return {float(k): v for k, v in self.markers.items()}

    def DeleteMarkerAtFrame(self, f):
        return self.markers.pop(int(f), None) is not None

    def GetMarkerByCustomData(self, cd):
        return next((v for v in self.markers.values() if v["customData"] == cd), {})

    def DuplicateTimeline(self, name):
        dup = Timeline(self.project, name, self.fps, self.start, self.w, self.h)
        self.project.timelines.append(dup)
        return dup

    # used by MediaPool.AppendToTimeline
    def _append(self, info):
        mtype = info.get("mediaType")
        t = "audio" if mtype == 2 else "video"
        idx = info.get("trackIndex", 1)
        if idx > len(self.tracks[t]):
            return None
        dur = int(info["endFrame"]) - int(info["startFrame"]) + 1  # inclusive
        if info["mediaPoolItem"].props["Type"] == "Still":
            dur = min(dur, 5 * self.fps)
        item = TimelineItem(info["mediaPoolItem"], int(info["recordFrame"]), dur, int(info["startFrame"]), t)
        self.tracks[t][idx - 1]["items"].append(item)
        return item


class Folder:
    def __init__(self, name):
        self.name, self.clips, self.subs = name, [], []

    def GetName(self):
        return self.name

    def GetClipList(self):
        return list(self.clips)

    def GetSubFolderList(self):
        return list(self.subs)


class MediaPool:
    def __init__(self, project):
        self.project = project
        self.root = Folder("Master")
        self.current = self.root

    def GetRootFolder(self):
        return self.root

    def AddSubFolder(self, parent, name):
        f = Folder(name)
        parent.subs.append(f)
        return f

    def GetCurrentFolder(self):
        return self.current

    def SetCurrentFolder(self, f):
        self.current = f
        return True

    def ImportMedia(self, paths):
        items = [MediaPoolItem(p) for p in paths]
        self.current.clips += items
        return items

    def AppendToTimeline(self, infos):
        tl = self.project.current
        out = [tl._append(i) for i in infos]
        return [x for x in out if x is not None]

    def CreateEmptyTimeline(self, name):
        tl = Timeline(self.project, name)
        self.project.timelines.append(tl)
        self.project.current = tl
        return tl

    def DeleteTimelines(self, tls):
        self.project.timelines = [t for t in self.project.timelines if t not in tls]
        return True


class Project:
    def __init__(self, review_source):
        self.timelines = []
        self.current = None
        self.pool = MediaPool(self)
        self.render = {}
        self.review_source = review_source

    def GetName(self):
        return "Test Project"

    def GetMediaPool(self):
        return self.pool

    def GetCurrentTimeline(self):
        return self.current

    def SetCurrentTimeline(self, tl):
        self.current = tl
        return True

    def GetSetting(self, key=None):
        return {"timelineFrameRate": "60"}.get(key, "")

    def SetCurrentRenderMode(self, m):
        return True

    def GetRenderFormats(self):
        return {"MP4": "mp4", "QuickTime": "mov"}

    def GetRenderCodecs(self, fmt):
        return {"H.264": "H264", "H.265": "H265"} if fmt in ("mp4", "MP4", "mov") else {}

    def SetCurrentRenderFormatAndCodec(self, f, c):
        self.render["fmt"], self.render["codec"] = f, c
        return True

    def SetRenderSettings(self, s):
        self.render.update(s)
        return True

    def AddRenderJob(self):
        return "job-1"

    def StartRendering(self, jobs, isInteractiveMode=False):
        shutil.copy(self.review_source, f"{self.render['TargetDir']}/{self.render['CustomName']}.mp4")
        return True

    def IsRenderingInProgress(self):
        return False

    def GetRenderJobStatus(self, job):
        return {"JobStatus": "Complete", "CompletionPercentage": 100}

    def DeleteRenderJob(self, job):
        return True

    def ExportCurrentFrameAsStill(self, path):
        return False


class ProjectManager:
    def __init__(self, project):
        self.project = project

    def GetCurrentProject(self):
        return self.project


class Resolve:
    def __init__(self, project):
        self.pm = ProjectManager(project)

    def GetProjectManager(self):
        return self.pm

    def GetProductName(self):
        return "DaVinci Resolve"

    def GetVersionString(self):
        return "21.0.4.7"

    def GetCurrentPage(self):
        return "edit"
