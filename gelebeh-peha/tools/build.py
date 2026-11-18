"""Generate the HyperFrames project for "3 senaman untuk gelebeh peha" (no voiceover).

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

HERO, HEAD, SUB, LABEL = 140, 112, 84, 36
CAPTION = 60
YELLOW, GREEN, PINK, RED, INK = "#FFE600", "#39FF14", "#FF3D8B", "#FF2D2D", "#0B0B0B"

# ---------------------------------------------------------------- on-screen script (captions)
# No voiceover: captions carry the spoken-style guide lines, read at ~0.32 s a word.
# Lines a graphic already writes out (titles, tips, USP, CTA) are NOT captions.
SCRIPT = [
    (2.30, "Jom cuba kat rumah!"),
    (6.20, "Pegang kettlebell depan dada"),
    (7.70, "Turun, punggung ke belakang"),
    (12.90, "Asalkan form betul"),
    (16.10, "Langkah ke depan"),
    (17.30, "Turun perlahan, tolak balik"),
    (26.10, "Kaki buka lebar"),
    (27.40, "Kettlebell di tengah"),
    (36.70, "Picit pun boleh!"),
]
KEYWORDS = {"KETTLEBELL", "DADA", "PUNGGUNG", "FORM", "LANGKAH", "LEBAR", "PICIT", "RUMAH!", "TOLAK"}
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


def header(sid, num, l1, l2, top=820):
    return f"""    <div class="row" style="top: {top}px; gap: 26px;">
      <div id="{sid}-badge" class="badge">#{num}</div>
      <div style="display:flex; flex-direction:column;">
        <div id="{sid}-t1" class="hd head">{l1}</div>
        <div id="{sid}-t2" class="hd head g">{l2}</div>
      </div>
    </div>"""


def anat(sid, left, img, title, w=160):
    return f"""    <div style="position:absolute; left: {left}px; top: 300px;">
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


def scenes():
    c = {x["id"]: x for x in CLIPS}
    files = {}

    def win(cid):
        return c[cid]["start"], c[cid]["end"] - c[cid]["start"]

    # ---------------- g01 hook: one shot, thighs close-up
    st, du = win("c01")
    m = """    <div class="row up" style="top: 300px;"><div id="g01-tag" class="pill pink">Kettlebell di rumah</div></div>
    <div class="col up" style="top: 372px; gap: 0;">
      <div id="g01-t1" class="hd hero"><span class="y">3</span> SENAMAN</div>
      <div id="g01-t2" class="hd sub">UNTUK <span class="p">GELEBEH PEHA</span></div>
    </div>"""
    s = (f'      tl.fromTo(q("t1"), {{ opacity: 1, scale: 1.35 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }}, 0);\n'
         f'      tl.fromTo(q("tag"), {{ opacity: 1, y: -40 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "expo.out" }}, 0);\n'
         + slam("t2", 0.50, 1.4)
         + out(["tag", "t1", "t2"], 4.22))
    files["g01"] = (st, du, scene_file("g01", st, du, m, s, LBS_CSS))

    # ---------------- g02 #1 goblet squat demo + front-thigh anatomy
    st, du = win("c02")
    m = header("g02", 1, "GOBLET", "SQUAT", 330) + "\n" + anat("g02", 650, "gray430-thigh-front.png", "Peha depan", 150)
    s = (popin("badge", 4.62) + slam("t1", 4.75) + slam("t2", 4.95, 1.4) + slide("an", 5.50, 140)
         + out(["badge", "t1", "t2", "an"], 9.22))
    files["g02"] = (st, du, scene_file("g02", st, du, m, s, LBS_CSS))

    # ---------------- g03 goblet tip: partial squat + depth gauge
    st, du = win("c03")
    rows = """      <div id="g03-q" class="lbs">Tak boleh turun habis?</div>
      <div id="g03-a" class="hd head g">PARTIAL SQUAT</div>
      <div id="g03-b" class="lbs">pun dah cukup!</div>"""
    m = tip_col("g03", rows) + f"""
    <div style="position:absolute; left: 120px; top: 310px;">
      <div id="g03-gauge" class="card" style="width: 300px; padding: 22px 26px;">
        <div class="lbl" style="font-size: 28px; margin-bottom: 14px;">Kedalaman</div>
        <div style="position: relative; height: 300px;">
          <div style="position:absolute; left: 22px; top: 0; width: 14px; height: 300px; border-radius: 7px; background: rgba(255,255,255,.2);"></div>
          <div style="position:absolute; left: 22px; top: 0; width: 14px; height: 150px; border-radius: 7px; background: {GREEN};"></div>
          <div class="lbl" style="position:absolute; left: 66px; top: -6px; font-size: 28px; color:#ddd;">Berdiri</div>
          <div id="g03-half" class="lbl" style="position:absolute; left: 66px; top: 132px; font-size: 30px; color:{GREEN};">Separuh ✓</div>
          <div class="lbl" style="position:absolute; left: 66px; top: 272px; font-size: 28px; color:#888;">Penuh</div>
          <div id="g03-mk" style="position:absolute; left: 6px; top: -16px; width: 46px; height: 46px; border-radius: 50%; background: {PINK}; border: 5px solid {INK};"></div>
        </div>
      </div>
    </div>"""
    s = (popin("pill", 9.60) + slide("gauge", 9.75) + blurin("q", 9.95) + slam("a", 10.45) + blurin("b", 11.05)
         + '      tl.fromTo(q("mk"), { y: 0 }, { y: 150, duration: 0.7, ease: "power2.inOut" }, T(10.30));\n'
         + '      tl.to(q("mk"), { y: 0, duration: 0.7, ease: "power2.inOut" }, T(11.60));\n'
         + '      tl.to(q("mk"), { y: 150, duration: 0.7, ease: "power2.inOut" }, T(12.50));\n'
         + '      tl.fromTo(q("half"), { scale: 1 }, { scale: 1.15, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" }, T(11.00));\n'
         + out(["pill", "q", "a", "b", "gauge"], 14.22))
    files["g03"] = (st, du, scene_file("g03", st, du, m, s, LBS_CSS))

    # ---------------- g04 #2 forward lunges demo
    st, du = win("c04")
    m = header("g04", 2, "FORWARD", "LUNGES", 330)
    s = (popin("badge", 14.62) + slam("t1", 14.75) + slam("t2", 14.95, 1.4)
         + out(["badge", "t1", "t2"], 19.22))
    files["g04"] = (st, du, scene_file("g04", st, du, m, s, LBS_CSS))

    # ---------------- g05 lunge tip: 90 degrees + diagram
    st, du = win("c05")
    rows = """      <div id="g05-a" class="hd head g">LUTUT 90°</div>
      <div id="g05-b1" class="lbs">Lutut depan jangan</div>
      <div id="g05-b2" class="lbs">lepas hujung kaki</div>"""
    m = tip_col("g05", rows) + f"""
    <div style="position:absolute; left: 560px; top: 300px;"><div id="g05-dg" class="diag">{LUNGE_SVG.replace('{p}', 'g05')}</div></div>"""
    s = (popin("pill", 19.60) + popin("dg", 19.90, 0.6) + slam("a", 20.40)
         + popin("m1", 20.55, 0.3, 0.3) + popin("m2", 20.75, 0.3, 0.3)
         + blurin("b1", 21.20) + blurin("b2", 21.45)
         + '      tl.fromTo(q("toe"), { opacity: 0 }, { opacity: 1, duration: 0.2 }, T(21.60));\n'
         + out(["pill", "a", "b1", "b2", "dg"], 24.22))
    files["g05"] = (st, du, scene_file("g05", st, du, m, s, LBS_CSS))

    # ---------------- g06 #3 sumo squat demo + inner-thigh anatomy
    st, du = win("c06")
    m = header("g06", 3, "SUMO", "SQUAT", 330) + "\n" + anat("g06", 650, "gray433-thigh-inner.png", "Peha dalam", 130)
    s = (popin("badge", 24.62) + slam("t1", 24.75) + slam("t2", 24.95, 1.4) + slide("an", 25.40, 140)
         + out(["badge", "t1", "t2", "an"], 29.22))
    files["g06"] = (st, du, scene_file("g06", st, du, m, s, LBS_CSS))

    # ---------------- g07 sumo tip: toes out 45 degrees + feet diagram
    st, du = win("c07")
    rows = """      <div id="g07-q" class="lbs">Hujung kaki pusing</div>
      <div id="g07-a" class="hd head g">45° KELUAR</div>
      <div id="g07-b" class="lbs">lutut ikut arah jari kaki</div>"""
    m = tip_col("g07", rows) + f"""
    <div style="position:absolute; left: 560px; top: 300px;"><div id="g07-dg" class="diag">{FEET_SVG.replace('{p}', 'g07')}</div></div>"""
    s = (popin("pill", 29.60) + popin("dg", 29.90, 0.6) + blurin("q", 30.20) + slam("a", 30.60)
         + '      tl.fromTo([q("arc"), q("lab")], { opacity: 0 }, { opacity: 1, duration: 0.2, stagger: 0.1 }, T(30.70));\n'
         + blurin("b", 31.60)
         + out(["pill", "q", "a", "b", "dg"], 34.42))
    files["g07"] = (st, du, scene_file("g07", st, du, m, s, LBS_CSS))

    # ---------------- g08 USP: soft material
    st, du = win("c08")
    m = """    <div class="col" style="top: 790px; gap: 4px;">
      <div id="g08-tag" class="pill pink">Soft kettlebell</div>
      <div id="g08-t1" class="hd head">MATERIAL</div>
      <div id="g08-t2" class="hd hero g">LEMBUT</div>
    </div>"""
    s = (popin("tag", 34.80) + slam("t1", 35.00) + slam("t2", 35.35, 1.5)
         + out(["tag", "t1", "t2"], 38.62))
    files["g08"] = (st, du, scene_file("g08", st, du, m, s, LBS_CSS))

    # ---------------- g09 USP: drop test (drops at 39.50 s and 42.95 s)
    st, du = win("c09")
    m = f"""    <div class="col" style="top: 780px; gap: 22px;">
      <div id="g09-i1" style="display:flex; align-items:center; gap: 18px; opacity:0;">{CHECK_SVG}
        <div><div class="hd sub g" style="opacity:1;">TAK PECAH</div><div class="lbs" style="opacity:1;">kalau terjatuh</div></div></div>
      <div id="g09-i2" style="display:flex; align-items:center; gap: 18px; opacity:0;">{CHECK_SVG}
        <div><div class="hd sub g" style="opacity:1;">TAK SAKIT KAKI</div><div class="lbs" style="opacity:1;">bila terkena</div></div></div>
    </div>"""
    s = (stamp("i1", 39.52, -3) + stamp("i2", 41.00, -3)
         + out(["i1", "i2"], 43.42))
    files["g09"] = (st, du, scene_file("g09", st, du, m, s, LBS_CSS))

    # ---------------- g10 CTA
    st, du = win("c10")
    m = f"""    <div class="col up" style="top: 350px; gap: 0;">
      <div id="g10-t1" class="hd head">NAK TRIM</div>
      <div id="g10-t2" class="hd head p">GELEBEH PEHA?</div>
    </div>
    <div class="row" style="top: 780px;">
      <div id="g10-btn" style="opacity:0; background:{YELLOW}; border: 8px solid {INK}; border-radius: 36px; padding: 18px 30px 20px;
           box-shadow: 0 14px 0 {INK}; display:flex; flex-direction:column;">
        <div style="display:flex; align-items:center; gap: 14px;">
          <div style="width:70px;">{CART_SVG.replace('width="96" height="86"', 'width="70" height="63"')}</div>
          <div class="lbl" style="color:{INK}; font-size: 34px;">Grab kettlebell kat</div>
        </div>
        <div class="hd head" style="opacity:1; color:{INK}; -webkit-text-stroke:0; text-shadow:none;">BEG KUNING</div>
        <div class="lbl" style="color:{INK}; font-size: 36px;">sekarang!</div>
      </div>
    </div>
    <div style="position:absolute; left: 40px; top: 1390px; display:flex; flex-direction:column; align-items:flex-start;">
      <div id="g10-a1" style="opacity:0">{ARROW_SVG}</div>
      <div id="g10-a2" style="opacity:0; margin-top: -24px;">{ARROW_SVG}</div>
    </div>"""
    s = (slam("t1", 43.85) + slam("t2", 44.20, 1.4) + popin("btn", 45.00, 0.3)
         + '      tl.fromTo([q("a1"), q("a2")], { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: 0.3, stagger: 0.08, ease: "expo.out" }, T(45.40));\n'
         + '      tl.to([q("a1"), q("a2")], { y: 26, duration: 0.28, yoyo: true, repeat: 3, stagger: 0.08, ease: "sine.inOut" }, T(45.90));\n'
         + '      tl.fromTo(q("btn"), { scale: 1 }, { scale: 1.07, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" }, T(46.30));\n')
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
    ("impact", 0.00), ("pop-a", 0.50),
    ("whoosh-a", 4.40), ("pop-a", 4.62), ("pop-b", 5.50),
    ("whoosh-b", 9.40), ("ding", 9.60), ("pop-a", 10.45),
    ("whoosh-c", 14.40), ("pop-a", 14.62),
    ("whoosh-a", 19.40), ("ding", 19.60), ("pop-b", 19.90), ("pop-a", 20.40),
    ("whoosh-b", 24.40), ("pop-a", 24.62), ("pop-b", 25.40),
    ("whoosh-c", 29.40), ("ding", 29.60), ("pop-b", 29.90), ("zap", 30.70),
    ("whoosh-a", 34.60), ("pop-a", 35.00), ("pop-b", 35.35),
    ("whoosh-b", 38.80), ("riser", 39.50), ("impact", 39.50), ("pop-a", 41.00), ("impact", 42.95),
    ("whoosh-c", 43.60), ("pop-a", 43.85), ("pop-b", 45.00), ("cha-ching", 46.30),
]
SHAKES = [39.50, 42.95]  # camera shake on the drop test hits


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
    for t in SHAKES:
        zooms.append(f'      tl.to("#z09", {{ x: 18, duration: 0.035, ease: "none" }}, {t}).to("#z09", {{ x: -14, duration: 0.05, ease: "none" }})'
                     f'.to("#z09", {{ x: 8, duration: 0.05, ease: "none" }}).to("#z09", {{ x: 0, duration: 0.06, ease: "power2.out" }});')
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
      <!-- Footage: 10 cuts, original sound at 30 % (c04 muted: its ambience reads as music). No voiceover, no music. -->
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
