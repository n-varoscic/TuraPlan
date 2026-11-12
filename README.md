# TuraPlan

Spletna aplikacija za planiranje dostavnih tur distribucijskega podjetja. Disponent sestavi turo za vozilo, sistem sproti preveri, ali naročila po teži in številu palet gredo v vozilo, disponent določi vrstni red postankov in turo potrdi, voznik pa na telefonu označuje opravljene dostave.

## Uporabljene tehnologije

| Del | Tehnologije |
|---|---|
| Frontend | React, Vite, React Router, Bootstrap 5 |
| Backend | Python 3.12, Django 5, Django REST Framework |
| Podatkovna baza | SQLite |
| Avtentikacija | JWT (`djangorestframework-simplejwt`) |
| Zemljevid (izven MVP) | Leaflet + OpenStreetMap, Nominatim, OSRM (pot po cestah) |
| Testiranje | pytest-django (backend), oxlint (preverjanje kode frontenda) |

## Struktura repozitorija

```text
turaplan/
├── frontend/   React aplikacija (uporabniški vmesnik)
├── backend/    Django aplikacija z REST API-jem
└── docs/       projektna dokumentacija in arhitekturne odločitve
```

## Lokalni zagon

### Z Dockerjem (priporočeno)

Potrebna sta [Git](https://git-scm.com/) in nameščen ter zagnan [Docker Desktop](https://www.docker.com/products/docker-desktop/). Vrata 5173 in 8000 morajo biti prosta.

1. Kloniraj repozitorij in pojdi v njegovo mapo:

   ```bash
   git clone https://github.com/n-varoscic/TuraPlan.git
   cd TuraPlan
   ```

2. Zaženi backend in frontend (prvi zagon traja nekaj minut, ker se namestijo knjižnice; tabele v bazi se ustvarijo samodejno):

   ```bash
   docker compose up --build
   ```

3. V drugem terminalu, v isti mapi, naloži testne podatke (uporabniki, vozila, stranke, naročila in ture):

   ```bash
   docker compose exec backend python manage.py seed_data
   ```

4. Odpri http://localhost:5173 in se prijavi kot disponent: `dejan.zupan@turaplan.si`, geslo `turaplan123`. Ostali testni uporabniki so v razdelku [Testni podatki](#testni-podatki).

Dodatno:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/health/
- Ustavitev: `Ctrl + C` ali `docker compose down`
- Spremembe kode se takoj uporabijo, ponovna gradnja (`--build`) je potrebna le ob novih knjižnicah
- Baza je shranjena v Docker volumnu `backend-data`, `docker compose down -v` jo izbriše
- Za zemljevid, iskanje lokacije in pot po cestah je potrebna internetna povezava; ostalo deluje tudi brez nje

### Brez Dockerja

Potrebna sta Python 3.12 in Node.js (LTS).

Backend (prvi terminal):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate         # ustvari tabele v bazi
python manage.py runserver       # http://localhost:8000
```

Frontend (drugi terminal):

```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

Nato v mapi `backend` naloži testne podatke z ukazom `python manage.py seed_data` (razdelek [Testni podatki](#testni-podatki)) in se prijavi na http://localhost:5173.

### Prvi uporabnik

Registracije ni, uporabnike ustvari administrator. Če naložiš testne podatke, ta korak ni potreben, ker so uporabniki vseh vlog že med njimi. Brez testnih podatkov prvega administratorja ustvariš z ukazom:

```bash
docker compose exec backend python manage.py createsuperuser   # z Dockerjem
python manage.py createsuperuser                               # brez Dockerja, v mapi backend
```

Nato se prijaviš v Django Admin (http://localhost:8000/admin/) in dodaš disponente in voznike.

### Testni podatki

Ukaz izbriše obstoječe ture, naročila, stranke in vozila ter naloži testne podatke (uporabniki vseh vlog, vozila, stranke, naročila in ture v različnih statusih). Datumi tur so določeni glede na današnji dan: včeraj zaključena tura, danes tura v dostavi, jutri potrjena tura in osnutek.

Kaj je v testnih podatkih:

- **91 strank** v osmih regijah (Podravska, Pomurska, Savinjska, Osrednjeslovenska, Gorenjska, Goriška, Dolenjska, Obalno-kraška); imena so izmišljena, naslovi so resnični, koordinate so že shranjene
- **100 naročil**: manjša za kombi, večja za tovornjak in nekaj izjemno velikih; nekatere stranke imajo dve naročili
- **17 vozil** z mariborsko registrsko: 7 kombijev (1.200 kg, 4 paletna mesta) in 10 tovornjakov (8.000–10.000 kg, 16–18 paletnih mest); kombi `MB PR-632` ni aktiven
- **17 uporabnikov**: 1 disponent, 1 administrator in 15 voznikov
- **skladišče**: Tržaška cesta 65, 2000 Maribor
- **4 ture**, vsaka v svoji regiji: včeraj Pomurska (zaključena), danes Podravska (v dostavi), jutri Savinjska (potrjena, tovornjak) in Dolenjska (osnutek)

```bash
docker compose exec backend python manage.py seed_data   # z Dockerjem
python manage.py seed_data                               # brez Dockerja, v mapi backend
```

Testni uporabniki (geslo vseh je `turaplan123`):

| E-pošta | Vloga | Kaj lahko preizkusiš |
|---|---|---|
| `dejan.zupan@turaplan.si` | Disponent | seznam tur, sestavljanje, potrditev in vrnitev ture v osnutek |
| `vid.krajnc@turaplan.si` | Voznik | današnja tura v dostavi: označevanje dostav, popravek oznake in zaključek ture |
| `luka.horvat@turaplan.si` | Voznik | jutrišnja potrjena tura: gumb »Začni turo« je do datuma odpreme onemogočen |
| `maja.kovac@turaplan.si` | Voznik | včerajšnja zaključena tura |
| še 12 voznikov, npr. `nejc.potocnik@turaplan.si` | Voznik | brez tur, na voljo pri novi turi (vsi so v `seed_data.py`, seznam `USERS`) |
| `ana.novak@turaplan.si` | Administrator | Django Admin na http://localhost:8000/admin/ |

### Preizkus zemljevida in iskanja lokacije

Zemljevid ture (skladišče, oštevilčeni postanki in črta po vrstnem redu) je na straneh Sestavljanje ture, Podrobnosti ture in na turi voznika. Koordinate testnih strank so že shranjene, zato zemljevid deluje takoj. Lokacijo nove stranke ali spremenjenega naslova backend poišče pri storitvi Nominatim (OpenStreetMap), ko disponent doda njeno naročilo v turo.

Kako preizkusiš iskanje lokacije:

1. V brskalniku odpri `https://nominatim.openstreetmap.org/search?q=Tržaška+cesta+67,+Maribor&format=json`; v odgovoru vidiš `lat` in `lon`.
2. V Django Admin (http://localhost:8000/admin/, `ana.novak@turaplan.si`) stranki izbriši koordinati ali spremeni naslov. Nato kot disponent dodaj njeno naročilo v turo: koordinate se shranijo pri stranki, postanek se pojavi na zemljevidu.
3. Izklopi internet (Wi-Fi) in ponovi korak 2: naročilo se doda, pri postanku piše »Lokacija ni določena«, pod zemljevidom je seznam postankov brez lokacije.

Kako preizkusiš predlog vrstnega reda:

1. Kot disponent odpri jutrišnji osnutek (Dolenjska) in klikni »Uredi turo«.
2. Klikni »Predlagaj vrstni red«: nad postanki se pokaže predlagani vrstni red z zračno razdaljo (in trenutno razdaljo za primerjavo), zemljevid pokaže predlog.
3. »Sprejmi predlog« vrstni red shrani, »Zavrzi« ga opusti. Postanke lahko potem še ročno premikaš.

Kako preizkusiš iskanje naročila:

1. Kot disponent na strani Seznam tur v iskalno polje vpiši `N-003` in pritisni Enter: zadetek ima status »Nedostavljeno« in razlog »Stranka zaprta«.
2. Vpiši `pekarna`: zadetki so vsa naročila strank s tem nazivom; pri planiranih in dostavljenih je povezava na turo z datumom in voznikom.
3. Vpiši `xy`: prikaže se »Ni najdenih naročil« (za naziv stranke so potrebni vsaj 3 znaki).

Kako preizkusiš pot po cestah:

1. Odpri osnutek na strani Sestavljanje ture: črta na zemljevidu sledi cestam, ob naslovu »Postanki« sta cestna razdalja in čas vožnje.
2. Premakni postanek: črta, razdalja in čas se čez trenutek posodobijo.
3. »Predlagaj vrstni red« najbližji postanek izbere po cestni razdalji in pokaže cestno razdaljo predloga in trenutne ture.
4. Izklopi internet in osveži stran: črta je ravna, piše »km zračne razdalje«, predlog deluje po zračni razdalji.

Kako preizkusiš dodajanje naročil na zemljevidu:

1. Na strani Sestavljanje ture klikni »Povečaj zemljevid«: zemljevid se poveča, seznama naročil in postankov se zožita.
2. Siva oznaka »+« je nerazporejeno naročilo, rdeča je naročilo po roku odpreme. Zemljevid kaže ista naročila kot seznam, zato nanj vplivata filtra regije in roka odpreme.
3. Klikni oznako »+« in nato »Dodaj v turo«: naročilo postane zadnji postanek ture.
4. Klikni oštevilčeno oznako postanka in nato »Odstrani iz ture«: naročilo se vrne med nerazporejena.

Po dodajanju novih knjižnic frontenda (Leaflet) je treba z Dockerjem enkrat pognati `docker compose exec frontend npm install` ali `docker compose up --build`, brez Dockerja pa `npm install` v mapi `frontend`.

### Testi

Testi backenda preverijo poslovna pravila in sprejemne kriterije uporabniških zgodb (npr. tura s preseženo kapaciteto se ne da potrditi, voznik ne vidi tur drugih voznikov).

```bash
docker compose exec backend pytest   # z Dockerjem
pytest                               # brez Dockerja, v mapi backend
```

Preverjanje kode frontenda:

```bash
docker compose exec frontend npm run lint   # z Dockerjem
npm run lint                                # brez Dockerja, v mapi frontend
```

## Dokumentacija

1. [Zasnova rešitve](docs/01-zasnova-resitve.md)
2. [Funkcionalnosti in obseg](docs/02-funkcionalnosti-in-obseg.md)
3. [Podatkovni model](docs/03-podatkovni-model.md)
4. [Arhitektura in tehnološki sklad](docs/04-arhitektura-in-tehnoloski-sklad.md)
5. [Uporabniške zgodbe](docs/05-uporabniske-zgodbe.md)
6. [Wireframes](docs/06-wireframes.md)
7. [Arhitekturne odločitve (ADR)](docs/adr/)
