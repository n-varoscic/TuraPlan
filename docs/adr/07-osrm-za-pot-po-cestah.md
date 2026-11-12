# OSRM za pot po cestah

## Kontekst in problem

- Zemljevid ture (F-10) je postanke povezoval z ravnimi črtami, predlog vrstnega reda (F-12) pa je uporabljal zračne razdalje ([ADR-06](06-openstreetmap-za-zemljevid.md)).
- Zračna razdalja ne pove, koliko bo voznik dejansko vozil: ceste zavijajo, čez reko ali hrib je treba naokoli.
- Disponent želi videti pot po cestah, cestno razdaljo in čas vožnje (F-15, [02](../02-funkcionalnosti-in-obseg.md)).
- Rešitev naj ostane brez stroškov in brez API ključev, aplikacija pa mora delovati tudi, ko zunanja storitev ni dosegljiva.

## Obravnavane možnosti

- **OSRM (javni strežnik)** – odprtokodni izračun poti nad podatki OpenStreetMap; brez registracije in ključa, namenjen lahki uporabi.
- **openrouteservice** – podobna storitev nad podatki OpenStreetMap; zahteva registracijo in API ključ.
- **Google Maps Routes API** – upošteva tudi promet; zahteva API ključ in plačilni račun.

## Odločitev

Izbrana možnost: **OSRM (javni strežnik)**, ker:

- uporablja iste podatke kot zemljevid in ne potrebuje ključa ali računa,
- z eno zahtevo vrne črto poti, razdaljo in čas vožnje (`route`), z drugo pa tabelo razdalj med vsemi točkami (`table`), ki jo potrebuje predlog vrstnega reda,
- ga backend kliče z vgrajeno knjižnico `urllib`, enako kot Nominatim, zato ni nove odvisnosti.

### Posledice

- Dobro, ker disponent vidi realno razdaljo in čas vožnje, predlog vrstnega reda pa upošteva ceste.
- Dobro, ker ni stroškov in skrivnih ključev.
- Dobro, ker aplikacija deluje tudi brez OSRM: črta je ravna, razdalja zračna, predlog se izračuna po zračni razdalji.
- Slabo, ker javni strežnik nima zagotovljene dosegljivosti in je namenjen lahki uporabi; za produkcijo bi OSRM namestili na lasten strežnik.
- Slabo, ker čas vožnje ne upošteva prometa, postankov in razkladanja.
- Slabo, ker predlog ostaja hevristika najbližjega soseda in ni vedno najkrajši.
- Slabo, ker se pot ne shranjuje: po vsaki spremembi vrstnega reda backend storitev vpraša znova.
