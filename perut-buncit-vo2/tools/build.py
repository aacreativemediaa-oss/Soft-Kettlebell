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
DUR = 57.50  # voiceover length (ffprobe 57.515 s), floored to a whole frame (3450 @ 60 fps)

CLIPS = json.load(open(os.path.join(HERE, "clips.json")))
CUTS = [c["start"] for c in CLIPS[1:]]

# ---------------------------------------------------------------- type scale
# Sizes are 70 % of the first-version scale (hero 200, header 160, sub 120, label 52).
HERO, HEAD, SUB, LABEL = 93, 75, 56, 24   # 23 Nov 2026 format (2/3 of the old scale)
CAPTION = 40
YELLOW, GREEN, PINK, RED, INK = "#FFE600", "#39FF14", "#FF3D8B", "#FF2D2D", "#0B0B0B"

# ---------------------------------------------------------------- words
FIX = {"boncit": "buncit", "pandang": "badan"}
KEYWORDS = {"KETTLEBELL", "YOGA", "MAT", "KIRI", "KANAN", "KEPALA", "BETIS", "KAKI", "LUTUT", "PUSINGKAN", "BADAN", "MELEPASI", "SISI", "GRAB", "CEPAT", "KEMAS", "EASY"}
# Clauses already written out by a graphic: their captions are hidden (start, end of the clause).
HIDE = [(0.0, 3.70), (3.80, 5.60), (5.70, 8.00), (14.50, 16.70), (17.55, 20.00), (27.60, 30.50),
        (30.90, 34.30), (40.25, 42.90), (42.95, 45.45), (45.45, 50.45), (50.60, 53.20), (54.60, 57.30)]


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
    # Words Whisper misheard in this take (checked against the footage/script):
    for w in words:
        if w["text"] == "DUDUK" and 28.0 < w["start"] < 29.0:      # "untuk duduk arah" -> "dua-dua arah"
            w["text"] = "DUA-DUA"
        elif w["text"] == "TWIST" and w["start"] > 33:             # "side to side leg twist" -> "leg raise"
            w["text"] = "RAISE"
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
      -webkit-text-stroke: 8px {INK}; paint-order: stroke fill; letter-spacing: 1px; white-space: nowrap;
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


LBS_CSS = f"""
.row:not(.up) .hd, .col:not(.up) .hd {{ transform-origin: 0% 50%; }}
.col.up > .hd {{ transform-origin: 50% 0%; }}
.lbs {{ font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 27px; color: #fff; text-transform: uppercase;
       letter-spacing: 1px; white-space: nowrap; -webkit-text-stroke: 8px {INK}; paint-order: stroke fill; opacity: 0; }}
.anat {{ background: #fff; border: 6px solid {INK}; border-radius: 24px; padding: 10px 10px 8px; box-shadow: 0 10px 0 rgba(0,0,0,.4);
        display: flex; flex-direction: column; align-items: center; opacity: 0; }}
.anat .t {{ font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 19px; color: {INK}; text-transform: uppercase; margin-top: 6px; }}
.anat .c {{ font-family: 'Montserrat', sans-serif; font-weight: 600; font-size: 15px; color: #666; }}
.diag {{ background: #fff; border: 6px solid {INK}; border-radius: 26px; padding: 10px; box-shadow: 0 10px 0 rgba(0,0,0,.4); opacity: 0; }}
"""

# Side-view lunge: both knees at 90 degrees, front knee not past the toes (dashed red line).
LUNGE_SVG = f"""<svg width="300" height="300" viewBox="0 0 300 300">
  <line x1="10" y1="282" x2="290" y2="282" stroke="#bbb" stroke-width="4"/>
  <line id="{{p}}-toe" x1="250" y1="110" x2="250" y2="282" stroke="{RED}" stroke-width="5" stroke-dasharray="12 9" opacity="0"/>
  <g stroke="{INK}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" fill="none">
    <path d="M130 70 L130 160"/>
    <path d="M130 160 L210 160 L210 270 L250 274"/>
    <path d="M130 160 L120 262 L40 266"/>
    <path d="M130 86 L112 140"/>
  </g>
  <circle cx="130" cy="44" r="22" fill="{INK}"/>
  <circle cx="108" cy="158" r="20" fill="{PINK}" stroke="{INK}" stroke-width="5"/>
  <g id="{{p}}-m1" opacity="0"><path d="M210 186 L186 186 L186 160" fill="none" stroke="{PINK}" stroke-width="6"/>
    <text x="150" y="214" font-family="Anton" font-size="30" fill="{PINK}">90°</text></g>
  <g id="{{p}}-m2" opacity="0"><path d="M120 236 L96 236 L96 262" fill="none" stroke="{PINK}" stroke-width="6"/>
    <text x="52" y="226" font-family="Anton" font-size="30" fill="{PINK}">90°</text></g>
</svg>"""

# Top view of a sumo stance: feet wide, toes turned out ~45 degrees.
FOOT = '<g transform="translate({x} 170) rotate({r})"><ellipse cx="0" cy="0" rx="30" ry="62" fill="{fill}" stroke="#0B0B0B" stroke-width="6"/>' \
       '<circle cx="-14" cy="-70" r="9" fill="{fill}" stroke="#0B0B0B" stroke-width="4"/><circle cx="4" cy="-76" r="8" fill="{fill}" stroke="#0B0B0B" stroke-width="4"/>' \
       '<circle cx="19" cy="-70" r="7" fill="{fill}" stroke="#0B0B0B" stroke-width="4"/></g>'
FEET_SVG = f"""<svg width="300" height="300" viewBox="0 0 300 300">
  <line x1="70" y1="235" x2="70" y2="40" stroke="#bbb" stroke-width="4" stroke-dasharray="10 8"/>
  <line x1="230" y1="235" x2="230" y2="40" stroke="#bbb" stroke-width="4" stroke-dasharray="10 8"/>
  {FOOT.format(x=70, r=-45, fill='#ffffff')}
  {FOOT.format(x=230, r=45, fill='#ffffff')}
  <g id="{{p}}-arc" opacity="0" fill="none" stroke="{PINK}" stroke-width="6">
    <path d="M70 90 A80 80 0 0 0 13 113"/><path d="M230 90 A80 80 0 0 1 287 113"/></g>
  <g id="{{p}}-lab" opacity="0" font-family="Anton" font-size="34" fill="{PINK}">
    <text x="4" y="78">45°</text><text x="236" y="78">45°</text></g>
  <text x="150" y="292" text-anchor="middle" font-family="Montserrat" font-weight="800" font-size="28" fill="#0B0B0B">KAKI LEBAR</text>
</svg>"""


# Top view of a seated Russian twist: shoulders rotate around the spine, arms stay with the chest.
TWIST_SVG = f"""<svg width="300" height="300" viewBox="0 0 300 300">
  <ellipse cx="150" cy="165" rx="112" ry="40" fill="#f1f1f1" stroke="#bbb" stroke-width="4" stroke-dasharray="10 8"/>
  <g id="{{p}}-body">
    <rect x="60" y="148" width="180" height="34" rx="17" fill="#ffffff" stroke="{INK}" stroke-width="7"/>
    <circle cx="150" cy="165" r="30" fill="{INK}"/>
    <circle cx="150" cy="105" r="20" fill="{PINK}" stroke="{INK}" stroke-width="5"/>
  </g>
  <g id="{{p}}-arr" opacity="0" fill="none" stroke="{PINK}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M60 232 Q150 286 240 232"/><path d="M226 216 L242 232 L222 246"/><path d="M74 216 L58 232 L78 246"/>
  </g>
  <text x="150" y="40" text-anchor="middle" font-family="Montserrat" font-weight="800" font-size="28" fill="{INK}">PUTAR BAHU</text>
</svg>"""

# Front view, kneeling halo: kettlebell path circles the head, trunk braced (pink band).
HALO_SVG = f"""<svg width="300" height="300" viewBox="0 0 300 300">
  <line x1="40" y1="286" x2="260" y2="286" stroke="#bbb" stroke-width="4"/>
  <ellipse id="{{p}}-path" cx="150" cy="70" rx="70" ry="42" fill="none" stroke="{PINK}" stroke-width="6" stroke-dasharray="14 10" opacity="0"/>
  <g stroke="{INK}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" fill="none">
    <path d="M150 96 L150 200"/>
    <path d="M150 200 L118 222 L118 282"/><path d="M150 200 L182 222 L182 282"/>
    <path d="M150 116 L110 84 L132 50"/><path d="M150 116 L190 84 L168 50"/>
  </g>
  <circle cx="150" cy="76" r="22" fill="{INK}"/>
  <circle id="{{p}}-kb" cx="150" cy="30" r="18" fill="{PINK}" stroke="{INK}" stroke-width="5"/>
  <rect id="{{p}}-core" x="122" y="150" width="56" height="34" rx="10" fill="{GREEN}" stroke="{INK}" stroke-width="5" opacity="0"/>
</svg>"""

# Side view, seated leg raise: bent knees first (green), straight legs later (dashed grey).
LEGS_SVG = f"""<svg width="300" height="300" viewBox="0 0 300 300">
  <line x1="10" y1="268" x2="290" y2="268" stroke="#bbb" stroke-width="4"/>
  <path id="{{p}}-straight" d="M120 230 L280 150" stroke="#aaa" stroke-width="14" stroke-linecap="round" stroke-dasharray="16 12" fill="none" opacity="0"/>
  <g stroke="{INK}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" fill="none">
    <path d="M120 230 L80 110"/><path d="M84 130 L40 230 L30 262"/>
  </g>
  <path id="{{p}}-bent" d="M120 230 L190 150 L250 196" stroke="{GREEN}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0"/>
  <circle cx="74" cy="86" r="22" fill="{INK}"/>
  <circle cx="200" cy="248" r="18" fill="{PINK}" stroke="{INK}" stroke-width="5"/>
  <g id="{{p}}-ok" opacity="0"><circle cx="190" cy="118" r="22" fill="{GREEN}" stroke="{INK}" stroke-width="5"/>
    <path d="M178 118 l8 8 l14 -16" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></g>
</svg>"""


def header(sid, num, l1, l2, top=820):
    return f"""    <div class="row" style="top: {top}px; gap: 26px;">
      <div id="{sid}-badge" class="badge">#{num}</div>
      <div style="display:flex; flex-direction:column;">
        <div id="{sid}-t1" class="hd head">{l1}</div>
        <div id="{sid}-t2" class="hd head g">{l2}</div>
      </div>
    </div>"""


def anat(sid, left, img, title, w=160, top=300):
    return f"""    <div style="position:absolute; left: {left}px; top: {top}px;">
      <div id="{sid}-an" class="anat">
        <img src="assets/images/{img}" alt="{title}" style="display:block; width: {w}px;">
        <div class="t">Sasar:</div><div class="t" style="margin-top:0; color:{PINK};">{title}</div>
        <div class="c" data-layout-ignore>Gray's Anatomy (domain awam)</div>
      </div>
    </div>"""


def tip_col(sid, rows):
    return f"""    <div class="col" style="top: 770px; gap: 6px;">
      <div id="{sid}-pill" class="pill">Core tip</div>
{rows}
    </div>"""


def reps(sid, top, l1, l2):
    return f"""    <div class="row" style="top: {top}px;">
      <div id="{sid}-reps" class="card" style="background:{YELLOW}; border-color:{INK}; padding: 16px 30px; display:flex; align-items:center; gap: 20px;">
        <div class="hd hero" style="opacity:1; color:{INK}; -webkit-text-stroke:0; text-shadow:none; line-height: 0.9;">{l1}</div>
        <div class="lbl" style="color:{INK}; font-size: 36px; line-height: 1.15;">{l2}</div>
      </div>
    </div>"""


H_CSS = """
.cbox { position: relative; display: inline-block; width: 430px; height: 1.05em; vertical-align: top; }
.cnum { position: absolute; left: 0; top: 0; white-space: nowrap; transform-origin: 0% 60%; }
.h150 { font-size: 100px; line-height: 1.0; }
.s70 { font-size: 47px; line-height: 1.08; -webkit-text-stroke-width: 6px; }
"""


def top_block(sid, sub, l1, l2, c2="g", sub_first=True, center=False, sub_color="y", top=318, extra=""):
    """Headline block in the top band (x 120-888, from y 300): sub-headline 70 px + two 150 px headline lines."""
    cls = "col up" if center else "col"
    sub_html = f'<div id="{sid}-s" class="hd s70 {sub_color}">{sub}</div>' if sub else ""
    lines = f'<div id="{sid}-t1" class="hd h150">{l1}</div>\n      <div id="{sid}-t2" class="hd h150 {c2}">{l2}</div>'
    inner = (sub_html + "\n      " + lines) if sub_first else (lines + "\n      " + sub_html)
    return f"""    <div class="{cls}" style="top: {top}px; width: 768px; gap: 0;"{extra}>
      {inner}
    </div>"""


def anat2(sid, img, title, w=118, left=120):
    return f"""    <div style="position:absolute; left: {left}px; top: 700px;">
      <div id="{sid}-an" class="anat">
        <img src="assets/images/{img}" alt="{title}" style="display:block; width: {w}px;">
        <div class="t">Sasar:</div><div class="t" style="margin-top:0; color:{PINK};">{title}</div>
        <div class="c" data-layout-ignore>Gray's Anatomy (domain awam)</div>
      </div>
    </div>"""



K_CSS = f"""
.ckrow {{ display: flex; align-items: center; gap: 14px; opacity: 0; }}
.ckrow .hd {{ opacity: 1; }}
.chip {{ font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 19px; letter-spacing: 1px; text-transform: uppercase;
        color: {INK}; background: {YELLOW}; border: 3px solid {INK}; border-radius: 999px; padding: 5px 14px; white-space: nowrap; }}
.pill {{ font-size: 24px; padding: 9px 22px; border-width: 4px; box-shadow: 0 6px 0 {INK}; gap: 10px; }}
.card {{ padding: 20px 26px; border-radius: 24px; border-width: 4px; }}
.lbl {{ font-size: 24px; }}
.brow {{ display: flex; align-items: baseline; gap: 16px; }}
.brow .lbl {{ font-size: 24px; text-shadow: 0 3px 0 rgba(0,0,0,.6); }}
"""
CK = ('<svg width="36" height="36" viewBox="0 0 54 54"><circle cx="27" cy="27" r="25" fill="' + GREEN +
      '" stroke="#0B0B0B" stroke-width="4"/><path d="M15 28 l8 8 l16 -18" fill="none" stroke="#0B0B0B" stroke-width="6" '
      'stroke-linecap="round" stroke-linejoin="round"/></svg>')
XX = ('<svg width="36" height="36" viewBox="0 0 54 54"><circle cx="27" cy="27" r="25" fill="' + RED +
      '" stroke="#0B0B0B" stroke-width="4"/><path d="M17 17 L37 37 M37 17 L17 37" stroke="#fff" stroke-width="7" stroke-linecap="round"/></svg>')



def count_block(sid, top=1160):
    """'SETIAP ARAH / 10 KALI' block, bottom-left (client layout for reps), pops on the word '10'."""
    return f"""    <div class="col" style="top: {top}px; gap: 0;" data-layout-allow-safe-zone>
      <div id="{sid}-cs" class="hd s70 y">SETIAP ARAH</div>
      <div id="{sid}-ct" class="hd h150 g">10 KALI</div>
    </div>"""


def count_anim(sid, t, t_end):
    return (f'      tl.fromTo(q("cs"), {{ opacity: 0, filter: "blur(14px)", y: 24 }}, {{ opacity: 1, filter: "blur(0px)", y: 0, duration: 0.2, ease: "power4.out" }}, T({t - 0.15:.2f}));\n'
            + f'      tl.fromTo(q("ct"), {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: 0.32, ease: "expo.out", transformOrigin: "0% 50%" }}, T({t:.2f}));\n'
            + out(["cs", "ct"], t_end))


def scenes():
    c = {x["id"]: x for x in CLIPS}
    files = {}
    css = LBS_CSS + H_CSS + K_CSS

    def win(cid):
        return c[cid]["start"], c[cid]["end"] - c[cid]["start"]

    def put(sid, cid, m, s, extra=""):
        st, du = win(cid)
        files[sid] = (st, du, scene_file(sid, st, du, m, s, css + extra))

    # ---------------- g01 hook (one shot IMG_2779) + save sticker on "save"
    m = top_block("g01", '<span class="y">3</span> SENAMAN SIMPLE KAT RUMAH', "PERUT", "BUNCIT?", c2="p", sub_first=False, sub_color="") + f"""
    <div class="row" style="top: 600px;"><div id="g01-save" class="pill white">{BOOKMARK_SVG.format(id='g01-mark')}Save dulu sebelum hilang</div></div>"""
    s = (f'      tl.fromTo(q("t1"), {{ opacity: 1, scale: 1.35 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }}, 0);\n'
         + slam("t2", 0.56, 1.4) + slam("s", 1.46, 1.4) + popin("save", 3.84)
         + '      tl.fromTo(q("mark"), { fill: "#ffffff" }, { fill: "' + YELLOW + '", duration: 0.12 }, T(4.26));\n'
         + '      tl.fromTo(q("save"), { scale: 1 }, { scale: 1.12, duration: 0.1, yoyo: true, repeat: 1, ease: "power2.out" }, T(4.26));\n'
         + out(["t1", "t2", "s", "save"], 5.34))
    put("g01", "c01", m, s)

    # ---------------- g02 #1 russian twist + oblique anatomy
    m = top_block("g02", "LATIHAN #1", "RUSSIAN", "TWIST") + "\n" + anat2("g02", "gray392-oblique.png", "Perut sisi", 118, 600)
    s = (blurin("s", 6.24) + slam("t1", 7.36) + slam("t2", 7.56, 1.4) + slide("an", 8.00, 140)
         + out(["s", "t1", "t2", "an"], 11.43))
    put("g02", "c02", m, s)

    # ---------------- g03 twist left/right + 10x each side
    m = f"""    <div style="position:absolute; left: 640px; top: 318px;"><div id="g03-dg" class="diag" style="padding: 6px;">{TWIST_SVG.replace('{p}', 'g03').replace('width="300" height="300"', 'width="220" height="220"')}</div></div>
""" + count_block("g03")
    s = (popin("dg", 12.40, 0.6)
         + '      tl.fromTo(q("arr"), { opacity: 0 }, { opacity: 1, duration: 0.2 }, T(12.50));\n'
         + '      tl.fromTo(q("body"), { rotation: -18, transformOrigin: "150px 165px" }, { rotation: 18, duration: 0.6, yoyo: true, repeat: 6, ease: "sine.inOut" }, T(12.60));\n'
         + count_anim("g03", 15.30, 16.42)
         + out(["dg"], 16.42))
    put("g03", "c03", m, s)

    # ---------------- g04 #2 kneeling halos title (header low: kettlebell travels round the head)
    m = top_block("g04", "LATIHAN #2", "KNEELING", "HALOS", top=820)
    s = blurin("s", 18.08) + slam("t1", 19.26) + slam("t2", 19.58, 1.4) + out(["s", "t1", "t2"], 19.95)
    put("g04", "c04", m, s)

    # ---------------- g05 halo path diagram (on "pusingkan kettlebell belakang kepala") + 10x
    m = f"""    <div style="position:absolute; left: 640px; top: 318px;"><div id="g05-dg" class="diag" style="padding: 6px;">{HALO_SVG.replace('{p}', 'g05').replace('width="300" height="300"', 'width="220" height="220"')}</div></div>
    <div class="row" style="top: 318px;"><div id="g05-tag" class="pill green">Easy je!</div></div>
""" + count_block("g05")
    s = (popin("tag", 20.86) + out(["tag"], 21.80) + popin("dg", 23.62, 0.6)
         + '      tl.fromTo(q("path"), { opacity: 0 }, { opacity: 1, duration: 0.2 }, T(23.80));\n'
         + '      tl.fromTo(q("kb"), { x: 0, y: 0 }, { keyframes: [{ x: 70, y: 40, duration: 0.4 }, { x: 0, y: 82, duration: 0.4 }, { x: -70, y: 40, duration: 0.4 }, { x: 0, y: 0, duration: 0.4 }], ease: "none", repeat: 2 }, T(24.00));\n'
         + count_anim("g05", 30.06, 30.38)
         + out(["dg"], 30.38))
    put("g05", "c05", m, s)

    # ---------------- g06 #3 side to side leg raise title + rectus anatomy
    m = top_block("g06", "LATIHAN #3", "SIDE TO SIDE", "LEG RAISE") + "\n" + anat2("g06", "gray397-rectus.png", "Perut depan", 110, 600)
    s = (blurin("s", 31.82) + slam("t1", 33.08) + slam("t2", 33.68, 1.4) + slide("an", 33.90, 140)
         + out(["s", "t1", "t2", "an"], 34.27))
    put("g06", "c06", m, s)

    # ---------------- g07 "level betis" tag + 10x
    m = f"""    <div class="row" style="top: 318px;"><div id="g07-tag" class="pill">Kettlebell paras betis</div></div>
""" + count_block("g07")
    s = popin("tag", 35.80) + out(["tag"], 40.10) + count_anim("g07", 41.80, 42.66)
    put("g07", "c07", m, s)

    # ---------------- g08 USP: soft material
    m = top_block("g08", "KETTLEBELL NI", "LEMBUT", "TAU!", c2="g") + """
    <div class="row" style="top: 560px;"><div id="g08-tag" class="pill pink">Soft kettlebell</div></div>"""
    s = blurin("s", 43.42) + slam("t1", 44.94, 1.5) + slam("t2", 45.10, 1.4) + popin("tag", 44.40) + out(["s", "t1", "t2", "tag"], 45.31)
    put("g08", "c08", m, s)

    # ---------------- g09 USP: drop test (hits at 46.19 s and 49.64 s), "tak sakit, tak pecah" on the VO words
    m = (top_block("g09", "TERJATUH / KENA KAKI?", "TAK SAKIT", "TAK PECAH", c2="g", top=318)
         .replace('class="hd h150"', 'class="hd h150 g"', 1))
    s = (blurin("s", 46.30)
         + f'      tl.set(q("t1"), {{ opacity: 0 }}, 0);\n'
         + slam("t1", 49.02) + slam("t2", 49.94, 1.4)
         + out(["s", "t1", "t2"], 50.37))
    put("g09", "c09", m, s)

    # ---------------- g10 CTA: link beg kuning + harga murah, then colour/weight cards "sebelum warna habis"
    def card(k, img, label):
        return (f'<div id="g10-k{k}" class="kbc" style="opacity:0"><img src="assets/images/{img}" alt="{label}">'
                f'<div class="kbl">{label}</div></div>')
    m = f"""    <div class="row" style="top: 318px;">
      <div id="g10-btn" style="opacity:0; background:{YELLOW}; border: 6px solid {INK}; border-radius: 26px; padding: 12px 22px 14px;
           box-shadow: 0 10px 0 {INK}; display:flex; align-items:center; gap: 14px;">
        {CART_SVG.replace('width="96" height="86"', 'width="64" height="57"')}
        <div style="display:flex; flex-direction:column;">
          <div class="lbl" style="color:{INK}; font-size: 24px;">Link</div>
          <div class="hd" style="opacity:1; font-size: 75px; color:{INK}; -webkit-text-stroke:0; text-shadow:none;">BEG KUNING</div>
        </div>
      </div>
    </div>
    <div class="row" style="top: 520px;"><div id="g10-tag" class="pill pink">Harga tengah murah!</div></div>
    <div class="col" style="top: 318px; gap: 0;">
      <div id="g10-ws" class="hd s70 y" style="opacity:0">SEBELUM WARNA KEGEMARAN</div>
      <div id="g10-wt" class="hd h150 p" style="opacity:0">HABIS!</div>
    </div>
    <div class="row" style="top: 530px; gap: 16px;">
      {card(1, "kb-2kg.jpg", "2KG")}{card(2, "kb-2-5kg.jpg", "2.5KG")}{card(3, "kb-4kg.jpg", "4KG")}{card(4, "kb-6kg.jpg", "6KG")}{card(5, "kb-8kg.jpg", "8KG")}
    </div>
    <div style="position:absolute; left: 40px; top: 1390px; display:flex; flex-direction:column; align-items:flex-start;">
      <div id="g10-a1" style="opacity:0">{ARROW_SVG}</div>
      <div id="g10-a2" style="opacity:0; margin-top: -24px;">{ARROW_SVG}</div>
    </div>"""
    kcss = f"""
.kbc {{ position: relative; width: 118px; height: 158px; border: 4px solid {INK}; border-radius: 16px; overflow: hidden;
       background: #fff; box-shadow: 0 7px 0 rgba(0,0,0,.45); }}
.kbc img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
.kbl {{ position: absolute; left: 0; right: 0; bottom: 6px; margin: 0 auto; width: max-content; padding: 1px 8px;
       font-family: 'Anton', sans-serif; font-size: 24px; color: {INK}; background: {YELLOW}; border: 3px solid {INK};
       border-radius: 9px; }}"""
    s = (popin("btn", 51.36, 0.3) + popin("tag", 52.60)
         + '      tl.fromTo([q("a1"), q("a2")], { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: 0.3, stagger: 0.08, ease: "expo.out" }, T(51.70));\n'
         + '      tl.to([q("a1"), q("a2")], { y: 26, duration: 0.28, yoyo: true, repeat: 7, stagger: 0.08, ease: "sine.inOut" }, T(52.10));\n'
         + '      tl.fromTo(q("btn"), { scale: 1 }, { scale: 1.07, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" }, T(54.10));\n'
         + out(["btn", "tag"], 54.50)
         + blurin("ws", 54.68) + slam("wt", 55.74, 1.4)
         + popin("k1", 55.12, 0.3) + popin("k2", 55.30, 0.3) + popin("k3", 55.48, 0.3) + popin("k4", 55.66, 0.3) + popin("k5", 55.84, 0.3)
         + '      tl.fromTo(q("btn"), { opacity: 0, scale: 0.3, filter: "blur(10px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.42, ease: "back.out(2.2)", immediateRender: false }, T(56.20));\n'
         + '      tl.to([q("ws"), q("wt")], { opacity: 0, duration: 0.15 }, T(56.02));\n')
    put("g10", "c10", m, s, kcss)
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
      text-align: center; color: #fff; -webkit-text-stroke: 6px {INK}; paint-order: stroke fill;
      letter-spacing: 1px; white-space: nowrap; text-shadow: 0 6px 0 rgba(0,0,0,.45); }}
.w {{ display: inline-block; margin: 0 5px; }}
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
    ("impact", 0.00), ("pop-a", 0.56), ("pop-b", 1.46), ("pop-a", 3.84), ("ding", 4.26),
    ("whoosh-a", 5.52), ("pop-b", 6.24), ("pop-a", 7.36), ("pop-b", 7.56), ("pop-a", 8.00),
    ("whoosh-b", 11.61), ("pop-b", 12.40), ("ding", 15.30),
    ("whoosh-c", 16.60), ("pop-a", 18.08), ("pop-b", 19.26), ("pop-a", 19.58),
    ("whoosh-a", 20.13), ("pop-b", 20.86), ("pop-a", 23.62), ("ding", 30.06),
    ("whoosh-b", 30.56), ("pop-a", 31.82), ("pop-b", 33.08), ("pop-a", 33.68), ("pop-b", 33.90),
    ("whoosh-c", 34.45), ("pop-a", 35.80), ("ding", 41.80),
    ("whoosh-a", 42.84), ("pop-b", 44.40), ("pop-a", 44.94),
    ("whoosh-b", 45.49), ("impact", 46.19), ("pop-a", 46.30), ("riser", 49.64), ("impact", 49.64), ("zap", 49.02), ("zap", 49.94),
    ("whoosh-c", 50.55), ("pop-a", 51.36), ("pop-b", 52.60), ("cha-ching", 54.10),
    ("pop-a", 55.12), ("pop-b", 55.30), ("pop-a", 55.48), ("pop-b", 55.66), ("pop-a", 55.84), ("impact", 55.74), ("ding", 56.20),
]
SHAKES = [46.19, 49.64]  # camera shake on the drop-test hits (clip c09)
SHAKES = [38.66, 42.11]  # camera shake on the drop-test hits


def wav_len(name):
    import wave
    with wave.open(os.path.join(ROOT, "assets", "sfx", name + ".wav")) as w:
        return w.getnframes() / w.getframerate()


def index_file(files):
    vids, hosts, sfx_tags, zooms = [], [], [], []
    for i, c in enumerate(CLIPS):
        d = c["end"] - c["start"]
        audio = 'muted' if c["music"] else f'data-has-audio="true" data-volume="{c.get("vol", 0.3)}"'
        vids.append(f'''      <div id="z{c["id"][1:]}" class="vwrap" style="z-index: {i + 1};">
        <video id="{c["id"]}" class="clip" src="assets/footage/{c["id"]}.mp4" data-start="{c["start"]}" data-duration="{d:.4f}"
               data-media-start="0" data-track-index="0" playsinline {audio}></video>
      </div>''')
        zooms.append(f'      tl.fromTo("#z{c["id"][1:]}", {{ scale: 1 }}, {{ scale: 1.08, duration: 0.55, ease: "expo.out" }}, {c["start"]});')
    for t in SHAKES:
        zooms.append(f'      tl.to("#z09", {{ x: 18, duration: 0.035, ease: "none" }}, {t}).to("#z09", {{ x: -14, duration: 0.05, ease: "none" }})'
                     f'.to("#z09", {{ x: 8, duration: 0.05, ease: "none" }}).to("#z09", {{ x: 0, duration: 0.06, ease: "power2.out" }});')
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
