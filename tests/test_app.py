import io

import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.sqlite")})
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
