import copy
import io

import pytest
from PIL import Image

import manual_store as store
from app import create_app
from manual_content import MANUAL

OWNER = "kudelka.zdenek0@gmail.com"


@pytest.fixture()
def app(tmp_path):
    original = copy.deepcopy(MANUAL)
    app = create_app({"DATA_DIR": str(tmp_path), "TESTING": True})
    yield app
    MANUAL[:] = original
    store.save()


def login(client, email=OWNER):
    with client.session_transaction() as s:
        s["fto"] = email
        s["csrf"] = "t"


def test_fto_hidden_for_public(app):
    client = app.test_client()
    page = client.get("/").get_data(as_text=True)
    assert "FTO MANAGE" not in page
    assert client.get("/fto/").status_code == 302
    assert client.get("/fto/login").status_code == 503
    login(client, "cizi@gmail.com")
    assert client.get("/fto/").status_code == 302


def test_password_login(monkeypatch, tmp_path):
    monkeypatch.setenv("FTO_PASSWORD", "LSPD 921830")
    app = create_app({"DATA_DIR": str(tmp_path), "TESTING": True})
    client = app.test_client()
    with client.session_transaction() as s:
        s["csrf"] = "t"
    response = client.post("/fto/login", data={"csrf": "t", "password": "wrong"})
    assert response.status_code == 200
    assert "Nesprávné heslo" in response.get_data(as_text=True)
    response = client.post("/fto/login", data={"csrf": "t", "password": "LSPD 921830"})
    assert response.status_code == 302
    assert response.location.endswith("/fto/")


def test_owner_sees_button_and_dashboard(app):
    client = app.test_client()
    login(client)
    assert "FTO MANAGE" in client.get("/").get_data(as_text=True)
    page = client.get("/fto/").get_data(as_text=True)
    assert "Správa výcviku" in page and "Základy služby" in page


def test_post_requires_csrf(app):
    client = app.test_client()
    login(client)
    assert client.post("/fto/kurz/novy", data={"nazev": "X"}).status_code == 400


def test_course_and_lesson_crud(app, tmp_path):
    client = app.test_client()
    login(client)
    count = len(MANUAL)
    client.post("/fto/kurz/novy", data={"csrf": "t", "nazev": "Pátrání", "ikona": "pouta", "barva": "#123456"})
    assert len(MANUAL) == count + 1 and MANUAL[-1]["slug"] == "patrani"
    ci = count
    img = io.BytesIO()
    Image.new("RGB", (40, 30), "red").save(img, "PNG")
    img.seek(0)
    client.post(f"/fto/kurz/{ci}/lekce/nova", content_type="multipart/form-data", data={
        "csrf": "t", "nazev": "BOLO", "text": "# Co je BOLO\n- Pátrání po osobě\n10-30 | Hledaná osoba | oznameni",
        "obrazky": (img, "foto.png"),
    })
    lesson = MANUAL[ci]["moduly"][0]
    assert lesson["slug"] == "bolo" and len(lesson["obrazky"]) == 1
    page = client.get("/k/patrani/bolo").get_data(as_text=True)
    assert "Pátrání po osobě" in page
    assert client.get(f"/obrazky/{lesson['obrazky'][0]}").status_code == 200
    assert client.get("/png/patrani/bolo/1.png").data[:4] == b"\x89PNG"
    assert (tmp_path / "manual.json").exists()

    client.post(f"/fto/kurz/{ci}/nahoru", data={"csrf": "t"})
    assert MANUAL[ci - 1]["slug"] == "patrani"
    client.post(f"/fto/kurz/{ci - 1}/lekce/0/smazat", data={"csrf": "t"})
    assert MANUAL[ci - 1]["moduly"] == []
    client.post(f"/fto/kurz/{ci - 1}/smazat", data={"csrf": "t"})
    assert len(MANUAL) == count and client.get("/k/patrani").status_code == 404


def test_email_access_management_is_removed(app):
    client = app.test_client()
    login(client)
    assert client.get("/fto/").get_data(as_text=True).find("Přístup do FTO MANAGE") == -1
    assert client.post("/fto/pristup", data={"csrf": "t", "pridat": "Kolega@Gmail.com"}).status_code == 404
