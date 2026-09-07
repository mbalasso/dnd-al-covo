import re

H1 = re.compile(r"^#\s+.+$", re.M)


def on_page_markdown(markdown, page, config, files, **kwargs):
    game_date = page.meta.get("game_date")
    if not game_date:
        return markdown

    subtitle = f'<p class="session-date">{game_date}</p>'

    return H1.sub(lambda m: m.group(0) + "\n\n" + subtitle, markdown, count=1)
