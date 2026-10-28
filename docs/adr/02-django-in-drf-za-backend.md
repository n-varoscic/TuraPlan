# Django in Django REST Framework za backend

## Kontekst in problem

- Backend hrani podatke, izvaja poslovna pravila (kapaciteta vozila, prehodi statusov) in jih ponuja frontendu prek REST API-ja ([ADR-03](03-rest-api-v-json.md)).
- Potrebni so uporabniki z vlogami (disponent, voznik, administrator) in varno shranjena gesla.
- Podatki so relacijski: tura – postanek – naročilo – stranka ([03](../03-podatkovni-model.md)).
- V MVP je treba vozila in uporabnike vnašati brez lastnih strani.
- Projekt razvija ena oseba v enem semestru.

## Obravnavane možnosti

- **Django + Django REST Framework** – Python ogrodje z vgrajenimi uporabniki, delom z bazo in administracijo; DRF doda REST API.
- **FastAPI** – sodobno in hitro Python ogrodje samo za API-je; uporabnike, delo z bazo in administracijo je treba dodati sam.
- **Node.js z Express** – backend v JavaScriptu, istem jeziku kot frontend; uporabnike, delo z bazo in administracijo je treba dodati sam.

## Odločitev

Izbrana možnost: **Django + Django REST Framework**, ker:

- vgrajeni uporabniki, gesla in pravice pokrijejo vloge,
- delo z bazo (ORM) z migracijami ustreza relacijskemu modelu,
- vgrajen Django Admin v MVP nadomesti strani za vozila in uporabnike,
- DRF poskrbi za pretvorbo v JSON, preverjanje vnosov in pravice na API-ju,
- je Python primeren tudi za izračune nad podatki, ki jih projekt potrebuje (predlog vrstnega reda, izkoriščenost vozil).

### Posledice

- Dobro, ker je MVP mogoče narediti hitreje, saj je veliko infrastrukture že pripravljene.
- Slabo, ker je Django obsežnejše ogrodje s predpisano strukturo projekta.
- Slabo, ker bi bil pri zelo velikem številu zahtev FastAPI hitrejši.
- Slabo, ker je projekt vezan na Django ORM.
