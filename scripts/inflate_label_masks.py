#!/usr/bin/env python3
import re
import sys
from pathlib import Path

# Matches D2 mask label rect paths like: M265 86h94v21h-94z
RECT_RE = re.compile(
    r"M(?P<x>-?\d+(?:\.\d+)?)\s+(?P<y>-?\d+(?:\.\d+)?)"
    r"h(?P<w>\d+(?:\.\d+)?)v(?P<h>\d+(?:\.\d+)?)h-(?P=w)z"
)


def inflate_rect_path(d: str, scale: float, pad_x: float, pad_y: float) -> str:
    m = RECT_RE.fullmatch(d.strip())
    if not m:
        return d  # leave unchanged if it doesn't match our simple rect form

    x = float(m.group("x"))
    y = float(m.group("y"))
    w = float(m.group("w"))
    h = float(m.group("h"))

    new_w = w * scale + 2 * pad_x
    new_h = h * scale + 2 * pad_y

    # keep it centered relative to original
    x -= (new_w - w) / 2.0
    y -= (new_h - h) / 2.0

    # Rebuild path (keep same pattern D2 uses)
    # Use minimal decimals to avoid noise
    def fmt(v: float) -> str:
        s = f"{v:.3f}".rstrip("0").rstrip(".")
        return s if s else "0"

    return f"M{fmt(x)} {fmt(y)}h{fmt(new_w)}v{fmt(new_h)}h-{fmt(new_w)}z"


def main():
    if len(sys.argv) < 2:
        print(
            "usage: inflate_label_masks.py <svg_path> [scale] [pad_x] [pad_y]",
            file=sys.stderr,
        )
        sys.exit(2)

    svg_path = Path(sys.argv[1])
    scale = float(sys.argv[2]) if len(sys.argv) > 2 else 1.25
    pad_x = float(sys.argv[3]) if len(sys.argv) > 3 else 6.0
    pad_y = float(sys.argv[4]) if len(sys.argv) > 4 else 4.0

    txt = svg_path.read_text(encoding="utf-8")

    # Only touch <mask ...> blocks, and only rect-form <path d="..."> entries inside them.
    def repl_mask(match: re.Match) -> str:
        mask_block = match.group(0)

        def repl_path(m2: re.Match) -> str:
            d = m2.group("d")
            new_d = inflate_rect_path(d, scale=scale, pad_x=pad_x, pad_y=pad_y)
            return m2.group(0).replace(d, new_d)

        # Replace d="...": only those that match RECT_RE
        mask_block = re.sub(r'd="([^"]+)"', lambda m2: repl_path(m2), mask_block)
        return mask_block

    txt2 = re.sub(r"<mask\b.*?</mask>", repl_mask, txt, flags=re.DOTALL)

    svg_path.write_text(txt2, encoding="utf-8")


if __name__ == "__main__":
    main()
