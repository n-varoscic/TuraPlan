# 01 – Zasnova rešitve

## Ime rešitve

**TuraPlan** – spletna aplikacija za planiranje dostavnih tur, preverjanje kapacitete vozil in vodenje dostav.

## Namen rešitve in problem

Rešitev je namenjena distribucijskemu podjetju, ki z lastnimi kombiji in tovornjaki dostavlja blago poslovnim strankam – pekarnam, slaščičarnam, trgovinam in gostinskim obratom. Dostavlja predvsem živila (moka, sir, mleko, semena, nadevi) in opremo (podstavki, embalaža).

Ročno planiranje dostav (Excel, papir, telefon) predstavlja naslednje težave:

- **preobremenjena vozila** – šele pri nakladanju se ugotovi, da je presežena dovoljena nosilnost,
- **neugoden vrstni red postankov** – disponent naredi napako pri določanju vrstnega reda dostave, zato vozniki delajo nepotrebne kilometre,
- **ni povratne informacije** – disponent ne more sproti spremljati katera naročila so bila dostavljena in katera še ne.

TuraPlan omogoča, da disponent sestavi turo za posamezno vozilo, sistem sproti preveri, ali naročila po teži in številu palet gredo v vozilo, disponent določi vrstni red postankov in dopiše opombe, turo potrdi in voznik dobi pregleden seznam. Voznik med vožnjo označuje, katera naročila je dostavil, nedostavljena pa se samodejno vrnejo disponentu v ponovno planiranje. Disponent ima vpogled v aktivno turo in lahko sproti spremlja napredek dostave.

## Ciljni uporabniki

| Uporabnik | Kdo je | V kakšni situaciji uporablja rešitev |
|---|---|---|
| **Disponent** | zaposleni v logistiki, ki pripravlja dostave | Vnaprej pripravi ture za naslednje dni: razporedi prejeta naročila na vozila (pri tem si pomaga s pregledom naročil po regijah), preveri kapaciteto, določi vrstni red, dopiše opombe in ture potrdi. |
| **Voznik** | voznik kombija ali tovornjaka | Na dan odpreme pogleda svojo turo, med vožnjo na telefonu označuje dostavljena in nedostavljena naročila. |
| **Administrator (vodja logistike)** | odgovorna oseba za logistiko | Upravlja uporabnike, vozila (nosilnost, paletna mesta) in nastavitve. |

## Kratek opis delovanja

Tipičen potek:

1. **Naročila** – TuraPlan prevzame prejeta naročila strank iz ERP sistema podjetja (v projektu jih nadomestijo testni podatki). Vsako naročilo ima datum prejema, rok odpreme, težo (kg) in število palet. Število palet določi skladišče, ki blago pripravi.
2. **Sestavljanje ture** – disponent ustvari turo z datumom odpreme (danes ali vnaprej), izbere vozilo in voznika ter vanjo doda nerazporejena naročila. Sistem sproti prikazuje zasedenost vozila (kg in palete) in opozori, če je kapaciteta presežena ali če bi naročilo odšlo po roku odpreme.
3. **Vrstni red in opombe** – disponent razvrsti postanke in dopiše opombe za voznika. (Kasneje: sistem predlaga vrstni red glede na razdalje, tura je prikazana na zemljevidu.)
4. **Potrditev** – disponent turo potrdi. Sistem potrditev dovoli samo, če ima tura vozilo, voznika, vsaj en postanek in kapaciteta ni presežena. Potrjena tura je zaklenjena za urejanje.
5. **Tura pri vozniku** – potrjena tura se prikaže vozniku v aplikaciji (na telefonu): vrstni red postankov, stranka, naslov, telefon, palete, teža in opombe. Tiskanje ni potrebno.
6. **Izvedba** – voznik na dan odpreme turo začne in za vsak postanek označi `DOSTAVLJENO` ali `NI DOSTAVLJENO` (z obveznim razlogom). Tura lahko traja tudi več dni (oddaljene stranke). Disponent v aplikaciji sproti vidi, kateri postanki so že dostavljeni. Ko so označeni vsi postanki, se tura samodejno zaključi.
7. **Ponovno planiranje** – nedostavljena naročila se vrnejo na seznam nerazporejenih naročil, disponent pa jih uvrsti v novo turo.

## Ključni pojmi

| Pojem | Pomen v tej rešitvi |
|---|---|
| Stranka | poslovni kupec z naslovom dostave (in koordinatami za zemljevid) |
| Naročilo | blago za eno stranko; ima datum prejema, rok odpreme, težo (kg) in število palet |
| Regija | območje dostave stranke (npr. »Štajerska«, »Nemčija – Bavarska«), po katerem disponent združuje naročila za isto vozilo |
| Rok odpreme | najkasnejši dan, ko mora blago oditi iz skladišča |
| Paletno mesto | prostor za eno EUR paleto (1,2 × 0,8 m) v vozilu; kombi ima npr. 4 paletna mesta, tovornjak 16 |
| Palete naročila | koliko paletnih mest zasede naročilo, na 0,25 natančno (npr. 0,25 = četrt palete). Podatek poda skladišče: manjša naročila lahko združi na skupno paleto, zato zasedejo le del palete. |
| Vozilo | kombi ali tovornjak z največjo nosilnostjo (kg) in številom paletnih mest |
| Tura | ena vožnja enega vozila z enim voznikom, ki se začne na datum odpreme in je sestavljena iz postankov |
| Postanek | eno naročilo v turi, z zaporedno številko, opombo za voznika in rezultatom dostave |
| Kapaciteta presežena | vsota teže naročil v turi je večja od nosilnosti vozila **ali** vsota potrebnih palet je večja od števila paletnih mest |
