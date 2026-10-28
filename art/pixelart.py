"""Pixel art maskotki Claude Code rysowany kodem (bez generatorow obrazu).

Wszystko powstaje na siatce pikseli i jest skalowane metoda nearest neighbour.
  tiles(): ikony kafelkow 20x20 (render 240x240)
  wheel_frames(): klatki animacji tamagotchi na kolo 48x48 (render 240x240)
"""
from PIL import Image, ImageDraw
import math

# --- paleta -----------------------------------------------------------------------------------------
T = (0, 0, 0, 0)
ORANGE, ORANGE_HI, ORANGE_LO = (217, 119, 87, 255), (236, 152, 120, 255), (178, 86, 58, 255)
INK = (24, 20, 18, 255)
WHITE, GREY, DGREY = (250, 246, 240, 255), (150, 150, 158, 255), (82, 82, 92, 255)
RED, DRED, GREEN, DGREEN = (232, 64, 64, 255), (160, 32, 40, 255), (92, 200, 104, 255), (40, 130, 60, 255)
YELLOW, GOLD, BROWN, LBROWN = (255, 214, 72, 255), (230, 170, 40, 255), (122, 76, 44, 255), (176, 120, 70, 255)
BLUE, LBLUE, PINK, PURPLE = (80, 140, 240, 255), (150, 200, 255, 255), (255, 120, 170, 255), (170, 110, 230, 255)
CREAM = (255, 240, 214, 255)

PAL = {".": None, "o": ORANGE, "h": ORANGE_HI, "l": ORANGE_LO, "k": INK, "w": WHITE, "g": GREY, "d": DGREY,
       "r": RED, "R": DRED, "G": GREEN, "D": DGREEN, "y": YELLOW, "Y": GOLD, "b": BROWN, "B": LBROWN,
       "u": BLUE, "U": LBLUE, "p": PINK, "v": PURPLE, "c": CREAM}


class Canvas:
    def __init__(self, w, h=None):
        self.w, self.h = w, h or w
        self.px = [[T] * self.w for _ in range(self.h)]

    def set(self, x, y, c):
        if c and 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = c

    def rect(self, x, y, w, h, c):
        for j in range(h):
            for i in range(w):
                self.set(x + i, y + j, c)

    def sprite(self, x, y, rows, flip=False, k=1):
        for j, row in enumerate(rows):
            if flip:
                row = row[::-1]
            for i, ch in enumerate(row):
                if PAL.get(ch):
                    self.rect(x + i * k, y + j * k, k, k, PAL[ch])

    def image(self, scale, bg=None):
        im = Image.new("RGBA", (self.w, self.h), T)
        im.putdata([c for row in self.px for c in row])
        if bg:
            im = Image.alpha_composite(Image.new("RGBA", im.size, bg), im)
        return im.resize((self.w * scale, self.h * scale), Image.NEAREST)


# --- maskotka ---------------------------------------------------------------------------------------
class Size:
    """Proporcje maskotki w pikselach siatki."""
    def __init__(self, W, H, ew, eh, aw, ah, lw, lh):
        self.W, self.H, self.ew, self.eh, self.aw, self.ah, self.lw, self.lh = W, H, ew, eh, aw, ah, lw, lh

SMALL = Size(12, 7, 1, 2, 2, 2, 1, 2)
BIG = Size(26, 15, 2, 5, 3, 4, 3, 4)


def mascot(cv, cx, by, s=SMALL, eyes="normal", look=0, arms="side", step=0, mouth=None, squash=0,
           blush=False, tilt=0):
    """Rysuje maskotke. cx = srodek, by = dolny wiersz nog. Zwraca slownik punktow zaczepienia."""
    W, H = s.W + 2 * squash, max(3, s.H - squash)
    lh = s.lh if step != 9 else 0
    x0, y0 = cx - W // 2, by - lh - H + 1
    # nogi (step: 0 = stoi, 1/2 = fazy chodu)
    gap = W // 5
    legs = [x0 + gap // 2 + 1, x0 + gap + 2, x0 + W - gap - 2 - s.lw + 1, x0 + W - gap // 2 - 1 - s.lw + 1]
    legs = [x0 + 1 + round(i * (W - 2 - s.lw) / 3) for i in range(4)]
    for i, lx in enumerate(legs):
        dy = 0
        if step in (1, 2) and (i % 2 == step - 1):
            dy = -1
        cv.rect(lx, by - lh + 1 + dy, s.lw, lh, ORANGE_LO)
    # tulow z cieniowaniem; tilt przesuwa gorne wiersze
    for j in range(H):
        off = round(tilt * (H - 1 - j) / max(1, H - 1))
        for i in range(W):
            c = ORANGE
            if j == 0:
                c = ORANGE_HI
            elif j == H - 1 or i == W - 1:
                c = ORANGE_LO
            elif i == 0:
                c = ORANGE_HI if j < H // 2 else ORANGE
            cv.set(x0 + i + off, y0 + j, c)
    top_off = tilt
    # rece
    ay = y0 + H // 2 - s.ah // 2
    if arms == "side":
        cv.rect(x0 - s.aw, ay, s.aw, s.ah, ORANGE)
        cv.rect(x0 + W, ay, s.aw, s.ah, ORANGE)
    elif arms in ("up", "left_up", "right_up"):
        for side in ("left", "right"):
            up = arms == "up" or arms == side + "_up"
            ax = x0 - s.aw if side == "left" else x0 + W
            if up:
                cv.rect(ax, ay - s.ah - 1, s.aw, s.ah * 2, ORANGE)
            else:
                cv.rect(ax, ay, s.aw, s.ah, ORANGE)
    elif arms == "down":
        cv.rect(x0 - s.aw + 1, ay + s.ah, s.aw - 1 or 1, s.ah, ORANGE)
        cv.rect(x0 + W, ay + s.ah, s.aw - 1 or 1, s.ah, ORANGE)
    # oczy
    ey = y0 + max(1, H // 2 - s.eh // 2 - (1 if s is BIG else 0))
    exs = [x0 + W // 4 + look + top_off // 2, x0 + W - W // 4 - s.ew + look + top_off // 2]
    ew, eh = s.ew, s.eh
    for k, ex in enumerate(exs):
        if eyes == "normal":
            cv.rect(ex, ey, ew, eh, INK)
            if s is BIG:
                cv.rect(ex, ey, 1, 1, WHITE)
        elif eyes == "blink" or eyes == "sleep":
            yy = ey + eh - 1 if eyes == "sleep" else ey + eh // 2
            cv.rect(ex - (1 if s is BIG else 0), yy, ew + (2 if s is BIG else 0), 1, INK)
        elif eyes == "happy":  # ^ ^
            if s is BIG:
                cv.set(ex - 1, ey + 2, INK); cv.set(ex, ey + 1, INK); cv.set(ex + 1, ey + 1, INK); cv.set(ex + 2, ey + 2, INK)
                cv.set(ex - 2, ey + 3, INK); cv.set(ex + 3, ey + 3, INK)
            else:
                cv.set(ex - 1, ey + 1, INK); cv.set(ex, ey, INK); cv.set(ex + 1, ey + 1, INK)
        elif eyes == "x":
            r = 2 if s is BIG else 1
            for d in range(-r, r + 1):
                cv.set(ex + d, ey + 1 + d, INK); cv.set(ex + d, ey + 1 - d, INK)
        elif eyes == "squint":  # > <
            d = 1 if k == 0 else -1
            r = 2 if s is BIG else 1
            for t in range(-r, r + 1):
                cv.set(ex + d * (r - abs(t)), ey + 1 + t, INK)
        elif eyes == "spiral":
            for (dx, dy) in [(0, 0), (1, 0), (1, 1), (0, 2), (-1, 2), (-2, 1), (-2, 0), (-2, -1), (-1, -2), (0, -2), (1, -2), (2, -2), (3, -1), (3, 0), (3, 1), (3, 2)]:
                cv.set(ex + dx, ey + 2 + dy, INK)
        elif eyes == "big":
            bw, bh = (ew + 2, eh + 1) if s is BIG else (2, 3)
            cv.rect(ex - (1 if s is BIG else 0), ey - 1, bw, bh, INK)
            cv.set(ex - (1 if s is BIG else 0), ey - 1, WHITE)
        elif eyes == "sad":
            cv.rect(ex, ey + 1, ew, eh - 1, INK)
            bx = ex - 1 if k == 0 else ex + ew
            cv.set(ex + (ew if k == 0 else -1), ey - 1, INK); cv.set(bx + (1 if k == 0 else -1), ey - 1, INK)
    if eyes == "shades":
        cv.sprite(exs[0] - 2, ey, ["kkkkkkkkkk", ".wkk..wkk."][: 2] if s is SMALL else
                  ["kkkkkkkkkkkkkkkkkkkkkk", "kwwkkkkk......kwwkkkkk", ".kkkkkk........kkkkkk.", "..kkkk..........kkkk.."])
    # usta
    mx, my = x0 + W // 2 - 1 + top_off // 2, ey + eh + (1 if s is BIG else 0)
    if mouth == "o":
        cv.rect(mx, my, 2, 2 if s is BIG else 1, INK)
    elif mouth == "O":
        if s is BIG:
            cv.rect(mx - 1, my, 4, 3, INK); cv.rect(mx, my + 1, 2, 1, RED)
        else:
            cv.rect(mx, my + 1, 2, 2, INK)
    elif mouth == "smile":
        cv.set(mx - 1, my, INK); cv.rect(mx, my + 1, 2, 1, INK); cv.set(mx + 2, my, INK)
    elif mouth == "tongue":
        cv.rect(mx - 1, my, 4, 1, INK); cv.rect(mx + 1, my + 1, 2, 2, PINK)
    elif mouth == "chomp":
        cv.rect(mx - 2, my, 6, 3, INK); cv.rect(mx - 1, my, 4, 1, WHITE)
    elif mouth == "wavy":
        for i in range(-2, 4):
            cv.set(mx + i, my + (i % 2), INK)
    if blush:
        cv.rect(exs[0] - 2, ey + eh + (1 if s is BIG else 0), 2 if s is BIG else 1, 1, PINK)
        cv.rect(exs[1] + ew, ey + eh + (1 if s is BIG else 0), 2 if s is BIG else 1, 1, PINK)
    return {"x0": x0, "y0": y0, "W": W, "H": H, "ay": ay, "eyes": exs, "ey": ey, "mouth": (mx, my)}


# --- male rekwizyty (string art) ------------------------------------------------------------------
ARROW_R = ["...w...", "...ww..", "wwwwww.", "wwwwwww", "wwwwww.", "...ww..", "...w..."]
ARROW_D = [".www.", ".www.", "wwwww", ".www.", "..w.."]
PARTY = ["...y...", "...v...", "..vwv..", "..wvw..", ".vwvwv.", ".wvwvw.", "vwvwvwv"]
CONFETTI = [(1, 2, YELLOW), (3, 6, PINK), (16, 1, GREEN), (18, 5, BLUE), (2, 10, BLUE), (17, 9, YELLOW), (5, 1, GREEN), (14, 4, PINK)]
PLAY = ["G...", "GG..", "GGG.", "GGGG", "GGG.", "GG..", "G..."]
STOP = [".rrr.", "rwwwr", "rrrrr", "rwwwr", ".rrr.", "..d..", "..d..", "..d.."]
HALO = [".yyyy.", "y....y", ".yyyy."]
SPARK = [".w.", "www", ".w."]
SPARK_Y = [".y.", "yyy", ".y."]
BULB = [".yyy.", "yyyyy", "yywyy", ".yyy.", "..g..", ".ggg."]
FLASK = [".ww.", ".ww.", ".UU.", "UGGU", "GGGG", "GGGG"]
MAGNI = [".ggg..", "gUUUg.", "gUwUg.", "gUUUg.", ".ggg..", "....b.", ".....b"]
BROOM = ["....b", "...b.", "..b..", ".b...", "yyy..", "yYy..", "y.y.."]
PAPER = ["wwww", "wddw", "wwww", "wddw", "wwww"]
CHECKS = [".wwwwww.", "w......w", "w.G.dd.w", "w.......", "w.G.dd.w", "w......w", ".www.ww.", ".....w..", "....w..."]
EGG = ["c.c.c.c.c.c.c.", "cccccccccccccc", "cccccccccccccc", ".cccccccccccc."]
PLUS = [".G.", "GGG", ".G."]
MINUS = ["rrr"]
SPEED = ["ggg..", ".....", "gggg.", ".....", "gg..."]
SWEAT = [".U", "UU"]
TAB = ["uuuu.", "uuuuu"]
FONT_A = ["..ww..", ".w..w.", "w....w", "wwwwww", "w....w", "w....w"]
HEART = [".p.p.", "ppppp", "ppppp", ".ppp.", "..p.."]
HEART_S = ["p.p", "ppp", ".p."]
ZZ = ["www", "..w", ".w.", "www"]
NOTE = ["..ww", "..w.", "..w.", "ww..", "ww.."]
STAR = ["..y..", ".yyy.", "yyyyy", ".yyy.", ".y.y."]
COOKIE = [".BBB.", "BbBBB", "BBBbB", "BbBBB", ".BBB."]
LAPTOP = [".dddddddd.", ".duuuuuud.", ".duUuUuud.", ".duuuuuud.", "gggggggggg"]
GLASSES = ["kkk.kkk", "kUk.kUk", "kkkkkkk"]
DROP = [".U.", "UUU", ".U."]


def tile(name):
    """Ikony kafelkow, siatka 20x20."""
    c = Canvas(20)
    if name == "compact":
        mascot(c, 10, 18, eyes="squint", squash=3, mouth="wavy")
        c.sprite(3, 2, ARROW_D); c.sprite(12, 2, ARROW_D)
        c.rect(1, 8, 18, 1, GREY)
    elif name == "clear":
        mascot(c, 8, 18, eyes="happy", arms="right_up")
        c.sprite(14, 7, BROOM)
        c.sprite(1, 3, SPARK); c.sprite(15, 1, SPARK_Y); c.sprite(4, 0, SPARK_Y)
    elif name == "model":
        mascot(c, 10, 18, eyes="shades", mouth="smile", arms="left_up")
        c.sprite(15, 3, SPARK); c.sprite(1, 2, SPARK_Y); c.sprite(11, 1, SPARK_Y)
    elif name == "resume":
        mascot(c, 8, 18, eyes="normal", look=1, arms="right_up", mouth="o")
        c.sprite(14, 6, PLAY)
        c.sprite(2, 2, ZZ)
    elif name == "plan":
        mascot(c, 7, 18, eyes="normal", look=1)
        c.sprite(11, 0, CHECKS)
        c.set(13, 10, WHITE); c.set(12, 11, WHITE)
    elif name == "stop":
        mascot(c, 8, 18, eyes="big", arms="right_up", mouth="O")
        c.sprite(14, 3, STOP)
    elif name == "kill":
        mascot(c, 10, 18, eyes="x", mouth="tongue")
        c.sprite(7, 3, HALO)
    elif name == "git_status":
        m = mascot(c, 8, 18, eyes="normal", look=1, arms="right_up")
        c.sprite(13, 3, MAGNI)
        c.sprite(1, 2, ["w", "w", ".", "w"])
    elif name == "git_diff":
        mascot(c, 10, 18, eyes="happy", arms="up", mouth="smile")
        c.sprite(1, 2, PLUS); c.sprite(16, 3, MINUS); c.sprite(4, 0, PLUS); c.sprite(13, 0, MINUS)
    elif name == "new":
        m = mascot(c, 10, 18, eyes="happy", arms="up", mouth="smile", blush=True)
        c.sprite(7, m["y0"] - 7, PARTY)
        for (x, y, col) in CONFETTI:
            c.set(x, y, col)
    elif name == "continue":
        mascot(c, 11, 18, eyes="normal", look=1, step=1, mouth="o")
        c.sprite(0, 9, SPEED); c.sprite(16, 6, SWEAT)
    elif name == "next":
        mascot(c, 6, 18, eyes="normal", look=1, arms="right_up")
        c.sprite(13, 7, ARROW_R)
    elif name == "prev":
        mascot(c, 14, 18, eyes="normal", look=-1, arms="left_up")
        c.sprite(0, 7, ARROW_R, flip=True)
    elif name == "review":
        m = mascot(c, 8, 18, eyes="normal", look=1)
        c.sprite(m["eyes"][0] - 1, m["ey"] - 1, GLASSES)
        c.sprite(15, 8, PAPER)
    elif name == "tests":
        mascot(c, 8, 18, eyes="big", arms="right_up", mouth="o")
        c.sprite(15, 6, FLASK); c.set(16, 4, GREEN); c.set(17, 2, GREEN)
    elif name == "explain":
        mascot(c, 10, 18, eyes="happy", arms="left_up", mouth="smile")
        c.sprite(7, 1, BULB)
    elif name == "tabs":
        c.sprite(2, 2, TAB); c.sprite(8, 2, ["rrrr.", "rrrrr"]); c.sprite(14, 2, ["GGGG", "GGGG"])
        c.rect(2, 4, 16, 2, BLUE)
        mascot(c, 10, 18, eyes="normal", look=-1, arms="up")
    elif name == "font":
        c.sprite(2, 2, FONT_A); c.sprite(12, 4, ["..w.", ".w.w", "wwww", "w..w"])
        mascot(c, 10, 18, eyes="big", mouth="o")
    return c


TILE_NAMES = ["compact", "clear", "model", "resume", "plan", "stop", "kill", "git_status", "git_diff",
              "new", "continue", "next", "prev", "review", "tests", "explain", "tabs", "font"]


# --- kolo: tamagotchi -------------------------------------------------------------------------------
G = 48          # siatka kola
BY = 38         # linia "podlogi"

def wheel_base(c):
    # ksiezyc/pokoj: delikatna podloga
    for x in range(6, 42):
        c.set(x, BY + 1, (60, 44, 40, 255))
    for x in range(10, 38, 3):
        c.set(x, BY + 2, (44, 34, 32, 255))


def wheel_frame(state, f, x=24, floor=True):
    """Jedna klatka; state = nazwa zachowania, f = numer klatki, x = pozycja srodka maskotki."""
    c = Canvas(G)
    if floor:
        wheel_base(c)
    bob = (f // 2) % 2
    if state == "idle":
        eyes = "blink" if f % 16 == 15 else "normal"
        look = [0, 0, 1, 1, 0, 0, -1, -1][(f // 4) % 8]
        mascot(c, x, BY - bob * 0, BIG, eyes=eyes, look=look)
        if bob:  # oddech: podniesione ramiona
            pass
    elif state == "walk_r" or state == "walk_l":
        d = 1 if state == "walk_r" else -1
        mascot(c, x, BY - (f % 2), BIG, eyes="normal", look=d * 2, step=1 + f % 2)
    elif state == "sleep":
        m = mascot(c, x, BY, BIG, eyes="sleep", squash=1 if (f // 4) % 2 else 0, mouth="o" if (f // 4) % 2 else None)
        for k in range(3):
            t = (f + k * 5) % 15
            c.sprite(x + 6 + t // 3 + k * 4, 17 - t, ZZ, k=2 if k == 0 else 1)
    elif state == "happy":
        jump = [0, 3, 6, 7, 6, 3, 0, 0][f % 8]
        mascot(c, x, BY - jump, BIG, eyes="happy", arms="up" if jump > 2 else "side", mouth="smile", blush=True)
        for k in range(2):
            t = (f + k * 4) % 8
            c.sprite(x - 18 + k * 30, 12 - t, HEART, k=2 if k == 0 else 1)
    elif state == "eat":
        chew = f % 4 < 2
        mascot(c, x - 4, BY, BIG, eyes="happy" if chew else "normal", look=2, mouth="chomp" if chew else "o", arms="right_up")
        bites = min(3, f // 4)
        ck = [row[:5 - bites] + "." * bites for row in COOKIE]
        c.sprite(x + 10, BY - 16, ck, k=2)
        for k in range(f % 3):
            c.set(x + 10 - k * 2, BY - 2 - k, LBROWN)
    elif state == "dizzy":
        tilt = [-2, -1, 0, 1, 2, 1, 0, -1][f % 8]
        mascot(c, x, BY, BIG, eyes="spiral", mouth="wavy", tilt=tilt)
        for k in range(3):
            a = (f / 8.0) * 2 * math.pi + k * 2 * math.pi / 3
            c.sprite(x - 2 + round(math.cos(a) * 15), 9 + round(math.sin(a) * 3), STAR)
    elif state == "hungry":
        mascot(c, x, BY, BIG, eyes="sad", mouth="o" if f % 8 < 4 else None, arms="down")
        c.sprite(x - 1, 4, ["wwwwwwwwwwwww", "w...........w", "w...........w", "w...........w", "w...........w", "w...........w", "w...........w", "w...........w", "w...........w", "w...........w", "w...........w", "wwwwwwwwwwwww", "...w.........", "..w.........."])
        c.sprite(x + 1, 5, COOKIE, k=2)
    elif state == "dance":
        a = ["left_up", "right_up"][(f // 2) % 2]
        mascot(c, x + [0, 1, 0, -1][f % 4], BY - (f % 2), BIG, eyes="happy", arms=a, mouth="smile", step=1 + (f // 2) % 2)
        c.sprite(5 + (f % 4), 8 - (f % 3), NOTE, k=2); c.sprite(36 - (f % 4), 6 + (f % 3), NOTE)
    elif state == "work":
        m = mascot(c, x, BY, BIG, eyes="normal", look=[1, 2][(f // 3) % 2], arms="down")
        c.sprite(x - 10, BY - 9, LAPTOP, k=2)
        if f % 2:
            c.sprite(x + 14, 10 - (f % 6), ["k", "k", "w"][:1] if False else ["w.w", ".w.", "w.w"][: 1 + f % 3])
        for k in range(f % 4):
            c.set(x - 4 + k * 2, BY - 6, WHITE)
    elif state == "pet":
        mascot(c, x, BY, BIG, eyes="happy", blush=True, mouth="smile", squash=1 if f % 4 < 2 else 0)
        c.sprite(x - 5, 6 - (f % 4), HEART, k=2)
    return c


WHEEL_STATES = {"idle": 16, "walk_r": 4, "walk_l": 4, "sleep": 15, "happy": 8, "eat": 16, "dizzy": 8,
                "hungry": 8, "dance": 8, "work": 6, "pet": 8}


def tile_png(name, scale=6):
    import io
    buf = io.BytesIO()
    tile(name).image(scale).save(buf, "PNG")
    return buf.getvalue()


WALK_X = list(range(18, 31))   # zakres chodzenia srodka maskotki po kole


def export_wheel(outdir, scale=5):
    """Klatki kola dla wtyczki: <stan>_<n>.png (240x240, przezroczyste, maskotka na x=24),
    floor.png (tlo z podloga) i frames.json. Wtyczka sklada: floor + klatka przesunieta o (x-24)*scale."""
    import json, os
    os.makedirs(outdir, exist_ok=True)
    floor = Canvas(G)
    wheel_base(floor)
    floor.image(scale, bg=(0, 0, 0, 255)).save(os.path.join(outdir, "floor.png"), optimize=True)
    for state, n in WHEEL_STATES.items():
        for f in range(n):
            wheel_frame(state, f, 24, floor=False).image(scale).save(
                os.path.join(outdir, f"{state}_{f}.png"), optimize=True)
    json.dump({"states": WHEEL_STATES, "scale": scale, "walk_x": [WALK_X[0], WALK_X[-1]]},
              open(os.path.join(outdir, "frames.json"), "w"), indent=1)
    return WHEEL_STATES
