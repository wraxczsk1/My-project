# LSPD MANUAL

Databázová aplikace pro výcvik LSPD (FiveM) postavená na Flask + SQLite.

## Funkce

- **Nástěnka**: počet důstojníků, kadetů, kdo je právě ve službě (nástup / ukončení služby jedním klikem), poslední výcviky
- **Výcvik**: přehled všech důstojníků a jejich splněných modulů podle kategorií LSPD Manualu
  (Základy služby, Radiová komunikace, Zdravověda, Dopravní postupy, Evidence a MDT, Taktika a zásah, Kriminalistika)
- **Karta důstojníka**: seznam modulů se stavem, datem, body a instruktorem, tlačítko „Zapsat“ u nesplněných
- tabulky `dustojnici`, `hodnosti`, `kategorie`, `vycviky`, `absolvovane_vycviky`, `sluzby` – vše lze upravovat
- obecný databázový editor: vlastní tabulky a sloupce (text, číslo, datum, datum a čas, ano/ne, odkaz na jinou tabulku),
  hledání, řazení, stránkování, import/export CSV, SQL konzole pouze pro čtení

Při prvním spuštění se databáze naplní hodnostmi, kategoriemi a moduly výcviku a třemi ukázkovými důstojníky
(ty můžeš smazat).

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
