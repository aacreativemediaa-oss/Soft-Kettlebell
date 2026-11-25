"""Find rep moments in a clip by tracking the top of the moving body (head) over time.

Background = per-pixel median of the clip; foreground = pixels far from it. The top foreground row in the
central columns follows the head: a squat/lunge rep is a local *maximum* of that row (lowest head),
a kettlebell swing rep is a local minimum of the kettlebell's height (use --mode swing: tracks the highest
foreground pixel left of centre... simplified: lowest head = hinge bottom, rep counted at the next top).

    python3 tools/rep_times.py assets/footage/c05.mp4 [--mode squat|swing] [--fps 20]
Prints the candidate rep times (clip seconds).
"""
import argparse, subprocess
import numpy as np

ap = argparse.ArgumentParser(); ap.add_argument("clip"); ap.add_argument("--mode", default="squat")
ap.add_argument("--fps", type=float, default=20); a = ap.parse_args()
W, H = 108, 192
raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", a.clip, "-vf", f"fps={a.fps},scale={W}:{H},format=gray",
                      "-f", "rawvideo", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
bg = np.median(fr, axis=0)
fg = np.abs(fr - bg) > 28
cols = slice(W // 4, 3 * W // 4)
top = []
for m in fg:
    rows = np.where(m[:, cols].sum(axis=1) >= 3)[0]
    top.append(rows[0] if len(rows) else np.nan)
top = np.array(top, float)
# smooth
k = np.ones(5) / 5
s = np.convolve(np.nan_to_num(top, nan=np.nanmean(top)), k, mode="same")
t = np.arange(len(s)) / a.fps
sig = s if a.mode == "squat" else -s
peaks = [i for i in range(3, len(sig) - 3) if sig[i] == max(sig[i - 3:i + 4]) and sig[i] - np.min(sig[max(0, i - 15):i + 16]) > 4]
print("head-top row:", " ".join(f"{t[i]:.2f}:{s[i]:.0f}" for i in range(0, len(s), 4)))
print("reps at:", [round(t[i], 2) for i in peaks])
