#!/usr/bin/env bash
set -euo pipefail

in="${1:?usage: render.sh input.d2 [name]}"
name="${2:-$(basename "$in" .d2)}"

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
outdir="$root/out"

mkdir -p "$outdir"

svg="$outdir/${name}.svg"
pdf="$outdir/${name}.pdf"
png="$outdir/${name}.png"

# ---- Render SVG with Office-friendly styling ----
d2 "$in" "$svg"

# --- Typography scaling for Office ---
# D2 emits inline: style="...font-size:16px"
# We scale by editing common sizes. Adjust SCALE_* to taste.
SCALE_16_TO="20"
SCALE_14_TO="18"
SCALE_12_TO="16"

# macOS sed in-place
sed -i '' -E "s/font-size:16px/font-size:${SCALE_16_TO}px/g" "$svg"
sed -i '' -E "s/font-size:14px/font-size:${SCALE_14_TO}px/g" "$svg"
sed -i '' -E "s/font-size:12px/font-size:${SCALE_12_TO}px/g" "$svg"

# --- Optional: slightly thicker lines for projector/readability ---
# D2 uses stroke-width:2 in your snippet.
sed -i '' -E "s/stroke-width:2/stroke-width:2.5/g" "$svg"

# ---- Optional: optimize SVG ----
if command -v svgo >/dev/null 2>&1; then
  svgo --multipass "$svg" -o "$svg"
fi

# ---- Optional exports for fallback workflows ----
if command -v rsvg-convert >/dev/null 2>&1; then
  rsvg-convert -f pdf -o "$pdf" "$svg"
  rsvg-convert -f png -o "$png" -d 200 -p 200 "$svg"
fi

echo "Wrote: $svg"
[ -f "$pdf" ] && echo "Wrote: $pdf"
[ -f "$png" ] && echo "Wrote: $png"
