"""Generate the SVG assets for the profile README.

    python assets/generate.py

Writes assets/banner.svg and assets/cards/<slug>.svg (default output
dir is the folder this script lives in). Every SVG is self-contained,
no external fonts or images, so GitHub's image proxy renders it as-is,
and all motion is CSS keyframes so it plays inside an <img>.

To add a project: write an art_<slug>() function that returns
(svg_fragment, css) drawn inside a 180x180 box, add a row to CARDS,
run the script, and reference assets/cards/<slug>.svg from README.md.
Pitches wrap automatically; the script stops if one needs more than 4 lines.

Preview without pushing (Windows, Edge installed):
    msedge --headless=new --window-size=580,210 --screenshot=out.png file:///.../assets/cards/<slug>.svg
"""
import sys, os


# Palette: matches kamaldhami.in (bg #0a0a0a, accent #4a9eff).
BG = "#0b0f14"
PANEL = "#10161d"
BORDER = "#1f2a36"
GRID = "#16202b"
TEXT = "#e6edf3"
MUTED = "#8b949e"
BLUE = "#4a9eff"
GREEN = "#7ee787"
ORANGE = "#f0883e"
RED = "#ff7b72"
PURPLE = "#bc8cff"

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"

REDUCE = "@media(prefers-reduced-motion:reduce){*{animation:none!important}}"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- banner
def banner():
    W, H = 1200, 300
    # Three foothill layers, drawn as polygons. Dehradun sits in the Doon
    # valley under the Shivalik hills, and Kamal's blog is "Building from
    # the Foothills", so the motif is his, not a template.
    far = "M680,230 L700,150 L760,185 L830,120 L900,170 L960,135 L1040,190 L1100,150 L1200,200 L1200,300 L620,300 Z"
    mid = "M620,300 L690,210 L720,250 L790,190 L860,240 L930,205 L1010,255 L1080,215 L1200,260 L1200,300 Z"
    near = "M580,300 L640,262 L680,290 L760,250 L850,285 L930,262 L1020,290 L1110,268 L1200,290 L1200,300 Z"
    # A "commit route": a dashed path running across the ridge line.
    route = "M600,205 C680,150 720,220 800,165 S900,200 960,150 S1080,200 1180,170"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">Kamal Singh Dhami</title>
<desc id="d">Full-stack engineer and ML student in Dehradun, India. Animated foothills with a route tracing the ridge line.</desc>
<defs>
  <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" fill="none" stroke="{GRID}" stroke-width=".7"/></pattern>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#0e1a2b"/><stop offset="1" stop-color="{BG}"/></linearGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop stop-color="{BG}"/><stop offset=".5" stop-color="{BG}" stop-opacity="0"/></linearGradient>
  <radialGradient id="sun"><stop stop-color="{BLUE}" stop-opacity=".55"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
  <clipPath id="clip"><rect width="{W}" height="{H}" rx="16"/></clipPath>
</defs>
<style>
  .sans{{font-family:{SANS}}} .mono{{font-family:{MONO}}}
  .route{{stroke-dasharray:6 14;animation:flow 4s linear infinite}}
  .draw{{stroke-dasharray:900;stroke-dashoffset:900;animation:draw 7s ease-out infinite}}
  .sun{{animation:breathe 6s ease-in-out infinite;transform-origin:1010px 95px}}
  .star{{animation:twinkle 3s ease-in-out infinite}}
  .s2{{animation-delay:1s}} .s3{{animation-delay:2s}} .s4{{animation-delay:.5s}}
  .cursor{{animation:blink 1.1s steps(1) infinite}}
  @keyframes flow{{to{{stroke-dashoffset:-80}}}}
  @keyframes draw{{0%{{stroke-dashoffset:900;opacity:0}}10%{{opacity:1}}70%,100%{{stroke-dashoffset:0;opacity:1}}}}
  @keyframes breathe{{50%{{transform:scale(1.18);opacity:.8}}}}
  @keyframes twinkle{{50%{{opacity:.15}}}}
  @keyframes blink{{50%{{opacity:0}}}}
  {REDUCE}
</style>
<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="url(#sky)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <!-- stars -->
  <circle class="star" cx="700" cy="60" r="1.5" fill="{TEXT}"/>
  <circle class="star s2" cx="860" cy="40" r="1.2" fill="{TEXT}"/>
  <circle class="star s3" cx="1120" cy="70" r="1.6" fill="{TEXT}"/>
  <circle class="star s4" cx="960" cy="90" r="1.1" fill="{TEXT}"/>
  <circle class="star s2" cx="1160" cy="30" r="1.3" fill="{TEXT}"/>
  <!-- sun -->
  <circle class="sun" cx="1010" cy="95" r="70" fill="url(#sun)"/>
  <circle cx="1010" cy="95" r="9" fill="{BLUE}"/>
  <!-- hills -->
  <path d="{far}" fill="#152333"/>
  <path d="{mid}" fill="#101b28"/>
  <path d="{near}" fill="#0c141d"/>
  <!-- route over the ridge -->
  <path class="draw" d="{route}" fill="none" stroke="{BLUE}" stroke-width="2" stroke-linecap="round" opacity=".9"/>
  <path class="route" d="{route}" fill="none" stroke="{TEXT}" stroke-width="1" stroke-linecap="round" opacity=".35"/>
  <circle cx="800" cy="165" r="3.5" fill="{GREEN}"/>
  <circle cx="960" cy="150" r="3.5" fill="{GREEN}"/>
  <circle cx="1180" cy="170" r="3.5" fill="{ORANGE}"/>
  <!-- left fade so text sits clean -->
  <rect width="{W}" height="{H}" fill="url(#fade)"/>
  <!-- text -->
  <text class="mono" x="56" y="78" font-size="13" fill="{BLUE}">~/dehradun $ whoami<tspan class="cursor" fill="{TEXT}">_</tspan></text>
  <text class="sans" x="56" y="138" font-size="50" font-weight="700" fill="{TEXT}" letter-spacing="-1">Kamal Singh Dhami</text>
  <text class="sans" x="56" y="176" font-size="20" fill="{MUTED}">Full-stack engineer and ML student. I build web products end to end,</text>
  <text class="sans" x="56" y="202" font-size="20" fill="{MUTED}">train the occasional CNN, and write about what broke along the way.</text>
  <g class="mono" font-size="12.5">
    <rect x="56" y="232" width="150" height="26" rx="13" fill="{PANEL}" stroke="{BORDER}"/>
    <text x="131" y="249" text-anchor="middle" fill="{TEXT}">Dehradun, India</text>
    <rect x="216" y="232" width="118" height="26" rx="13" fill="{PANEL}" stroke="{BORDER}"/>
    <text x="275" y="249" text-anchor="middle" fill="{TEXT}">GEHU  '27</text>
    <rect x="344" y="232" width="162" height="26" rx="13" fill="{PANEL}" stroke="{BORDER}"/>
    <circle cx="361" cy="245" r="4" fill="{GREEN}"/>
    <text x="431" y="249" text-anchor="middle" fill="{TEXT}">open to roles</text>
  </g>
  <rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{BORDER}"/>
</g>
</svg>'''


# ---------------------------------------------------------------- cards
# Cards are shown 400px wide on desktop (two per row) and shrink to about
# 290px on phones, so type is sized for that: the pitch stays ~12px there.
CARD_W, CARD_H = 480, 324
PAD = 26
ART_X, ART_Y, ART_S = 300, 104, 0.86   # motif box (180x180, scaled)
PITCH_SIZE, PITCH_LH, PITCH_W = 20, 28, 266
CHIP_SIZE = 15


def wrap(text, width_px, size):
    """Greedy word wrap using an average sans glyph width."""
    max_chars = int(width_px / (size * 0.5))
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if len(trial) <= max_chars:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def chips(tags, y):
    out, x = [], PAD
    for t in tags:
        w = 18 + len(t) * CHIP_SIZE * 0.6
        out.append(f'<rect x="{x:.0f}" y="{y-21}" width="{w:.0f}" height="30" rx="15" fill="{PANEL}" stroke="{BORDER}"/>')
        out.append(f'<text x="{x + w/2:.0f}" y="{y}" text-anchor="middle" fill="{MUTED}">{esc(t)}</text>')
        x += w + 8
    return "\n".join(out)


def card(slug, title, kicker, pitch, tags, art, art_css, accent):
    lines = wrap(pitch, PITCH_W, PITCH_SIZE)
    if len(lines) > 4:
        raise SystemExit(f"{slug}: pitch wraps to {len(lines)} lines, keep it to 4")
    body = "".join(
        f'<text class="sans" x="{PAD}" y="{136 + i*PITCH_LH}" font-size="{PITCH_SIZE}" fill="{MUTED}">{esc(l)}</text>'
        for i, l in enumerate(lines)
    )
    cx, cy = ART_X + 90 * ART_S, ART_Y + 90 * ART_S
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{CARD_H}" viewBox="0 0 {CARD_W} {CARD_H}" role="img" aria-labelledby="t d">
<title id="t">{esc(title)}</title>
<desc id="d">{esc(pitch)}</desc>
<defs>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{GRID}" stroke-width=".6"/></pattern>
  <radialGradient id="halo"><stop stop-color="{accent}" stop-opacity=".22"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
  <clipPath id="clip"><rect width="{CARD_W}" height="{CARD_H}" rx="16"/></clipPath>
</defs>
<style>
  .sans{{font-family:{SANS}}} .mono{{font-family:{MONO}}}
  {art_css}
  {REDUCE}
</style>
<g clip-path="url(#clip)">
  <rect width="{CARD_W}" height="{CARD_H}" fill="{BG}"/>
  <rect width="{CARD_W}" height="{CARD_H}" fill="url(#grid)"/>
  <circle cx="{cx:.0f}" cy="{cy:.0f}" r="110" fill="url(#halo)"/>
  <text class="mono" x="{PAD}" y="46" font-size="15" fill="{accent}">{esc(kicker)}</text>
  <text class="sans" x="{PAD}" y="88" font-size="32" font-weight="700" fill="{TEXT}" letter-spacing="-.4">{esc(title)}</text>
  {body}
  <g class="mono" font-size="{CHIP_SIZE}">{chips(tags, CARD_H - 30)}</g>
  <g transform="translate({ART_X},{ART_Y}) scale({ART_S})">{art}</g>
  <rect x=".5" y=".5" width="{CARD_W-1}" height="{CARD_H-1}" rx="16" fill="none" stroke="{BORDER}"/>
</g>
</svg>'''


# Motifs are drawn in a 180x180 box.

def art_prepology():
    css = f'''
  .today{{animation:step 6s steps(1) infinite}}
  .ring{{stroke-dasharray:138;stroke-dashoffset:138;animation:fill 6s ease-out infinite;transform:rotate(-90deg);transform-origin:140px 46px}}
  .tick{{animation:tick 6s steps(1) infinite;opacity:0}}
  .t2{{animation-delay:2s}} .t3{{animation-delay:4s}}
  @keyframes step{{0%{{transform:translateY(0)}}33%{{transform:translateY(34px)}}66%{{transform:translateY(68px)}}}}
  @keyframes fill{{0%{{stroke-dashoffset:138}}90%,100%{{stroke-dashoffset:20}}}}
  @keyframes tick{{0%{{opacity:0}}30%{{opacity:1}}100%{{opacity:1}}}}'''
    rows = ""
    labels = ["Organic chem", "Mock test 4", "Review 12 cards"]
    for i, l in enumerate(labels):
        y = 70 + i * 34
        rows += f'<rect x="18" y="{y}" width="100" height="24" rx="6" fill="{PANEL}" stroke="{BORDER}"/>'
        rows += f'<text class="mono" x="26" y="{y+16}" font-size="9.5" fill="{MUTED}">{l}</text>'
        rows += f'<path class="tick t{i+1}" d="M106,{y+12} l3,3 l6,-7" fill="none" stroke="{GREEN}" stroke-width="1.6"/>'
    art = f'''
  <rect class="today" x="14" y="66" width="108" height="32" rx="8" fill="none" stroke="{BLUE}" stroke-width="1.5"/>
  {rows}
  <circle cx="140" cy="46" r="22" fill="none" stroke="{BORDER}" stroke-width="5"/>
  <circle class="ring" cx="140" cy="46" r="22" fill="none" stroke="{BLUE}" stroke-width="5" stroke-linecap="round"/>
  <text class="mono" x="140" y="50" font-size="10" text-anchor="middle" fill="{TEXT}">today</text>'''
    return art, css


def art_linkup():
    css = f'''
  .link{{stroke-dasharray:120;stroke-dashoffset:120;animation:draw 5s ease-in-out infinite}}
  .l2{{animation-delay:.6s}} .l3{{animation-delay:1.2s}} .l4{{animation-delay:1.8s}}
  .hub{{animation:pulse 2.4s ease-in-out infinite;transform-origin:90px 90px}}
  @keyframes draw{{0%{{stroke-dashoffset:120}}50%,80%{{stroke-dashoffset:0}}100%{{stroke-dashoffset:-120}}}}
  @keyframes pulse{{50%{{transform:scale(1.25);opacity:.4}}}}'''
    pts = [(90, 28), (152, 90), (90, 152), (28, 90)]
    links = "".join(
        f'<line class="link l{i+1}" x1="90" y1="90" x2="{x}" y2="{y}" stroke="{PURPLE}" stroke-width="1.6"/>'
        for i, (x, y) in enumerate(pts)
    )
    nodes = "".join(
        f'<circle cx="{x}" cy="{y}" r="12" fill="{PANEL}" stroke="{BORDER}"/><text class="mono" x="{x}" y="{y+4}" font-size="9" text-anchor="middle" fill="{TEXT}">{s}</text>'
        for (x, y), s in zip(pts, ["A1", "B2", "C3", "D1"])
    )
    art = f'''
  <circle class="hub" cx="90" cy="90" r="24" fill="{PURPLE}" opacity=".25"/>
  {links}
  <circle cx="90" cy="90" r="16" fill="{PANEL}" stroke="{PURPLE}" stroke-width="1.5"/>
  <text class="mono" x="90" y="94" font-size="9" text-anchor="middle" fill="{TEXT}">team</text>
  {nodes}'''
    return art, css


def art_zencube():
    css = f'''
  .wall{{stroke-dasharray:6 6;animation:march 3s linear infinite}}
  .proc{{animation:bounce 4s ease-in-out infinite}}
  .cube{{animation:hover 5s ease-in-out infinite}}
  @keyframes march{{to{{stroke-dashoffset:-24}}}}
  @keyframes bounce{{0%,100%{{transform:translate(0,0)}}25%{{transform:translate(22px,-14px)}}50%{{transform:translate(-18px,-6px)}}75%{{transform:translate(10px,16px)}}}}
  @keyframes hover{{50%{{transform:translateY(-4px)}}}}'''
    # isometric cube centered at (90,92)
    art = f'''
  <rect class="wall" x="24" y="24" width="132" height="132" rx="10" fill="none" stroke="{GREEN}" stroke-width="1.5" opacity=".8"/>
  <g class="cube">
    <path d="M90,52 L128,72 L90,92 L52,72 Z" fill="#17311f" stroke="{GREEN}" stroke-width="1.2"/>
    <path d="M52,72 L90,92 L90,132 L52,112 Z" fill="#102417" stroke="{GREEN}" stroke-width="1.2"/>
    <path d="M128,72 L90,92 L90,132 L128,112 Z" fill="#0c1b12" stroke="{GREEN}" stroke-width="1.2"/>
  </g>
  <circle class="proc" cx="90" cy="92" r="5" fill="{ORANGE}"/>
  <text class="mono" x="90" y="170" font-size="9.5" text-anchor="middle" fill="{MUTED}">rlimit · chroot · seccomp</text>'''
    return art, css


def art_sre():
    css = f'''
  .alert{{animation:blink 1.2s steps(1) infinite}}
  .trace{{stroke-dasharray:5 9;animation:flow 2s linear infinite}}
  .scan{{animation:scan 5s ease-in-out infinite}}
  @keyframes blink{{50%{{opacity:.25}}}}
  @keyframes flow{{to{{stroke-dashoffset:-56}}}}
  @keyframes scan{{0%,100%{{transform:translateX(0)}}50%{{transform:translateX(96px)}}}}'''
    def box(x, y, label, stroke, cls=""):
        return (f'<rect class="{cls}" x="{x}" y="{y}" width="40" height="26" rx="6" fill="{PANEL}" stroke="{stroke}" stroke-width="1.4"/>'
                f'<text class="mono {cls}" x="{x+20}" y="{y+17}" font-size="9" text-anchor="middle" fill="{TEXT}">{label}</text>')
    art = f'''
  {box(18, 40, "web", BORDER)}
  {box(70, 40, "api", BORDER)}
  {box(122, 40, "db", RED, "alert")}
  <path class="trace" d="M70,53 H58" stroke="{BLUE}" stroke-width="1.4"/>
  <path class="trace" d="M122,53 H110" stroke="{BLUE}" stroke-width="1.4"/>
  <rect x="18" y="90" width="144" height="70" rx="8" fill="{PANEL}" stroke="{BORDER}"/>
  <text class="mono" x="26" y="106" font-size="9" fill="{GREEN}">$ query_logs db</text>
  <text class="mono" x="26" y="120" font-size="9" fill="{MUTED}">pool exhausted: 200/200</text>
  <text class="mono" x="26" y="134" font-size="9" fill="{MUTED}">leak &lt;- payment-svc</text>
  <text class="mono" x="26" y="150" font-size="9" fill="{ORANGE}">&gt; diagnose root_cause</text>
  <rect class="scan" x="22" y="94" width="40" height="62" rx="6" fill="{BLUE}" opacity=".07"/>'''
    return art, css


def art_yukti():
    css = f'''
  .b1{{animation:swap 6s ease-in-out infinite}}
  .b2{{animation:swap 6s ease-in-out infinite;animation-delay:3s}}
  .arrow{{stroke-dasharray:4 8;animation:flow 2s linear infinite}}
  @keyframes swap{{0%,45%{{opacity:1}}50%,95%{{opacity:.25}}}}
  @keyframes flow{{to{{stroke-dashoffset:-48}}}}'''
    art = f'''
  <g class="b1">
    <path d="M16,46 h100 a8,8 0 0 1 8,8 v22 a8,8 0 0 1 -8,8 h-70 l-12,12 v-12 h-18 a8,8 0 0 1 -8,-8 v-22 a8,8 0 0 1 8,-8 z" fill="{PANEL}" stroke="{BORDER}"/>
    <text class="mono" x="30" y="68" font-size="10" fill="{TEXT}">hola, ¿cómo estás?</text>
  </g>
  <path class="arrow" d="M90,100 V118" stroke="{ORANGE}" stroke-width="1.6"/>
  <g class="b2">
    <path d="M56,122 h100 a8,8 0 0 1 8,8 v22 a8,8 0 0 1 -8,8 h-18 v12 l-12,-12 h-70 a8,8 0 0 1 -8,-8 v-22 a8,8 0 0 1 8,-8 z" fill="{PANEL}" stroke="{ORANGE}"/>
    <text class="mono" x="68" y="144" font-size="10" fill="{TEXT}">hi, how are you?</text>
    <text class="mono" x="68" y="156" font-size="7.5" fill="{MUTED}">only you can see this</text>
  </g>'''
    return art, css


def art_virtukey():
    css = f'''
  .sel{{animation:jump 4s steps(1) infinite}}
  @keyframes jump{{0%{{transform:translate(0,0)}}25%{{transform:translate(70px,0)}}50%{{transform:translate(70px,56px)}}75%{{transform:translate(0,56px)}}}}'''
    tiles = ""
    for i, (x, y) in enumerate([(22, 42), (92, 42), (22, 98), (92, 98)]):
        tiles += f'<rect x="{x}" y="{y}" width="62" height="46" rx="6" fill="{PANEL}" stroke="{BORDER}"/>'
        tiles += f'<text class="mono" x="{x+31}" y="{y+28}" font-size="12" text-anchor="middle" fill="{MUTED}">{i+1}</text>'
    art = f'''
  {tiles}
  <rect class="sel" x="19" y="39" width="68" height="52" rx="8" fill="none" stroke="{BLUE}" stroke-width="2"/>
  <g class="mono" font-size="9.5">
    <rect x="34" y="156" width="36" height="18" rx="4" fill="{PANEL}" stroke="{BORDER}"/><text x="52" y="168" text-anchor="middle" fill="{TEXT}">Win</text>
    <text x="80" y="168" text-anchor="middle" fill="{MUTED}">+</text>
    <rect x="90" y="156" width="36" height="18" rx="4" fill="{PANEL}" stroke="{BLUE}"/><text x="108" y="168" text-anchor="middle" fill="{TEXT}">1..9</text>
  </g>'''
    return art, css


CARDS = [
    ("prepology", "Prepology", "study planner · live",
     "Tells a NEET, JEE or GATE student what to study today, and re-plans when they fall behind.",
     ["Flutter", "Hono", "Supabase", "Groq"], art_prepology, BLUE),
    ("linkup", "Link-UP", "teammate finder · live",
     "Find and form project teams at GEHU. Enforces the one-per-section rule.",
     ["React", "TypeScript", "Supabase"], art_linkup, PURPLE),
    ("zencube", "ZenCube", "linux sandbox",
     "A process sandbox in C, built to learn resource limits, chroot jails and seccomp.",
     ["C", "Python", "Linux"], art_zencube, GREEN),
    ("sre-env", "SRE Incident Env", "openenv · agents",
     "An agent gets paged, digs through a fake distributed system, and has to find the root cause.",
     ["Python", "Docker", "OpenEnv"], art_sre, RED),
    ("yukti", "Yukti", "discord bot",
     "Translates on demand and replies privately, so channels stay clean.",
     ["discord.py", "SQLite"], art_yukti, ORANGE),
    ("virtukey", "VirtuKey", "windows utility",
     "Win+number jumps straight to a virtual desktop, with no slide animation.",
     ["AutoHotkey v2", "Windows 11"], art_virtukey, BLUE),
]

def main():
    OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(OUT, "cards"), exist_ok=True)
    with open(os.path.join(OUT, "banner.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(banner())
    for slug, title, kicker, pitch, tags, fn, accent in CARDS:
        art, css = fn()
        with open(os.path.join(OUT, "cards", f"{slug}.svg"), "w", encoding="utf-8", newline="\n") as f:
            f.write(card(slug, title, kicker, pitch, tags, art, css, accent))
    print("wrote banner + %d cards to %s" % (len(CARDS), OUT))


if __name__ == "__main__":
    main()
