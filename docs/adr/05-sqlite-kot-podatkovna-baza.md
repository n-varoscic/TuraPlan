# SQLite kot podatkovna baza

## Kontekst in problem

- Podatki so relacijski in povezani s tujimi ključi: stranka – naročilo – postanek – tura – vozilo ([03](../03-podatkovni-model.md)).
- Prehodi statusov morajo potekati v transakcijah.
- Aplikacija je interna, z malo hkratnimi uporabniki (nekaj disponentov in voznikov).
- Za razvoj in predstavitev mora biti baza enostavna za zagon.

## Obravnavane možnosti

- **SQLite** – relacijska baza, shranjena v eni datoteki, brez strežnika.
- **PostgreSQL** – zmogljiva relacijska baza, ki teče kot ločen strežnik.
- **MongoDB** – dokumentna (NoSQL) baza, ki hrani podatke kot dokumente brez fiksnih tabel.

## Odločitev

Izbrana možnost: **SQLite**, ker:

- podpira tuje ključe in transakcije, ki jih podatkovni model potrebuje (MongoDB za tako povezane podatke ni primerna),
- je ni treba nameščati ali zaganjati kot strežnik,
- zadošča za majhno število uporabnikov interne aplikacije,
- je prek Django ORM kasnejši prehod na PostgreSQL le sprememba nastavitev.

### Posledice

- Dobro, ker je zagon projekta preprost.
- Dobro, ker je testne podatke enostavno ponastaviti.
- Slabo, ker hkrati dovoli le enega pisca – ob več disponentih, ki hkrati urejajo ture, pride do čakanja.
- Slabo, ker bo za produkcijo z več uporabniki potreben prehod na PostgreSQL (nov ADR).
