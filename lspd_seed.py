HODNOSTI = [
    ("Cadet", "CDT"), ("Officer I", "PO-I"), ("Officer II", "PO-II"),
    ("Officer III", "PO-III"), ("Senior Lead Officer", "SLO"),
    ("Sergeant I", "SGT-I"), ("Sergeant II", "SGT-II"),
    ("Lieutenant I", "LT-I"), ("Lieutenant II", "LT-II"), ("Captain", "CPT"),
    ("Commander", "CMDR"), ("Deputy Chief", "DC"), ("Assistant Chief", "AC"),
    ("Chief of Police", "COP"),
]

MANUAL = {
    "Základy služby": [
        "Kódy", "Miranda", "Etický kodex", "Povinná výbava",
        "Vstup do kanceláře", "Oprávnění úřední osoby",
        "Donucovací prostředky", "Odtah vozidel", "Hodnosti a volačky",
    ],
    "Radiová komunikace": ["Frekvence", "Základní hlášení", "Zkratky ulic"],
    "Zdravověda": [
        "CPR", "Střelné a bodné poranění", "Zlomeniny", "Obsah MB",
        "10-50", "A-B-C-D-E",
    ],
    "Dopravní postupy": [
        "Traffic stop", "Felony stop", "Box manévr", "PIT manévr", "Radar",
    ],
    "Evidence a MDT": [
        "MDT zapisování", "Registrace zbraně", "Zjištění identity",
        "CPZ postup", "Mugshot", "Large dispatch",
    ],
    "Taktika a zásah": ["10-13", "Užití síly", "10-68", "Perimetr"],
    "Kriminalistika": [
        "Klíčová slova", "Základní odbory", "Poučení před interakcí",
    ],
}

SCHEMA = [
    'CREATE TABLE "hodnosti" (id INTEGER PRIMARY KEY AUTOINCREMENT, '
    '"nazev" TEXT, "zkratka" TEXT, "poradi" INTEGER)',
    'CREATE TABLE "kategorie" (id INTEGER PRIMARY KEY AUTOINCREMENT, '
    '"nazev" TEXT, "poradi" INTEGER)',
    'CREATE TABLE "vycviky" (id INTEGER PRIMARY KEY AUTOINCREMENT, "nazev" TEXT, '
    '"kategorie" INTEGER REFERENCES "kategorie"(id) ON DELETE SET NULL, '
    '"povinny" BOOLEAN, "popis" TEXT)',
    'CREATE TABLE "dustojnici" (id INTEGER PRIMARY KEY AUTOINCREMENT, "jmeno" TEXT, '
    '"volacka" TEXT, "hodnost" INTEGER REFERENCES "hodnosti"(id) ON DELETE SET NULL, '
    '"oddeleni" TEXT, "stav" TEXT, "nastup" DATE)',
    'CREATE TABLE "absolvovane_vycviky" (id INTEGER PRIMARY KEY AUTOINCREMENT, '
    '"dustojnik" INTEGER REFERENCES "dustojnici"(id) ON DELETE SET NULL, '
    '"vycvik" INTEGER REFERENCES "vycviky"(id) ON DELETE SET NULL, '
    '"instruktor" INTEGER REFERENCES "dustojnici"(id) ON DELETE SET NULL, '
    '"datum" DATE, "body" INTEGER, "splneno" BOOLEAN, "poznamka" TEXT)',
    'CREATE TABLE "sluzby" (id INTEGER PRIMARY KEY AUTOINCREMENT, '
    '"dustojnik" INTEGER REFERENCES "dustojnici"(id) ON DELETE SET NULL, '
    '"zacatek" DATETIME, "konec" DATETIME, "unit" TEXT, '
    '"partner" INTEGER REFERENCES "dustojnici"(id) ON DELETE SET NULL, '
    '"poznamka" TEXT)',
]

DEMO_DUSTOJNICI = [
    ("John Miller", "1-ADAM-01", "Sergeant I", "Výcvik", "Aktivní", "2026-01-10"),
    ("Sarah Connor", "1-ADAM-12", "Officer II", "Hlídková služba", "Aktivní", "2026-03-02"),
    ("Jakub Novák", "1-ADAM-31", "Cadet", "Akademie", "Ve výcviku", "2026-09-20"),
]


def seed_lspd(db, demo=True):
    for sql in SCHEMA:
        db.execute(sql)
    db.executemany(
        'INSERT INTO "hodnosti" ("nazev", "zkratka", "poradi") VALUES (?, ?, ?)',
        [(n, z, i) for i, (n, z) in enumerate(HODNOSTI, start=1)],
    )
    for poradi, (kategorie, moduly) in enumerate(MANUAL.items(), start=1):
        kat_id = db.execute(
            'INSERT INTO "kategorie" ("nazev", "poradi") VALUES (?, ?)',
            (kategorie, poradi),
        ).lastrowid
        db.executemany(
            'INSERT INTO "vycviky" ("nazev", "kategorie", "povinny") VALUES (?, ?, 1)',
            [(m, kat_id) for m in moduly],
        )
    if demo:
        for jmeno, volacka, hodnost, oddeleni, stav, nastup in DEMO_DUSTOJNICI:
            db.execute(
                'INSERT INTO "dustojnici" ("jmeno", "volacka", "hodnost", "oddeleni", '
                '"stav", "nastup") VALUES (?, ?, (SELECT id FROM "hodnosti" '
                'WHERE "nazev" = ?), ?, ?, ?)',
                (jmeno, volacka, hodnost, oddeleni, stav, nastup),
            )
        db.execute(
            'INSERT INTO "absolvovane_vycviky" ("dustojnik", "vycvik", "instruktor", '
            '"datum", "body", "splneno") SELECT 3, id, 1, \'2026-09-25\', 90, 1 '
            'FROM "vycviky" WHERE "kategorie" = 1 AND id <= 4'
        )
        db.execute(
            'INSERT INTO "absolvovane_vycviky" ("dustojnik", "vycvik", "instruktor", '
            '"datum", "body", "splneno") SELECT 2, id, 1, \'2026-04-01\', 95, 1 '
            'FROM "vycviky"'
        )
        db.execute(
            'INSERT INTO "sluzby" ("dustojnik", "zacatek", "unit", "partner") '
            "VALUES (2, '2026-10-05 18:00', '1-ADAM-12', 3)"
        )
    db.commit()
