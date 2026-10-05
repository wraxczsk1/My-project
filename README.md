# MiniDB

Jednoduchá webová databázová aplikace (Flask + SQLite).

## Funkce

- vytváření tabulek s vlastními sloupci (text, celé číslo, desetinné číslo, datum, ano/ne)
- přidávání, úprava a mazání záznamů s validací typů
- fulltextové hledání přes všechny sloupce, řazení kliknutím na hlavičku, stránkování
- přidání sloupce do existující tabulky, smazání tabulky
- import a export CSV
- SQL konzole pouze pro čtení (`SELECT` dotazy)

## Spuštění

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app app run --debug
```

Aplikace poběží na http://127.0.0.1:5000. Data se ukládají do `instance/database.sqlite`
(cestu lze změnit proměnnou prostředí `DATABASE_PATH`).

## Testy

```bash
pip install -r requirements-dev.txt
pytest
```
