"""LegalWithDev blog engine (Path A: markdown articles, no database).

Naya article daalne ka tarika:
  1. blog/ folder me ek nayi .md file banaiye
  2. File ka format:
         # Article ka Title
         date: 18 September 2026
         Ek line ki summary...
         --- se neeche poora article (markdown)
  3. GitHub pe upload karke commit kar dein — page khud ban jayega /blog/<filename> pe
"""
from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

BLOG_DIR = Path(__file__).parent / "blog"
router = APIRouter()

_BLOG_CSS = """
  body { font-family: -apple-system, 'Segoe UI', Roboto, 'Noto Sans', 'Noto Sans Devanagari', sans-serif;
    background: #0b1020; color: #e8edf7; margin: 0; padding: 20px 16px 48px; line-height: 1.75; }
  .page { max-width: 720px; margin: 0 auto; }
  a.top { color: #8aa2ff; text-decoration: none; font-size: 14px; }
  h1 { font-size: 25px; line-height: 1.3; margin: 14px 0 4px; }
  .date { color: #8b95ad; font-size: 13px; margin-bottom: 20px; }
  h2 { font-size: 19px; color: #8aa2ff; margin: 28px 0 8px; }
  h3 { font-size: 16px; color: #8aa2ff; margin: 22px 0 6px; }
  p, li { font-size: 15px; color: #c7d0e4; }
  ul { margin: 8px 0 8px 22px; }
  strong { color: #fff; }
  em { color: #8b95ad; }
  a { color: #8aa2ff; }
  .card { background: #151d33; border: 1px solid #232d4a; border-radius: 16px; padding: 18px 20px; margin: 14px 0; }
  .card h2 { margin: 0 0 6px; font-size: 18px; }
  .card h2 a { text-decoration: none; }
  .card .date { margin: 0 0 8px; }
  .card p { font-size: 14px; margin: 0 0 8px; }
  .card a.read { color: #8aa2ff; text-decoration: none; font-weight: 600; font-size: 14px; }
  @media (prefers-color-scheme: light) {
    body { background: #f2f3f7; color: #1c1c1e; }
    h1, h2, h3, .card h2 { color: #3b5bdb; }
    p, li { color: #3a3f4a; }
    strong { color: #000; }
    .card { background: #fff; border-color: #dfe3ee; box-shadow: 0 2px 10px rgba(28,28,30,.05); }
    .date, em { color: #6e7480; }
  }
"""

_BACK_LINK = '<a class="top" href="/">&larr; LegalWithDev</a>'


def _md_to_html(md_text: str) -> str:
    """Tiny safe markdown renderer: escape HTML first, then convert."""
    h = md_text.replace("&", "&" + "amp;").replace("<", "&" + "lt;").replace(">", "&" + "gt;")
    out: list[str] = []
    in_list = False
    for ln in h.split("\n"):
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            if in_list:
                out.append("</ul>")
                in_list = False
            level = len(m.group(1)) + 1
            out.append(f"<h{level}>{m.group(2)}</h{level}>")
        elif re.match(r"^[-*]\s+", ln):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>" + re.sub(r"^[-*]\s+", "", ln) + "</li>")
        elif ln.strip() == "":
            if in_list:
                out.append("</ul>")
                in_list = False
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<p>{ln}</p>")
    if in_list:
        out.append("</ul>")
    body = "\n".join(out)
    body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body)
    body = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", body)
    body = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<a href="\2" target="_blank" rel="noopener">\1</a>',
        body,
    )
    return body


def _load_posts() -> list[dict]:
    posts: list[dict] = []
    if not BLOG_DIR.exists():
        return posts
    for f in sorted(BLOG_DIR.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        title_m = re.search(r"^#\s+(.+)$", text, re.M)
        date_m = re.search(r"^date:\s*(.+)$", text, re.M)
        summary = ""
        if date_m:
            for ln in text[date_m.end():].split("\n"):
                s = ln.strip()
                if s and not s.startswith("#") and s != "---":
                    summary = s[:180]
                    break
        posts.append(
            {
                "slug": f.stem,
                "title": (title_m.group(1).strip() if title_m else f.stem.replace("-", " ").title()),
                "date": (date_m.group(1).strip() if date_m else ""),
                "summary": summary,
            }
        )
    return posts


def _page(title: str, body: str) -> HTMLResponse:
    page = (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">"
        f"<title>{title}</title><style>{_BLOG_CSS}</style></head>"
        f"<body><div class=\"page\">{body}</div></body></html>"
    )
    return HTMLResponse(page, headers={"Cache-Control": "no-store, must-revalidate"})


@router.get("/blog", response_class=HTMLResponse)
def blog_index() -> HTMLResponse:
    posts = _load_posts()
    if not posts:
        cards = "<div class='card'><p>Pehla article jald hi aayega!</p></div>"
    else:
        cards = "\n".join(
            "<div class='card'><h2><a href='/blog/{slug}'>{title}</a></h2>"
            "<div class='date'>{date}</div><p>{summary}</p>"
            "<a class='read' href='/blog/{slug}'>Padhiye &rarr;</a></div>".format(
                slug=p["slug"], title=p["title"], date=p["date"], summary=p["summary"]
            )
            for p in posts
        )
    body = f"{_BACK_LINK}<h1>⚖️ LegalWithDev Blog</h1><div class='date'>Kanoon, aapki bhasha me — simple guides by Dev</div>{cards}"
    return _page("Blog — LegalWithDev", body)


@router.get("/blog/{slug}", response_class=HTMLResponse)
def blog_post(slug: str) -> HTMLResponse:
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        return _page("404", "<h1>404</h1><p><a href='/blog'>Wapas blog par jayein</a></p>")
    path = BLOG_DIR / f"{slug}.md"
    if not path.exists():
        return _page("Article nahi mila", "<h1>Article nahi mila</h1><p><a href='/blog'>Wapas blog par jayein</a></p>")
    text = path.read_text(encoding="utf-8")
    title_m = re.search(r"^#\s+(.+)$", text, re.M)
    date_m = re.search(r"^date:\s*(.+)$", text, re.M)
    title = title_m.group(1).strip() if title_m else slug.title()
    date = date_m.group(1).strip() if date_m else ""
    body = f"<a class='top' href='/blog'>&larr; Sab articles</a><h1>{title}</h1><div class='date'>{date} · LegalWithDev</div>" + _md_to_html(text)
    return _page(f"{title} — LegalWithDev Blog", body)
