"""Obsah LSPD MANUALu.

Formát textu modulu (jeden řádek = jeden prvek):
  # Nadpis           barevný štítek sekce
  - bod              odrážka
  ! text             červené upozornění
  > text             příklad / vzor hlášení
  KÓD | význam | typ tabulka kódů (typ: status, oznameni, dispatch, emergency, prikaz, info)
  [legenda]          barevná legenda typů kódů
  jiný text          odstavec
"""
import re
import unicodedata


def slugify(text):
    ascii_text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-") or "modul"


def modul(nazev, text, obrazky=(), video=None):
    return {"slug": slugify(nazev), "nazev": nazev, "text": text.strip(),
            "obrazky": list(obrazky), "video": video}


def kategorie(nazev, ikona, barva, moduly):
    return {"slug": slugify(nazev), "nazev": nazev, "ikona": ikona, "barva": barva, "moduly": moduly}


KODY = """
[legenda]
# 10-kódy (10-0 až 10-29)
10-0 | Vizuální kontakt ztracen | oznameni
10-1 | Změna frekvence | prikaz
10-2 | Negativní | oznameni
10-3 | Ticho na vysílači | prikaz
10-4 | Rozumím | oznameni
10-5 | Přestávka | status
10-6 | Zaneprázdněný | status
10-7 | Mimo službu | status
10-8 | Ve službě | status
10-9 | Opakujte hlášení | prikaz
10-10 | Napadení | emergency
10-11 | Traffic stop | oznameni
10-12 | Samostatná jízda | oznameni
10-13 | Střelba | dispatch
10-14 | Prodej drog | dispatch
10-15 | Převoz zadrženého (kam) | oznameni
10-16 | Krádež vozidla | dispatch
10-17 | Podezřelá osoba | dispatch
10-18 | Vloupání | dispatch
10-20 | Lokace | oznameni
10-21 | Výzva k nahlášení lokace | prikaz
10-22 | Ignorujte hlášení | prikaz
10-23 | Příchod na scénu | oznameni
10-24 | Odchod ze scény | oznameni
10-26 | Podezřelá činnost | dispatch
10-27 | Kontrola DL | oznameni
10-28 | Kontrola SPZ | oznameni
10-29 | Kontrola osoby, zda je hledaná | prikaz
# 10-kódy (10-30 až 10-100)
10-30 | Hledaná osoba | oznameni
10-31 | Osoba není hledaná | oznameni
10-32 | Je potřeba asistence (počet) | emergency
10-35 | Odchod všech jednotek ze scény | prikaz
10-38 | Příjezd na EMS (kam) | oznameni
10-41 | Zahájení patroly | status
10-42 | Ukončení patroly | status
10-43 | Podání informací | prikaz
10-44 | Smrt osoby / potřebuji koronera | oznameni
10-48 | Požár | dispatch
10-49 | Sebevrah | dispatch
10-50 | Dopravní nehoda | dispatch
10-51 | Potřebuji odtah | prikaz
10-52 | Potřebuji záchranku | prikaz
10-53 | Potřebuji hasiče | prikaz
10-60 | Ozbrojen střelnou zbraní | dispatch
10-61 | Ozbrojen chladnou zbraní | dispatch
10-62 | Únos | dispatch
10-66 | Bezohledný řidič | dispatch
10-68 | Ozbrojená loupež | dispatch
10-70 | Pěší nahánění | emergency
10-71 | Žádám supervisora na scénu | prikaz
10-80 | Ujíždění hlídce | emergency
10-90 | Napomenutí | prikaz
10-95 | Suspect zajištěn | oznameni
10-97 | Na cestě (kód) | oznameni
10-98 | Pokračuji v patrole | oznameni
10-99 | Jednotka v nouzi | emergency
10-100 | Jednotka v bezvědomí | emergency
# CODE
CODE 0 | Pád hry | info
CODE 1 | Bez majáků / bez sirén | info
CODE 2 | S majáky / bez sirén | info
CODE 3 | S majáky / se sirénou | info
CODE 4 | Situace pod kontrolou | info
CODE 5 | Felony stop | info
CODE 6 | Zahájení vyšetřování | info
CODE 11 | Potřeba zásahové jednotky | info
CODE 12 | Falešný poplach | info
CODE 500 | Hromadná nehoda / zranění | info
CODE 1000 | Pád letadla | info
# SIGNAL
SIGNAL 11 | Měření rychlosti radarem | info
SIGNAL 60 | Zátah – drogy | info
SIGNAL 100 | Zastavení dopravy | info
# Doplňky
ETA | Odhadovaný čas příjezdu | info
Stand By | Zůstaňte na místě | info
Hold Fire | Zastavit palbu | info
"""

MANUAL = [
    kategorie("Základy služby", "📘", "#2563eb", [
        modul("Kódy", KODY),
        modul("Miranda", """
# Kdy se Miranda čte
- Osobě starší 21 let ji při zatčení číst nemusíš, ale musíš se zeptat, zda svá práva zná
- Pokud práva nezná, musíš mu je sdělit
- Práva sděl před výslechem a oznam, že výpověď se nahrává (aby šla použít u soudu)
# Miranda Rights
> Máte právo nevypovídat.
> Vše, co řeknete, může být použito proti vám.
> Máte právo na advokáta. Pokud si jej nemůžete dovolit, bude vám přidělen.
> Máte právo na 2minutový hovor monitorovaný sborem LSPD.
> Máte právo na lékařské ošetření, jídlo a pití.
> Rozuměl jste svým právům?
! Osoba musí odpovědět, že právům rozumí. Když nerozumí, sdělíš je až 3×. Po třetím pokusu už nemusíš.
"""),
        modul("Etický kodex", """
# Poslání
- Zvyšovat bezpečnost a snižovat kriminalitu
- Řešit komunitní problémy, které ovlivňují bezpečnost
# Základní hodnoty
- Profesionalita · Nestrannost · Zodpovědnost
- Ohleduplnost · Bezúhonnost
# Závazky vůči společnosti
- Chránit práva a svobodu občanů
- Prosazovat kalifornské zákony a ústavu
- Chovat se na úrovni a neporušovat zákony
- Zachovávat mlčenlivost o informacích
- Nepřijímat ve službě dary ani úplatky
- Udržovat bezpečnost a pořádek
- Usilovat o důvěru veřejnosti
- Minimalizovat sílu, upřednostnit de-eskalaci
- Rovné zacházení bez diskriminace
"""),
        modul("Povinná výbava", """
# Osobní výbava
- Glock 17, taser, obušek / teleskop
- Baterka, služební pouta, kapesní nůž, rukavice
- MDT, vysílačka, BodyCam
- Služební odznak
# Výbava vozidla
- Pumpovací brokovnice + 12 Gauge, Bean Bag + náboje
- Pepřák a anti-pepřák, rádio
- Adrenalin, Narcan, neprůstřelné vesty, evidenční sáčky
- Ruční radar, kužely, dopravní značky, zábrany
- Plynové masky, potápěčský oblek, riot štít
- Pouta, botičky na kolo, fotoaparát, zápisník
- Hrotový pás, tint meter, elektronický náramek
""", obrazky=["vybava-vozidla-1.png", "vybava-vozidla-2.png"]),
        modul("Vstup do kanceláře", """
# Při předvolání
- Zaklepeš a čekáš na povolení ke vstupu
- Představíš se: oslovení, hodnost, jméno, žádost
> „Dobrý den, pane kapitáne, Police Officer III Peter Simpson, dostavil jsem se na vaše předvolání.“
# Odchod
> „Pane kapitáne, dovolte mi odejít.“
# Bez předvolání
- Postup je stejný, liší se jen žádost
> „Dobrý den, pane kapitáne, Police Officer III Peter Simpson, dovolte mi promluvit.“
# Ve více lidech
- Mluví nejvyšší hodnost, při stejné hodnosti ten, kdo vstoupí první
> „…Police Officer III Peter Simpson a další (počet), dovolte mi promluvit.“
"""),
        modul("Oprávnění úřední osoby", """
# Vstup do objektu
- Kde probíhají ilegální hazardní hry osob mladších 21 let
- Kde je podezření na protiprávní jednání
- Na soukromý pozemek, kde dochází k trestné činnosti
# Zadržení osoby
- Která se dopouští protiprávního jednání
- Která ohrožuje život svůj nebo ostatních
# Donucovací prostředky
- K ochraně osob, majetku a veřejného pořádku
- Když osoba neuposlechne výzvu nebo se brání zadržení
# Smrtící síla
- K ochraně života svého nebo jiné osoby
- Když osoba ohrožuje životy ostatních
# Unmarked vozidlo
- Detektivové při vyšetřování, zásahové jednotky
# Majáky
- Úkol od dispečera, převoz nebezpečné osoby do CPZ / věznice
- Řešení přestupku / TČ, jízda nad povolenou rychlost
# Zastavení a prohlídka vozidla
- Pátrání po pachateli / vozidle z trestného činu
- Důvodné podezření, že vozidlem byl spáchán TČ
- Pátrání po hledaných nebo pohřešovaných osobách
- Ve voze mohou být zbraně, výbušniny nebo drogy
"""),
        modul("Donucovací prostředky", """
# Typy
- Hmaty, chvaty, údery a kopy
- Obušek, úder střelnou zbraní
- Vytlačení vozidlem, služební pes (K-9)
- Hrozba namířenou zbraní, varovný výstřel
- Taser, služební pouta
- Zastavovací pás, zablokování cesty
# Zásady
! Taser nikdy na osobu mokrou od tekutiny – hrozí usmrcení
- Před taserem 3× vyzvi: „Taser, taser, taser!“
- Psovod K-9 odpovídá za svého psa
- Varovný výstřel jen s kontrolou okolí, ve městě jen v nouzi
"""),
        modul("Odtah vozidel", """
# Doba odtahu
- Jakékoliv porušení → odtah na 1 den
! Střelba po LEO → odtah na 7 dní
"""),
        modul("Hodnosti a volací znaky", """
# Vedení
Staff-1 | Chief of Police | info
Staff-2 | Assistant Chief of Police | info
Staff-3 | Deputy Chief of Police | info
Staff-4 | Commander | info
# Velitelé a officeři
Nora | Captain | info
Henry | Lieutenant | info
John | Sergeant / Sergeant II | info
Lincoln | Police Officers | info
"""),
    ]),
    kategorie("Radiová komunikace", "📻", "#d97706", [
        modul("Frekvence", """
Vysílačkou se policisté a další složky domlouvají stručně a rychle na dálku.
# Frekvence
1 | LSPD, LSSD, SAHP | info
1.5 | Akademie | info
2 | EMS | info
3 | FD | info
5 | CID | info
6 | SWAT | info
# Pravidla
- Větu vždy začni svým volacím znakem
- Nedělej zbytečný hluk, mluv profesionálně a používej kódy
- Hlášení podávej z bezpečného místa
- Mluv jen když je to důležité, nech pauzy mezi vysíláním
- Respektuj hierarchii
"""),
        modul("Základní hlášení", """
# Služba
Začátek | Volačka CheckIn 10-8 | status
Konec | Volačka CheckOut 10-7 | status
Přestávka | Volačka krátká 10-5 (důvod) | status
Frekvence | Volačka 10-1 2 | prikaz
Rádio off | Volačka radio off (důvod) | info
Respond | Volačka responding last 10-68 code 2 | oznameni
# Volání kolegy
> „Lincoln 20 na Lincoln 30, příjem?“
- Po odpovědi řekni věc stručně, ať nezatěžuješ frekvenci
# Patrola s kolegou
> „Lincoln 1, Adam check.“
> „Lincoln 1 na Adam 1, příjem?“ (když se nikdo neozve, pokračuj)
> „Lincoln 1 a Lincoln 20 nyní jako Adam 1, Adam 1 10-41.“
! Vždy jako první říkáš vyšší hodnost
"""),
        modul("Zkratky ulic", """
# Zkratky
Rd | Road | info
Ave | Avenue | info
St | Street | info
Hwy | Highway | info
Fwy | Freeway | info
Dr | Drive | info
Blvd | Boulevard | info
Ln | Lane | info
Pl | Place | info
Pkwy | Parkway | info
# Další
ETA | Estimated time of arrival – čas příjezdu | info
"""),
    ]),
    kategorie("Zdravověda", "🚑", "#dc2626", [
        modul("KPR", """
Kardiopulmonální resuscitace – oddálení klinické smrti.
# Postup
- Odhal hrudník postiženého
- Ruce na střed hrudní kosti (spojnice bradavek)
- Stlačuj do 1/3 hloubky = 5–6 cm
- Tempo 100–120 / min (2× za sekundu)
- Propnuté paže, prsty propletené, kývej celým tělem
- Při únavě se zachránci rychle vystřídají
"""),
        modul("Střelné a bodné poranění", """
! Předmět v ráně NIKDY nevytahuj – funguje jako zátka. Kulku vytahuje lékař.
# Krk
- Okamžitě ucpi ránu (1–2 prsty / sterilní polštářky)
# Končetina
- Turniket 5–15 cm nad ránou, zapiš čas (max 6 h)
- Vydezinfikuj okolí rány
- Sterilní krytí a obvaz (až 3 vrstvy)
# Břicho a hrudník
- Vydezinfikuj okolí, přelep chestsealem
- Při prosakování 2. chestseal / sterilní krytí
! Na hrudník NE tlakový obvaz
"""),
        modul("Zlomeniny", """
! S osobou zbytečně nemanipuluj
# Uzavřená
- Fixační / vakuová dlaha
- Krční límec
- Transport na EMS
# Otevřená
- Nejdřív zastav masivní krvácení (turniket 15–20 cm nad ránou)
- Dál jako uzavřená zlomenina
"""),
        modul("Obsah MB", """
# Dýchání a měření
Ambuvak | 1 ks | info
Stetoskop | 1 ks | info
Oxymetr | 1 ks | info
Glukoměr | 1 ks | info
Teploměr | 1 ks | info
Tonometr | 1 ks | info
# Krvácení a obvazy
Škrtidlo | 2 ks | info
Kompresní obvaz | 6 ks | info
Elastický obvaz | 6 ks | info
Klasický obvaz | 6 ks | info
Trojcípý šátek | 2 ks | info
Tamponky | 10 ks | info
Sterilní čtverec | 10 ks | info
Náplasti | 20 ks | info
Bollinovy chlopně | 4 ks | info
# Fixace a ostatní
Krční límec | 2 ks | info
Tvarovatelná dlaha | 2 ks | info
Vakuová dlaha | 2 ks | info
Izotermická fólie | 2 ks | info
Rukavice | 20 párů | info
Desinfekce | 1 ks | info
Lepicí páska | 1 ks | info
Blok a psací potřeby | 1 ks | info
Nástroje | nůžky, pean, pinzeta, Magillovy kleště | info
"""),
        modul("10-50", """
# Příjezd
- Zastav opodál na Code 2
- Po výstupu nahlas nehodu na vysílačku
- Zkontroluj, zda je někdo ve voze
# Ve voze jsou osoby
- Nasaď rukavice, zjisti stav, nabídni EMS
- První pomoc, zajištění místa, odklon dopravy
- Nafoť místo, zapiš do evidence, zajisti odtah
! Zaklíněná osoba → vždy volej LSFD
# Vůz je prázdný
- Vyhledej majitele a po dohodě zajisti odtah
- Vozidlo můžeš vždy prohledat
"""),
        modul("A-B-C-D-E", """
# A – Airway
- Zprůchodni dýchací cesty, zkontroluj ústa
# B – Breathing
- Kontrola dechu: pohled na hrudník, poslech u úst
# C – Circulation
- Tep na zápěstí nebo krku
# D – Disability
- Reakce, zorničky, reakce na hlas a bolest
# E – Exposure
- Odhal pacienta podle typu poranění
""", obrazky=["abcde.png"]),
    ]),
    kategorie("Dopravní postupy", "🚓", "#0891b2", [
        modul("Traffic stop", """
Zastavení vozidla a dočasné zadržení řidiče kvůli přestupku nebo TČ.
- Zaparkuj za vozidlem, nech Code 2
# Hlášení (jen když chceš 10-32)
> „Adam 1, máme tu 10-11, 10-20 EMS, žluté BMW, 3 osoby se šátky přes obličej, vyžaduji 10-32.“
# Postup
- Vyžádej ID, řidičák a doklady od vozidla
- Přestupek sděl až po kontrole dokladů
- Řidič: vypnutý motor, nevystupuje, netelefonuje
- Doklady kontroluj ve svém voze (pravost, fotka, majitel)
- U pokuty se zeptej, zda s ní souhlasí
- Pokuta se platí do 3 pracovních dnů
- Vrať doklady, po vypnutí majáků může jet
""", obrazky=["traffic-stop.png"]),
        modul("Felony stop", """
Felony stop = CODE 5. Nejčastěji u ujíždějícího vozidla.
# Velení
- Kdo zahlásí CODE 5, je velitel – jeho vůz stojí uprostřed
- Velí po celou dobu a určuje směr přístupu k vozidlu
- Začíná se vždy u řidiče, osoby vystupují po jednom
! Jednotky čekají na příkaz velitele. Postupuje se jen z jedné strany – žádný crossfire!
# Povely
- Vypněte motor a vyhoďte klíčky z okna
- Obě ruce z okna, otevřete dveře zvenčí
- Pomalu vystupte, 2 kroky od vozidla
- Pomalu se otočte o 360°
- Couvejte za mým hlasem
- Metr před vozem: klekněte, ruce za hlavu
- Je ve voze ještě další osoba?
! Když vidíš zbraň, nikdy nepřikazuj, ať ji vezme a odhodí
""", obrazky=["felony-stop.png"]),
        modul("Box manévr", """
Zablokování vozidla ze všech stran, nejčastěji po PIT manévru.
- Cíl: suspect nesmí znovu ujet
- Vozidlo zablokuj jemným ťuknutím v co nejnižší rychlosti
! Když vozidlo stojí a hlásíš box, je zakázané silné ramování
""", obrazky=["box-block.png"]),
        modul("PIT manévr", """
Pursuit Immobilization Technique – náraz do zadní nápravy, vůz dostane smyk. Obvykle následuje box.
# Podmínky
- Pronásledování trvá déle než 8–10 minut
- Neobydlená oblast
- Rychlost max. 80–100 km/h
- Schválení vyšší hodností
# Žádost
> „Adam 2, máme 10-80 přes 10 minut, Grand Senora Freeway směr Paleto Bay, 100 km/h, osoba extrémně nebezpečná, žádám o povolení PIT.“
""", obrazky=["pit-manevr.png"]),
        modul("Radar", """
- Měř ruční nebo vozidlový radar z bezpečně zaparkovaného vozu
- Měření hlas jako SIGNAL 11
- Postup je ukázaný ve videu
""", video="https://medal.tv/games/gta-v/clips/m0NcXWcFkxxWORHLO?invite=cr-MSw0dnAsMTQ5Mzg0OTQ3&v=107"),
    ]),
    kategorie("Evidence a MDT", "💻", "#7c3aed", [
        modul("MDT zapisování", """
MDT (Mobile Data Terminal) je hlavní databáze pro práci v terénu.
# Sekce
Profily | Osoby, licence, vozidla, tresty | info
Vozidla | Hledání podle SPZ | info
Zbraně | Registrované zbraně a sériová čísla | info
Cases | Veškerá dokumentace | info
# Booking (zatčení)
- Eskorta do CPZ, kontrola ID, otisky
- Mugshot tabletem a nahrání do profilu
- Nelegální věci do MDT přes Open Stash
- Přečti práva (§825 PC); nesouhlas s trestem → DOJ do 24 h
# Kam co zapsat
Cases | Incident report (střelba, ujíždění) – do 24 h | emergency
Reports | Traffic stop, oznámení bez arrestu | oznameni
Warrant | Zatykač – jen se souhlasem soudu | prikaz
BOLO | Pátrání po osobě / vozidle | dispatch
- Incident report: jméno, datum, LEO, popis, status
- CPZ report propoj s incident reportem přes ID
- Do názvu pátrání napiš jasně „BOLO“
"""),
        modul("Registrace zbraně", """
# Vyžádej si
- ID (Identification Card) a WL (Weapon Licence)
# Podmínky
- Trestní bezúhonnost, vlastní WL, věk 21+
# Nelze registrovat
- Krátkou i dlouhou automatickou zbraň
- Zbraň s nelegální úpravou (drum, tlumič)
- Použitou zbraň
# Před registrací
- Zkontroluj, že zbraň není nabitá
- Ověř fotku osoby v MDT, když chybí, doplň ji
"""),
        modul("Zjištění identity", """
# Doklad totožnosti
- ID karta, řidičák, zbrojní průkaz, cestovní pas
- Na místě prohledej osobu, zda nemá doklad u sebe
- Doklad obsahuje jméno, fotografii a datum narození
# Otisky prstů
- Daktyloskopie: sken otisku a digitalizace
- Starší metoda: daktyloskopický inkoust a karta
# Rozpoznání obličeje
- Fotka obličeje a hledání v databázi (Face Recognition)
- Osoby od 16 let jsou v databázi občanů SA
# Mugshot / foto evidence
- Hledání v databázi podle údajů od pachatele
- Porovnání s fotkou v profilu MDT a v archivu
""", obrazky=["zjisteni-identity.png"]),
        modul("CPZ postup", """
# Kdy do CPZ
- Spáchání trestného činu
- Osoba ohrožuje sebe nebo okolí
- Zajištění pro další úkony (výslech, převoz, soud)
# Postup
- Pouč osobu o důvodu zadržení a o jejích právech
- Důkladná prohlídka, odeber zbraně, drogy a ostré věci
- Věci uschovej a zaeviduj
- Umísti do cely, sděl orientační dobu zadržení
- Zjisti totožnost, pátrání, záznamy a licence
- Sepiš protokol a připrav podklady (soud / propuštění / převoz)
# Dohoda o vině a trestu
> Podle oddílu 688.1 a kap. 7.5 California Penal Code (AB No. 1): Osoba XXX nar. XXX souhlasí s trestem odnětí svobody na X let a pokutou XXX USD za XXX. Podpis: (jméno)
"""),
        modul("Mugshot", """
- Vyfoť suspecta zepředu tabletem
- Fotku nahraj do jeho profilu v MDT
- Postup je ukázaný ve videu
""", video="https://medal.tv/games/gta-v/clips/m1DytionY_5WQ2Jtj?invite=cr-MSwwUWgsMzkxMDQyMTgy&v=118"),
        modul("Large dispatch", """
- Zelená šipka = poloha kolegů. V zeleném rámečku vidíš, kdo je na místě
- Červený rámeček = nastavení dispatche (status a volačka)
- Červeno-bílé značky = nahlášená nelegální činnost
# Nastavení dispatche
- Status, automatické mazání oznámení (1–60 min)
- Callsign, přidělené vozidlo, ztlumení zvuků
""", obrazky=["dispatch-mapa.png", "dispatch-nastaveni.png"]),
    ]),
    kategorie("Taktika a zásah", "🎯", "#ea580c", [
        modul("10-13", """
10-13 = hlášení o střelbě. Vždy nebezpečný call – jedou jednotky s vestami a těžšími zbraněmi.
! Cadet nereaguje, pokud není přímo zavolán na podporu
# Hlášení
> „(volací znak) responding na 10-13.“
- Po příjezdu hned nahlas stav situace
# Co nahlásit
- Počet suspectů
- Počet ohrožených civilistů
- Vozidla pro únik v okolí
"""),
        modul("Užití síly", """
# Úvod
- Na prvním místě je lidský život
- Přednost má čas, odstup a komunikace
- Síla musí být přiměřená, nadměrná je protiprávní
- Smrtící síla jen k záchraně životů
# Zásady
- Přiměřenost: síla odpovídá hrozbě
- Objektivita: bez ohledu na rasu, víru, pohlaví, věk
! Po každém zranění je povinná první pomoc
# De-eskalace
- Klidný projev, odstup, čas, komunikace
- Nekřič a zbytečně netas zbraň
> „Budete prohledán.“ · „Jste zadržen.“
# Druhy síly
Smrtící | Zbraň, vozidlo – smrt / vážné zranění | emergency
Nesmrtící | Taser, obušek, sprej, flashbang, bean bag – fyzická agrese | prikaz
Mírná | Hmaty, chvaty, pouta – nespolupráce | status
Žádná | Příkazy a výzvy – osoba spolupracuje | oznameni
"""),
        modul("10-68", """
Velmi nebezpečné, často dojde k přestřelce. Hlavní priorita: všichni rukojmí přežijí.
- Obvykle se nejdřív slovně vyjednává
- Rychle uzavři silnice a evakuuj okolí
- Zjisti počet suspectů a ohrožených civilistů
# Air unit
- Hlídá střechy a celé okolí
# Police Officers
- Uzavřou silnice služebními vozy, u každé zůstane jeden officer
- Ostatní se kryjí za vozem a hlásí jen krátké, důležité informace
# Specializované jednotky
- S vyjednávačem přebírají velení
- Připraví vstup, používají smoke a flashbang
# Vyjednávač
- Získává informace a předává je velitelům
- Rozhoduje o nejlepším postupu k záchraně rukojmí
"""),
        modul("Perimetr", """
Vymezený prostor kolem zásahu, do kterého nesmí nepovolané osoby.
# Postup
- Urči hranice podle rozsahu události
- Uzavři prostor: pásky, bariéry, vozidla
- Hlídky na vstupech, pouštěj jen oprávněné
- Udržuj spojení s velitelem a dalšími složkami
# Proč
- Chrání důkazy, zasahující i veřejnost
# Ve hře
> /perimetr do OOC chatu
- Postal 0 = střed na tvé pozici
- Velikost 60–100, trvání 10–30 min
"""),
    ]),
    kategorie("Kriminalistika", "🔍", "#16a34a", [
        modul("Klíčová slova", """
Kriminalistika chrání občany vyhledáváním a zkoumáním stop a důkazů.
# Pojmy
Kriminalita | Souhrn trestných činů za určité období | info
Odhalování | Hledání skryté a organizované trestné činnosti | info
Objasňování | Motiv, doba činu, pachatel | info
Vyšetřování | Procesní úkony a důkazy podle trestního řádu | info
Prevence | Předcházení kriminalitě | info
# Kriminologie zkoumá
- Stav, strukturu a vývoj kriminality, její příčiny
- Pachatele a oběť
# 7 kriminalistických otázek
Kdo? | Pachatel, spolupachatel, poškozený | info
Co? | TČ, nehoda, sebevražda, přirozená smrt | info
Kdy? | Co nejpřesnější čas | info
Kde? | Přesné místo události | info
Jak? | Způsob a průběh | info
Čím? | Nástroje a jejich použití | info
Proč? | Motiv, okruh podezřelých | info
"""),
        modul("Základní odbory", """
# Odbory
Daktyloskopie | Identita podle otisků prstů | info
Antropologie | Kosti, lebky a chrup | info
Trasologie | Stopy bot a pneumatik | info
Balistika | Identifikace zbraně podle projektilu | info
Chemie | Jedy a jiné látky | info
Medicína | Čas a příčina smrti nebo zranění | info
Psychologie | Psychologie podezřelých | info
Genetika | Identifikace z DNA | info
"""),
        modul("Poučení před interakcí", """
Před každým úkonem musíš osobu informovat a poučit.
# Kdy poučit
- Před osobní prohlídkou a prohlídkou vozidla
- Před zadržením osoby a vypsáním faktury
- Před zabavením věcí / dokladů a odtahem vozidla
- Před převozem do věznice a dalšími úkony
# Příklady
> „Právě vám bude vypsána faktura.“
> „Právě vám bude prohledáno vozidlo.“
> „Právě budete prohledán.“
> „Právě jste omezen na osobní svobodě.“
""", obrazky=["pouceni-pred-interakci.png"]),
    ]),
]
