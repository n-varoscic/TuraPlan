# Prijava z žetoni JWT

## Kontekst in problem

- Frontend in backend sta ločeni aplikaciji, ki med razvojem tečeta na različnih naslovih.
- Aplikacija je interna: registracije ni, račune ustvari administrator ([02](../02-funkcionalnosti-in-obseg.md)).
- Vsaka zahteva mora nositi podatek, kdo je uporabnik in kakšno vlogo ima.
- Uporabnik, ki zapusti podjetje, mora takoj izgubiti dostop ([US-14](../05-uporabniske-zgodbe.md)).
- Kasneje je mogoča mobilna aplikacija za voznike, ki bi uporabljala isti API.

## Obravnavane možnosti

- **JWT (JSON Web Token)** – ob prijavi backend vrne podpisan žeton, ki ga frontend pošilja z vsako zahtevo.
- **Django seje s piškotki** – backend si zapomni prijavo, brskalnik pa z vsako zahtevo pošlje piškotek z oznako seje; najbolje deluje, ko sta frontend in backend na istem naslovu.

## Odločitev

Izbrana možnost: **JWT**, ker:

- enak način prijave brez sprememb uporabi tudi mobilna aplikacija ali drug sistem, kjer piškotkov ni,
- ne zahteva, da sta frontend in backend na istem naslovu,
- je najpogostejši pristop pri aplikacijah z Reactom in Django REST Framework, zato je na voljo največ gradiva.

### Posledice

- Dobro, ker backend ne hrani sej.
- Dobro, ker je prijava enaka za vse odjemalce.
- Slabo, ker žeton velja do izteka – backend mora pri vsaki zahtevi preveriti, ali je uporabnik še aktiven.
- Slabo, ker je treba upravljati dva žetona (kratkotrajni dostopni in žeton za osvežitev).
- Slabo, ker je žeton, shranjen v brskalniku, izpostavljen napadom XSS.
