"""Footage sound standard: every clip's original sound sits at the same loudness in the final mix.

Each clip is set so its integrated loudness after the clip volume is TARGET LUFS (default -57,
about 27 dB under a -30 LUFS voiceover). Loud clips are turned down; quiet clips are turned up by at
most MAX_BOOST_DB so background hiss is not pushed up too far. Clips flagged "music": true stay muted.
Writes "vol" (and the measured "lufs") into tools/clips.json of the project.

    python3 tools/level_footage.py [--target -57] [--max-boost 12]
"""
import argparse, json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
ap = argparse.ArgumentParser()
ap.add_argument("--target", type=float, default=-57.0)
ap.add_argument("--max-boost", type=float, default=12.0)
a = ap.parse_args()
clips = json.load(open(os.path.join(HERE, "clips.json")))
for c in clips:
    out = subprocess.run(["ffmpeg", "-nostdin", "-i", os.path.join(ROOT, "assets/footage", c["id"] + ".mp4"),
                          "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])
    gain_db = min(a.target - lufs, a.max_boost)
    c["lufs"] = lufs
    c["vol"] = round(min(3.98, 10 ** (gain_db / 20)), 4)
    print(f'{c["id"]} {lufs:6.1f} LUFS -> volume {c["vol"]} ({gain_db:+.1f} dB) -> {lufs + gain_db:6.1f} LUFS'
          + ("  [muted: music]" if c.get("music") else ""))
json.dump(clips, open(os.path.join(HERE, "clips.json"), "w"), indent=1)
