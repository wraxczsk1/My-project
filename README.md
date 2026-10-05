# LSPD MANUAL

Výukový manuál pro kadety LSPD (FiveM). Flask aplikace se 7 barevnými kategoriemi a 36 moduly; každý modul se dá stáhnout jako PNG pro Discord.

## Spuštění

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/flask --app app run
```

Otevři http://127.0.0.1:5000.

## Úprava učiva

Veškeré texty jsou v `manual_content.py`, obrázky v `static/manual/`. Formát textu modulu:

```
# Nadpis              barevný štítek sekce
- bod                 odrážka
! text                červené upozornění
> text                příklad / vzor hlášení
10-4 | Rozumím | oznameni   řádek tabulky kódů (status, oznameni, dispatch, emergency, prikaz, info)
[legenda]             barevná legenda typů kódů
jiný text             odstavec
```

Dlouhé moduly se v PNG automaticky rozdělí na více stran (1/2, 2/2…).

## Export

- `/png/obsah.png` – obsah celého manuálu
- `/png/<kategorie>/<modul>/<strana>.png` – PNG modulu (`?download=1` pro stažení)
- `/lspd-manual.zip` – všechna PNG roztříděná do složek podle kategorií

## Testy

```bash
.venv/bin/pytest -q
```
