"""Generate the HyperFrames project for "Peha gendut? Buat 3 latihan ni" (no voiceover, 12 reps x 3 set).

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

HERO, HEAD, SUB, LABEL = 93, 75, 56, 24   # 23 Nov 2026 format (2/3 of the old scale)
CAPTION = 40
YELLOW, GREEN, PINK, RED, INK = "#FFE600", "#39FF14", "#FF3D8B", "#FF2D2D", "#0B0B0B"

# ---------------------------------------------------------------- on-screen script (captions)
# No voiceover: captions carry the spoken-style guide lines, read at ~0.32 s a word.
# Lines a graphic already writes out (titles, tips, USP, CTA) are NOT captions.
SCRIPT = [
    (5.70, "Pegang kettlebell depan dada"),
    (17.70, "Pusing kettlebell keliling kepala"),
    (29.70, "Hayun dari pinggul"),
    (49.80, "Kalori terus terbakar lepas workout"),
]
KEYWORDS = {"KETTLEBELL", "DADA", "KEPALA", "HAYUN", "PINGGUL", "KALORI", "TERBAKAR"}
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


# 23 Nov 2026 format: headline 100 px, sub-headline / save sticker 47 px, caption 40 px, chip/label 19 px,
# everything else at 2/3 of the previous scale (pills 24 px, card text 24 px).
H_CSS = """
.cbox { position: relative; display: inline-block; width: 300px; height: 1.08em; vertical-align: top; }
.cnum { position: absolute; left: 0; top: 0; white-space: nowrap; transform-origin: 0% 60%; }
.h150 { font-size: 100px; line-height: 1.0; }
.s70 { font-size: 47px; line-height: 1.08; -webkit-text-stroke-width: 6px; }
.anat .t { font-size: 19px !important; }
.anat .c { font-size: 11px !important; }
"""
K_CSS = f"""
.chip {{ font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 19px; letter-spacing: 1px; text-transform: uppercase;
        color: {INK}; background: {YELLOW}; border: 3px solid {INK}; border-radius: 999px; padding: 5px 14px; white-space: nowrap; }}
.pill {{ font-size: 24px; padding: 9px 22px; border-width: 4px; box-shadow: 0 6px 0 {INK}; gap: 10px; }}
.card {{ padding: 16px 20px; border-radius: 22px; border-width: 4px; }}
.lbl {{ font-size: 24px; }}
"""


REPOST_SVG = ('<svg width="30" height="30" viewBox="0 0 44 44"><g id="g01-rp" fill="none" stroke="#0B0B0B" stroke-width="5" '
              'stroke-linecap="round" stroke-linejoin="round"><path d="M8 18 a14 14 0 0 1 26 -6"/><path d="M36 26 a14 14 0 0 1 -26 6"/>'
              '<path d="M34 4 v8 h-8"/><path d="M10 40 v-8 h8"/></g></svg>')


def top_block(sid, sub, l1, l2, c2="g", sub_first=True, center=False, sub_color="y", top=318, extra=""):
    """Headline block in the top band (x 120-888, from y 318): sub-headline 47 px + two 100 px headline lines."""
    cls = "col up" if center else "col"
    sub_html = f'<div id="{sid}-s" class="hd s70 {sub_color}">{sub}</div>' if sub else ""
    lines = f'<div id="{sid}-t1" class="hd h150">{l1}</div>\n      <div id="{sid}-t2" class="hd h150 {c2}">{l2}</div>'
    inner = (sub_html + "\n      " + lines) if sub_first else (lines + "\n      " + sub_html)
    return f"""    <div class="{cls}" style="top: {top}px; width: 768px; gap: 0;"{extra}>
      {inner}
    </div>"""


def muscles(sid, imgs, title, left=632, top=600):
    """'Otot bekerja' card: one or two Gray's Anatomy plates, shown for the whole exercise clip."""
    pics = "".join(f'<img src="assets/images/{f}" alt="" style="display:block; width: {w}px;">' for f, w in imgs)
    return f"""    <div style="position:absolute; left: {left}px; top: {top}px;">
      <div id="{sid}-an" class="anat" style="padding: 8px 8px 6px; border-width: 4px; border-radius: 18px;">
        <div style="display:flex; gap: 4px;">{pics}</div>
        <div class="t">Otot bekerja:</div><div class="t" style="margin-top:0; color:{PINK};">{title}</div>
        <div class="c" data-layout-ignore>Gray's Anatomy (domain awam)</div>
      </div>
    </div>"""


TIMER_SVG = f"""<svg width="134" height="134" viewBox="0 0 230 230">
  <circle cx="115" cy="115" r="92" fill="#ffffff" stroke="{INK}" stroke-width="8"/>
  <circle cx="115" cy="115" r="76" fill="none" stroke="#e6e6e6" stroke-width="20"/>
  <circle id="{{p}}-ring" cx="115" cy="115" r="76" fill="none" stroke="{GREEN}" stroke-width="20" stroke-linecap="round"
          stroke-dasharray="477.5" stroke-dashoffset="477.5" transform="rotate(-90 115 115)"/>
  <text id="{{p}}-num" x="115" y="134" text-anchor="middle" font-family="Anton" font-size="62" fill="{INK}">1:00</text>
</svg>"""


# Rep moments (film seconds): goblet = bottom of the squat, halo = kettlebell over the head, swing = kettlebell at
# chest height (tools/rep_times.py head-top track). A rep while the reps block is still arriving is not counted.
REPS = {1: [9.70, 11.50, 13.15, 14.95],
        2: [21.60, 23.50, 25.80, 27.90],
        3: [33.45, 34.90, 36.50, 38.15, 39.75]}
REPS_START = 12
HEADER_END = 2.60   # exercise name shown for the first 2.6 s of each 12 s exercise clip, then the reps block
REPS_LINE_PX = 47   # "12 REPS × 3 SET" as wide as the 47 px "SETIAP LATIHAN" (Anton, measured)


def exercise_scene(sid, t0, t_end, n, l1, l2, imgs, title, an_left=632, an_top=600, hd_top=318):
    counts = [REPS_START - i for i in range(len(REPS[n]) + 1)]
    lines = "".join(f'<span id="{sid}-n{c}" class="cnum" style="opacity:{1 if i == 0 else 0}">{c} REPS <span class="g">&#215; 3 SET</span></span>'
                    for i, c in enumerate(counts))
    m = (top_block(sid, f"LATIHAN #{n}", l1, l2, top=hd_top) + "\n" + muscles(sid, imgs, title, an_left, an_top) + f"""
    <div class="col" style="top: 1262px; width: 330px; gap: 2px;" data-layout-allow-safe-zone>
      <div id="{sid}r-s" class="hd s70 y">SETIAP LATIHAN</div>
      <div id="{sid}r-t1" class="hd s70" style="font-size: {REPS_LINE_PX}px;"><span class="cbox">{lines}</span></div>
    </div>
    <div style="position:absolute; left: 500px; top: 1214px;" data-layout-allow-safe-zone>
      <div id="{sid}-tm" class="card" style="background:{YELLOW}; border-color:{INK}; padding: 10px 14px 8px; display:flex; flex-direction:column; align-items:center;">
        {TIMER_SVG.replace('{p}', sid)}
        <div class="lbl" style="color:{INK}; font-size: 24px; margin-top: 4px;">Rehat</div>
        <div class="lbl" style="color:{INK}; font-size: 19px; font-weight: 700;">setiap set</div>
      </div>
    </div>""")
    h = t0 + HEADER_END
    t_tm, d_tm = h + 1.0, t_end - h - 1.3   # timer runs 1:00 -> 0:00 over the rest of the exercise clip
    s = (blurin("s", t0 + 0.20) + slam("t1", t0 + 0.35) + slam("t2", t0 + 0.60, 1.4)
         + slide("an", t0 + 1.00, 140)
         + out(["s", "t1", "t2"], h)
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
         + f'      tl.to(["#{sid}r-s", "#{sid}r-t1", q("tm"), q("an")], {{ opacity: 0, filter: "blur(10px)", scale: 0.92, duration: 0.16, ease: "power2.in" }}, T({t_end - 0.18:.2f}));\n'
         + f'      tl.set(["#{sid}r-s", "#{sid}r-t1", q("tm"), q("an")], {{ opacity: 0 }}, T({t_end - 0.01:.2f}));\n')
    for i, t in enumerate(REPS[n]):
        a, b = counts[i], counts[i + 1]
        s += (f'      tl.set(q("n{a}"), {{ opacity: 0 }}, T({t:.2f}));\n'
              f'      tl.set(q("n{b}"), {{ opacity: 1 }}, T({t:.2f}));\n'
              f'      tl.fromTo(q("n{b}"), {{ scale: 1.45, color: "{YELLOW}" }}, {{ scale: 1, color: "#ffffff", duration: 0.35, ease: "back.out(2)", immediateRender: false }}, T({t:.2f}));\n')
    return m, s


def kb_icon(label):
    return (f'<div class="kbc" style="background:#f3f3f3;"><svg width="100%" height="100%" viewBox="0 0 118 158">'
            f'<path d="M36 64 C30 26 88 26 82 64" fill="none" stroke="#9a9a9a" stroke-width="11" stroke-linecap="round"/>'
            f'<circle cx="59" cy="96" r="38" fill="#c9c9c9" stroke="{INK}" stroke-width="4"/></svg><div class="kbl">{label}</div></div>')


def scenes():
    c = {x["id"]: x for x in CLIPS}
    files = {}
    css = LBS_CSS + H_CSS + K_CSS

    def win(cid):
        return c[cid]["start"], c[cid]["end"] - c[cid]["start"]

    def put(sid, cid, m, s, extra=""):
        st, du = win(cid)
        files[sid] = (st, du, scene_file(sid, st, du, m, s, css + extra))

    # ---------------- g01 hook (one shot at the running track) + save & repost sticker
    m = f"""    <div class="col" style="top: 760px; width: 768px; gap: 0;">
      <div id="g01-t1" class="hd h150">OBESE TAPI</div>
      <div id="g01-t2" class="hd h150 y">MALAS NAK</div>
      <div id="g01-t3" class="hd h150 p">JOGGING?</div>
      <div id="g01-s2" class="hd s70">BUAT <span class="g">3</span> SENAMAN MUDAH NI</div>
    </div>
    <div class="row" style="top: 1150px;" data-layout-allow-safe-zone><div id="g01-save" class="pill white">{BOOKMARK_SVG.format(id='g01-mark').replace('width="44" height="54"', 'width="26" height="32"')}{REPOST_SVG}Save &amp; repost video sebelum hilang</div></div>"""
    s = (f'      tl.fromTo(q("t1"), {{ opacity: 0, scale: 1.35 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }}, 0.03);\n'
         + slam("t2", 0.40, 1.4) + slam("t3", 0.75, 1.5) + blurin("s2", 1.45) + popin("save", 2.30)
         + '      tl.fromTo(q("mark"), { fill: "#ffffff" }, { fill: "' + YELLOW + '", duration: 0.12 }, T(2.90));\n'
         + '      tl.fromTo(q("rp"), { rotation: 0 }, { rotation: 360, duration: 0.5, ease: "power2.inOut", svgOrigin: "22 22" }, T(3.10));\n'
         + '      tl.fromTo(q("save"), { scale: 1 }, { scale: 1.1, duration: 0.1, yoyo: true, repeat: 1, ease: "power2.out" }, T(2.90));\n'
         + out(["t1", "t2", "t3", "s2", "save"], 4.80))
    put("g01", "c01", m, s)

    m, s = exercise_scene("g02", 5.00, 17.00, 1, "GOBLET", "SQUAT", [("gray430-thigh-front.png", 72), ("gray434-glutes-hamstrings.png", 72)], "Peha &amp; punggung", an_left=150)
    put("g02", "c02", m, s)
    m, s = exercise_scene("g03", 17.00, 29.00, 2, "KETTLEBELL", "HALOS", [("gray397-rectus.png", 88)], "Bahu &amp; core", an_left=716, an_top=540, hd_top=820)
    put("g03", "c03", m, s)
    m, s = exercise_scene("g04", 29.00, 41.00, 3, "KETTLEBELL", "SWING", [("gray434-glutes-hamstrings.png", 96)], "Punggung &amp;<br>hamstring")
    put("g04", "c04", m, s)

    # ---------------- g05 the three together = total body workout
    ck = CHECK_SVG.replace('width="54" height="54"', 'width="30" height="30"')
    m = top_block("g05", "KOMBINASI 3 SENAMAN NI", "TOTAL BODY", "WORKOUT", c2="g") + f"""
    <div class="col" style="top: 860px; gap: 16px;">
      <div id="g05-p1" class="pill white">{ck}Goblet squat: kaki &amp; punggung</div>
      <div id="g05-p2" class="pill white">{ck}Halos: bahu, lengan &amp; core</div>
      <div id="g05-p3" class="pill white">{ck}Swing: belakang &amp; pinggul</div>
    </div>"""
    s = (blurin("s", 41.20) + slam("t1", 41.45) + slam("t2", 41.75, 1.4)
         + slide("p1", 42.30) + slide("p2", 42.85) + slide("p3", 43.40)
         + out(["s", "t1", "t2", "p1", "p2", "p3"], 45.80))
    put("g05", "c05", m, s)

    # ---------------- g06 afterburn effect (EPOC diagram, Wikimedia Commons CC BY-SA 4.0, credit on screen)
    m = f"""    <div class="row up" style="top: 318px;">
      <div id="g06-fig" class="card" style="background:#fff; border-color:{INK}; padding: 12px 12px 8px; width: 640px; opacity: 0;">
        <div style="position: relative; width: 612px; height: 360px;">
          <img src="assets/images/epoc-diagram.jpg" alt="EPOC diagram" style="position:absolute; left:0; top:0; width: 612px; height: 360px; border-radius: 12px;">
          <div id="g06-h1" class="hl" style="left: 18.5%; width: 44%;"></div>
          <div id="g06-h2" class="hl" style="left: 61.8%; width: 36.5%;"></div>
        </div>
        <div class="credit" data-layout-ignore>Rajah EPOC: Henoktade / Wikimedia Commons, CC BY-SA 4.0</div>
      </div>
    </div>
    <div class="col" style="top: 840px; gap: 18px;">
      <div id="g06-c1" class="pill white">{ck}Masa workout: bakar kalori</div>
      <div id="g06-c2" class="pill">{ck}Lepas workout: masih bakar!</div>
    </div>
    <div class="col" style="top: 840px; gap: 0;">
      <div id="g06-t1" class="hd h150"><span class="fire">AFTERBURN</span></div>
      <div id="g06-t2" class="hd h150">EFFECT</div>
    </div>"""
    acss = f"""
.hl {{ position: absolute; top: 3%; height: 82%; border: 6px solid {PINK}; border-radius: 14px;
      background: rgba(255,61,139,.12); opacity: 0; }}
.credit {{ font-family: 'Montserrat', sans-serif; font-weight: 600; font-size: 15px; color: #555; margin-top: 4px; text-align: center; }}
.fire {{ background: linear-gradient(180deg, {YELLOW} 0%, #FF9A00 55%, #FF3D00 100%); -webkit-background-clip: text;
        background-clip: text; color: transparent; }}
#g06-t1 {{ -webkit-text-stroke: 0; }}
#g06-t1 .fire {{ filter: drop-shadow(5px 0 0 #0B0B0B) drop-shadow(-5px 0 0 #0B0B0B)
        drop-shadow(0 5px 0 #0B0B0B) drop-shadow(0 -5px 0 #0B0B0B); }}"""
    s = (popin("fig", 46.25, 0.6)
         + slide("c1", 46.60) + popin("h1", 46.60, 0.9, 0.3)
         + out(["h1"], 47.60) + slide("c2", 47.70, 140) + popin("h2", 47.70, 0.9, 0.3)
         + out(["c1", "c2"], 48.90)
         + slam("t1", 49.10) + slam("t2", 49.40, 1.4)
         + out(["t1", "t2", "fig", "h2"], 52.30))
    put("g06", "c06", m, s, acss)

    # ---------------- g07 USP: soft material
    m = top_block("g07", "MATERIAL", "LEMBUT", "", c2="g").replace('<div id="g07-t2" class="hd h150 g"></div>', "") + """
    <div class="row" style="top: 480px;"><div id="g07-tag" class="pill pink">Soft kettlebell</div></div>"""
    s = blurin("s", 52.70) + slam("t1", 52.90, 1.5) + popin("tag", 53.30) + out(["s", "t1", "tag"], 55.32)
    put("g07", "c07", m, s)

    # ---------------- g08 USP: drop test (hits at 56.20 s and 59.65 s)
    m = (top_block("g08", "BILA TERJATUH", "TAK", "PECAH", c2="g")
         + "\n" + top_block("g08b", "KENA KAKI", "TAK", "SAKIT", c2="g"))
    s = (blurin("s", 55.70) + slam("t1", 56.20, 1.6) + slam("t2", 56.40, 1.4) + out(["s", "t1", "t2"], 58.00)
         + '      tl.fromTo("#g08b-s", { opacity: 0, filter: "blur(14px)", y: 24 }, { opacity: 1, filter: "blur(0px)", y: 0, duration: 0.2, ease: "power4.out" }, T(58.20));\n'
         + '      tl.fromTo("#g08b-t1", { opacity: 0, scale: 1.6 }, { opacity: 1, scale: 1, duration: 0.32, ease: "expo.out" }, T(58.40));\n'
         + '      tl.fromTo("#g08b-t2", { opacity: 0, scale: 1.6 }, { opacity: 1, scale: 1, duration: 0.32, ease: "expo.out" }, T(58.65));\n'
         + '      tl.to(["#g08b-s", "#g08b-t1", "#g08b-t2"], { opacity: 0, duration: 0.12 }, T(59.96));\n')
    put("g08", "c08", m, s)

    # ---------------- g09 CTA
    m = top_block("g09", "", "2027 NAK UPGRADE", "BODY?", c2="p") + f"""
    <div class="row" style="top: 560px;">
      <div id="g09-btn" style="opacity:0; background:{YELLOW}; border: 6px solid {INK}; border-radius: 26px; padding: 12px 22px 14px;
           box-shadow: 0 10px 0 {INK}; display:flex; flex-direction:column;">
        <div class="lbl" style="color:{INK}; font-size: 24px;">Start bersenam</div>
        <div class="hd" style="opacity:1; font-size: 75px; color:{INK}; -webkit-text-stroke:0; text-shadow:none;">SEKARANG!</div>
      </div>
    </div>
    <div class="row" style="top: 770px;">
      <div id="g09-link" class="pill white">{CART_SVG.replace('width="96" height="86"', 'width="32" height="29"')}Kettlebell kat beg kuning</div>
    </div>
    <div style="position:absolute; left: 40px; top: 1390px; display:flex; flex-direction:column; align-items:flex-start;">
      <div id="g09-a1" style="opacity:0">{ARROW_SVG}</div>
      <div id="g09-a2" style="opacity:0; margin-top: -24px;">{ARROW_SVG}</div>
    </div>"""
    s = (slam("t1", 60.35) + slam("t2", 60.65, 1.4) + popin("btn", 61.30, 0.3) + popin("link", 61.90)
         + '      tl.fromTo([q("a1"), q("a2")], { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: 0.3, stagger: 0.08, ease: "expo.out" }, T(62.10));\n'
         + '      tl.to([q("a1"), q("a2")], { y: 26, duration: 0.28, yoyo: true, repeat: 3, stagger: 0.08, ease: "sine.inOut" }, T(62.60));\n'
         + '      tl.fromTo(q("btn"), { scale: 1 }, { scale: 1.07, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" }, T(62.60));\n')
    put("g09", "c09", m, s)
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
    ("impact", 0.00),
    ("pop-a", 0.40),
    ("pop-b", 0.75),
    ("pop-a", 1.45),
    ("pop-b", 2.30),
    ("ding", 2.90),
    ("whoosh-a", 5.00),
    ("pop-a", 5.35),
    ("pop-b", 5.60),
    ("pop-a", 6.00),
    ("whoosh-c", 7.80),
    ("ding", 8.30),
    ("whoosh-a", 17.00),
    ("pop-a", 17.35),
    ("pop-b", 17.60),
    ("pop-a", 18.00),
    ("whoosh-c", 19.80),
    ("ding", 20.30),
    ("whoosh-a", 29.00),
    ("pop-a", 29.35),
    ("pop-b", 29.60),
    ("pop-a", 30.00),
    ("whoosh-c", 31.80),
    ("ding", 32.30),
    ("whoosh-b", 41.00),
    ("pop-a", 41.45),
    ("impact", 41.75),
    ("pop-b", 42.30),
    ("pop-a", 42.85),
    ("pop-b", 43.40),
    ("whoosh-c", 46.00),
    ("pop-a", 46.25),
    ("pop-b", 46.60),
    ("pop-a", 47.70),
    ("zap", 49.10),
    ("impact", 49.40),
    ("whoosh-a", 52.50),
    ("pop-a", 52.90),
    ("pop-b", 53.30),
    ("whoosh-b", 55.50),
    ("impact", 56.20),
    ("pop-a", 56.40),
    ("pop-b", 58.40),
    ("pop-a", 58.65),
    ("impact", 59.65),
    ("whoosh-c", 60.10),
    ("pop-a", 60.35),
    ("pop-b", 61.30),
    ("cha-ching", 62.60),
    ("pop-a", 9.70),
    ("pop-b", 11.50),
    ("pop-a", 13.15),
    ("pop-b", 14.95),
    ("pop-a", 21.60),
    ("pop-b", 23.50),
    ("pop-a", 25.80),
    ("pop-b", 27.90),
    ("pop-a", 33.45),
    ("pop-b", 34.90),
    ("pop-a", 36.50),
    ("pop-b", 38.15),
    ("pop-a", 39.75),
]
SHAKES = [56.20, 59.65]  # camera shake on the drop-test hits (clip c08)


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
