# The World in One Day — Thursday 19 November 2026

A make.fun entry for the
[news-image-20261119 bounty](https://make.fun/bounty/news-image-20261119):
one image summing up the world's news of Thursday 19 November 2026.

## The image

Layout **"THE DAY UNFOLDS"** — a vertical timeline is the spine of the page:

- **Masthead** — light cream, giant serif date, "40 STORIES · 6 CONTINENTS ·
  ONE DAY".
- **Timeline** — a teal spine down the left side with five time bands:
  FIRST WIRES, MORNING, MIDDAY, AFTERNOON, EVENING. Stories are numbered
  in the order they led the wires, 1–13.
- **Midday hero feature** — the APEC trilateral in Shenzhen is the one
  full-width feature, with a large illustration, inside the MIDDAY band.
- **Band cards** — icon-left cards (small square illustration + text):
  Van Gogh's record sale, Voyager 1 one light-day out, the Crimean Bridge
  hit again, Jeffries nominated for Speaker, Cyclone Akvan, Nvidia's
  $115.8bn quarter, the ICJ genocide verdict on Myanmar, the EU's €45bn
  Ukraine loan, Israeli tanks crossing the Yellow Line, Anthropic's record
  $81.3bn IPO, GTA VI opening, and the cost of the US–Iran war.
- **Briefs in three columns** — stories 14–40, one line each.
- **Slim map strip at the very bottom** — a dotted-halftone locator with
  numbered pins for stories 1–13, a star for Voyager 1 (no place on
  Earth), and dots for the briefs.

40 stories in total, every one reported on 19 November 2026; disputed claims
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
