HODNOSTI = [
    ("Cadet", "CDT"), ("Officer I", "PO-I"), ("Officer II", "PO-II"),
    ("Officer III", "PO-III"), ("Senior Lead Officer", "SLO"),
    ("Sergeant I", "SGT-I"), ("Sergeant II", "SGT-II"),
    ("Lieutenant I", "LT-I"), ("Lieutenant II", "LT-II"), ("Captain", "CPT"),
    ("Commander", "CMDR"), ("Deputy Chief", "DC"), ("Assistant Chief", "AC"),
    ("Chief of Police", "COP"),
]

# (název, ikona, barva, [(modul, studijní text – jeden bod na řádek)])
MANUAL = [
    ("Základy služby", "📘", "#2563eb", [
        ("Kódy", "10-4 – rozumím / potvrzuji\n10-6 – zaneprázdněn, nevolat\n10-7 – mimo službu, 10-8 – ve službě a dostupný\n10-9 – zopakuj zprávu, 10-20 – moje poloha\n10-23 – jsem na místě, 10-97 – jsem na cestě\nCode 1 bez majáků, Code 2 jen světla, Code 3 světla i siréna"),
        ("Miranda", "Čte se při zadržení, nejpozději před výslechem.\n„Máte právo nevypovídat. Cokoli řeknete, může a bude použito proti vám u soudu.“\n„Máte právo na advokáta. Pokud si ho nemůžete dovolit, bude vám přidělen.“\n„Rozumíte svým právům?“ – odpověď si vždy nech potvrdit\nBez přečtení Mirandy nelze výpověď použít"),
        ("Etický kodex", "Jednej profesionálně, slušně a nestranně ke všem občanům\nNezneužívej pravomoc ani služební výbavu pro osobní účely\nNepřijímej úplatky ani dary za výkon služby\nChraň život a zdraví – i podezřelého\nChyby kolegů hlas nadřízenému, nekryj je"),
        ("Povinná výbava", "Služební zbraň + 2 zásobníky, taser, obušek\nPouta, svítilna, vysílačka\nOdznak a služební průkaz\nLékárnička (MB) a reflexní vesta\nVýbavu kontroluj před každým nástupem do služby"),
        ("Vstup do kanceláře", "Před vstupem zaklepej a počkej na vyzvání\nPozdrav a představ se: hodnost, jméno, volačka\nMluv věcně a stručně, poslouchej nadřízeného\nOdejdi až po ukončení rozhovoru, zavři za sebou"),
        ("Oprávnění úřední osoby", "Požadovat prokázání totožnosti\nVydat výzvu a vyžadovat její splnění\nZastavit a prohledat vozidlo při důvodném podezření\nZadržet osobu podezřelou z trestného činu\nKaždý zásah musí být přiměřený a zdokumentovaný"),
        ("Donucovací prostředky", "Postup: výzva → hmaty a chvaty → taser / obušek → zbraň\nVždy volíš nejmírnější prostředek, který stačí\nPřed použitím dej výzvu, pokud to situace dovolí\nPo použití zajisti první pomoc a vše zapiš do MDT"),
        ("Odtah vozidel", "Odtah při překážce provozu, nehodě nebo zabavení\nVozidlo prohlédni a zdokumentuj stav (foto)\nNahlas odtah na dispečink se SPZ a lokací\nZapiš důvod odtahu do MDT"),
        ("Hodnosti a volačky", "Cadet → Officer I–III → SLO → Sergeant → Lieutenant → Captain → Commander → Chief\nNadřízeného oslovuj hodností a příjmením\nVolačka = oddělení-jednotka-číslo (např. 1-ADAM-12)\nADAM = dvoučlenná hlídka, LINCOLN = jeden důstojník"),
    ]),
    ("Radiová komunikace", "📻", "#d97706", [
        ("Frekvence", "Hlavní frekvence – běžná komunikace a dispečink\nTaktická frekvence – zásahy a pronásledování\nVelitelská frekvence – jen pro Sergeant+\nPři změně frekvence to vždy nahlas"),
        ("Základní hlášení", "Formát: KDO volá → KOMU → CO → KDE\nPř.: „1-ADAM-12 dispečinku, 10-23 na Legion Square, traffic stop, černý Sultan.“\nMluv krátce a jasně, nepřerušuj ostatní\nPrioritu má vždy 10-13"),
        ("Zkratky ulic", "Používej oficiální názvy ulic a jejich zkratky\nHlášení lokace: ulice + nejbližší křižovatka nebo budova\nMRPD = Mission Row Police Department\nPostal kódy na mapě pro rychlé určení místa"),
    ]),
    ("Zdravověda", "🚑", "#dc2626", [
        ("CPR", "Zkontroluj bezpečí, reakci a dýchání\nVolej EMS a začni masáž\n30 stlačení : 2 vdechy, tempo 100–120/min\nHloubka stlačení 5–6 cm, střed hrudníku\nPokračuj do příjezdu EMS"),
        ("Střelné a bodné poranění", "Zajisti místo, teprve pak ošetřuj\nZastav krvácení přímým tlakem\nU končetin použij turniket nad ranou, zapiš čas\nPředmět v ráně nevytahuj, zafixuj ho\nVolej EMS a sleduj vědomí"),
        ("Zlomeniny", "S postiženou končetinou nehýbej\nZafixuj ji v poloze, ve které je\nOtevřenou zlomeninu kryj sterilním obvazem\nPodezření na páteř – nehýbej s osobou, volej EMS"),
        ("Obsah MB", "Obvazy, gázy a tlakový obvaz\nTurniket a nůžky\nRukavice a resuscitační rouška\nDlahy a izotermická fólie\nObsah doplň po každém použití"),
        ("10-50", "10-50 = dopravní nehoda\nZajisti místo nehody (výstražná světla, kužely)\nZjisti počet zraněných a nahlas ho dispečinku\nPřivolej EMS, případně odtah\nZapiš svědky a sepiš záznam"),
        ("A-B-C-D-E", "A – Airway: průchodnost dýchacích cest\nB – Breathing: dýchání\nC – Circulation: krvácení a oběh\nD – Disability: vědomí a neurologie\nE – Exposure: celková prohlídka těla"),
    ]),
    ("Dopravní postupy", "🚓", "#0891b2", [
        ("Traffic stop", "Nahlas dispečinku: lokaci, SPZ, model a barvu vozu\nZastav za vozidlem, trochu vyosený doleva\nPřistup ze strany řidiče, ruku měj u pasu\nPozdrav, představ se, uveď důvod zastavení\nVyžádej doklady: řidičák, technický průkaz, pojištění"),
        ("Felony stop", "Pro vozidla s nebezpečnými nebo ozbrojenými osobami\nMinimálně 2 hlídky, vozy za podezřelým\nKryj se za dveřmi, zbraň připravená\nOsoby vyvolávej po jedné hlasovými povely\nRuce nahoře, couvej ke mně, klekni"),
        ("Box manévr", "Uzavření vozidla ze 3–4 stran\nPouze nízká rychlost nebo stojící vozidlo\nPotřebuje koordinaci na rádiu\nPo zastavení postupuj jako při felony stop"),
        ("PIT manévr", "Jen se souhlasem nadřízeného\nMax. rychlost dle pravidel serveru (obvykle do 100 km/h)\nNe v hustém provozu, na mostech a u chodců\nNárazník k zadnímu kolu, plynule zatoč"),
        ("Radar", "Měř z bezpečně zaparkovaného vozidla\nZapiš naměřenou rychlost a limit\nPokutu odstupňuj podle překročení\nPři vysokém překročení zvaž zabavení ŘP"),
    ]),
    ("Evidence a MDT", "💻", "#7c3aed", [
        ("MDT zapisování", "Každý zásah zapiš do MDT ještě v průběhu služby\nUveď: datum, čas, lokaci, zúčastněné osoby\nPopiš průběh věcně a chronologicky\nPřilož důkazy, fotky a čísla případů"),
        ("Registrace zbraně", "Ověř sériové číslo v databázi\nZkontroluj zbrojní průkaz majitele\nNeregistrovanou zbraň zabav a zapiš\nZapiš typ, ráži a sériové číslo"),
        ("Zjištění identity", "Vyžádej si doklad totožnosti\nOvěř osobu v MDT (jméno, datum narození)\nZkontroluj pátrání a záznamy\nOdmítnutí prokázat se je důvod k předvedení"),
        ("CPZ postup", "CPZ = cela předběžného zadržení\nOsobu prohledej a zabav nebezpečné věci\nZapiš čas umístění a důvod\nPravidelně kontroluj stav zadrženého"),
        ("Mugshot", "Fotka zepředu a z profilu\nTabulka se jménem, datem a číslem případu\nPřilož fotky k záznamu v MDT"),
        ("Large dispatch", "Velké události: přestřelky, loupeže, pronásledování\nVelení přebírá nejvyšší hodnost na místě\nJednotky se hlásí po přidělení úkolu\nNeblokuj rádio zbytečnými hlášeními"),
    ]),
    ("Taktika a zásah", "🎯", "#ea580c", [
        ("10-13", "10-13 = důstojník v ohrožení, potřebuje okamžitou pomoc\nVšechny volné jednotky jedou Code 3\nUveď lokaci, jinak co nejdřív\nMá absolutní prioritu na rádiu"),
        ("Užití síly", "Síla musí být nutná, přiměřená a okamžitě ukončená\nSmrtící síla jen při přímém ohrožení života\nVaruj před použitím, pokud je to možné\nKaždé užití síly zapiš a nahlas nadřízenému"),
        ("10-68", "10-68 = loupež / přepadení\nPřijíždí se bez sirény v posledním úseku\nNejprve perimetr, pak vyjednávání\nNevstupuj sám, čekej na posily"),
        ("Perimetr", "Vnitřní perimetr: uzavření místa činu\nVnější perimetr: odklon dopravy a civilistů\nKaždá jednotka hlásí svou pozici\nNikdo nevstoupí bez povolení velitele"),
    ]),
    ("Kriminalistika", "🔍", "#16a34a", [
        ("Klíčová slova", "Důvodné podezření – konkrétní fakta pro zastavení\nPravděpodobná příčina – důvod pro zatčení nebo prohlídku\nZadržení ≠ zatčení\nDůkazní řetězec – chain of custody"),
        ("Základní odbory", "Patrol – hlídková služba\nTraffic – dopravní policie\nDetective Bureau – vyšetřování\nSWAT / Metro – speciální zásahy\nAir Support a K9"),
        ("Poučení před interakcí", "Představ se a uveď důvod kontroly\nZachovej klid a bezpečnou vzdálenost\nVysvětli osobě její práva a povinnosti\nKomunikuj zdvořile i při nespolupráci"),
    ]),
]

SCHEMA = [
    'CREATE TABLE "hodnosti" (id INTEGER PRIMARY KEY AUTOINCREMENT, '
    '"nazev" TEXT, "zkratka" TEXT, "poradi" INTEGER)',
    'CREATE TABLE "kategorie" (id INTEGER PRIMARY KEY AUTOINCREMENT, '
    '"nazev" TEXT, "poradi" INTEGER, "ikona" TEXT, "barva" TEXT)',
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
    for poradi, (kategorie, ikona, barva, moduly) in enumerate(MANUAL, start=1):
        kat_id = db.execute(
            'INSERT INTO "kategorie" ("nazev", "poradi", "ikona", "barva") '
            "VALUES (?, ?, ?, ?)",
            (kategorie, poradi, ikona, barva),
        ).lastrowid
        db.executemany(
            'INSERT INTO "vycviky" ("nazev", "kategorie", "povinny", "popis") '
            "VALUES (?, ?, 1, ?)",
            [(m, kat_id, popis) for m, popis in moduly],
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
