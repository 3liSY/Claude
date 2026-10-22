"""Find B-roll and sounds from sources that are safe on a monetized channel.

  python stock.py search "rubik cube" [--sfx] [--source pexels|pixabay|freesound|youtube] [--project P]
  python stock.py download candidate:pexels:12345 [--project P]     # ONLY after his OK in chat
  python stock.py links "rubik cube"                                 # browse links, no API keys needed

Search never downloads anything. Results are saved as candidates
(analysis/candidates.json) with preview pictures for the edit sheet.
API keys (free) live in EDITOR_HOME/keys.json: {"pexels": "...", "pixabay": "...",
"freesound": "...", "youtube": "..."}. No keys -> 'links' mode.
"""
from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request

import edcommon as ec

LICENSES = {
    "pexels": ("Pexels License (free, monetized OK, no attribution required)", "https://www.pexels.com/license/"),
    "pixabay": ("Pixabay Content License (free, monetized OK, no attribution required)",
                "https://pixabay.com/service/license-summary/"),
}
FREESOUND_OK = {"creative commons 0": ("CC0 1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
                "attribution": ("CC BY", "https://creativecommons.org/licenses/by/4.0/")}
UA = {"User-Agent": "editor-skill/1.0"}


def http_json(url: str, headers: dict | None = None) -> dict:
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def links(query: str) -> list[tuple[str, str]]:
    q = urllib.parse.quote(query)
    qp = urllib.parse.quote_plus(query)
    return [
        ("Pexels videos", f"https://www.pexels.com/search/videos/{q}/"),
        ("Pixabay videos", f"https://pixabay.com/videos/search/{q}/"),
        ("Coverr", f"https://coverr.co/search?q={qp}"),
        ("Mixkit", f"https://mixkit.co/free-stock-video/{ec.slugify(query)}/"),
        ("YouTube, Creative Commons only", f"https://www.youtube.com/results?search_query={qp}&sp=EgIwAQ%253D%253D"),
        ("Freesound, CC0 only", f"https://freesound.org/search/?q={qp}&f=license:%22Creative+Commons+0%22"),
        ("Pixabay sound effects", f"https://pixabay.com/sound-effects/search/{q}/"),
        ("YouTube Audio Library (sound effects)", "https://studio.youtube.com/ -> Audio Library -> Sound effects"),
    ]


def search_pexels(q, key, n):
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode({"query": q, "per_page": n})
    data = http_json(url, {"Authorization": key})
    out = []
    for v in data.get("videos", []):
        files = sorted((f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4" and f.get("width")),
                       key=lambda f: abs((f.get("height") or 0) - 1080))
        if not files:
            continue
        out.append({"ref": f"candidate:pexels:{v['id']}", "kind": "video", "duration": v.get("duration"),
                    "width": files[0].get("width"), "height": files[0].get("height"), "thumb": v.get("image"),
                    "page_url": v.get("url"), "creator": (v.get("user") or {}).get("name"),
                    "download": files[0]["link"], "license": LICENSES["pexels"][0], "license_url": LICENSES["pexels"][1]})
    return out


def search_pixabay(q, key, n):
    url = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode({"key": key, "q": q, "per_page": max(3, n)})
    out = []
    for h in http_json(url).get("hits", []):
        vids = h.get("videos", {})
        best = vids.get("large") if (vids.get("large") or {}).get("url") else vids.get("medium", {})
        out.append({"ref": f"candidate:pixabay:{h['id']}", "kind": "video", "duration": h.get("duration"),
                    "width": best.get("width"), "height": best.get("height"), "thumb": best.get("thumbnail"),
                    "page_url": h.get("pageURL"), "creator": h.get("user"), "download": best.get("url"),
                    "tags": h.get("tags"), "license": LICENSES["pixabay"][0], "license_url": LICENSES["pixabay"][1]})
    return out


def search_freesound(q, key, n):
    params = {"query": q, "filter": 'license:("Creative Commons 0" OR "Attribution")', "page_size": n,
              "fields": "id,name,duration,license,username,previews,url,tags", "token": key}
    data = http_json("https://freesound.org/apiv2/search/text/?" + urllib.parse.urlencode(params))
    out = []
    for s in data.get("results", []):
        lic = str(s.get("license", "")).lower()
        kind = next((v for k, v in FREESOUND_OK.items() if k in lic and "noncommercial" not in lic), None)
        if not kind:
            continue  # never NonCommercial
        attr = None if kind[0] == "CC0 1.0" else f"\"{s['name']}\" by {s['username']} (freesound.org/s/{s['id']}) – CC BY"
        out.append({"ref": f"candidate:freesound:{s['id']}", "kind": "sfx", "duration": s.get("duration"),
                    "page_url": s.get("url"), "creator": s.get("username"), "name": s.get("name"),
                    "download": (s.get("previews") or {}).get("preview-hq-mp3"), "preview": (s.get("previews") or {}).get("preview-hq-mp3"),
                    "license": kind[0], "license_url": kind[1], "attribution": attr})
    return out


def search_youtube_cc(q, key, n):
    params = {"part": "snippet", "q": q, "type": "video", "videoLicense": "creativeCommon", "maxResults": n, "key": key}
    data = http_json("https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode(params))
    out = []
    for it in data.get("items", []):
        vid = it["id"]["videoId"]
        sn = it["snippet"]
        out.append({"ref": f"candidate:youtube:{vid}", "kind": "video", "title": sn.get("title"),
                    "creator": sn.get("channelTitle"), "thumb": (sn.get("thumbnails", {}).get("medium") or {}).get("url"),
                    "page_url": f"https://www.youtube.com/watch?v={vid}", "download": None,
                    "license": "CC BY (YouTube Creative Commons)", "license_url": "https://www.youtube.com/t/creative_commons",
                    "attribution": f"\"{sn.get('title')}\" by {sn.get('channelTitle')} – youtube.com/watch?v={vid} – CC BY",
                    "note": "YouTube's own CC BY label only. 'No copyright' in a title means nothing. "
                            "YouTube's terms don't allow downloading with outside tools: he decides how to get the file."})
    return out


SEARCHERS = {"pexels": search_pexels, "pixabay": search_pixabay, "freesound": search_freesound, "youtube": search_youtube_cc}


def cmd_search(args) -> None:
    keys = ec.load_keys()
    sources = [args.source] if args.source else (["freesound"] if args.sfx else ["pexels", "pixabay", "youtube"])
    results, missing = [], []
    for src in sources:
        if not keys.get(src):
            missing.append(src)
            continue
        try:
            got = SEARCHERS[src](args.query, keys[src], args.n)
            for g in got:
                g["query"] = args.query
            results += got
            print(f"{src}: {len(got)} result(s)")
        except Exception as e:
            print(f"{src}: search failed ({e})")
    if missing:
        print(f"No API key for: {', '.join(missing)}. Browse instead:")
        for name, url in links(args.query):
            print(f"  {name}: {url}")
    if args.project and results:
        proj = ec.resolve_project(args.project)
        cp = proj / "analysis" / "candidates.json"
        cands = ec.read_json(cp) if cp.exists() else {}
        for r in results:
            cands[r["ref"]] = r
        ec.write_json(cp, cands)
        print(f"Saved candidates: {cp}")
    for r in results:
        dur = f"{r['duration']}s" if r.get("duration") else ""
        print(f"  {r['ref']}  {dur}  {r.get('width') or ''}x{r.get('height') or ''}  by {r.get('creator')}  {r.get('page_url')}")


def cmd_links(args) -> None:
    for name, url in links(args.query):
        print(f"{name}: {url}")


def cmd_download(args) -> None:
    from library import cmd_register

    proj = ec.resolve_project(args.project)
    cands = ec.read_json(proj / "analysis" / "candidates.json")
    c = cands.get(args.ref)
    if not c:
        ec.die(f"{args.ref} is not in this project's candidates. Search first.")
    if not c.get("download"):
        ec.die(f"{args.ref} can't be downloaded by the skill. {c.get('note', '')}")
    _, source, sid = args.ref.split(":", 2)
    folder = ec.library_dir() / "stock" / ("sfx" if c["kind"] == "sfx" else "video")
    folder.mkdir(parents=True, exist_ok=True)
    ext = ".mp3" if c["kind"] == "sfx" else ".mp4"
    out = folder / f"{source}_{sid}{ext}"
    if not out.exists():
        print(f"Downloading {args.ref} ...")
        req = urllib.request.Request(c["download"], headers=UA)
        with urllib.request.urlopen(req, timeout=120) as r, open(out, "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
    proof = folder / f"{source}_{sid}.license.json"
    ec.write_json(proof, {**c, "downloaded": ec.now_iso()})
    reg = argparse.Namespace(file=str(out), source=source, id=sid, page=c.get("page_url"), creator=c.get("creator"),
                             license=c["license"], license_url=c.get("license_url"), attribution=c.get("attribution"))
    cmd_register(reg)  # prints the library id to use as asset.ref in the plan


def main() -> None:
    ec.setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--sfx", action="store_true")
    s.add_argument("--source", choices=list(SEARCHERS)); s.add_argument("--project"); s.add_argument("-n", type=int, default=8)
    s.set_defaults(fn=cmd_search)
    s = sub.add_parser("links"); s.add_argument("query"); s.set_defaults(fn=cmd_links)
    s = sub.add_parser("download"); s.add_argument("ref"); s.add_argument("--project"); s.set_defaults(fn=cmd_download)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
