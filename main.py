#!/usr/bin/env python3
"""Entrypoint for the news-image-20261119 entry (agent 2, noble-robin-77).

Copies the committed entry.png to $MAKEFUN_OUTPUT_DIR/entry.png.
Standard library only. No network. Deterministic: both runs write the
same bytes, because the file is copied, never regenerated.
"""
import os
import shutil
import sys


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
