import re
from datetime import date

H1 = re.compile(r"^#\s+.+$", re.M)


def _arcs(meta):
    a = meta.get("arc") or []
    return [a] if isinstance(a, str) else list(a)


def on_page_markdown(markdown, page, config, files, **kwargs):
    meta = page.meta
    parts = []

    game_date = meta.get("game_date")
    if game_date:
        parts.append(str(game_date))

    real_date = meta.get("real_date")
    if isinstance(real_date, date):
        parts.append(f"sessione del {real_date.strftime('%d/%m/%Y')}")
    elif real_date:
        parts.append(f"sessione del {real_date}")

    arcs = _arcs(meta)
    if arcs:
        parts.append("Party " + ", ".join(arcs))

    if not parts:
        return markdown

    subtitle = f'<p class="session-date">{" · ".join(parts)}</p>'
    return H1.sub(lambda m: m.group(0) + "\n\n" + subtitle, markdown, count=1)
