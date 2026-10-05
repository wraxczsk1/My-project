import io

import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(
        {"TESTING": True, "DATABASE": str(tmp_path / "test.sqlite"), "SEED_LSPD": False}
    )
    return app.test_client()


def make_table(client, name="hraci"):
    return client.post(
        "/tables/new",
        data={
            "name": name,
            "col_name": ["jmeno", "vek", "skore", "narozen", "aktivni"],
            "col_type": ["TEXT", "INTEGER", "REAL", "DATE", "BOOLEAN"],
        },
    )


def test_create_table_and_crud(client):
    assert make_table(client).status_code == 302
    r = client.post(
        "/t/hraci/add",
        data={"jmeno": "Petr", "vek": "21", "skore": "3,5", "narozen": "2003-04-01", "aktivni": "1"},
    )
    assert r.status_code == 302
    page = client.get("/t/hraci").get_data(as_text=True)
    assert "Petr" in page and "3.5" in page and "Ano" in page

    client.post("/t/hraci/1/edit", data={"jmeno": "Pavel", "vek": "22"})
    page = client.get("/t/hraci").get_data(as_text=True)
    assert "Pavel" in page and "Petr" not in page

    client.post("/t/hraci/1/delete")
    assert "Pavel" not in client.get("/t/hraci").get_data(as_text=True)


def test_validation_errors(client):
    make_table(client)
    r = client.post("/t/hraci/add", data={"jmeno": "X", "vek": "abc"})
    assert r.status_code == 400
    assert "není celé číslo" in r.get_data(as_text=True)


def test_rejects_bad_identifiers(client):
    r = client.post(
        "/tables/new",
        data={"name": 'x"; DROP TABLE y; --', "col_name": ["a"], "col_type": ["TEXT"]},
    )
    assert r.status_code == 400
    r = client.post("/tables/new", data={"name": "t", "col_name": ["a"], "col_type": ["EVIL"]})
    assert r.status_code == 400


def test_search_sort_and_pagination(client):
    make_table(client)
    for i in range(30):
        client.post("/t/hraci/add", data={"jmeno": f"hrac{i}", "vek": str(i)})
    page = client.get("/t/hraci?q=hrac2").get_data(as_text=True)
    assert "hrac2<" in page and "hrac25" in page and "hrac3<" not in page
    page = client.get("/t/hraci?sort=vek&dir=desc").get_data(as_text=True)
    assert page.index("hrac29") < page.index("hrac28")
    assert "Strana 1 / 2" in page


def test_add_column_and_drop_table(client):
    make_table(client)
    client.post("/t/hraci/columns", data={"col_name": ["tym"], "col_type": ["TEXT"]})
    assert "tym" in client.get("/t/hraci").get_data(as_text=True)
    client.post("/t/hraci/delete")
    assert client.get("/t/hraci").status_code == 404


def test_csv_export_import(client):
    make_table(client)
    data = "jmeno,vek,neznamy\nAnna,30,x\nBob,nan,y\n".encode()
    client.post(
        "/t/hraci/import",
        data={"file": (io.BytesIO(data), "data.csv")},
        content_type="multipart/form-data",
    )
    csv_text = client.get("/t/hraci/export.csv").get_data(as_text=True)
    assert "Anna" in csv_text and "Bob" not in csv_text


def test_sql_console_is_read_only(client):
    make_table(client)
    client.post("/t/hraci/add", data={"jmeno": "Eva"})
    page = client.post("/sql", data={"query": "SELECT jmeno FROM hraci"}).get_data(as_text=True)
    assert "Eva" in page
    page = client.post("/sql", data={"query": "DELETE FROM hraci"}).get_data(as_text=True)
    assert "readonly" in page
    assert "Eva" in client.get("/t/hraci").get_data(as_text=True)


@pytest.fixture
def lspd(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "lspd.sqlite")})
    return app.test_client()


def test_lspd_seed_and_pages(lspd):
    page = lspd.get("/").get_data(as_text=True)
    assert "Ve službě" in page and "Sarah Connor" in page
    page = lspd.get("/vycvik").get_data(as_text=True)
    assert "Základy služby" in page and "Kriminalistika" in page
    page = lspd.get("/vycvik/3").get_data(as_text=True)
    assert "Felony stop" in page and "Poučení před interakcí" in page
    assert lspd.get("/t/vycviky").get_data(as_text=True).count("Základy služby") >= 9


def test_ref_columns_show_labels_and_validate(lspd):
    page = lspd.get("/t/dustojnici?q=Sergeant").get_data(as_text=True)
    assert "John Miller" in page and "Jakub Novák" not in page
    r = lspd.post("/t/sluzby/add", data={"dustojnik": "999", "zacatek": "2026-10-05T10:00"})
    assert r.status_code == 400 and "Neplatný odkaz" in r.get_data(as_text=True)
    page = lspd.get("/t/absolvovane_vycviky/add?dustojnik=3&vycvik=5").get_data(as_text=True)
    assert '<option value="3" selected>' in page


def test_duty_start_and_end(lspd):
    lspd.post("/sluzba/start", data={"dustojnik": "1", "unit": "1-ADAM-01"})
    page = lspd.get("/").get_data(as_text=True)
    assert "1-ADAM-01" in page
    r = lspd.post("/sluzba/start", data={"dustojnik": "1"}, follow_redirects=True)
    assert "už je ve službě" in r.get_data(as_text=True)
    lspd.post("/sluzba/2/end")
    lspd.post("/sluzba/1/end")
    assert "Nikdo není ve službě" in lspd.get("/").get_data(as_text=True)


def test_cannot_drop_referenced_table(lspd):
    r = lspd.post("/t/dustojnici/delete", follow_redirects=True)
    assert "nelze smazat" in r.get_data(as_text=True)
    assert lspd.get("/t/dustojnici").status_code == 200


def test_add_ref_column(lspd):
    lspd.post("/t/sluzby/columns", data={"col_name": ["vozidlo_ridic"], "col_type": ["REF:dustojnici"]})
    page = lspd.get("/t/sluzby").get_data(as_text=True)
    assert "→ dustojnici" in page


def test_manual_page_and_png_export(lspd):
    import io
    import zipfile

    page = lspd.get("/manual").get_data(as_text=True)
    assert "LSPD MANUAL" in page and "Máte právo nevypovídat" in page
    r = lspd.get("/manual/1.png?download=1")
    assert r.mimetype == "image/png" and r.data[:4] == b"\x89PNG"
    assert "01-zaklady-sluzby.png" in r.headers["Content-Disposition"]
    assert lspd.get("/manual/obsah.png").data[:4] == b"\x89PNG"
    assert lspd.get("/manual/999.png").status_code == 404
    archive = zipfile.ZipFile(io.BytesIO(lspd.get("/manual/lspd-manual.zip").data))
    assert len(archive.namelist()) == 8 and "07-kriminalistika.png" in archive.namelist()
