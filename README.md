# TuraPlan

Spletna aplikacija za planiranje dostavnih tur distribucijskega podjetja. Disponent sestavi turo za vozilo, sistem sproti preveri, ali naročila po teži in številu palet gredo v vozilo, disponent določi vrstni red postankov in turo potrdi, voznik pa na telefonu označuje opravljene dostave.

## Uporabljene tehnologije

| Del | Tehnologije |
|---|---|
| Frontend | React, Vite, React Router, Bootstrap 5 |
| Backend | Python 3.12, Django 5, Django REST Framework |
| Podatkovna baza | SQLite |
| Avtentikacija | JWT (`djangorestframework-simplejwt`) |
| Zemljevid (izven MVP) | Leaflet + OpenStreetMap, Nominatim |
| Testiranje | pytest-django, Vitest |

## Struktura repozitorija

```text
turaplan/
├── frontend/   React aplikacija (uporabniški vmesnik)
├── backend/    Django aplikacija z REST API-jem
└── docs/       projektna dokumentacija in arhitekturne odločitve
```

## Dokumentacija

1. [Zasnova rešitve](docs/01-zasnova-resitve.md)
2. [Funkcionalnosti in obseg](docs/02-funkcionalnosti-in-obseg.md)
3. [Podatkovni model](docs/03-podatkovni-model.md)
4. [Arhitektura in tehnološki sklad](docs/04-arhitektura-in-tehnoloski-sklad.md)
5. [Uporabniške zgodbe](docs/05-uporabniske-zgodbe.md)
6. [Wireframes](docs/06-wireframes.md)
7. [Arhitekturne odločitve (ADR)](docs/adr/)
