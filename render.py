#!/usr/bin/env python3
"""Render entry.png for news-image-20261119 — agent 2 REDO (noble-robin-77).

Layout "THE DAY UNFOLDS": the spine of the page is a VERTICAL TIMELINE down
the left side; stories sit in five time bands (FIRST WIRES / MORNING / MIDDAY
/ AFTERNOON / EVENING). The APEC trilateral is the single full-width feature
inside the MIDDAY band. Band cards use icon-left layout (small square flat
illustration + text). Briefs 14-40 in three columns. The world map is only a
SLIM locator strip at the very bottom (~90px), not the hero. 40 stories, all
reported on Thursday 19 November 2026. Flat vector original drawings, PIL
only, fully deterministic (same bytes every run).
"""
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 14                      # page margin
CW = W - 2 * M              # content width = 996

PAPER = (247, 243, 232)     # warm cream #F7F3E8
INK = (17, 17, 17)          # near-black
RED = (179, 39, 30)         # brick red #B3271E
NAVY = (27, 42, 74)         # #1B2A4A
GOLD = (201, 162, 39)       # #C9A227
GREY = (85, 85, 85)
TEAL = (31, 92, 77)         # timeline spine #1F5C4D
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


def num_circle(draw, cx, cy, n, r=8):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    f = sans_b(10 if len(str(n)) < 2 else 9)
    tw = draw.textlength(str(n), font=f)
    th = f.getbbox(str(n))[3]
    draw.text((cx - tw / 2, cy - th / 2 - 1), str(n), font=f, fill=(255, 255, 255))


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


# Equirectangular mapping for the slim map strip; lat 75..-55 fits the panel.
MAP_LAT_TOP = 75.0
MAP_LAT_BOT = -55.0


def project(lon, lat, mx, my, mw, mh):
    x = mx + (lon + 180.0) / 360.0 * mw
    y = my + (MAP_LAT_TOP - lat) / (MAP_LAT_TOP - MAP_LAT_BOT) * mh
    return x, y

# ------------------------------------------------------------------- stories
# (num, kicker, headline, deck, illustration key, tint index)
# Numbering follows the day: FIRST WIRES 1-3, MORNING 4-6, MIDDAY hero 7,
# AFTERNOON 8-10, EVENING 11-13.
CARDS = [
    (1, "CULTURE · ART",
     "Van Gogh sells for $190.4m — a record",
     "\u201cChataigniers en fleurs\u201d (1890), Sotheby\u2019s New York; $165m "
     "hammer; claim settled.",
     "painting", 4),
    (2, "SCIENCE · SPACE",
     "Voyager 1, one light-day from Earth",
     "First human-made object one light-day out (~16bn miles); signal "
     "takes 24 hours.",
     "probe", 5),
    (3, "EUROPE · WAR",
     "Crimean Bridge hit again",
     "Ukraine strike halts trains hours before APEC; Russia says the bridge "
     "was attacked.",
     "bridge", 1),
    (4, "USA · POLITICS",
     "Jeffries nominated for Speaker, 251–11",
     "Democrats pick Hakeem Jeffries; if elected 3 Jan, first Black Speaker "
     "in US history.",
     "parliament", 3),
    (5, "ASIA · WEATHER",
     "Cyclone Akvan bears down on India",
     "Severe cyclone nears India\u2019s east coast; Odisha evacuates; "
     "landfall due near Puri.",
     "cyclone", 0),
    (6, "MARKETS · TECH",
     "Nvidia posts $115.8bn quarter",
     "Revenue $115.8bn (reported 18 Nov); Huang won\u2019t return; Kress "
     "stays on.",
     "chip", 2),
    (8, "WORLD · JUSTICE",
     "World court: Myanmar committed genocide",
     "9\u20136: first state guilty of genocide in 80 years; ~10,000 Rohingya "
     "killed in 2017.",
     "court", 1),
    (9, "EUROPE · WAR",
     "EU proposes \u20ac45bn loan for Ukraine",
     "Covers ~2/3 of a ~\u20ac70bn gap for 2027; repaid only if Russia pays "
     "reparations.",
     "euro", 3),
    (10, "MIDDLE EAST · WAR",
     "Israeli tanks cross the Yellow Line",
     "First ground operation across the line since the Oct 2025 truce; at "
     "least 3 killed.",
     "tank", 4),
    (11, "MARKETS · IPO",
     "Anthropic lists at $83 — the largest IPO ever",
     "$81.3bn at $83 a share, ~$1.5tn value; ANT debut, +17%, past "
     "SpaceX\u2019s $75bn.",
     "ipo", 2),
    (12, "CULTURE · GAMES",
     "GTA VI opens after a 13-year wait",
     "Launches midnight UK 19 Nov; ~2.8m UK adults set to play day one; "
     "time off +9%.",
     "game", 0),
    (13, "MIDDLE EAST · WAR",
     "Cost of the US–Iran war passes $48.3bn",
     "Pentagon official tells a Senate committee; Iran fired on US sites "
     "in Kuwait.",
     "cost", 5),
]

# The MIDDAY hero feature: (num, kicker, headline, deck, illustration key)
HERO = (7, "ASIA · SUMMIT",
        "Three leaders, one table: Trump, Xi and Putin meet in Shenzhen",
        "First-ever trilateral, ~90 minutes at Kylin Villa: a four-point "
        "\u201cDeclaration Towards Peace\u201d \u2014 nuclear war cannot be won "
        "and must never be fought; no mention of Ukraine, no timeline, no "
        "mechanism.",
        "summit")

# (num, lead, one-line text) — three columns, column-major: 14-22, 23-31, 32-40
BRIEFS = [
    (14, "SOMALIA", "orders UAE envoy out in 72 hours."),
    (15, "SENEGAL", "boat capsizes off Yenne; dozens missing."),
    (16, "INDONESIA", "refinery blast in Cepu kills one worker."),
    (17, "NETHERLANDS", "summons envoy after Kyiv strike."),
    (18, "USA", "Treasury sanctions 3 people, 2 firms."),
    (19, "ETHIOPIA", "both sides mass troops near Badme."),
    (20, "YEMEN", "Saudis expect campaign to run into 2027."),
    (21, "USA", "Senate votes 51\u201348 on curbing Iran war."),
    (22, "EU", "Commission hit by AI cyberattack."),
    (23, "DENMARK", "ratifies US\u2013Greenland deal, 109\u20130."),
    (24, "CANADA", "Carney recalibrates China ties."),
    (25, "USA", "Fed minutes: more rate hikes expected."),
    (26, "MARKETS", "Gold off ~5% to ~$3,735; oil down."),
    (27, "FINLAND", "approves Onkalo, first waste store."),
    (28, "ESTONIA", "to shut Russia crossings in Dec."),
    (29, "CZECHIA", "huge Prague protest for free media."),
    (30, "SPAIN", "general strike hits ports, factories."),
    (31, "YEMEN", "Houthi rocket kills 53 soldiers."),
    (32, "GERMANY", "Russian held for spying on Palantir."),
    (33, "INDIA\u2013JAPAN", "2+2 defence talks open in Tokyo."),
    (34, "RELIGION", "Pew: Islam largest faith by 2035."),
    (35, "SPORT", "England win by 97 runs; Duckett 133."),
    (36, "INDIA", "\u2018Ramayana\u2019 tops \u20b91,000 crore in 14 days."),
    (37, "OBITUARY", "Actor Stacy Keach dies at 85."),
    (38, "UK", "McDonald's abuse inquiry widens."),
    (39, "GERMANY", "2027 tax forecast hits record \u20ac1tn."),
    (40, "CLIMATE", "Coral reefs face extinction in 50 years."),
]

# Map pins: (num, lon, lat, dx, dy) — dx/dy offset the label from its true
# point; a hairline leads from the label back to the true place.
PINS = [
    (1, -74.0, 40.7, 14, -12),     # New York (Van Gogh)
    (3, 35.0, 45.3, 16, -12),      # Kerch / Crimean Bridge
    (4, -77.0, 38.9, -26, 10),     # Washington DC (Jeffries)
    (5, 88.0, 17.0, 0, -16),       # Bay of Bengal (Cyclone Akvan)
    (6, -121.95, 37.35, 14, 12),   # Santa Clara (Nvidia)
    (7, 114.1, 22.5, 12, -12),     # Shenzhen (APEC)
    (8, 4.3, 52.1, -28, 12),       # The Hague (ICJ)
    (9, 4.35, 50.85, 4, 16),       # Brussels (EU loan)
    (10, 34.5, 31.5, 14, 12),      # Gaza
    (11, -122.4, 37.8, -30, -10),  # San Francisco (Anthropic)
    (12, -0.1, 51.5, -34, 0),      # London (GTA VI)
    (13, 47.5, 29.4, -14, -10),    # Kuwait / Gulf
]

# Brief dots: (num, lon, lat) — small red dots for briefs 14-40.
DOTS = [
    (14, 45.3, 2.0), (15, -17.2, 14.7), (16, 111.6, -7.1),
    (17, 5.5, 52.3), (18, -80.0, 37.0), (19, 37.9, 14.7),
    (20, 45.0, 12.8), (21, -80.0, 36.0), (22, 7.0, 51.5),
    (23, 12.6, 55.7), (24, -75.7, 45.4), (25, -82.0, 38.0),
    (26, -71.0, 42.0), (27, 25.0, 60.2), (28, 24.7, 59.4),
    (29, 14.4, 50.1), (30, -3.7, 40.4), (31, 44.2, 15.4),
    (32, 13.4, 52.5), (33, 139.7, 35.7), (34, -79.0, 39.0),
    (35, -3.0, 53.0), (36, 72.8, 19.1), (37, -118.2, 34.0),
    (38, -2.5, 51.0), (39, 10.0, 51.0), (40, 147.0, -19.0),
]

# Time bands: (phase label lines, y, height, card numbers)
BANDS = [
    (("FIRST", "WIRES"), 126, 96, [1, 2, 3]),
    (("MORNING",), 222, 96, [4, 5, 6]),
    (("MIDDAY",), 318, 136, [7]),          # hero feature
    (("AFTERNOON",), 454, 96, [8, 9, 10]),
    (("EVENING",), 550, 96, [11, 12, 13]),
]
SPINE_X = 112
BAND_X0 = 128
BAND_X1 = 1010

# ------------------------------------------------------------- illustrations
# Every illustration draws inside (x, y, w, h) with relative coordinates, so
# the same motif works as a 54px icon and as the 300px hero panel.
def ill_painting(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[4])
    cx = x + w // 2
    fw, fh = w * 0.62, h * 0.86
    d.rectangle([cx - fw / 2, y + (h - fh) / 2, cx + fw / 2,
                 y + (h + fh) / 2], fill=(250, 246, 230), outline=INK, width=2)
    d.rectangle([cx - fw / 2 + 3, y + (h - fh) / 2 + 3, cx + fw / 2 - 3,
                 y + (h + fh) / 2 - 3], fill=(168, 205, 225))
    d.line([cx, y + h - 5, cx + 2, y + h * 0.30], fill=(90, 60, 30), width=3)
    for ox, oy, c in [(-0.16, -0.10, (240, 180, 200)),
                      (0.0, -0.18, (245, 200, 210)),
                      (0.16, -0.10, (240, 180, 200)),
                      (-0.08, 0.02, (250, 220, 225)),
                      (0.10, 0.02, (245, 195, 205))]:
        r = w * 0.09
        d.ellipse([cx + ox * w - r, y + h * 0.42 + oy * h - r,
                   cx + ox * w + r, y + h * 0.42 + oy * h + r],
                  fill=c, outline=INK)


def ill_probe(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    for i in range(0, int(w * 0.55), 10):
        d.line([x + w * 0.22 + i, y + h * 0.55,
                x + w * 0.22 + i + 5, y + h * 0.55], fill=GOLD, width=2)
    d.ellipse([x + w * 0.06, y + h * 0.42, x + w * 0.20, y + h * 0.68],
              fill=(90, 160, 200), outline=(255, 255, 255))
    px, py = x + w * 0.62, y + h * 0.18
    d.polygon([(px, py), (px + w * 0.28, py + h * 0.10),
               (px + w * 0.05, py + h * 0.26)], fill=(220, 220, 220),
              outline=(255, 255, 255))
    d.rectangle([px + w * 0.04, py + h * 0.26, px + w * 0.20, py + h * 0.38],
                fill=GOLD, outline=INK)
    for sx, sy in [(0.30, 0.15), (0.45, 0.10), (0.55, 0.18)]:
        d.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1,
                   y + sy * h + 1], fill=(255, 255, 255))


def ill_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(168, 205, 225))
    # bridge deck + arch
    d.line([x, y + h * 0.55, x + w, y + h * 0.55], fill=INK, width=3)
    d.arc([x + w * 0.18, y + h * 0.30, x + w * 0.82, y + h * 0.80],
          180, 360, fill=INK, width=2)
    d.line([x + w * 0.30, y + h * 0.20, x + w * 0.30, y + h * 0.55],
           fill=INK, width=2)
    d.line([x + w * 0.70, y + h * 0.20, x + w * 0.70, y + h * 0.55],
           fill=INK, width=2)
    # red burst where it was hit
    bx, by = x + w * 0.50, y + h * 0.42
    burst = []
    for i in range(10):
        r = w * 0.13 if i % 2 == 0 else w * 0.06
        a = -math.pi / 2 + i * math.pi / 5
        burst.append((bx + r * math.cos(a), by + r * math.sin(a)))
    d.polygon(burst, fill=RED)


def ill_parliament(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[3])
    cx = x + w // 2
    d.polygon([(cx - w * 0.30, y + h * 0.22), (cx + w * 0.30, y + h * 0.22),
               (cx, y + h * 0.04)], fill=NAVY)
    d.rectangle([cx - w * 0.30, y + h * 0.22, cx + w * 0.30, y + h * 0.28],
                fill=NAVY)
    for i in range(4):
        px = cx - w * 0.26 + i * w * 0.16
        d.rectangle([px, y + h * 0.28, px + w * 0.08, y + h * 0.88],
                    fill=(250, 250, 246), outline=INK)
    d.rectangle([cx - w * 0.30, y + h * 0.88, cx + w * 0.30, y + h * 0.94],
                fill=NAVY)


def ill_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[0])
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(168, 205, 225))
    cx, cy = x + w // 2, y + h * 0.42
    for r in (0.08, 0.16, 0.24, 0.32):
        rr = w * r
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 20, 300, fill=NAVY,
              width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)
    d.line([x + w * 0.62, y + h * 0.82, x + w * 0.86, y + h * 0.72],
           fill=INK, width=2)


def ill_chip(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[5])
    cx, cy = x + w // 2, y + h // 2
    d.rectangle([cx - w * 0.36, cy - h * 0.36, cx + w * 0.36, cy + h * 0.36],
                fill=NAVY, outline=INK)
    d.rectangle([cx - w * 0.20, cy - h * 0.20, cx + w * 0.20, cy + h * 0.20],
                fill=GOLD, outline=INK)
    for px in (-0.24, 0.0, 0.24):
        d.line([cx + px * w, y + 2, cx + px * w, cy - h * 0.36],
               fill=INK, width=2)
        d.line([cx + px * w, cy + h * 0.36, cx + px * w, y + h - 2],
               fill=INK, width=2)


def ill_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(233, 224, 196))
    cx, base = x + w * 0.42, y + h * 0.86
    d.polygon([(cx - w * 0.32, y + h * 0.26), (cx + w * 0.32, y + h * 0.26),
               (cx, y + h * 0.06)], fill=NAVY)
    for i in range(4):
        px = cx - w * 0.28 + i * w * 0.16
        d.rectangle([px, y + h * 0.28, px + w * 0.07, base],
                    fill=(250, 250, 246), outline=INK)
    d.rectangle([cx - w * 0.32, y + h * 0.26, cx + w * 0.32, y + h * 0.30],
                fill=(250, 250, 246), outline=INK)
    # scales of justice, right
    sx = x + w * 0.82
    d.line([sx, y + h * 0.16, sx, y + h * 0.62], fill=INK, width=2)
    d.line([sx - w * 0.10, y + h * 0.22, sx + w * 0.10, y + h * 0.22],
           fill=INK, width=2)
    d.ellipse([sx - w * 0.13, y + h * 0.52, sx - w * 0.05, y + h * 0.64],
              fill=GOLD, outline=INK)
    d.ellipse([sx + w * 0.05, y + h * 0.52, sx + w * 0.13, y + h * 0.64],
              fill=GOLD, outline=INK)
    d.line([sx - w * 0.09, y + h * 0.22, sx - w * 0.09, y + h * 0.52],
           fill=INK, width=1)
    d.line([sx + w * 0.09, y + h * 0.22, sx + w * 0.09, y + h * 0.52],
           fill=INK, width=1)


def ill_euro(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[3])
    cx, cy = x + w * 0.32, y + h // 2
    r = h * 0.38
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD, outline=INK)
    d.text((cx - r * 0.45, cy - r * 0.62), "\u20ac", font=sans_b(int(h * 0.55)),
           fill=INK)
    for sx, sy in [(0.62, 0.16), (0.78, 0.28), (0.84, 0.52), (0.72, 0.72),
                   (0.58, 0.78)]:
        d.ellipse([x + sx * w, y + sy * h, x + sx * w + 3, y + sy * h + 3],
                  fill=NAVY)


def ill_tank(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[1])
    d.rectangle([x, y + h * 0.84, x + w, y + h], fill=(233, 224, 196))
    cx = x + w // 2
    d.rectangle([cx - w * 0.26, y + h * 0.24, cx + w * 0.22, y + h * 0.42],
                fill=(90, 100, 70), outline=INK)
    d.line([cx + w * 0.22, y + h * 0.30, cx + w * 0.46, y + h * 0.26],
           fill=INK, width=3)
    d.rectangle([cx - w * 0.32, y + h * 0.42, cx + w * 0.28, y + h * 0.60],
                fill=(70, 80, 55), outline=INK)
    for i in range(4):
        wx = cx - w * 0.28 + i * w * 0.15
        d.ellipse([wx, y + h * 0.42, wx + w * 0.08, y + h * 0.60], fill=INK)


def ill_ipo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[2])
    # small chip, left
    d.rectangle([x + w * 0.08, y + h * 0.30, x + w * 0.34, y + h * 0.72],
                fill=NAVY, outline=INK)
    d.rectangle([x + w * 0.15, y + h * 0.42, x + w * 0.27, y + h * 0.60],
                fill=GOLD, outline=INK)
    # rising chart with arrow, right
    pts = [(x + w * 0.40, y + h * 0.72), (x + w * 0.54, y + h * 0.64),
           (x + w * 0.66, y + h * 0.68), (x + w * 0.78, y + h * 0.44),
           (x + w * 0.90, y + h * 0.26)]
    d.line(pts, fill=RED, width=3)
    d.polygon([(x + w * 0.90, y + h * 0.26), (x + w * 0.80, y + h * 0.24),
               (x + w * 0.88, y + h * 0.38)], fill=RED)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)


def ill_game(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[0])
    cx = x + w // 2
    d.rounded_rectangle([cx - w * 0.38, y + h * 0.22, cx + w * 0.38,
                         y + h * 0.78], radius=8, fill=INK)
    d.ellipse([cx - w * 0.30, y + h * 0.30, cx - w * 0.20, y + h * 0.44],
              fill=(250, 250, 246))
    d.ellipse([cx + w * 0.20, y + h * 0.30, cx + w * 0.30, y + h * 0.44],
              fill=RED)
    d.ellipse([cx + w * 0.20, y + h * 0.56, cx + w * 0.30, y + h * 0.70],
              fill=GOLD)
    d.rectangle([cx - w * 0.05, y + h * 0.30, cx + w * 0.05, y + h * 0.44],
                fill=(250, 250, 246))
    d.ellipse([cx - w * 0.15, y + h * 0.32, cx - w * 0.09, y + h * 0.42],
              fill=(250, 250, 246))


def ill_cost(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[2])
    for i, bh in enumerate([0.16, 0.28, 0.42, 0.58]):
        bx = x + w * 0.10 + i * w * 0.14
        d.rectangle([bx, y + h * 0.88 - h * bh, bx + w * 0.09, y + h * 0.88],
                    fill=NAVY)
    d.ellipse([x + w * 0.66, y + h * 0.12, x + w * 0.94, y + h * 0.56],
              fill=GOLD, outline=INK)
    d.text((x + w * 0.74, y + h * 0.16), "$", font=sans_b(int(h * 0.32)),
           fill=INK)


def ill_summit(d, x, y, w, h):
    """Hero illustration: Shenzhen skyline + 3 flag poles + round table."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(233, 224, 196))
    # skyline silhouettes
    for bx, bw, bh in [(0.02, 0.08, 0.30), (0.12, 0.06, 0.42),
                       (0.20, 0.09, 0.26), (0.31, 0.07, 0.36),
                       (0.40, 0.08, 0.22), (0.50, 0.06, 0.34),
                       (0.58, 0.09, 0.24), (0.69, 0.07, 0.38),
                       (0.78, 0.08, 0.28), (0.88, 0.07, 0.32)]:
        d.rectangle([x + bx * w, y + h * 0.86 - bh * h, x + (bx + bw) * w,
                     y + h * 0.86], fill=NAVY)
    # three flag poles
    for fx, fc in [(0.30, RED), (0.50, NAVY), (0.70, GOLD)]:
        d.line([x + fx * w, y + h * 0.08, x + fx * w, y + h * 0.86],
               fill=INK, width=2)
        d.rectangle([x + fx * w, y + h * 0.08, x + (fx + 0.05) * w,
                     y + h * 0.16], fill=fc)
    # round table with three seated figures (dots/blocks, no faces)
    d.ellipse([x + w * 0.36, y + h * 0.68, x + w * 0.64, y + h * 0.84],
              fill=(196, 120, 60), outline=INK)
    for cx, c in [(0.41, RED), (0.50, NAVY), (0.59, GOLD)]:
        d.ellipse([x + cx * w - 6, y + h * 0.56, x + cx * w + 6,
                   y + h * 0.68], fill=c, outline=INK)
        d.rectangle([x + cx * w - 7, y + h * 0.68, x + cx * w + 7,
                     y + h * 0.76], fill=c, outline=INK)


ILL = {"summit": ill_summit, "court": ill_court, "ipo": ill_ipo,
       "parliament": ill_parliament, "painting": ill_painting,
       "probe": ill_probe, "game": ill_game, "tank": ill_tank,
       "cost": ill_cost, "euro": ill_euro, "cyclone": ill_cyclone,
       "chip": ill_chip, "bridge": ill_bridge}

# -------------------------------------------------------------------- layout
DATE_TEXT = "Thursday 19 November 2026"
SUBLINE = ("From the first wires of the morning to the last edition at night "
           "\u2014 Thursday, hour by hour.")
KICKER_LEFT = "THE DAY IN WORLD NEWS"
KICKER_RIGHT = "40 STORIES · 6 CONTINENTS · ONE DAY"

CARD_BY_NUM = {c[0]: c for c in CARDS}


def draw_masthead(d):
    tracked(d, (M, 12), KICKER_LEFT, sans_b(11), INK, track=2)
    rw = tracked_width(d, KICKER_RIGHT, sans_b(11), track=2)
    tracked(d, (W - M - rw, 12), KICKER_RIGHT, sans_b(11), RED, track=2)
    size = 58
    f = serif_b(size)
    while d.textlength(DATE_TEXT, font=f) > CW and size > 40:
        size -= 2
        f = serif_b(size)
    d.text((M, 26), DATE_TEXT, font=f, fill=INK)
    d.rectangle([M, 92, W - M, 94], fill=RED)
    d.text((M, 100), SUBLINE, font=serif_i(14), fill=INK)


def draw_band_card(d, x, y, w, h, num):
    _n, kick, head, deck, ill_key, tint = CARD_BY_NUM[num]
    # icon-left: small square illustration, text to its right
    ILL[ill_key](d, x, y + 8, 54, 54)
    tx = x + 66
    tw = w - 66 - 4
    num_circle(d, tx + 8, y + 16, num, r=8)
    tracked(d, (tx + 22, y + 10), kick, sans_b(10), RED, track=1)
    hf = serif_b(15)
    hlines = wrap(d, head, hf, tw)
    if len(hlines) > 2:
        print(f"OVERFLOW headline {num}: {hlines}")
    hy = y + 28
    for ln in hlines[:2]:
        d.text((tx, hy), ln, font=hf, fill=INK)
        hy += 17
    df = sans(10)
    dlines = wrap(d, deck, df, tw)
    if len(dlines) > 2:
        print(f"OVERFLOW deck {num}: {dlines}")
    dy = hy + 3
    for ln in dlines[:2]:
        d.text((tx, dy), ln, font=df, fill=INK)
        dy += 13


def draw_hero(d, y, h):
    num, kick, head, deck, ill_key = HERO
    ILL[ill_key](d, BAND_X0, y + 8, 300, h - 16)
    tx = BAND_X0 + 316
    tw = BAND_X1 - tx
    num_circle(d, tx + 9, y + 18, num, r=9)
    tracked(d, (tx + 24, y + 11), kick, sans_b(11), RED, track=1)
    hf = serif_b(24)
    hlines = wrap(d, head, hf, tw)
    if len(hlines) > 2:
        print(f"OVERFLOW hero headline: {hlines}")
    hy = y + 32
    for ln in hlines[:2]:
        d.text((tx, hy), ln, font=hf, fill=INK)
        hy += 27
    df = sans(12)
    dlines = wrap(d, deck, df, tw)
    if len(dlines) > 3:
        print(f"OVERFLOW hero deck: {dlines}")
    dy = hy + 4
    for ln in dlines[:3]:
        d.text((tx, dy), ln, font=df, fill=INK)
        dy += 15


def draw_timeline(d):
    # spine
    d.line([SPINE_X, BANDS[0][1], SPINE_X, BANDS[-1][1] + BANDS[-1][2]],
           fill=TEAL, width=2)
    card_w = (BAND_X1 - BAND_X0 - 2 * 8) // 3
    card_xs = [BAND_X0, BAND_X0 + card_w + 8, BAND_X0 + 2 * (card_w + 8)]
    for phase, y, h, nums in BANDS:
        cy = y + h // 2
        # phase label in the left rail, right-aligned to x=100
        lf = sans_b(10)
        if len(phase) == 1:
            lw = d.textlength(phase[0], font=lf)
            d.text((100 - lw, cy - 5), phase[0], font=lf, fill=RED)
        else:
            d.text((100 - d.textlength(phase[0], font=lf), cy - 11),
                   phase[0], font=lf, fill=RED)
            d.text((100 - d.textlength(phase[1], font=lf), cy + 1),
                   phase[1], font=lf, fill=RED)
        d.ellipse([SPINE_X - 5, cy - 5, SPINE_X + 5, cy + 5], fill=RED)
        # hairline separators
        d.line([M, y, W - M, y], fill=(170, 160, 140), width=1)
        if nums == [7]:
            draw_hero(d, y, h)
        else:
            for n, cx in zip(nums, card_xs):
                draw_band_card(d, cx, y, card_w, h, n)
    d.line([M, BANDS[-1][1] + BANDS[-1][2], W - M,
            BANDS[-1][1] + BANDS[-1][2]], fill=(170, 160, 140), width=1)


def draw_briefs(d):
    y0 = 656
    d.line([M, y0, W - M, y0], fill=INK, width=1)
    tracked(d, (M, y0 + 6), "ALSO ON THURSDAY 19 NOVEMBER 2026", sans_b(11),
            INK, track=2)
    d.line([M, y0 + 22, W - M, y0 + 22], fill=INK, width=1)
    col_w = (CW - 2 * 12) // 3
    col_x = [M, M + col_w + 12, M + 2 * (col_w + 12)]
    for ci in range(3):
        for ri, (num, lead, text) in enumerate(BRIEFS[ci * 9:(ci + 1) * 9]):
            y = y0 + 28 + ri * 14
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


def draw_map(d):
    hy = 816
    tracked(d, (M, hy), "WHERE IT HAPPENED", sans_b(11), INK, track=2)
    legend = "pin: stories 1–13  ·  star: 2  ·  dot: briefs 14–40"
    lw = d.textlength(legend, font=sans(10))
    d.text((W - M - lw, hy + 1), legend, font=sans(10), fill=GREY)
    mx, my, mw, mh = M, 830, CW, 110
    d.rectangle([mx, my, mx + mw, my + mh], fill=MAP_BG, outline=INK)
    step = 5
    for gx in range(mx + 3, mx + mw - 2, step):
        for gy in range(my + 3, my + mh - 2, step):
            lon = (gx - mx) / mw * 360.0 - 180.0
            lat = MAP_LAT_TOP - (gy - my) / mh * (MAP_LAT_TOP - MAP_LAT_BOT)
            if on_land(lon, lat):
                d.ellipse([gx - 1.4, gy - 1.4, gx + 1.4, gy + 1.4],
                          fill=MAP_DOT)
    for _num, lon, lat in DOTS:
        x, y = project(lon, lat, mx, my, mw, mh)
        d.ellipse([x - 2.2, y - 2.2, x + 2.2, y + 2.2], fill=RED)
    for num, lon, lat, dx, dy in PINS:
        ax, ay = project(lon, lat, mx, my, mw, mh)
        lx, ly = ax + dx, ay + dy
        d.line([ax, ay, lx, ly], fill=INK, width=1)
        d.ellipse([ax - 2, ay - 2, ax + 2, ay + 2], fill=INK)
        num_circle(d, lx, ly, num, r=7)
    # Voyager 1 has no place on Earth: red star, top-right of the panel,
    # label on a mint patch so dots never show through the text.
    sx, sy = mx + mw - 24, my + 16
    label = "2 · VOYAGER 1 — ONE LIGHT-DAY OUT"
    lf = sans_b(9)
    lw = d.textlength(label, font=lf)
    d.rectangle([sx - 14 - lw, sy - 8, sx - 10, sy + 8], fill=MAP_BG)
    d.text((sx - 12 - lw, sy - 5), label, font=lf, fill=RED)
    star = []
    for i in range(10):
        r = 8 if i % 2 == 0 else 3.5
        a = -math.pi / 2 + i * math.pi / 5
        star.append((sx + r * math.cos(a), sy + r * math.sin(a)))
    d.polygon(star, fill=RED)


def draw_footer(d):
    d.line([M, 948, W - M, 948], fill=INK, width=2)
    d.text((M, 954),
           "Every story was reported on 19 November 2026; disputed claims "
           "are attributed.", font=sans(10), fill=GREY)
    d.text((M, 968),
           "Sources: Reuters · AP · AFP · BBC · Al Jazeera. "
           "Original drawings.", font=sans(10), fill=GREY)


def build(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_timeline(d)
    draw_briefs(d)
    draw_map(d)
    draw_footer(d)
    img.save(out_path, "PNG", optimize=True)
    total = len(CARDS) + 1 + len(BRIEFS)
    print(f"wrote {out_path} ({total} stories)")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "entry.png"))
