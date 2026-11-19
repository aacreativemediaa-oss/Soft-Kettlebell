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
DUR = 47.6833  # voiceover length (ffprobe 47.693 s), floored to a whole frame (2861 @ 60 fps)

CLIPS = json.load(open(os.path.join(HERE, "clips.json")))
CUTS = [c["start"] for c in CLIPS[1:]]

# ---------------------------------------------------------------- type scale
# Sizes are 70 % of the first-version scale (hero 200, header 160, sub 120, label 52).
HERO, HEAD, SUB, LABEL = 140, 112, 84, 36
CAPTION = 60
YELLOW, GREEN, PINK, RED, INK = "#FFE600", "#39FF14", "#FF3D8B", "#FF2D2D", "#0B0B0B"

# ---------------------------------------------------------------- words
FIX = {"auto": "otot"}
KEYWORDS = {"KALORI", "BURN", "BEBAN", "WORKOUT", "AFTERBURN", "POSTURE", "KETTLEBELL", "CORE",
            "BAHU", "BACK", "TEGAP", "MELENTIK", "CANTIK", "GELEBEH", "PEHA", "PERUT", "LENGAN",
            "TEGANG", "KEMAS", "SADO", "MURAH", "YOGA", "MAT", "KIRI", "KANAN", "KEPALA", "BETIS", "KAKI", "ABS", "GRAB", "MELUTUT", "PUSING", "PUSINGKAN",
            "KARDIO", "JOGGING", "SAVE", "REPOST", "LINK", "KUNING", "LENGUH", "RESISTEN"}
# Clauses already written out by a graphic: their captions are hidden (start, end of the clause).
HIDE = [(0.0, 2.45), (2.50, 3.50), (4.60, 6.30), (9.50, 12.45), (12.50, 14.25), (14.28, 16.60),
        (22.38, 24.95), (24.96, 27.31), (32.46, 34.92), (34.95, 38.20), (38.25, 40.80), (40.85, 43.90),
        (43.98, 46.40)]


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


LBS_CSS = f"""
.row:not(.up) .hd, .col:not(.up) .hd {{ transform-origin: 0% 50%; }}
.col.up > .hd {{ transform-origin: 50% 0%; }}
.lbs {{ font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 40px; color: #fff; text-transform: uppercase;
       letter-spacing: 1px; white-space: nowrap; -webkit-text-stroke: 8px {INK}; paint-order: stroke fill; opacity: 0; }}
.anat {{ background: #fff; border: 6px solid {INK}; border-radius: 24px; padding: 10px 10px 8px; box-shadow: 0 10px 0 rgba(0,0,0,.4);
        display: flex; flex-direction: column; align-items: center; opacity: 0; }}
.anat .t {{ font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 28px; color: {INK}; text-transform: uppercase; margin-top: 6px; }}
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


def scenes():
    c = {x["id"]: x for x in CLIPS}
    files = {}

    def win(cid):
        return c[cid]["start"], c[cid]["end"] - c[cid]["start"]

    # ---------------- g01 hook (one shot IMG_2770) + save
    st, du = win("c01")
    m = f"""    <div class="col up" style="top: 330px; gap: 0;">
      <div id="g01-t1" class="hd hero"><span class="y">3</span> SENAMAN</div>
      <div id="g01-t2" class="hd sub">UNTUK <span class="p">PERUT BUNCIT</span></div>
    </div>
    <div class="row up" style="top: 640px;"><div id="g01-save" class="pill white">{BOOKMARK_SVG.format(id='g01-mark')}Save dulu!</div></div>"""
    s = (f'      tl.fromTo(q("t1"), {{ opacity: 1, scale: 1.35 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }}, 0);\n'
         + slam("t2", 1.70, 1.4)
         + popin("save", 3.18)
         + '      tl.fromTo(q("mark"), { fill: "#ffffff" }, { fill: "' + YELLOW + '", duration: 0.12 }, T(3.38));\n'
         + '      tl.fromTo(q("save"), { scale: 1 }, { scale: 1.12, duration: 0.1, yoyo: true, repeat: 1, ease: "power2.out" }, T(3.38));\n'
         + out(["t1", "t2", "save"], 4.40))
    files["g01"] = (st, du, scene_file("g01", st, du, m, s, LBS_CSS))

    # ---------------- g02 #1 russian twist + oblique anatomy
    st, du = win("c02")
    m = header("g02", 1, "RUSSIAN", "TWIST", 330) + "\n" + anat("g02", 650, "gray392-oblique.png", "Perut sisi", 200)
    s = (popin("badge", 5.08) + slam("t1", 5.56) + slam("t2", 5.86, 1.4) + slide("an", 6.20, 140)
         + out(["badge", "t1", "t2", "an"], 9.32))
    files["g02"] = (st, du, scene_file("g02", st, du, m, s, LBS_CSS))

    # ---------------- g03 twist: turn left / right + 10x each side
    st, du = win("c03")
    m = f"""    <div style="position:absolute; left: 556px; top: 300px;"><div id="g03-dg" class="diag">{TWIST_SVG.replace('{p}', 'g03')}</div></div>
    <div class="col" style="top: 330px; width: 420px; gap: 0;">
      <div id="g03-q" class="lbs">Pusing badan</div>
      <div id="g03-a" class="hd sub g">KIRI</div>
      <div id="g03-b" class="hd sub g">&amp; KANAN</div>
    </div>
""" + reps("g03", 1000, "10X", "setiap<br>arah")
    s = (popin("dg", 9.80, 0.6) + blurin("q", 10.28) + slam("a", 10.88) + slam("b", 12.08)
         + '      tl.fromTo(q("arr"), { opacity: 0 }, { opacity: 1, duration: 0.2 }, T(10.40));\n'
         + '      tl.fromTo(q("body"), { rotation: -18, transformOrigin: "150px 165px" }, { rotation: 18, duration: 0.6, yoyo: true, repeat: 4, ease: "sine.inOut" }, T(10.50));\n'
         + popin("reps", 13.14, 0.3)
         + out(["dg", "q", "a", "b", "reps"], 14.10))
    files["g03"] = (st, du, scene_file("g03", st, du, m, s, LBS_CSS))

    # ---------------- g04 #2 kneeling halos (IMG_2772; header low: kettlebell travels round the head)
    st, du = win("c04")
    m = header("g04", 2, "KNEELING", "HALOS", 820)
    s = (popin("badge", 15.16) + slam("t1", 15.68) + slam("t2", 16.12, 1.4)
         + out(["badge", "t1", "t2"], 17.50))
    files["g04"] = (st, du, scene_file("g04", st, du, m, s, LBS_CSS))

    # ---------------- g05 halo path diagram + 2 arah, 10 reps
    st, du = win("c05")
    m = f"""    <div style="position:absolute; left: 120px; top: 300px;"><div id="g05-dg" class="diag">{HALO_SVG.replace('{p}', 'g05')}</div></div>
""" + reps("g05", 1000, "10", "reps setiap<br>arah")
    s = (popin("dg", 18.98, 0.6)
         + '      tl.fromTo(q("path"), { opacity: 0 }, { opacity: 1, duration: 0.2 }, T(19.10));\n'
         + '      tl.fromTo(q("kb"), { x: 0, y: 0 }, { keyframes: [{ x: 70, y: 40, duration: 0.4 }, { x: 0, y: 82, duration: 0.4 }, { x: -70, y: 40, duration: 0.4 }, { x: 0, y: 0, duration: 0.4 }], ease: "none", repeat: 1 }, T(19.60));\n'
         + '      tl.fromTo(q("core"), { opacity: 0 }, { opacity: 1, duration: 0.15 }, T(20.42));\n'
         + popin("reps", 22.94, 0.3)
         + out(["dg", "reps"], 24.80))
    files["g05"] = (st, du, scene_file("g05", st, du, m, s, LBS_CSS))

    # ---------------- g06 #3 side to side leg raise + rectus anatomy + "level betis"
    st, du = win("c06")
    m = f"""    <div class="row" style="top: 330px; gap: 26px;">
      <div id="g06-badge" class="badge">#3</div>
      <div style="display:flex; flex-direction:column;">
        <div id="g06-t1" class="hd sub">SIDE TO SIDE</div>
        <div id="g06-t2" class="hd head g">LEG RAISE</div>
      </div>
    </div>
""" + anat("g06", 640, "gray397-rectus.png", "Perut depan", 130, 545)
    s = (popin("badge", 25.74) + slam("t1", 26.28) + slam("t2", 26.90, 1.4) + slide("an", 27.30, 140)
         + out(["badge", "t1", "t2", "an"], 29.25))
    files["g06"] = (st, du, scene_file("g06", st, du, m, s, LBS_CSS))

    # ---------------- g07 10x each side
    st, du = win("c07")
    m = reps("g07", 330, "10X", "setiap<br>arah")
    s = popin("reps", 33.88, 0.3) + out(["reps"], 34.80)
    files["g07"] = (st, du, scene_file("g07", st, du, m, s, LBS_CSS))

    # ---------------- g08 latih otot abs & core (both anatomy plates)
    st, du = win("c08")
    m = anat("g08", 150, "gray392-oblique.png", "Perut sisi", 190) + "\n" + anat("g08b", 480, "gray397-rectus.png", "Perut depan", 150) + """
    <div class="col" style="top: 860px; gap: 0;">
      <div id="g08-t1" class="lbs">Latih otot</div>
      <div id="g08-t2" class="hd head g">ABS &amp; CORE</div>
    </div>"""
    s = (slide("an", 35.30) + '      tl.fromTo("#g08b-an", { opacity: 0, x: 140, filter: "blur(10px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 0.38, ease: "expo.out" }, T(35.50));\n'
         + blurin("t1", 36.64) + slam("t2", 37.02)
         + out(["an", "t1", "t2"], 38.02)
         + '      tl.to("#g08b-an", { opacity: 0, filter: "blur(10px)", scale: 0.92, duration: 0.16, ease: "power2.in" }, T(38.02));\n'
         + '      tl.set("#g08b-an", { opacity: 0 }, T(38.19));\n')
    files["g08"] = (st, du, scene_file("g08", st, du, m, s, LBS_CSS))

    # ---------------- g09 USP: lembut, tak sakit, tak pecah (drops at 38.66 s and 42.11 s)
    st, du = win("c09")
    m = f"""    <div class="col" style="top: 790px; gap: 4px;">
      <div id="g09-tag" class="pill pink">Soft kettlebell</div>
      <div id="g09-t1" class="hd head">MATERIAL</div>
      <div id="g09-t2" class="hd hero g">LEMBUT</div>
    </div>
    <div class="col" style="top: 780px; gap: 22px;">
      <div id="g09-i1" style="display:flex; align-items:center; gap: 18px; opacity:0;">{CHECK_SVG}
        <div><div class="hd sub g" style="opacity:1;">TAK SAKIT KAKI</div><div class="lbs" style="opacity:1;">kalau terjatuh</div></div></div>
      <div id="g09-i2" style="display:flex; align-items:center; gap: 18px; opacity:0;">{CHECK_SVG}
        <div><div class="hd sub g" style="opacity:1;">TAK PECAH</div></div></div>
    </div>"""
    s = (popin("tag", 39.00) + slam("t1", 39.52) + slam("t2", 40.28, 1.5)
         + out(["tag", "t1", "t2"], 40.80)
         + stamp("i1", 41.70, -3) + stamp("i2", 42.70, -3)
         + out(["i1", "i2"], 43.80))
    files["g09"] = (st, du, scene_file("g09", st, du, m, s, LBS_CSS))

    # ---------------- g10 CTA: link beg kuning + harga murah + arrows far left
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
    <div class="row" style="top: 760px;">
      <div id="g10-tag" style="opacity:0; background:{PINK}; border: 7px solid {INK}; border-radius: 30px; padding: 16px 34px 20px; box-shadow: 0 12px 0 {INK};">
        <div class="lbl" style="font-size: 40px;">Harga tengah</div>
        <div class="hd hero y" style="opacity:1;">MURAH!</div>
      </div>
    </div>
    <div style="position:absolute; left: 40px; top: 1390px; display:flex; flex-direction:column; align-items:flex-start;">
      <div id="g10-a1" style="opacity:0">{ARROW_SVG}</div>
      <div id="g10-a2" style="opacity:0; margin-top: -24px;">{ARROW_SVG}</div>
    </div>"""
    s = (popin("btn", 44.00, 0.3)
         + '      tl.fromTo([q("a1"), q("a2")], { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: 0.3, stagger: 0.08, ease: "expo.out" }, T(44.40));\n'
         + '      tl.to([q("a1"), q("a2")], { y: 26, duration: 0.28, yoyo: true, repeat: 3, stagger: 0.08, ease: "sine.inOut" }, T(44.80));\n'
         + '      tl.fromTo(q("btn"), { scale: 1 }, { scale: 1.07, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" }, T(44.92));\n'
         + stamp("tag", 45.38, -5))
    files["g10"] = (st, du, scene_file("g10", st, du, m, s, LBS_CSS))
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
    ("impact", 0.00), ("pop-a", 1.70), ("pop-b", 3.18), ("ding", 3.38),
    ("whoosh-a", 4.57), ("pop-a", 5.08), ("pop-b", 5.56), ("pop-a", 6.20),
    ("whoosh-b", 9.49), ("pop-b", 9.80), ("zap", 10.88), ("zap", 12.08), ("ding", 13.14),
    ("whoosh-c", 14.26), ("pop-a", 15.16), ("pop-b", 15.68),
    ("whoosh-a", 17.67), ("pop-b", 18.98), ("ding", 22.94),
    ("whoosh-b", 24.93), ("pop-a", 25.74), ("pop-b", 26.28), ("pop-a", 27.30),
    ("whoosh-c", 32.47), ("ding", 33.88),
    ("whoosh-a", 34.93), ("pop-a", 35.30), ("pop-b", 35.50), ("pop-a", 37.02),
    ("whoosh-b", 38.17), ("impact", 38.66), ("pop-b", 39.00), ("pop-a", 40.28), ("riser", 42.11), ("impact", 42.11),
    ("pop-a", 41.70), ("pop-b", 42.70),
    ("whoosh-c", 43.93), ("pop-b", 44.00), ("cha-ching", 45.38),
]
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
