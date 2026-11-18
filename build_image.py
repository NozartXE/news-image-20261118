#!/usr/bin/env python3
"""Draw 'The Daily Edition — Wednesday 18 November 2026' (round 3).

A denser broadsheet front page that sums up the world news of
Wednesday 18 November 2026 in one 1024x1024 image: the proven round-2
form (masthead + full date, Gulf-escalation hero, three columns) plus
a schematic world-map panel with story pins on six continents, an
eight-number DAY IN NUMBERS strip and a sixteen-item wire band —
28 distinct story items in total.  Every element is drawn
deterministically with Pillow from the string constants below: no
randomness, no network, no external assets beyond system fonts.
Running this file rewrites entry.png next to it, byte for byte the
same on every run.  All facts come from the verified lists in
hidden_files/idea-funnel.md only.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- canvas
W = H = 1024
PAPER = (247, 242, 231)
INK = (24, 22, 20)
FADED = (92, 84, 72)
ACCENT = (156, 38, 24)
NAVY = (18, 38, 66)
GOLD = (198, 148, 42)
TAN = (236, 228, 208)
SEA = (206, 222, 232)
LAND = (104, 124, 100)
LAND_LINE = (70, 88, 66)

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
    """Dusk over the Gulf: a tanker at sea, Qeshm Island, a strike burst.

    Laid out from the scene height so the tanker, island and burst
    always stay above the caption strip at the bottom.
    """
    hh = y1 - y0
    sea_y = y0 + int(hh * 0.52)
    # sky: horizontal bands from deep dusk purple down to ember orange
    sky_top = (43, 32, 66)
    sky_mid = (148, 62, 44)
    sky_low = (232, 138, 62)
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
    sun_cx, sun_cy, sun_r = x0 + 110, sea_y - 18, 26
    draw.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
                 fill=(246, 196, 96))
    # sea
    draw.rectangle([x0, sea_y, x1, y1], fill=(26, 44, 66))
    for i, yy in enumerate(range(sea_y + 10, y1 - 30, 12)):
        off = 18 if i % 2 else 0
        for xx in range(x0 + 14 + off, x1 - 60, 92):
            draw.line([(xx, yy), (xx + 34, yy)], fill=(74, 104, 132), width=2)
    # Qeshm Island: a dark headland on the right
    draw.polygon([(x1 - 300, sea_y + 2), (x1 - 190, sea_y - 34),
                  (x1 - 90, sea_y - 20), (x1, sea_y - 6), (x1, sea_y + 2)],
                 fill=(30, 24, 26))
    # strike burst above the island: star of rays + core
    bx, by = x1 - 185, sea_y - 40
    for dx, dy in [(-34, 0), (34, 0), (0, -24), (0, 22), (-25, -18),
                   (25, -18), (-25, 16), (25, 16), (-38, -8), (38, 6)]:
        draw.line([(bx, by), (bx + dx, by + dy)], fill=(250, 214, 110), width=5)
    draw.ellipse([bx - 14, by - 11, bx + 14, by + 11], fill=(252, 232, 150))
    draw.ellipse([bx - 7, by - 6, bx + 7, by + 6], fill=(255, 250, 220))
    # smoke plume drifting sideways from the burst, kept inside the scene
    for i, (sx, sy, sr) in enumerate([(bx - 32, by - 10, 9), (bx - 54, by - 16, 11),
                                      (bx - 76, by - 20, 13)]):
        shade = 96 - i * 8
        draw.ellipse([sx - sr, sy - sr // 2, sx + sr, sy + sr // 2],
                     fill=(shade, shade - 6, shade - 2))
    # tanker silhouette on the left: long hull, three deck tanks, tower aft
    hx, hy = x0 + 140, sea_y + 10
    hull = [(hx, hy), (hx + 276, hy), (hx + 250, hy + 24), (hx + 24, hy + 24)]
    draw.polygon(hull, fill=(12, 12, 14))
    draw.rectangle([hx + 28, hy - 12, hx + 190, hy], fill=(12, 12, 14))   # deck line
    for tx in (hx + 48, hx + 94, hx + 140):
        draw.ellipse([tx, hy - 22, tx + 32, hy - 6], fill=(12, 12, 14))
    draw.rectangle([hx + 204, hy - 32, hx + 234, hy], fill=(12, 12, 14))  # bridge tower
    draw.rectangle([hx + 212, hy - 42, hx + 226, hy - 32], fill=(12, 12, 14))
    draw.line([(hx + 219, hy - 42), (hx + 219, hy - 56)], fill=(12, 12, 14), width=3)
    # two drones as small chevrons in the upper sky
    for cx, cy in [(x0 + 290, y0 + 26), (x0 + 360, y0 + 44)]:
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


# ---------------------------------------------------------------- world map
# Schematic continent outlines as (lon, lat) points, hand-drawn for this
# page.  Equirectangular projection: lon -180..180 across, lat 85..-55 down.
CONTINENTS = [
    [(-168, 66), (-150, 70), (-130, 71), (-110, 73), (-95, 80), (-85, 73),
     (-75, 72), (-65, 60), (-55, 52), (-60, 45), (-70, 42), (-75, 35),
     (-80, 32), (-81, 26), (-90, 21), (-95, 16), (-100, 16), (-105, 20),
     (-110, 24), (-117, 32), (-125, 40), (-125, 48), (-135, 58),
     (-150, 60), (-165, 60), (-168, 66)],                                    # N America
    [(-79, 9), (-72, 11), (-62, 10), (-55, 6), (-50, 0), (-44, -3),
     (-35, -8), (-38, -15), (-40, -22), (-48, -28), (-55, -34), (-62, -40),
     (-68, -50), (-70, -55), (-73, -50), (-73, -40), (-72, -30),
     (-75, -20), (-80, -12), (-81, -5), (-80, 0), (-79, 9)],                 # S America
    [(-17, 15), (-16, 20), (-10, 30), (-5, 35), (10, 37), (20, 32),
     (30, 31), (35, 28), (40, 20), (43, 12), (48, 11), (51, 10), (46, 5),
     (40, -5), (40, -15), (36, -22), (32, -28), (26, -34), (19, -35),
     (15, -30), (12, -18), (13, -10), (9, -1), (9, 4), (-8, 5),
     (-13, 8), (-17, 15)],                                                    # Africa
    [(-10, 36), (-9, 43), (-2, 48), (-4, 49), (0, 50), (3, 52), (5, 58),
     (8, 57), (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
     (30, 70), (35, 68), (40, 67), (45, 65), (40, 60), (35, 55), (30, 50),
     (28, 45), (23, 40), (19, 42), (12, 44), (8, 44), (3, 42), (-1, 37),
     (-6, 36), (-10, 36)],                                                    # Europe
    [(30, 70), (40, 68), (50, 70), (60, 70), (70, 72), (80, 73), (90, 75),
     (100, 77), (110, 76), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 70), (170, 67), (178, 65), (170, 60), (162, 58), (158, 52),
     (150, 45), (142, 40), (135, 35), (128, 33), (122, 30), (120, 22),
     (112, 15), (108, 10), (104, 8), (100, 10), (98, 15), (92, 16),
     (88, 22), (85, 20), (80, 13), (76, 8), (72, 20), (68, 23), (62, 25),
     (58, 26), (54, 26), (50, 28), (48, 30), (44, 29), (40, 32), (36, 36),
     (33, 38), (30, 40), (30, 45), (28, 50), (30, 55), (30, 62),
     (30, 70)],                                                               # Asia
    [(113, -22), (114, -30), (115, -35), (120, -34), (126, -32),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (145, -38), (150, -37), (153, -32), (153, -27), (150, -22),
     (146, -19), (142, -11), (137, -12), (132, -12), (126, -14),
     (122, -17), (117, -20), (113, -22)],                                     # Australia
]

# Story locations pinned on the map: Gulf, Kerch, Manila, Congo,
# Antalya, Cook Islands, Kemerovo, Alaska, Sudan, Yemen, Shenzhen, Gaza.
# The four eastern-Mediterranean / Gulf pins are nudged a few degrees
# apart so the cluster stays readable at this scale.
PINS = [(58, 24), (36.5, 45), (121, 14.6), (25, -2), (29, 33),
        (-160, -21), (86, 55.4), (-150, 64), (30, 13), (45, 15),
        (114, 22.5), (38, 28)]

# Continent labels, placed on the sea beside each landmass so no pin
# sits on a word; dark ink on the pale sea.
MAP_LABELS = [("N. AMERICA", -125, 45), ("S. AMERICA", -72, -38),
              ("EUROPE", -16, 52), ("AFRICA", 32, -38), ("ASIA", 110, 80),
              ("OCEANIA", 132, -38)]


def map_panel(draw, x0, y0, x1, y1):
    """Schematic world map with a pin per story region, six continents."""
    draw.rectangle([x0, y0, x1, y1], fill=TAN, outline=INK, width=2)
    centred(draw, (x0 + x1) // 2, y0 + 9, "THE WORLD TODAY",
            font(SANS_BOLD, 15))
    mx0, my0 = x0 + 8, y0 + 34
    mw, mh = (x1 - x0) - 16, 100
    draw.rectangle([mx0, my0, mx0 + mw, my0 + mh], fill=SEA, outline=INK, width=1)

    def proj(lon, lat):
        return (mx0 + (lon + 180) / 360 * mw,
                my0 + (85 - lat) / 140 * mh)

    for poly in CONTINENTS:
        draw.polygon([proj(lon, lat) for lon, lat in poly],
                     fill=LAND, outline=LAND_LINE)
    for name, lon, lat in MAP_LABELS:
        px, py = proj(lon, lat)
        centred(draw, int(px), int(py), name, font(SANS_BOLD, 9),
                fill=INK)
    for lon, lat in PINS:
        px, py = proj(lon, lat)
        r = 3
        draw.ellipse([px - r - 1, py - r - 1, px + r + 1, py + r + 1],
                     fill=PAPER)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=ACCENT)
    cy = my0 + mh + 8
    centred(draw, (x0 + x1) // 2, cy, "12 STORIES · 6 CONTINENTS",
            font(SANS_BOLD, 10))
    centred(draw, (x0 + x1) // 2, cy + 16, "GULF · KERCH · MANILA",
            font(SANS_BOLD, 10))
    centred(draw, (x0 + x1) // 2, cy + 31, "CONGO · ANTALYA · SUDAN",
            font(SANS_BOLD, 10))
    centred(draw, (x0 + x1) // 2, cy + 46, "COOK IS. · YEMEN · GAZA",
            font(SANS_BOLD, 10))


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
            "Iran drones at Bahrain & Kuwait  ·  Restricted zone: Chabahar to the Arabian Sea",
            font(SANS_BOLD, 16))
    y += 28
    hero_scene(d, M, y, R, y + 130)
    y += 130 + 9
    y = block(d, M, y,
              "Five tankers sunk — Kaviz, Charminar, Horizon 1, Riesco in the Gulf of Oman, "
              "Derya near Kharg. U.S. strikes an IRGC missile site on Qeshm Island.",
              font(SANS, 15), R - M, 20)
    y += 7
    d.line([(M, y), (R, y)], fill=INK, width=2)

    # ---- columns + world map ------------------------------------------
    top = y + 11
    row_h = 215
    map_x = R - 204
    col_gap = 16
    col_w = (map_x - M - col_gap - 2 * col_gap) // 3

    columns = [
        ("UKRAINE WAR", "KERCH BRIDGE HIT AGAIN — DAY 2", bridge_icon,
         "Ukraine struck the Kerch Bridge for a second day; part of the road "
         "span fell into the strait. Russia hit two bridges in return."),
        ("ASIA TOUR", "TRUMP OPENS TOUR IN MANILA", plane_icon,
         "Trump opened his Asia tour in Manila with the Philippines and Quad "
         "partners, then China for a first trilateral with Xi and Putin."),
        ("HEALTH", "EBOLA CASES DOUBLE IN CONGO", virus_icon,
         "The Ebola outbreak in DR Congo has more than doubled in three "
         "months: over 11,000 cases and 5,400 deaths (UN)."),
    ]
    for i, (kicker, head, icon, body) in enumerate(columns):
        cx = M + i * (col_w + col_gap)
        d.text((cx, top), kicker, font=font(SANS_BOLD, 13), fill=ACCENT)
        yy = block(d, cx, top + 19, head, font(SERIF_BOLD, 18), col_w, 22)
        icon(d, cx + 6, yy + 2)
        block(d, cx, yy + 58, body, font(SANS, 14), col_w, 18)
        if i < 2:
            vx = cx + col_w + col_gap // 2
            d.line([(vx, top), (vx, top + row_h)], fill=FADED, width=1)

    map_panel(d, map_x, top, R, top + row_h)

    # ---- day in numbers strip ------------------------------------------
    ny = top + row_h + 8
    strip_h = 54
    d.rectangle([M, ny, R, ny + strip_h], fill=TAN, outline=INK, width=2)
    numbers = [
        ("5", "tankers sunk"),
        ("6", "drones over Bahrain"),
        ("11,000", "Ebola cases"),
        ("144", "COP31 items disputed"),
        ("19", "dead in Siberia crash"),
        ("2,230", "civilians killed, Sudan"),
        ("60", "Houthi targets hit"),
        ("56", "Democrat Senate seats"),
    ]
    head_w = 110
    cell_w = (R - M - head_w) / 8
    d.text((M + 8, ny + 11), "DAY IN", font=font(SANS_BOLD, 11), fill=INK)
    d.text((M + 8, ny + 25), "NUMBERS", font=font(SANS_BOLD, 11), fill=INK)
    for i, (big, label) in enumerate(numbers):
        cx = M + head_w + i * cell_w
        if i:
            d.line([(cx - 2, ny + 6), (cx - 2, ny + strip_h - 6)],
                   fill=FADED, width=1)
        d.text((cx + 6, ny + 6), big, font=font(SERIF_BOLD, 17), fill=ACCENT)
        block(d, cx + 6, ny + 28, label, font(SANS, 10), cell_w - 12, 12)

    # ---- wire band ------------------------------------------------------
    wy = ny + strip_h + 8
    d.rectangle([M, wy, R, H - 30], fill=NAVY)
    d.text((M + 16, wy + 9), "THE WIRE — AROUND THE WORLD IN A DAY",
           font=font(SANS_BOLD, 16), fill=(246, 240, 224))
    right = "16 STORIES · 6 CONTINENTS"
    d.text((R - 16 - text_w(d, right, font(SANS_BOLD, 12)), wy + 12), right,
           font=font(SANS_BOLD, 12), fill=GOLD)
    wire = [
        "CYCLONE XAVIER: Cat 5 storm hits Northern Cook Islands",
        "COP31 ANTALYA: climate talks enter decisive phase, end Friday",
        "SIBERIA: Russian military plane crashes in Kemerovo, 19 dead",
        "NORTH KOREA: ballistic missiles fired after U.S.-led drills",
        "ALASKA: Democrat Mary Peltola wins the state's Senate seat",
        "THE HAGUE: World Court to rule on Myanmar genocide case",
        "HOLLYWOOD: Robert Pattinson named the new James Bond",
        "SHENZHEN: Trump heads to China for first trilateral with Xi, Putin",
        "U.S. OUTAGES: Microsoft, FAA, JPMorgan Chase and NSA hit",
        "GAZA: Board of Peace warns the ceasefire may collapse",
        "WASHINGTON: Trump takes Iran dirty-bomb report seriously",
        "SUDAN: UN: 2,230 civilians killed in 2026, mostly by drones",
        "YEMEN: Saudi-led coalition hits 60 Houthi targets, incl. Sanaa",
        "FLIGHTS: flydubai cancellations to Nov 27, Etihad to Nov 30",
        "CARRIERS: USS Roosevelt and George Washington in Arabian Sea",
        "TEHRAN: Iran claims Hormuz hits; missiles at Al-Azraq, Jordan",
    ]
    cell_w = (R - M - 32) // 2
    for i, item in enumerate(wire):
        cx = M + 16 + (i % 2) * cell_w
        cy = wy + 38 + (i // 2) * 16
        d.rectangle([cx, cy + 4, cx + 7, cy + 11], fill=GOLD)
        d.text((cx + 14, cy), item, font=font(SANS_BOLD, 12),
               fill=(240, 238, 228))

    return img


def main():
    out = Path(__file__).with_name("entry.png")
    build().save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
