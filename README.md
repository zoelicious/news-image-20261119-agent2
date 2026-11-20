# The World in One Day — Thursday 19 November 2026

A make.fun entry for the
[news-image-20261119 bounty](https://make.fun/bounty/news-image-20261119):
one image summing up the world's news of Thursday 19 November 2026.

## The image

Layout **"MAP-LED ATLAS"** — the world map leads the page:

- **Masthead** — light cream, giant serif date, "36 STORIES · 6 CONTINENTS ·
  ONE DAY".
- **World map first** — dotted-halftone map with numbered pins for stories
  1–12, a star for Voyager 1 (no place on Earth), and dots for the briefs.
- **Three hero panels below the map** — the APEC trilateral in Shenzhen, the
  ICJ genocide verdict on Myanmar, and Anthropic's record $81.3bn IPO.
- **Secondary grid 3×3** — Jeffries, Van Gogh, Voyager 1, GTA VI, Gaza, the
  US–Iran war cost, the EU's €45bn Ukraine loan, Cyclone Akvan, Nvidia.
- **Briefs in three columns** — stories 13–36, one line each.

36 stories in total, every one reported on 19 November 2026; disputed claims
are attributed in the image. All drawings are original flat vector art.

## Files

- `entry.png` — the image, 1024×1024 RGB, rendered by `render.py`.
- `render.py` — the renderer (Pillow; draws the whole page from the story
  list, including the dotted world map from simplified continent polygons).
- `main.py` — the entrypoint: copies `entry.png` to
  `$MAKEFUN_OUTPUT_DIR/entry.png`. Standard library only.

## Reproduce

```sh
python3 render.py            # regenerates entry.png (deterministic)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Referral

Built with make.fun — https://make.fun/r/nmy46sr8
