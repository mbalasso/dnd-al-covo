import os
import re
import yaml
from pathlib import Path

MARKER = re.compile(r"<!-- TIMELINE(?::([A-Z]+))? -->")
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
ARCS = {"ABF", "SVW", "BLR"}
ROOT = "sessioni"


def _arcs(meta):
    a = meta.get("arc") or []
    return [a] if isinstance(a, str) else list(a)


def _collect(files):
    out = []
    for f in files.documentation_pages():
        p = Path(f.src_uri)
        if p.parts[0] != ROOT or p.name == "index.md":
            continue

        text = Path(f.abs_src_path).read_text(encoding="utf-8")
        m = FRONTMATTER.match(text)
        meta = yaml.safe_load(m.group(1)) if m else {}

        title = next(
            (l[2:].strip() for l in text.splitlines() if l.startswith("# ")),
            p.stem,
        )

        unknown = set(_arcs(meta)) - ARCS
        if unknown:
            raise ValueError(f"{f.src_uri}: invalid arc {unknown}")

        out.append({
            "order": str(meta.get("real_date", "")),
            "session": meta.get("session", p.stem),
            "game_date": meta.get("game_date") or "—",
            "arcs": _arcs(meta),
            "title": title,
            "uri": f.src_uri,
            "folder": str(p.parent),
        })

    return sorted(out, key=lambda r: r["order"])


def _table(rows, page_uri, show_arc):
    if not rows:
        return "*Nessuna sessione ancora pubblicata.*"

    header = ["Sessione", "Data reale", "Data in gioco"]
    if show_arc:
        header.append("Arco")
    header.append("Titolo")

    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    base = os.path.dirname(page_uri)

    for r in rows:
        rel = os.path.relpath(r["uri"], base).replace(os.sep, "/")
        cells = [f"**{r['session']}**", r["order"] or "—", r["game_date"]]
        if show_arc:
            cells.append(" · ".join(r["arcs"]) or "—")
        cells.append(f"[{r['title']}]({rel})")
        out.append("| " + " | ".join(cells) + " |")

    return "\n".join(out)


def on_page_markdown(markdown, page, config, files, **kwargs):
    if not MARKER.search(markdown):
        return markdown

    all_rows = _collect(files)
    uri = page.file.src_uri
    folder = str(Path(uri).parent)

    def replace(m):
        arc = m.group(1)
        if arc:
            rows = [r for r in all_rows if arc in r["arcs"]]
        else:
            rows = [r for r in all_rows if r["folder"] == folder]
        return _table(rows, uri, show_arc=not arc)

    return MARKER.sub(replace, markdown)
