"""Rebuild the live parts of the profile README from the GitHub API.

    GH_TOKEN=... python assets/live.py

Writes assets/activity.svg (contribution heatmap, yearly numbers and the
most recently pushed repos) and rewrites two marked blocks in README.md:
ACTIVITY (the dashboard image and its alt text) and CONTRIB (repos owned
by other people that I have committed to or opened merged PRs against).

Token: the GitHub Action's built-in token only sees public repos. To list
private repos in "recently pushed", store a fine-grained personal access
token as the PROFILE_TOKEN secret: resource owner KamalSDhami, all
repositories, Metadata read-only. Nothing else is needed. Private repos
show by name only, never description or link.

Standard library only, so the Action needs no pip install.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from generate import (BG, PANEL, BORDER, GRID, TEXT, MUTED, BLUE, GREEN,  # noqa: E402
                      ORANGE, MONO, SANS, REDUCE, esc)

LOGIN = "KamalSDhami"
README = os.path.join(HERE, "..", "README.md")

# Repos never listed under "recently pushed".
HIDE = {"KamalSDhami"}

# Language shown for a repo when GitHub's guess is misleading (for example
# a repo whose bytes are mostly generated HTML). Colors are GitHub's.
LANG_OVERRIDE = {"prepology": ("Dart", "#00B4AB")}
SHORT_LANG = {"Jupyter Notebook": "Jupyter"}

# How many repos the dashboard lists.
RECENT_COUNT = 6

# Outside repos the token cannot see (someone else's private repo) or that
# you want to describe by hand. Each entry is shown exactly as written.
# Only add a private repo here with its owner's OK, since this page is public.
# Example:
#   {"name": "owner/repo", "url": None, "about": "What it is.",
#    "role": "What I did there."},
EXTRA_CONTRIB = [
    # Private repo, listed with the owner's OK (Oct 2026).
    {"name": "hemalbadola/baton", "url": None,
     "about": "Runs one LLM across several laptops on the same Wi-Fi, each holding a few "
              "layers and passing activations along like a relay baton. "
              "On PyPI as [baton-cluster](https://pypi.org/project/baton-cluster/).",
     "role": "I'm the second-largest contributor: int8 and int4 quantized weights in the decoder, "
             "recovery when a laptop drops out of the ring, per-hop network timing for the planner, "
             "and the Windows installer and PyPI release pipeline."},
]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(first: 20, ownerAffiliations: OWNER, isFork: false,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes { name url isPrivate pushedAt primaryLanguage { name color } }
    }
    repositoriesContributedTo(first: 30, includeUserRepositories: false,
                              contributionTypes: [COMMIT, PULL_REQUEST]) {
      nodes {
        nameWithOwner url isPrivate description stargazerCount
        primaryLanguage { name }
      }
    }
  }
}
"""


def graphql(token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"Bearer {token}", "User-Agent": "profile-readme"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]


# ------------------------------------------------------------ dashboard
W = 1200
CELL, GAP = 13, 3
STEP = CELL + GAP
HM_X, HM_Y = 66, 112          # heatmap origin
LEVELS = ["#151c25", "#0f3460", "#1b5bab", "#3a8ae8", "#8cc4ff"]


def level(n, cuts):
    if n == 0:
        return 0
    for i, c in enumerate(cuts, start=1):
        if n <= c:
            return i
    return 4


def nice_date(iso):
    d = dt.date.fromisoformat(iso[:10])
    return d.strftime("%b %d").replace(" 0", " ")


def stats(days):
    counts = [d["contributionCount"] for d in days]
    active = sum(1 for c in counts if c)
    best = cur = 0
    for c in counts:
        cur = cur + 1 if c else 0
        best = max(best, cur)
    # current streak, allowing today to be empty so far
    streak = 0
    for c in reversed(counts[:-1] if counts and counts[-1] == 0 else counts):
        if not c:
            break
        streak += 1
    top = max(days, key=lambda d: d["contributionCount"])
    return active, best, streak, top


def heatmap(weeks):
    nonzero = sorted(d["contributionCount"] for w in weeks for d in w["contributionDays"]
                     if d["contributionCount"])
    if nonzero:
        q = lambda p: nonzero[min(len(nonzero) - 1, int(len(nonzero) * p))]
        cuts = [q(.25), q(.5), q(.8)]
    else:
        cuts = [1, 2, 3]
    cells, months, css = [], [], []
    last_month = None
    for x, w in enumerate(weeks):
        for d in w["contributionDays"]:
            y = dt.date.fromisoformat(d["date"]).isoweekday() % 7   # Sunday = 0
            lv = level(d["contributionCount"], cuts)
            cells.append(
                f'<rect class="c w{x}" x="{HM_X + x*STEP}" y="{HM_Y + y*STEP}" width="{CELL}" '
                f'height="{CELL}" rx="3" fill="{LEVELS[lv]}"/>'
            )
        first = dt.date.fromisoformat(w["contributionDays"][0]["date"])
        # label a month at its first full week; skip a partial first week
        if first.month != last_month and x < len(weeks) - 2 and (x > 0 or first.day <= 7):
            months.append(f'<text x="{HM_X + x*STEP}" y="{HM_Y - 10}">{first.strftime("%b")}</text>')
            last_month = first.month
        elif x == 0:
            last_month = first.month
        css.append(f".w{x}{{animation-delay:{x*0.025:.3f}s}}")
    return "".join(cells), "".join(months), "".join(css), len(weeks)


def hot_ring(weeks):
    best = None
    for x, w in enumerate(weeks):
        for d in w["contributionDays"]:
            if best is None or d["contributionCount"] > best[0]:
                best = (d["contributionCount"], x, dt.date.fromisoformat(d["date"]).isoweekday() % 7)
    if not best or not best[0]:
        return ""
    _, x, y = best
    return (f'<rect class="hot" x="{HM_X + x*STEP - 3}" y="{HM_Y + y*STEP - 3}" width="{CELL+6}" '
            f'height="{CELL+6}" rx="5" fill="none" stroke="{GREEN}" stroke-width="1.5"/>')


def recent_rows(repos, y0):
    out = []
    col_w = 534
    for i, r in enumerate(repos):
        col, row = i % 2, i // 2
        x = 66 + col * (col_w + 0)
        y = y0 + row * 34
        lang = r["primaryLanguage"] or {"name": "", "color": "#6e7681"}
        if r["name"] in LANG_OVERRIDE:
            lang = dict(zip(("name", "color"), LANG_OVERRIDE[r["name"]]))
        lang = {"name": SHORT_LANG.get(lang["name"], lang["name"]), "color": lang["color"]}
        name = esc(r["name"])
        tag = ""
        nx = x + 22 + len(r["name"]) * 8.4 + 12
        if r["isPrivate"]:
            tag = (f'<rect x="{nx:.0f}" y="{y-14}" width="62" height="20" rx="10" fill="none" '
                   f'stroke="{ORANGE}" stroke-opacity=".7"/>'
                   f'<text x="{nx+31:.0f}" y="{y}" text-anchor="middle" font-size="11" fill="{ORANGE}">private</text>')
        out.append(
            f'<g class="row r{i}">'
            f'<circle cx="{x+6}" cy="{y-4}" r="5" fill="{lang["color"] or "#6e7681"}"/>'
            f'<text x="{x+22}" y="{y}" font-size="14" fill="{TEXT}">{name}</text>{tag}'
            f'<text x="{x+col_w-140}" y="{y}" font-size="12" fill="{MUTED}">{esc(lang["name"] or "")}</text>'
            f'<text x="{x+col_w-24}" y="{y}" font-size="12" text-anchor="end" fill="{MUTED}">{nice_date(r["pushedAt"])}</text>'
            f'</g>'
        )
    return "".join(out)


def dashboard(data, recent):
    cal = data["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    active, best, streak, top = stats(days)
    cells, months, wcss, nweeks = heatmap(weeks)
    hm_w = nweeks * STEP
    sx = HM_X + hm_w + 34                       # stats column x
    rows_y = HM_Y + 7*STEP + 92
    H = rows_y + ((len(recent) + 1) // 2) * 34 + 30
    legend_x = HM_X + hm_w - 5*STEP - 74
    legend = "".join(
        f'<rect x="{legend_x + 40 + i*STEP}" y="{HM_Y + 7*STEP + 10}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>'
        for i, c in enumerate(LEVELS))

    def stat(y, big, small, color=TEXT):
        return (f'<text class="sans" x="{sx}" y="{y}" font-size="30" font-weight="700" fill="{color}" letter-spacing="-.5">{big}</text>'
                f'<text class="mono" x="{sx}" y="{y+20}" font-size="12" fill="{MUTED}">{small}</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">Activity over the last year</title>
<desc id="d">{cal["totalContributions"]} contributions in the last year across {active} active days. Longest streak {best} days. Most recently pushed: {esc(", ".join(r["name"] + (" (private)" if r["isPrivate"] else "") for r in recent))}.</desc>
<defs>
  <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" fill="none" stroke="{GRID}" stroke-width=".6"/></pattern>
  <linearGradient id="scan" x1="0" x2="1"><stop stop-color="{BLUE}" stop-opacity="0"/><stop offset=".5" stop-color="{BLUE}" stop-opacity=".22"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>
  <clipPath id="clip"><rect width="{W}" height="{H}" rx="16"/></clipPath>
  <clipPath id="hm"><rect x="{HM_X-4}" y="{HM_Y-4}" width="{hm_w+4}" height="{7*STEP+4}"/></clipPath>
</defs>
<style>
  text{{font-family:{MONO}}} text.sans{{font-family:{SANS}}}
  .scan{{animation:scan 7s ease-in-out infinite}}
  @keyframes scan{{0%{{transform:translateX(-120px)}}100%{{transform:translateX({hm_w+40}px)}}}}
  .cursor{{animation:blink 1.1s steps(1) infinite}}
  @keyframes blink{{50%{{opacity:0}}}}
  .live{{animation:live 2.4s ease-in-out infinite}}
  .hot{{animation:hot 3s ease-in-out infinite}}
  @keyframes hot{{50%{{opacity:.35}}}}
  @keyframes live{{50%{{opacity:.3}}}}
  {REDUCE}
</style>
<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>

  <text x="{HM_X}" y="44" font-size="13" fill="{BLUE}">~/activity $ git log --since="1 year ago"<tspan class="cursor" fill="{TEXT}">_</tspan></text>
  <circle class="live" cx="{W-150}" cy="40" r="4" fill="{GREEN}"/>
  <text x="{W-138}" y="44" font-size="12" fill="{MUTED}">updated {dt.date.today().strftime("%b %d").replace(" 0", " ")}</text>

  <g font-size="11" fill="{MUTED}">{months}</g>
  <g font-size="10" fill="{MUTED}">
    <text x="{HM_X-34}" y="{HM_Y + 1*STEP + 10}">Mon</text>
    <text x="{HM_X-34}" y="{HM_Y + 3*STEP + 10}">Wed</text>
    <text x="{HM_X-34}" y="{HM_Y + 5*STEP + 10}">Fri</text>
  </g>
  {cells}
  {hot_ring(weeks)}
  <g clip-path="url(#hm)"><rect class="scan" x="{HM_X}" y="{HM_Y-4}" width="120" height="{7*STEP+4}" fill="url(#scan)"/></g>
  <g font-size="10" fill="{MUTED}">
    <text x="{legend_x}" y="{HM_Y + 7*STEP + 21}">less</text>{legend}<text x="{legend_x + 44 + 5*STEP}" y="{HM_Y + 7*STEP + 21}">more</text>
  </g>

  <line x1="{sx-18}" y1="{HM_Y-14}" x2="{sx-18}" y2="{HM_Y + 7*STEP}" stroke="{BORDER}"/>
  {stat(HM_Y + 14, cal["totalContributions"], "contributions this year", BLUE)}
  {stat(HM_Y + 70, f"{best} days", f"longest streak · {active} active days")}
  <rect class="hot" x="{sx}" y="{HM_Y + 7*STEP - 13}" width="{CELL}" height="{CELL}" rx="4" fill="none" stroke="{GREEN}" stroke-width="1.5"/>
  <text x="{sx + 22}" y="{HM_Y + 7*STEP - 2}" font-size="12" fill="{MUTED}">busiest day · {top["contributionCount"]} on {nice_date(top["date"])}</text>

  <line x1="{HM_X}" y1="{rows_y-46}" x2="{W-66}" y2="{rows_y-46}" stroke="{BORDER}"/>
  <text x="{HM_X}" y="{rows_y-18}" font-size="13" fill="{BLUE}">~/repos $ ls --sort=pushed | head -{len(recent)}</text>
  {recent_rows(recent, rows_y + 8)}

  <rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{BORDER}"/>
</g>
</svg>'''


# ------------------------------------------------------------ README blocks
def replace_block(text, name, body):
    pat = re.compile(rf"(<!-- {name}:START -->\n).*?(<!-- {name}:END -->)", re.S)
    if not pat.search(text):
        raise SystemExit(f"README has no {name} markers")
    return pat.sub(lambda m: m.group(1) + body + m.group(2), text)


def activity_block(data, recent):
    total = data["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    names = ", ".join(r["name"] + (" (private)" if r["isPrivate"] else "") for r in recent)
    alt = esc(f"{total} contributions in the last year. Recently pushed: {names}.").replace('"', "&quot;")
    links = " · ".join(
        f'{r["name"]} (private)' if r["isPrivate"] else f'[{r["name"]}]({r["url"]})'
        for r in recent)
    return (f'<a href="https://github.com/{LOGIN}?tab=repositories&sort=pushed">'
            f'<img src="assets/activity.svg" width="100%" alt="{alt}" /></a>\n\n'
            f'<sub>Recently pushed: {links}. Redrawn every six hours by a GitHub Action.</sub>\n')


def contrib_block(data):
    rows = []
    # A fine-grained token returns null for repos it cannot read.
    for r in filter(None, data["user"]["repositoriesContributedTo"]["nodes"]):
        if r["isPrivate"]:
            continue                         # someone else's private repo: never auto-listed
        about = (r["description"] or "").strip().rstrip(".")
        bits = [f'[{r["nameWithOwner"]}]({r["url"]})']
        if about:
            bits.append(f"{about}.")
        if r["stargazerCount"]:
            bits.append(f'<sub>★ {r["stargazerCount"]}</sub>')
        rows.append("- " + " ".join(bits))
    for e in EXTRA_CONTRIB:
        name = f'[{e["name"]}]({e["url"]})' if e.get("url") else f'**{e["name"]}** <sub>private</sub>'
        parts = [name] + [e[k].strip() for k in ("about", "role") if e.get(k, "").strip()]
        rows.append("- " + "<br>".join(parts))
    if not rows:
        return ("Nothing public yet. My work outside my own repos so far has been in private ones, "
                "so it shows up only in the heatmap above.\n")
    return "\n".join(rows) + "\n"


def main():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("Set GH_TOKEN.")
    data = graphql(token)
    if os.environ.get("PROFILE_TOKEN_SET") == "false":
        print("Token is not the profile owner's, so private repos are not visible. "
              "Add a PROFILE_TOKEN secret to include them.")
    repos = [r for r in data["user"]["repositories"]["nodes"] if r and r["name"] not in HIDE]
    recent = repos[:RECENT_COUNT]

    with open(os.path.join(HERE, "activity.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(dashboard(data, recent))

    with open(README, encoding="utf-8") as f:
        text = f.read()
    text = replace_block(text, "ACTIVITY", activity_block(data, recent))
    text = replace_block(text, "CONTRIB", contrib_block(data))
    with open(README, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("recent:", ", ".join(r["name"] + ("*" if r["isPrivate"] else "") for r in recent))


if __name__ == "__main__":
    main()
