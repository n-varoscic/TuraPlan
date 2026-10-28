# 02 – Funkcionalnosti in obseg

## Uporabniške vloge

Vsak uporabnik ima natanko eno vlogo.

### Disponent

**Lahko:**

- pregleda naročila (nerazporejena, planirana, nedostavljena), razvrščena po roku odpreme,
- ustvari turo z datumom odpreme ter ji dodeli vozilo in voznika,
- dodaja naročila v turo in jih odstranjuje iz nje, dokler je tura v osnutku,
- določi vrstni red postankov in dopiše opombe za voznika,
- potrdi turo ali jo vrne v osnutek (dokler je voznik še ni začel),
- spremlja napredek tur v izvedbi (kateri postanki so dostavljeni, kateri ne in zakaj),
- poišče naročilo po številki naročila ali nazivu stranke.

**Nima pravic:**

- spreminjati ture, ki je v dostavi ali zaključena,
- označevati dostav namesto voznika,
- urejati vozil, uporabnikov in nastavitev,
- vnašati ali spreminjati naročil in strank (prihajajo iz ERP sistema podjetja).

### Voznik

**Lahko:**

- vidi seznam svojih potrjenih tur,
- odpre podrobnosti svoje ture (vrstni red, naslovi, telefoni, palete, teža, opombe),
- turo začne (najprej na datum odpreme),
- za vsak postanek označi `DOSTAVLJENO` ali `NI DOSTAVLJENO` z razlogom.

**Nima pravic:**

- videti tur drugih voznikov ali tur v osnutku,
- spreminjati vrstnega reda postankov, naročil ali opomb,
- spreminjati oznake postanka, ko je tura zaključena.

### Administrator (vodja logistike)

**Lahko:**

- ustvari uporabnika, mu dodeli vlogo ali ga deaktivira,
- dodaja in ureja vozila (registrska številka, tip, nosilnost, število paletnih mest) in jih deaktivira,
- enkrat ob vzpostavitvi sistema nastavi lokacijo skladišča (začetna točka tur) prek Django Admina,
- pregleduje vse ture in naročila (samo branje).

**Nima pravic:**

- sestavljati, potrjevati ali spreminjati tur (to je naloga disponenta),
- označevati dostav,
- brisati zaključenih tur in naročil (zgodovina se ohranja).

## Predvidene funkcionalnosti

Oznaka **MVP** pomeni, da je funkcionalnost del prve delujoče različice.

| Oznaka | Funkcionalnost | Vloga | MVP |
|---|---|---|---|
| F-01 | Prijava v sistem in dostop glede na vlogo | vse | **MVP** |
| F-02 | Seznam tur s statusom, zasedenostjo vozila in napredkom dostav | Disponent | **MVP** |
| F-03 | Sestavljanje ture: datum odpreme, vozilo, voznik in dodajanje nerazporejenih naročil | Disponent | **MVP** |
| F-04 | Sprotno preverjanje kapacitete vozila po teži in paletnih mestih | Disponent | **MVP** |
| F-05 | Ročno razvrščanje postankov in opombe za voznika | Disponent | **MVP** |
| F-06 | Potrditev ture s preverjanjem pogojev in zaklepanjem ture | Disponent | **MVP** |
| F-07 | Izvedba ture na telefonu: pregled postankov, začetek ture in označevanje dostav | Voznik | **MVP** |
| F-08 | Iskanje naročila po številki naročila ali nazivu stranke s prikazom statusa in ture, v kateri je naročilo | Disponent | |
| F-09 | Pregled nerazporejenih naročil, združenih po regijah, s seštevkom teže in palet ter označenimi zamujenimi in nedostavljenimi | Disponent | |
| F-10 | Prikaz ture na zemljevidu z oštevilčenimi postanki (Leaflet + OpenStreetMap) | Disponent, Voznik | |
| F-11 | Samodejna določitev lokacije postanka na zemljevidu iz naslova stranke ob dodajanju naročila v turo (geokodiranje prek OpenStreetMap Nominatim) | Disponent | |
| F-12 | Predlog vrstnega reda postankov po najkrajši zračni razdalji (hevristika najbližjega soseda od skladišča) | Disponent | |
| F-13 | Pregled izkoriščenosti vozil po dnevih (% nosilnosti in % paletnih mest) | Disponent, Administrator | |
| F-14 | Upravljanje uporabniških dostopov in evidence vozil | Administrator | |

> TuraPlan naročil in strank ne vnaša: v realnem okolju jih prevzame iz ERP sistema podjetja, v projektu pa jih nadomestijo testni podatki, naloženi v bazo. Vozila in uporabnike v MVP ureja administrator prek vgrajenega Django Admin vmesnika, lastne strani zanje prinese F-14. Lokacijo skladišča administrator nastavi enkrat ob vzpostavitvi sistema prek Django Admina.

### Podrobnejši opis MVP funkcionalnosti

**F-01 Prijava in dostop glede na vlogo** – Uporabnik se prijavi z e-pošto in geslom. Disponent po prijavi vidi ture in naročila, voznik samo svoje potrjene ture, administrator administracijo. Neprijavljen uporabnik vidi le prijavno stran.

**F-02 Seznam tur in napredek** – Disponent vidi seznam tur, razvrščen po datumu odpreme, s filtrom po datumu in statusu. Pri vsaki turi je prikazano: datum odpreme, vozilo, voznik, število postankov, zasedenost vozila (npr. `980 / 1.200 kg`, `3,5 / 4 palete`) in status. Pri turah v statusu `V_DOSTAVI` je prikazan napredek (npr. `7 / 12 dostavljeno, 1 nedostavljeno`). V podrobnostih ture disponent za vsak postanek vidi rezultat, čas označitve in razlog nedostave. Podatki se posodobijo ob ponovnem nalaganju strani.

**F-03 Sestavljanje ture** – Disponent ustvari turo z datumom odpreme (danes ali kateri koli dan vnaprej) ter izbere aktivno vozilo in aktivnega voznika. Pravila:

- vozilo ima lahko na isti datum odpreme največ eno turo,
- voznik ima lahko na isti datum odpreme največ eno turo,
- v turo je mogoče dodati samo naročila s statusom `NOVO` ali `NEDOSTAVLJENO`,
- datum odpreme ture ne sme biti pred datumom prejema naročila,
- če je datum odpreme ture po roku odpreme naročila, sistem prikaže opozorilo »po roku odpreme«, vendar dodajanje dovoli,
- naročilo je lahko hkrati le v eni aktivni turi,
- seznam nerazporejenih naročil, iz katerega disponent izbira, je mogoče filtrirati po regiji stranke in je razvrščen po roku odpreme.

Nova tura ima status `OSNUTEK`. Dodano naročilo dobi status `PLANIRANO`, odstranjeno pa se vrne v `NOVO`.

**F-04 Preverjanje kapacitete** – Vsako naročilo ima težo (kg) in število palet (na 0,25 natančno), ki jih poda skladišče. Sistem ob vsaki spremembi ture sešteje težo in palete vseh naročil v turi in jih primerja z nosilnostjo in številom paletnih mest izbranega vozila. Na strani ture je prikazano:

- skupna teža / nosilnost vozila (npr. `980 / 1.200 kg`),
- skupne palete / paletna mesta (npr. `3,5 / 4`).

Če je katera koli meja presežena, je vrednost označena rdeče in prikazano je opozorilo. Turo v osnutku je še vedno mogoče shraniti (disponent lahko naročilo nato odstrani ali zamenja vozilo), ni pa je mogoče potrditi.

**F-05 Razvrščanje postankov in opombe** – Vsak postanek ima zaporedno številko (1, 2, 3 …). Disponent postanek premakne gor ali dol; številke se samodejno preštevilčijo brez lukenj. Pri vsakem postanku lahko vpiše opombo za voznika (do 300 znakov). Če ima stranka stalno opombo za dostavo (npr. »zadnji vhod«), se ta samodejno prikaže pri postanku.

Naročila iste stranke v isti turi:

- vsako naročilo ostane svoj postanek (s svojo številko naročila),
- ko disponent doda naročilo stranke, ki že ima postanek v turi, ga sistem samodejno uvrsti takoj za zadnji postanek te stranke,
- zaporedni postanki iste stranke so vizualno združeni (enaka barva ozadja in oznaka, npr. »Pekarna Zrno – 2 naročili«).

Če disponent postanke iste stranke ročno razmakne, sistem prikaže opozorilo »postanki iste stranke niso zaporedni«, vendar to dovoli.

**F-06 Potrditev ture** – Disponent turo potrdi. Sistem potrditev dovoli samo, če:

- ima tura vozilo in voznika,
- ima vsaj en postanek,
- kapaciteta ni presežena (ne po teži ne po paletah).

Če pogoj ni izpolnjen, sistem prikaže vse razloge. Potrjena tura (`POTRJENA`) je zaklenjena: postankov, vrstnega reda in opomb ni mogoče spreminjati. Disponent jo lahko vrne v `OSNUTEK`, dokler je voznik ni začel.

**F-07 Izvedba ture na telefonu** – Voznik vidi svoje potrjene ture. V podrobnostih ture so postanki po vrstnem redu: zaporedna številka, stranka, naslov, telefon, številka naročila, palete, teža in opombe; postanki iste stranke so vizualno združeni. Turo lahko začne (`V_DOSTAVI`) najprej na datum odpreme in samo, če nima druge ture v statusu `V_DOSTAVI`. Nato za vsak postanek označi:

- `DOSTAVLJENO` – naročilo dobi status `DOSTAVLJENO`,
- `NI DOSTAVLJENO` – razlog je obvezen (npr. »stranka zaprta«); naročilo dobi status `NEDOSTAVLJENO` in se vrne med nerazporejena naročila za ponovno planiranje.

Tura lahko traja več dni. Ko so označeni vsi postanki, tura samodejno preide v `ZAKLJUCENA`. Stran za voznika je prilagojena uporabi na telefonu.

## Kasnejše nadgradnje

1. **Optimizacija poti po cestah prek Google Maps (Routes API)** – vrstni red po dejanski cestni razdalji in času vožnje, prikaz poti na zemljevidu (nadgradnja F-12, ki uporablja zračne razdalje).
2. **Upoštevanje časovnih oken strank** – npr. pekarna sprejema blago samo od 5.00 do 9.00; sistem opozori, če predviden prihod ni v oknu.
3. **Samodejna razporeditev naročil na več vozil** (problem usmerjanja vozil, VRP) – npr. za 40 palet naročil v Nemčiji sistem predlaga, katera naročila gredo v katerega od treh tovornjakov glede na lokacije strank in kapaciteto.
4. **Integracija z ERP sistemom** – samodejni prenos naročil in strank iz ERP sistema podjetja prek REST API-ja (v projektu jih nadomeščajo testni podatki).
5. **Potrdilo o dostavi na telefonu** – podpis prejemnika ali fotografija ob dostavi.
6. **Obvestilo stranki** – e-pošta ali SMS z napovedanim časom dostave.
7. **Analitika dostav** – mesečni trendi: delež nedostavljenih naročil po razlogih in strankah, primerjava izkoriščenosti vozil skozi čas (nadgradnja dnevnega pregleda F-13).
8. **Izvoz ture v PDF** – za primere, ko voznik potrebuje seznam na papirju.

## Izven obsega (Out of scope)

V tem projektu **ne bomo** implementirali:

- vnosa in urejanja naročil in strank – te TuraPlan prevzame iz ERP sistema podjetja (v projektu testni podatki),
- izdajanja računov, dobavnic in drugih knjigovodskih dokumentov,
- upravljanja zalog, skladišča in priprave (komisioniranja) blaga,
- sledenja vozil z GPS v realnem času,
- evidence delovnega časa voznikov, tahografov in obračuna plač,
- spletnega naročanja za stranke – stranke sistema ne uporabljajo, naročila pripravi podjetje,
- nadzora temperature (hladna veriga) za živila,
- samostojne mobilne aplikacije (stran za voznika bo prilagojena telefonu v brskalniku),
- razporejanja blaga na palete – število palet za naročilo določi skladišče, sistem preverja le, ali palete in teža gredo v vozilo,
- delnih dostav, vračil blaga in reklamacij – postanek je lahko le v celoti dostavljen ali v celoti nedostavljen.
