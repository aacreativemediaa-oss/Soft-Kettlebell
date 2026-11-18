"""Generate the HyperFrames project files for the Soft Kettlebell vertical edit.

Inputs (all in tools/):
  clips.json              the 10 cuts: source file, trim, film start/end
  transcript_whisper.json word timings of the original voiceover (Whisper large-v3)
  vo_silences.txt         silence gaps in the voiceover (ffmpeg silencedetect, -40 dB)

Outputs:
  index.html                 root: 10 footage clips, 10 graphics scenes, captions, fx, VO, SFX
  compositions/g01..g10.html one graphics overlay per clip
  compositions/captions.html every caption group
  compositions/fx.html       white flash on each cut
  tools/words.json           cleaned word list used for captions

    python3 tools/build.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
W, H, FPS = 1080, 1920, 60
DUR = 59.25  # voiceover length (ffprobe 59.256 s), floored to a whole frame

CLIPS = json.load(open(os.path.join(HERE, "clips.json")))
CUTS = [c["start"] for c in CLIPS[1:]]

# ---------------------------------------------------------------- type scale
# Sizes are 70 % of the first-version scale (hero 200, header 160, sub 120, label 52).
HERO, HEAD, SUB, LABEL = 140, 112, 84, 36
CAPTION = 60
YELLOW, GREEN, PINK, RED, INK = "#FFE600", "#39FF14", "#FF3D8B", "#FF2D2D", "#0B0B0B"

# ---------------------------------------------------------------- words
FIX = {"dari": "dan", "post": "repost", "lengoh": "lenguh", "sadur": "sado",
       "jim": "gym", "limit": "link beg"}
KEYWORDS = {"KALORI", "BURN", "BEBAN", "WORKOUT", "AFTERBURN", "POSTURE", "KETTLEBELL", "CORE",
            "BAHU", "BACK", "TEGAP", "MELENTIK", "CANTIK", "GELEBEH", "PEHA", "PERUT", "LENGAN",
            "TEGANG", "KEMAS", "SADO", "TESTOSTERON", "KONSISTEN", "HASIL", "YAKIN", "MURAH",
            "KARDIO", "JOGGING", "SAVE", "REPOST", "LINK", "KUNING", "LENGUH", "RESISTEN"}
# Clauses already written out by a graphic: their captions are hidden (start, end of the clause).
HIDE = [(0.0, 2.50), (2.80, 4.25), (4.80, 5.80), (6.95, 9.05), (10.30, 12.20), (15.10, 17.15),
        (17.22, 18.75), (19.30, 22.25), (25.00, 26.80), (27.30, 28.55), (30.05, 32.10), (33.28, 35.10),
        (37.90, 39.30), (40.36, 41.30), (41.60, 44.05), (47.45, 48.95), (52.25, 54.70), (55.10, 56.30),
        (57.60, 59.10)]


def load_silences():
    out = []
    for line in open(os.path.join(HERE, "vo_silences.txt")):
        a, b = line.strip().split("-")
        out.append((float(a), float(b)))
    return out


def clean_words():
    sil = load_silences()
    raw = json.load(open(os.path.join(HERE, "transcript_whisper.json")))
    words = []
    for seg in raw:
        for w in seg["words"]:
            text = w["w"].strip()
            s, e = w["s"], w["e"]
            # Whisper starts words early; snap a start that sits in a silence to its end.
            for a, b in sil:
                if a <= s < b:
                    s = b
                if a < e <= b and e - a > 0.05:
                    e = a
            if text.startswith("-") and words:  # "Mula" "-mula" -> "MULA-MULA"
                words[-1]["text"] += text.upper()
                words[-1]["end"] = round(e, 3)
                words[-1]["punct"] = bool(re.search(r"[.,!?]$", text))
                words[-1]["text"] = re.sub(r"[.,!?]$", "", words[-1]["text"])
                continue
            punct = bool(re.search(r"[.,!?]$", text))
            core = re.sub(r"[.,!?]$", "", text)
            core = FIX.get(core.lower(), core)
            words.append({"text": core.upper(), "start": round(s, 3), "end": round(max(e, s + 0.06), 3),
                          "punct": punct})
    for i, w in enumerate(words):
        w["id"] = f"w{i}"
        w["key"] = w["text"] in KEYWORDS
    return words


def hidden(w):
    return any(a <= w["start"] < b for a, b in HIDE)


def group_words(words):
    groups, cur = [], []
    for i, w in enumerate(words):
        if hidden(w):
            if cur:
                groups.append(cur)
                cur = []
            continue
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["start"] - w["end"]) if nxt else 9
        if w["punct"] or gap >= 0.15 or len(cur) == 3 or (nxt and any(w["end"] <= t <= nxt["start"] for t in CUTS)):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    # never leave a lone word after a 3-word group of the same phrase: 3+1 -> 2+2
    out = []
    for g in groups:
        if out and len(g) == 1 and len(out[-1]) == 3 and not out[-1][-1]["punct"] \
                and g[0]["start"] - out[-1][-1]["end"] < 0.15:
            out[-1], g = out[-1][:2], out[-1][2:] + g
        out.append(g)
    return out


# ---------------------------------------------------------------- shared css
FONTS = """
@font-face { font-family: 'Anton'; src: url('assets/fonts/Anton-Regular.woff2') format('woff2'); font-weight: 400; }
@font-face { font-family: 'Montserrat'; src: url('assets/fonts/Montserrat-Variable.woff2') format('woff2'); font-weight: 100 900; }
"""

GFX_CSS = FONTS + f"""
#root {{ position: absolute; inset: 0; overflow: hidden; }}
/* Social safe area (TikTok + Reels + Shorts): y 288-1248; x 120-888 above y 840, x 120-780 below.
   Lower-band blocks are left-aligned from x 120 and at most 660 px wide; .up blocks centre in 120-888. */
.row {{ position: absolute; left: 120px; width: 660px; display: flex; justify-content: flex-start; align-items: center; gap: 22px; }}
.col {{ position: absolute; left: 120px; width: 660px; display: flex; flex-direction: column; align-items: flex-start; gap: 10px; }}
.row.up, .col.up {{ left: 120px; width: 768px; justify-content: center; align-items: center; }}
.hd {{ font-family: 'Anton', sans-serif; text-transform: uppercase; line-height: 1.02; color: #fff;
      -webkit-text-stroke: 12px {INK}; paint-order: stroke fill; letter-spacing: 1px; white-space: nowrap;
      text-shadow: 0 10px 0 rgba(0,0,0,.35); opacity: 0; }}
.hero {{ font-size: {HERO}px; }}
.head {{ font-size: {HEAD}px; }}
.sub {{ font-size: {SUB}px; -webkit-text-stroke-width: 10px; }}
.y {{ color: {YELLOW}; }} .g {{ color: {GREEN}; }} .p {{ color: {PINK}; }}
.pill {{ font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: {LABEL}px; letter-spacing: 1px;
        text-transform: uppercase; color: {INK}; background: {YELLOW}; border: 5px solid {INK};
        border-radius: 999px; padding: 12px 30px; box-shadow: 0 8px 0 {INK}; white-space: nowrap;
        display: flex; align-items: center; gap: 14px; opacity: 0; }}
.pill.dark {{ background: rgba(11,11,11,.88); color: #fff; border-color: #fff; box-shadow: 0 8px 0 rgba(0,0,0,.5); }}
.pill.green {{ background: {GREEN}; }}
.pill.pink {{ background: {PINK}; color: #fff; }}
.pill.white {{ background: #fff; }}
.badge {{ width: 150px; height: 150px; border-radius: 50%; background: {PINK}; border: 8px solid {INK};
         box-shadow: 0 10px 0 {INK}; display: flex; align-items: center; justify-content: center;
         font-family: 'Anton', sans-serif; font-size: {SUB}px; color: #fff; opacity: 0; flex: none; }}
.card {{ background: rgba(11,11,11,.86); border: 5px solid #fff; border-radius: 34px; padding: 30px 38px;
        box-shadow: 0 14px 0 rgba(0,0,0,.45); opacity: 0; }}
.lbl {{ font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: {LABEL}px; color: #fff;
       text-transform: uppercase; letter-spacing: 1px; white-space: nowrap; }}
svg {{ display: block; }}
"""


def scene_file(sid, start, dur, markup, script, extra_css=""):
    return f"""<template>
  <style>{GFX_CSS}{extra_css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}" data-layout-allow-overlap>
{markup}
  </div>
  <script>
    (function () {{
      // Times below are written in film seconds; T(x) converts to this scene's clock.
      const T0 = {start};
      const T = (x) => +(x - T0).toFixed(4);
      const END = T({start + dur:.4f});
      const tl = gsap.timeline({{ paused: true }});
      const q = (s) => "#{sid}-" + s;
{script}
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
"""


# GSAP snippets (film time -> scene time through T())
def slam(sel, t, s0=1.6):
    return (f'      tl.fromTo(q("{sel}"), {{ opacity: 0, scale: {s0} }}, '
            f'{{ opacity: 1, scale: 1, duration: 0.32, ease: "expo.out" }}, T({t}));\n')


def popin(sel, t, s0=0.4, dur=0.42):
    return (f'      tl.fromTo(q("{sel}"), {{ opacity: 0, scale: {s0} }}, '
            f'{{ opacity: 1, scale: 1, duration: {dur}, ease: "back.out(2.2)" }}, T({t}));\n')


def slide(sel, t, x0=-140):
    return (f'      tl.fromTo(q("{sel}"), {{ opacity: 0, x: {x0}, filter: "blur(10px)" }}, '
            f'{{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.38, ease: "expo.out" }}, T({t}));\n')


def blurin(sel, t):
    return (f'      tl.fromTo(q("{sel}"), {{ opacity: 0, filter: "blur(14px)", y: 24 }}, '
            f'{{ opacity: 1, filter: "blur(0px)", y: 0, duration: 0.2, ease: "power4.out" }}, T({t}));\n')


def stamp(sel, t, rot=-8):
    return (f'      tl.fromTo(q("{sel}"), {{ opacity: 0, scale: 2.4, rotation: {rot - 10} }}, '
            f'{{ opacity: 1, scale: 1, rotation: {rot}, duration: 0.26, ease: "power4.out" }}, T({t}));\n')


def out(sels, t):
    lst = ", ".join(f'q("{s}")' for s in sels)
    return (f'      tl.to([{lst}], {{ opacity: 0, filter: "blur(10px)", scale: 0.92, duration: 0.16, ease: "power2.in" }}, T({t}));\n'
            f'      tl.set([{lst}], {{ opacity: 0 }}, T({t + 0.17:.3f}));\n')


CHECK_SVG = ('<svg width="54" height="54" viewBox="0 0 54 54"><circle cx="27" cy="27" r="25" fill="' + GREEN +
             '" stroke="#0B0B0B" stroke-width="4"/><path d="M15 28 l8 8 l16 -18" fill="none" stroke="#0B0B0B" '
             'stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
X_SVG = ('<svg width="{s}" height="{s}" viewBox="0 0 100 100"><path d="M18 18 L82 82 M82 18 L18 82" stroke="' + RED +
         '" stroke-width="16" stroke-linecap="round"/></svg>')
FLAME_SVG = ('<svg width="92" height="118" viewBox="0 0 92 118"><path d="M46 4 C58 30 86 44 84 76 C82 102 64 114 46 114 '
             'C26 114 8 100 8 76 C8 58 20 46 28 36 C30 50 36 56 42 58 C38 40 40 20 46 4 Z" fill="#FF7A00" stroke="#0B0B0B" '
             'stroke-width="6" stroke-linejoin="round"/><path d="M46 60 C54 74 66 80 64 94 C62 106 54 110 46 110 C36 110 '
             '28 104 28 94 C28 84 36 78 40 70 C42 78 46 80 48 80 C46 72 44 66 46 60 Z" fill="' + YELLOW + '"/></svg>')
BOOKMARK_SVG = ('<svg width="44" height="54" viewBox="0 0 44 54"><path id="{id}" d="M6 4 H38 V50 L22 38 L6 50 Z" '
                'fill="#fff" stroke="#0B0B0B" stroke-width="5" stroke-linejoin="round"/></svg>')
CART_SVG = ('<svg width="96" height="86" viewBox="0 0 96 86"><path d="M4 8 H18 L28 58 H80 L90 22 H22" fill="none" '
            'stroke="#0B0B0B" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>'
            '<circle cx="34" cy="76" r="7" fill="#0B0B0B"/><circle cx="74" cy="76" r="7" fill="#0B0B0B"/></svg>')
SPARK_SVG = ('<svg width="{s}" height="{s}" viewBox="0 0 100 100"><path d="M50 0 C54 36 64 46 100 50 C64 54 54 64 50 100 '
             'C46 64 36 54 0 50 C36 46 46 36 50 0 Z" fill="' + YELLOW + '" stroke="#0B0B0B" stroke-width="4"/></svg>')
ARROW_SVG = ('<svg width="110" height="70" viewBox="0 0 110 70"><path d="M10 10 L55 55 L100 10" fill="none" stroke="' + YELLOW +
             '" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def scenes():
    c = {x["id"]: x for x in CLIPS}
    files = {}

    def win(cid):
        return c[cid]["start"], c[cid]["end"] - c[cid]["start"]

    # ---------------- g01 hook (one shot, 0 - 6.70) - upper band, centred in the safe width
    st, du = win("c01")
    m = f"""    <div class="row up" style="top: 300px;"><div id="g01-tag" class="pill pink">Untuk Wanita</div></div>
    <div class="col up" style="top: 372px; gap: 0;">
      <div id="g01-t1" class="hd hero"><span class="p">3</span> KELEBIHAN</div>
      <div id="g01-t2" class="hd sub g">LATIHAN RESISTEN</div>
    </div>
    <div class="row up" style="top: 640px;"><div id="g01-no3" class="pill">No. 3 paling ramai suka!</div></div>
    <div class="row up" style="top: 640px;"><div id="g01-save" class="pill white">{BOOKMARK_SVG.format(id='g01-mark')}Save &amp; repost dulu!</div></div>"""
    s = (f'      tl.fromTo(q("t1"), {{ opacity: 1, scale: 1.35 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }}, 0);\n'
         f'      tl.fromTo(q("tag"), {{ opacity: 1, y: -40 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "expo.out" }}, 0);\n'
         + blurin("t2", 1.46)
         + popin("no3", 3.02)
         + out(["no3"], 4.42)
         + popin("save", 4.82)
         + '      tl.fromTo(q("mark"), { fill: "#ffffff" }, { fill: "' + YELLOW + '", duration: 0.12 }, T(5.30));\n'
         + '      tl.fromTo(q("save"), { scale: 1 }, { scale: 1.12, duration: 0.1, yoyo: true, repeat: 1, ease: "power2.out" }, T(5.30));\n'
         + out(["t1", "t2", "tag", "save"], 6.48))
    files["g01"] = (st, du, scene_file("g01", st, du, m, s))

    # ---------------- g02 #1 bakar kalori (6.70 - 12.45)
    st, du = win("c02")
    m = f"""    <div class="row" style="top: 700px;"><div id="g02-badge" class="badge">#1</div><div id="g02-flame" style="opacity:0">{FLAME_SVG}</div></div>
    <div class="col" style="top: 862px; gap: 0;">
      <div id="g02-t1" class="hd head">BAKAR KALORI</div>
      <div id="g02-t2" class="hd sub y">BANYAK GILA!</div>
    </div>
    <div class="row" style="top: 880px;">
      <div id="g02-card" class="card" style="display:flex; align-items:center; gap: 22px; padding: 26px 32px;">
        <div><div class="lbl" style="font-size: 40px;">Kena kardio je</div><div class="lbl" style="font-size: 40px; color:{YELLOW};">baru burn kalori?</div></div>
        <div id="g02-x" style="opacity:0">{X_SVG.format(s=72)}</div>
      </div>
    </div>"""
    s = (popin("badge", 6.99) + popin("flame", 7.10) + slam("t1", 7.60) + slam("t2", 8.34, 1.4)
         + out(["badge", "flame", "t1", "t2"], 9.0)
         + slide("card", 10.34) + stamp("x", 10.84, -4)
         + out(["card", "x"], 12.28))
    files["g02"] = (st, du, scene_file("g02", st, du, m, s))

    # ---------------- g03 masa + selepas workout, afterburn (12.45 - 19.05)
    st, du = win("c03")
    # Fact image: EPOC diagram (Wikimedia Commons, CC BY-SA 4.0 - credit on screen).
    # Highlights sit over its "Exercise time" (19-62 % of width) and "Recovery time" (62-97 %) areas.
    m = f"""    <div class="row up" style="top: 318px;">
      <div id="g03-fig" class="card" style="background:#fff; border-color:{INK}; padding: 14px 14px 10px; width: 724px;">
        <div style="position: relative; width: 686px; height: 404px;">
          <img src="assets/images/epoc-diagram.jpg" alt="EPOC diagram" style="position:absolute; left:0; top:0; width: 686px; height: 404px; border-radius: 14px;">
          <div id="g03-h1" class="hl" style="left: 18.5%; width: 44%;"></div>
          <div id="g03-h2" class="hl" style="left: 61.8%; width: 36.5%;"></div>
        </div>
        <div class="credit" data-layout-ignore>Rajah EPOC: Henoktade / Wikimedia Commons, CC BY-SA 4.0</div>
      </div>
    </div>
    <div class="col" style="top: 840px; gap: 26px;">
      <div id="g03-c1" class="pill white" style="font-size: 42px;">{CHECK_SVG}Masa workout</div>
      <div id="g03-c2" class="pill white" style="font-size: 42px;">{CHECK_SVG}Selepas workout</div>
    </div>
    <div class="col" style="top: 820px; gap: 0;">
      <div id="g03-t1" class="hd hero"><span class="fire">AFTERBURN</span></div>
      <div id="g03-t2" class="hd head">EFFECT</div>
    </div>"""
    css = f"""
.hl {{ position: absolute; top: 3%; height: 82%; border: 7px solid {PINK}; border-radius: 16px;
      background: rgba(255,61,139,.12); opacity: 0; }}
.hlt {{ position: absolute; left: 50%; top: -30px; margin-left: -110px; width: 220px; text-align: center;
       font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 26px; text-transform: uppercase;
       color: {INK}; background: {YELLOW}; border: 4px solid {INK}; border-radius: 999px; padding: 4px 0; }}
.credit {{ font-family: 'Montserrat', sans-serif; font-weight: 600; font-size: 20px; color: #555; margin-top: 6px; text-align: center; }}
.fire {{ background: linear-gradient(180deg, {YELLOW} 0%, #FF9A00 55%, #FF3D00 100%); -webkit-background-clip: text;
        background-clip: text; color: transparent; }}
#g03-t1 {{ -webkit-text-stroke: 0; }}
#g03-t1 .fire {{ filter: drop-shadow(5px 0 0 #0B0B0B) drop-shadow(-5px 0 0 #0B0B0B)
        drop-shadow(0 5px 0 #0B0B0B) drop-shadow(0 -5px 0 #0B0B0B); }}"""
    s = (popin("fig", 15.20, 0.6)
         + slide("c1", 15.40) + popin("h1", 15.40, 0.9, 0.3)
         + out(["h1"], 16.30) + slide("c2", 16.40, 140) + popin("h2", 16.40, 0.9, 0.3)
         + out(["c1", "c2"], 17.10)
         + slam("t1", 17.52) + blurin("t2", 18.04)
         + out(["t1", "t2", "fig", "h2"], 18.86))
    files["g03"] = (st, du, scene_file("g03", st, du, m, s, css))

    # ---------------- g04 #2 posture + core/bahu/back (19.05 - 27.10)
    st, du = win("c04")
    m = """    <div class="row" style="top: 700px;"><div id="g04-badge" class="badge">#2</div></div>
    <div class="col" style="top: 862px; gap: 0;">
      <div id="g04-t1" class="hd head">TEGAPKAN</div>
      <div id="g04-t2" class="hd head g">POSTURE</div>
    </div>
    <div class="row" style="top: 960px; gap: 24px;">
      <div id="g04-k1" class="pill green" style="font-size: 44px;">Core</div>
      <div id="g04-k2" class="pill green" style="font-size: 44px;">Bahu</div>
      <div id="g04-k3" class="pill green" style="font-size: 44px;">Back</div>
    </div>"""
    s = (popin("badge", 19.32) + slam("t1", 20.38) + slam("t2", 20.74, 1.4)
         + out(["badge", "t1", "t2"], 22.24)
         + popin("k1", 25.02) + popin("k2", 25.81) + popin("k3", 26.28)
         + out(["k1", "k2", "k3"], 26.92))
    files["g04"] = (st, du, scene_file("g04", st, du, m, s))

    # ---------------- g05 lenguh -> tegap & melentik (27.10 - 33.05)
    st, du = win("c05")
    m = f"""    <div class="col" style="top: 840px; gap: 6px;">
      <div id="g05-l1" class="pill dark">Mula-mula</div>
      <div id="g05-a" class="hd head">LENGUH</div>
    </div>
    <div class="col" style="top: 780px; gap: 0;">
      <div id="g05-l2" class="pill dark" style="margin-bottom: 8px;">Lama-lama</div>
      <div id="g05-b1" class="hd head g">TEGAP</div>
      <div id="g05-b2" class="hd head g">&amp; MELENTIK</div>
    </div>
    <div id="g05-s1" style="position:absolute; left: 480px; top: 830px; opacity:0">{SPARK_SVG.format(s=84)}</div>
    <div id="g05-s2" style="position:absolute; left: 700px; top: 1010px; opacity:0">{SPARK_SVG.format(s=64)}</div>
    <div id="g05-s3" style="position:absolute; left: 70px; top: 930px; opacity:0">{SPARK_SVG.format(s=52)}</div>"""
    s = (slide("l1", 27.37) + slam("a", 28.06, 1.3)
         + '      tl.fromTo(q("a"), { rotation: 0 }, { rotation: 3, duration: 0.07, yoyo: true, repeat: 5, ease: "sine.inOut" }, T(28.40));\n'
         + out(["l1", "a"], 29.62)
         + slide("l2", 29.95, 140) + slam("b1", 30.86) + slam("b2", 31.44, 1.3)
         + popin("s1", 32.42, 0, 0.26) + popin("s2", 32.48, 0, 0.26) + popin("s3", 32.54, 0, 0.26)
         + '      tl.fromTo([q("s1"), q("s2"), q("s3")], { rotation: 0 }, { rotation: 60, duration: 0.4, ease: "power2.out" }, T(32.42));\n'
         + out(["l2", "b1", "b2", "s1", "s2", "s3"], 32.86))
    files["g05"] = (st, du, scene_file("g05", st, du, m, s))

    # ---------------- g06 #3 kurangkan gelebeh (33.05 - 36.55)
    st, du = win("c06")
    m = """    <div class="row" style="top: 700px;"><div id="g06-badge" class="badge" style="background:#FFE600; color:#0B0B0B;">#3</div></div>
    <div class="col" style="top: 862px; gap: 0;">
      <div id="g06-t1" class="hd head">KURANGKAN</div>
      <div id="g06-t2" class="hd hero p">GELEBEH</div>
    </div>"""
    s = (slam("badge", 33.30, 2.2) + slam("t1", 33.92) + slam("t2", 34.42, 1.5)
         + out(["badge", "t1", "t2"], 35.10))
    files["g06"] = (st, du, scene_file("g06", st, du, m, s))

    # ---------------- g07 peha / perut / lengan -> tegang & kemas (36.55 - 41.45)
    st, du = win("c07")
    m = """    <div style="position:absolute; left: 120px; top: 800px;"><div id="g07-k1" class="pill green" style="font-size: 44px;">Peha</div></div>
    <div style="position:absolute; left: 300px; top: 910px;"><div id="g07-k2" class="pill green" style="font-size: 44px;">Perut</div></div>
    <div style="position:absolute; left: 120px; top: 1020px;"><div id="g07-k3" class="pill green" style="font-size: 44px;">Lengan</div></div>
    <div class="col" style="top: 862px; gap: 0;">
      <div id="g07-t1" class="hd head">TEGANG</div>
      <div id="g07-t2" class="hd head g">&amp; KEMAS</div>
    </div>"""
    s = (slide("k1", 38.30) + slide("k2", 38.83) + slide("k3", 39.10)
         + out(["k1", "k2", "k3"], 40.30)
         + stamp("t1", 40.50, -5) + stamp("t2", 41.02, -5)
         + out(["t1", "t2"], 41.32))
    files["g07"] = (st, du, scene_file("g07", st, du, m, s))

    # ---------------- g08 takkan sado + testosteron meter (41.45 - 49.10)
    st, du = win("c08")
    m = f"""    <div class="row" style="top: 740px;"><div id="g08-tag" class="pill">Jangan risau!</div></div>
    <div class="col" style="top: 830px; gap: 8px;">
      <div id="g08-t1" class="hd sub">TAKKAN NAMPAK</div>
      <div style="position: relative;">
        <div id="g08-t2" class="hd hero y">SADO</div>
        <div style="position:absolute; left: -20px; right: -20px; top: 0; bottom: 0; display:flex; justify-content:center; align-items:center;">
          <div id="g08-x" style="opacity:0"><svg width="330" height="150" viewBox="0 0 330 150"><path d="M20 20 L310 130 M310 20 L20 130" stroke="{RED}" stroke-width="20" stroke-linecap="round"/></svg></div>
        </div>
      </div>
    </div>
    <div class="row" style="top: 640px;">
      <div id="g08-card" class="card" style="width: 660px; padding: 26px 34px;">
        <div style="display:flex; align-items:center; gap: 22px; margin-bottom: 22px;">
          <div style="background:#fff; border-radius: 16px; padding: 6px; flex: none;">
            <img src="assets/images/testosterone-structure.png" alt="Testosterone structure" style="display:block; width: 210px; height: 137px;">
          </div>
          <div>
            <div class="hd sub" style="opacity:1; font-size: 58px; -webkit-text-stroke-width: 8px;">TESTOSTERON</div>
            <div class="lbl" style="font-size: 28px; color:#cfcfcf;">Hormon C19H28O2</div>
            <div class="lbl" data-layout-ignore style="font-size: 18px; font-weight: 600; color:#9a9a9a; margin-top: 6px;">Struktur: PubChem (NIH)</div>
          </div>
        </div>
        <div class="lbl" style="font-size: 36px; margin-bottom: 18px;">Level testosteron</div>
        <div style="display:flex; align-items:center; gap: 18px; margin-bottom: 20px;">
          <div class="lbl" style="width: 170px; color:#bbb;">Lelaki</div>
          <div style="flex:1; height: 44px; border-radius: 22px; background: rgba(255,255,255,.14); overflow: hidden;">
            <div id="g08-bm" style="width: 100%; height: 100%; background: #9AA3AD; border-radius: 22px; transform-origin: left center;"></div>
          </div>
        </div>
        <div style="display:flex; align-items:center; gap: 18px;">
          <div class="lbl" style="width: 170px; color:{GREEN};">Wanita</div>
          <div style="flex:1; height: 44px; border-radius: 22px; background: rgba(255,255,255,.14); overflow: hidden;">
            <div id="g08-bw" style="width: 100%; height: 100%; background: {GREEN}; border-radius: 22px; transform-origin: left center;"></div>
          </div>
        </div>
      </div>
    </div>
    <div class="row" style="top: 1092px;"><div id="g08-low" class="pill green">Lebih rendah</div></div>"""
    s = (popin("tag", 41.64) + blurin("t1", 42.40) + slam("t2", 42.92)
         + stamp("x", 43.18, 0)
         + out(["tag", "t1", "t2", "x"], 44.02)
         + slide("card", 44.40)
         + '      tl.fromTo(q("bm"), { scaleX: 0 }, { scaleX: 1, duration: 0.7, ease: "expo.out" }, T(44.70));\n'
         + '      tl.fromTo(q("bw"), { scaleX: 0 }, { scaleX: 0.92, duration: 0.6, ease: "expo.out" }, T(44.90));\n'
         + '      tl.to(q("bw"), { scaleX: 0.22, duration: 0.55, ease: "power3.inOut" }, T(47.62));\n'
         + popin("low", 48.30)
         + out(["card", "low"], 48.96))
    files["g08"] = (st, du, scene_file("g08", st, du, m, s))

    # ---------------- g09 checklist (49.10 - 54.95)
    st, du = win("c09")
    m = f"""    <div class="row" style="top: 840px;">
      <div id="g09-card" class="card" style="display:flex; flex-direction:column; gap: 22px; padding: 30px 40px;">
        <div id="g09-i1" style="display:flex; align-items:center; gap: 20px; opacity:0;">{CHECK_SVG}<div class="lbl" style="font-size: 40px;">Badan lebih kemas</div></div>
        <div id="g09-i2" style="display:flex; align-items:center; gap: 20px; opacity:0;">{CHECK_SVG}<div><div class="lbl" style="font-size: 40px;">Lebih yakin</div><div class="lbl" style="font-size: 30px; font-weight: 600; color: #cfcfcf;">nak jumpa orang</div></div></div>
      </div>
    </div>"""
    s = (slide("card", 52.20) + slide("i1", 52.30) + slide("i2", 53.40)
         + out(["card", "i1", "i2"], 54.80))
    files["g09"] = (st, du, scene_file("g09", st, du, m, s))

    # ---------------- g10 CTA (54.95 - 59.25)
    st, du = win("c10")
    m = f"""    <div class="row up" style="top: 300px;">
      <div id="g10-btn" style="opacity:0; display:flex; align-items:center; gap: 20px; background:{YELLOW}; border: 8px solid {INK};
           border-radius: 40px; padding: 18px 34px; box-shadow: 0 14px 0 {INK};">
        {CART_SVG}
        <div style="display:flex; flex-direction:column;">
          <div class="lbl" style="color:{INK}; font-size: 38px;">Link</div>
          <div class="hd head" style="opacity:1; color:{INK}; -webkit-text-stroke:0; text-shadow:none;">BEG KUNING</div>
          <div class="lbl" style="color:{INK}; font-size: 38px;">Kat bawah ni!</div>
        </div>
      </div>
    </div>
    <div class="row" style="top: 860px;">
      <div id="g10-tag" style="opacity:0; background:{PINK}; border: 7px solid {INK}; border-radius: 30px; padding: 16px 34px 20px; box-shadow: 0 12px 0 {INK};">
        <div class="lbl" style="font-size: 40px;">Harga tengah</div>
        <div class="hd hero y" style="opacity:1;">MURAH!</div>
      </div>
    </div>
    <div class="col up" style="top: 1390px; gap: 0;">
      <div id="g10-a1" style="opacity:0">{ARROW_SVG}</div>
      <div id="g10-a2" style="opacity:0; margin-top: -24px;">{ARROW_SVG}</div>
    </div>"""
    s = (popin("btn", 55.15, 0.3)
         + '      tl.fromTo([q("a1"), q("a2")], { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: 0.3, stagger: 0.08, ease: "expo.out" }, T(55.55));\n'
         + '      tl.to([q("a1"), q("a2")], { y: 26, duration: 0.28, yoyo: true, repeat: 3, stagger: 0.08, ease: "sine.inOut" }, T(56.0));\n'
         + '      tl.fromTo(q("btn"), { scale: 1 }, { scale: 1.07, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" }, T(56.86));\n'
         + stamp("tag", 57.16, -5))
    files["g10"] = (st, du, scene_file("g10", st, du, m, s))
    return files


# ---------------------------------------------------------------- captions
def captions_file(groups):
    rows = []
    for gi, g in enumerate(groups):
        spans = "".join(
            f'<span id="cw{w["id"][1:]}" class="w{" k" if w["key"] else ""}" data-s="{w["start"]}" data-e="{w["end"]}">{w["text"]}</span> '
            for w in g)
        rows.append(f'    <div id="cg{gi}" class="cg" data-s="{g[0]["start"]}" data-e="{g[-1]["end"]}"><div class="cl">{spans.strip()}</div></div>')
    css = FONTS + f"""
#root {{ position: absolute; inset: 0; pointer-events: none; }}
.cg {{ position: absolute; left: 0; right: 0; top: 1150px; display: flex; justify-content: center; opacity: 0; overflow: visible; }}
.cl {{ font-family: 'Anton', sans-serif; font-size: {CAPTION}px; line-height: 1.1; text-transform: uppercase;
      text-align: center; color: #fff; -webkit-text-stroke: 9px {INK}; paint-order: stroke fill;
      letter-spacing: 1px; white-space: nowrap; text-shadow: 0 6px 0 rgba(0,0,0,.45); }}
.w {{ display: inline-block; margin: 0 7px; }}
.w.k {{ color: {GREEN}; }}
"""
    return f"""<template>
  <style>{css}
  </style>
  <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}" data-layout-allow-safe-zone>
{chr(10).join(rows)}
  </div>
  <script>
    (function () {{
      // Each group: in at its first word, hard kill after its last word (or when the next group starts).
      // Active word turns yellow; keywords stay neon green and pop while spoken.
      const tl = gsap.timeline({{ paused: true }});
      const groups = Array.from(document.querySelectorAll("[data-composition-id=captions] .cg"));
      groups.forEach((g, i) => {{
        const s = parseFloat(g.dataset.s), e = parseFloat(g.dataset.e);
        const next = groups[i + 1] ? parseFloat(groups[i + 1].dataset.s) : Infinity;
        const tIn = Math.max(0.05, s - 0.06);
        const tOut = Math.min(e + 0.22, next - 0.04);
        tl.fromTo(g, {{ opacity: 0, scale: 0.86 }}, {{ opacity: 1, scale: 1, duration: 0.1, ease: "back.out(2)" }}, tIn);
        tl.set(g, {{ opacity: 0, visibility: "hidden" }}, tOut);
        g.querySelectorAll(".w").forEach((w) => {{
          const ws = parseFloat(w.dataset.s), we = Math.min(parseFloat(w.dataset.e), tOut - 0.02);
          if (w.classList.contains("k")) {{
            tl.fromTo(w, {{ scale: 1 }}, {{ scale: 1.08, duration: 0.08, ease: "power2.out" }}, ws);
            tl.to(w, {{ scale: 1, duration: 0.12, ease: "power2.in" }}, Math.max(ws + 0.09, we - 0.06));
          }} else {{
            tl.set(w, {{ color: "{YELLOW}" }}, ws);
            tl.set(w, {{ color: "#ffffff" }}, Math.max(ws + 0.05, we));
          }}
        }});
      }});
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
"""


def fx_file():
    lines = []
    for i, t in enumerate(CUTS):
        ir = "" if i == 0 else ", immediateRender: false"
        lines.append(f'      tl.fromTo("#fx-flash", {{ opacity: 0 }}, {{ opacity: 0.92, duration: 0.034, ease: "none"{ir} }}, {t - 0.034:.3f});')
        lines.append(f'      tl.to("#fx-flash", {{ opacity: 0, duration: 0.2, ease: "power2.out" }}, {t:.3f});')
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    #fx-flash {{ position: absolute; inset: 0; background: #ffffff; opacity: 0; }}
  </style>
  <div id="root" data-composition-id="fx" data-width="{W}" data-height="{H}" data-layout-ignore>
    <div id="fx-flash"></div>
  </div>
  <script>
    (function () {{
      // White flash on every cut: 2 frames up, 0.2 s down.
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(lines)}
      window.__timelines["fx"] = tl;
    }})();
  </script>
</template>
"""


# ---------------------------------------------------------------- sound effects
# (file, film time of the picture event, volume). Peak offsets are measured from the files.
SFX_VOL = {"whoosh": 0.10, "pop": 0.14, "ding": 0.09, "impact": 0.12, "cha-ching": 0.10, "riser": 0.07, "zap": 0.09}
PEAK = {"whoosh-a": 0.31, "whoosh-b": 0.25, "whoosh-c": 0.40, "pop-a": 0.0, "pop-b": 0.0, "ding": 0.0,
        "impact": 0.0, "cha-ching": 0.0, "riser": 1.57, "zap": 0.0}
SFX = [
    ("impact", 0.00),
    ("pop-a", 3.02), ("pop-b", 4.82), ("ding", 5.30),
    ("whoosh-a", 6.70), ("pop-a", 6.99), ("pop-b", 7.60), ("whoosh-c", 10.34), ("zap", 10.84),
    ("whoosh-b", 12.45), ("pop-a", 15.40), ("pop-b", 16.40), ("zap", 17.52),
    ("whoosh-c", 19.05), ("pop-a", 19.32), ("pop-b", 25.02), ("pop-a", 25.81), ("pop-b", 26.28),
    ("whoosh-a", 27.10), ("pop-a", 28.06), ("pop-b", 30.86), ("ding", 32.42),
    ("riser", 33.05), ("impact", 33.05),
    ("whoosh-b", 36.55), ("pop-a", 38.30), ("pop-b", 38.83), ("pop-a", 39.10), ("impact", 40.50),
    ("whoosh-c", 41.45), ("zap", 43.18), ("pop-a", 47.62), ("pop-b", 48.30),
    ("whoosh-a", 49.10), ("pop-b", 52.30), ("pop-a", 53.40),
    ("whoosh-b", 54.95), ("pop-b", 55.15), ("cha-ching", 57.16),
]


def wav_len(name):
    import wave
    with wave.open(os.path.join(ROOT, "assets", "sfx", name + ".wav")) as w:
        return w.getnframes() / w.getframerate()


def index_file(files):
    vids, hosts, sfx_tags, zooms = [], [], [], []
    for i, c in enumerate(CLIPS):
        d = c["end"] - c["start"]
        audio = 'muted' if c["music"] else 'data-has-audio="true" data-volume="0.3"'
        vids.append(f'''      <div id="z{c["id"][1:]}" class="vwrap" style="z-index: {i + 1};">
        <video id="{c["id"]}" class="clip" src="assets/footage/{c["id"]}.mp4" data-start="{c["start"]}" data-duration="{d:.4f}"
               data-media-start="0" data-track-index="0" playsinline {audio}></video>
      </div>''')
        zooms.append(f'      tl.fromTo("#z{c["id"][1:]}", {{ scale: 1 }}, {{ scale: 1.08, duration: 0.55, ease: "expo.out" }}, {c["start"]});')
    for sid, (st, du, _) in files.items():
        hosts.append(f'''      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html"
           data-start="{st}" data-duration="{du:.4f}" data-track-index="1" data-track-kind="graphics"
           data-width="{W}" data-height="{H}" style="z-index: 20;"></div>''')
    lane_end = {}
    for n, (name, t) in enumerate(SFX):
        kind = name.split("-")[0] if not name.startswith("cha") else "cha-ching"
        start = max(0.0, round(t - PEAK[name] + 1 / FPS, 3)) if t > 0 else 0.0
        length = wav_len(name)
        lane = 4
        while lane_end.get(lane, -1) > start:
            lane += 1
        lane_end[lane] = start + length
        sfx_tags.append(f'      <audio id="sfx{n:02d}" class="clip" src="assets/sfx/{name}.wav" data-start="{start}" '
                        f'data-duration="{length:.3f}" data-track-index="{lane}" data-volume="{SFX_VOL[kind]}"></audio>')
    return f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; background: #000; }}
      .vwrap {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; overflow: hidden; transform-origin: 50% 45%; }}
      .vwrap video {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-fps="{FPS}"
         data-width="{W}" data-height="{H}">
      <!-- Footage: 10 cuts, original sound at 30 % (sources with music would be muted). -->
{chr(10).join(vids)}

      <!-- One graphics overlay per cut -->
{chr(10).join(hosts)}

      <!-- Captions (Anton 60 px, 2-3 words, centre-bottom) -->
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html"
           data-start="0" data-duration="{DUR}" data-track-index="2" data-track-kind="captions"
           data-width="{W}" data-height="{H}" style="z-index: 30;"></div>

      <!-- White flash on every cut -->
      <div id="fx" data-composition-id="fx" data-composition-src="compositions/fx.html"
           data-start="0" data-duration="{DUR}" data-track-index="3" data-track-kind="graphics"
           data-width="{W}" data-height="{H}" style="z-index: 40;"></div>

      <!-- Original voiceover: untouched, full length, volume 100 %. No music. -->
      <audio id="vo" class="clip" src="assets/audio/voiceover.m4a" data-start="0" data-duration="{DUR}"
             data-media-start="0" data-track-index="3" data-volume="1"></audio>

      <!-- Synthesised sound effects (tools/sfx.py), well under the voiceover -->
{chr(10).join(sfx_tags)}
    </div>
    <script>
      // Short zoom-in at the head of every clip.
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(zooms)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


if __name__ == "__main__":
    words = clean_words()
    json.dump(words, open(os.path.join(HERE, "words.json"), "w"), ensure_ascii=False, indent=1)
    groups = group_words(words)
    os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
    files = scenes()
    for sid, (_, _, html) in files.items():
        open(os.path.join(ROOT, "compositions", sid + ".html"), "w").write(html)
    open(os.path.join(ROOT, "compositions", "captions.html"), "w").write(captions_file(groups))
    open(os.path.join(ROOT, "compositions", "fx.html"), "w").write(fx_file())
    open(os.path.join(ROOT, "index.html"), "w").write(index_file(files))
    with open(os.path.join(HERE, "caption_groups.txt"), "w") as f:
        for g in groups:
            f.write(f'{g[0]["start"]:6.2f}-{g[-1]["end"]:6.2f}  ' + " ".join(w["text"] for w in g) + "\n")
    print(f"{len(words)} words, {len(groups)} caption groups, {len(SFX)} sfx")
