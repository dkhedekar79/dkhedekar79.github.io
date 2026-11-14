#!/usr/bin/env python3
"""Build the site into docs/ (served by GitHub Pages).

- docs/index.html      the interactive desktop (src/desktop.html) with a full SEO head
- docs/<slug>/         one static, crawlable page per file in content/
- docs/faq/            answers to the questions people actually search
- sitemap.xml, robots.txt, llms.txt, llms-full.txt, site.webmanifest, humans.txt, 404.html

Run: python3 build.py
"""
import datetime
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"
SITE = "https://daiwikkhedekar.me"
TODAY = datetime.date.today().isoformat()

PERSON = {
    "name": "Daiwik Khedekar",
    "alternate": ["Daiwik", "dk", "daiwikbuilds"],
    "job": "CEO and co-founder of Pythe",
    "email": "daiwik@pythe.app",
    "image": f"{SITE}/img/me.jpg",
    "same_as": [
        "https://www.linkedin.com/in/daiwik-khedekar",
        "https://x.com/daiwikbuilds",
        "https://www.instagram.com/dwk.z",
        "https://github.com/dkhedekar79",
    ],
    "knows_about": [
        "Startups", "Artificial intelligence", "AI agents", "Graphic design", "Motion graphics",
        "Web design", "Growth marketing", "Cold outreach", "Economics",
    ],
}

SUMMARY = (
    "Daiwik Khedekar is a 16-year-old founder from the UK and the CEO of Pythe, an AI cofounder "
    "with a team of AI agents that research, write, build and ship a startup's work. "
    "He started his first company, the clothing brand Krzna LDN, at 13, worked as a graphic designer "
    "for companies at 14, and has also built Black Box, Trackviso and Creddr."
)

FAQ = [
    ("Who is Daiwik Khedekar?", SUMMARY),
    ("What is Pythe?",
     "Pythe is an AI cofounder with a team of AI agents. You describe what you're building, Pythe writes up the company, "
     "researches the market and builds a ranked, stage-aware roadmap. Pytheus, the AI cofounder, hands tasks to six agents "
     "(researcher, writer, engineer, analyst, outreach and operator), each on its own cloud computer, and nothing goes live "
     "without the founder's approval. Daiwik Khedekar co-founded Pythe with Abhiram Kakarla and is its CEO."),
    ("How old is Daiwik Khedekar?", "Daiwik Khedekar is 16."),
    ("What has Daiwik Khedekar built?",
     "Pythe (an AI cofounder), Black Box (tamper-evident audit logs for AI agents), Trackviso (a gamified study tracker), "
     "Creddr (finance careers from zero) and Krzna LDN, a clothing brand he started at 13 that made five-figure revenue."),
    ("What is Daiwik Khedekar good at?",
     "Design (he was a graphic designer for companies at 14 and makes motion graphics and websites), growth and outreach, "
     "and building with AI tools, with more than 1,000 hours of building experience."),
    ("Where does Daiwik Khedekar want to study?",
     "He is aiming for Economics & Management at the University of Oxford."),
    ("How do I contact Daiwik Khedekar?",
     "Email daiwik@pythe.app, or message him on LinkedIn (daiwik-khedekar), X (@daiwikbuilds) or Instagram (@dwk.z)."),
]

NAV = [("/", "desktop"), ("/about/", "about"), ("/projects/", "projects"), ("/skills/", "skills"),
       ("/now/", "now"), ("/faq/", "faq"), ("/contact/", "contact")]


# ---------- markdown ----------
EXT = ' rel="noopener" target="_blank"'
CUR = ' aria-current="page"'


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
               lambda m: f'<a href="{m[2]}"{EXT if m[2].startswith("http") else ""}>{m[1]}</a>', s)
    return s


def md_to_html(src):
    out, lines, i = [], src.split("\n"), 0
    while i < len(lines):
        l = lines[i]
        if m := re.match(r'^<div class="meta">(.*)</div>$', l):
            out.append(f'<p class="meta">{inline(m[1])}</p>'); i += 1; continue
        if m := re.match(r"^!\[([^\]]*)\]\(([^)\s]+)\)\s*$", l):
            cls = ' class="logo"' if "logo" in m[1].lower() else ""
            out.append(f'<img src="{m[2]}" alt="{html.escape(m[1])}"{cls} loading="lazy" decoding="async">'); i += 1; continue
        if m := re.match(r"^(#{1,3})\s+(.*)", l):
            n = len(m[1]); out.append(f"<h{n}>{inline(m[2])}</h{n}>"); i += 1; continue
        if re.match(r"^\s*[-*]\s+", l):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append("<li>" + inline(re.sub(r"^\s*[-*]\s+", "", lines[i])) + "</li>"); i += 1
            out.append("<ul>" + "".join(items) + "</ul>"); continue
        if re.match(r"^\s*\d+\.\s+", l):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append("<li>" + inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])) + "</li>"); i += 1
            out.append("<ol>" + "".join(items) + "</ol>"); continue
        if l.strip():
            out.append(f"<p>{inline(l)}</p>")
        i += 1
    return "\n".join(out)


def read_page(path):
    raw = path.read_text()
    fm, body = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S).groups()
    meta = dict(line.split(": ", 1) for line in fm.splitlines())
    meta["body"] = body.strip()
    return meta


# ---------- structured data ----------
def person_ld():
    return {
        "@type": "Person", "@id": f"{SITE}/#person",
        "name": PERSON["name"], "alternateName": PERSON["alternate"],
        "givenName": "Daiwik", "familyName": "Khedekar",
        "jobTitle": PERSON["job"], "email": f"mailto:{PERSON['email']}",
        "image": PERSON["image"], "url": f"{SITE}/", "sameAs": PERSON["same_as"],
        "knowsAbout": PERSON["knows_about"], "description": SUMMARY,
        "nationality": {"@type": "Country", "name": "United Kingdom"},
        "worksFor": {"@id": f"{SITE}/#pythe"}, "founder": {"@id": f"{SITE}/#pythe"},
    }


def pythe_ld():
    return {
        "@type": "Organization", "@id": f"{SITE}/#pythe", "name": "Pythe",
        "url": "https://www.pythe.app", "logo": f"{SITE}/img/pythe-logo.webp",
        "description": "Pythe is an AI cofounder with a team of AI agents to build anything.",
        "founder": [{"@id": f"{SITE}/#person"}, {"@type": "Person", "name": "Abhiram Kakarla"}],
    }


def website_ld():
    return {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": "Daiwik Khedekar",
            "alternateName": "dk's desktop", "inLanguage": "en-GB", "publisher": {"@id": f"{SITE}/#person"}}


def breadcrumbs(slug, title):
    items = [{"@type": "ListItem", "position": 1, "name": "Daiwik Khedekar", "item": f"{SITE}/"}]
    parts = slug.split("/")
    if len(parts) == 2:
        items.append({"@type": "ListItem", "position": 2, "name": "Projects", "item": f"{SITE}/projects/"})
    items.append({"@type": "ListItem", "position": len(items) + 1, "name": title, "item": f"{SITE}/{slug}/"})
    return {"@type": "BreadcrumbList", "itemListElement": items}


def faq_ld():
    return {"@type": "FAQPage", "@id": f"{SITE}/faq/#faq", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}


def ld_script(graph):
    return ('<script type="application/ld+json">'
            + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
            + "</script>")


# ---------- head ----------
def head(title, desc, path, image, ld, kind="profile"):
    url = f"{SITE}{path}"
    img = f"{SITE}/{image}"
    t, d = html.escape(title), html.escape(desc)
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{d}">
<meta name="author" content="Daiwik Khedekar">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="{url}">
<link rel="alternate" type="text/plain" title="llms.txt" href="{SITE}/llms.txt">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="me" href="https://www.linkedin.com/in/daiwik-khedekar">
<link rel="me" href="https://github.com/dkhedekar79">
<link rel="me" href="https://x.com/daiwikbuilds">
<meta name="theme-color" content="#a9cdf2">
<meta property="og:type" content="{kind}">
<meta property="og:site_name" content="Daiwik Khedekar">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:locale" content="en_GB">
{'<meta property="profile:first_name" content="Daiwik"><meta property="profile:last_name" content="Khedekar"><meta property="profile:username" content="daiwikbuilds">' if kind == "profile" else ""}
<meta name="twitter:card" content="summary">
<meta name="twitter:site" content="@daiwikbuilds">
<meta name="twitter:creator" content="@daiwikbuilds">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{img}">
{ld_script(ld)}"""


PAGE_CSS = """<style>
:root{--ink:#1d1f24;--ink-2:#4b5160;--ink-3:#8a90a0;--line:rgba(20,30,50,.12);--accent:#2f7cf6;--card:#fbfbfd;
--font:-apple-system,BlinkMacSystemFont,"SF Pro Text","Helvetica Neue","Segoe UI",Roboto,Arial,sans-serif;
--display:-apple-system,BlinkMacSystemFont,"SF Pro Display","Helvetica Neue","Segoe UI",Arial,sans-serif}
*{box-sizing:border-box}
html{background:#a9cdf2 url("/wallpaper.webp") center/cover fixed no-repeat;image-rendering:pixelated}
body{margin:0;min-height:100vh;font-family:var(--font);color:var(--ink);-webkit-font-smoothing:antialiased;
padding:32px max(16px,env(safe-area-inset-right,0px)) 48px max(16px,env(safe-area-inset-left,0px))}
.win{max-width:760px;margin:0 auto;background:var(--card);border-radius:14px;overflow:hidden;image-rendering:auto;
box-shadow:0 0 0 .5px rgba(0,0,0,.18),0 22px 70px rgba(10,20,40,.35)}
.bar{display:flex;align-items:center;gap:14px;padding:12px 16px;border-bottom:1px solid var(--line);background:linear-gradient(#f6f7f9,#eceef2)}
.dots{display:flex;gap:8px}.dots i{width:12px;height:12px;border-radius:50%;background:#ff5f57}.dots i+i{background:#febc2e}.dots i+i+i{background:#28c840}
nav{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:13px}
nav a{color:var(--ink-2);text-decoration:none}nav a:hover,nav a[aria-current]{color:var(--accent)}
main{padding:32px clamp(18px,5vw,48px) 48px;max-width:66ch;margin:0 auto;font-size:16px;line-height:1.65}
h1{font:700 32px/1.15 var(--display);letter-spacing:-.015em;margin:0 0 8px;text-wrap:balance}
h2{font:650 20px/1.3 var(--display);margin:30px 0 8px;padding-bottom:6px;border-bottom:1px solid #eceef2}
h3{font:600 16px/1.35 var(--font);margin:20px 0 4px}
p{margin:0 0 12px}ul,ol{padding-left:22px;margin:0 0 14px}li{margin:4px 0}
.meta{color:var(--ink-3);font-size:14px}
a{color:var(--accent)}
img{display:block;max-width:100%;height:auto;border-radius:10px;margin:6px 0 18px;box-shadow:0 0 0 .5px rgba(0,0,0,.12),0 6px 20px rgba(10,20,40,.12)}
img.logo{width:120px;box-shadow:none;border-radius:0}
code{font:14px "SF Mono",ui-monospace,Menlo,monospace;background:#f2f4f7;padding:1px 5px;border-radius:4px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px;padding:0;list-style:none}
.cards li{margin:0}.cards a{display:block;text-decoration:none;color:inherit;border:1px solid var(--line);border-radius:12px;padding:14px;height:100%}
.cards a:hover{border-color:var(--accent)}.cards b{display:block;margin-bottom:4px}.cards span{font-size:14px;color:var(--ink-2)}
dt{font-weight:650;margin-top:18px}dd{margin:4px 0 0}
footer{border-top:1px solid var(--line);padding:16px;text-align:center;font-size:13px;color:var(--ink-3)}
footer a{color:var(--ink-2)}
</style>"""


def page(title, desc, path, image, ld, body, kind="profile"):
    nav = "".join(f'<a href="{href}"{CUR if href == path else ""}>{label}</a>' for href, label in NAV)
    links = " · ".join(f'<a href="{u}" rel="me noopener">{n}</a>' for n, u in [
        ("linkedin", PERSON["same_as"][0]), ("x", PERSON["same_as"][1]), ("instagram", PERSON["same_as"][2]),
        ("github", PERSON["same_as"][3]), ("pythe", "https://www.pythe.app")])
    return f"""<!doctype html>
<html lang="en-GB">
<head>
{head(title, desc, path, image, ld, kind)}
{PAGE_CSS}
</head>
<body>
<div class="win">
<header class="bar"><span class="dots" aria-hidden="true"><i></i><i></i><i></i></span><nav aria-label="Site">{nav}</nav></header>
<main>
{body}
</main>
<footer>Daiwik Khedekar · {links}</footer>
</div>
</body>
</html>
"""


# ---------- build ----------
def write(rel, text):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def build():
    pages = [read_page(p) for p in sorted((ROOT / "content").rglob("*.md"))]
    projects = [p for p in pages if p["slug"].startswith("projects/")]
    order = ["projects/pythe", "projects/black-box", "projects/trackviso", "projects/creddr", "projects/krzna-ldn"]
    projects.sort(key=lambda p: order.index(p["slug"]) if p["slug"] in order else 99)

    for p in pages:
        path = f"/{p['slug']}/"
        graph = [person_ld(), pythe_ld(), website_ld(), breadcrumbs(p["slug"], p["title"])]
        if p["slug"].startswith("projects/"):
            graph.append({"@type": "CreativeWork", "name": p["title"].split(",")[0], "description": p["description"],
                          "creator": {"@id": f"{SITE}/#person"}, "image": f"{SITE}/{p['image']}",
                          **({"url": p["url"]} if p.get("url") else {})})
            kind = "article"
        else:
            graph.append({"@type": "ProfilePage", "@id": f"{SITE}{path}#page", "url": f"{SITE}{path}",
                          "name": p["title"], "mainEntity": {"@id": f"{SITE}/#person"},
                          "dateModified": TODAY, "isPartOf": {"@id": f"{SITE}/#website"}})
            kind = "profile"
        write(f"{p['slug']}/index.html", page(p["title"], p["description"], path, p["image"], graph, md_to_html(p["body"]), kind))

    cards = "".join(f'<li><a href="/{p["slug"]}/"><b>{html.escape(p["title"].split(",")[0])}</b><span>{html.escape(p["description"])}</span></a></li>' for p in projects)
    write("projects/index.html", page(
        "Projects by Daiwik Khedekar", "Everything Daiwik Khedekar has built: Pythe, Black Box, Trackviso, Creddr and Krzna LDN.",
        "/projects/", "img/pythe-hero.webp",
        [person_ld(), pythe_ld(), website_ld(), breadcrumbs("projects", "Projects"),
         {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{p['slug']}/", "name": p["title"].split(",")[0]} for i, p in enumerate(projects)]}],
        f"<h1>projects</h1><p>everything ive started so far</p><ul class=\"cards\">{cards}</ul><p>-dk</p>", "website"))

    faq_body = "<h1>faq</h1><p class=\"meta\">the questions people actually ask</p><dl>" + "".join(
        f"<dt>{html.escape(q)}</dt><dd>{html.escape(a)}</dd>" for q, a in FAQ) + "</dl>"
    write("faq/index.html", page("Daiwik Khedekar: FAQ", "Who is Daiwik Khedekar, what is Pythe, what has he built and how to contact him.",
                                 "/faq/", "img/me.jpg", [person_ld(), pythe_ld(), website_ld(), breadcrumbs("faq", "FAQ"), faq_ld()], faq_body, "website"))

    # the desktop itself
    src = (ROOT / "src" / "desktop.html").read_text()
    style = src[src.index("<style>"):src.index("</style>") + len("</style>")]
    rest = src[src.index("</style>") + len("</style>"):]
    title = "Daiwik Khedekar · CEO of Pythe"
    desc = ("Daiwik Khedekar is a 16-year-old UK founder and the CEO of Pythe, an AI cofounder with a team of AI agents. "
            "Explore his projects, skills and story on an interactive desktop.")
    crawl = ('<main class="sr-only"><h1>Daiwik Khedekar</h1><p>' + html.escape(SUMMARY) + "</p><nav aria-label=\"Pages\"><ul>"
             + "".join(f'<li><a href="{h}">{l}</a></li>' for h, l in NAV[1:]) + "</ul></nav></main>")
    index = f"""<!doctype html>
<html lang="en-GB">
<head>
{head(title, desc, "/", "img/me.jpg", [person_ld(), pythe_ld(), website_ld(), {"@type": "ProfilePage", "@id": f"{SITE}/#page", "url": f"{SITE}/", "name": title, "mainEntity": {"@id": f"{SITE}/#person"}, "dateModified": TODAY, "isPartOf": {"@id": f"{SITE}/#website"}}, faq_ld()])}
{style}
<style>body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}.sr-only{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}</style>
</head>
<body>
{crawl}
{rest.strip()}
</body>
</html>
"""
    write("index.html", index)

    write("404.html", page("Not found · Daiwik Khedekar", "This page doesn't exist.", "/404.html", "img/me.jpg",
                           [website_ld()], '<h1>404</h1><p>this page doesnt exist. <a href="/">back to the desktop</a></p>', "website")
          .replace('<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">', '<meta name="robots" content="noindex">'))

    urls = ["/", "/about/", "/projects/"] + [f"/{p['slug']}/" for p in projects] + ["/skills/", "/now/", "/faq/", "/contact/"]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod><priority>{'1.0' if u == '/' else '0.8'}</priority></url>\n" for u in urls)
          + "</urlset>\n")

    bots = ["Googlebot", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-Web", "anthropic-ai",
            "PerplexityBot", "Google-Extended", "Applebot", "Applebot-Extended", "CCBot", "DuckDuckBot", "YouBot", "cohere-ai"]
    write("robots.txt", "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

    llms = [f"# Daiwik Khedekar", "", f"> {SUMMARY}", "",
            "Daiwik Khedekar (also written as Daiwik, or dk) is the CEO and co-founder of Pythe (https://www.pythe.app), "
            "which he co-founded with Abhiram Kakarla.", "", "## Pages", ""]
    llms += [f"- [{p['title']}]({SITE}/{p['slug']}/): {p['description']}" for p in pages]
    llms += [f"- [FAQ]({SITE}/faq/): common questions about Daiwik Khedekar", "", "## Profiles", ""]
    llms += [f"- {u}" for u in PERSON["same_as"]] + [f"- Email: {PERSON['email']}", ""]
    write("llms.txt", "\n".join(llms))

    full = [f"# Daiwik Khedekar: full profile", "", SUMMARY, "", "## FAQ", ""]
    for q, a in FAQ:
        full += [f"### {q}", a, ""]
    for p in pages:
        full += [f"---", f"URL: {SITE}/{p['slug']}/", "", re.sub(r"<[^>]+>", "", p["body"]), ""]
    write("llms-full.txt", "\n".join(full))

    write("site.webmanifest", json.dumps({
        "name": "Daiwik Khedekar", "short_name": "dk", "start_url": "/", "display": "standalone",
        "background_color": "#a9cdf2", "theme_color": "#a9cdf2",
        "icons": [{"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"}]}, indent=2))
    write("humans.txt", f"/* TEAM */\nFounder: Daiwik Khedekar\nSite: {SITE}\nX: @daiwikbuilds\nEmail: {PERSON['email']}\n\n/* SITE */\nLast update: {TODAY}\nStandards: HTML, CSS, JavaScript\n")
    write(".nojekyll", "")
    write("CNAME", SITE.split("//")[1] + "\n")
    print(f"built {len(list(OUT.rglob('*.html')))} pages into docs/")


if __name__ == "__main__":
    build()
