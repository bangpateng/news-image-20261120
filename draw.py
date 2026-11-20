#!/usr/bin/env python3
"""Draw the 20 November 2026 front page: 'THE WORLD IN ONE DAY'.

Fresh renderer written for the news-image-20261120 entry. It paints a
1024x1024 newspaper front page with PIL: a masthead naming the day, a
3x2 grid of six stories (each with a tag chip, a flat illustration, a
headline and a short body), a gold-bordered lead story, and a bottom
news ticker. All text comes from literal strings in this file, so no
glyph is ever garbled. Run: python3 draw.py  ->  entry.png
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

PAPER = (247, 242, 231)
INK = (26, 26, 46)
NAVY = (20, 50, 79)
NAVY_SOFT = (31, 74, 110)
GOLD = (201, 162, 39)
GOLD_SOFT = (232, 203, 110)
RED = (179, 57, 46)
TEAL = (31, 111, 107)
SKY = (122, 178, 205)
SKY_DEEP = (58, 122, 158)
SAND = (226, 205, 158)
GREEN = (74, 124, 74)
GREY = (90, 90, 100)
CARD = (255, 253, 247)
CHIP_TEXT = (255, 255, 255)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Wrap text; if it overflows max_lines, trim with an ellipsis."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    last = lines[-1]
    while last and draw.textlength(last + " ...", font=fnt) > max_w:
        last = last.rsplit(" ", 1)[0] if " " in last else ""
    lines[-1] = (last + " ...").strip()
    return lines


def text_center(draw, cx, y, s, fnt, fill):
    draw.text((cx - draw.textlength(s, font=fnt) / 2, y), s, font=fnt, fill=fill)


# ---------------------------------------------------------------- stories
# (tag, chip colour, headline, body, art key)
STORIES = [
    ("WEATHER", RED,
     "AKVAN HITS INDIA'S EAST COAST",
     "Cyclone Akvan comes ashore near Gopalpur at noon. About 300,000 evacuated; 423 rescue teams ready; 69 trains cancelled.",
     "cyclone"),
    ("MARKETS", NAVY,
     "ASIAN SHARES IN WORST WEEK SINCE 2020",
     "Nikkei -4.1%, KOSPI -4.7%. MSCI Asia-Pacific falls 2.5% for a sixth straight loss as gloom over the AI trade deepens.",
     "chart"),
    ("TAIWAN", TEAL,
     "TAIWAN MOVES TO STEADY ITS STOCKS",
     "Five measures take effect today: the short-sale cap falls to 1% after the Taiex lost 5,248 points in three days.",
     "shield"),
    ("WHITE HOUSE", NAVY_SOFT,
     "TRUMP BACK FROM CHINA, TO FACE PRESS",
     "The president holds a noon White House news conference on his China trip and trade deals with Thailand and the Philippines.",
     "podium"),
    ("EUROPE", (90, 60, 120),
     "UK-EU SUMMIT GOES DOWN TO THE WIRE",
     "Burnham meets EU leaders in Brussels today. Food, energy and youth-mobility deals are at stake - and he says he may walk away.",
     "flags"),
    ("MIDDLE EAST", GREEN,
     "FOUR NATIONS URGE GAZA AID ACCESS",
     "Australia, Canada, Italy and Britain jointly call on Israel to open aid routes as floods add to the suffering in Gaza.",
     "aid"),
]

TICKER = ("GOLD: STEEPEST WEEKLY FALL SINCE MARCH  ·  DOLLAR RALLIES  ·  "
          "OIL EDGES HIGHER")


# ---------------------------------------------------------------- art
def art_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(178, 214, 230))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(196, 178, 130))  # coast
    cx, cy = x + w // 2, y + h // 2 - 8
    # staggered arcs read as a swirl, not a target
    for r, a0, a1 in ((62, 20, 300), (46, 140, 60), (30, 200, 120),
                      (16, 320, 240)):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=a0, end=a1,
              fill=(255, 255, 255), width=7)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=NAVY)
    for dx, dy in ((-78, -18), (-58, 22), (66, -26), (72, 18)):
        d.line([cx + dx, cy + dy, cx + dx + 16, cy + dy + 6],
               fill=(255, 255, 255), width=4)


def art_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 238, 244))
    base = y + h - 18
    bars = [0.62, 0.78, 0.55, 0.88, 0.66, 0.95, 0.42]
    bw = w // len(bars)
    for i, v in enumerate(bars):
        bh = int((h - 34) * v)
        bx = x + 10 + i * bw
        d.rectangle([bx, base - bh, bx + bw - 12, base], fill=RED)
    pts = [(x + 10 + i * bw + (bw - 12) // 2,
            base - int((h - 34) * v) - 8) for i, v in enumerate(bars)]
    d.line(pts, fill=NAVY, width=4, joint="curve")
    for px, py in pts:
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=NAVY)
    label = "-4.1%  -4.7%"
    lf = font(SANS_B, 20)
    lw = d.textlength(label, font=lf) + 16
    d.rounded_rectangle([x + 8, y + 6, x + 8 + lw, y + 32], radius=6,
                        fill=(255, 255, 255))
    d.text((x + 16, y + 8), label, font=lf, fill=RED)


def art_shield(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 232, 226))
    cx, cy = x + w // 2, y + h // 2
    pts = [(cx, cy - 52), (cx + 52, cy - 30), (cx + 52, cy + 8),
           (cx, cy + 56), (cx - 52, cy + 8), (cx - 52, cy - 30)]
    d.polygon(pts, fill=TEAL, outline=(255, 255, 255))
    d.line([(cx - 24, cy + 2), (cx - 6, cy + 20), (cx + 28, cy - 22)],
           fill=(255, 255, 255), width=7, joint="curve")


def art_podium(d, x, y, w, h):
    # Simple White House silhouette: sky, pediment, thin columns, podium.
    d.rectangle([x, y, x + w, y + h], fill=(214, 226, 238))
    bx, by, bw, bh = x + 56, y + 40, w - 112, h - 66
    d.polygon([(bx + bw // 2 - 30, by - 2), (bx + bw // 2 + 30, by - 2),
               (bx + bw // 2, by - 22)], fill=(255, 255, 255))  # pediment
    d.rectangle([bx, by, bx + bw, by + 12], fill=(255, 255, 255))  # entablature
    for i in range(4):
        cx = bx + 18 + i * ((bw - 36) // 3)
        d.rectangle([cx - 6, by + 12, cx + 6, by + bh - 22], fill=(255, 255, 255))
    d.rectangle([bx, by + bh - 22, bx + bw, by + bh], fill=(255, 255, 255))
    d.rectangle([bx + bw // 2 - 12, by + bh - 52, bx + bw // 2 + 12, by + bh - 22],
                fill=NAVY)  # door
    d.rectangle([x + w // 2 - 36, y + h - 34, x + w // 2 + 36, y + h - 6],
                fill=NAVY)  # podium
    d.rectangle([x + w // 2 - 36, y + h - 34, x + w // 2 + 36, y + h - 26],
                fill=GOLD)
    d.text((x + 12, y + 8), "12 NOON", font=font(SANS_B, 18), fill=NAVY)


def art_flags(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 232, 240))
    # UK flag (left) and EU flag (right), flat and simple.
    fx, fy, fw, fh = x + 18, y + 26, 118, 72
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=(18, 46, 110))
    d.line([(fx, fy), (fx + fw, fy + fh)], fill=(255, 255, 255), width=10)
    d.line([(fx, fy + fh), (fx + fw, fy)], fill=(255, 255, 255), width=10)
    d.rectangle([fx, fy + fh // 2 - 10, fx + fw, fy + fh // 2 + 10],
                fill=(255, 255, 255))
    d.rectangle([fx + fw // 2 - 10, fy, fx + fw // 2 + 10, fy + fh],
                fill=(255, 255, 255))
    d.rectangle([fx, fy + fh // 2 - 5, fx + fw, fy + fh // 2 + 5], fill=RED)
    d.rectangle([fx + fw // 2 - 5, fy, fx + fw // 2 + 5, fy + fh], fill=RED)
    ex, ey, ew, eh = x + w - 136, y + 26, 118, 72
    d.rectangle([ex, ey, ex + ew, ey + eh], fill=(0, 51, 153))
    import math
    for k in range(12):
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx = ex + ew // 2 + int(26 * math.cos(a))
        sy = ey + eh // 2 + int(22 * math.sin(a))
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 204, 0))
    d.text((x + 14, y + h - 32), "BRUSSELS TODAY", font=font(SANS_B, 18),
           fill=NAVY)


def art_aid(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 234, 220))
    # stacked aid boxes with a cross, rain lines above
    d.rectangle([x + 52, y + 62, x + 52 + 74, y + 62 + 52], fill=(214, 178, 110))
    d.rectangle([x + 52 + 84, y + 62, x + 52 + 84 + 74, y + 62 + 52],
                fill=(196, 160, 96))
    d.rectangle([x + 52 + 42, y + 8, x + 52 + 42 + 74, y + 8 + 52],
                fill=(226, 196, 130))
    for bx, by in ((x + 52, y + 62), (x + 52 + 84, y + 62),
                   (x + 52 + 42, y + 8)):
        d.rectangle([bx + 30, by + 8, bx + 44, by + 44], fill=(255, 255, 255))
        d.rectangle([bx + 15, by + 19, bx + 59, by + 33], fill=(255, 255, 255))
    for rx in range(x + 24, x + w - 20, 34):
        d.line([rx, y + 118, rx - 8, y + 138], fill=SKY_DEEP, width=4)


ART = {"cyclone": art_cyclone, "chart": art_chart, "shield": art_shield,
       "podium": art_podium, "flags": art_flags, "aid": art_aid}


# ---------------------------------------------------------------- page
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead
    d.rectangle([0, 0, W, 118], fill=NAVY)
    d.rectangle([0, 118, W, 124], fill=GOLD)
    text_center(d, W // 2, 16, "THE WORLD IN ONE DAY",
                font(SERIF_B, 58), (255, 255, 255))
    text_center(d, W // 2, 82, "FRIDAY  ·  20 NOVEMBER 2026",
                font(SANS_B, 26), GOLD_SOFT)
    d.line([40, 142, W - 40, 142], fill=INK, width=2)
    text_center(d, W // 2, 150,
                "SIX STORIES FROM AROUND THE WORLD  —  ALL FROM TODAY",
                font(SANS_B, 19), GREY)

    # Grid: 3 columns x 2 rows
    gx, gy = 28, 182
    cw, chh = 308, 372
    gapx, gapy = 16, 16
    head_f = font(SERIF_B, 25)
    body_f = font(SANS, 16)
    chip_f = font(SANS_B, 16)

    for i, (tag, chip_col, headline, body, art) in enumerate(STORIES):
        col, row = i % 3, i // 3
        x = gx + col * (cw + gapx)
        y = gy + row * (chh + gapy)
        lead = (i == 0)
        d.rectangle([x, y, x + cw, y + chh], fill=CARD,
                    outline=GOLD if lead else (200, 192, 172),
                    width=5 if lead else 2)
        # illustration band
        ax, ay, aw, ah = x + 10, y + 10, cw - 20, 132
        ART[art](d, ax, ay, aw, ah)
        # tag chip
        chip_w = d.textlength(tag, font=chip_f) + 22
        cy = y + 152
        d.rounded_rectangle([x + 12, cy, x + 12 + chip_w, cy + 26], radius=13,
                            fill=chip_col)
        d.text((x + 23, cy + 4), tag, font=chip_f, fill=CHIP_TEXT)
        if lead:
            lw = d.textlength("LEAD", font=chip_f) + 22
            d.rounded_rectangle([x + cw - 14 - lw, cy, x + cw - 14, cy + 26],
                                radius=13, fill=GOLD)
            d.text((x + cw - 3 - lw, cy + 4), "LEAD", font=chip_f, fill=INK)
        # headline
        hl = fit_lines(d, headline, head_f, cw - 24, 3)
        hy = y + 186
        for line in hl:
            d.text((x + 12, hy), line, font=head_f, fill=INK)
            hy += 30
        # body
        bl = fit_lines(d, body, body_f, cw - 24, 4)
        by = hy + 6
        for line in bl:
            d.text((x + 12, by), line, font=body_f, fill=(52, 52, 64))
            by += 21
        # hard check: no text may cross the card's inner bottom edge
        if by - 21 + 16 > y + chh - 8:
            raise SystemExit(
                f"OVERFLOW in story {i + 1} ({tag}): text ends at "
                f"{by - 5}, card ends at {y + chh}")
        if "..." in (bl[-1] if bl else ""):
            raise SystemExit(f"TRUNCATED body in story {i + 1} ({tag}): {bl}")

    # Ticker
    ty = H - 56
    d.rectangle([0, ty, W, H], fill=INK)
    tf = font(SANS_B, 21)
    while d.textlength(TICKER, font=tf) > W - 24 and tf.size > 10:
        tf = font(SANS_B, tf.size - 1)
    if d.textlength(TICKER, font=tf) > W - 24:
        raise SystemExit("ticker still too wide at minimum size")
    d.text(((W - d.textlength(TICKER, font=tf)) / 2, ty + 15), TICKER,
           font=tf, fill=(255, 255, 255))
    # source line just above the ticker
    sf = font(SANS, 14)
    text_center(d, W // 2, H - 78,
                "Sources: IMD · Reuters · Taiwan FSC · White House · PA — events of Friday 20 November 2026",
                sf, GREY)

    img.save(OUT, optimize=True)
    print(f"wrote {OUT} {W}x{H}")


if __name__ == "__main__":
    main()
