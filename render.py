#!/usr/bin/env python3
"""Render entry.png for news-image-20261119 — agent 2 (noble-robin-77).

Layout "MAP-LED ATLAS": light masthead, world map FIRST under the masthead,
three hero panels below the map, 3x3 secondary grid, briefs in THREE columns.
36 stories, all reported on Thursday 19 November 2026. Flat vector original
drawings, PIL only, fully deterministic (same bytes every run).
"""
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 12                      # page margin
CW = W - 2 * M              # content width = 1000

PAPER = (247, 243, 232)     # warm cream #F7F3E8
INK = (17, 17, 17)          # near-black
RED = (179, 39, 30)         # brick red #B3271E
NAVY = (27, 42, 74)         # #1B2A4A
GOLD = (201, 162, 39)       # #C9A227
GREY = (85, 85, 85)
MAP_BG = (234, 242, 236)    # pale mint #EAF2EC
MAP_DOT = (90, 107, 93)     # dark grey-green #5A6B5D
SKY = (220, 232, 238)       # pale blue sky wash
TINTS = [(220, 232, 238), (221, 235, 224), (228, 222, 239),
         (242, 232, 201), (240, 220, 216), (213, 232, 230)]

DJV = "/usr/share/fonts/truetype/dejavu/"
NOTO = "/usr/share/fonts/truetype/noto/"


def font(path, size):
    return ImageFont.truetype(path, size)


def serif_b(size):
    return font(DJV + "DejaVuSerif-Bold.ttf", size)


def serif(size):
    return font(DJV + "DejaVuSerif.ttf", size)


def serif_i(size):
    return font(NOTO + "NotoSerif-Italic.ttf", size)


def sans_b(size):
    return font(DJV + "DejaVuSans-Bold.ttf", size)


def sans(size):
    return font(DJV + "DejaVuSans.ttf", size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def tracked(draw, xy, text, fnt, fill, track=1):
    """Draw ALL-CAPS text with extra tracking (px between chars)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + track
    return x


def tracked_width(draw, text, fnt, track=1):
    w = 0
    for ch in text:
        w += draw.textlength(ch, font=fnt) + track
    return w - track if text else 0


def num_circle(draw, cx, cy, n, r=9):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    f = sans_b(11 if len(str(n)) < 2 else 10)
    tw = draw.textlength(str(n), font=f)
    th = f.getbbox(str(n))[3]
    draw.text((cx - tw / 2, cy - th / 2 - 1), str(n), font=f, fill=(255, 255, 255))


def kicker_line(draw, x, y, num, text):
    """Numbered red circle + red caps kicker; returns y after the line."""
    num_circle(draw, x + 9, y + 8, num)
    tracked(draw, (x + 23, y + 3), text, sans_b(10), RED, track=1)
    return y + 18


# ---------------------------------------------------------------- world map
# Simplified continent polygons (lon, lat). Coarse but geographically honest:
# pins are projected with the same equirectangular mapping, so a pin always
# sits on the right continent.
POLYS = [
    # North America
    [(-168, 66), (-155, 71), (-140, 70), (-128, 71), (-115, 73), (-100, 73),
     (-90, 74), (-82, 73), (-80, 72), (-76, 70), (-72, 62), (-65, 60),
     (-60, 55), (-55, 52), (-60, 47), (-65, 44), (-70, 42), (-74, 39),
     (-76, 35), (-80, 32), (-81, 26), (-84, 30), (-88, 29), (-92, 29),
     (-97, 26), (-97, 22), (-94, 18), (-90, 16), (-86, 13), (-83, 9),
     (-80, 8), (-78, 7), (-82, 9), (-86, 12), (-90, 14), (-93, 15),
     (-97, 16), (-102, 18), (-106, 22), (-110, 24), (-113, 29), (-117, 33),
     (-121, 36), (-124, 40), (-124, 46), (-128, 50), (-132, 56), (-140, 60),
     (-148, 61), (-155, 58), (-162, 58), (-166, 60)],
    # Greenland
    [(-55, 60), (-45, 60), (-40, 64), (-32, 68), (-22, 70), (-20, 74),
     (-30, 76), (-45, 78), (-58, 76), (-60, 72), (-55, 64)],
    # South America
    [(-79, 9), (-76, 4), (-80, -3), (-81, -5), (-78, -10), (-74, -16),
     (-70, -20), (-70, -28), (-72, -34), (-73, -42), (-74, -50), (-70, -54),
     (-66, -55), (-64, -48), (-62, -40), (-58, -34), (-52, -32), (-48, -27),
     (-41, -22), (-39, -16), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
     (-50, 0), (-54, 5), (-58, 7), (-63, 10), (-68, 11), (-72, 12),
     (-76, 10)],
    # Africa
    [(-17, 15), (-16, 20), (-14, 26), (-10, 31), (-6, 35), (0, 36), (9, 37),
     (11, 34), (15, 32), (20, 32), (25, 31), (30, 31), (32, 30), (33, 27),
     (35, 23), (37, 20), (38, 17), (40, 15), (43, 12), (48, 11), (51, 11),
     (46, 5), (42, 0), (40, -6), (39, -12), (36, -18), (34, -22), (32, -28),
     (28, -33), (22, -35), (18, -33), (15, -27), (12, -18), (12, -12),
     (13, -8), (10, -2), (9, 4), (6, 4), (0, 6), (-6, 5), (-12, 7),
     (-16, 11)],
    # Eurasia
    [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-1, 49), (2, 51),
     (5, 53), (8, 55), (8, 57), (10, 59), (6, 60), (5, 62), (10, 64),
     (14, 67), (18, 69), (24, 71), (29, 71), (33, 69), (38, 68), (44, 68),
     (50, 69), (56, 69), (62, 70), (68, 72), (74, 73), (80, 73), (86, 74),
     (92, 75), (98, 76), (104, 77), (110, 74), (114, 73), (120, 73),
     (126, 72), (132, 72), (138, 72), (144, 71), (150, 70), (156, 69),
     (160, 68), (166, 66), (170, 66), (178, 65), (178, 62), (172, 62),
     (168, 60), (162, 58), (158, 53), (156, 51), (150, 59), (144, 59),
     (142, 55), (140, 50), (138, 46), (135, 43), (132, 43), (130, 42),
     (128, 38), (127, 35), (126, 33), (124, 31), (122, 29), (120, 26),
     (118, 24), (114, 22), (110, 20), (108, 18), (106, 10), (104, 8),
     (102, 7), (100, 6), (98, 10), (97, 14), (94, 17), (92, 21), (90, 22),
     (88, 22), (86, 20), (84, 18), (82, 16), (80, 14), (78, 8), (76, 10),
     (74, 14), (72, 19), (70, 21), (68, 23), (66, 25), (63, 25), (60, 25),
     (57, 26), (54, 26), (52, 27), (50, 29), (48, 30), (47, 30), (50, 26),
     (52, 25), (54, 24), (56, 26), (57, 25), (59, 22), (58, 20), (55, 17),
     (52, 15), (48, 14), (45, 13), (43, 12), (42, 15), (40, 20), (39, 21),
     (38, 24), (36, 28), (35, 29), (34, 31), (35, 36), (33, 36), (30, 36),
     (27, 37), (26, 38), (23, 36), (22, 37), (20, 39), (19, 40), (21, 42),
     (19, 44), (18, 46), (15, 44), (14, 45), (12, 45), (10, 44), (8, 44),
     (6, 43), (3, 43), (0, 40), (-2, 37), (-6, 36)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-2, 50)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
     (141, 39), (141, 41), (142, 43), (144, 44), (143, 42), (141, 39),
     (140, 36), (138, 35), (136, 33), (133, 34), (131, 33)],
    # Sumatra
    [(95, 5), (98, 3), (101, 0), (104, -3), (106, -6), (104, -7), (100, -5),
     (97, 2)],
    # Borneo
    [(109, 1), (112, 3), (116, 6), (118, 2), (117, -2), (114, -4),
     (110, -3)],
    # New Guinea
    [(131, -1), (136, -2), (140, -3), (145, -6), (150, -9), (147, -9),
     (142, -8), (138, -7), (134, -4)],
    # Java
    [(105, -6), (108, -7), (112, -7), (114, -8), (110, -8), (106, -7)],
    # Sulawesi
    [(119, 0), (121, 1), (123, 0), (121, -2), (120, -4), (119, -2)],
    # Australia
    [(114, -22), (114, -30), (116, -35), (120, -34), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (140, -17), (136, -15), (135, -12), (132, -12), (130, -13), (126, -14),
     (122, -17), (118, -20)],
    # New Zealand (South Island)
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (174, -41),
     (171, -44)],
    # New Zealand (North Island)
    [(173, -35), (176, -38), (178, -38), (176, -40), (174, -41), (172, -40)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (44, -25),
     (43, -21), (43, -17)],
    # Philippines
    [(120, 18), (122, 18), (122, 14), (121, 11), (120, 9), (121, 13),
     (122, 16)],
    # Taiwan
    [(120, 22), (121, 23), (122, 25), (121, 25)],
]


def _in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            xinters = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xinters:
                inside = not inside
        j = i
    return inside


def on_land(lon, lat):
    return any(_in_poly(lon, lat, p) for p in POLYS)


# Equirectangular mapping for the map panel; lat 75..-55 fits the panel.
MAP_LAT_TOP = 75.0
MAP_LAT_BOT = -55.0


def project(lon, lat, mx, my, mw, mh):
    x = mx + (lon + 180.0) / 360.0 * mw
    y = my + (MAP_LAT_TOP - lat) / (MAP_LAT_TOP - MAP_LAT_BOT) * mh
    return x, y

# ------------------------------------------------------------------- stories
# (num, kicker, headline, deck, illustration key, tint index)
HEROES = [
    (1, "ASIA · SUMMIT",
     "Trump, Xi and Putin meet in Shenzhen",
     "First trilateral, ~90 min at Kylin Villa: \u201cDeclaration Towards "
     "Peace\u201d, four points; no Ukraine, no timeline.",
     "summit", 0),
    (2, "WORLD · JUSTICE",
     "World court: Myanmar committed genocide",
     "9\u20136: first state ever found guilty of genocide in 80 years; "
     "~10,000 Rohingya killed in 2017.",
     "court", 1),
    (3, "MARKETS · IPO",
     "Anthropic lists at $83 \u2014 the largest IPO ever",
     "$81.3bn at $83 a share, ~$1.5tn value; ANT debut, +17%, past "
     "SpaceX\u2019s $75bn.",
     "ipo", 2),
]

CARDS = [
    (4, "USA · POLITICS",
     "Jeffries nominated for Speaker, 251\u201311",
     "House Democrats pick Hakeem Jeffries; if elected 3 Jan, the first Black "
     "Speaker in US history.",
     "parliament", 3),
    (5, "CULTURE · ART",
     "Van Gogh sells for $190.4m \u2014 a record",
     "\u201cChataigniers en fleurs\u201d (1890), Sotheby\u2019s New York; $165m hammer, "
     "after a Nazi-era claim was settled.",
     "painting", 4),
    (6, "SCIENCE · SPACE",
     "Voyager 1, one light-day from Earth",
     "First human-made object to reach one light-day out (~16bn miles); its "
     "signal takes 24 hours.",
     "probe", 5),
    (7, "CULTURE · GAMES",
     "GTA VI opens after a 13-year wait",
     "Launches at midnight UK 19 Nov; ~2.8m UK adults set to play on day one; "
     "time off +9%.",
     "game", 0),
    (8, "MIDDLE EAST · WAR",
     "Israeli tanks cross the Yellow Line",
     "First ground operation across the line since the Oct 2025 truce; at "
     "least 3 killed.",
     "tank", 1),
    (9, "MIDDLE EAST · WAR",
     "Cost of the US\u2013Iran war passes $48.3bn",
     "Pentagon official tells a Senate committee; Iran fired on US sites in "
     "Kuwait overnight.",
     "cost", 2),
    (10, "EUROPE · WAR",
     "EU proposes \u20ac45bn loan for Ukraine",
     "Covers ~2/3 of a ~\u20ac70bn gap for 2027; repaid only if Russia pays "
     "reparations.",
     "euro", 3),
    (11, "ASIA · WEATHER",
     "Cyclone Akvan bears down on India",
     "Severe cyclone nears India\u2019s east coast; landfall forecast between "
     "Machilipatnam and Puri.",
     "cyclone", 4),
    (12, "MARKETS · TECH",
     "Nvidia posts $115.8bn quarter",
     "Revenue $115.8bn (reported 18 Nov); Huang will not return as CEO; "
     "Kress stays interim chief.",
     "chip", 5),
]

# (num, lead, one-line text) — three columns, column-major: 13-20, 21-28, 29-36
BRIEFS = [
    (13, "SOMALIA", "orders UAE envoy out in 72 hours."),
    (14, "SENEGAL", "boat capsizes off Yenne; dozens missing."),
    (15, "INDONESIA", "refinery blast in Cepu kills one worker."),
    (16, "NETHERLANDS", "summons envoy after Kyiv strike."),
    (17, "USA", "Treasury sanctions 3 people, 2 firms."),
    (18, "ETHIOPIA", "both sides mass troops near Badme."),
    (19, "YEMEN", "Saudis expect campaign to run into 2027."),
    (20, "USA", "Senate votes 51\u201348 on curbing Iran war."),
    (21, "EU", "Commission hit by AI cyberattack."),
    (22, "DENMARK", "ratifies US\u2013Greenland deal, 109\u20130."),
    (23, "CANADA", "Carney recalibrates China ties."),
    (24, "USA", "Fed minutes: more rate hikes expected."),
    (25, "MARKETS", "Gold off ~5% to ~$3,735; oil down."),
    (26, "FINLAND", "approves Onkalo, first waste store."),
    (27, "ESTONIA", "to shut Russia crossings in Dec."),
    (28, "CZECHIA", "huge Prague protest for free media."),
    (29, "SPAIN", "general strike hits ports, factories."),
    (30, "YEMEN", "Houthi rocket kills 53 soldiers."),
    (31, "GERMANY", "Russian held for spying on Palantir."),
    (32, "INDIA\u2013JAPAN", "2+2 defence talks open in Tokyo."),
    (33, "RELIGION", "Pew: Islam largest faith by 2035."),
    (34, "SPORT", "England win by 97 runs; Duckett 133."),
    (35, "INDIA", "\u2018Ramayana\u2019 tops \u20b91,000 crore in 14 days."),
    (36, "OBITUARY", "Actor Stacy Keach dies at 85."),
]

# Map pins: (num, lon, lat, dx, dy) — dx/dy offset the label from its true
# point; a hairline leads from the label back to the true place.
PINS = [
    (1, 114.1, 22.5, 12, 10),      # Shenzhen
    (2, 4.3, 52.1, -26, -14),      # The Hague
    (3, -122.4, 37.8, -14, -12),   # San Francisco (Anthropic)
    (4, -77.0, 38.9, -16, 10),     # Washington DC
    (5, -74.0, 40.7, 14, -12),     # New York (Van Gogh)
    (7, -0.1, 51.5, 24, -14),      # London (GTA VI)
    (8, 34.5, 31.5, 12, 12),       # Gaza
    (9, 47.5, 29.4, -14, -10),     # Kuwait / Gulf
    (10, 4.35, 50.85, 16, 12),     # Brussels (EU loan)
    (11, 88.0, 17.0, 0, -16),      # Bay of Bengal (Cyclone Akvan)
    (12, -121.95, 37.35, 14, 12),  # Santa Clara (Nvidia)
]

# Brief dots: (num, lon, lat) — small red dots for briefs 13-36.
DOTS = [
    (13, 45.3, 2.0), (14, -17.2, 14.7), (15, 111.6, -7.1), (16, 5.5, 52.3),
    (17, -80.0, 37.0), (18, 37.9, 14.7), (19, 45.0, 12.8), (20, -80.0, 36.0),
    (21, 7.0, 51.5), (22, 12.6, 55.7), (23, -75.7, 45.4), (24, -82.0, 38.0),
    (25, -71.0, 42.0), (26, 25.0, 60.2), (27, 24.7, 59.4), (28, 14.4, 50.1),
    (29, -3.7, 40.4), (30, 44.2, 15.4), (31, 13.4, 52.5), (32, 139.7, 35.7),
    (33, -79.0, 39.0), (34, -3.0, 53.0), (35, 72.8, 19.1), (36, -118.2, 34.0),
]

LEGEND_REGIONS = [
    ("Americas", (46, 139, 87)), ("Europe", (66, 103, 178)),
    ("Africa", (180, 120, 60)), ("Middle East", (179, 39, 30)),
    ("Asia", (201, 162, 39)), ("Oceania", (0, 150, 136)),
    ("Global", (128, 96, 160)),
]


# ------------------------------------------------------------- illustrations
def ill_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(233, 224, 196))
    # skyline silhouettes
    for bx, bw, bh in [(6, 22, 26), (34, 16, 34), (56, 26, 22), (88, 18, 30),
                       (112, 24, 18), (142, 16, 28), (164, 22, 24),
                       (192, 18, 32), (216, 26, 20), (248, 20, 28),
                       (274, 22, 16)]:
        d.rectangle([x + bx, y + h - 14 - bh, x + bx + bw, y + h - 14],
                    fill=NAVY)
    # three flag poles
    for fx, fc in [(96, (179, 39, 30)), (150, (27, 42, 74)), (204, (201, 162, 39))]:
        d.line([x + fx, y + 6, x + fx, y + h - 14], fill=INK, width=2)
        d.rectangle([x + fx, y + 6, x + fx + 14, y + 14], fill=fc)
    # round table with three seated figures (dots/blocks, no faces)
    d.ellipse([x + 128, y + h - 26, x + 198, y + h - 12], fill=(196, 120, 60),
              outline=INK)
    for cx, c in [(140, (179, 39, 30)), (163, (27, 42, 74)), (186, (201, 162, 39))]:
        d.ellipse([x + cx - 5, y + h - 38, x + cx + 5, y + h - 28], fill=c,
                  outline=INK)
        d.rectangle([x + cx - 6, y + h - 28, x + cx + 6, y + h - 22], fill=c,
                    outline=INK)


def ill_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(233, 224, 196))
    # courthouse: pediment + columns
    cx, base = x + w // 2, y + h - 12
    d.polygon([(cx - 52, y + 16), (cx + 52, y + 16), (cx, y + 2)], fill=NAVY)
    for i in range(5):
        px = cx - 44 + i * 22
        d.rectangle([px, y + 18, px + 7, base], fill=(250, 250, 246),
                    outline=INK)
    d.rectangle([cx - 52, y + 16, cx + 52, y + 20], fill=(250, 250, 246),
                outline=INK)
    # scales of justice, right
    sx = x + w - 52
    d.line([sx, y + 10, sx, y + 34], fill=INK, width=2)
    d.line([sx - 14, y + 14, sx + 14, y + 14], fill=INK, width=2)
    d.ellipse([sx - 18, y + 30, sx - 8, y + 36], fill=GOLD, outline=INK)
    d.ellipse([sx + 8, y + 30, sx + 18, y + 36], fill=GOLD, outline=INK)
    d.line([sx - 13, y + 14, sx - 13, y + 30], fill=INK, width=1)
    d.line([sx + 13, y + 14, sx + 13, y + 30], fill=INK, width=1)


def ill_ipo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[2])
    # chip
    d.rectangle([x + 14, y + 12, x + 62, y + 44], fill=NAVY, outline=INK)
    d.rectangle([x + 26, y + 22, x + 50, y + 34], fill=GOLD, outline=INK)
    for px in (22, 34, 46):
        d.line([x + px, y + 6, x + px, y + 12], fill=INK, width=2)
        d.line([x + px, y + 44, x + px, y + 50], fill=INK, width=2)
    # rising chart with arrow
    pts = [(x + 78, y + 44), (x + 108, y + 38), (x + 138, y + 40),
           (x + 168, y + 26), (x + 198, y + 18), (x + 228, y + 8)]
    d.line(pts, fill=RED, width=3)
    d.polygon([(x + 228, y + 8), (x + 216, y + 6), (x + 226, y + 18)],
              fill=RED)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)


def ill_parliament(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[3])
    cx = x + w // 2
    d.polygon([(cx - 30, y + 8), (cx + 30, y + 8), (cx, y + 1)], fill=NAVY)
    d.rectangle([cx - 30, y + 8, cx + 30, y + 11], fill=NAVY)
    for i in range(4):
        px = cx - 26 + i * 14
        d.rectangle([px, y + 11, px + 8, y + h - 4], fill=(250, 250, 246),
                    outline=INK)
    d.rectangle([cx - 30, y + h - 4, cx + 30, y + h - 1], fill=NAVY)


def ill_painting(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[4])
    # framed canvas, centred, with a bigger blossoming tree
    cx = x + w // 2
    d.rectangle([cx - 78, y + 2, cx + 78, y + h - 2], fill=(250, 246, 230),
                outline=INK, width=2)
    d.rectangle([cx - 73, y + 6, cx + 73, y + h - 6], fill=(168, 205, 225))
    d.line([cx, y + h - 7, cx + 3, y + 10], fill=(90, 60, 30), width=3)
    d.line([cx, y + 16, cx - 12, y + 8], fill=(90, 60, 30), width=2)
    for ox, oy, c in [(-18, -4, (240, 180, 200)), (0, -10, (245, 200, 210)),
                      (18, -4, (240, 180, 200)), (-9, 4, (250, 220, 225)),
                      (11, 4, (245, 195, 205))]:
        d.ellipse([cx + ox - 8, y + 12 + oy, cx + ox + 8, y + 28 + oy],
                  fill=c, outline=INK)


def ill_probe(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    # dashed path Earth -> probe
    for i in range(0, w - 110, 12):
        d.line([x + 26 + i, y + h // 2, x + 34 + i, y + h // 2], fill=GOLD,
               width=2)
    d.ellipse([x + 8, y + h // 2 - 6, x + 20, y + h // 2 + 6],
              fill=(90, 160, 200), outline=(255, 255, 255))
    # probe, larger: dish + body + boom
    px, py = x + w - 78, y + 4
    d.polygon([(px, py), (px + 30, py + 6), (px + 6, py + 16)], fill=(220, 220, 220),
              outline=(255, 255, 255))
    d.rectangle([px + 4, py + 16, px + 22, py + 24], fill=GOLD, outline=INK)
    d.line([px + 22, py + 20, px + 36, py + 20], fill=(255, 255, 255), width=2)
    for sx, sy in [(90, 6), (130, 10), (170, 6)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                  fill=(255, 255, 255))


def ill_game(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[0])
    # controller, centred and narrower so it reads as a controller
    cx = x + w // 2
    d.rounded_rectangle([cx - 62, y + 4, cx + 62, y + h - 4], radius=9,
                        fill=INK)
    d.ellipse([cx - 48, y + 9, cx - 36, y + 21], fill=(250, 250, 246))
    d.ellipse([cx + 36, y + 9, cx + 48, y + 21], fill=RED)
    d.ellipse([cx + 36, y + h - 21, cx + 48, y + h - 9], fill=GOLD)
    d.rectangle([cx - 6, y + 9, cx + 6, y + 21], fill=(250, 250, 246))
    d.ellipse([cx - 24, y + 10, cx - 16, y + 18], fill=(250, 250, 246))


def ill_tank(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[1])
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(233, 224, 196))
    # tank silhouette, larger and centred
    cx = x + w // 2
    d.rectangle([cx - 34, y + 8, cx + 30, y + 16], fill=(90, 100, 70),
                outline=INK)
    d.line([cx + 30, y + 11, cx + 62, y + 9], fill=INK, width=3)
    d.rectangle([cx - 40, y + 16, cx + 36, y + 22], fill=(70, 80, 55),
                outline=INK)
    for wx in range(-34, 32, 12):
        d.ellipse([cx + wx, y + 16, cx + wx + 7, y + 22], fill=INK)


def ill_cost(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[2])
    # rising bars + dollar coin
    for i, bh in enumerate([8, 14, 20, 28]):
        bx = x + 12 + i * 16
        d.rectangle([bx, y + h - 6 - bh, bx + 10, y + h - 6], fill=NAVY)
    d.ellipse([x + w - 34, y + 6, x + w - 8, y + 32], fill=GOLD, outline=INK)
    d.text((x + w - 26, y + 8), "$", font=sans_b(16), fill=INK)


def ill_euro(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[3])
    d.ellipse([x + 8, y + 4, x + 36, y + h - 4], fill=GOLD, outline=INK)
    d.text((x + 13, y + 5), "\u20ac", font=sans_b(18), fill=INK)
    # stars around
    for sx, sy in [(48, 6), (64, 12), (76, 24), (64, 28), (48, 30)]:
        d.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3], fill=NAVY)


def ill_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[0])
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(168, 205, 225))
    cx, cy = x + w // 2, y + h // 2 - 1
    for r in (5, 10, 15):
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=NAVY, width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)
    # coastline hint, bottom right
    d.line([x + w - 46, y + h - 6, x + w - 20, y + h - 12], fill=INK, width=2)


def ill_chip(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[5])
    # chip, centred and narrower so it reads as a chip, not a bar
    cx = x + w // 2
    d.rectangle([cx - 52, y + 4, cx + 52, y + h - 4], fill=NAVY, outline=INK)
    d.rectangle([cx - 30, y + 9, cx + 30, y + h - 9], fill=GOLD, outline=INK)
    for px in (cx - 36, cx - 12, cx + 12, cx + 36):
        d.line([px, y + 1, px, y + 4], fill=INK, width=2)
        d.line([px, y + h - 4, px, y + h - 1], fill=INK, width=2)


ILL = {"summit": ill_summit, "court": ill_court, "ipo": ill_ipo,
       "parliament": ill_parliament, "painting": ill_painting,
       "probe": ill_probe, "game": ill_game, "tank": ill_tank,
       "cost": ill_cost, "euro": ill_euro, "cyclone": ill_cyclone,
       "chip": ill_chip}

# -------------------------------------------------------------------- layout
import math

DATE_TEXT = "Thursday 19 November 2026"
SUBLINE = ("Three leaders at one table in Shenzhen, a court finds a state "
           "guilty of genocide, and the biggest share sale in history.")
KICKER_LEFT = "THE DAY IN WORLD NEWS"
KICKER_RIGHT = "36 STORIES · 6 CONTINENTS · ONE DAY"


def draw_masthead(d):
    tracked(d, (M, 12), KICKER_LEFT, sans_b(11), INK, track=2)
    rw = tracked_width(d, KICKER_RIGHT, sans_b(11), track=2)
    tracked(d, (W - M - rw, 12), KICKER_RIGHT, sans_b(11), RED, track=2)
    size = 60
    f = serif_b(size)
    while d.textlength(DATE_TEXT, font=f) > CW and size > 40:
        size -= 2
        f = serif_b(size)
    d.text((M, 26), DATE_TEXT, font=f, fill=INK)
    d.rectangle([M, 94, W - M, 96], fill=RED)
    d.text((M, 100), SUBLINE, font=serif_i(14), fill=INK)


def draw_map(d):
    tracked(d, (M, 120), "WHERE IT HAPPENED", sans_b(11), INK, track=2)
    mx, my, mw, mh = M, 134, CW, 138
    d.rectangle([mx, my, mx + mw, my + mh], fill=MAP_BG, outline=INK)
    step = 7
    for gx in range(mx + 4, mx + mw - 3, step):
        for gy in range(my + 4, my + mh - 3, step):
            lon = (gx - mx) / mw * 360.0 - 180.0
            lat = MAP_LAT_TOP - (gy - my) / mh * (MAP_LAT_TOP - MAP_LAT_BOT)
            if on_land(lon, lat):
                d.ellipse([gx - 1.6, gy - 1.6, gx + 1.6, gy + 1.6],
                          fill=MAP_DOT)
    for _num, lon, lat in DOTS:
        x, y = project(lon, lat, mx, my, mw, mh)
        d.ellipse([x - 2.5, y - 2.5, x + 2.5, y + 2.5], fill=RED)
    for num, lon, lat, dx, dy in PINS:
        ax, ay = project(lon, lat, mx, my, mw, mh)
        lx, ly = ax + dx, ay + dy
        d.line([ax, ay, lx, ly], fill=INK, width=1)
        d.ellipse([ax - 2, ay - 2, ax + 2, ay + 2], fill=INK)
        num_circle(d, lx, ly, num, r=9)
    # Voyager 1 has no place on Earth: red star, top-right of the panel.
    sx, sy = mx + mw - 28, my + 14
    star = []
    for i in range(10):
        r = 9 if i % 2 == 0 else 4
        a = -math.pi / 2 + i * math.pi / 5
        star.append((sx + r * math.cos(a), sy + r * math.sin(a)))
    d.polygon(star, fill=RED)
    label = "6 · VOYAGER 1 — ONE LIGHT-DAY OUT"
    lf = sans_b(9)
    lw = d.textlength(label, font=lf)
    d.rectangle([sx - 16 - lw, sy - 7, sx - 12, sy + 7], fill=MAP_BG)
    d.text((sx - 14 - lw, sy - 5), label, font=lf, fill=RED)
    # legend, one line
    x = M
    y = 276
    for name, color in LEGEND_REGIONS:
        d.ellipse([x, y + 2, x + 8, y + 10], fill=color)
        x += 12
        d.text((x, y), name, font=sans(10), fill=GREY)
        x += d.textlength(name, font=sans(10)) + 12
    suffix = "numbered pin: stories 1–12  ·  star: 6  ·  dot: briefs 13–36"
    d.text((x, y), suffix, font=sans(10), fill=GREY)
    if x + d.textlength(suffix, font=sans(10)) > W - M:
        print("OVERFLOW legend")


def draw_panel(d, x, y, w, h, num, kicker, headline, deck, ill_key, hero):
    d.rectangle([x, y, x + w, y + h], outline=INK)
    ill_h = 56 if hero else 28
    ILL[ill_key](d, x + 1, y + 1, w - 2, ill_h)
    ky = y + ill_h + 6
    kicker_line(d, x + 8, ky, num, kicker)
    hw = w - 16
    hf = serif_b(20 if hero else 15)
    hlh = 23 if hero else 17
    hlines = wrap(d, headline, hf, hw)
    if len(hlines) > 2:
        print(f"OVERFLOW headline {num}: {hlines}")
    hy = ky + 18
    for ln in hlines[:2]:
        d.text((x + 8, hy), ln, font=hf, fill=INK)
        hy += hlh
    df = sans(11 if hero else 10)
    dlh = 14 if hero else 13
    dlines = wrap(d, deck, df, hw)
    if len(dlines) > 2:
        print(f"OVERFLOW deck {num}: {dlines}")
    dy = hy + 2
    for ln in dlines[:2]:
        d.text((x + 8, dy), ln, font=df, fill=INK)
        dy += dlh


def draw_heroes(d):
    y, h = 296, 164
    pw = (CW - 2 * 10) // 3
    xs = [M, M + pw + 10, M + 2 * (pw + 10)]
    for (num, kick, head, deck, ill_key, _t), x in zip(HEROES, xs):
        draw_panel(d, x, y, pw, h, num, kick, head, deck, ill_key, hero=True)


def draw_grid(d):
    y0, h, gap = 468, 112, 6
    pw = (CW - 2 * 10) // 3
    xs = [M, M + pw + 10, M + 2 * (pw + 10)]
    for row in range(3):
        for col in range(3):
            num, kick, head, deck, ill_key, _t = CARDS[row * 3 + col]
            draw_panel(d, xs[col], y0 + row * (h + gap), pw, h, num, kick,
                       head, deck, ill_key, hero=False)


def draw_briefs(d):
    d.line([M, 820, W - M, 820], fill=INK, width=1)
    tracked(d, (M, 825), "ALSO ON THURSDAY 19 NOVEMBER 2026", sans_b(11),
            INK, track=2)
    d.line([M, 842, W - M, 842], fill=INK, width=1)
    col_w = (CW - 2 * 12) // 3
    col_x = [M, M + col_w + 12, M + 2 * (col_w + 12)]
    for ci in range(3):
        for ri, (num, lead, text) in enumerate(BRIEFS[ci * 8:(ci + 1) * 8]):
            y = 848 + ri * 15
            x = col_x[ci]
            nstr = f"{num}. "
            d.text((x, y), nstr, font=sans_b(11), fill=RED)
            x += d.textlength(nstr, font=sans_b(11))
            d.text((x, y), lead, font=sans_b(11), fill=INK)
            x += d.textlength(lead + " ", font=sans_b(11))
            d.text((x, y), "— " + text, font=sans(11), fill=INK)
            total = (d.textlength(nstr, font=sans_b(11))
                     + d.textlength(lead + " ", font=sans_b(11))
                     + d.textlength("— " + text, font=sans(11)))
            if total > col_w:
                print(f"OVERFLOW brief {num}: {total:.0f}px > {col_w}px :: "
                      f"{lead} — {text}")


def draw_footer(d):
    d.line([M, 974, W - M, 974], fill=INK, width=2)
    d.text((M, 980),
           "Every story was reported on 19 November 2026; disputed claims "
           "are attributed.", font=sans(10), fill=GREY)
    d.text((M, 994),
           "Sources: Reuters · AP · AFP · BBC · Al Jazeera. "
           "Original drawings.", font=sans(10), fill=GREY)


def build(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_map(d)
    draw_heroes(d)
    draw_grid(d)
    draw_briefs(d)
    draw_footer(d)
    img.save(out_path, "PNG", optimize=True)
    total = len(HEROES) + len(CARDS) + len(BRIEFS)
    print(f"wrote {out_path} ({total} stories)")


if __name__ == "__main__":
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "entry.png"))
