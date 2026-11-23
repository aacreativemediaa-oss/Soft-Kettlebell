"""Track a coloured object (pink kettlebell / white shoes) through a clip and print its path.
    python3 tools/track_color.py clip.mp4 pink|shoe
"""
import subprocess, sys
import numpy as np
clip, what = sys.argv[1], sys.argv[2]
W, H, FPS = 108, 192, 20
raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", clip, "-vf", f"fps={FPS},scale={W}:{H}", "-pix_fmt", "rgb24",
                      "-f", "rawvideo", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).astype(int)
out = []
for f in fr:
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    if what == "pink":
        m = (r > 170) & (r - g > 45) & (b > g) & (r - b > 10)
    else:
        m = (r > 200) & (g > 190) & (b > 160) & (np.abs(r - g) < 40)
        m[: H // 3] = False
    ys, xs = np.nonzero(m)
    if len(xs) < 4:
        out.append((np.nan, np.nan, np.nan)); continue
    out.append((xs.mean(), ys.mean(), np.percentile(ys, 5)))
a = np.array(out)
for i in range(0, len(a), 2):
    print(f"{i / FPS:5.2f} x={a[i,0]:5.1f} y={a[i,1]:5.1f} top={a[i,2]:5.1f}")
