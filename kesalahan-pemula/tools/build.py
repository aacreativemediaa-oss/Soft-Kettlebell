"""Generate the HyperFrames project for "3 kesalahan kettlebell workout (pemula)" (no voiceover).

Inputs (tools/): clips.json (10 cuts). The on-screen script lives in SCRIPT below.
Outputs: index.html, compositions/g01..g10.html, compositions/captions.html, compositions/fx.html,
tools/caption_groups.txt.

Format (same as the first Soft Kettlebell edit): 1080x1920 60 fps, no music, footage sound 30 %
(music footage muted), max 10 clips, one-shot intro at normal speed, zoom-in + white flash on every
cut, Anton titles/captions + Montserrat labels at 70 % scale, captions 60 px uppercase with black
stroke (active word yellow, keywords neon green, 2-3 words, centre-bottom), no caption where a
graphic already writes the line, synthesised SFX at low level, CTA arrows on the far left.

    python3 tools/build.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
W, H, FPS = 1080, 1920, 60

CLIPS = json.load(open(os.path.join(HERE, "clips.json")))
CUTS = [c["start"] for c in CLIPS[1:]]
DUR = CLIPS[-1]["end"]

HERO, HEAD, SUB, LABEL = 93, 75, 56, 24   # 23 Nov 2026 format: 2/3 of the old scale
CAPTION = 40
YELLOW, GREEN, PINK, RED, INK = "#FFE600", "#39FF14", "#FF3D8B", "#FF2D2D", "#0B0B0B"

# ---------------------------------------------------------------- on-screen script (captions)
# No voiceover: captions carry the spoken-style guide lines, read at ~0.32 s a word.
# Lines a graphic already writes out (titles, tips, USP, CTA) are NOT captions.
SCRIPT = []  # no voiceover; every line is written by a graphic (no-overlap rule)
KEYWORDS = {"KEPALA", "KAKI,", "KETTLEBELL", "PUTAR", "PICIT", "MELUTUT,"}
WORD_T = 0.32


def script_groups():
    groups, n = [], 0
    for t0, line in SCRIPT:
        words = line.upper().split()
        # 2-3 words a group: 4 -> 2+2, 5 -> 3+2, 3 -> 3, 2 -> 2
        sizes = {1: [1], 2: [2], 3: [3], 4: [2, 2], 5: [3, 2], 6: [3, 3]}[len(words)]
        t, i = t0, 0
        for sz in sizes:
            g = []
            for w in words[i:i + sz]:
                dur = WORD_T + 0.02 * max(0, len(w) - 6)
                g.append({"id": f"w{n}", "text": w, "start": round(t, 3), "end": round(t + dur, 3),
                          "key": w.strip(",!?") in KEYWORDS or w in KEYWORDS, "punct": w[-1] in ",.!?"})
                t += dur
                n += 1
            t += 0.05
            groups.append(g)
            i += sz
    return groups


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


# Updated format: top headline 150 px, sub-headline 70 px (Anton).
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


TIMER_SVG = f"""<svg width="200" height="200" viewBox="0 0 230 230">
  <circle cx="115" cy="115" r="92" fill="#ffffff" stroke="{INK}" stroke-width="8"/>
  <circle cx="115" cy="115" r="76" fill="none" stroke="#e6e6e6" stroke-width="20"/>
  <circle id="{{p}}-ring" cx="115" cy="115" r="76" fill="none" stroke="{GREEN}" stroke-width="20" stroke-linecap="round"
          stroke-dasharray="477.5" stroke-dashoffset="477.5" transform="rotate(-90 115 115)"/>
  <text id="{{p}}-num" x="115" y="134" text-anchor="middle" font-family="Anton" font-size="62" fill="{INK}">1:00</text>
</svg>"""


# Rep moments (film seconds), measured with tools/track_color.py (kettlebell / shoe path) and a 4 fps strip:
# halos = kettlebell behind the head; leg raise = feet passing over the kettlebell; twist = each side touch.
REPS = {1: [12.40, 14.70, 16.90], 2: [22.30, 23.25, 24.15, 25.10, 26.00, 26.90, 27.75], 3: [31.90, 32.90, 34.10, 35.20, 36.20, 37.35]}
HEADER_END = 2.60   # exercise name shown for the first 2.6 s of each exercise clip, then the reps block


# Reps line sized so "10 REPS × 3 SET" is as wide as the 70 px "SETIAP LATIHAN" above it
# (measured with the real Anton font: 410 px each at 70 px).
REPS_LINE_PX = 70


def exercise_scene(sid, t0, t_end, n, l1, l2, img=None, title=None, w=118, an_left=556):
    counts = [10 - i for i in range(len(REPS[n]) + 1)]
    lines = "".join(f'<span id="{sid}-n{c}" class="cnum" style="opacity:{1 if i == 0 else 0}">{c} REPS <span class="g">&#215; 3 SET</span></span>'
                    for i, c in enumerate(counts))
    m = (top_block(sid, f"LATIHAN #{n}", l1, l2) + ("\n" + anat2(sid, img, title, w, an_left) if img else "") + f"""
    <div class="col" style="top: 1262px; width: 460px; gap: 2px;" data-layout-allow-safe-zone>
      <div id="{sid}r-s" class="hd s70 y">SETIAP LATIHAN</div>
      <div id="{sid}r-t1" class="hd s70" style="font-size: {REPS_LINE_PX}px;"><span class="cbox">{lines}</span></div>
    </div>
    <div style="position:absolute; left: 590px; top: 1196px;" data-layout-allow-safe-zone>
      <div id="{sid}-tm" class="card" style="background:{YELLOW}; border-color:{INK}; padding: 14px 18px 12px; display:flex; flex-direction:column; align-items:center;">
        {TIMER_SVG.replace('{p}', sid)}
        <div class="lbl" style="color:{INK}; font-size: 36px; margin-top: 6px;">Rehat</div>
        <div class="lbl" style="color:{INK}; font-size: 30px; font-weight: 700;">setiap set</div>
      </div>
    </div>""")
    h = t0 + HEADER_END
    t_tm, d_tm = h + 1.0, t_end - h - 1.3   # timer runs 1:00 -> 0:00 over the rest of the exercise clip
    s = (blurin("s", t0 + 0.20) + slam("t1", t0 + 0.35) + slam("t2", t0 + 0.60, 1.4)
         + (slide("an", t0 + 1.00, 140) if img else "")
         + out(["s", "t1", "t2"] + (["an"] if img else []), h)
         + f'      tl.fromTo("#{sid}r-s", {{ opacity: 0, filter: "blur(14px)", y: 24 }}, {{ opacity: 1, filter: "blur(0px)", y: 0, duration: 0.2, ease: "power4.out" }}, T({h + 0.20:.2f}));\n'
         + f'      tl.fromTo("#{sid}r-t1", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.32, ease: "expo.out" }}, T({h + 0.30:.2f}));\n'
         + popin("tm", h + 0.70, 0.5)
         + f'      tl.fromTo(q("ring"), {{ attr: {{ "stroke-dashoffset": 477.5 }} }}, {{ attr: {{ "stroke-dashoffset": 0 }}, duration: {d_tm:.2f}, ease: "none" }}, T({t_tm:.2f}));\n'
         + f'''      (function () {{
        const el = document.querySelector("#{sid}-num"), o = {{ v: 60 }};
        const show = () => {{ const n = Math.ceil(o.v - 1e-6); el.textContent = n >= 60 ? "1:00" : "0:" + String(n).padStart(2, "0"); }};
        tl.fromTo(o, {{ v: 60 }}, {{ v: 0, duration: {d_tm:.2f}, ease: "none", onUpdate: show, onStart: show, onComplete: show }}, T({t_tm:.2f}));
      }})();
'''
         + f'      tl.to(["#{sid}r-s", "#{sid}r-t1", q("tm")], {{ opacity: 0, filter: "blur(10px)", scale: 0.92, duration: 0.16, ease: "power2.in" }}, T({t_end - 0.18:.2f}));\n'
         + f'      tl.set(["#{sid}r-s", "#{sid}r-t1", q("tm")], {{ opacity: 0 }}, T({t_end - 0.01:.2f}));\n')
    for i, t in enumerate(REPS[n]):
        a, b = counts[i], counts[i + 1]
        s += (f'      tl.set(q("n{a}"), {{ opacity: 0 }}, T({t:.2f}));\n'
              f'      tl.set(q("n{b}"), {{ opacity: 1 }}, T({t:.2f}));\n'
              f'      tl.fromTo(q("n{b}"), {{ scale: 1.45, color: "{YELLOW}" }}, {{ scale: 1, color: "#ffffff", duration: 0.35, ease: "back.out(2)", immediateRender: false }}, T({t:.2f}));\n')
    return m, s


# ---------------- 23 Nov 2026 format: headline 100 px, sub/save sticker 47 px, caption 40 px, chip/label 19 px,
# everything else at 2/3 of the previous scale (pills 24 px, card text 24 px, icons 36 px).
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


def posture_svg(good):
    """Side view of a hip hinge holding a kettlebell: rounded back (bad) or neutral spine (good)."""
    col = GREEN if good else RED
    back = "M70 150 L150 92" if good else "M70 150 C 92 84, 136 70, 152 100"
    head = (164, 82) if good else (160, 118)
    knee = "M70 150 L84 196 L74 238" if good else "M70 150 L102 194 L70 238"
    arm = "M140 99 L132 160" if good else "M146 104 L140 168"
    kb_y = 176 if good else 184
    mark = CK if good else XX
    return f"""<svg width="200" height="230" viewBox="0 0 220 250">
  <line x1="20" y1="240" x2="200" y2="240" stroke="#bbb" stroke-width="4"/>
  <path d="{back}" fill="none" stroke="{col}" stroke-width="16" stroke-linecap="round"/>
  <path d="{knee}" fill="none" stroke="{INK}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="{arm}" fill="none" stroke="{INK}" stroke-width="11" stroke-linecap="round"/>
  <circle cx="{head[0]}" cy="{head[1]}" r="17" fill="{INK}"/>
  <path d="M120 {kb_y - 14} C 120 {kb_y - 34}, 152 {kb_y - 34}, 152 {kb_y - 14}" fill="none" stroke="{PINK}" stroke-width="7"/>
  <circle cx="136" cy="{kb_y + 4}" r="20" fill="{PINK}" stroke="{INK}" stroke-width="4"/>
  <g transform="translate(176 6)">{mark}</g>
</svg>"""


def scenes():
    c = {x["id"]: x for x in CLIPS}
    files = {}
    css = LBS_CSS + H_CSS + K_CSS

    def win(cid):
        return c[cid]["start"], c[cid]["end"] - c[cid]["start"]

    def put(sid, cid, m, s, extra=""):
        st, du = win(cid)
        files[sid] = (st, du, scene_file(sid, st, du, m, s, css + extra))

    def rows(sid, items, top, left=120, icon=CK):
        r = "".join(f'<div id="{sid}-r{i}" class="ckrow">{icon}<div class="hd s70">{t}</div></div>' for i, t in enumerate(items))
        return f'    <div class="col" style="top: {top}px; left: {left}px; gap: 12px;" data-layout-allow-safe-zone>{r}</div>'

    # ---------------- g01 hook (one shot: blue shirt, lunges with two kettlebells)
    m = top_block("g01", "WORKOUT (PEMULA)", '<span class="y">3</span> KESALAHAN', "KETTLEBELL", c2="p", sub_first=False, sub_color="y",
                  top=985, extra=" data-layout-allow-safe-zone")
    s = (f'      tl.fromTo(q("t1"), {{ opacity: 1, scale: 1.35 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }}, 0);\n'
         + slam("t2", 0.40, 1.4) + slam("s", 0.85, 1.4)
         + out(["t1", "t2", "s"], 4.02))
    put("g01", "c01", m, s)

    # ---------------- g02 mistake 1: holding the breath
    m = top_block("g02", "KESALAHAN #1", "SALAH TEKNIK", "PERNAFASAN", c2="p") + f"""
    <div class="row" style="top: 570px;"><div id="g02-tag" class="card" style="display:flex; align-items:center; gap: 14px;">
      {XX}<div><div class="hd s70" style="opacity:1; color:{PINK};">TAHAN NAFAS</div>
      <div class="lbl">masa angkat beban</div></div></div></div>"""
    s = (blurin("s", 4.40) + slam("t1", 4.60) + slam("t2", 5.00, 1.4) + stamp("tag", 6.00, -3)
         + out(["s", "t1", "t2", "tag"], 8.82))
    put("g02", "c02", m, s)

    # ---------------- g03 fix 1: exhale up, inhale down (synced to the squat in the clip)
    DOWN = [9.00, 10.60, 12.30, 14.00, 15.70]   # top -> bottom: tarik nafas
    UP = [9.90, 11.50, 13.25, 14.90]            # bottom -> top: hembus nafas
    m = f"""    <div class="col" style="top: 1150px; gap: 4px;" data-layout-allow-safe-zone>
      <div id="g03-s" class="hd s70 g">TEKNIK BETUL</div>
      <div id="g03-ex" class="brow" style="opacity:0"><div class="hd h150 g" style="opacity:1;">HEMBUS</div><div class="lbl">&#8593; masa angkat</div></div>
      <div id="g03-in" class="brow" style="opacity:0"><div class="hd h150 y" style="opacity:1;">TARIK</div><div class="lbl">&#8595; masa turun</div></div>
    </div>"""
    s = (blurin("s", 9.15) + '      tl.fromTo([q("ex"), q("in")], { opacity: 0, x: -60 }, { opacity: 0.35, x: 0, duration: 0.3, stagger: 0.1, ease: "expo.out" }, T(9.20));\n')
    for t in DOWN:
        s += (f'      tl.to(q("in"), {{ opacity: 1, scale: 1.08, duration: 0.18, ease: "power2.out", transformOrigin: "0% 50%" }}, T({max(t, 9.55):.2f}));\n'
              f'      tl.to(q("ex"), {{ opacity: 0.3, scale: 1, duration: 0.18, ease: "power2.out", transformOrigin: "0% 50%" }}, T({max(t, 9.55):.2f}));\n')
    for t in UP:
        s += (f'      tl.to(q("ex"), {{ opacity: 1, scale: 1.08, duration: 0.18, ease: "power2.out", transformOrigin: "0% 50%" }}, T({t:.2f}));\n'
              f'      tl.to(q("in"), {{ opacity: 0.3, scale: 1, duration: 0.18, ease: "power2.out", transformOrigin: "0% 50%" }}, T({t:.2f}));\n')
    s += out(["s", "ex", "in"], 15.82)
    put("g03", "c03", m, s)

    # ---------------- g04 mistake 2: posture (bad vs good diagram)
    m = top_block("g04", "KESALAHAN #2", "SALAH POSTUR", "BADAN", c2="p") + f"""
    <div class="row" style="top: 1110px; gap: 18px;" data-layout-allow-safe-zone>
      <div id="g04-bad" class="card" style="background:#fff; border-color:{INK}; padding: 10px 12px; text-align:center;">{posture_svg(False)}
        <div class="chip" style="background:{RED}; color:#fff;">Bongkok · lutut goyang</div></div>
      <div id="g04-good" class="card" style="background:#fff; border-color:{INK}; padding: 10px 12px; text-align:center;">{posture_svg(True)}
        <div class="chip" style="background:{GREEN};">Tulang belakang neutral</div></div>
    </div>
    <div class="row" style="top: 572px;"><div id="g04-tag" class="pill dark">Tekanan pada tulang belakang</div></div>"""
    s = (blurin("s", 16.20) + slam("t1", 16.40) + slam("t2", 16.75, 1.4) + popin("bad", 17.40, 0.5) + popin("tag", 17.90)
         + popin("good", 18.80, 0.5)
         + out(["s", "t1", "t2", "tag", "bad", "good"], 20.82))
    put("g04", "c04", m, s)

    # ---------------- g05 fix 2: posture checklist
    m = top_block("g05", "KEKALKAN", "POSTUR", "BETUL", c2="g") + "\n" + rows("g05", ["TULANG BELAKANG NEUTRAL", "DADA TERBUKA", "BAHU STABIL"], 1170)
    s = (blurin("s", 21.20) + slam("t1", 21.40) + slam("t2", 21.75, 1.4)
         + slide("r0", 22.40) + slide("r1", 23.20) + slide("r2", 24.00)
         + out(["s", "t1", "t2", "r0", "r1", "r2"], 26.82))
    put("g05", "c05", m, s)

    # ---------------- g06 mistake 3: ego lifting
    m = (top_block("g06", "KESALAHAN #3", "BERAT TAK", "SESUAI", c2="p")
         + '\n    <div class="row" style="top: 572px;"><div id="g06-tag" class="pill pink">Ego lifting</div></div>\n'
         + rows("g06", ["SAKIT BELAKANG", "FORM LARI"], 1170, icon=XX)
         + '\n    <div class="col" style="top: 1122px;" data-layout-allow-safe-zone><div id="g06-k" class="chip">Kettlebell terlalu berat:</div></div>')
    s = (blurin("s", 27.20) + slam("t1", 27.40) + slam("t2", 27.75, 1.4) + popin("tag", 28.30)
         + popin("k", 28.90) + stamp("r0", 29.20, 0) + stamp("r1", 30.10, 0)
         + out(["s", "t1", "t2", "tag", "k", "r0", "r1"], 31.82))
    put("g06", "c06", m, s)

    # ---------------- g07 fix 3: start light (weight range bar, pemula zone 2-4 kg)
    ticks = [("2KG", 0), ("4KG", 33.3), ("6KG", 66.7), ("8KG", 100)]
    tk = "".join(f'<div class="lbl" style="position:absolute; left: {p}%; top: 52px; transform: translateX(-50%); font-size: 24px;">{n}</div>' for n, p in ticks)
    m = top_block("g07", "MULAKAN DENGAN", "BEBAN", "RINGAN", c2="g") + f"""
    <div class="row" style="top: 1150px;" data-layout-allow-safe-zone>
      <div id="g07-bar" class="card" style="width: 640px; padding: 26px 40px 46px;">
        <div class="lbl" style="font-size: 24px; margin-bottom: 18px;">Pilih berat</div>
        <div style="position: relative; height: 92px;">
          <div style="position:absolute; left: 0; right: 0; top: 14px; height: 22px; border-radius: 11px; background: rgba(255,255,255,.2);"></div>
          <div id="g07-zone" style="position:absolute; left: 0; width: 33.3%; top: 14px; height: 22px; border-radius: 11px; background: {GREEN}; transform-origin: left center;"></div>
          <div id="g07-mk" style="position:absolute; left: -18px; top: 6px; width: 38px; height: 38px; border-radius: 50%; background: {PINK}; border: 4px solid {INK};"></div>
          {tk}
        </div>
        <div style="position:absolute; left: 40px; top: 10px;"></div>
        <div id="g07-chip" class="chip" style="position:absolute; right: 30px; top: 22px; background:{GREEN};">Pemula: 2 – 4KG</div>
      </div>
    </div>"""
    s = (blurin("s", 32.20) + slam("t1", 32.40) + slam("t2", 32.75, 1.4) + slide("bar", 33.30)
         + '      tl.fromTo(q("zone"), { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "expo.out" }, T(33.70));\n'
         + '      tl.fromTo(q("mk"), { x: 0 }, { x: 0, duration: 0.01 }, T(33.70));\n'
         + popin("chip", 34.30)
         + out(["s", "t1", "t2", "bar"], 36.42))
    put("g07", "c07", m, s)

    # ---------------- g08 USP: soft (drop test hits at 37.30 s and 40.75 s)
    m = (top_block("g08", "MATERIAL LEMBUT", "TAK", "PECAH", c2="g")
         + "\n" + top_block("g08b", "KENA KAKI", "TAK", "SAKIT", c2="g"))
    s = (blurin("s", 36.80) + slam("t1", 37.30, 1.6) + slam("t2", 37.50, 1.4) + out(["s", "t1", "t2"], 39.10)
         + '      tl.fromTo("#g08b-s", { opacity: 0, filter: "blur(14px)", y: 24 }, { opacity: 1, filter: "blur(0px)", y: 0, duration: 0.2, ease: "power4.out" }, T(39.30));\n'
         + '      tl.fromTo("#g08b-t1", { opacity: 0, scale: 1.6 }, { opacity: 1, scale: 1, duration: 0.32, ease: "expo.out" }, T(39.50));\n'
         + '      tl.fromTo("#g08b-t2", { opacity: 0, scale: 1.6 }, { opacity: 1, scale: 1, duration: 0.32, ease: "expo.out" }, T(39.75));\n'
         + '      tl.to(["#g08b-s", "#g08b-t1", "#g08b-t2"], { opacity: 0, duration: 0.12 }, T(41.06));\n')
    put("g08", "c08", m, s)

    # ---------------- g09 USP: many weights - real 2 / 2.5 / 4 / 6 / 8 kg kettlebells
    def card(k, img, label):
        return (f'<div id="g09-k{k}" class="kbc" style="opacity:0"><img src="assets/images/{img}" alt="{label}">'
                f'<div class="kbl">{label}</div></div>')
    m = top_block("g09", "ADA BANYAK", "PILIHAN", "BERAT", c2="y") + f"""
    <div class="row" style="top: 580px; gap: 16px;">
      {card(1, "kb-2kg.jpg", "2KG")}{card(2, "kb-2-5kg.jpg", "2.5KG")}{card(3, "kb-4kg.jpg", "4KG")}{card(4, "kb-6kg.jpg", "6KG")}{card(5, "kb-8kg.jpg", "8KG")}
    </div>"""
    kcss = f"""
.kbc {{ position: relative; width: 118px; height: 158px; border: 4px solid {INK}; border-radius: 16px; overflow: hidden;
       background: #fff; box-shadow: 0 7px 0 rgba(0,0,0,.45); }}
.kbc img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
.kbl {{ position: absolute; left: 0; right: 0; bottom: 6px; margin: 0 auto; width: max-content; padding: 1px 8px;
       font-family: 'Anton', sans-serif; font-size: 24px; color: {INK}; background: {YELLOW}; border: 3px solid {INK};
       border-radius: 9px; }}"""
    s = (blurin("s", 41.40) + slam("t1", 41.60) + slam("t2", 41.90, 1.4)
         + popin("k1", 42.40, 0.3) + popin("k2", 42.65, 0.3) + popin("k3", 42.90, 0.3) + popin("k4", 43.15, 0.3) + popin("k5", 43.40, 0.3)
         + out(["s", "t1", "t2", "k1", "k2", "k3", "k4", "k5"], 45.62))
    put("g09", "c09", m, s, kcss)

    # ---------------- g10 CTA
    m = top_block("g10", "2027 NAK START", "KETTLEBELL", "WORKOUT?", c2="p") + f"""
    <div class="row" style="top: 590px;">
      <div id="g10-btn" style="opacity:0; background:{YELLOW}; border: 6px solid {INK}; border-radius: 26px; padding: 12px 22px 14px;
           box-shadow: 0 10px 0 {INK}; display:flex; align-items:center; gap: 14px;">
        {CART_SVG.replace('width="96" height="86"', 'width="64" height="57"')}
        <div style="display:flex; flex-direction:column;">
          <div class="lbl" style="color:{INK}; font-size: 24px;">Pilih berat di</div>
          <div class="hd" style="opacity:1; font-size: 75px; color:{INK}; -webkit-text-stroke:0; text-shadow:none;">BEG KUNING</div>
        </div>
      </div>
    </div>
    <div style="position:absolute; left: 40px; top: 1390px; display:flex; flex-direction:column; align-items:flex-start;">
      <div id="g10-a1" style="opacity:0">{ARROW_SVG}</div>
      <div id="g10-a2" style="opacity:0; margin-top: -24px;">{ARROW_SVG}</div>
    </div>"""
    s = (blurin("s", 46.00) + slam("t1", 46.20) + slam("t2", 46.55, 1.4) + popin("btn", 47.30, 0.3)
         + '      tl.fromTo([q("a1"), q("a2")], { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: 0.3, stagger: 0.08, ease: "expo.out" }, T(47.70));\n'
         + '      tl.to([q("a1"), q("a2")], { y: 26, duration: 0.28, yoyo: true, repeat: 3, stagger: 0.08, ease: "sine.inOut" }, T(48.20));\n'
         + '      tl.fromTo(q("btn"), { scale: 1 }, { scale: 1.07, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" }, T(48.20));\n')
    put("g10", "c10", m, s)
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
        const tOut = Math.min(e + 0.45, next - 0.04);
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
# No voiceover, so effects carry the sound; still kept soft.
SFX_VOL = {"whoosh": 0.14, "pop": 0.18, "ding": 0.12, "impact": 0.16, "cha-ching": 0.14, "riser": 0.10, "zap": 0.12}
PEAK = {"whoosh-a": 0.31, "whoosh-b": 0.25, "whoosh-c": 0.40, "pop-a": 0.0, "pop-b": 0.0, "ding": 0.0,
        "impact": 0.0, "cha-ching": 0.0, "riser": 1.57, "zap": 0.0}
SFX = [
    ("impact", 0.00), ("pop-a", 0.40), ("pop-b", 0.85),
    ("whoosh-a", 4.20), ("pop-a", 4.60), ("pop-b", 5.00), ("zap", 6.00),
    ("whoosh-b", 9.00), ("ding", 9.20), ("pop-a", 9.90), ("pop-b", 10.60), ("pop-a", 11.50), ("pop-b", 12.30), ("pop-a", 13.25), ("pop-b", 14.00), ("pop-a", 14.90), ("pop-b", 15.70),
    ("whoosh-c", 16.00), ("pop-a", 16.40), ("pop-b", 16.75), ("zap", 17.40), ("pop-a", 17.90), ("ding", 18.80),
    ("whoosh-a", 21.00), ("pop-a", 21.40), ("pop-b", 21.75), ("ding", 22.40), ("ding", 23.20), ("ding", 24.00),
    ("whoosh-b", 27.00), ("pop-a", 27.40), ("pop-b", 27.75), ("pop-a", 28.30), ("zap", 29.20), ("zap", 30.10),
    ("whoosh-c", 32.00), ("pop-a", 32.40), ("pop-b", 32.75), ("pop-a", 33.30), ("ding", 34.30),
    ("whoosh-a", 36.60), ("impact", 37.30), ("pop-a", 37.50), ("pop-b", 39.50), ("pop-a", 39.75), ("impact", 40.75),
    ("whoosh-b", 41.20), ("pop-a", 41.60), ("zap", 41.90), ("pop-a", 42.40), ("pop-b", 42.65), ("pop-a", 42.90), ("pop-b", 43.15), ("pop-a", 43.40),
    ("whoosh-c", 45.80), ("pop-a", 46.20), ("pop-b", 46.55), ("cha-ching", 48.20),
]
SHAKES = [37.30, 40.75]  # camera shake on the drop-test hits (clip c08)
SHAKES = [42.10, 45.55]  # camera shake on the drop-test hits (clip c07)


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
        zooms.append(f'      tl.to("#z08", {{ x: 18, duration: 0.035, ease: "none" }}, {t}).to("#z08", {{ x: -14, duration: 0.05, ease: "none" }})'
                     f'.to("#z08", {{ x: 8, duration: 0.05, ease: "none" }}).to("#z08", {{ x: 0, duration: 0.06, ease: "power2.out" }});')
    for sid, (st, du, _) in files.items():
        hosts.append(f'''      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html"
           data-start="{st}" data-duration="{du:.4f}" data-track-index="1" data-track-kind="graphics"
           data-width="{W}" data-height="{H}" style="z-index: 20;"></div>''')
    lane_end = {}
    for n, (name, t) in enumerate(SFX):
        kind = "cha-ching" if name.startswith("cha") else name.split("-")[0]
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
      <!-- Footage: 10 cuts, original sound at 30 % (no footage here has music). No voiceover, no music. -->
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

      <!-- Synthesised sound effects (tools/sfx.py) -->
{chr(10).join(sfx_tags)}
    </div>
    <script>
      // Short zoom-in at the head of every clip; shake on the drop-test hits.
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(zooms)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


if __name__ == "__main__":
    groups = script_groups()
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
    print(f"{len(groups)} caption groups, {len(SFX)} sfx, {DUR}s")
