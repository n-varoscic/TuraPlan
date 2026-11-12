# Docker Compose za lokalni zagon

## Kontekst in problem

- Projekt sestavljata dve ločeni aplikaciji: backend v Djangu in frontend v Reactu ([04](../04-arhitektura-in-tehnoloski-sklad.md)).
- Za zagon brez pripomočkov je treba namestiti pravo različico Pythona in Node.js, ustvariti virtualno okolje, namestiti knjižnice in zagnati dva strežnika v dveh terminalih.
- Kdor klonira repozitorij (npr. ocenjevalec), mora projekt zagnati hitro in z enakim rezultatom kot na razvojnem računalniku.
- Med razvojem se mora sprememba kode uporabiti takoj, brez ponovne gradnje.

## Obravnavane možnosti

- **Ročni zagon (Python `venv` in `npm`)** – vsak del se namesti in zažene posebej; brez dodatnih orodij, a z več koraki in odvisnostjo od nameščenih različic.
- **Docker Compose** – backend in frontend tečeta vsak v svojem vsebniku, oba se zaženeta z enim ukazom.
- **En sam vsebnik za oba dela** – ena slika z Djangom in zgrajenim frontendom; preprostejši zagon, a brez sprotnega osveževanja frontenda med razvojem.

## Odločitev

Izbrana možnost: **Docker Compose**, ker:

- se celoten projekt zažene z enim ukazom (`docker compose up --build`), potreben je samo Docker,
- sta različici Pythona in Node.js določeni v datotekah `Dockerfile`, zato je okolje pri vseh enako,
- ločena vsebnika ustrezata arhitekturi z ločenim backendom in frontendom,
- je koda z računalnika povezana v vsebnik, zato se spremembe uporabijo takoj,
- ročni zagon ostane mogoč in je opisan v [README](../../README.md).

### Posledice

- Dobro, ker je zagon za novega uporabnika kratek in ponovljiv.
- Dobro, ker se tabele v bazi ob zagonu ustvarijo samodejno (`migrate`).
- Dobro, ker baza v Docker volumnu ostane ohranjena med zagoni.
- Slabo, ker je treba namestiti Docker Desktop, prvi zagon pa traja nekaj minut.
- Slabo, ker je treba ob novih knjižnicah sliko zgraditi znova (`--build`).
- Slabo, ker je postavitev namenjena razvoju (razvojna strežnika Django in Vite); za produkcijo bi potrebovali drugačno konfiguracijo in nov ADR.
