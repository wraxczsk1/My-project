"""Build a static copy of LSPD MANUAL into ./dist for public hosting."""
import re
import shutil
import sys
from pathlib import Path

from app import app
from manual_content import MANUAL
from manual_png import module_pages

PAGE_LINK = re.compile(r'href="(/k/[^"?#]+)"')


def page_urls():
    yield "/"
    for ci, c in enumerate(MANUAL):
        yield f"/k/{c['slug']}"
        for mi, m in enumerate(c["moduly"]):
            yield f"/k/{c['slug']}/{m['slug']}"


def file_urls():
    yield "/png/obsah.png"
    yield "/lspd-manual.zip"
    for c in MANUAL:
        for m in c["moduly"]:
            for name in m["obrazky"]:
                yield f"/obrazky/{name}"
    for ci, c in enumerate(MANUAL):
        for mi, m in enumerate(c["moduly"]):
            for page in range(1, len(module_pages(ci, mi)) + 1):
                yield f"/png/{c['slug']}/{m['slug']}/{page}.png"


def build(out):
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(Path(app.root_path) / "static", out / "static")
    app.config["STATIC_BUILD"] = True
    client = app.test_client()
    for url in page_urls():
        resp = client.get(url)
        assert resp.status_code == 200, url
        html = PAGE_LINK.sub(r'href="\1/index.html"', resp.get_data(as_text=True))
        target = out / url.lstrip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
    for url in file_urls():
        resp = client.get(url)
        assert resp.status_code == 200, url
        target = out / url.lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(resp.data)
    return out


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else "dist"))
