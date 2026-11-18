#!/usr/bin/env python3
"""Draw 'The Daily Edition — Wednesday 18 November 2026'.

A single-page broadsheet front page that sums up the world news of
Wednesday 18 November 2026 in one 1024x1024 image.  Every element is
drawn deterministically with Pillow from the string constants below:
no randomness, no network, no external assets beyond system fonts.
Running this file rewrites entry.png next to it, byte for byte the
same on every run.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- canvas
W = H = 1024
PAPER = (247, 242, 231)
INK = (24, 22, 20)
FADED = (92, 84, 72)
RULE = (24, 22, 20)
ACCENT = (156, 38, 24)
NAVY = (18, 38, 66)
GOLD = (198, 148, 42)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF_BOLD = str(FONT_DIR / "DejaVuSerif-Bold.ttf")
SERIF = str(FONT_DIR / "DejaVuSerif.ttf")
SANS = str(FONT_DIR / "DejaVuSans.ttf")
SANS_BOLD = str(FONT_DIR / "DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, fnt):
    box = draw.textbbox((0, 0), s, font=fnt)
    return box[2] - box[0]


def centred(draw, cx, y, s, fnt, fill=INK):
    draw.text((cx - text_w(draw, s, fnt) / 2, y), s, font=fnt, fill=fill)


def wrap(draw, s, fnt, width):
    """Greedy word wrap measured against the real font metrics."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(draw, x, y, s, fnt, width, leading, fill=INK):
    """Draw wrapped text, return the y just below it."""
    for line in wrap(draw, s, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- scenes
def hero_scene(draw, x0, y0, x1, y1):
    """Dusk over the Gulf: a tanker at sea, Qeshm Island, a strike burst."""
    # sky: horizontal bands from deep dusk purple down to ember orange
    sky_top = (43, 32, 66)
    sky_mid = (148, 62, 44)
    sky_low = (232, 138, 62)
    sea_y = y0 + int((y1 - y0) * 0.68)
    for yy in range(y0, sea_y):
        t = (yy - y0) / max(1, sea_y - y0)
        if t < 0.55:
            k = t / 0.55
            col = tuple(int(sky_top[i] + (sky_mid[i] - sky_top[i]) * k) for i in range(3))
        else:
            k = (t - 0.55) / 0.45
            col = tuple(int(sky_mid[i] + (sky_low[i] - sky_mid[i]) * k) for i in range(3))
        draw.line([(x0, yy), (x1, yy)], fill=col)
    # sun disc low on the horizon
    sun_cx, sun_cy, sun_r = x0 + 120, sea_y - 26, 34
    draw.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
                 fill=(246, 196, 96))
    # sea
    draw.rectangle([x0, sea_y, x1, y1], fill=(26, 44, 66))
    for i, yy in enumerate(range(sea_y + 12, y1 - 6, 14)):
        off = 18 if i % 2 else 0
        for xx in range(x0 + 14 + off, x1 - 60, 92):
            draw.line([(xx, yy), (xx + 34, yy)], fill=(74, 104, 132), width=2)
    # Qeshm Island: a dark headland on the right
    draw.polygon([(x1 - 330, sea_y + 4), (x1 - 210, sea_y - 52),
                  (x1 - 96, sea_y - 30), (x1, sea_y - 8), (x1, sea_y + 4)],
                 fill=(30, 24, 26))
    # strike burst above the island: star of rays + core
    bx, by = x1 - 205, sea_y - 62
    for dx, dy in [(-46, 0), (46, 0), (0, -34), (0, 30), (-34, -25),
                   (34, -25), (-34, 22), (34, 22), (-52, -10), (52, 8)]:
        draw.line([(bx, by), (bx + dx, by + dy)], fill=(250, 214, 110), width=5)
    draw.ellipse([bx - 19, by - 15, bx + 19, by + 15], fill=(252, 232, 150))
    draw.ellipse([bx - 10, by - 8, bx + 10, by + 8], fill=(255, 250, 220))
    # smoke plume drifting sideways from the burst, kept inside the scene
    for i, (sx, sy, sr) in enumerate([(bx - 44, by - 16, 12), (bx - 76, by - 28, 15),
                                      (bx - 112, by - 36, 18)]):
        shade = 96 - i * 8
        draw.ellipse([sx - sr, sy - sr // 2, sx + sr, sy + sr // 2],
                     fill=(shade, shade - 6, shade - 2))
    # tanker silhouette on the left: long hull, three deck tanks, tower aft
    hx, hy = x0 + 150, sea_y + 20
    hull = [(hx, hy), (hx + 276, hy), (hx + 250, hy + 24), (hx + 24, hy + 24)]
    draw.polygon(hull, fill=(12, 12, 14))
    draw.rectangle([hx + 28, hy - 12, hx + 190, hy], fill=(12, 12, 14))   # deck line
    for tx in (hx + 48, hx + 94, hx + 140):
        draw.ellipse([tx, hy - 22, tx + 32, hy - 6], fill=(12, 12, 14))
    draw.rectangle([hx + 204, hy - 32, hx + 234, hy], fill=(12, 12, 14))  # bridge tower
    draw.rectangle([hx + 212, hy - 42, hx + 226, hy - 32], fill=(12, 12, 14))
    draw.line([(hx + 219, hy - 42), (hx + 219, hy - 56)], fill=(12, 12, 14), width=3)
    draw.line([(hx + 60, hy + 30), (hx + 220, hy + 30)], fill=(74, 104, 132), width=2)
    # two drones as small chevrons in the upper sky
    for cx, cy in [(x0 + 300, y0 + 34), (x0 + 372, y0 + 56)]:
        draw.polygon([(cx - 17, cy + 6), (cx, cy - 7), (cx + 17, cy + 6),
                      (cx + 5, cy + 6), (cx, cy + 1), (cx - 5, cy + 6)],
                     fill=(16, 14, 18))
    # caption strip inside the scene
    draw.rectangle([x0, y1 - 26, x1, y1], fill=(14, 14, 16))
    centred(draw, (x0 + x1) // 2, y1 - 21,
            "THE GULF AT DUSK — TANKER, QESHM ISLAND AND THE STRIKE",
            font(SANS_BOLD, 14), fill=(238, 232, 218))


def bridge_icon(draw, x, y):
    """A simple suspension span with one section dropped."""
    draw.line([(x, y + 34), (x + 62, y + 34)], fill=NAVY, width=4)
    draw.line([(x + 84, y + 44), (x + 150, y + 30)], fill=NAVY, width=4)
    for tx in (x + 14, x + 128):
        draw.line([(tx, y), (tx, y + 46)], fill=NAVY, width=4)
    draw.line([(x, y + 8), (x + 150, y + 2)], fill=NAVY, width=2)
    draw.line([(x + 92, y + 44), (x + 118, y + 53)], fill=ACCENT, width=4)


def plane_icon(draw, x, y):
    """A jet in profile, nose to the right."""
    draw.polygon([(x, y + 26), (x + 34, y + 18), (x + 108, y + 16),
                  (x + 138, y + 22), (x + 108, y + 30), (x + 30, y + 32)],
                 fill=NAVY)
    draw.polygon([(x + 58, y + 18), (x + 84, y + 2), (x + 98, y + 2),
                  (x + 84, y + 18)], fill=NAVY)
    draw.polygon([(x + 8, y + 24), (x - 2, y + 8), (x + 10, y + 8),
                  (x + 20, y + 22)], fill=NAVY)
    for wx in range(x + 44, x + 104, 14):
        draw.ellipse([wx, y + 21, wx + 6, y + 26], fill=PAPER)


def virus_icon(draw, x, y):
    """A spiked round cell beside a medical cross."""
    cx, cy, r = x + 34, y + 28, 17
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-0.7, -0.7),
                   (0.7, -0.7), (-0.7, 0.7), (0.7, 0.7)]:
        ex, ey = cx + int(dx * (r + 8)), cy + int(dy * (r + 8))
        draw.line([(cx, cy), (ex, ey)], fill=ACCENT, width=3)
        draw.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=ACCENT)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ACCENT, width=3)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=ACCENT)
    px, py = x + 96, y + 12
    draw.rectangle([px + 10, py, px + 22, py + 34], fill=(30, 110, 62))
    draw.rectangle([px, py + 10, px + 32, py + 22], fill=(30, 110, 62))


# ---------------------------------------------------------------- page
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 34                      # page margin
    R = W - M                   # right edge of the text area

    # outer frame
    d.rectangle([14, 14, W - 14, H - 14], outline=INK, width=3)
    d.rectangle([20, 20, W - 20, H - 20], outline=INK, width=1)

    # ---- masthead ------------------------------------------------------
    y = 28
    centred(d, W // 2, y, "THE DAILY EDITION", font(SERIF_BOLD, 58))
    y += 74
    d.line([(M, y), (R, y)], fill=INK, width=3)
    d.line([(M, y + 5), (R, y + 5)], fill=INK, width=1)
    y += 11
    d.rectangle([M, y, R, y + 48], fill=INK)
    centred(d, W // 2, y + 6, "WEDNESDAY 18 NOVEMBER 2026",
            font(SANS_BOLD, 35), fill=(250, 247, 238))
    y += 58
    centred(d, W // 2, y, "One day's world news in one image  ·  No. 322  ·  Price: the truth",
            font(SERIF, 15), fill=FADED)
    y += 27
    d.line([(M, y), (R, y)], fill=INK, width=2)

    # ---- hero ----------------------------------------------------------
    y += 10
    centred(d, W // 2, y, "GULF ERUPTS: U.S. STRIKES IRAN",
            font(SERIF_BOLD, 41), fill=ACCENT)
    y += 52
    centred(d, W // 2, y, "MISSILE SITE ON QESHM ISLAND",
            font(SERIF_BOLD, 41), fill=ACCENT)
    y += 56
    centred(d, W // 2, y,
            "Five tankers destroyed · Iran drones at Bahrain & Kuwait · Hormuz restricted",
            font(SANS_BOLD, 16))
    y += 28
    hero_scene(d, M, y, R, y + 160)
    y += 160 + 9
    y = block(d, M, y,
              "Washington confirmed the strike on an IRGC missile site on Qeshm Island. "
              "Tehran claims hits on ships near Hormuz and missiles aimed at a U.S. base in "
              "Jordan, and declares a restricted zone from Chabahar to the Arabian Sea.",
              font(SANS, 15), R - M, 20)
    y += 7
    d.line([(M, y), (R, y)], fill=INK, width=2)

    # ---- columns + numbers sidebar ------------------------------------
    top = y + 11
    side_w = 204
    side_x = R - side_w
    col_gap = 16
    col_w = (side_x - M - 2 * col_gap - 12) // 3
    col_h = 246

    columns = [
        ("UKRAINE WAR", "KERCH BRIDGE HIT AGAIN — DAY 2", bridge_icon,
         "Ukraine struck the Kerch Bridge for a second day; part of the road "
         "span fell into the strait. Russia hit two bridges in return."),
        ("ASIA TOUR", "TRUMP OPENS TOUR IN MANILA", plane_icon,
         "President Trump arrived in Manila to meet the Philippines and Quad "
         "partners as his Asia tour opens. China is the next stop."),
        ("HEALTH", "EBOLA CASES DOUBLE IN CONGO", virus_icon,
         "The Ebola outbreak in DR Congo has more than doubled in three "
         "months: over 11,000 cases and 5,400 deaths (UN)."),
    ]
    for i, (kicker, head, icon, body) in enumerate(columns):
        cx = M + i * (col_w + col_gap)
        d.text((cx, top), kicker, font=font(SANS_BOLD, 13), fill=ACCENT)
        yy = block(d, cx, top + 19, head, font(SERIF_BOLD, 18), col_w, 22)
        icon(d, cx + 6, yy + 2)
        yy += 58
        block(d, cx, yy, body, font(SANS, 14), col_w, 19)
        if i < 2:
            vx = cx + col_w + col_gap // 2
            d.line([(vx, top), (vx, top + col_h)], fill=FADED, width=1)

    # sidebar: the day in numbers
    d.rectangle([side_x, top, R, top + col_h], fill=(236, 228, 208),
                outline=INK, width=2)
    centred(d, (side_x + R) // 2, top + 9, "DAY IN NUMBERS",
            font(SANS_BOLD, 16))
    d.line([(side_x + 12, top + 36), (R - 12, top + 36)], fill=INK, width=1)
    numbers = [
        ("5", "tankers destroyed in the Gulf"),
        ("6", "drones downed over Bahrain"),
        ("11,000", "Ebola cases in DR Congo"),
        ("144", "COP31 items still disputed"),
        ("19", "dead in Siberia plane crash"),
    ]
    ny = top + 43
    for big, label in numbers:
        d.text((side_x + 13, ny), big, font=font(SERIF_BOLD, 21), fill=ACCENT)
        block(d, side_x + 13, ny + 26, label, font(SANS, 12), side_w - 26, 15)
        ny += 40

    # ---- wire band ------------------------------------------------------
    wy = top + col_h + 12
    d.rectangle([M, wy, R, H - 30], fill=NAVY)
    d.text((M + 16, wy + 9), "THE WIRE — AROUND THE WORLD IN A DAY",
           font=font(SANS_BOLD, 16), fill=(246, 240, 224))
    wire = [
        "CYCLONE XAVIER: Category 5 storm hits Northern Cook Islands",
        "COP31 ANTALYA: climate talks enter decisive phase, end Friday",
        "NORTH KOREA: ballistic missiles fired after U.S.-led drills",
        "ALASKA: Democrat Mary Peltola wins the state's Senate seat",
        "THE HAGUE: World Court to rule on Myanmar genocide case",
        "HOLLYWOOD: Robert Pattinson named the new James Bond",
    ]
    cell_w = (R - M - 48) // 3
    for i, item in enumerate(wire):
        cx = M + 16 + (i % 3) * (cell_w + 8)
        cy = wy + 42 + (i // 3) * 56
        d.rectangle([cx, cy + 4, cx + 7, cy + 11], fill=GOLD)
        block(d, cx + 14, cy, item, font(SANS_BOLD, 12), cell_w - 14, 16,
              fill=(240, 238, 228))
    centred(d, W // 2, H - 58, "—  END OF THE DAY'S EDITION  —",
            font(SANS_BOLD, 12), fill=GOLD)

    return img


def main():
    out = Path(__file__).with_name("entry.png")
    build().save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
