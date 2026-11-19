"""Give every footage clip the same ambient level: clips louder than the quiet exercise footage
are turned down so their integrated loudness matches TARGET (never boosted; 30 % is the ceiling).
Writes "vol" into tools/clips.json.   python3 tools/level_footage.py
"""
import json, os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
TARGET = -46.5  # LUFS of the raw exercise clips (median of c02-c07)
clips = json.load(open(os.path.join(HERE, "clips.json")))
for c in clips:
    out = subprocess.run(["ffmpeg", "-nostdin", "-i", os.path.join(ROOT, "assets/footage", c["id"] + ".mp4"),
                          "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])
    gain = min(1.0, 10 ** ((TARGET - lufs) / 20))
    c["lufs"] = lufs
    c["vol"] = round(0.3 * gain, 4)
    print(f'{c["id"]} {lufs:6.1f} LUFS -> volume {c["vol"]}')
json.dump(clips, open(os.path.join(HERE, "clips.json"), "w"), indent=1)
