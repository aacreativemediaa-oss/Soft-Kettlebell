"""Check the rendered film's audio still lines up with the original voiceover.

Cross-correlates the render's mix against the original VO in 5 s windows and reports the
lag of each window (should be ~0 ms everywhere) and the correlation strength.

    python3 tools/verify_vo_sync.py renders/out.mp4 assets/audio/voiceover.m4a
"""
import subprocess
import sys

import numpy as np

SR = 8000


def pcm(path):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-map", "0:a:0", "-ac", "1",
                          "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768


def main(render, vo):
    a, b = pcm(render), pcm(vo)
    print(f"render audio {len(a) / SR:.3f}s, original VO {len(b) / SR:.3f}s")
    win, maxlag = 5 * SR, int(0.2 * SR)
    worst = 0
    for st in range(0, len(b) - win, win):
        ref = b[st:st + win]
        seg = a[max(0, st - maxlag): st + win + maxlag]
        if len(seg) < len(ref):
            break
        c = np.correlate(seg, ref, mode="valid")
        k = int(np.argmax(c))
        lag = (k - (st - max(0, st - maxlag))) / SR * 1000
        r = c[k] / (np.linalg.norm(ref) * np.linalg.norm(seg[k:k + len(ref)]) + 1e-12)
        worst = max(worst, abs(lag))
        print(f"  {st / SR:5.1f}s  lag {lag:+6.1f} ms  corr {r:.3f}")
    print(f"max |lag| = {worst:.1f} ms")


if __name__ == "__main__":
    main(*sys.argv[1:3])
