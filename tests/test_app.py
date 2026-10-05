import io
import zipfile

import pytest

from app import create_app
from manual_content import MANUAL
from manual_png import CODE_COLORS, image_path, module_pages, parse


@pytest.fixture()
def client():
    return create_app().test_client()


def test_index_lists_categories(client):
    page = client.get("/").get_data(as_text=True)
    assert "LSPD MANUAL" in page
    for c in MANUAL:
        assert c["nazev"] in page


def test_category_and_module_pages(client):
    page = client.get("/k/zaklady-sluzby").get_data(as_text=True)
    assert "Miranda" in page and "Kódy" in page
    page = client.get("/k/zaklady-sluzby/miranda").get_data(as_text=True)
    assert "Máte právo nevypovídat." in page
    assert "/png/zaklady-sluzby/miranda/1.png" in page
    assert client.get("/k/neexistuje").status_code == 404
    assert client.get("/k/zaklady-sluzby/neexistuje").status_code == 404


def test_module_shows_images_and_video(client):
    page = client.get("/k/dopravni-postupy/felony-stop").get_data(as_text=True)
    assert "/obrazky/felony-stop.png" in page
    page = client.get("/k/dopravni-postupy/radar").get_data(as_text=True)
    assert "medal.tv" in page


def test_module_png(client):
    r = client.get("/png/zaklady-sluzby/miranda/1.png?download=1")
    assert r.mimetype == "image/png" and r.data[:4] == b"\x89PNG"
    assert "attachment" in r.headers["Content-Disposition"]
    assert "02-miranda.png" in r.headers["Content-Disposition"]
    assert client.get("/png/zaklady-sluzby/miranda/99.png").status_code == 404
    assert client.get("/png/obsah.png").data[:4] == b"\x89PNG"


def test_long_module_is_split_into_pages():
    assert len(module_pages(0, 0)) > 1


def test_zip_contains_every_page(client):
    archive = zipfile.ZipFile(io.BytesIO(client.get("/lspd-manual.zip").data))
    names = archive.namelist()
    expected = 1 + sum(len(module_pages(ci, mi)) for ci, c in enumerate(MANUAL) for mi in range(len(c["moduly"])))
    assert len(names) == expected
    assert "00-obsah.png" in names
    assert "07-kriminalistika/04-pouceni-pred-interakci.png" in names


def test_content_is_valid():
    slugs = set()
    for c in MANUAL:
        assert c["slug"] not in slugs
        slugs.add(c["slug"])
        mods = [m["slug"] for m in c["moduly"]]
        assert len(mods) == len(set(mods))
        for m in c["moduly"]:
            assert parse(m["text"])
            for name in m["obrazky"]:
                assert image_path(name), name


def test_parse_markup():
    blocks = parse("# Nadpis\n- bod\n! pozor\n> vzor\n10-4 | Rozumím | oznameni\nX | Y\ntext")
    assert [b["type"] for b in blocks] == ["heading", "bullet", "warn", "quote", "codes", "para"]
    assert [r["kind"] for r in blocks[4]["rows"]] == ["oznameni", "info"]
    assert "info" not in CODE_COLORS


def test_static_build(tmp_path):
    from freeze import build

    out = build(tmp_path / "dist")
    home = (out / "index.html").read_text(encoding="utf-8")
    assert 'href="/k/zaklady-sluzby/index.html"' in home
    assert (out / "k/zaklady-sluzby/kody/index.html").exists()
    assert (out / "png/zaklady-sluzby/kody/1.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert (out / "lspd-manual.zip").exists()
    assert (out / "static/style.css").exists()
