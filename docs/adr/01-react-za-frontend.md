# React za frontend

## Kontekst in problem

- Uporabniški vmesnik je ločena aplikacija, ki z backendom komunicira prek API-ja ([04](../04-arhitektura-in-tehnoloski-sklad.md)).
- Dva zelo različna pogleda: zahteven zaslon disponenta na računalniku in preprost pogled voznika na telefonu ([06](../06-wireframes.md)).
- Zaslon za sestavljanje ture se sproti posodablja (zasedenost vozila, vrstni red postankov) brez ponovnega nalaganja strani.
- Isti gradniki se ponavljajo na več zaslonih (kartica postanka, prikaz zasedenosti vozila).
- Kasneje je predviden prikaz ture na zemljevidu (F-10).

## Obravnavane možnosti

- **React** – knjižnica za gradnjo vmesnika iz ponovno uporabnih komponent.
- **Vue** – podobna knjižnica, preprostejša za začetek, z manjšim ekosistemom.
- **Angular** – celovito ogrodje z vnaprej določeno strukturo in obveznim TypeScriptom.

## Odločitev

Izbrana možnost: **React**, ker:

- se komponente ujemajo z gradniki na zaslonih in jih uporabimo pri disponentu in vozniku,
- se prikaz posodobi brez ponovnega nalaganja strani,
- ima pripravljene knjižnice, ki jih projekt potrebuje: React Router, `react-leaflet` za zemljevid, Bootstrap,
- ima največ dokumentacije in primerov.

### Posledice

- Dobro, ker je ekosistem knjižnic velik.
- Dobro, ker je znanje uporabno tudi pri drugih projektih.
- Slabo, ker React pokrije le prikaz – usmerjanje med zasloni in klice API-ja je treba dodati z dodatnimi knjižnicami.
- Slabo, ker je potrebno učenje JSX in upravljanja stanja.
