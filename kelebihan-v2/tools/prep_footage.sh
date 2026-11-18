#!/usr/bin/env bash
# Trim + reframe each selected source clip to 1080x1920 @ 60fps, H.264, keyframe every 0.5 s.
# Usage: tools/prep_footage.sh <dir-with-raw-footage>
set -euo pipefail
RAW="$1"; HERE="$(cd "$(dirname "$0")/.." && pwd)"
python3 - "$HERE/tools/clips.json" <<'PY' | while IFS=$'\t' read -r id src ss dur; do
import json,sys
for c in json.load(open(sys.argv[1])):
    print(f"{c['id']}\t{c['src']}\t{c['ss']}\t{c['end']-c['start']+0.25:.3f}")
PY
  ffmpeg -nostdin -v error -y -ss "$ss" -t "$dur" -i "$RAW/$src" \
    -vf "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=60,format=yuv420p" \
    -c:v libx264 -preset slow -crf 17 -g 30 -keyint_min 30 -sc_threshold 0 -movflags +faststart \
    -map 0:v:0 -map 0:a:0 -c:a aac -b:a 160k -ar 48000 -ac 2 \
    "$HERE/assets/footage/$id.mp4"
  echo "$id <- $src ($ss +$dur)"
done
