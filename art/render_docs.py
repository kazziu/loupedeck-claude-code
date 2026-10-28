"""Renders the README images from the same pixel art code (no image generators).

Usage: python art/render_docs.py            -> docs/img/{hero.png, wheel.gif, tiles.png, states.png}
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pixelart as P  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "img")
BG, PANEL, TILE, TEXT, MUTED = (13, 17, 23), (32, 33, 38), (0, 0, 0), (235, 235, 235), (140, 140, 150)

PAGE1 = [("compact", "Compact"), ("clear", "Clear"), ("model", "Model"), ("resume", "Resume"),
         ("plan", "Plan"), ("stop", "Stop"), ("kill", "Kill"), ("git_status", "git status"),
         ("remote", "Remote"), ("new", "New session"), ("continue", "Continue"), ("next", "Next")]
STATES = [("idle", "idle"), ("work", "Claude is working"), ("attention", "Claude needs you"),
          ("done", "task done"), ("oops", "tool failed"), ("squish", "/compact"), ("hello", "session start"),
          ("happy", "tap"), ("eat", "tap when hungry"), ("dance", "double tap"), ("dizzy", "spin too fast"),
          ("sleep", "3 min alone"), ("hungry", "hungry"), ("walk_r", "wandering")]


def font(size):
    for name in ("arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def tile_img(name, caption, size=120):
    """One LCD tile like on the device: icon + caption."""
    im = Image.new("RGB", (size, size), TILE)
    icon = P.tile(name).image(1).resize((int(size * 0.72),) * 2, Image.NEAREST)
    im.paste(icon, ((size - icon.width) // 2, 2), icon)
    d = ImageDraw.Draw(im)
    f = font(int(size * 0.12))
    w = d.textlength(caption, font=f)
    d.text(((size - w) / 2, size * 0.8), caption, font=f, fill=TEXT)
    return im


def wheel_img(state, f, size=240):
    frame = P.wheel_frame(state, f, P.CX).image(P.SCALE, bg=(0, 0, 0, 255)).convert("RGB")
    if size != 240:
        frame = frame.resize((size, size), Image.NEAREST)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    return frame, mask


def rounded(d, box, r, fill):
    d.rounded_rectangle(box, r, fill=fill)


def hero():
    W, H = 1280, 560
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    rounded(d, (40, 40, W - 40, H - 40), 36, PANEL)
    # 3x4 tile grid
    t, gap, x0, y0 = 120, 14, 90, 70
    rounded(d, (x0 - 20, y0 - 20, x0 + 4 * t + 3 * gap + 20, y0 + 3 * t + 2 * gap + 20), 18, (8, 8, 10))
    for i, (name, cap) in enumerate(PAGE1):
        im.paste(tile_img(name, cap, t), (x0 + (i % 4) * (t + gap), y0 + (i // 4) * (t + gap)))
    # wheel
    cx, cy, R = 930, 280, 190
    d.ellipse((cx - R - 22, cy - R - 22, cx + R + 22, cy + R + 22), fill=(20, 20, 24))
    d.ellipse((cx - R - 10, cy - R - 10, cx + R + 10, cy + R + 10), fill=(70, 70, 78))
    frame, mask = wheel_img("attention", 2, 2 * R)
    im.paste(frame, (cx - R, cy - R), mask)
    return im


def tiles_sheet():
    names = [(n, n.replace("_", " ")) for n in P.TILE_NAMES]
    cols, t, gap = 7, 120, 12
    rows = (len(names) + cols - 1) // cols
    im = Image.new("RGB", (cols * (t + gap) + gap, rows * (t + gap) + gap), BG)
    for i, (n, cap) in enumerate(names):
        im.paste(tile_img(n, cap, t), (gap + (i % cols) * (t + gap), gap + (i // cols) * (t + gap)))
    return im


def states_sheet():
    cols, s, gap = 7, 160, 18
    rows = (len(STATES) + cols - 1) // cols
    im = Image.new("RGB", (cols * (s + gap) + gap, rows * (s + gap + 26) + gap), BG)
    d = ImageDraw.Draw(im)
    f = font(14)
    for i, (st, cap) in enumerate(STATES):
        x, y = gap + (i % cols) * (s + gap), gap + (i // cols) * (s + gap + 26)
        frame, mask = wheel_img(st, 3, s)
        im.paste(frame, (x, y), mask)
        w = d.textlength(cap, font=f)
        d.text((x + (s - w) / 2, y + s + 5), cap, font=f, fill=MUTED)
    return im


def wheel_gif(path):
    seq = ["hello", "idle", "work", "attention", "work", "oops", "work", "done", "squish", "dizzy", "eat", "dance",
           "sleep"]
    frames = []
    size = 240
    for st in seq:
        n = max(P.WHEEL_STATES.get(st, 8), 12)
        for f in range(n):
            frame, mask = wheel_img(st, f, size)
            canvas = Image.new("RGB", (size, size), BG)
            canvas.paste(frame, (0, 0), mask)
            frames.append(canvas.convert("P", palette=Image.ADAPTIVE, colors=64))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=120, loop=0, optimize=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    hero().save(os.path.join(OUT, "hero.png"), optimize=True)
    tiles_sheet().save(os.path.join(OUT, "tiles.png"), optimize=True)
    states_sheet().save(os.path.join(OUT, "states.png"), optimize=True)
    wheel_gif(os.path.join(OUT, "wheel.gif"))
    print(OUT)


if __name__ == "__main__":
    main()
