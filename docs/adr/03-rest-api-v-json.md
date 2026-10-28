# REST API v JSON za komunikacijo med frontendom in backendom

## Kontekst in problem

- Frontend ([ADR-01](01-react-za-frontend.md)) in backend ([ADR-02](02-django-in-drf-za-backend.md)) sta ločeni aplikaciji in potrebujeta skupen način komunikacije.
- Podatki so preprosti viri: ture, postanki, naročila, vozila ([03](../03-podatkovni-model.md)).
- Poleg branja so potrebna dejanja s pravili: potrdi turo, začni turo, označi dostavo.
- Kasneje naj bi z istim vmesnikom komuniciral tudi ERP sistem.

## Obravnavane možnosti

- **REST API v JSON** – vsak vir ima svoj naslov (npr. `/api/ture/`), dejanja se izvedejo z metodami HTTP (GET, POST …).
- **GraphQL** – en sam naslov, frontend v poizvedbi sam določi, katere podatke želi.

## Odločitev

Izbrana možnost: **REST API v JSON**, ker:

- se viri in dejanja naravno preslikajo v naslove (npr. `/api/ture/{id}/potrdi/`),
- so zasloni vnaprej določeni, zato prilagodljive poizvedbe GraphQL niso potrebne,
- je vsako končno točko mogoče preizkusiti neposredno (brskalnik, Postman),
- je REST najpogostejši način povezovanja z zunanjimi sistemi, kot je ERP.

### Posledice

- Dobro, ker je način standarden in dobro podprt v Django REST Framework.
- Dobro, ker je mogoča samodejna dokumentacija API-ja (OpenAPI).
- Slabo, ker lahko en zaslon potrebuje več zahtev (npr. tura in nerazporejena naročila).
- Slabo, ker posodobitve niso v realnem času – napredek dostav se prikaže ob osvežitvi.
