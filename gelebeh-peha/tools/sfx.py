"""Synthesise every sound effect used in the film (no samples, no music).

Writes 48 kHz mono 16-bit WAVs to assets/sfx/. Deterministic: a fixed seed per file.
Each file is peak-normalised to -6 dBFS; the mix level is set in index.html (data-volume),
so the effects sit well under the voiceover.

    python3 tools/sfx.py
"""
import os
import wave

import numpy as np

SR = 48000
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "sfx")


def t_axis(dur):
    return np.arange(int(SR * dur)) / SR


def env_ad(n, attack, decay_pow=3.0):
    """Linear attack (seconds) then a power-curve decay to zero."""
    e = np.ones(n)
    a = max(1, int(attack * SR))
    e[:a] = np.linspace(0, 1, a)
    rest = n - a
    e[a:] = (1 - np.linspace(0, 1, rest)) ** decay_pow
    return e


def one_pole_lp(x, cutoff):
    """Time-varying one-pole low-pass; cutoff may be an array (Hz)."""
    cutoff = np.broadcast_to(cutoff, x.shape)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        a = 1 - np.exp(-2 * np.pi * cutoff[i] / SR)
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def bandpass(x, center, q=1.2):
    """Crude time-varying band-pass: LP(center*1.6) - LP(center/1.6)."""
    hi = one_pole_lp(x, center * (1 + 0.6 / q))
    lo = one_pole_lp(x, center / (1 + 0.6 / q))
    return hi - lo


def fade_edges(x, ms=4):
    n = int(SR * ms / 1000)
    x[:n] *= np.linspace(0, 1, n)
    x[-n:] *= np.linspace(1, 0, n)
    return x


def save(name, x, peak_db=-6.0):
    x = fade_edges(np.asarray(x, dtype=np.float64))
    x = x / (np.max(np.abs(x)) + 1e-9) * (10 ** (peak_db / 20))
    os.makedirs(OUT, exist_ok=True)
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    print(f"{name}.wav  {len(x) / SR:.2f}s")


def whoosh(seed, dur=0.55, f0=500, f1=3800, peak_at=0.6):
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    n = len(t)
    noise = rng.standard_normal(n)
    # sweep the band up then slightly down, loudest at peak_at of the clip
    u = t / dur
    center = f0 + (f1 - f0) * np.sin(np.clip(u / peak_at, 0, 1) * np.pi / 2) ** 2
    center = np.where(u > peak_at, f1 - (f1 - f0) * 0.35 * (u - peak_at) / (1 - peak_at), center)
    x = bandpass(noise, center, q=0.9)
    amp = np.where(u < peak_at, (u / peak_at) ** 2.2, (1 - (u - peak_at) / (1 - peak_at)) ** 1.6)
    return x * amp


def pop(seed, f_start=900, f_end=380, dur=0.12):
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    f = f_end + (f_start - f_end) * np.exp(-t * 55)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * env_ad(len(t), 0.002, 4)
    click = rng.standard_normal(len(t)) * np.exp(-t * 900) * 0.25
    return body + click


def ding(f=1318.5, dur=1.1):
    t = t_axis(dur)
    partials = [(1.0, 1.0, 3.2), (2.0, 0.35, 5.0), (2.76, 0.22, 6.5), (5.4, 0.08, 9.0)]
    x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * d) for m, a, d in partials)
    atk = np.minimum(1, t / 0.003)
    return x * atk


def impact(seed, dur=0.9):
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    f = 42 + 120 * np.exp(-t * 18)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    noise = one_pole_lp(rng.standard_normal(len(t)), 1800) * np.exp(-t * 22) * 0.9
    thump = np.tanh(1.8 * (sub + noise))
    return thump


def cha_ching(seed):
    rng = np.random.default_rng(seed)
    dur = 0.95
    t = t_axis(dur)
    x = np.zeros(len(t))
    # "cha": short bright metallic noise burst
    burst = bandpass(rng.standard_normal(len(t)), 5200, q=2.0) * np.exp(-t * 40)
    x += burst * 1.4
    # "ching": two inharmonic bell strikes, the second at +0.12 s
    for delay, base in ((0.0, 2093.0), (0.12, 2637.0)):
        tt = np.clip(t - delay, 0, None)
        on = (t >= delay).astype(float)
        bell = sum(a * np.sin(2 * np.pi * base * m * tt) * np.exp(-tt * d)
                   for m, a, d in [(1, 1.0, 4.5), (2.4, 0.5, 7.0), (3.9, 0.3, 10.0), (5.2, 0.15, 13.0)])
        x += bell * on * 0.8
    # coin rattle
    rattle = rng.standard_normal(len(t)) * (np.sin(2 * np.pi * 28 * t) > 0.6) * np.exp(-t * 6) * 0.15
    return x + bandpass(rattle, 7000)


def riser(seed, dur=1.6):
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    u = t / dur
    center = 300 * (12000 / 300) ** (u ** 1.4)
    noise = bandpass(rng.standard_normal(len(t)), np.minimum(center, 14000), q=1.4)
    tone_f = 180 * 2 ** (u * 2.5)
    tone = np.sin(2 * np.pi * np.cumsum(tone_f) / SR) * 0.25
    amp = u ** 2.4
    x = (noise + tone) * amp
    tail = int(0.03 * SR)
    x[-tail:] *= np.linspace(1, 0, tail)
    return x


def zap(seed, dur=0.28):
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    f = 2400 * np.exp(-t * 14) + 160
    sq = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR))
    sq = one_pole_lp(sq, 6000)
    fm = 1 + 0.3 * np.sin(2 * np.pi * 70 * t)
    return sq * fm * env_ad(len(t), 0.002, 2.2) + rng.standard_normal(len(t)) * np.exp(-t * 60) * 0.1


if __name__ == "__main__":
    save("whoosh-a", whoosh(11, 0.50, 450, 3600, 0.62))
    save("whoosh-b", whoosh(23, 0.45, 650, 4800, 0.55))
    save("whoosh-c", whoosh(37, 0.60, 380, 3000, 0.66))
    save("pop-a", pop(5, 950, 420))
    save("pop-b", pop(9, 1250, 560, 0.10))
    save("ding", ding())
    save("impact", impact(3))
    save("cha-ching", cha_ching(17))
    save("riser", riser(29))
    save("zap", zap(41))
