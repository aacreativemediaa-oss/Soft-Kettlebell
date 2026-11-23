#!/usr/bin/env bash
# Trim + reframe each selected source clip to 1080x1920 @ 60fps, H.264, keyframe every 0.5 s.
# iPhone HDR sources (HLG, BT.2020) are tone-mapped to SDR BT.709 so the film renders as SDR
# (otherwise HyperFrames promotes the whole render to HDR and the graphics look washed out).
# Usage: tools/prep_footage.sh <dir-with-raw-footage>
set -euo pipefail
RAW="$1"; HERE="$(cd "$(dirname "$0")/.." && pwd)"
TM="zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv"
python3 - "$HERE/tools/clips.json" <<'PY' | while IFS=$'\t' read -r id src ss dur; do
import json,sys
for c in json.load(open(sys.argv[1])):
    print(f"{c['id']}\t{c['src']}\t{c['ss']}\t{c['end']-c['start']+0.25:.3f}")
PY
  trc=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer -of csv=p=0 "$RAW/$src" | tr -d ',')
  vf="scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=60"
  [ "$trc" = "arib-std-b67" ] && vf="$vf,$TM"
  ffmpeg -nostdin -v error -y -ss "$ss" -t "$dur" -i "$RAW/$src" \
    -vf "$vf,format=yuv420p" -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
    -c:v libx264 -preset slow -crf 17 -g 30 -keyint_min 30 -sc_threshold 0 -movflags +faststart \
    -map 0:v:0 -map 0:a:0 -c:a aac -b:a 160k -ar 48000 -ac 2 \
    "$HERE/assets/footage/$id.mp4"
  echo "$id <- $src ($ss +$dur) ${trc:-sdr}"
done
