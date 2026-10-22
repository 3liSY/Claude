"""Render text pop-ups / captions as transparent full-frame PNGs.

Resolve's own text tools break Arabic (letters not joined, wrong order). A real
browser engine shapes Arabic correctly, so cards are drawn as HTML and
screenshotted by Edge/Chrome in headless mode (Edge ships with Windows 11:
nothing to install). Each PNG is exactly the timeline size, so it drops onto a
top video track with no positioning.

  python text_cards.py cards.json --out DIR --size 1920x1080
  cards.json = [{"id": "P01", "text": "PLL", "style": "pop", "position": "top"}, ...]
  python text_cards.py --demo --out DIR      # sample cards to check fonts
"""
from __future__ import annotations

import argparse
import html
import os
import shutil
import tempfile
from pathlib import Path

import edcommon as ec

FONT_STACK = "'Cairo','Tajawal','Noto Kufi Arabic','Segoe UI','Tahoma','Arial',sans-serif"

STYLES = {
    # size = font size as a fraction of frame height
    "pop": {"size": 0.10, "color": "#FFFFFF", "stroke": "#000000", "stroke_w": 0.012, "weight": 900, "bg": None},
    "number": {"size": 0.16, "color": "#FFD400", "stroke": "#000000", "stroke_w": 0.014, "weight": 900, "bg": None},
    "label": {"size": 0.055, "color": "#FFFFFF", "stroke": None, "stroke_w": 0, "weight": 800, "bg": "rgba(10,10,10,0.78)"},
    "caption": {"size": 0.055, "color": "#FFFFFF", "stroke": "#000000", "stroke_w": 0.007, "weight": 800, "bg": None},
    "warning": {"size": 0.075, "color": "#FFFFFF", "stroke": None, "stroke_w": 0, "weight": 900, "bg": "rgba(220,30,30,0.92)"},
}

POSITIONS = {"top": (0.5, 0.16), "center": (0.5, 0.5), "bottom": (0.5, 0.84), "upper": (0.5, 0.3),
             "lower": (0.5, 0.7), "left": (0.25, 0.5), "right": (0.75, 0.5)}


def card_html(card: dict, w: int, h: int) -> str:
    st = dict(STYLES.get(card.get("style", "pop"), STYLES["pop"]))
    st.update({k: card[k] for k in ("color", "stroke", "bg") if k in card})
    pos = card.get("position", "center")
    cx, cy = POSITIONS.get(pos, (0.5, 0.5)) if isinstance(pos, str) else (float(pos[0]), float(pos[1]))
    fs = round(st["size"] * h * float(card.get("scale", 1.0)))
    sw = round(st["stroke_w"] * h, 1)
    stroke_css = (f"-webkit-text-stroke:{sw * 2}px {st['stroke']};paint-order:stroke fill;"
                  if st.get("stroke") and sw else "")
    bg_css = (f"background:{st['bg']};padding:{fs * 0.18:.0f}px {fs * 0.45:.0f}px;border-radius:{fs * 0.3:.0f}px;"
              if st.get("bg") else "")
    shadow = f"text-shadow:0 {fs * 0.06:.0f}px {fs * 0.12:.0f}px rgba(0,0,0,0.55);" if not st.get("bg") else ""
    text = html.escape(str(card["text"])).replace("\n", "<br>")
    max_w = card.get("max_width", 0.82)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;padding:0;width:{w}px;height:{h}px;background:transparent;overflow:hidden}}
.t{{position:absolute;left:{cx * 100:.2f}%;top:{cy * 100:.2f}%;transform:translate(-50%,-50%) rotate({card.get('rotate', 0)}deg);
font-family:{FONT_STACK};font-weight:{st['weight']};font-size:{fs}px;line-height:1.25;color:{st['color']};
text-align:center;width:max-content;max-width:{max_w * w:.0f}px;unicode-bidi:plaintext;white-space:pre-wrap;{stroke_css}{bg_css}{shadow}}}
</style></head><body><div class="t" dir="auto">{text}</div></body></html>"""


def find_browser() -> str | None:
    cfg = ec.load_config()
    cands = [cfg.get("browser") or ""]
    pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    pf = os.environ.get("ProgramFiles", r"C:\Program Files")
    cands += [rf"{pf86}\Microsoft\Edge\Application\msedge.exe", rf"{pf}\Microsoft\Edge\Application\msedge.exe",
              rf"{pf}\Google\Chrome\Application\chrome.exe", rf"{pf86}\Google\Chrome\Application\chrome.exe"]
    for name in ("msedge", "chrome", "google-chrome", "chromium", "chromium-browser"):
        p = shutil.which(name)
        if p:
            cands.append(p)
    pw = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers"))
    if pw.exists():
        cands += [str(p) for p in sorted(pw.glob("chromium-*/chrome-linux*/chrome"))]
    for c in cands:
        if c and Path(c).exists():
            return c
    return None


def render_with_playwright(jobs: list[tuple[str, Path]], w: int, h: int) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
            for doc, out in jobs:
                page.set_content(doc, wait_until="load")
                page.screenshot(path=str(out), omit_background=True)
            browser.close()
        return True
    except Exception as e:
        print(f"(Playwright failed, trying the system browser: {e})")
        return False


def render_with_browser(jobs: list[tuple[str, Path]], w: int, h: int) -> None:
    exe = find_browser()
    if not exe:
        ec.die("No Edge/Chrome found for text cards. Set 'browser' in config.json to msedge.exe.")
    with tempfile.TemporaryDirectory() as tmp:
        for i, (doc, out) in enumerate(jobs):
            page = Path(tmp) / f"card_{i}.html"
            page.write_text(doc, encoding="utf-8")
            profile = Path(tmp) / "profile"
            cmd = [exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                   "--no-default-browser-check", f"--user-data-dir={profile}", "--force-device-scale-factor=1",
                   "--default-background-color=00000000", f"--window-size={w},{h}",
                   f"--screenshot={out}", page.as_uri()]
            if hasattr(os, "geteuid") and os.geteuid() == 0:
                cmd.insert(1, "--no-sandbox")  # Linux containers run as root; never needed on Windows
            ec.run(cmd, check=False)
            if not out.exists():
                ec.die(f"Browser did not produce {out.name}.")


def render_cards(cards: list[dict], out_dir: Path, w: int, h: int) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs, paths = [], {}
    for c in cards:
        out = out_dir / f"{c['id']}.png"
        jobs.append((card_html(c, w, h), out))
        paths[c["id"]] = out
    if jobs and not render_with_playwright(jobs, w, h):
        render_with_browser(jobs, w, h)
    return paths


def preview_grid(paths: list[Path], out: Path) -> Path:
    """All cards on a checkerboard, so Claude can check every Arabic word is joined."""
    from PIL import Image

    thumbs = []
    for p in paths:
        im = Image.open(p).convert("RGBA")
        im.thumbnail((640, 360))
        bg = Image.new("RGBA", im.size, (90, 90, 90, 255))
        tile = 20
        for y in range(0, im.size[1], tile):
            for x in range((y // tile) % 2 * tile, im.size[0], tile * 2):
                bg.paste((140, 140, 140, 255), (x, y, x + tile, y + tile))
        thumbs.append(Image.alpha_composite(bg, im))
    cols = 2
    rows = (len(thumbs) + cols - 1) // cols
    grid = Image.new("RGB", (640 * cols, 360 * max(1, rows)), (0, 0, 0))
    for i, t in enumerate(thumbs):
        grid.paste(t.convert("RGB"), ((i % cols) * 640, (i // cols) * 360))
    grid.save(out, quality=88)
    return out


def main() -> None:
    ec.setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cards", nargs="?")
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    w, h = (int(x) for x in args.size.lower().split("x"))
    if args.demo:
        cards = [{"id": "demo_pop", "text": "هاد الـ PLL أسهل واحد", "style": "pop", "position": "top"},
                 {"id": "demo_num", "text": "8.53", "style": "number", "position": "center"},
                 {"id": "demo_label", "text": "R U R' U'", "style": "label", "position": "bottom"},
                 {"id": "demo_caption", "text": "يا جماعة هاد أسرع حل بحياتي", "style": "caption", "position": "bottom"}]
    else:
        cards = ec.read_json(args.cards)
    paths = render_cards(cards, Path(args.out), w, h)
    grid = preview_grid(list(paths.values()), Path(args.out) / "_preview.jpg")
    print(f"{len(paths)} card(s) rendered. Check them: {grid}")


if __name__ == "__main__":
    main()
